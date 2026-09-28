# RF-11 Fase 4 — consulta en vivo a la SCVS

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-24, v3.9)

## Pregunta del propietario

"Para la actividad comercial (buscar en SCVS), en lugar de que la IA busque el número
de RUC en un archivo interno Excel, es preferible que busque los datos directamente en
`https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf`, ese
archivo estimo que debe actualizarse automáticamente con los cambios de supercias."

## Investigación (antes de escribir código)

Se abrió la página real en el navegador. Hallazgos:

- La página muestra el mismo Directorio de Compañías que ya usa la app (227,708 filas,
  columnas RUC/NOMBRE/CIIU NIVEL 1/etc. — coinciden con `_COLUMNAS_DIRECTORIO` de
  `sala_entidad`), con `FECHA DE ACTUALIZACIÓN: 24/09/2026 00:45:15` — confirma la
  intuición del propietario: la SCVS sí actualiza este reporte diariamente.
- La tabla en pantalla es un `DataTable` de JSF (paginado, con filtro por NOMBRE/
  SITUACIÓN LEGAL/TIPO DE COMPAÑÍA, **sin filtro por RUC visible**) — automatizar una
  búsqueda por RUC contra esa interfaz habría requerido manejar sesión/ViewState de JSF,
  fila por fila, frágil y lento.
- La página trae un enlace de descarga directo: **"Descargar en formato Excel"** →
  `/reportes/excel/directorio_companias.xlsx`. Verificado con `curl -I`: `HTTP 200 OK`,
  **sin cookies ni sesión**, `Last-Modified` del mismo día. Es el mismo archivo completo
  que ya se usa localmente, descargable con una petición HTTP simple.
- `robots.txt` del sitio → `404 Not Found` (no existe, sin restricción declarada).

**Conclusión**: no hace falta scrapear la interfaz de búsqueda ni construir un cliente
JSF con manejo de sesión — mucho más simple y robusto descargar el archivo completo
público (35 MB) al inicio de cada sesión y reemplazar el snapshot local, que es
exactamente lo que ya hacía el usuario manualmente al pedir el archivo a la SCVS.

## Implementación

- `src/sala_entidad/_service.py`: nueva `URL_DIRECTORIO_SCVS` (constante) y
  `actualizar_snapshot_directorio(directorio_path, url, timeout_segundos=30)` — descarga
  con `requests.get`, escribe a un archivo temporal y solo reemplaza el snapshot con
  `os.replace` si la descarga se completó (atómico, evita dejar un `.xlsx` corrupto a
  medio escribir). Si falla por cualquier motivo (sin red, timeout, HTTP de error),
  **no toca el snapshot existente** y devuelve `(False, motivo)`.
- `app.py`: `_cargar_directorio_cacheado()` ahora llama a
  `actualizar_snapshot_directorio` antes de `cargar_directorio` (sigue cacheado una vez
  por sesión vía `st.cache_data`, mismo patrón de rendimiento ya establecido). La UI
  muestra un badge verde (`cloud_done`) si la actualización en vivo tuvo éxito, o
  naranja (`cloud_off`) con el motivo si falló y se está usando el snapshot local.
- `requirements.txt`: se agregó `requests` (usado por la descarga) y `pyarrow` (ya se
  usaba para la caché Parquet de `cargar_directorio` pero nunca se había declarado como
  dependencia — corregido de paso).
- El catálogo CIIU (`ciiu.xlsx`) **no** se actualiza en vivo — la SCVS no publica un
  enlace de descarga equivalente para el catálogo CIIU en la misma página; sigue siendo
  snapshot local únicamente. No se investigó una fuente en vivo separada (INEC) en esta
  sesión.

## Verificación

- 2 tests nuevos en `tests/test_sala_entidad.py`:
  `test_actualizar_snapshot_directorio_exito_reemplaza_archivo` (con `requests.get`
  mockeado) y `test_actualizar_snapshot_directorio_falla_conserva_archivo_existente`
  (simula `ConnectionError`, confirma que el archivo original queda intacto y no se deja
  un `.tmp_descarga` huérfano).
- `python -m pytest tests/` — 46/46 en verde, corrido con el `venv` real del proyecto
  (`venv/Scripts/python.exe`), no solo el Python del sistema.
- **Prueba end-to-end real en la app** (Streamlit corriendo desde `venv`, navegador):
  búsqueda del RUC `1790013731001` → badge verde "Directorio SCVS actualizado en vivo" →
  entidad resuelta correctamente (ACEITES TROPICALES SOCIEDAD ANONIMA ATSA) → fecha de
  snapshot mostrada: `24/09/2026 00:45:15`, la del día de la sesión, coincidiendo
  exactamente con la fecha vista en la página real de la SCVS.
- Nota operativa: el ciclo completo (descarga ~35 MB + lectura con `openpyxl` de 227k
  filas + escritura de caché Parquet) tardó **~70-80 segundos** la primera vez que se
  ejecutó en esta sesión — mismo orden de magnitud ya documentado para la lectura del
 `.xlsx` sin la descarga (, hallazgo de rendimiento). Ocurre una
  sola vez por sesión (`st.cache_data`), no en cada búsqueda de RUC.

## Nota de alcance — qué NO resuelve esta tarea

Esta tarea corrige la **vigencia del dato** (RUC/CIIU/razón social siempre al día). El
**criterio de negocio** que interpreta esos datos (qué código CIIU implica
`financiacion_es_actividad_principal` / `inversion_es_actividad_principal`) sigue siendo
un problema distinto — ver (requiere revisión
contable) y (extensión: ese mapeo también debería ser
editable desde la app, no solo el directorio).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
