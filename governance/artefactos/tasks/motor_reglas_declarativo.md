# Motor de reglas de clasificación como tabla declarativa

## **Proyecto:** NIIF 18

**Estado:** Pendiente — plan (2026-09-23, v3.7), no implementado

## Origen

Reunión de producto — Roberto: "la NIIF 18 establece reglas fijas de agregación y
desagregación, por lo que se deben programar en una tabla de comandos o parametrización
para mitigar el error humano y no depender del criterio del contador."

## Estado actual

`sala_clasificacion/_service.py` implementa el árbol de decisión (`PRD.md` §3) con listas
de palabras clave **hardcodeadas en Python** (`_PALABRAS_BALANCE`,
`_PALABRAS_MOVIMIENTO_PL`, `_PALABRAS_FINANCIACION`, `_PALABRAS_INVERSION`,
`_PALABRAS_INTERES_SIEMPRE_FINANCIACION`, `_PALABRAS_METODO_PARTICIPACION`, etc.) y
prefijos de código de cuenta (`cta.startswith(('1','2','3'))`). Funciona y está
verificado contra datos reales , pero **cambiar
una regla requiere editar código Python y desplegar** — no es auditable ni ajustable por
un contador sin conocimientos de programación.

## Qué implicaría implementarlo

- Extraer las listas `_PALABRAS_*` y los prefijos de código a una tabla de datos externa
  (CSV/YAML/JSON versionado en el repo, o una tabla en base de datos si la app crece a
  multiusuario) — cada fila: patrón (palabra clave o prefijo), categoría candidata,
  condición (paso del árbol §3 al que aplica), fuente normativa que la respalda.
- `sala_clasificacion.clasificar_partida` pasaría de tener las reglas escritas en código
  a **leerlas** de esa tabla en tiempo de ejecución — el árbol de decisión (el orden de
  los 7 pasos, que sí es normativo y no debe ser editable por un usuario) se mantiene en
  código; solo las listas de palabras clave se externalizan.
- Una interfaz (nueva pestaña en `app.py`, o un archivo editable con validación) para que
  un contador con permisos pueda agregar/editar patrones sin tocar Python — con el mismo
  patrón de auditoría ya usado en `sala_auditoria` (quién cambió qué regla, cuándo, por
  qué).

## Por qué no se implementa ya

Es un cambio arquitectónico grande (afecta el corazón de `sala_clasificacion`, ya
verificado exhaustivamente esta sesión contra `TB_ERP` real) — antes de tocarlo:

1. Debe decidirse el formato de la tabla de reglas (no es obvio — depende de si la app
   seguirá siendo de sesión única en Streamlit o crecerá a multiusuario con persistencia).
2. Debe preservarse la cobertura de test actual (44 tests, incluyendo el de integración
   que fija los subtotales exactos de `ER_NIIF18`) — cualquier refactor a reglas
   declarativas debe pasar la misma suite sin cambiar ningún resultado.
3. Riesgo de regresión alto si se apura: el árbol §3 ya tuvo 2 bugs reales encontrados y
   corregidos esta sesión (método de participación, cuentas de balance con vocabulario de
   flujo) — mover la lógica a una capa de datos sin la misma disciplina de verificación
   podría reintroducirlos silenciosamente.

## Extensión (2026-09-24): mismo mecanismo cubre también el mapeo CIIU → actividad principal (y, a futuro, FINREP)

Origen: al preparar la revisión contable de , el
propietario notó que ese mapeo tiene **el mismo problema estructural** que las listas
`_PALABRAS_*` de este task — hoy `_SECCIONES_FINANCIACION = {"K"}` /
`_SECCIONES_INVERSION = {"L"}` en `sala_entidad/_service.py` también son constantes
Python hardcodeadas, y también dependen de un criterio contable que **no es estático**
(cambia con jurisprudencia, políticas internas, corrección de casos mal mapeados como
el de holdings/`M70` documentado en ).

Decisión: en vez de construir dos soluciones separadas (una tabla declarativa para
`sala_clasificacion` y otra distinta para `sala_entidad`), **este mismo motor de reglas
declarativas debe cubrir ambos mapeos** — y, cuando se implemente, el
mapeo NIIF18→FINREP también, porque es el mismo patrón otra vez (una tabla
código/patrón → categoría, mantenida por criterio profesional, no por lógica de árbol
normativo). El árbol de 7 pasos (§3) y el orden de evaluación siguen siendo normativos y
NO editables por el usuario; lo que se externaliza son las listas de patrones/códigos
que alimentan cada paso.

**Requisito nuevo que esto agrega al alcance** (no estaba en la versión original de este
task): una **interfaz de edición dentro de la app**, no solo un archivo de datos
versionado en el repo — el propietario pidió explícitamente "un campo para ello en la
app" porque el criterio cambia con el tiempo y un contador debe poder ajustarlo sin
pedirle a un desarrollador que edite y despliegue código. Esto implica:

- Una pestaña nueva (o sección de configuración) en `app.py`, con acceso restringido a
  un rol con permiso — no cualquier usuario, porque un cambio aquí afecta la
  clasificación de **todas** las entidades que usen la app, no solo la sesión actual.
- **Persistencia real entre sesiones** — hoy la app es 100% `st.session_state` de
  Streamlit (se pierde al cerrar la sesión); esta es la primera funcionalidad del
  proyecto que necesita sobrevivir más allá de una sesión. Requiere decidir el mecanismo
  (archivo versionado en el repo con control de acceso a nivel de OS/git, o una base de
  datos real si la app crece a multiusuario) — la misma pregunta que ya estaba abierta
  en "Por qué no se implementa ya" (punto 1), ahora con una respuesta más concreta: sí
  hace falta persistencia, no es opcional para este caso de uso.
- Auditoría de cada cambio vía `sala_auditoria` (quién cambió qué patrón/sección CIIU,
  cuándo, justificación) — mismo patrón ya usado para cambios de clasificación por
  cuenta (RF-10), extendido a cambios de regla en vez de cambios de dato.

## No implementado — solo documentado

Este archivo registra el plan para que quede trazable en `VPA_MAP.md`/`TASKS.md`. No se
ha escrito código.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
