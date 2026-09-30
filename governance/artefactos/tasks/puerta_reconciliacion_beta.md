# Puerta reconciliacion beta
## **Proyecto:** NIIF 18

**Estado:** Completada

`sala_validacion.puede_exportar(df, categorias_validas)` — nueva función que bloquea el Estado de Resultados (RF-09) si la balanza no cuadra o quedan cuentas sin categoría válida, en vez de solo advertir. Decisión de diseño: el CSV de "Mapeo y trazabilidad" queda siempre disponible (incluso sin reconciliar) porque es la herramienta para diagnosticar el problema, no el entregable regulatorio final — solo se bloquea el Excel del Estado de Resultados. 5 tests nuevos (27/27 en verde) + verificación con `AppTest` en ambos escenarios (bloqueado/desbloqueado).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
