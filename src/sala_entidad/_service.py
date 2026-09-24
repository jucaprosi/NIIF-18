"""
Compuerta _service.py para sala_entidad.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-11, sala antes propuesta en TASKS.md ¤sala_entidad_nueva):
identificación de la entidad por RUC, resolución de su código CIIU, y sugerencia
(editable, nunca aplicada sin confirmación del usuario — ver PRD.md §3 nota de
implementación y aporte A-02 en APORTES_INEDITOS.md) de si financiación o inversión es
su actividad principal.

Fuente de datos — consulta en vivo por RUC vía SRI (PRD.md RF-11, Fase 5, 2026-09-24):
se verificó que `https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/
rest/ConsolidadoContribuyente/obtenerPorNumerosRuc` es un endpoint público, sin sesión
ni autenticación, que responde al instante con razón social/estado/actividad económica
por RUC — a diferencia del directorio de la SCVS (verificado antes, Fase 4), el SRI SÍ
permite consulta puntual por RUC sin descargar ningún archivo masivo. Limitación real:
el SRI no devuelve código CIIU, solo el texto libre de la actividad económica —
`inferir_ciiu_por_texto` compara ese texto contra el catálogo CIIU local
(`cargar_catalogo_ciiu`, estático, no requiere descarga en vivo — ver nota abajo) para
sugerir la sección CIIU más probable, con el mismo patrón de "sugerencia DRAFT sin
validar" que ya rige `sugerir_actividad_principal`.

El catálogo CIIU (`ciiu.xlsx`) es una tabla de clasificación estándar (3,052 filas, del
INEC/SCVS) que cambia cada varios años, no datos de entidades — se sigue empaquetando
como archivo local con la app (no necesita descarga en vivo ni base de datos, a
diferencia del directorio de 227k compañías).

Las funciones de descarga masiva del directorio SCVS (`actualizar_snapshot_directorio`,
`cargar_directorio`, `buscar_entidad_por_ruc`) se conservan (probadas, funcionales) mas
ya no son el flujo por defecto de la UI (`app.py`) — quedan disponibles si se necesita
resolver un código CIIU exacto (no inferido) contra la fuente oficial completa. Ver
`TASKS.md` `¤consulta_sri_ruc_en_vivo`.
"""
import os
import re
import unicodedata
import pandas as pd
import requests

__all__ = [
    "URL_DIRECTORIO_SCVS",
    "URL_SRI_CONSULTA_RUC",
    "actualizar_snapshot_directorio",
    "fecha_snapshot_directorio",
    "cargar_directorio",
    "cargar_catalogo_ciiu",
    "buscar_entidad_por_ruc",
    "buscar_entidad_ruc_sri",
    "inferir_ciiu_por_texto",
    "resolver_descripcion_ciiu",
    "sugerir_actividad_principal",
]

URL_DIRECTORIO_SCVS = "https://mercadodevalores.supercias.gob.ec/reportes/excel/directorio_companias.xlsx"
URL_SRI_CONSULTA_RUC = "https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc"

_COLUMNAS_DIRECTORIO = ["RUC", "NOMBRE", "SITUACIÓN LEGAL", "CIIU NIVEL 1", "CIIU NIVEL 6"]

# Palabras sin valor discriminante para el matching de texto de `inferir_ciiu_por_texto`
# — conectores gramaticales y la palabra "actividad(es)", que aparece en casi toda
# descripción CIIU y en casi todo texto de actividad del SRI, por lo que no aporta señal.
_PALABRAS_VACIAS_CIIU = {
    "DE", "LA", "EL", "Y", "EN", "CON", "PARA", "POR", "A", "LOS", "LAS", "SIN", "DEL",
    "AL", "U", "O", "SU", "SUS", "QUE", "SE", "UN", "UNA", "COMO", "NO", "OTROS",
    "OTRAS", "OTRO", "OTRA", "NCP", "ACTIVIDADES", "ACTIVIDAD",
}

