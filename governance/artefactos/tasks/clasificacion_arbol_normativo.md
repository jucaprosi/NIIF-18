# Clasificacion arbol normativo
## **Proyecto:** NIIF 18

**Estado:** Completada

`auto_classify_niif18_series` reemplazada por `sala_clasificacion.clasificar_partida`, que sigue el árbol de `PRD.md` §3 paso a paso y recibe `financiacion_es_actividad_principal` / `inversion_es_actividad_principal` como parámetros explícitos. Al reestructurar se encontraron y corrigieron 2 regresiones reales (no parcheadas — causa raíz investigada, ver `PRD.md` §10): falsos positivos del prefiltro de Categoría 0 sobre gastos que mencionan "pasivo"/"activo" en su descripción, y filas sin cuenta que no se descartaban cuando la celda vacía era `None` en vez de `NaN`. **Actualización (v3.2):** el árbol se validó además contra el *Project Summary* oficial gratuito del IASB (ver ) y se corrigió una regla normativa real: los dividendos pagados no son partida del Estado de Resultados.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
