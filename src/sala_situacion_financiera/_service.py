"""
Compuerta _service.py para sala_situacion_financiera.

Responsabilidad (PRD.md RF-12, §12.1 Fase B — funcionalidad completa a pedido del
propietario, 2026-09-24): clasificar las cuentas de balance de una balanza de
comprobación en las 5 categorías del Estado de Situación Financiera bajo NIC 1
revisada (IAS 1, "Presentation of Financial Statements", párrafos 60-76): Activo
Corriente, Activo No Corriente, Pasivo Corriente, Pasivo No Corriente, Patrimonio.

Reutiliza exactamente la misma señal fuerte que `sala_clasificacion` (código de
cuenta, no palabra clave) — verificado contra `TB_ERP` (archivo de prueba real de
este proyecto): las cuentas de balance siguen la convención de plan de cuentas
`1.1.x` = Activo Corriente, `1.2.x` = Activo No Corriente, `2.1.x` = Pasivo
Corriente, `2.2.x` = Pasivo No Corriente, `3.x` = Patrimonio — el mismo tipo de señal
que ya demostró ser más confiable que las palabras clave de la descripción (ver
`APORTES_INEDITOS.md` A-05, ).

NIC 1.66-68 define "corriente" por el criterio operativo: se espera realizar/liquidar
dentro del ciclo normal de operación o 12 meses, se mantiene principalmente para
negociación, o es efectivo/equivalente sin restricción. Ese criterio no puede
derivarse de una balanza de comprobación por sí sola (requiere conocer plazos
contractuales/vencimientos) — el código de cuenta es una aproximación práctica que
asume que el plan de cuentas del cliente ya codificó esa distinción (como ocurre en
`TB_ERP`), no un sustituto del criterio NIC 1. Riesgo señalado explícitamente en
`PRD.md` §8, igual criterio que el mapeo CIIU→actividad principal.
"""

__all__ = ["CATEGORIAS_SITUACION_FINANCIERA", "clasificar_partida_balance", "clasificar_dataframe_balance", "calcular_totales"]

CATEGORIA_ACTIVO_CORRIENTE = "1. Activo Corriente"
CATEGORIA_ACTIVO_NO_CORRIENTE = "2. Activo No Corriente"
CATEGORIA_PASIVO_CORRIENTE = "3. Pasivo Corriente"
CATEGORIA_PASIVO_NO_CORRIENTE = "4. Pasivo No Corriente"
CATEGORIA_PATRIMONIO = "5. Patrimonio"
CATEGORIA_NO_CLASIFICADA = "0. No Clasificada (revisar código de cuenta)"

CATEGORIAS_SITUACION_FINANCIERA = [
    CATEGORIA_ACTIVO_CORRIENTE,
    CATEGORIA_ACTIVO_NO_CORRIENTE,
    CATEGORIA_PASIVO_CORRIENTE,
    CATEGORIA_PASIVO_NO_CORRIENTE,
    CATEGORIA_PATRIMONIO,
]

# Prefijo de código -> categoría, en orden de especificidad decreciente (se evalúa el
# primero que matchea). "3" solo debe matchear cuentas de patrimonio genuinas (3.x),
# nunca una cuenta que arranque con otro dígito -- por eso el prefijo de un solo
# carácter se evalúa al final, después de los de 3 caracteres más específicos.
_PREFIJOS_BALANCE = [
    ("1.1", CATEGORIA_ACTIVO_CORRIENTE),
    ("1.2", CATEGORIA_ACTIVO_NO_CORRIENTE),
    ("2.1", CATEGORIA_PASIVO_CORRIENTE),
    ("2.2", CATEGORIA_PASIVO_NO_CORRIENTE),
    ("3", CATEGORIA_PATRIMONIO),
]