# DRAFT — mapeo CIIU (sección, nivel 1) -> sugerencia de actividad principal.
# NO VALIDADO CON CRITERIO CONTABLE (PRD.md §8, riesgo de mapeo CIIU->actividad
# principal; TASKS.md ¤mapeo_ciiu_actividad_principal). Es un punto de partida editable,
# nunca una clasificación final — ver `sugerir_actividad_principal`.
_SECCIONES_FINANCIACION = {"K"}  # K: Actividades financieras y de seguros
_SECCIONES_INVERSION = {"L"}  # L: Actividades inmobiliarias


def fecha_snapshot_directorio(directorio_path):
    """Lee la fecha de actualización declarada en la cabecera del snapshot SCVS."""
    df_meta = pd.read_excel(directorio_path, sheet_name=0, header=None, nrows=4)
    for valor in df_meta[0]:
        texto = str(valor)
        if texto.upper().startswith("FECHA DE ACTUALIZACION"):
            return texto.split(":", 1)[1].strip()
    return "desconocida"


def _ruta_cache_parquet(directorio_path):
    raiz, _ = os.path.splitext(directorio_path)
    return raiz + ".parquet"


# ¤sala_entidad ¤scvs
def actualizar_snapshot_directorio(directorio_path, url=URL_DIRECTORIO_SCVS, timeout_segundos=30):
    """Intenta refrescar el snapshot local del directorio SCVS descargando el archivo
    público más reciente. Devuelve (bool actualizado, str motivo).

    Falla de forma segura (no rompe el flujo, no borra el snapshot existente) ante
    cualquier problema de red: timeout, DNS, HTTP != 200, sitio caído. Escribe primero
    a un archivo temporal y solo reemplaza el snapshot si la descarga completa fue
    exitosa — evita dejar un `.xlsx` corrupto a medio escribir si la conexión se corta
    a mitad de la descarga (~35 MB).
    """
    tmp_path = directorio_path + ".tmp_descarga"
    try:
        respuesta = requests.get(url, timeout=timeout_segundos, headers={"User-Agent": "Mozilla/5.0"})
        respuesta.raise_for_status()
        with open(tmp_path, "wb") as f:
            f.write(respuesta.content)
        os.replace(tmp_path, directorio_path)
        return True, "Directorio SCVS actualizado en vivo desde la fuente pública."
    except Exception as exc:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return False, f"No se pudo actualizar en vivo ({exc.__class__.__name__}) — usando snapshot local existente."


def cargar_directorio(directorio_path):
    """Carga el snapshot completo del directorio SCVS (227k+ filas) — operación cara.

    Reestructuración (no parche): antes, `buscar_entidad_por_ruc` releía el xlsx entero
    en cada búsqueda (~37s por RUC, verificado en esta sesión). La causa raíz no era la
    UI (un spinner no la resuelve) sino mezclar "cargar la fuente" con "filtrar un
    valor" en la misma función. Aquí se separan: el llamador (app.py) debe cachear el
    resultado de esta función una sola vez por proceso (`st.cache_data`) y reusarlo para
    todas las búsquedas de esa sesión — ver `references/performance.md` de la guía
    developing-with-streamlit: "cache la fuente cara, filtre barato después".

    Optimización (TASKS.md ¤optimizar_carga_directorio_scvs): `st.cache_data` solo dura
    lo que dura el proceso de Streamlit — cada reinicio del servidor vuelve a pagar los
    ~40-70s de leer el `.xlsx` de 227k filas vía openpyxl. Aquí se agrega una caché en
    disco: un `.parquet` hermano del `.xlsx` (mismo nombre, otra extensión), que se
    regenera automáticamente si no existe o si el `.xlsx` se modificó después (snapshot
    actualizado). Leer ese `.parquet` es del orden de decenas de milisegundos en vez de
    decenas de segundos — el `.xlsx` sigue siendo la fuente de verdad declarada en
    RF-11; el `.parquet` es solo una caché derivada, no se versiona como fuente aparte.
    """
    if not os.path.exists(directorio_path):
        return None
    ruta_parquet = _ruta_cache_parquet(directorio_path)
    xlsx_mtime = os.path.getmtime(directorio_path)
    if os.path.exists(ruta_parquet) and os.path.getmtime(ruta_parquet) >= xlsx_mtime:
        return pd.read_parquet(ruta_parquet)
    df = pd.read_excel(directorio_path, sheet_name=0, header=4, usecols=_COLUMNAS_DIRECTORIO, dtype={"RUC": str})
    try:
        df.to_parquet(ruta_parquet, index=False)
    except Exception:
        pass  # la caché en disco es una optimización, no una dependencia dura: si falla
              # (p. ej. sin permisos de escritura), se sigue funcionando solo más lento.
    return df


