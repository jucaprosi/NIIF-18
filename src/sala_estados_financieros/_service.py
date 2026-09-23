"""
Compuerta _service.py para sala_estados_financieros.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-04, RF-07): generación del Estado de Resultados y cálculo
de los 3 subtotales mandatorios (PRD.md §2.2) a partir de la balanza ya clasificada.
"""

__all__ = ["is_income_account", "calculate_pl_contribution", "calcular_subtotales"]


def is_income_account(cta, desc, saldo):
    # Los términos de gasto prevalecen: "Costo de ventas" o "Gasto por impuesto a las
    # ganancias" no son ingresos aunque contengan otras palabras ambiguas.
    if cta.startswith('4'):
        return True
    if any(w in desc for w in ['costo', 'gasto', 'impuesto', 'depreciaci', 'amortizaci', 'comisi', 'provisi', 'perdida', 'pérdida', 'deterioro']):
        return False
    if any(w in desc for w in ['ingreso', 'venta', 'honorario', 'ganancia', 'rendimiento', 'dividendo', 'utilidad']):
        return True
    if 'interes' in desc or 'interés' in desc:
        return saldo < 0
    if cta[:1] in ('5', '6', '7', '8', '9'):
        return False
    return saldo < 0


def calculate_pl_contribution(row):
    if str(row['Categoria_NIIF18']).startswith('0.'):
        return 0.0
    cta, desc, saldo = str(row['Cuenta']).strip(), str(row['Descripcion']).strip().lower(), float(row['Saldo'])
    return abs(saldo) if is_income_account(cta, desc, saldo) else -abs(saldo)


# ¤sala_estados_financieros ¤subtotales_mandatorios
def calcular_subtotales(df_clasificado):
    """Calcula PL_Neto por partida y los 3 subtotales mandatorios (PRD.md §2.2).

    Devuelve (df_con_pl, subtotales) donde subtotales es un dict con las claves
    v_operacion, v_inversion, v_financiacion, v_impuestos, v_discontinuadas,
    sub_1_resultado_operativo, sub_2_antes_fin_imp, sub_3_resultado_periodo.
    """
    df = df_clasificado.copy()
    df['PL_Neto'] = df.apply(calculate_pl_contribution, axis=1)

    def _suma(prefijo):
        return float(df[df['Categoria_NIIF18'].str.startswith(prefijo)]['PL_Neto'].sum())

    v_op, v_inv, v_fin = _suma('1.'), _suma('2.'), _suma('3.')
    v_imp, v_disc = _suma('4.'), _suma('5.')
    sub_1 = v_op
    sub_2 = v_op + v_inv
    sub_3 = v_op + v_inv + v_fin + v_imp + v_disc

    subtotales = {
        'v_operacion': v_op, 'v_inversion': v_inv, 'v_financiacion': v_fin,
        'v_impuestos': v_imp, 'v_discontinuadas': v_disc,
        'sub_1_resultado_operativo': sub_1,
        'sub_2_antes_fin_imp': sub_2,
        'sub_3_resultado_periodo': sub_3,
    }
    return df, subtotales
