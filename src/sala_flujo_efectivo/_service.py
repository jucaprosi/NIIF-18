"""
Compuerta _service.py para sala_flujo_efectivo.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-13, §12.1 Fase B — funcionalidad completa a pedido del
propietario, 2026-09-24): Estado de Flujo de Efectivo bajo NIC 7 ("Statement of Cash
Flows"), método indirecto (NIC 7.18(b)) — el único derivable de una balanza de
comprobación sin un libro de caja detallado; el método directo (NIC 7.18(a)) requiere
cobros/pagos brutos que esta app no captura.

Diferencia estructural real con `sala_clasificacion`/`sala_situacion_financiera`: el
Flujo de Efectivo **no puede calcularse de un solo período** — es, por definición
(NIC 7.10), el cambio de efectivo *entre* dos fechas. Requiere el Estado de Resultados
ya clasificado del período (`sala_estados_financieros`), y el Estado de Situación
Financiera de **ambos** períodos, Año 1 (comparativo) y Año 2 (actual), ya clasificado
(`sala_situacion_financiera`).

**Riesgo señalado (PRD.md §8, mismo criterio que el resto del proyecto)**: el método
indirecto aquí implementado usa el cambio NETO de cada categoría de balance entre los
dos períodos (NIC 7.20) — una simplificación estándar en herramientas que parten de
balanzas, no de un libro de activos fijos (PPE roll-forward) detallado. No distingue
compras brutas de disposiciones brutas dentro de Activo No Corriente, ni separa
préstamos nuevos de pagos de capital dentro de Pasivo No Corriente — ambos se
aproximan por el cambio neto. **No validado todavía contra un caso de dos períodos
reales** (el archivo de prueba de este proyecto, `balance_prueba_niif18_sap_business_
one.xlsx`, es de un solo período) — solo contra datos sintéticos construidos para
verificar la identidad contable fundamental (ver `calcular_flujo_efectivo_indirecto`).
"""
import pandas as pd

__all__ = ["calcular_flujo_efectivo_indirecto"]

# Palabras que identifican partidas no monetarias del Estado de Resultados que deben
# revertirse en la conciliación CFO (NIC 7.20(a)) -- mismo estilo de listas de palabras
# clave ya usado en sala_clasificacion, con la misma limitación reconocida (heurística,
# no un catálogo contable tipado; ver PRD.md §8).
_PALABRAS_NO_MONETARIAS_CFO = ('depreciaci', 'amortizaci', 'deterioro')
_PALABRAS_METODO_PARTICIPACION = ('metodo de participacion', 'método de participación', 'participacion en resultado', 'participación en resultado')
_PALABRAS_DIVIDENDO = ('dividendo',)


def _cambio_por_categoria(df_balance_a1, df_balance_a2, categoria, columna_categoria='Categoria_Situacion_Financiera'):
    """Suma de Saldo por categoría en cada período; devuelve (saldo_a1, saldo_a2, delta)."""
    s_a1 = float(df_balance_a1[df_balance_a1[columna_categoria] == categoria]['Saldo'].sum()) if df_balance_a1 is not None and len(df_balance_a1) else 0.0
    s_a2 = float(df_balance_a2[df_balance_a2[columna_categoria] == categoria]['Saldo'].sum()) if df_balance_a2 is not None and len(df_balance_a2) else 0.0
    return s_a1, s_a2, s_a2 - s_a1


def _suma_por_palabras(df_pl_clasificado, palabras):
    if df_pl_clasificado is None or len(df_pl_clasificado) == 0:
        return 0.0
    desc = df_pl_clasificado['Descripcion'].astype(str).str.lower()
    mask = desc.apply(lambda d: any(w in d for w in palabras))
    return float(df_pl_clasificado.loc[mask, 'Saldo'].sum())


