# Carga de PDF generado por herramienta en Ingesta

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-24)

## Pedido del propietario

"En la ingesta, agrega el poder cargar archivos PDF generados con herramientas, no
foto ni scan."

## Implementación

- `src/sala_importacion/_service.py`: nueva `extraer_tabla_de_pdf(archivo)` usa
  `pdfplumber` (Python puro, sin binarios externos como Ghostscript/Java que sí
  requieren `camelot`/`tabula`).
- **Rechazo explícito de escaneos/fotos**: antes de buscar tablas, se mide el promedio
  de caracteres de texto extraíble por página (`page.extract_text()`). Un PDF generado
  por herramienta (ERP, Excel, sistema contable) trae cientos de caracteres por página;
  un escaneo/foto sin OCR no tiene capa de texto en absoluto — devuelve 0. El umbral
  (40 caracteres/página) es deliberadamente bajo porque la brecha real es enorme, no un
  caso límite que requiera calibración fina.
- El DataFrame crudo resultante se reincorpora al **mismo pipeline** que ya usan
  CSV/Excel (`infer_columns_by_mathematical_weights`, `construir_balanza_estandar`,
  `evaluar_calidad_balanza`) — no se duplicó lógica de inferencia de columnas para PDF.
- `app.py`: el `file_uploader` de la pestaña Ingesta ahora acepta `.pdf` además de
  `.xlsx/.xls/.csv`, con mensaje de ayuda explícito sobre la restricción de escaneos.

## Verificación

- 3 tests nuevos en `tests/test_sala_importacion_pdf.py`, con PDFs sintéticos
  generados con `reportlab` (dependencia de test únicamente — no se usa en
  producción, solo para poder probar sin depender de un PDF real que el propietario
  aún no aportó): uno con una tabla real con grid visible (pdfplumber detecta tablas
  por líneas dibujadas, no solo por texto — se documentó ese detalle en el propio
  test tras un primer intento fallido con una tabla sin `TableStyle`), y otro que
  simula un escaneo (contenido gráfico, sin ninguna operación de texto).
- `python -m pytest tests/` — 63/63 en verde.

## Limitación reconocida (no oculta)

`pdfplumber.extract_tables()` detecta tablas por su estrategia por defecto de líneas
de grilla dibujadas. Un PDF con una tabla real pero **sin bordes visibles** (solo
espaciado/alineación, común en reportes exportados desde algunos ERPs) podría no
detectarse — el mensaje de error en ese caso ("no se detectó ninguna tabla... puede
que el reporte use texto libre") lo hace explícito y sugiere el fallback a Excel/CSV,
en vez de fallar en silencio. No validado todavía contra un PDF real de un ERP —
solo contra sintéticos, igual limitación que `sala_flujo_efectivo`/`sala_cambios_
patrimonio` (sin datos de dos períodos reales).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
