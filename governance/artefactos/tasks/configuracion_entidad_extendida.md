# Configuracion entidad extendida
## **Proyecto:** NIIF 18

**Estado:** Completada — (RF-11)

`ConfiguracionEntidad` (en `st.session_state['configuracion_entidad']`) incluye `ruc` y `origen_actividad_principal`; el botón "Re-aplicar auto-clasificación" (RF-03) queda deshabilitado en la UI hasta que `origen_actividad_principal` sea `"confirmado_usuario"` o `"manual"`. Verificado en el navegador (badge cambia de "pendiente" a "confirmada" tras confirmar).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
