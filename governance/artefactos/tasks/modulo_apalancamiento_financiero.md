# Módulo de apalancamiento financiero e integración de créditos

## **Proyecto:** NIIF 18

**Estado:** Pendiente — evaluado, NO recomendado sin decisión de negocio explícita (2026-09-23, v3.7)

## Origen

Reunión de producto:
- **Giovanni**: anclar el análisis financiero a un módulo de apalancamiento que dirija al
  usuario a crédito tributario, financiamiento nacional o internacional. Alojar el
  reporte en un link en la nube/hosting para reenviarlo a entidades financieras o
  inversionistas. Firma electrónica y protección de datos. Botón "Quiero liquidez y
  financiamiento".
- **Roberto**: modelo de análisis de riesgo crediticio que evalúe balances y calcule
  calificación + monto de crédito preaprobado.

## Evaluación — riesgo alto, no es una extensión del producto actual

Esto **no es una función más del motor de clasificación NIIF 18** — es un producto
distinto (fintech / bróker de crédito) con requisitos que esta app hoy no tiene:

1. **Infraestructura**: la app es hoy una sesión Streamlit local, sin cuentas de usuario
   persistentes, sin base de datos, sin backend. `sala_reportes` genera un archivo Excel
   descargable dentro de la sesión — no hay "link en la nube" ni hosting de reportes.
   Construir esto implica una infraestructura completamente nueva (autenticación,
   almacenamiento persistente, hosting), no una función dentro de `sala_reportes`.
2. **Firma electrónica**: requiere un proveedor certificado (en Ecuador: entidades
   acreditadas por la ARCOTEL/Banco Central según la Ley de Comercio Electrónico) — es
   una integración de terceros con su propio marco legal, no una función de la app.
3. **Riesgo regulatorio**: conectar el análisis financiero de una entidad con oferta de
   crédito (aunque sea un "link de salida") puede calificar como intermediación
   financiera o promoción de productos financieros bajo la regulación ecuatoriana (Ley
   de creación de la Red de Seguridad Financiera, regulaciones de la Superintendencia de
   Bancos) — **no evaluado en este proyecto**, requiere asesoría legal antes de construir
   nada, no solo antes de lanzar.
4. **Scoring de riesgo crediticio**: requiere datos y expertise de riesgo crediticio (no
   de contabilidad NIIF) — un modelo de "calificación y monto de crédito preaprobado"
   construido sin ese expertise, ofrecido a usuarios reales, es un riesgo de producto
   serio (decisiones de crédito basadas en un modelo no validado).

## Recomendación

**No bundlear este módulo en la misma app.** Si el propietario decide perseguirlo:
- Tratarlo como un producto o módulo separado, con su propia decisión de negocio y
  posiblemente su propio equipo/socio con expertise en riesgo crediticio.
- Si se integra, empezar por lo más simple y de menor riesgo: un enlace de salida que
  refiera al usuario a una entidad financiera (sin scoring interno, sin firma
  electrónica, sin hosting de reportes) — validar interés real antes de construir la
  infraestructura completa.
- Consultar asesoría legal sobre las implicaciones regulatorias **antes** de diseñar
  cualquier flujo, no después.

## No implementado — solo documentado

Este archivo registra la evaluación para que quede trazable en `VPA_MAP.md`/`TASKS.md`.
No se ha escrito código ni se recomienda iniciarlo sin una decisión de negocio explícita
del propietario, informada por asesoría legal.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
