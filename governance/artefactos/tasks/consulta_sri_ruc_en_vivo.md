# RF-11 rediseñado — consulta puntual al SRI, sin descarga masiva

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-24, v3.10)

## Corrección del propietario sobre

"Error. Lo que se requiere es que la app busque directamente desde la nube la actividad
comercial en `directorioCompanias.jsf`, pues la app va a estar alojada en internet, de
lo contrario tenemos que descargar el archivo y luego subirlo a Neon o a otra base de
datos, para qué realizar doble proceso si la información está ya visible ahí."

La tarea anterior resolvía la *vigencia* del dato (siempre al
día) pero seguía requiriendo traer un archivo de 227k filas completo a cada arranque de
sesión — no lo que el propietario pedía (consulta puntual por RUC, sin descarga masiva,
apta para un hosting con disco efímero sin necesitar una base de datos externa).

## Investigación (antes de escribir código, otra vez)

1. **¿La SCVS permite filtrar su tabla en vivo por RUC?** Se inspeccionó el DOM y las
   peticiones AJAX subyacentes (PrimeFaces DataTable sobre JSF) de
   `directorioCompanias.jsf`. Hallazgo verificado con JavaScript ejecutado en la propia
   página: de 24 columnas, solo 9 tienen filtro habilitado por la SCVS (NOMBRE,
   SITUACIÓN LEGAL, TIPO DE COMPAÑÍA, PAÍS, REGIÓN, PROVINCIA, CANTÓN, CIUDAD, CIIU
   NIVEL 1/6) — **RUC y EXPEDIENTE no tienen filtro, ni visible ni en el mecanismo AJAX
   que sostiene la tabla**. No existe una consulta puntual por RUC en este sitio, punto.
2. **¿Existe una fuente distinta que sí permita consulta por RUC?** El RUC lo emite el
   SRI (Servicio de Rentas Internas), no la SCVS. Se probó el endpoint público conocido
   `srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/
   ConsolidadoContribuyente/obtenerPorNumerosRuc?&ruc={RUC}` con 3 RUCs reales de
   distinto sector (Aceites Tropicales — agrícola, Banco Pichincha — financiero,
   Conecel/Claro — telecomunicaciones): responde en menos de 1 segundo, sin sesión ni
   autenticación, con razón social/estado/actividad económica/tipo de
   contribuyente/obligación de llevar contabilidad.
3. **Limitación real encontrada**: el SRI **no devuelve código CIIU**, solo el texto
   libre de la actividad económica (ej. "ACTIVIDADES DE INTERMEDIACIÓN MONETARIA
   REALIZADA POR LA BANCA COMERCIAL." para el Banco Pichincha). El árbol de
   clasificación (§3) necesita la sección CIIU (letra A-U), no texto libre.

## Diseño de la solución (validado con el propietario antes de implementar)

Se presentaron 3 opciones (`AskUserQuestion`): (a) SRI en vivo + inferir CIIU por
coincidencia de texto contra el catálogo local, (b) SRI en vivo + CIIU 100% manual, (c)
mantener el enfoque híbrido de . El propietario eligió (a).

**Precisión aparte, ya aclarada con el propietario**: el catálogo CIIU local
(`ciiu.xlsx`) no necesita el mismo tratamiento que el directorio de RUCs — es una tabla
de clasificación estándar de 3,052 filas (INEC/SCVS) que cambia cada varios años, no
datos de entidades. Se queda empaquetada como archivo local de la app, como cualquier
otro dato de configuración — no requiere descarga en vivo ni base de datos.

## Implementación

- `src/sala_entidad/_service.py`:
  - `buscar_entidad_ruc_sri(ruc, timeout_segundos=15)` — consulta en vivo al SRI, sin
    tocar disco. Devuelve `None` ante cualquier fallo (RUC no encontrado, timeout, error
    HTTP) — mismo contrato de "permitir configuración 100% manual" que el resto de
    RF-11.
  - `inferir_ciiu_por_texto(texto_actividad, df_catalogo, nivel_minimo=2)` — heurística
    de solapamiento de palabras (Jaccard sobre tokens significativos, sin stopwords)
    entre el texto del SRI y las descripciones del catálogo CIIU. Se excluye nivel 1 del
    matching por defecto (verificado empíricamente: las descripciones nivel-1 son
    demasiado generales y pierden frente a la nivel-3, más específica — "ACTIVIDADES
    FINANCIERAS Y DE SEGUROS" pierde contra "INTERMEDIACIÓN MONETARIA" al comparar con
    el texto del SRI para un banco). Devuelve el código/sección con mejor puntaje y un
    `score_confianza` explícito.
- `src/app.py`: la pestaña "Entidad" ahora llama a `buscar_entidad_ruc_sri` +
  `inferir_ciiu_por_texto` en vez de `_cargar_directorio_cacheado` (retirada). Muestra
  la actividad económica textual del SRI, la sección/código CIIU inferido con su score
  de confianza, y la misma advertencia DRAFT de siempre.
- **Se conserva** (no se elimina) el código de
  (`actualizar_snapshot_directorio`, `cargar_directorio`, `buscar_entidad_por_ruc`) — es
  código probado y funcional, útil como ruta alterna si en el futuro se necesita el
  código CIIU exacto (no inferido) contra la fuente oficial completa. Solo dejó de ser
  el flujo por defecto de la UI.

## Bug encontrado y corregido durante la verificación en la app real

Los checkboxes "Financiar clientes..." / "Invertir en activos..." no se pre-marcaban
con la sugerencia calculada, aunque el cálculo era correcto (verificado por separado).
Causa raíz: Streamlit solo aplica el parámetro `value=` la primera vez que una `key` de
widget se renderiza; en corridas posteriores usa `st.session_state[key]`, ignorando el
nuevo valor por defecto de una búsqueda distinta. Como la clave (`chk_fin_principal`)
era fija, quedaba congelada en `False` desde la primera corrida (antes de cualquier
búsqueda). **Corrección de causa raíz**: clave dinámica atada al RUC buscado
(`f"chk_fin_principal_{ruc_buscado}"`), no un `session_state.pop(...)` como parche.

## Verificación

- 6 tests nuevos en `tests/test_sala_entidad.py` (éxito/no encontrado/fallo de red para
  `buscar_entidad_ruc_sri`; match correcto/sin coincidencia/sin catálogo/texto vacío
  para `inferir_ciiu_por_texto`) — con mock de red, sin depender de que el SRI esté
  disponible al correr la suite.
- `python -m pytest tests/` — 54/54 en verde, con el `venv` real del proyecto.
- **Prueba end-to-end real en la app** (Streamlit, navegador): RUC del Banco Pichincha →
  resultado instantáneo (sin el retraso de ~70s de la versión anterior) → razón social
  correcta, actividad económica textual correcta, CIIU inferido K (K641,
  "Intermediación monetaria", confianza 40%) → checkbox "Financiar clientes" pre-marcado
  correctamente tras la corrección del bug.

## Nota de alcance — qué sigue pendiente

El `score_confianza` de la inferencia (0.32-1.00 en los 3 casos probados) es una señal
útil pero no reemplaza la revisión contable de — sigue
haciendo falta que un contador confirme qué secciones CIIU (más allá de K/L) deberían
sugerir financiación/inversión, y ahora además ese mapeo debe convivir con una sección
que en sí misma es inferida, no leída de un código oficial (doble incertidumbre,
documentada en `PRD.md` RF-11).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
