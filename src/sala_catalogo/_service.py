"""
Compuerta _service.py para sala_catalogo.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-02): catálogo de las 5 categorías NIIF 18 (más la
categoría 0, filtro previo de Balance General) y su presentación canónica.
"""

__all__ = ["CATEGORIAS_NIIF18", "CATEGORIA_BALANCE_GENERAL"]

CATEGORIA_BALANCE_GENERAL = "0. Balance General (No P&L / Excluir)"

# ¤sala_catalogo ¤niif18_categorias
CATEGORIAS_NIIF18 = [
    CATEGORIA_BALANCE_GENERAL,
    "1. Operación (Ingresos / Gastos Operativos)",
    "2. Inversión (Ingresos / Gastos por Inversiones)",
    "3. Financiación (Costos / Pasivos Financieros)",
    "4. Impuestos a las Ganancias",
    "5. Operaciones Discontinuadas",
]