# ¤sala_flujo_efectivo
def calcular_flujo_efectivo_indirecto(df_pl_clasificado, df_balance_ano1, df_balance_ano2, resultado_neto):
    """Estado de Flujo de Efectivo, método indirecto (NIC 7.18(b)).

    Parámetros:
    - df_pl_clasificado: balanza de resultados ya clasificada por `sala_clasificacion`
      (columnas Cuenta/Descripcion/Saldo/Categoria_NIIF18) del período actual (Año 2).
    - df_balance_ano1, df_balance_ano2: balanzas de situación financiera ya clasificadas
      por `sala_situacion_financiera` (columna Categoria_Situacion_Financiera) de cada
      período. `df_balance_ano1` puede ser `None` si no hay comparativo -- en ese caso
      todos los deltas de capital de trabajo/inversión/financiación son 0 (no hay
      período previo con el que comparar) y el resultado es solo CFO = resultado neto +
      partidas no monetarias, sin capital de trabajo ni CFI/CFF reales.
    - resultado_neto: utilidad/pérdida del período (de `sala_estados_financieros.
      calcular_subtotales`, clave `sub_3_resultado_periodo`).

    Devuelve un dict con cfo, cfi, cff, flujo_neto_efectivo, y el desglose de cada
    ajuste -- para que la UI pueda mostrar la conciliación completa (mismo criterio de
    trazabilidad que `sala_mpm`).
    """
    # Gasto no monetario (depreciación/amortización/deterioro) tiene Saldo > 0 (débito,
    # convención de este proyecto) y ya restó del resultado neto sin que saliera
    # efectivo -- se devuelve a CFO en su magnitud (NIC 7.20(a)).
    ajuste_no_monetario = abs(_suma_por_palabras(df_pl_clasificado, _PALABRAS_NO_MONETARIAS_CFO))

    ajuste_metodo_participacion = -_suma_por_palabras(df_pl_clasificado, _PALABRAS_METODO_PARTICIPACION)
    # Resultado por método de participación es no monetario (NIC 7.20(a)): si fue
    # ingreso (Saldo < 0 en la convención de este proyecto), se resta de CFO; si fue
    # pérdida (Saldo > 0), se suma. `-suma` ya invierte el signo correctamente.

    activo_no_corriente_a1, activo_no_corriente_a2, delta_activo_no_corriente = _cambio_por_categoria(
        df_balance_ano1, df_balance_ano2, "2. Activo No Corriente")
    pasivo_no_corriente_a1, pasivo_no_corriente_a2, delta_pasivo_no_corriente = _cambio_por_categoria(
        df_balance_ano1, df_balance_ano2, "4. Pasivo No Corriente")

    sin_comparativo = df_balance_ano1 is None or df_balance_ano2 is None or len(df_balance_ano1) == 0 or len(df_balance_ano2) == 0

    # Aporte de capital y dividendos pagados se derivan del propio balance, no del P&L:
    # un dividendo PAGADO nunca aparece en `df_pl_clasificado` -- por diseño de
    # `sala_clasificacion` (Paso 0) se excluye a Categoría 0 / Balance General, no es
    # partida del Estado de Resultados (PRD.md §3). Bug encontrado al verificar con un
    # escenario sintético: buscar "dividendo" en el P&L siempre da 0. La fuente correcta
    # es el cambio en Resultados Acumulados: ese cambio es exactamente
    # `resultado_neto - dividendos_pagados` (asumiendo que no hay otras transferencias a
    # reservas en el período, limitación reconocida igual que el resto del motor).
    def _patrimonio_por_filtro(df, incluir_resultados):
        if df is None or len(df) == 0:
            return 0.0
        mask_cat = df['Categoria_Situacion_Financiera'] == "5. Patrimonio"
        es_resultado = df['Descripcion'].astype(str).str.lower().str.contains('resultado|utilidad|acumulad', regex=True)
        mask = mask_cat & (es_resultado if incluir_resultados else ~es_resultado)
        return float(df[mask]['Saldo'].sum())

    if sin_comparativo:
        aporte_capital = 0.0
        dividendos_pagados = 0.0
    else:
        patrimonio_contribuido_a1 = _patrimonio_por_filtro(df_balance_ano1, incluir_resultados=False)
        patrimonio_contribuido_a2 = _patrimonio_por_filtro(df_balance_ano2, incluir_resultados=False)
        # Saldo de patrimonio es negativo (crédito); un aumento de capital lo vuelve más
        # negativo, así que se invierte el signo para reportar una entrada de efectivo
        # positiva cuando el capital contribuido aumenta.
        aporte_capital = -(patrimonio_contribuido_a2 - patrimonio_contribuido_a1)

        resultados_acum_a1 = _patrimonio_por_filtro(df_balance_ano1, incluir_resultados=True)
        resultados_acum_a2 = _patrimonio_por_filtro(df_balance_ano2, incluir_resultados=True)
        cambio_real_resultados_acum = -(resultados_acum_a2 - resultados_acum_a1)
        dividendos_pagados = max(0.0, resultado_neto - cambio_real_resultados_acum)

    # Capital de trabajo: cambio en Activo Corriente y Pasivo Corriente EXCLUYENDO
    # efectivo/equivalentes (Caja, Bancos) -- el cambio en efectivo es el resultado del
    # estado, no un insumo de él (NIC 7.6, definición de efectivo y equivalentes).
    def _cambio_corriente_sin_efectivo(df_a1, df_a2, categoria):
        def _filtrar(df):
            if df is None or len(df) == 0:
                return pd.DataFrame(columns=['Saldo'])
            mask_cat = df['Categoria_Situacion_Financiera'] == categoria
            mask_no_efectivo = ~df['Descripcion'].astype(str).str.lower().str.contains('caja|banco|efectivo', regex=True)
            return df[mask_cat & mask_no_efectivo]
        s1 = float(_filtrar(df_a1)['Saldo'].sum())
        s2 = float(_filtrar(df_a2)['Saldo'].sum())
        return s2 - s1

    delta_activo_corriente_op = _cambio_corriente_sin_efectivo(df_balance_ano1, df_balance_ano2, "1. Activo Corriente")
    delta_pasivo_corriente_op = _cambio_corriente_sin_efectivo(df_balance_ano1, df_balance_ano2, "3. Pasivo Corriente")

    # Activo corriente operativo (cuentas por cobrar, inventario) al subir consume
    # efectivo (Saldo sube = débito = uso de caja) -> resta a CFO. Pasivo corriente
    # operativo (proveedores) al subir libera efectivo (Saldo baja, más negativo =
    # crédito mayor) -> el delta ya es negativo cuando sube, así que se resta también
    # con signo invertido para sumar a CFO.
    cambio_capital_trabajo = -delta_activo_corriente_op - delta_pasivo_corriente_op

    cfo = resultado_neto + ajuste_no_monetario + ajuste_metodo_participacion + cambio_capital_trabajo

    # CFI: cambio neto en Activo No Corriente, con signo invertido (un aumento de
    # activo no corriente es una salida de efectivo -- una compra), sumando de vuelta
    # `ajuste_no_monetario` -- el Activo No Corriente neto ya bajó por la depreciación
    # del período, que no es una salida de efectivo por sí sola y ya se contó en CFO;
    # sin este ajuste, la compra bruta de activos queda subestimada exactamente por el
    # monto de la depreciación (bug encontrado y corregido al verificar con un
    # escenario sintético de dos períodos: sin el ajuste, una compra real de $50 se
    # calculaba como $30).
    # Sin comparativo no hay Activo No Corriente de un período previo con el que medir
    # un delta real -- forzar CFI a 0 en vez de restar `ajuste_no_monetario` contra un
    # delta inexistente (que daría un CFI negativo falso igual a la depreciación).
    cfi = 0.0 if sin_comparativo else -(delta_activo_no_corriente + ajuste_no_monetario)

    # CFF: cambio neto en Pasivo No Corriente, con signo invertido -- Saldo de pasivo es
    # negativo (crédito); un pago de deuda vuelve el saldo MENOS negativo, así que
    # `delta_pasivo_no_corriente` (s2-s1) da positivo cuando en realidad hubo una SALIDA
    # de efectivo (bug de signo encontrado y corregido igual que el de CFI, ambos con el
    # mismo escenario sintético) + aporte de capital contribuido - dividendos pagados.
    cff = 0.0 if sin_comparativo else (-delta_pasivo_no_corriente + aporte_capital - dividendos_pagados)

    flujo_neto_efectivo = cfo + cfi + cff

    return {
        'resultado_neto': resultado_neto,
        'ajuste_no_monetario': ajuste_no_monetario,
        'ajuste_metodo_participacion': ajuste_metodo_participacion,
        'cambio_capital_trabajo': cambio_capital_trabajo,
        'cfo': cfo,
        'delta_activo_no_corriente': delta_activo_no_corriente,
        'cfi': cfi,
        'delta_pasivo_no_corriente': delta_pasivo_no_corriente,
        'aporte_capital': aporte_capital,
        'dividendos_pagados': dividendos_pagados,
        'cff': cff,
        'flujo_neto_efectivo': flujo_neto_efectivo,
    }
