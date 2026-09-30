import pandas as pd
from sala_cambios_patrimonio import _service as cp_svc


def _balance(filas):
    return pd.DataFrame(filas, columns=["Cuenta", "Descripcion", "Saldo", "Categoria_Situacion_Financiera"])


# Mismo escenario sintético que tests/test_sala_flujo_efectivo.py (verificado por
# partida doble ahí) -- Capital social sin cambios, Resultados acumulados sube de 140 a
# 220 (utilidad neta 100, dividendos pagados 20: 140+100-20=220).
def _balance_ano1():
    return _balance([
        ("3.1.01.001", "Capital social", -200.0, "5. Patrimonio"),
        ("3.1.02.001", "Resultados acumulados", -140.0, "5. Patrimonio"),
    ])


def _balance_ano2():
    return _balance([
        ("3.1.01.001", "Capital social", -200.0, "5. Patrimonio"),
        ("3.1.02.001", "Resultados acumulados", -220.0, "5. Patrimonio"),
    ])


def test_construir_cambios_patrimonio_reconcilia_cada_componente():
    df, totales = cp_svc.construir_cambios_patrimonio(_balance_ano1(), _balance_ano2(), resultado_neto=100.0)

    capital = df[df['Cuenta'] == "3.1.01.001"].iloc[0]
    assert capital['Saldo_Inicial'] == 200.0
    assert capital['Aportes_Y_Otros_Movimientos'] == 0.0
    assert capital['Saldo_Final'] == 200.0

    resultados = df[df['Cuenta'] == "3.1.02.001"].iloc[0]
    assert resultados['Saldo_Inicial'] == 140.0
    assert resultados['Utilidad_Del_Periodo'] == 100.0
    assert resultados['Dividendos'] == -20.0
    assert resultados['Saldo_Final'] == 220.0
    # Identidad contable por fila: inicial + movimientos = final.
    assert (resultados['Saldo_Inicial'] + resultados['Utilidad_Del_Periodo']
            + resultados['Dividendos'] + resultados['Aportes_Y_Otros_Movimientos']) == resultados['Saldo_Final']


def test_construir_cambios_patrimonio_totales_cuadran():
    _, totales = cp_svc.construir_cambios_patrimonio(_balance_ano1(), _balance_ano2(), resultado_neto=100.0)
    assert totales['patrimonio_inicial'] == 340.0
    assert totales['patrimonio_final'] == 420.0
    assert totales['utilidad_del_periodo'] == 100.0
    assert totales['dividendos'] == -20.0
    assert (totales['patrimonio_inicial'] + totales['utilidad_del_periodo']
            + totales['dividendos'] + totales['aportes_y_otros_movimientos']) == totales['patrimonio_final']


def test_construir_cambios_patrimonio_consistente_con_flujo_efectivo_en_dividendos():
    # Las dos salas deben reportar exactamente el mismo monto de dividendos pagados
    # para el mismo par de balances -- se llama a la misma función, no se duplica la
    # derivación (ver docstring de sala_cambios_patrimonio).
    from sala_flujo_efectivo import _service as fe_svc
    df_pl_vacio = pd.DataFrame(columns=['Cuenta', 'Descripcion', 'Saldo', 'Categoria_NIIF18'])
    resultado_fe = fe_svc.calcular_flujo_efectivo_indirecto(df_pl_vacio, _balance_ano1(), _balance_ano2(), resultado_neto=100.0)
    _, totales_cp = cp_svc.construir_cambios_patrimonio(_balance_ano1(), _balance_ano2(), resultado_neto=100.0)
    assert resultado_fe['dividendos_pagados'] == -totales_cp['dividendos']


# Escenario con Otro Resultado Integral (ORI): además del escenario base, una reserva
# de revaluación aumenta $30 (ORI real -- ganancia de revaluación de PP&E, NIC 16.39/
# NIIF 18) y una reserva legal aumenta $15 (apropiación estatutaria desde Resultados
# Acumulados en Ecuador -- traslado interno, NO es ORI, debe excluirse).
def _balance_ano1_con_ori():
    return _balance([
        ("3.1.01.001", "Capital social", -200.0, "5. Patrimonio"),
        ("3.1.02.001", "Resultados acumulados", -140.0, "5. Patrimonio"),
        ("3.1.03.001", "Reserva de revaluación de propiedades", -0.0, "5. Patrimonio"),
        ("3.1.04.001", "Reserva legal", -10.0, "5. Patrimonio"),
    ])


def _balance_ano2_con_ori():
    return _balance([
        ("3.1.01.001", "Capital social", -200.0, "5. Patrimonio"),
        ("3.1.02.001", "Resultados acumulados", -220.0, "5. Patrimonio"),
        ("3.1.03.001", "Reserva de revaluación de propiedades", -30.0, "5. Patrimonio"),
        ("3.1.04.001", "Reserva legal", -25.0, "5. Patrimonio"),
    ])


def test_calcular_resultado_integral_detecta_solo_la_reserva_de_revaluacion_como_ori():
    df, _ = cp_svc.construir_cambios_patrimonio(_balance_ano1_con_ori(), _balance_ano2_con_ori(), resultado_neto=100.0)
    resultado = cp_svc.calcular_resultado_integral(df, resultado_neto=100.0)

    assert resultado['resultado_del_periodo'] == 100.0
    # Solo la reserva de revaluación ($30) cuenta como ORI -- la reserva legal ($15) se
    # excluye explícitamente por ser una apropiación interna, no una ganancia nueva.
    assert resultado['otro_resultado_integral'] == 30.0
    assert resultado['resultado_integral_total'] == 130.0
    cuentas_en_desglose = {d['Cuenta'] for d in resultado['desglose_ori']}
    assert "3.1.03.001" in cuentas_en_desglose
    assert "3.1.04.001" not in cuentas_en_desglose
    assert "3.1.01.001" not in cuentas_en_desglose  # capital, tampoco es ORI


def test_calcular_resultado_integral_sin_movimientos_de_reserva_ori_es_cero():
    df, _ = cp_svc.construir_cambios_patrimonio(_balance_ano1(), _balance_ano2(), resultado_neto=100.0)
    resultado = cp_svc.calcular_resultado_integral(df, resultado_neto=100.0)
    assert resultado['otro_resultado_integral'] == 0.0
    assert resultado['resultado_integral_total'] == 100.0
    assert resultado['desglose_ori'] == []
