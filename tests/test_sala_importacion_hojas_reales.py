"""
Prueba de integración contra el archivo real `balance_prueba_niif18_sap_business_one.xlsx`
(raíz del repo). Reproduce dos hallazgos de esta sesión: el archivo trae 8 pestañas, solo
una de las cuales (TB_ERP) es una balanza real; las demás son hojas de referencia o de
controles de prueba con otra estructura. `evaluar_calidad_balanza` debe aceptar la
primera y rechazar las demás.
"""
import os
import pandas as pd
import pytest
from sala_importacion import _service as imp_svc
from sala_clasificacion import _service as class_svc
from sala_estados_financieros import _service as ef_svc

XLSX_PATH = os.path.join(os.path.dirname(__file__), "..", "balance_prueba_niif18_sap_business_one.xlsx")

pytestmark = pytest.mark.skipif(not os.path.exists(XLSX_PATH), reason="archivo de prueba no presente en este checkout")


def _inferir_y_evaluar(sheet_name):
    xl = pd.ExcelFile(XLSX_PATH)
    df_raw = imp_svc.read_excel_smart_header(xl, sheet_name)
    inf_cta, _, inf_saldo, _ = imp_svc.infer_columns_by_mathematical_weights(df_raw)
    return imp_svc.evaluar_calidad_balanza(df_raw, inf_cta, inf_saldo)


def test_tb_erp_es_una_balanza_valida():
    ok, motivos = _inferir_y_evaluar("TB_ERP")
    assert ok is True, motivos


def test_mapeo_niif18_no_es_una_balanza():
    # Es la hoja de respuesta esperada (ya trae la categoría NIIF 18 correcta) — no una
    # balanza de comprobación cruda.
    ok, motivos = _inferir_y_evaluar("MAPEO_NIIF18")
    assert ok is False


def test_er_niif18_no_es_una_balanza():
    # Es el Estado de Resultados ya resumido por línea de presentación.
    ok, motivos = _inferir_y_evaluar("ER_NIIF18")
    assert ok is False


def test_checks_no_es_una_balanza():
    # Es una tabla de controles de prueba (débitos/créditos esperados vs. reales) — no
    # una balanza. Detectado por el propietario tras la primera versión de esta
    # validación, que solo miraba la columna Saldo y dejaba pasar esta hoja.
    ok, motivos = _inferir_y_evaluar("CHECKS")
    assert ok is False


def test_motor_completo_sobre_tb_erp_reproduce_er_niif18_esperado():
    # Prueba de regresión de extremo a extremo (importación -> clasificación -> subtotales)
    # contra la hoja "respuesta esperada" del propio archivo (ER_NIIF18). Fija los 3
    # subtotales exactos que el motor debe reproducir -- documentado como brecha abierta
    # en TASKS.md ¤discrepancia_motor_tb_erp_pendiente hasta que se corrigió la causa
    # raíz (cuentas de balance 1.x/2.x con vocabulario de flujo -- "Depreciación
    # acumulada", "Deterioro acumulado", "Provisión por litigios" -- entraban al Estado
    # de Resultados por error, inflando el resultado operativo en $690,000).
    xl = pd.ExcelFile(XLSX_PATH)
    df_raw = imp_svc.read_excel_smart_header(xl, "TB_ERP")
    cta, desc, saldo, _ = imp_svc.infer_columns_by_mathematical_weights(df_raw)
    df_bal = imp_svc.construir_balanza_estandar(df_raw, cta, desc, saldo)
    df_bal["Categoria_NIIF18"] = class_svc.clasificar_dataframe(df_bal)
    _, subtotales = ef_svc.calcular_subtotales(df_bal)

    assert subtotales["sub_1_resultado_operativo"] == 813000.0
    assert subtotales["sub_2_antes_fin_imp"] == 898000.0
    assert subtotales["sub_3_resultado_periodo"] == 550000.0
