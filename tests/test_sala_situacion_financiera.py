import os
import pandas as pd
from sala_situacion_financiera import _service as sf_svc


def test_clasificar_partida_balance_por_prefijo_de_codigo():
    assert sf_svc.clasificar_partida_balance("1.1.01.001", "Caja general") == sf_svc.CATEGORIA_ACTIVO_CORRIENTE
    assert sf_svc.clasificar_partida_balance("1.2.01.001", "Terrenos") == sf_svc.CATEGORIA_ACTIVO_NO_CORRIENTE
    assert sf_svc.clasificar_partida_balance("2.1.01.001", "Proveedores nacionales") == sf_svc.CATEGORIA_PASIVO_CORRIENTE
    assert sf_svc.clasificar_partida_balance("2.2.01.001", "Préstamo bancario largo plazo") == sf_svc.CATEGORIA_PASIVO_NO_CORRIENTE
    assert sf_svc.clasificar_partida_balance("3.1.01.001", "Capital social") == sf_svc.CATEGORIA_PATRIMONIO


def test_clasificar_partida_balance_codigo_no_reconocido():
    assert sf_svc.clasificar_partida_balance("9.9.99.999", "Cuenta rara") == sf_svc.CATEGORIA_NO_CLASIFICADA


def test_calcular_totales_neta_contra_cuentas_por_signo_no_por_abs():
    # Regresión: sumar por abs() por fila contaba una cuenta contra-activo (crédito) como
    # si sumara en vez de restar -- error de $1,220,000 detectado y corregido en esta
    # sesión al verificar contra TB_ERP real.
    df = pd.DataFrame([
        {"Cuenta": "1.1.01.001", "Descripcion": "Caja", "Saldo": 100000.0, "Categoria_Situacion_Financiera": sf_svc.CATEGORIA_ACTIVO_CORRIENTE},
        {"Cuenta": "1.1.02.099", "Descripcion": "Deterioro acumulado de cartera", "Saldo": -10000.0, "Categoria_Situacion_Financiera": sf_svc.CATEGORIA_ACTIVO_CORRIENTE},
    ])
    _, totales = sf_svc.calcular_totales(df)
    assert totales['activo_corriente'] == 90000.0  # 100000 - 10000, no 110000


def test_calcular_totales_reproduce_balance_real_tb_erp():
    xlsx_path = os.path.join(os.path.dirname(__file__), "..", "balance_prueba_niif18_sap_business_one.xlsx")
    if not os.path.exists(xlsx_path):
        return
    from sala_importacion import _service as imp_svc
    xl = pd.ExcelFile(xlsx_path)
    df_raw = imp_svc.read_excel_smart_header(xl, "TB_ERP")
    df_raw = df_raw[df_raw['Tipo'] == 'Balance']
    df_bal = imp_svc.construir_balanza_estandar(df_raw, 'Código cuenta', 'Nombre cuenta', 'Saldo final firmado')
    df_bal['Categoria_Situacion_Financiera'] = sf_svc.clasificar_dataframe_balance(df_bal)
    _, totales = sf_svc.calcular_totales(df_bal)

    assert totales['total_activo'] == 5455000.0
    assert totales['total_pasivo'] == 2125000.0
    assert totales['patrimonio'] == 2780000.0
    # Verificación cruzada real entre dos salas independientes: el resultado del
    # período implícito en el balance (Activo - Pasivo - Patrimonio) debe coincidir
    # exactamente con la utilidad neta ya verificada en sala_estados_financieros contra
    # ER_NIIF18 (ver test_motor_completo_sobre_tb_erp_reproduce_er_niif18_esperado).
    assert totales['resultado_del_periodo_implicito'] == 550000.0
    assert totales['total_activo'] == totales['total_pasivo_y_patrimonio']
