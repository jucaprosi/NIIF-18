# Estado de Resultado Integral — detección de Otro Resultado Integral (ORI)

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-25, v3.13)

## Origen

Durante la implementación de RF-12/13/14, el propietario preguntó cómo usar la misma
balanza para los 4 estados. Al responder, se aclaró que las 5 categorías de NIIF 18
(Operación/Inversión/Financiación/Impuestos/Discontinuadas) son exclusivas del Estado
de Resultados — los otros 3 estados tienen sus propias normas. El propietario respondió
que, según su contador, "las 5 categorías trabajan con el estado de resultado
integral" — es decir: falta la pieza del **Otro Resultado Integral (ORI)** para que el
Estado de Resultados calculado hoy (`sala_estados_financieros`) sea realmente el Estado
de Resultado Integral completo que exige NIC 1.81A / NIIF 18.

Antes de programar nada, se confirmó con el propietario (`AskUserQuestion`) el alcance
exacto: detectar ORI automáticamente a partir de `sala_cambios_patrimonio` (movimientos
de reserva no explicados por utilidad/dividendos), no pedirle al contador que lo marque
manualmente cuenta por cuenta (opción descartada por el propietario).

## Qué es el ORI y por qué no se ve en la balanza de resultados

El ORI (revaluación de propiedades, diferencias de conversión, remediciones de planes
de beneficios definidos, entre otros) casi nunca pasa por una cuenta de ingreso/gasto —
por diseño de las NIIF, se reconoce directamente en una cuenta de **reserva del
Patrimonio**, sin pasar por el Estado de Resultados como tal. Por eso no podía
detectarse desde `sala_clasificacion` (que solo ve cuentas 4.x/5.x) — la única forma de
verlo es comparando el Patrimonio de Año 1 contra Año 2, que es exactamente lo que
`sala_cambios_patrimonio` ya hacía.

## Implementación

- `src/sala_cambios_patrimonio/_service.py`: nueva `calcular_resultado_integral(df_conciliacion,
  resultado_neto)`. Toma la salida de `construir_cambios_patrimonio` (ya existente) y
  suma la columna `Aportes_Y_Otros_Movimientos` de las cuentas que **no** son capital
  contribuido ni resultados acumulados — esas son los candidatos a ORI.
- **Exclusión explícita de reserva legal/estatutaria** (`_PALABRAS_NO_ORI`): en Ecuador,
  la reserva legal se nutre por apropiación desde Resultados Acumulados (un traslado
  interno del patrimonio, no una ganancia nueva) — si no se excluyera, se contaría como
  ORI por error. Cualquier otra reserva no reconocida por las palabras clave actuales
  requiere confirmación del contador antes de reportarse como ORI — heurística DRAFT,
 mismo criterio que el resto del proyecto .
- `app.py`: nueva sección "Estado de Resultado Integral" dentro de la sub-pestaña
  Cambios en Patrimonio (requiere el mismo comparativo Año1/Año2), con desglose de ORI
  por cuenta en un expander explícito ("confirme con su contador antes de reportar").

## Verificación

- 2 tests nuevos en `tests/test_sala_cambios_patrimonio.py`, con un escenario que
  incluye a la vez una reserva de revaluación (ORI real, $30) y una reserva legal
  ($15, que debe excluirse) — confirma que el motor distingue correctamente entre
  ambas, no solo que "algo suma".
- `python -m pytest tests/` — 68/68 en verde.
- App verificada: importa sin errores con la nueva sección conectada.

## Pendiente / riesgo señalado

La lista `_PALABRAS_NO_ORI` es un punto de partida, no una lista exhaustiva — un
contador debe revisarla contra el catálogo de cuentas real del cliente antes de
producción, igual criterio que el mapeo CIIU. No validado contra un caso real de dos
períodos (mismo motivo que `sala_flujo_efectivo`/`sala_cambios_patrimonio` en general).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
