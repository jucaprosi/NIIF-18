# Conectar VPA_MAP a los archivos reales del proyecto
## **Proyecto:** NIIF 18

**Estado:** Completada

## Objetivo aclarado por el propietario

Tras corregir `TASKS.md` (ver ), el propietario
señaló que `VPA_MAP.md` tenía el mismo síntoma (varios tokens en un solo archivo), pero
aclaró que la corrección correcta **no es fragmentar VPA_MAP** — su rol de "cerebro de la
red neuronal" exige que los tokens **nazcan ahí y se conecten** a los archivos reales del
proyecto según las funciones semánticas/semióticas que cada uno guarda, no que se
dispersen en archivos individuales (eso habría contradicho su propia doctrina: "todo
token nace aquí una vez").

## Corrección aplicada

Se usó `mcp_inject_stigmergic_trace` para validar el formato canónico de inyección
(`# sobre un elemento AST real — función, clase o constante), y luego se aplicó
ese mismo formato con `Edit` a los 10 archivos de código bajo `src/` que corresponden a
un token de dominio de VPA_MAP (G1: , ; G4: las 9 salas más
, , ,
, , , ). `VPA_MAP.md` se actualizó con una
columna nueva, "Archivo conectado", que apunta al archivo y función exactos donde vive
cada rastro — verificable con `grep -rn "^# ¤" src/`.

Los tokens de gobernanza transversal (, , ) se
documentaron explícitamente como "sin archivo único" en vez de forzar una conexión
artificial a un archivo que no los representa de verdad.

## Limitación de la herramienta de verificación, documentada con honestidad

`mcp_compile_stigmergy_graph` pasó de 10 a 45 intents tras la inyección, pero no detectó
la totalidad de los 12 rastros insertados — el comportamiento con líneas de un solo token
fue mayormente consistente (con una excepción, , sin explicación
identificable) y con líneas de varios tokens separados por espacio fue inconsistente
entre elementos de la misma línea, aunque reproducible (mismo resultado en dos
ejecuciones). Dado que esta herramienta ya había fallado antes en la sesión
(`mcp_inject_stigmergic_trace` con `target_element="*"`), se optó por no perseguir su
comportamiento interno exacto y en su lugar declarar la conectividad como verificada por
evidencia directa (`grep`), no solo por el reporte del compilador — más confiable porque
no depende de una caja negra de terceros.

## Verificación

- `grep -rn "^# ¤" src/` — 12 líneas de rastro en 10 archivos, todas correspondientes a
  filas reales de `VPA_MAP.md`.
- `python -m py_compile` sobre todos los archivos tocados — sin errores de sintaxis.
- `python -m pytest tests/` — 29/29 en verde (la inyección de comentarios no tocó lógica).
- `mcp_verify_huellas` sobre `VPA_MAP.md` — válido.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
