"""
Compuerta _service.py para sala_catalogo.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-02): catálogo de las 5 categorías NIIF 18 (más la
categoría 0, filtro previo de Balance General) y su presentación canónica.
"""

__all__ = ["CATEGORIAS_NIIF18", "CATEGORIA_BALANCE_GENERAL", "COLORES_NIIF18"]

# Nombres cortos (2026-09-23, a pedido del propietario, "renombra las categorías") — se
# conserva el prefijo "N." porque `sala_estados_financieros`, `sala_clasificacion` y
# `app.py` lo usan como clave de agrupación (`Categoria_NIIF18.str.startswith('1.')`,
# etc.); solo se recorta la descripción entre paréntesis.
CATEGORIA_BALANCE_GENERAL = "0. Balance General"

# ¤sala_catalogo ¤niif18_categorias
CATEGORIAS_NIIF18 = [
    CATEGORIA_BALANCE_GENERAL,
    "1. Operación",
    "2. Inversión",
    "3. Financiación",
    "4. Impuestos a las Ganancias",
    "5. Discontinuadas",
]

# Paleta de colores por categoría NIIF 18 (2026-09-23, a pedido del propietario, imagen
# de referencia aportada en la sesión). Dos tonos (Operación=verde, Inversión=naranja)
# se extrajeron por muestreo de píxeles directo de la imagen de referencia (confirmados,
# no inferidos); un tercero (Financiación=azul) se tomó del borde inferior visible de la
# misma imagen. Balance General, Impuestos y Discontinuadas no eran visibles en el
# recorte compartido — se extendieron siguiendo la misma paleta pastel/ocre que el
# propietario describió en la reunión (`TASKS.md` ¤categorizacion_colores_niif18) y
# quedan sujetos a confirmación visual si el propietario comparte el resto de la guía.
COLORES_NIIF18 = {
    CATEGORIA_BALANCE_GENERAL: {"fondo": "#E4E4E4", "texto": "#3D3D3D"},
    "1. Operación": {"fondo": "#BBDCA0", "texto": "#2B4014"},
    "2. Inversión": {"fondo": "#F6AE86", "texto": "#5A2A0E"},
    "3. Financiación": {"fondo": "#9CC5EA", "texto": "#0E3358"},
    "4. Impuestos a las Ganancias": {"fondo": "#E6C79C", "texto": "#4A3413"},
    "5. Discontinuadas": {"fondo": "#E8AFAF", "texto": "#5C1414"},
}
