"""
Compuerta _service.py para sala_importacion.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-01): importar y validar una balanza de comprobación desde
CSV o Excel, sin depender de nombres de cabecera fijos (ver ¤¦aportes A-01 en
governance/artefactos/APORTES_INEDITOS.md).
"""
import pandas as pd

__all__ = [
    "clean_numeric_series",
    "read_excel_smart_header",
    "infer_columns_by_mathematical_weights",
    "construir_balanza_estandar",
    "sugerir_hoja_balanza",
    "evaluar_calidad_balanza",
]

COLUMNAS_ESTANDAR = ["Cuenta", "Descripcion", "Saldo"]

# Un archivo Excel puede traer, además de la balanza real, hojas de referencia con otra
# estructura (respuesta esperada, estado de resultados ya resumido, notas, controles de
# prueba). Si el usuario selecciona una de esas hojas, `infer_columns_by_mathematical_
# weights` igual "adivina" 3 columnas — no tiene forma de saber que la premisa (esto es
# una balanza) es falsa. Verificado empíricamente en esta sesión contra
# `balance_prueba_niif18_sap_business_one.xlsx` (8 pestañas, solo TB_ERP es una balanza
# real): la columna Saldo real es 100% numérica y la columna Cuenta real es 0% numérica
# (códigos tipo "1.1.01.001" con varios puntos no parsean como número limpio); hojas que
# no son balanzas (MAPEO_NIIF18, ER_NIIF18, CHECKS) fallan uno de los dos umbrales.
UMBRAL_SALDO_NUMERICO = 0.70
UMBRAL_CUENTA_NUMERICA_MAXIMO = 0.30


def _a_numero_coercido(series):
    """Convierte a numérico preservando NaN para lo no convertible (a diferencia de
    `clean_numeric_series`, que además rellena con 0.0) — necesario para medir qué
    proporción de la columna es *genuinamente* numérica, sin que el relleno la enmascare.
    """
    return pd.to_numeric(
        series.astype(str).str.replace('$', '', regex=False).str.replace('€', '', regex=False)
        .str.replace('£', '', regex=False).str.replace(',', '', regex=False)
        .str.replace('(', '-', regex=False).str.replace(')', '', regex=False).str.strip(),
        errors='coerce'
    )


def clean_numeric_series(series):
    return _a_numero_coercido(series).fillna(0.0)


def evaluar_calidad_balanza(df_raw, col_cuenta, col_saldo):
    """Valida la premisa que `infer_columns_by_mathematical_weights` nunca verifica:
    ¿esta hoja es realmente una balanza de comprobación? Devuelve (bool, list[str]),
    igual patrón que `sala_validacion.puede_exportar`.

    Detectado en esta sesión: un archivo Excel puede traer hojas de referencia (respuesta
    esperada, Estado de Resultados ya resumido, controles de prueba) con una estructura
    distinta a una balanza. Sin esta validación, `clean_numeric_series` convierte
    silenciosamente texto no numérico en 0.0 (`fillna(0.0)`), y la balanza resultante
    parece "cuadrar" (todo en cero) o produce cifras sin sentido, sin ninguna advertencia.

    Dos condiciones, no una sola:

    1. **Saldo mayoritariamente numérico** (umbral `UMBRAL_SALDO_NUMERICO`), medido sobre
       el **total de filas**, no solo sobre las celdas no vacías — decisión deliberada:
       en una balanza real, prácticamente toda cuenta tiene un saldo, aunque sea cero.
       Una columna con pocos valores presentes pero 100% numéricos entre ellos (el resto
       `NaN`) no es una balanza real — caso real: hoja `ER_NIIF18` del archivo de prueba,
       9 de 13 filas `NaN` en la columna inferida como "Saldo".
    2. **Cuenta mayoritariamente NO numérica** (techo `UMBRAL_CUENTA_NUMERICA_MAXIMO`):
       un código de cuenta genuino (p. ej. "1.1.01.001", con varios puntos) no parsea
       como número limpio. La condición 1 sola no basta — caso real: hoja `CHECKS` del
       archivo de prueba, donde el motor infirió una columna de montos ("Actual") como
       si fuera el código de cuenta, y la columna "Diferencia" (mayormente ceros) pasaba
       el umbral de saldo por sí sola.
    """
    total_filas = len(df_raw)
    if total_filas == 0:
        return False, ["La hoja no tiene filas de datos."]
    motivos = []
    ratio_saldo = float((~_a_numero_coercido(df_raw[col_saldo].astype(str)).isna()).mean())
    if ratio_saldo < UMBRAL_SALDO_NUMERICO:
        motivos.append(
            f"Solo el {ratio_saldo * 100:.0f}% de las filas tienen un valor genuinamente "
            f"numérico en la columna de saldo inferida ('{col_saldo}') — se requiere al menos "
            f"{UMBRAL_SALDO_NUMERICO * 100:.0f}%."
        )
    ratio_cuenta_numerica = float((~_a_numero_coercido(df_raw[col_cuenta].astype(str)).isna()).mean())
    if ratio_cuenta_numerica > UMBRAL_CUENTA_NUMERICA_MAXIMO:
        motivos.append(
            f"El {ratio_cuenta_numerica * 100:.0f}% de las filas de la columna de cuenta inferida "
            f"('{col_cuenta}') son números limpios — un código de cuenta real casi nunca lo es "
            f"(se permite hasta {UMBRAL_CUENTA_NUMERICA_MAXIMO * 100:.0f}%); probablemente es una "
            "columna de montos, no de códigos de cuenta."
        )
    if motivos:
        return False, [
            "Esta hoja probablemente no es una balanza de comprobación: " + " ".join(motivos)
            + " Seleccione otra pestaña o corrija el mapeo de columnas manualmente."
        ]
    return True, []


