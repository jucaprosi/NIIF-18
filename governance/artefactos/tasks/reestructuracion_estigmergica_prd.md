# Reestructuración de `PRD.md` bajo la gramática de linaje ZERAG

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-24, v3.8)

## Pregunta/pedido del propietario

"Como ya se está operando bajo trazabilidad estigmérgica, debemos rediseñar el PRD,
analiza el archivo `C:\Users\Juan Carlos\Desktop\ZERAG\governance\nucleo\GLOSARIO.md`,
los rastros van luego de los markdowns y se agrega un cierre... se necesita refactorizar
el PRD para que las funcionalidades de la app estén segmentadas por markdowns y que su
rastro gobierne su trazabilidad."

## Gramática aplicada (fuente: `GLOSARIO.md` de otro proyecto, ZERAG)

- El rastro va en su propia línea, inmediatamente después del encabezado
  que gobierna, y rige todo el contenido hasta el siguiente encabezado del **mismo
  nivel**.
- El cierre se aplica **exclusivamente a encabezados H2** (`##`) — los
  niveles H3+ no llevan rastro ni cierre propio, su subordinación queda implícita por
  jerarquía markdown.

## Qué se hizo

`PRD.md` completo (0-12) se reestructuró para que cada sección `##` lleve su rastro en
línea propia (antes varios tokens estaban pegados al texto del encabezado, ej. `## 3.
Árbol de Decisión... \`) y su cierre correspondiente. Para lograr
que **cada funcionalidad esté segmentada por su propio markdown** (pedido explícito), se
promovieron a H2 todas las subsecciones H3 que describían una funcionalidad o hallazgo
distinto y antes carecían de rastro propio:

- Los wrappers `## 2. Modelo de Datos` y `## 5. Requisitos Funcionales` se retiraron —
  sus hijos (§2.1, §2.2, §2.3; RF-01 a RF-11) pasaron a ser H2 directos.
- §9.1, §9.2, §11.1-11.4, §12.1-12.4 pasaron de H3 a H2, cada uno con su propio rastro.

## Decisión de nomenclatura (no se importó todo de ZERAG)

Los tokens **ya conectados físicamente a código** (`# en `src/`, verificable con
`grep -rn "^# ¤" src/`) conservaron su nombre exacto con separador `_` — renombrarlos al
separador `-` de ZERAG habría roto esa conexión física ya verificada sin ningún
beneficio real. Los tokens nuevos de esta reestructuración (secciones puramente
narrativas: changelog, visión, roadmap, riesgos, arquitectura, contexto UE, plan de
reunión) también usan `_` por consistencia interna del proyecto — no se adoptó el
separador `-` de ZERAG. Tampoco se importó ningún otro contenido normativo de ZERAG
(roles `¤¤`, candados `¤¬`, invariantes `¤¦`, Contrato Bilateral) — el `PRD.md`
reestructurado incluye una nota explícita de este alcance acotado en su cierre.

## Registro en `VPA_MAP.md`

Los tokens narrativos nuevos se registraron como grupo **G5** (documentación, sin
contraparte en `src/`) — distinto de G4 (dominio de negocio, con archivo de código
conectado) — para no forzar una fila de "Archivo conectado" falsa. Ver
`governance/artefactos/VPA_MAP.md`.

## Verificación

- `grep -n "^##" governance/artefactos/PRD.md` — cada resultado H2 tiene su línea de
 rastro inmediatamente debajo y su cierre antes del
  siguiente `---`.
- Todo el contenido normativo/técnico preexistente se preservó textualmente — esta tarea
  fue de reestructuración de encabezados y ubicación de tokens, no de reescritura de
  contenido.
- `python -m pytest tests/` — sin cambios de código, 44/44 sigue en verde (esta tarea no
  tocó `src/`).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