# ¤ciiu
def cargar_catalogo_ciiu(catalogo_path):
    """Carga el catálogo CIIU completo — operación cara, cachear una sola vez (ver `cargar_directorio`)."""
    if not os.path.exists(catalogo_path):
        return None
    return pd.read_excel(catalogo_path, sheet_name=0)


def buscar_entidad_por_ruc(df_directorio, ruc, fecha_snapshot_origen="desconocida"):
    """Busca un RUC exacto en un directorio ya cargado en memoria (`cargar_directorio`).

    Devuelve un dict con ruc/razon_social/estado/ciiu_nivel_1/ciiu_nivel_6/fuente/
    fecha_snapshot_origen, o None si el RUC no aparece (RF-11: el sistema debe permitir
    continuar con configuración 100% manual en ese caso).
    """
    ruc = str(ruc).strip()
    if not ruc or df_directorio is None:
        return None
    fila = df_directorio[df_directorio["RUC"].astype(str).str.strip() == ruc]
    if fila.empty:
        return None
    r = fila.iloc[0]
    return {
        "ruc": ruc,
        "razon_social": str(r["NOMBRE"]).strip(),
        "estado": str(r["SITUACIÓN LEGAL"]).strip(),
        "ciiu_nivel_1": str(r["CIIU NIVEL 1"]).strip(),
        "ciiu_nivel_6": str(r["CIIU NIVEL 6"]).strip(),
        "fuente": "snapshot_local",
        "fecha_snapshot_origen": fecha_snapshot_origen,
    }


