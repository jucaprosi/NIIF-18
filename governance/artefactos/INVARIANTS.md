# Catálogo de Invariantes y Leyes Inmutables

**Proyecto:** NIIF 18

## Invariantes

### Contrato Bilateral

- **Código invariante:** `INV_BILATERAL_CONTRACT`
- **Vía de verificación:** `(C ⇒ S) ∧ ((C ∧ S) ⇒ ¬R)`

### UTF-8 Estricto sin BOM

- **Código invariante:** `INV_ZERO_UTF8_BOM`
- **Vía de verificación:** `verify_utf8_no_bom`

### Nido de Artefactos Vivos

- **Código invariante:** `INV_LIVING_ARTIFACTS`
- **Vía de verificación:** `living_artifacts_linter`

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
