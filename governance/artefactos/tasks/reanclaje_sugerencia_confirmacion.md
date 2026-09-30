# Re-anclaje de ¤sugerencia_confirmacion_actividad_principal como nodo de código

## **Proyecto:** NIIF 18

**Estado:** Pendiente — nueva (2026-09-30)

## Origen

`¤sugerencia_confirmacion_actividad_principal` está anclado como comentario suelto sobre
un `if entidad:` en `src/app.py:228` — no sobre un `def`/`class`/constante. El AST walker
de `stigmergy_engine.py` (ZERAG) no genera nodo de código para ese caso: `get_anchor()`
devuelve `None` y el cálculo de `alcance` del triaje reporta `archivos_codigo: 0` para
este rastro, aunque el ancla física sí existe (ver `H-196` en `APORTES_INEDITOS.md` de
ZERAG). Confirmado en dos delegaciones reales a Antigravity: el triaje no señaló `src/`
como parte del alcance, y la IA tuvo que redescubrirlo por su cuenta vía grep manual —
funcionó, pero sin la señal que el sistema de rastros debería dar.

## Qué implicaría corregirlo

Extraer el bloque de sugerencia+confirmación (`src/app.py:228-271`, el contenedor con el
CIIU inferido, los checkboxes `chk_fin_principal_*`/`chk_inv_principal_*` y el botón de
confirmación) a una función nombrada propia (p. ej. `renderizar_confirmacion_actividad_principal`)
para que el AST walker sí la detecte como `FUNCTION` y el rastro se resuelva en
`get_anchor()`/`alcance` del triaje.

## Por qué no se hace ahora

El bloque usa variables del scope circundante (`ruc_buscado`, `entidad`) y es código de
producción ya probado (68/68 tests, verificado en dos delegaciones reales) — extraerlo
implica pasar esas variables como parámetros y retocar un flujo que hoy funciona
correctamente. El riesgo de una regresión no se justifica solo para resolver una
limitación del compilador que ya tiene mitigación funcional (grep encuentra el rastro
igual, la IA delegada lo usó sin bloquearse dos veces seguidas).

## No implementado — solo documentado

Este archivo registra el gap para que quede trazable en `VPA_MAP.md`/`TASKS.md`. No se
ha escrito código.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
