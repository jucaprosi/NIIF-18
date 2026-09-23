import pandas as pd
from sala_importacion import _service as imp_svc


def test_clean_numeric_series_maneja_simbolos_y_negativos_contables():
    s = pd.Series(["$1,000.50", "(200.00)", "  300  ", "€50"])
    limpio = imp_svc.clean_numeric_series(s)
    assert list(limpio) == [1000.50, -200.00, 300.0, 50.0]


def test_infer_columns_detecta_codigo_descripcion_saldo_sin_cabeceras_estandar():
    df = pd.DataFrame({
        "col_a": ["100000", "110000", "120000"],
        "col_b": ["Efectivo y equivalentes", "Cuentas por cobrar comerciales", "Inventarios"],
        "col_c": ["250000.00", "180000.50", "-320000.00"],
    })
    cta, desc, saldo, confianza = imp_svc.infer_columns_by_mathematical_weights(df)
    assert cta == "col_a"
    assert desc == "col_b"
    assert saldo == "col_c"
    assert confianza > 0


def test_construir_balanza_estandar_descarta_filas_sin_cuenta():
    df_raw = pd.DataFrame({"c": ["100000", None], "d": ["Efectivo", "Total"], "s": [100.0, None]})
    out = imp_svc.construir_balanza_estandar(df_raw, "c", "d", "s")
    assert len(out) == 1
    assert list(out.columns) == ["Cuenta", "Descripcion", "Saldo"]


def test_evaluar_calidad_balanza_acepta_columnas_genuinas():
    df = pd.DataFrame({
        "Cuenta": ["1.1.01.001", "1.1.01.002", "4.1.01.001", "5.1.01.001"],
        "Saldo": ["100000.00", "-320000.50", "250000", "0"],
    })
    ok, motivos = imp_svc.evaluar_calidad_balanza(df, "Cuenta", "Saldo")
    assert ok is True
    assert motivos == []


def test_evaluar_calidad_balanza_rechaza_columna_saldo_de_texto():
    # Caso real: una hoja de referencia (no una balanza) donde la columna inferida como
    # "Saldo" es en realidad texto libre — reproduce MAPEO_NIIF18 del archivo de prueba.
    df = pd.DataFrame({
        "Cuenta": ["4.1.01.001", "4.1.02.001", "4.2.01.001", "4.2.02.001"],
        "Saldo": ["Documentar política", "Revisar contrato", "Correcto", None],
    })
    ok, motivos = imp_svc.evaluar_calidad_balanza(df, "Cuenta", "Saldo")
    assert ok is False
    assert "0%" in motivos[0]


def test_evaluar_calidad_balanza_columna_saldo_vacia():
    df = pd.DataFrame({"Cuenta": ["1.1.01.001", "1.1.01.002", "1.1.01.003"], "Saldo": [None, None, ""]})
    ok, motivos = imp_svc.evaluar_calidad_balanza(df, "Cuenta", "Saldo")
    assert ok is False
    assert "0%" in motivos[0]


def test_evaluar_calidad_balanza_rechaza_saldo_mayormente_nan_aunque_lo_presente_sea_numerico():
    # Pocos valores presentes, todos numéricos, pero la mayoría de filas son NaN: no es
    # una balanza real (una balanza tiene saldo, aunque sea 0, en casi toda cuenta).
    df = pd.DataFrame({
        "Cuenta": [f"1.1.01.{i:03d}" for i in range(13)],
        "Saldo": ["813000", "898000", "810000", "550000"] + [None] * 9,
    })
    ok, motivos = imp_svc.evaluar_calidad_balanza(df, "Cuenta", "Saldo")
    assert ok is False


def test_evaluar_calidad_balanza_rechaza_columna_cuenta_que_en_realidad_es_montos():
    # Caso real: reproduce CHECKS del archivo de prueba — el motor infirió una columna de
    # montos ("Actual": 11795000, 0, 0...) como si fuera el código de cuenta, mientras la
    # columna de saldo ("Diferencia": mayormente 0.0) sí pasaba el umbral de saldo por sí
    # sola. Sin este segundo chequeo, esa hoja (que no es una balanza) se aceptaba.
    df = pd.DataFrame({
        "Cuenta": ["11795000", "11795000", "0", "0", "0", "0", "0", "0"],
        "Saldo": ["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "-1.0", "-1.0"],
    })
    ok, motivos = imp_svc.evaluar_calidad_balanza(df, "Cuenta", "Saldo")
    assert ok is False
    assert "código de cuenta" in motivos[0]
