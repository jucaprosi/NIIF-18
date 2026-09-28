# Conectar PRD a VPA_MAP con rastros ¤ inline
## **Proyecto:** NIIF 18

**Estado:** Completada

## Objetivo aclarado por el propietario

Después de conectar `VPA_MAP.md` a los archivos de código ,
el propietario señaló que faltaba el eslabón intermedio: `PRD.md` es el documento donde
se **describen** las funcionalidades de las que nacen los tokens en `VPA_MAP.md`, pero no
llevaba ningún rastro `¤` inline en sus propias secciones — la cadena de trazabilidad
(VPA_MAP nace → PRD describe → código implementa) estaba rota en el eslabón del medio.

## Corrección aplicada

Se recorrió `PRD.md` completo y se agregó el token `¤` correspondiente de `VPA_MAP.md` en
cada punto donde el PRD describe la funcionalidad que ese token representa:

- §2.1 (categorías) → ; §2.2 (subtotales) → .
- §2.3 (entidades de datos) → , , , en cada
  bloque correspondiente (`ConfiguracionEntidad`, `EntidadPublica`, `CatalogoCIIU`, `MPM`).
- §3 (árbol de decisión) → .
- §4 (tabla de salas) → columna nueva "Token `¤`" con el token de cada una de las 9 salas.
- §5 (RF-01 a RF-11) → cada encabezado de RF ahora lista el/los token(s) de la(s) sala(s)
 que lo implementan, más en RF-03 y / en RF-11.
- §6 (NFR) → como invariante de codificación transversal.
- §9 (arquitectura) → , , y los tokens de gobernanza raíz (,
 , , , ).
- §10 (estado de implementación) → columna "Token `¤`" agregada a la tabla de salas, con
 nota explícita de que cada uno tiene su rastro físico `# verificable en el
  archivo `_service.py` correspondiente.

## Verificación

- `mcp_verify_huellas` sobre `PRD.md` — válido.
- No se modificó lógica de negocio ni estructura de encabezados existente — solo se
  agregaron tokens inline junto al texto ya escrito (consistente con la "Doctrine
  Stigmergy Preservation Bias": la estructura normativa del documento permanece).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
