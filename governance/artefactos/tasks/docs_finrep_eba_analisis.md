# Análisis de `docs/` — endoso UE de IFRS 18 y plantilla oficial FINREP

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-23, v3.5)

## Pregunta del propietario

"Analiza `docs/` y propón cómo se implementarán los cálculos y criterios a un balance
contable para que esté normado bajo NIIF 18."

## Qué había en `docs/`

El propietario agregó documentos oficiales nuevos de la European Banking Authority
(EBA), no presentes en el análisis anterior de §11 (que solo tenía el ECEP 2025 de
ESMA): `Opinion Finrep IFRS 18 - interim period.pdf` (EBA/Op/2026/07, 8-jul-2026) y sus
anexos técnicos (`Annex 1` — informe final, `Annex 2` — plantillas FINREP en Excel y
las instrucciones en Word, cada uno en versión `_CV` limpia y `_TC` con control de
cambios).

## Lectura realizada

- `Opinion Finrep IFRS 18 - interim period.pdf` — leído completo.
- Hoja `"2 (post consultation)"` (= plantilla F 02.00, Estado de Resultados) de
  `Annex 2 (Finrep templates IFRS 18- Annex III)_CV.xlsx` — leída completa (160 filas),
  con cita de párrafo IFRS 18 por línea.
- Nombres de hoja de ambos anexos (III y IV) confirmados: `Index`, `2`, `16`, `20`, `45`
  (post consultation) — F 02.00, F 16.xx, F 20.03, F 45.02-03 respectivamente.
- No se leyeron en detalle las hojas F 16/F 20/F 45 ni las instrucciones `.docx`
  (Anexo V) — ver "Fuera de alcance" abajo.

## Dos resultados concretos (ver `PRD.md` §11.2 para el detalle normativo completo)

1. **Corrección de estado regulatorio**: IFRS 18 **ya fue endosado** en la UE
   (Reglamento de Ejecución (UE) 2026/338, 13-feb-2026) — actualiza §11.1, que decía
   "aún no endosado" con base en una fuente de oct-2025.
2. **Confirmación con fuente oficial de una regla ya sospechada**: el resultado por
   método de participación en asociadas/negocios conjuntos no tiene excepción de
 actividad principal — resuelve , aplicado
   en `sala_clasificacion._service.clasificar_partida`.

## Propuesta de implementación (respuesta a la pregunta del propietario)

**No se propone adoptar el catálogo de líneas de FINREP.** FINREP es el reporte
supervisor bancario de la EBA — decenas de líneas específicas a instrumentos
financieros, deterioro por etapas de IFRS 9, garantías de depósito, etc., diseñadas
para bancos bajo supervisión prudencial europea. El público objetivo de este proyecto
(`PRD.md` §1) es una entidad genérica, no necesariamente financiera ni europea. Adoptar
el catálogo completo añadiría decenas de campos irrelevantes para la mayoría de
usuarios y un costo de mantenimiento que no se sostiene sin un cliente bancario europeo
real.

**Sí se propone (y ya se aplicó) adoptar**:

- La **taxonomía de categorías y el orden de subtotales** como validación cruzada del
  árbol §3 y de `calcular_subtotales` — ya coincide (Operación → Inversión → Resultado
  Operativo+Inversión → Financiación → antes de impuesto → impuesto → resultado del
  período), sin cambios de código necesarios más allá del método de participación.
- Las **citas de párrafo exactas** (IFRS 18.69(a), .71, .75, .76(a)/(b), .118(e)/(f),
  IE13) como reemplazo progresivo de las citas por página de documentos secundarios
  (Project Summary, ESMA) en `PRD.md` §3 y `biblioteca_doctrinal/` — pendiente como
  trabajo de limpieza de citas, no bloqueante, se puede hacer incrementalmente.
- Que el **método de participación sea reclasificable a un renglón propio y visible**
  en el Estado de Resultados exportado (`sala_reportes`), no fusionado dentro de
  "Inversión" genérica — candidato de mejora de presentación, no implementado aún (no
  bloqueante para el MVP; se deja como sugerencia de UX, no como tarea abierta porque no
  fue solicitada explícitamente por el propietario).

## Fuera de alcance (justificado)

- Hojas F 16 (desglose de ingresos/gastos por naturaleza), F 20.03, F 45.02-03
  (reconciliación MPM bancaria) — granularidad bancario-específica, no cambia ninguna
  decisión de diseño de este proyecto.
- Instrucciones `.docx` (Anexo V) — no leídas por ser un archivo binario no accesible
  directamente con las herramientas de este entorno; la hoja F 02.00 ya trae las citas
  de párrafo necesarias inline, que es la información de mayor valor que aportaban las
  instrucciones.
- `Annex 1` (informe final) y las versiones `_TC` (con control de cambios) — no
  aportarían información normativa adicional a la ya extraída de la plantilla F 02.00 y
  el Opinion; se pueden revisar si en el futuro se requiere el detalle de por qué se
  descartó una alternativa de diseño de plantilla (proceso de consulta), pero eso es
  historia del proceso EBA, no un criterio a implementar.

## Verificación

- `PRD.md` §11.2 nuevo, changelog v3.5.
- `FUENTES_Y_BIBLIOGRAFIA.md`: 2 filas nuevas (Opinion EBA, plantilla FINREP F 02.00).
- `sala_clasificacion/_service.py`: regla de método de participación aplicada (ver
  `tasks/excepcion_metodo_participacion_pendiente.md`).
- `python -m pytest tests/` — 39/39 en verde.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
