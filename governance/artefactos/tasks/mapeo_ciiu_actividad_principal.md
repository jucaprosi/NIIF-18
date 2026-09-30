# Mapeo CIIU → actividad principal — qué hace falta

## **Proyecto:** NIIF 18

**Estado:** Pendiente — bloqueada en revisión contable externa (2026-09-24)

## Estado actual del código

`sala_entidad._service.py` (`sugerir_actividad_principal`, `_SECCIONES_FINANCIACION = {"K"}`,
`_SECCIONES_INVERSION = {"L"}`) solo mapea 2 de las 21 secciones CIIU nivel 1: K
(Actividades financieras y de seguros) → `financiacion_es_actividad_principal`, L
(Actividades inmobiliarias) → `inversion_es_actividad_principal`. Las otras 19 secciones
devuelven `"NINGUNA"` implícitamente (ninguna coincide con los sets). La función ya
marca la sugerencia como `"sugerido_ciiu"` y expone una `advertencia` explícita en el
resultado; `app.py` bloquea la clasificación masiva (RF-03) hasta que el usuario
confirme o corrija.

## Qué hace falta exactamente (esto NO es una tarea de código)

Un contador debe revisar, para cada una de las 21 secciones CIIU nivel 1, si la
sugerencia DRAFT actual es correcta o si esa sección debería sugerir
`financiacion_es_actividad_principal` / `inversion_es_actividad_principal` /
ninguna de las dos — con **justificación** citando el criterio de IFRS 18 (¿la entidad
"principalmente obtiene fondos" para su actividad central, o "principalmente invierte"
en activos con retorno independiente del resto de sus recursos?) y, si aplica, el nivel
de código CIIU correcto (nivel 1 puede ser demasiado grueso — ver hallazgo abajo).

**Artefacto creado para facilitar esta revisión** (2026-09-24): `docs/mapeo_ciiu_actividad_principal_revision.xlsx`
— una hoja con las 21 secciones CIIU nivel 1 (código, descripción completa, sugerencia
DRAFT actual) y 4 columnas en blanco para que el contador complete: `Correcto_segun_contador`,
`Actividad_principal_corregida`, `Justificacion_contable`, `Evidencia_o_fuente`.
Generado directamente desde `data/ciiu.xlsx` (fuente real del proyecto, no inventado).

## Hallazgo concreto durante la preparación de este artefacto (2026-09-24)

Se verificó el riesgo ya señalado en `PRD.md` §8 ("un sector CIIU puede agrupar
entidades con giros muy distintos, ej. holdings dentro de un mismo código") contra el
catálogo real: el código **`M70` / `M7010` "Actividades de oficinas principales"**
(dentro de la sección M, "Actividades profesionales, científicas y técnicas", hoy
mapeada a `"NINGUNA"`) es donde CIIU clasifica a las **empresas holding** — entidades
cuya actividad central puede ser, en sustancia, supervisar y gestionar participaciones
en otras compañías del grupo. Dependiendo del caso, una holding real podría calificar
para `inversion_es_actividad_principal`, pero M70 también agrupa oficinas
administrativas centrales genéricas de cualquier grupo empresarial (no solo holdings de
inversión) — es exactamente el tipo de ambigüedad que requiere criterio profesional, no
una regla automática. **No se agregó M70 al mapeo DRAFT** — se deja registrado aquí como
punto específico a resolver en la revisión, en vez de decidirlo unilateralmente.

## Próximo paso

1. Enviar `docs/mapeo_ciiu_actividad_principal_revision.xlsx` a un contador para
   revisión (incluye el caso M70 como nota).
2. Con las respuestas, actualizar `_SECCIONES_FINANCIACION` / `_SECCIONES_INVERSION` en
   `sala_entidad._service.py` (o, si el contador determina que nivel 1 es insuficiente,
   extender `sugerir_actividad_principal` para aceptar códigos de nivel 2/3 en vez de
   truncar a la letra de sección).
3. Actualizar `PRD.md` RF-11 y este archivo de tarea con el resultado, y agregar tests
   que reproduzcan cada caso confirmado por el contador.

## Nota (2026-09-24): este mapeo pasó a ser parte de un alcance mayor

El propietario notó que este mapeo comparte el mismo problema que las reglas de
`sala_clasificacion` : depende de un criterio contable que
**no es estático** — un contador debe poder ajustarlo cuando cambie el criterio, sin
pedirle a un desarrollador que edite y despliegue código. Se registró como extensión de
 (ver ese archivo para el diseño completo: interfaz de
edición en la app, persistencia real, auditoría). El paso 1 de arriba (envío del
checklist para la primera revisión) sigue siendo válido y necesario de inmediato —
 es la solución de largo plazo para que los ajustes
*siguientes* no requieran otra vez editar `_service.py`.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
