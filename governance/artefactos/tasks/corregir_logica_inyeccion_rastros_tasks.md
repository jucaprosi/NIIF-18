# Corregir lógica de inyección de rastros en TASKS.md
## **Proyecto:** NIIF 18

**Estado:** Completada

## Problema detectado por el propietario

`governance/artefactos/TASKS.md` era un único archivo con ~27 tareas como texto en
negrita dentro de una lista plana (`- [x] **:** texto...`). Los demás artefactos
vivos (`PRD.md`, `INVARIANTS.md`, `VPA_MAP.md`, `FUENTES_Y_BIBLIOGRAFIA.md`,
`APORTES_INEDITOS.md`) sí siguen el patrón de "un archivo, un token raíz en el
encabezado H1". `TASKS.md` era la excepción, y eso tenía una consecuencia técnica real,
no solo estética.

## Causa raíz verificada (no asumida)

Antes de tocar nada, se ejecutó `mcp_compile_stigmergy_graph` para confirmar el
síntoma: de las ~27 tareas de `TASKS.md`, el grafo solo detectaba **2** como nodos
individuales ( y ) — y
solo porque esos dos tokens *también* aparecían citados dentro de comentarios de código
Python real (`sala_entidad/_service.py`, `sala_validacion/_service.py`), que el
compilador sí escanea vía AST. El resto de tareas, al vivir únicamente como texto en
negrita dentro de un archivo con un solo encabezado H1 , eran
invisibles para el grafo: el compilador registra como máximo un token por archivo desde
el nivel Markdown, más lo que encuentre vía AST en `.py`. Ningún token de tarea
individual podía recibirse como blanco de `mcp_inject_stigmergic_trace` porque no tenía
su propio "lugar" (archivo) al que ese rastro perteneciera de forma inequívoca.

## Corrección aplicada (reestructuración, no parche)

Se dividió `TASKS.md` en `governance/artefactos/tasks/<token>.md` — un archivo por
tarea, cada uno con su propio encabezado H1 # Título , estado, cuerpo
completo (migrado sin pérdida de contenido) y pie de copyright, igual patrón que el
resto de artefactos vivos. `TASKS.md` pasó a ser el **índice**: una tabla con estado,
token, resumen de una línea y enlace al archivo completo — sigue siendo legible de un
vistazo, pero cada tarea ahora es una unidad de archivo independiente.

## Verificación exógena

Se volvió a ejecutar `mcp_compile_stigmergy_graph` después del cambio. Resultado: pasó
de 2 tokens de tarea detectados individualmente a las ~27 tareas apareciendo como nodos
propios del grafo (ver cifra exacta en el resultado de la verificación de esta sesión).
Esto confirma la causa raíz y la corrección — no fue una suposición sin comprobar.

## Nota de alcance

No se tocó el contenido de ninguna tarea al migrarla — es una reestructuración
estructural (dónde vive el texto), no una revisión de su contenido. Las tareas
marcadas `[x]` siguen siendo un registro histórico inmutable; las `[ ]`/`[~]` siguen
pendientes exactamente con los mismos bloqueos ya documentados.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
