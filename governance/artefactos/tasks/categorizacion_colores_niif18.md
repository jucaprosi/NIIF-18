# Paleta de colores y renombrado de categorías NIIF 18

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-23, v3.7)

## Origen

Reunión de producto (Roberto/Giovanni/Juan Carlos): "utilizar colores diferenciadores
para las categorías (operación, financiamiento, inversión, actividades discontinuas e
impuesto a las ganancias)". El propietario compartió una imagen de referencia (mockup de
la matriz de reclasificación) con colores ya aplicados a 2-3 categorías, y pidió aplicar
esa paleta y renombrar las categorías.

## Extracción de la paleta (metodología, no adivinada)

Se hizo muestreo de píxeles directo sobre la imagen compartida (`PIL.Image.getpixel`
en grilla) para extraer valores RGB reales en vez de estimar visualmente:

- **Operación** (verde): confirmado por muestreo, ~rgb(190,220,175) → `#BBDCA0`
- **Inversión** (naranja/durazno): confirmado por muestreo, ~rgb(247,174,131) → `#F6AE86`
- **Financiación** (azul): parcialmente visible en el borde inferior del recorte,
  ~rgb(156,194,233) → `#9CC5EA`
- **Impuestos a las Ganancias** y **Discontinuadas**: no visibles en el recorte
  compartido (la imagen se cortaba antes de esas secciones) — se extendieron siguiendo
  el mismo estilo pastel/ocre observado (ocre `#E6C79C` para Impuestos, rojo/vino pastel
  `#E8AFAF` para Discontinuadas). **Quedan sujetos a confirmación** si el propietario
  comparte el resto de la guía o la "guía oficial del IASB" que Roberto mencionó en la
  reunión (ver nota de precaución abajo).
- **Balance General** (no es parte del Estado de Resultados): gris neutro `#E4E4E4`.

## Nota de precaución (para la exposición del propietario)

Roberto mencionó compartir "la guía oficial del IASB que define las paletas de colores
normativas (tonos ocre y pasteles)". Esa guía **no se ha recibido ni verificado** en este
proyecto. Hasta donde se investigó, el IASB no publica una paleta de colores normativa
para NIIF 18 — el estándar regula presentación y subtotales, no estilo visual. Se
recomienda presentar la paleta actual como **convención de producto propia** en la
exposición, no como "requisito oficial IASB", hasta verificar la fuente que Roberto
ofreció compartir.

## Implementación

- `src/sala_catalogo/_service.py`: nuevo diccionario `COLORES_NIIF18` (fondo + texto por
  categoría), agregado a `__all__`.
- `src/sala_catalogo/_service.py`: categorías renombradas a forma corta — se conserva el
  prefijo numérico "N." (del que dependen `sala_clasificacion`/`sala_estados_financieros`
  vía `.str.startswith('N.')`), se elimina la descripción entre paréntesis.
- `src/sala_clasificacion/_service.py`: las constantes `CATEGORIA_OPERACION`,
  `CATEGORIA_INVERSION`, etc. ahora se derivan por posición de
  `cat_svc.CATEGORIAS_NIIF18` en vez de redefinir los literales — elimina el riesgo de
  que un renombrado futuro se aplique en un archivo y no en el otro (root-cause fix
  aprovechando el cambio, no solo el rename pedido).
- `src/app.py`: nuevas funciones `chip_categoria()` y `leyenda_colores_niif18()` — un
  chip HTML con el color oficial de la categoría se muestra como leyenda en la Matriz de
  reclasificación y como encabezado de cada desglose del Árbol de EEFF. Streamlit no
  permite combinar `column_config` con un `Styler` de color por celda en el mismo
  `st.dataframe`, así que el color se aplica a nivel de sección, no por fila individual
  de la tabla — decisión de diseño, no limitación oculta.
- Tests: los 3 archivos de test que usaban los nombres largos de categoría como literales
  (`test_sala_auditoria.py`, `test_sala_estados_financieros.py`,
  `test_sala_validacion.py`) se actualizaron a los nombres cortos por consistencia
  (no eran necesarios para que pasaran, pero evitan confusión futura).

## Verificación

- `python -m pytest tests/` — 44/44 en verde.
- App verificada en navegador (Streamlit corriendo, sin errores en consola/logs del
  servidor) — no se pudo probar la carga de archivo real por el diálogo nativo del SO,
  fuera del alcance del navegador embebido de esta sesión.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
