# Validacion europea esma
## **Proyecto:** NIIF 18

**Estado:** Completada — (v3.3)

El propietario confirmó que NIIF 18/IFRS 18 aplica en Europa. Se investigaron repositorios europeos comparables y documentos públicos institucionales: (1) `IFRS-Converter` (GitHub, código abierto) — referencia arquitectónica para la fase beta, ver `PRD.md` §9.1; (2) el *Public Statement* de ESMA sobre IFRS 18 (17-feb-2026) — autoridad europea real, con la sección sobre "issuers with specified main business activities" (bancos, aseguradoras, inmobiliarias) que el usuario pidió como "excepciones finas". Se corrigió `sala_clasificacion` con un caso real que el árbol no cubría: el interés de arrendamientos/pensiones nunca se mueve a Operación por la excepción de actividad principal. 24/24 tests en verde.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
