# Validar que la hoja seleccionada sea realmente una balanza
## **Proyecto:** NIIF 18

**Estado:** Completada

## Pregunta del propietario

"¿Por qué cambian los resultados de acuerdo a la pestaña del balance de Excel? ¿Acaso no
es una reclasificación única?"

## Diagnóstico (no una suposición — verificado contra datos reales)

Para una misma hoja, la reclasificación **sí es determinista** — el mismo archivo y
pestaña siempre producen el mismo resultado. El problema real es otro: el archivo de
prueba `balance_prueba_niif18_sap_business_one.xlsx` (raíz del repo) trae 8 pestañas con
contenido **completamente distinto**, no la misma balanza repetida:

| Pestaña | Qué es realmente |
|---|---|
| `TB_ERP` | La balanza de comprobación real |
| `MAPEO_NIIF18` | La respuesta esperada (ya trae la categoría NIIF 18 correcta) |
| `ER_NIIF18` | El Estado de Resultados ya resumido por línea de presentación |
| `AJUSTES_PRUEBA`, `MPM`, `CHECKS`, `FUENTES`, `LEEME` | Metadatos y casos de prueba |

`infer_columns_by_mathematical_weights` no tiene forma de detectar "esto no es una
balanza en absoluto" — siempre elige la mejor combinación de 3 columnas entre las
disponibles y reporta un % de "confianza" que mide encaje *relativo*, no validez
*absoluta*. Se verificó empíricamente (`sala_importacion` + las 3 hojas reales):

- `TB_ERP`: columna Saldo inferida 100% numérica → correcto.
- `MAPEO_NIIF18`: la heurística tomó una columna de texto libre ("Evidencia requerida")
  como Saldo → 0% numérico, pero `clean_numeric_series` la convierte silenciosamente a
  `0.0` (`fillna(0.0)`), así que el resultado parecía "cuadrar perfecto" sin ninguna
  advertencia.
- `ER_NIIF18`: la heurística invirtió Cuenta y Saldo (tomó una columna de montos como
  código de cuenta) y la columna resultante de "Saldo" mezclaba dos mini-tablas — solo
  31% de sus filas eran genuinamente numéricas, el resto `NaN`.

## Corrección aplicada (reestructuración, no parche)

Se agregó `sala_importacion.evaluar_calidad_balanza(df_raw, col_saldo)`: mide qué
fracción del **total de filas** de la hoja tiene un valor genuinamente numérico en la
columna inferida como Saldo (no solo entre las celdas no vacías — decisión deliberada:
una balanza real tiene saldo, aunque sea cero, en casi toda cuenta; una columna con pocas
celdas presentes pero 100% numéricas entre ellas tampoco es una balanza real). Umbral:
70%, calibrado contra los 3 casos reales de arriba.

`app.py` (Fase 1, Ingesta) ahora llama esta validación antes de aceptar la hoja: si falla,
**bloquea la carga** (no solo advierte) con un mensaje claro, limpia
`df_balanza`/`df_clasificado`, y expande automáticamente el mapeo manual de columnas por
si el usuario quiere corregirlo. La misma validación se aplica también si el usuario
remapea columnas a mano.

## Regresión encontrada durante la implementación (el propio arnés la detectó)

Al calibrar el umbral con un test sintético de "columna vacía" (`[None, None, '']`), el
primer intento de la validación no la rechazaba — mismo patrón de bug ya corregido antes
en `construir_balanza_estandar`: `None` en una columna de texto se convierte a la cadena
literal `'None'` (no `'nan'`) con `astype(str)`. Se corrigió usando `columna.notna()`
sobre la serie original. Un segundo test sintético (columna mayormente `NaN` con los
pocos valores presentes 100% numéricos) expuso que medir el ratio solo sobre celdas no
vacías dejaba pasar ese caso — se corrigió midiendo sobre el total de filas, como se
describe arriba.

## Segunda vuelta: el propietario encontró un falso positivo real

Tras la primera versión (que solo validaba la columna Saldo), el propietario preguntó
puntualmente por la hoja `CHECKS` del archivo de prueba — una tabla de controles
(débitos/créditos esperados vs. reales, brechas intencionales), no una balanza. Se
verificó empíricamente: **sí pasaba** la validación, porque el motor había inferido una
columna de montos ("Actual": 11795000, 0, 0…) como si fuera el código de Cuenta, y la
columna "Diferencia" (mayormente ceros) pasaba el umbral de Saldo por sí sola.

Causa raíz: validar solo la columna Saldo no basta — una columna de Cuenta que en
realidad es de montos numéricos también es una señal de que la hoja no es una balanza.
Se verificó el discriminante contra las 4 hojas reales: los códigos de cuenta genuinos
(`"1.1.01.001"`, con varios puntos) tienen 0% de parseo numérico limpio; las columnas de
montos usadas por error como Cuenta (`CHECKS`, `ER_NIIF18`) tienen 80% y 100%.

**Corrección**: `evaluar_calidad_balanza` ahora recibe también `col_cuenta` y exige que
esa columna sea **mayoritariamente NO numérica** (techo 30%), además de que Saldo sea
mayoritariamente numérico (piso 70%). Ambas condiciones, no una sola.

## Verificación

- 12 tests unitarios en `tests/test_sala_importacion.py` (casos sintéticos, incluyendo
  el caso `CHECKS` reproducido de forma sintética).
- 4 tests de integración en `tests/test_sala_importacion_hojas_reales.py`, contra el
  archivo real del repo (`TB_ERP` acepta; `MAPEO_NIIF18`, `ER_NIIF18`, `CHECKS` rechazan).
- `python -m pytest tests/` — 38/38 en verde.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
