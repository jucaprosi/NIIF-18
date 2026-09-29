"""
Compuerta _service.py para sala_cambios_patrimonio.

Responsabilidad (PRD.md RF-14, §12.1 Fase B — funcionalidad completa a pedido del
propietario, 2026-09-24): Estado de Cambios en el Patrimonio bajo NIC 1.106-110 —
concilia cada componente del patrimonio (capital, reservas, resultados acumulados)
entre el saldo inicial (Año 1) y el saldo final (Año 2), mostrando el resultado del
período, los dividendos y otros movimientos por separado.

Comparte la misma limitación estructural que `sala_flujo_efectivo` (¤): requiere DOS
períodos ya clasificados por `sala_situacion_financiera`, no un solo balance. Reutiliza
exactamente la misma derivación de dividendos pagados (cambio en Resultados Acumulados
menos el resultado del período) ya verificada en `sala_flujo_efectivo` — no se duplica
la lógica, se llama a la misma función para evitar que las dos salas puedan reportar
cifras de dividendos distintas para el mismo par de balances.

**Otro Resultado Integral — ORI (2026-09-25, a pedido del contador vía el propietario)**:
NIIF 18/NIC 1 definen el Estado de Resultado Integral como Resultado del Período (lo
que ya calcula `sala_estados_financieros`) **más** el Otro Resultado Integral (ORI) —
partidas como revaluación de propiedades, diferencias de conversión, remediciones de
planes de beneficios definidos — que casi nunca pasan por una cuenta de resultados de
la balanza: aparecen como movimientos directos en cuentas de **reserva** del Patrimonio
entre Año 1 y Año 2. `calcular_resultado_integral` identifica esos movimientos --
exactamente lo que esta sala ya calculaba como "Aportes y Otros Movimientos" para
cuentas que no son capital contribuido ni resultados acumulados -- y los suma al
Resultado del Período para formar el Resultado Integral Total.

**Riesgo señalado (heurística DRAFT, mismo patrón que el resto del proyecto)**: no todo
movimiento de una cuenta de reserva es ORI -- una transferencia desde Resultados
Acumulados a una Reserva Legal (apropiación estatutaria, común en Ecuador) es un
traslado interno del patrimonio, no una ganancia/pérdida nueva del período, y hoy se
contaría como ORI por error si la cuenta de reserva legal no se excluye explícitamente.
Requiere revisión contable cuenta por cuenta antes de producción (mismo criterio que
).

**Riesgo señalado (PRD.md §8)**: no validado todavía contra un caso real de dos
períodos (mismo motivo que `sala_flujo_efectivo` — el archivo de prueba de este
proyecto es de un solo período) — solo contra un escenario sintético construido para
verificar la identidad contable de cada componente (saldo inicial + movimientos =
saldo final).
"""
import pandas as pd
from sala_flujo_efectivo import _service as fe_svc

__all__ = ["construir_cambios_patrimonio", "calcular_resultado_integral"]


def _saldo_por_cuenta(df, cuenta):
    if df is None or len(df) == 0:
        return 0.0
    fila = df[df['Cuenta'].astype(str) == str(cuenta)]
    return float(fila['Saldo'].sum()) if len(fila) else 0.0


def _es_cuenta_resultados(descripcion):
    return any(w in str(descripcion).lower() for w in ('resultado', 'utilidad', 'acumulad'))


# Cuentas de capital contribuido -- excluidas de ORI porque un aumento/reducción de
# capital es una transacción con los propietarios (NIC 1.106(d)), no una ganancia o
# pérdida del período. "Reserva legal" se excluye también: en Ecuador es una
# apropiación estatutaria desde Resultados Acumulados (traslado interno), no ORI --
# ver riesgo señalado arriba; el contador debe confirmar cualquier otra reserva.
_PALABRAS_NO_ORI = ('capital', 'accion', 'acción', 'aporte', 'reserva legal', 'reserva estatutaria')


