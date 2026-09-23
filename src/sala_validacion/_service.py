"""
Compuerta _service.py para sala_validacion.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-08): validaciones normativas de etiquetas y estructura
antes de permitir avanzar a exportación.
"""
from sala_catalogo import _service as cat_svc

__all__ = ["balanza_cuadrada", "contar_cuentas_pendientes", "puede_exportar"]

TOLERANCIA_CUADRE = 0.01


def balanza_cuadrada(suma_saldos):
    """RF-01: la balanza cuadra si la suma neta de saldos es ~0 (debe = haber)."""
    return abs(float(suma_saldos)) < TOLERANCIA_CUADRE


def contar_cuentas_pendientes(df_clasificado, categorias_validas=None):
    """RF-02/RF-08: cuenta cuántas filas no tienen una categoría NIIF 18 válida."""
    categorias_validas = categorias_validas or cat_svc.CATEGORIAS_NIIF18
    return int((~df_clasificado['Categoria_NIIF18'].isin(categorias_validas)).sum())


# ¤sala_validacion
def puede_exportar(df_clasificado, categorias_validas=None):
    """Puerta de reconciliación obligatoria antes de RF-09 (TASKS.md ¤puerta_reconciliacion_beta,
    inspirada en la revisión del repositorio `IFRS-Converter`: "no reconciliation, no
    finalized result"). Antes solo se advertía con un badge; ahora se bloquea la
    exportación si la balanza no cuadra o quedan cuentas sin categoría válida.

    Devuelve (bool, list[str]) — si puede exportar, y la lista de motivos de bloqueo
    (vacía si puede_exportar es True).
    """
    motivos = []
    suma = float(df_clasificado['Saldo'].sum())
    if not balanza_cuadrada(suma):
        motivos.append(f"La balanza no cuadra (neto de $ {suma:,.2f}, tolerancia $ {TOLERANCIA_CUADRE}).")
    pendientes = contar_cuentas_pendientes(df_clasificado, categorias_validas)
    if pendientes > 0:
        motivos.append(f"{pendientes} cuenta(s) sin categoría NIIF 18 válida.")
    return (len(motivos) == 0, motivos)
