# Doctrina fuera de frontend
## **Proyecto:** NIIF 18

**Estado:** Completada

Se retiró la pestaña "Visor doctrinal" de `src/app.py` — la `biblioteca_doctrinal/` es material de referencia para el desarrollo del backend (fundamentar el motor de clasificación, RF-03), no contenido de cara al usuario final de la app. De paso quedó documentado que, mientras estuvo, apuntaba a la ruta ya inexistente `docs/biblioteca_doctrinal` (el contenido se había movido a `governance/artefactos/biblioteca_doctrinal` en un commit previo) — un bug que ya no aplica al haberse eliminado la pestaña. `TITULOS_DOCTRINALES` y los imports `os`/`re` (usados solo por esa pestaña) se removieron de `app.py`.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
