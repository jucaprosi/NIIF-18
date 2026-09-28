# Discrepancia entre el motor real y `ER_NIIF18` esperado — RESUELTA

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-23, v3.6)

## Hallazgo original (v3.4/3.5, sin resolver)

Ejecutando el motor real (`sala_clasificacion` + `sala_estados_financieros`) sobre la
hoja `TB_ERP` de `balance_prueba_niif18_sap_business_one.xlsx`, el resultado reproducido
era Resultado operativo $123,000 / Antes de fin. e imp. $208,000 / Resultado del período
-$140,000 — muy por debajo de la respuesta esperada en `ER_NIIF18` ($813,000 / $898,000
/ $550,000).

## Diagnóstico (verificado contra datos reales, no una suposición)

Se comparó la clasificación del motor cuenta por cuenta contra `MAPEO_NIIF18` (hoja de
respuesta esperada por cuenta del mismo archivo). Todas las 26 cuentas 4.x/5.x (las
cuentas de resultados reales) clasificaban **correctamente** — cada reclasificación
esperada (intereses de depósitos → Inversión, participación en asociada → Inversión,
ganancia cambiaria de préstamo → Financiación, etc.) coincidía exactamente.

La causa real estaba en **4 cuentas de BALANCE** (prefijo de código 1.x/2.x) que
**se filtraban al Estado de Resultados por error**:

| Cuenta | Descripción | Saldo |
|---|---|---|
| `1.1.02.099` | Deterioro acumulado de cartera | -40,000 |
| `1.2.01.102` | Depreciación acumulada edificios | -240,000 |
| `1.2.01.103` | Depreciación acumulada maquinaria | -330,000 |
| `2.2.03.001` | Provisión por litigios | -80,000 |

Suma: **-690,000** — exactamente la diferencia entre el resultado operativo esperado
($813,000) y el obtenido ($123,000): `813,000 - 123,000 = 690,000`.

**Causa raíz**: en `sala_clasificacion._service.clasificar_partida`, el Paso 0 (filtro
de Balance General) tenía DOS señales distintas para detectar una cuenta de balance —
(a) el código empieza con 1/2/3 (convención de plan de cuentas, señal fuerte) y (b) la
descripción contiene una palabra de balance como "pasivo" (señal débil y ambigua). Existía
un rescate por `_PALABRAS_MOVIMIENTO_PL` (si la descripción también menciona
"gasto"/"interés"/"depreciación"/"provisión"/etc., no se excluye) — agregado
correctamente en una sesión anterior para el caso real "Interés neto de pasivo por
beneficios definidos" (una cuenta de GASTO, código `630200`, que solo caía en la
categoría de balance por mencionar "pasivo" en su descripción).

El bug: el rescate se aplicaba **también** cuando el disparador era la señal fuerte (a)
— código 1/2/3 — no solo la señal débil (b). Eso dejaba pasar cuentas de balance
legítimas cuyo nombre usa vocabulario de flujo por convención contable ("Depreciación
**acumulada**", "Deterioro **acumulado**", "Provisión por litigios") aunque representan
el saldo acumulado (una cuenta de balance), no el movimiento del período (que ya tiene
su propia cuenta de gasto separada, p. ej. "Depreciación edificios" `5.2.03.001`, ya
presente y correctamente clasificada).

## Corrección aplicada (root-cause, no parche)

`src/sala_clasificacion/_service.py`, Paso 0: se separaron explícitamente las dos
señales (`_por_codigo`, `_por_palabra_balance`) y el rescate por
`_PALABRAS_MOVIMIENTO_PL` ahora **solo** aplica cuando el disparador fue la descripción
(b) — nunca cuando el código de cuenta (a) ya lo clasificó como balance de forma
inequívoca:

```python
_por_codigo = cta.startswith(('1', '2', '3'))
_por_palabra_balance = any(w in desc for w in _PALABRAS_BALANCE)
if _por_codigo or _por_palabra_balance:
    if _por_codigo or not any(w in desc for w in _PALABRAS_MOVIMIENTO_PL):
        return CATEGORIA_BALANCE_GENERAL
```

## Verificación

- 4 tests unitarios nuevos en `tests/test_sala_clasificacion.py` (los 3 casos reales de
  la tabla arriba + un test de guarda que confirma que el caso original que motivó
  `_PALABRAS_MOVIMIENTO_PL` sigue funcionando).
- 1 test de integración de extremo a extremo nuevo en
  `tests/test_sala_importacion_hojas_reales.py`
  (`test_motor_completo_sobre_tb_erp_reproduce_er_niif18_esperado`): corre importación →
  clasificación → subtotales sobre `TB_ERP` real y fija los 3 subtotales exactos de
  `ER_NIIF18` ($813,000 / $898,000 / $550,000) — **coinciden al centavo** tras la
  corrección.
- `python -m pytest tests/` — 44/44 en verde (43 previos + 1 nuevo de integración; los 4
  tests unitarios ya estaban contados en los 43).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
