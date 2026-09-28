# Reexpresión retrospectiva de periodos comparativos (NIC 8)

## **Proyecto:** NIIF 18

**Estado:** Pendiente — nueva (2026-09-23)

## Origen

Detectada en el análisis de brecha entre la herramienta y el documento de exposición del
propietario ("El problema que resuelve la herramienta", punto "Aplicación
retrospectiva"): conforme a la **NIC 8** (*Políticas Contables, Cambios en las
Estimaciones Contables y Errores*), una entidad que adopta NIIF 18 debe **reexpresar**
sus periodos comparativos bajo las nuevas categorías/subtotales, no solo señalar que
hace falta.

## Estado actual

`RF-07` (`PRD.md` §5) genera comparativos entre 2+ periodos **con las mismas
categorías**, y su criterio de aceptación dice: *"si un periodo comparativo fue
preparado antes de la reclasificación NIIF 18, el sistema señala explícitamente que
requiere reexpresión"* — es decir, hoy el sistema **detecta y advierte**, pero no
**recalcula**. La reexpresión real queda como trabajo manual del usuario.

NIC 8 no está citada en `FUENTES_Y_BIBLIOGRAFIA.md` — consistente con que esta
funcionalidad no se ha investigado ni implementado todavía.

## Qué implicaría implementarlo

- Tomar una balanza de un periodo comparativo (potencialmente ya en formato NIC 1
  antiguo, con su propia agrupación de partidas) y correrla por el mismo árbol de
  clasificación de `sala_clasificacion` (§3) para obtener las categorías NIIF 18
  equivalentes.
- Requiere que el periodo comparativo tenga el mismo nivel de detalle por cuenta que el
  periodo actual (no solo los subtotales ya agregados) — si el comparativo solo existe
  ya resumido (como `ER_NIIF18` del archivo de prueba), no hay partidas que reclasificar.
- Añadir un flag `es_reexpresado` / `metodo_reexpresion` a la estructura de periodo
  comparativo, para que quede auditable qué periodos fueron reexpresados por el sistema
  vs. capturados ya en formato NIIF 18 originalmente.

## Riesgo normativo

Requiere validar contra el texto oficial de NIC 8 (párrafos de aplicación retrospectiva)
y contra el propio NIIF 18 (disposiciones transitorias) antes de implementar — mismo
criterio que . No iniciar sin esas fuentes.

## No implementado — solo documentado

Este archivo registra el gap para que quede trazable en `VPA_MAP.md`/`TASKS.md`. No se
ha escrito código.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
