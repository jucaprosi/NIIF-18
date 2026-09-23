"""
Compuerta _service.py para sala_entidad.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-11, sala antes propuesta en TASKS.md ¤sala_entidad_nueva):
identificación de la entidad por RUC contra el snapshot local del Directorio de
Compañías de la SCVS, resolución de su código CIIU, y sugerencia (editable, nunca
aplicada sin confirmación del usuario — ver PRD.md §3 nota de implementación y aporte
A-02 en APORTES_INEDITOS.md) de si financiación o inversión es su actividad principal.

Fuente de datos: modo snapshot local únicamente (PRD.md RF-11, MVP). La consulta en
vivo es una fase posterior (PRD.md §7, Fase 4) condicionada a validar un mecanismo de
acceso oficial — no implementada aquí.
"""
import os
import pandas as pd

__all__ = [
    "fecha_snapshot_directorio",
    "cargar_directorio",
    "cargar_catalogo_ciiu",
    "buscar_entidad_por_ruc",
    "resolver_descripcion_ciiu",
    "sugerir_actividad_principal",
]

_COLUMNAS_DIRECTORIO = ["RUC", "NOMBRE", "SITUACIÓN LEGAL", "CIIU NIVEL 1", "CIIU NIVEL 6"]

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