# ¤sala_entidad ¤sri
def buscar_entidad_ruc_sri(ruc, timeout_segundos=15):
    """Consulta en vivo al SRI por un RUC exacto — sin descargar ningún archivo masivo.

    Verificado 2026-09-24 contra 3 RUCs reales (persona jurídica agrícola, banco,
    operadora de telecomunicaciones): endpoint público, sin sesión ni autenticación,
    responde en menos de 1 segundo. Devuelve un dict con ruc/razon_social/estado/
    actividad_economica_texto/tipo_contribuyente/obligado_llevar_contabilidad/fuente,
    o None si el RUC no existe, el servicio no responde, o hay un error de red —
    mismo contrato que `buscar_entidad_por_ruc` (RF-11: el sistema debe permitir
    continuar con configuración 100% manual si no hay match).
    """
    ruc = str(ruc).strip()
    if not ruc:
        return None
    try:
        respuesta = requests.get(
            URL_SRI_CONSULTA_RUC, params={"ruc": ruc}, timeout=timeout_segundos,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception:
        return None
    if not datos:
        return None
    r = datos[0]
    return {
        "ruc": ruc,
        "razon_social": str(r.get("razonSocial") or "").strip(),
        "estado": str(r.get("estadoContribuyenteRuc") or "").strip(),
        "actividad_economica_texto": str(r.get("actividadEconomicaPrincipal") or "").strip(),
        "tipo_contribuyente": str(r.get("tipoContribuyente") or "").strip(),
        "obligado_llevar_contabilidad": str(r.get("obligadoLlevarContabilidad") or "").strip(),
        "fuente": "consulta_en_vivo_sri",
    }


def _tokens_significativos(texto):
    texto = str(texto).upper()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return {t for t in re.findall(r"[A-Z]{3,}", texto) if t not in _PALABRAS_VACIAS_CIIU}


# ¤ciiu
def inferir_ciiu_por_texto(texto_actividad, df_catalogo, nivel_minimo=2):
    """Sugiere el código/sección CIIU más probable comparando `texto_actividad` (texto
    libre, p. ej. `actividad_economica_texto` del SRI) contra las descripciones del
    catálogo CIIU local ya cargado en memoria (`cargar_catalogo_ciiu`).

    Heurística de solapamiento de palabras (Jaccard sobre tokens significativos, no
    TF-IDF ni embeddings — deliberadamente simple y auditable, mismo espíritu que el
    árbol de `sala_clasificacion`): se compara contra descripciones de nivel >=
    `nivel_minimo` (se excluye nivel 1 por defecto — sus descripciones son demasiado
    generales y pierden frente a texto específico del SRI, verificado empíricamente:
    "Actividades de intermediación monetaria..." solo matchea bien contra la
    descripción nivel-3 "INTERMEDIACIÓN MONETARIA", no contra la nivel-1 "ACTIVIDADES
    FINANCIERAS Y DE SEGUROS"). La sección CIIU nivel 1 se deriva de la primera letra
    del código de la fila con mejor puntaje.

    Devuelve un dict (codigo_ciiu, descripcion_ciiu, ciiu_nivel_1, score_confianza,
    advertencia) o None si no hay catálogo cargado, el texto está vacío, o ninguna fila
    comparte al menos una palabra significativa con el texto de entrada.

    **Es una sugerencia DRAFT, no una clasificación oficial** — igual criterio que
    `sugerir_actividad_principal`: requiere confirmación del usuario antes de habilitar
    RF-03 (ver PRD.md §3, RF-11).
    """
    if df_catalogo is None or not str(texto_actividad).strip():
        return None
    tokens_query = _tokens_significativos(texto_actividad)
    if not tokens_query:
        return None
    candidatos = df_catalogo[df_catalogo["NIVEL"] >= nivel_minimo]
    mejor_score, mejor_fila = -1.0, None
    for _, fila in candidatos.iterrows():
        tokens_fila = _tokens_significativos(fila["DESCRIPCION"])
        interseccion = tokens_query & tokens_fila
        if not interseccion:
            continue
        union = tokens_query | tokens_fila
        score = len(interseccion) / len(union)
        if score > mejor_score:
            mejor_score, mejor_fila = score, fila
    if mejor_fila is None:
        return None
    codigo = str(mejor_fila["CODIGO"]).strip()
    return {
        "codigo_ciiu": codigo,
        "descripcion_ciiu": str(mejor_fila["DESCRIPCION"]).strip(),
        "ciiu_nivel_1": codigo[0].upper() if codigo else "",
        "score_confianza": round(mejor_score, 2),
        "advertencia": (
            "Sección CIIU inferida por coincidencia de texto (no es el código oficial "
            "de la SCVS) — sugerencia DRAFT sin validar por un contador. Ver PRD.md "
            "§3, RF-11 y TASKS.md ¤mapeo_ciiu_actividad_principal."
        ),
    }


def resolver_descripcion_ciiu(df_catalogo, codigo_ciiu):
    """Resuelve la descripción de un código CIIU contra un catálogo ya cargado en memoria."""
    codigo_ciiu = str(codigo_ciiu).strip()
    if not codigo_ciiu or df_catalogo is None:
        return None
    fila = df_catalogo[df_catalogo["CODIGO"].astype(str).str.strip() == codigo_ciiu]
    if fila.empty:
        return None
    return str(fila.iloc[0]["DESCRIPCION"]).strip()


def sugerir_actividad_principal(ciiu_nivel_1):
    """Sugerencia DRAFT de actividad principal a partir de la sección CIIU nivel 1.

    Devuelve un dict con financiacion_es_actividad_principal, inversion_es_actividad_
    principal, origen_actividad_principal ("sugerido_ciiu") y advertencia. El llamador
    (UI) DEBE bloquear la clasificación masiva (RF-03) hasta que el usuario confirme o
    corrija esta sugerencia — ver PRD.md RF-11 y aporte A-02.
    """
    seccion = str(ciiu_nivel_1).strip().upper()
    return {
        "financiacion_es_actividad_principal": seccion in _SECCIONES_FINANCIACION,
        "inversion_es_actividad_principal": seccion in _SECCIONES_INVERSION,
        "origen_actividad_principal": "sugerido_ciiu",
        "advertencia": (
            "Sugerencia DRAFT sin validar por un contador (PRD.md §8, TASKS.md "
            "¤mapeo_ciiu_actividad_principal). No usar en producción sin revisión."
        ),
    }