def read_excel_smart_header(excel_file, sheet_name):
    df_preview = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, nrows=15)
    best_row, max_non_na = 0, 0
    for r in range(len(df_preview)):
        non_na = df_preview.iloc[r].dropna().count()
        if non_na > max_non_na and non_na >= 2:
            max_non_na, best_row = non_na, r
    df_full = pd.read_excel(excel_file, sheet_name=sheet_name, header=best_row)
    return df_full.dropna(how='all', axis=1).dropna(how='all', axis=0)


def sugerir_hoja_balanza(sheet_names):
    palabras_clave = ('tb', 'balanza', 'trial', 'balance', 'saldos', 'datos', 'data', 'cuentas')
    return next((i for i, s in enumerate(sheet_names) if any(k in s.lower() for k in palabras_clave)), 0)


def infer_columns_by_mathematical_weights(df):
    # Infiere el rol (código/descripción/saldo) por forma de los datos, no por nombre de
    # cabecera: generaliza entre balanzas exportadas de distintos ERPs (SAP B1, etc.) que
    # nombran sus columnas de forma inconsistente. Ver aporte A-01 en APORTES_INEDITOS.md.
    cols = list(df.columns)
    if len(cols) < 2:
        return cols[0], cols[0], cols[0], 1.0
    sample = df.head(min(len(df), 120))
    scores_cta, scores_desc, scores_saldo = {}, {}, {}
    total_cols = max(1, len(cols) - 1)
    for i, col in enumerate(cols):
        s = sample[col].astype(str).str.strip()
        ordinal = i / total_cols
        clean_num = clean_numeric_series(s)
        num_ratio = float((~clean_num.isna()).mean())
        has_neg = 1.0 if (clean_num < 0).any() else 0.0
        code_ratio = float((s.str.match(r'^[0-9A-Za-z\.\-_/]+$') & (~s.str.contains(' ', regex=False))).mean()) if len(s) > 0 else 0.0
        spaces_ratio = float(s.str.contains(r'\s+', regex=True).mean()) if len(s) > 0 else 0.0
        avg_char_len, uniq_ratio = float(s.str.len().mean()) if len(s) > 0 else 0.0, float(s.nunique() / max(1, len(s)))
        scores_saldo[col] = (0.50 * num_ratio) + (0.20 * has_neg) + (0.15 * (1.0 - code_ratio)) + (0.15 * ordinal)
        scores_cta[col] = (0.40 * code_ratio) + (0.30 * uniq_ratio) + (0.20 * (1.0 - spaces_ratio)) + (0.10 * (1.0 - ordinal))
        scores_desc[col] = (0.50 * spaces_ratio) + (0.30 * (1.0 - num_ratio)) + (0.20 * min(1.0, avg_char_len / 15.0))
    best_score, best_assignment = -1.0, (cols[0], cols[min(1, len(cols) - 1)], cols[-1])
    for c_i in cols:
        for d_j in cols:
            if d_j == c_i and len(cols) >= 3:
                continue
            for s_k in cols:
                if (s_k == c_i or s_k == d_j) and len(cols) >= 3:
                    continue
                total = scores_cta[c_i] + scores_desc[d_j] + scores_saldo[s_k]
                if total > best_score:
                    best_score, best_assignment = total, (c_i, d_j, s_k)
    return best_assignment[0], best_assignment[1], best_assignment[2], min(100.0, max(10.0, (best_score / 3.0) * 100.0))


# ¤sala_importacion
def construir_balanza_estandar(df_raw, col_cuenta, col_descripcion, col_saldo):
    """Normaliza un DataFrame crudo a las 3 columnas estándar (Cuenta, Descripcion, Saldo).

    Descarta filas sin código de cuenta usando `notna()` sobre la columna original, no
    comparando el texto ya convertido contra el literal 'nan': una celda vacía en una
    columna de cuenta tipo texto llega como `None` (que se convierte a la cadena
    'None', no 'nan'), así que comparar strings dejaba pasar filas vacías. Detectado por
    tests/test_sala_importacion.py::test_construir_balanza_estandar_descarta_filas_sin_cuenta.
    """
    cuenta_valida = df_raw[col_cuenta].notna() & (df_raw[col_cuenta].astype(str).str.strip() != '')
    df_raw = df_raw[cuenta_valida]
    df = pd.DataFrame({
        'Cuenta': df_raw[col_cuenta].astype(str),
        'Descripcion': df_raw[col_descripcion].astype(str),
        'Saldo': clean_numeric_series(df_raw[col_saldo]),
    })
    return df.reset_index(drop=True)
