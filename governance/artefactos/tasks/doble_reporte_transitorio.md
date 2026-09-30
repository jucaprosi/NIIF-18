# Doble reporte transitorio (periodo interino EBA)

## **Proyecto:** NIIF 18

**Estado:** Pendiente — nueva (2026-09-23)

## Origen

Detectada en el análisis de brecha entre la herramienta y el documento de exposición del
propietario: el `Opinion EBA/Op/2026/07` (ver `PRD.md` §11.2, `FUENTES_Y_BIBLIOGRAFIA.md`)
describe un **periodo de transición** para entidades supervisadas en la UE — entre el
endoso de IFRS 18 (13-feb-2026) y la fecha de aplicación del ITS sobre FINREP
(~fin sept-2027), las entidades pueden necesitar reportar **tanto en formato antiguo
(NIC 1 / FINREP pre-IFRS18) como en el nuevo (IFRS 18 / FINREP revisado)**
simultáneamente.

## Estado actual

No implementado. `sala_reportes` (`RF-09`) genera un único Estado de Resultados, en el
formato NIIF 18 de este proyecto (§2.2, 3 subtotales mandatorios) — no existe una
plantilla "formato antiguo" (NIC 1, con sus propios subtotales/estructura) para generar
en paralelo.

## Alcance real de este gap (importante, no sobrevender)

Esta funcionalidad **solo es relevante para entidades supervisadas en la UE bajo
FINREP** (bancos y entidades de crédito reguladas por la EBA) — el público objetivo
declarado de este proyecto (`PRD.md` §1) es una entidad genérica, no necesariamente
bancaria ni europea. Antes de invertir en esto, se debe confirmar con el propietario si
el mercado objetivo real incluye entidades bajo supervisión EBA (mismo criterio ya
aplicado a : "no iniciar sin confirmar mercado objetivo").

## Qué implicaría implementarlo

- Un segundo motor de presentación (no de clasificación — las partidas ya clasificadas
  bajo NIIF 18 se pueden volver a agrupar bajo la estructura NIC 1 antigua) en
  `sala_reportes` o una sala nueva dedicada.
- Requiere el mapeo inverso: de las 5 categorías NIIF 18 de vuelta a la agrupación NIC 1
  (que no tenía categorías obligatorias formales, por lo que el mapeo "inverso" es en
  realidad una convención de la entidad, no una regla NIIF).
- Marcar en la UI/exportación cuál de las dos salidas es la "oficial" para el periodo,
  según la fecha de aplicación efectiva de la entidad.

## No implementado — solo documentado

Este archivo registra el gap para que quede trazable en `VPA_MAP.md`/`TASKS.md`. No se
ha escrito código. Recomendado: no priorizar hasta confirmar si el mercado objetivo
incluye entidades supervisadas por la EBA (ver `PRD.md` §11.3).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