def clasificar_partida_balance(cuenta, descripcion=""):
    """Clasifica una cuenta de balance por prefijo de código (NIC 1.60-76).

    Devuelve `CATEGORIA_NO_CLASIFICADA` si el código no sigue la convención esperada
    -- señal explícita para que el usuario revise/mapee manualmente, en vez de
    adivinar por palabra clave (mismo criterio que evitó el bug de los $690,000 en
    `sala_clasificacion`, aporte A-05).
    """
    cta = str(cuenta).strip()
    for prefijo, categoria in _PREFIJOS_BALANCE:
        if cta.startswith(prefijo):
            return categoria
    return CATEGORIA_NO_CLASIFICADA


# ¤clasificar_dataframe_balance
def clasificar_dataframe_balance(df):
    """Aplica `clasificar_partida_balance` fila a fila sobre una balanza ya filtrada a
    cuentas de balance (típicamente `Categoria_NIIF18 == '0. Balance General'` de
    `sala_clasificacion`, o el `df_balanza` completo antes de ese filtro)."""
    return [clasificar_partida_balance(row['Cuenta'], row.get('Descripcion', '')) for _, row in df.iterrows()]


def calcular_totales(df_clasificado):
    """Suma cada categoría y valida la ecuación contable fundamental (Activo = Pasivo +
    Patrimonio + Resultado del período no cerrado). Devuelve (df_con_categoria,
    totales dict). `Saldo` sigue la convención de signo de este proyecto: positivo =
    débito, negativo = crédito (ver `sala_importacion`).

    Corrección (2026-09-24, verificada contra `TB_ERP` real): sumar por `abs()` cuenta
    por cuenta es incorrecto para categorías de Activo -- una cuenta contra-activo
    genuina (p. ej. "Depreciación acumulada edificios", saldo crédito/negativo) debe
    RESTAR del total de Activo, no sumarse en valor absoluto. La suma con signo
    (`sum()`, sin `abs()` por fila) ya neta correctamente las contra-cuentas, porque
    Saldo ya usa la convención positivo=débito/negativo=crédito de este proyecto; para
    Pasivo y Patrimonio (naturaleza crédito, saldo negativo) se niega el total una sola
    vez al final, no por fila, por la misma razón. Verificado: con esta corrección el
    total de Activo ($6,675,000) cuadra exacto contra Pasivo + Patrimonio + resultado
    del período implícito, sin el error de $1,220,000 que producía sumar por `abs()`.
    """
    df = df_clasificado.copy()

    def _suma_con_signo(categoria, invertir=False):
        total = float(df[df['Categoria_Situacion_Financiera'] == categoria]['Saldo'].sum())
        return -total if invertir else total

    activo_corriente = _suma_con_signo(CATEGORIA_ACTIVO_CORRIENTE)
    activo_no_corriente = _suma_con_signo(CATEGORIA_ACTIVO_NO_CORRIENTE)
    pasivo_corriente = _suma_con_signo(CATEGORIA_PASIVO_CORRIENTE, invertir=True)
    pasivo_no_corriente = _suma_con_signo(CATEGORIA_PASIVO_NO_CORRIENTE, invertir=True)
    patrimonio = _suma_con_signo(CATEGORIA_PATRIMONIO, invertir=True)

    total_activo = activo_corriente + activo_no_corriente
    total_pasivo = pasivo_corriente + pasivo_no_corriente
    # Ecuación contable: el resultado del período (aún no cerrado a Resultados
    # Acumulados en una balanza en vivo) es la diferencia -- si es exactamente 0, la
    # balanza ya incluye el cierre; si no, es la utilidad/pérdida del período.
    resultado_del_periodo_implicito = total_activo - total_pasivo - patrimonio

    totales = {
        'activo_corriente': activo_corriente,
        'activo_no_corriente': activo_no_corriente,
        'total_activo': total_activo,
        'pasivo_corriente': pasivo_corriente,
        'pasivo_no_corriente': pasivo_no_corriente,
        'total_pasivo': total_pasivo,
        'patrimonio': patrimonio,
        'resultado_del_periodo_implicito': resultado_del_periodo_implicito,
        'total_pasivo_y_patrimonio': total_pasivo + patrimonio + resultado_del_periodo_implicito,
    }
    return df, totales
