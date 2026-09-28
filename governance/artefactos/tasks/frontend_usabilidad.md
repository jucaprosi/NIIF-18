# Frontend usabilidad
## **Proyecto:** NIIF 18

**Estado:** Completada

Optimización del frontend (`src/app.py`) aplicando patrones de usabilidad de dashboards de referencia (guía `developing-with-streamlit`): tema corporativo nativo en `.streamlit/config.toml` (reemplaza el CSS inyectado), iconografía Material Symbols, tarjetas KPI con borde, badges de estado (cuadre de balanza, pendientes de clasificación), formato monetario vía `column_config` en vez de strings manuales, confirmación modal antes de resetear la sesión, `segmented_control` en el formulario de MPM, y estados vacíos consistentes por pestaña. Verificado con `streamlit.testing.v1.AppTest` (estado vacío, balanza cargada, MPM registrada) y con capturas del navegador. Pendiente: `sala_reportes`/lógica de negocio no se tocó (fuera de alcance de esta tarea); ver .

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
