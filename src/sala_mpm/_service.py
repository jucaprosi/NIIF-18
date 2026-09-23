"""
Compuerta _service.py para sala_mpm.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-05, RF-06): definición, cálculo y conciliación de Medidas
de Rendimiento Definidas por la Gerencia (MPM), ancladas a un subtotal NIIF 18.
"""
from sala_estados_financieros import _service as fs_svc

__all__ = ["PLANTILLAS_MPM", "calcular_base_niif", "construir_registro_mpm"]

TASA_EFECTO_FISCAL = 0.25

PLANTILLAS_MPM = {
    "EBITDA Ajustado": {
        "ajuste": 50000.0,
        "justificacion": "Exclusión de costos no recurrentes de reestructuración para reflejar el desempeño operativo recurrente.",
    },
    "Resultado Operativo Normalizado": {
        "ajuste": 35000.0,
        "justificacion": "Ajuste por contingencias legales atípicas de ejercicios anteriores.",
    },
    "Personalizado": {"ajuste": 0.0, "justificacion": ""},
}

SUBTOTAL_RESULTADO_OPERATIVO = "1. Resultado Operativo"
SUBTOTAL_RESULTADO_PERIODO = "3. Resultado del Periodo"


# ¤sala_mpm ¤mpm
def calcular_base_niif(df_clasificado, subtotal_base):
    """Devuelve el valor del subtotal NIIF 18 de anclaje elegido para una MPM."""
    if df_clasificado is None:
        return 0.0
    _, subtotales = fs_svc.calcular_subtotales(df_clasificado)
    if subtotal_base == SUBTOTAL_RESULTADO_OPERATIVO:
        return subtotales['sub_1_resultado_operativo']
    return subtotales['sub_3_resultado_periodo']


def construir_registro_mpm(nombre, subtotal_base, valor_base_niif, ajuste, justificacion):
    """RF-06: arma la fila de conciliación auditada (nota NIIF 18) para una MPM."""
    return {
        "Métrica": nombre,
        "Anclaje NIIF": subtotal_base,
        "Base NIIF ($)": valor_base_niif,
        "Ajuste ($)": ajuste,
        "Efecto fiscal ($)": -(ajuste * TASA_EFECTO_FISCAL),
        "Total MPM ($)": valor_base_niif + ajuste,
        "Justificación": justificacion,
    }
