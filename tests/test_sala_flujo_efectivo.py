import pandas as pd
from sala_flujo_efectivo import _service as fe_svc


def _balance(filas):
    return pd.DataFrame(filas, columns=["Cuenta", "Descripcion", "Saldo", "Categoria_Situacion_Financiera"])


def test_calcular_flujo_efectivo_indirecto_reconcilia_con_cambio_real_de_efectivo():
    # Escenario sintético de dos períodos construido a mano (T-accounts), verificado por
    # partida doble antes de escribir el test -- NIC 7.10 exige que CFO+CFI+CFF sea
    # exactamente igual al cambio real de efectivo entre los dos balances. Es la
    # identidad contable fundamental de este estado financiero: si no cuadra, el motor
    # está mal, sin importar qué tan razonable se vea cada línea por separado.
    #
    # Año 1: Caja 100, CxC 50, Inventario 30, PPE neto 500 | Proveedores 40, Préstamo LP 300 | Capital 200, Resultados acum. 140
    # Actividad del año: utilidad neta 100 (incluye depreciación 20 ya deducida),
    # CxC +10, Inventario -5, Proveedores +15, compra de PPE $50 (PPE neto 500+50-20=530),
    # pago de préstamo $30 (300->270), dividendos pagados $20, sin nuevo capital.
    # Año 2 resultante (por partida doble): Caja 130, CxC 60, Inventario 25, PPE neto 530
    #   | Proveedores 55, Préstamo LP 270 | Capital 200, Resultados acum. 220
    # Cambio real de efectivo: 130 - 100 = +30.

    df_pl = pd.DataFrame([
        {"Cuenta": "5.2.03.001", "Descripcion": "Depreciación equipos", "Saldo": 20.0, "Categoria_NIIF18": "1. Operación"},
    ])

    df_a1 = _balance([
        ("1.1.01.001", "Caja", 100.0, "1. Activo Corriente"),
        ("1.1.02.001", "Cuentas por cobrar", 50.0, "1. Activo Corriente"),
        ("1.1.03.001", "Inventario", 30.0, "1. Activo Corriente"),
        ("1.2.01.001", "Propiedad planta y equipo neto", 500.0, "2. Activo No Corriente"),
        ("2.1.01.001", "Proveedores", -40.0, "3. Pasivo Corriente"),
        ("2.2.01.001", "Préstamo bancario largo plazo", -300.0, "4. Pasivo No Corriente"),
        ("3.1.01.001", "Capital social", -200.0, "5. Patrimonio"),
        ("3.1.02.001", "Resultados acumulados", -140.0, "5. Patrimonio"),
    ])
    df_a2 = _balance([
        ("1.1.01.001", "Caja", 130.0, "1. Activo Corriente"),
        ("1.1.02.001", "Cuentas por cobrar", 60.0, "1. Activo Corriente"),
        ("1.1.03.001", "Inventario", 25.0, "1. Activo Corriente"),
        ("1.2.01.001", "Propiedad planta y equipo neto", 530.0, "2. Activo No Corriente"),
        ("2.1.01.001", "Proveedores", -55.0, "3. Pasivo Corriente"),
        ("2.2.01.001", "Préstamo bancario largo plazo", -270.0, "4. Pasivo No Corriente"),
        ("3.1.01.001", "Capital social", -200.0, "5. Patrimonio"),
        ("3.1.02.001", "Resultados acumulados", -220.0, "5. Patrimonio"),
    ])

    resultado = fe_svc.calcular_flujo_efectivo_indirecto(df_pl, df_a1, df_a2, resultado_neto=100.0)

    assert resultado['cfo'] == 130.0
    assert resultado['cfi'] == -50.0
    assert resultado['cff'] == -50.0
    # La identidad fundamental: debe cuadrar exacto con el cambio real de efectivo.
    assert resultado['flujo_neto_efectivo'] == 30.0


def test_calcular_flujo_efectivo_sin_comparativo_solo_cfo_no_monetario():
    df_pl = pd.DataFrame([
        {"Cuenta": "5.2.03.001", "Descripcion": "Depreciación equipos", "Saldo": 15.0, "Categoria_NIIF18": "1. Operación"},
    ])
    resultado = fe_svc.calcular_flujo_efectivo_indirecto(df_pl, None, None, resultado_neto=200.0)
    assert resultado['cfo'] == 215.0
    assert resultado['cfi'] == 0.0
    assert resultado['cff'] == 0.0
