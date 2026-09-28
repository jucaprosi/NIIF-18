# Desagregación inteligente de partidas genéricas

## **Proyecto:** NIIF 18

**Estado:** Pendiente — nueva (2026-09-23)

## Origen

Detectada en el análisis de brecha entre la herramienta y el documento de exposición del
propietario: NIIF 18 exige desagregar partidas materiales que hoy suelen agruparse bajo
etiquetas genéricas ("Otros", "Gastos varios") cuando esa agregación oculta información
relevante para el usuario de los estados financieros.

## Evidencia real de que el gap existe

El propio archivo de prueba (`balance_prueba_niif18_sap_business_one.xlsx`, hoja
`MAPEO_NIIF18`) trae la cuenta `5.2.99.001` "Gastos varios" con la anotación explícita
**"Debe desagregarse; contiene partidas distintas"** (confianza "Media", evidencia
requerida "Revisar contrato/origen del rendimiento"). El motor actual
(`sala_clasificacion.clasificar_partida`) clasifica esta cuenta como Operación
correctamente en cuanto a categoría, pero **no detecta ni señala** que la partida es
candidata a desagregación — se trata igual que cualquier otra cuenta ya suficientemente
específica.

## Qué implicaría implementarlo

- Un heurístico (o una regla explícita) que detecte nombres de cuenta genéricos:
  palabras como "varios", "otros", "diversos", "generales" en la descripción, o un umbral
  de materialidad (partida grande en monto pero sin desglose por debajo de ella en el
  catálogo de cuentas).
- Señalar la partida en la UI (similar a como `sala_validacion` ya señala cuentas sin
  categoría) para que el preparador decida si desagregar manualmente o justificar por
  qué no es material.
- **No** intentar desagregar automáticamente sin intervención humana — desagregar una
  partida genérica en sub-componentes requiere el mismo criterio profesional que ya rige
  el resto del árbol de clasificación (`PRD.md` §3, "el juicio profesional del preparador
  sigue siendo la autoridad final").

## Riesgo

El umbral de "qué es material" no está definido en NIIF 18 de forma numérica — es un
juicio profesional caso por caso. Cualquier heurístico automático debe presentarse como
sugerencia, no como regla vinculante, siguiendo el mismo patrón ya usado en RF-11
(sugerencia + confirmación obligatoria del usuario).

## No implementado — solo documentado

Este archivo registra el gap para que quede trazable en `VPA_MAP.md`/`TASKS.md`. No se
ha escrito código.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
