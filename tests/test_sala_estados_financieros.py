import pandas as pd
from sala_estados_financieros import _service as fs_svc


def _df():
    return pd.DataFrame([
        {"Cuenta": "410100", "Descripcion": "Venta de mercaderia", "Saldo": -1000.0, "Categoria_NIIF18": "1. Operación (Ingresos / Gastos Operativos)"},
        {"Cuenta": "510100", "Descripcion": "Costo de ventas", "Saldo": 400.0, "Categoria_NIIF18": "1. Operación (Ingresos / Gastos Operativos)"},
        {"Cuenta": "420100", "Descripcion": "Resultado por metodo de participacion", "Saldo": -100.0, "Categoria_NIIF18": "2. Inversión (Ingresos / Gastos por Inversiones)"},
        {"Cuenta": "610100", "Descripcion": "Interes de prestamo bancario", "Saldo": 50.0, "Categoria_NIIF18": "3. Financiación (Costos / Pasivos Financieros)"},
        {"Cuenta": "550100", "Descripcion": "Gasto por impuesto a la renta", "Saldo": 90.0, "Categoria_NIIF18": "4. Impuestos a las Ganancias"},
        {"Cuenta": "100000", "Descripcion": "Efectivo y equivalentes al efectivo", "Saldo": 5000.0, "Categoria_NIIF18": "0. Balance General (No P&L / Excluir)"},
    ])


def test_subtotales_cuadran_matematicamente():
    _, subtotales = fs_svc.calcular_subtotales(_df())
    # 1. Operativo = 1000 (venta) - 400 (costo) = 600
    assert subtotales['sub_1_resultado_operativo'] == 600.0
    # 2. Antes de fin/imp = 600 + 100 (inversión) = 700
    assert subtotales['sub_2_antes_fin_imp'] == 700.0
    # 3. Periodo = 700 - 50 (financiación) - 90 (impuestos) = 560
    assert subtotales['sub_3_resultado_periodo'] == 560.0


def test_categoria_0_no_afecta_subtotales():
    df, _ = fs_svc.calcular_subtotales(_df())
    fila_balance = df[df['Categoria_NIIF18'].str.startswith('0.')].iloc[0]
    assert fila_balance['PL_Neto'] == 0.0