def construir_cambios_patrimonio(df_balance_ano1, df_balance_ano2, resultado_neto):
    """Concilia cada cuenta de Patrimonio entre Año 1 y Año 2 (NIC 1.106-110).

    Devuelve (df_conciliacion, totales). `df_conciliacion` tiene una fila por cuenta de
    patrimonio (unión de las cuentas presentes en cualquiera de los dos períodos), con
    columnas: Cuenta, Descripcion, Saldo_Inicial, Utilidad_Del_Periodo, Dividendos,
    Aportes_Y_Otros_Movimientos, Saldo_Final -- todo en magnitud positiva (a diferencia
    de `Saldo`, que en este proyecto es negativo para cuentas de patrimonio).

    Las cuentas de resultados acumulados/utilidad reciben el resultado del período y
    los dividendos derivados (ver `sala_flujo_efectivo`); el resto de las cuentas de
    patrimonio (capital, reservas) reciben su cambio neto como "aportes y otros
    movimientos" -- no se intenta distinguir una emisión de capital de una reducción
    dentro de esa columna, mismo tipo de simplificación ya documentada en
    `sala_flujo_efectivo` para Activo/Pasivo No Corriente.
    """
    categoria = "5. Patrimonio"
    cuentas_a1 = df_balance_ano1[df_balance_ano1['Categoria_Situacion_Financiera'] == categoria] if df_balance_ano1 is not None and len(df_balance_ano1) else pd.DataFrame(columns=['Cuenta', 'Descripcion', 'Saldo'])
    cuentas_a2 = df_balance_ano2[df_balance_ano2['Categoria_Situacion_Financiera'] == categoria] if df_balance_ano2 is not None and len(df_balance_ano2) else pd.DataFrame(columns=['Cuenta', 'Descripcion', 'Saldo'])

    descripciones = {}
    for _, r in pd.concat([cuentas_a1, cuentas_a2]).iterrows():
        descripciones[str(r['Cuenta'])] = r['Descripcion']

    resultado_flujo_efectivo = fe_svc.calcular_flujo_efectivo_indirecto(
        pd.DataFrame(columns=['Cuenta', 'Descripcion', 'Saldo', 'Categoria_NIIF18']),
        df_balance_ano1, df_balance_ano2, resultado_neto,
    )
    dividendos_pagados = resultado_flujo_efectivo['dividendos_pagados']

    filas = []
    for cuenta, descripcion in descripciones.items():
        # Saldo de patrimonio es negativo (crédito) en la convención de este proyecto;
        # se invierte el signo para reportar magnitudes positivas, igual que
        # `sala_situacion_financiera.calcular_totales`.
        saldo_inicial = -_saldo_por_cuenta(cuentas_a1, cuenta)
        saldo_final = -_saldo_por_cuenta(cuentas_a2, cuenta)

        if _es_cuenta_resultados(descripcion):
            utilidad_del_periodo = resultado_neto
            dividendos = -dividendos_pagados
            # Residual: cualquier diferencia no explicada por utilidad/dividendos (p.
            # ej. una transferencia a reserva legal) se reporta, no se oculta.
            aportes_y_otros = (saldo_final - saldo_inicial) - utilidad_del_periodo - dividendos
        else:
            utilidad_del_periodo = 0.0
            dividendos = 0.0
            aportes_y_otros = saldo_final - saldo_inicial

        filas.append({
            'Cuenta': cuenta,
            'Descripcion': descripcion,
            'Saldo_Inicial': saldo_inicial,
            'Utilidad_Del_Periodo': utilidad_del_periodo,
            'Dividendos': dividendos,
            'Aportes_Y_Otros_Movimientos': aportes_y_otros,
            'Saldo_Final': saldo_final,
        })

    df_conciliacion = pd.DataFrame(filas, columns=[
        'Cuenta', 'Descripcion', 'Saldo_Inicial', 'Utilidad_Del_Periodo',
        'Dividendos', 'Aportes_Y_Otros_Movimientos', 'Saldo_Final',
    ])

    totales = {
        'patrimonio_inicial': float(df_conciliacion['Saldo_Inicial'].sum()),
        'utilidad_del_periodo': float(df_conciliacion['Utilidad_Del_Periodo'].sum()),
        'dividendos': float(df_conciliacion['Dividendos'].sum()),
        'aportes_y_otros_movimientos': float(df_conciliacion['Aportes_Y_Otros_Movimientos'].sum()),
        'patrimonio_final': float(df_conciliacion['Saldo_Final'].sum()),
    }
    return df_conciliacion, totales


def calcular_resultado_integral(df_conciliacion, resultado_neto):
    """Estado de Resultado Integral = Resultado del Período + Otro Resultado Integral
    (NIC 1.81A, NIIF 18). El ORI se identifica en `df_conciliacion` (salida de
    `construir_cambios_patrimonio`) como el movimiento de "Aportes y Otros Movimientos"
    de cuentas de patrimonio que **no** son capital contribuido ni resultados
    acumulados -- ver `_PALABRAS_NO_ORI` y el riesgo señalado en el docstring del
    módulo (requiere revisión contable, es una heurística DRAFT).

    Devuelve un dict con `resultado_del_periodo`, `otro_resultado_integral`,
    `resultado_integral_total`, y `desglose_ori` (lista de dicts Cuenta/Descripcion/
    Monto, una fila por cuenta de reserva con movimiento distinto de cero) -- para que
    la UI muestre de qué cuentas viene el ORI, no solo el total.
    """
    if df_conciliacion is None or len(df_conciliacion) == 0:
        return {
            'resultado_del_periodo': resultado_neto,
            'otro_resultado_integral': 0.0,
            'resultado_integral_total': resultado_neto,
            'desglose_ori': [],
        }

    es_no_ori = (
        df_conciliacion['Descripcion'].astype(str).str.lower().apply(
            lambda d: any(w in d for w in _PALABRAS_NO_ORI))
        | (df_conciliacion['Utilidad_Del_Periodo'] != 0.0)  # ya identificada como resultados acumulados
    )
    df_ori = df_conciliacion[~es_no_ori].copy()
    df_ori = df_ori[df_ori['Aportes_Y_Otros_Movimientos'] != 0.0]

    otro_resultado_integral = float(df_ori['Aportes_Y_Otros_Movimientos'].sum())
    desglose_ori = [
        {'Cuenta': r['Cuenta'], 'Descripcion': r['Descripcion'], 'Monto': r['Aportes_Y_Otros_Movimientos']}
        for _, r in df_ori.iterrows()
    ]

    return {
        'resultado_del_periodo': resultado_neto,
        'otro_resultado_integral': otro_resultado_integral,
        'resultado_integral_total': resultado_neto + otro_resultado_integral,
        'desglose_ori': desglose_ori,
    }
