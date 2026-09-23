"""
Tests de sala_clasificacion — verifica el árbol de decisión de PRD.md §3 (RF-03),
no la heurística anterior. Casos tomados del criterio de aceptación de RF-03.
"""
from sala_clasificacion import _service as class_svc


def test_impuesto_a_la_renta():
    assert class_svc.clasificar_partida("550100", "Gasto por impuesto a la renta", 5000) == class_svc.CATEGORIA_IMPUESTOS


def test_operacion_discontinuada():
    cat = class_svc.clasificar_partida("410500", "Resultado de operación discontinuada", -2000)
    assert cat == class_svc.CATEGORIA_DISCONTINUADAS


def test_prestamo_bancario_es_financiacion():
    cat = class_svc.clasificar_partida("610100", "Interes de prestamo bancario", 3000)
    assert cat == class_svc.CATEGORIA_FINANCIACION


def test_dividendo_pagado_no_es_partida_de_resultados():
    # Validado contra el Project Summary oficial IASB (IFRS 18, abril 2024, p. 6-7):
    # un dividendo pagado a accionistas se reconoce en el Estado de Cambios en el
    # Patrimonio, no en el Estado de Resultados -> se excluye (Categoría 0), incluso si
    # financiación fuera actividad principal de la entidad.
    cat = class_svc.clasificar_partida("620100", "Dividendo pagado a accionistas", 10000, financiacion_es_actividad_principal=True)
    assert cat == class_svc.CATEGORIA_BALANCE_GENERAL


def test_dividendo_recibido_es_inversion():
    # Sin otras palabras de inversión en la descripción, para probar puntualmente la
    # rama `elif es_dividendo` (no la de `_PALABRAS_INVERSION`).
    cat = class_svc.clasificar_partida("410200", "Dividendo recibido de acciones en otras companias", -500)
    assert cat == class_svc.CATEGORIA_INVERSION


def test_resultado_metodo_participacion_es_inversion():
    cat = class_svc.clasificar_partida("420100", "Resultado por metodo de participacion en asociada", -1500)
    assert cat == class_svc.CATEGORIA_INVERSION


def test_metodo_participacion_no_se_mueve_a_operacion_aunque_inversion_sea_actividad_principal():
    # Validado contra la plantilla oficial FINREP F 02.00 bajo IFRS 18 (fila 74, Anexo
    # V.Parte 2.54 -- EBA/Op/2026/07, 8-jul-2026): el resultado por método de
    # participación en asociadas/negocios conjuntos se presenta como línea propia dentro
    # de Inversión, sin excepción de actividad principal -- a diferencia del interés o
    # dividendo de inversión genérico (que sí puede moverse a OPERACION si invertir es el
    # giro central declarado), esta partida nunca se reclasifica.
    cat = class_svc.clasificar_partida(
        "420100", "Resultado por metodo de participacion en asociada", -1500,
        inversion_es_actividad_principal=True,
    )
    assert cat == class_svc.CATEGORIA_INVERSION


def test_interes_de_pension_sin_actividad_principal_configurada():
    # Interés (beneficios definidos a empleados), sin ConfiguracionEntidad -> se aproxima
    # por signo: saldo > 0 (gasto/pagado) -> FINANCIACION.
    cat = class_svc.clasificar_partida("630200", "Interes neto de pasivo por beneficios definidos", 800)
    assert cat == class_svc.CATEGORIA_FINANCIACION


def test_excepcion_actividad_principal_reclasifica_a_operacion():
    # Paso 5: financiación es actividad principal de la entidad (p.ej. una financiera) ->
    # una partida que candidatearía a FINANCIACION se reclasifica a OPERACION.
    cat = class_svc.clasificar_partida("610100", "Interes de prestamo bancario", 3000, financiacion_es_actividad_principal=True)
    assert cat == class_svc.CATEGORIA_OPERACION


def test_interes_de_pension_no_se_mueve_a_operacion_aunque_financiacion_sea_actividad_principal():
    # Validado contra el Public Statement de ESMA sobre IFRS 18 (17-feb-2026, p. 4):
    # incluso un banco (financiación = actividad principal) debe seguir clasificando en
    # FINANCIACION el interés de pensiones/arrendamientos -- la excepción de actividad
    # principal solo aplica al interés de "transacciones que involucran obtención de
    # fondos" (préstamos/bonos), no a este.
    cat = class_svc.clasificar_partida("630200", "Interes neto de pasivo por beneficios definidos", 800, financiacion_es_actividad_principal=True)
    assert cat == class_svc.CATEGORIA_FINANCIACION


def test_partida_no_recurrente_sin_categoria_clara_es_residual():
    cat = class_svc.clasificar_partida("710500", "Ajuste no recurrente por indemnizacion laboral", 900)
    assert cat == class_svc.CATEGORIA_OPERACION


def test_cuenta_de_balance_sin_movimiento_pl_se_excluye():
    cat = class_svc.clasificar_partida("100000", "Efectivo y equivalentes al efectivo", 250000)
    assert cat == class_svc.CATEGORIA_BALANCE_GENERAL


# Casos reales reproducidos de `balance_prueba_niif18_sap_business_one.xlsx` (hoja
# TB_ERP): cuentas de BALANCE (código 1.x/2.x) cuyo nombre usa vocabulario de flujo por
# convención contable (saldo acumulado, no movimiento del período) -- el rescate por
# `_PALABRAS_MOVIMIENTO_PL` las dejaba entrar al Estado de Resultados por error, inflando
# el resultado operativo en $690,000 frente a `ER_NIIF18` (ver TASKS.md
# ¤discrepancia_motor_tb_erp_pendiente). El código de cuenta (1/2/3 = balance) es una
# señal más fuerte que cualquier palabra de la descripción y no debe revertirse por ella.
def test_deterioro_acumulado_es_cuenta_de_balance_no_movimiento_pl():
    cat = class_svc.clasificar_partida("1.1.02.099", "Deterioro acumulado de cartera", -40000)
    assert cat == class_svc.CATEGORIA_BALANCE_GENERAL


def test_depreciacion_acumulada_es_cuenta_de_balance_no_movimiento_pl():
    cat = class_svc.clasificar_partida("1.2.01.102", "Depreciación acumulada edificios", -240000)
    assert cat == class_svc.CATEGORIA_BALANCE_GENERAL


def test_provision_por_litigios_es_cuenta_de_balance_no_movimiento_pl():
    cat = class_svc.clasificar_partida("2.2.03.001", "Provisión por litigios", -80000)
    assert cat == class_svc.CATEGORIA_BALANCE_GENERAL


def test_gasto_con_palabra_pasivo_en_descripcion_sigue_siendo_movimiento_pl():
    # Regresión de guarda: el rescate por palabra clave debe seguir funcionando cuando el
    # disparador es SOLO la descripción (código que no empieza con 1/2/3) -- no se debe
    # romper el caso que motivó `_PALABRAS_MOVIMIENTO_PL` originalmente.
    cat = class_svc.clasificar_partida("630200", "Interes neto de pasivo por beneficios definidos", 800)
    assert cat == class_svc.CATEGORIA_FINANCIACION
