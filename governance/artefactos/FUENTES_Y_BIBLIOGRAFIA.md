# Mapa de Fuentes, Linaje Epistémico y Bibliografía

**Proyecto:** NIIF 18

> **SSOT DE ANCLAJE EPISTÉMICO (PROHIBIDA LA MEMORIA PARAMÉTRICA CIEGA):**
> Toda función de negocio debe estar anclada a los tratados y especificaciones oficiales registradas en esta tabla.

## Estatus de purga (2026-09-22)

Este archivo tenía 1996 líneas (282 KB) copiadas de otro proyecto, según confirmó el
propietario del repositorio — el mismo patrón ya detectado y purgado en
`APORTES_INEDITOS.md`. Se auditó el contenido completo:

- Casi todas las citas sustentaban "teoremas" del framework ZERAG en abstracto (testing
  E2E, ACID, sockets TCP, sistemas operativos) y referenciaban rutas de otro repositorio
  (`docs/artefactos/`, `governance/dominio/`, `governance/contratos/`,
  `governance/protocolos/`, `instalador_cliente/`) que no existen en este proyecto.
- Dos citas sí eran aplicables a NIIF 18 y se rescataron abajo: la norma oficial IASB y el
  tratado fundacional de la partida doble (relevante para la validación de balanza
  cuadrada, RF-01).

El resto se purgó. Esta tabla queda como la fuente única de verdad real del proyecto —
ver `governance/artefactos/PRD.md` §8 (riesgo normativo) y `TASKS.md`, que dependían de que este archivo tuviera contenido genuino.

## Fuentes normativas y técnicas

### IASB / IFRS Foundation — IFRS 18 — Presentation and Disclosure in Financial…

- **Organización / Plataforma:** IASB / IFRS Foundation
- **Especificación oficial / Documento:** *IFRS 18 — Presentation and Disclosure in Financial Statements* (2024)
- **URL / Referencia:** https://www.ifrs.org/issued-standards/list-of-standards/ifrs-18-presentation-and-disclosure-in-financial-statements/
- **Aplica a:** Norma raíz del proyecto (RF-02 a RF-08). El texto completo con notas técnicas requiere suscripción paga de IFRS.org — **sigue pendiente** (`TASKS.md`) validar `PRD.md` §3 y `biblioteca_doctrinal/` línea por línea contra él.

### IASB / IFRS Foundation — IFRS 18 Presentation and Disclosure in Financial…

- **Organización / Plataforma:** IASB / IFRS Foundation
- **Especificación oficial / Documento:** *IFRS 18 Presentation and Disclosure in Financial Statements — Project Summary* (abril 2024) — documento gratuito preparado por el staff del IASB, sin muro de pago
- **URL / Referencia:** https://www.ifrs.org/content/dam/ifrs/project/primary-financial-statements/ifrs-standard/projectsummary-ifrs18-april2024.pdf
- **Aplica a:** **Usado para validar `PRD.md` §3 (2026-09-22, v3.2)**: confirmó las categorías Operación/Inversión/Financiación/Impuestos/Discontinuadas (p. 5-8) y corrigió el tratamiento de dividendos pagados (no son partida del Estado de Resultados — se reconocen en el Estado de Cambios en el Patrimonio) y la regla de intereses (gasto→Financiación siempre, ingreso→Inversión por defecto). No sustituye al estándar completo: es un resumen de conveniencia, "no debe considerarse autoritativo" (nota de la propia IFRS Foundation en el documento).

### ESMA (European Securities and Markets… — Public Statement — Reshaping performance:…

- **Organización / Plataforma:** ESMA (European Securities and Markets Authority)
- **Especificación oficial / Documento:** *Public Statement — Reshaping performance: Implementation of IFRS 18 Presentation and Disclosure in Financial Statements* (17 de febrero de 2026, ESMA32-193237008-9180) — documento público gratuito de una autoridad de la Unión Europea
- **URL / Referencia:** https://www.esma.europa.eu/sites/default/files/2026-02/ESMA32-193237008-9180_Public_Statement_IFRS_18.pdf
- **Aplica a:** **Usado para validar `PRD.md` §3 (2026-09-22, v3.3)**: confirma que IFRS 18 aplica en la UE (vigencia 1-ene-2027, aplicación anticipada permitida) y corrige el paso 5 del árbol — el interés de arrendamientos y pensiones no se reclasifica a Operación por la excepción de actividad principal, ni siquiera para un banco (sección II.a). Documenta también "excepciones finas" fuera del alcance del MVP: moneda extranjera, derivados de cobertura, contraprestación contingente, provisiones de largo plazo — ver `PRD.md` §3 y `TASKS.md`. Aclara que la evaluación de "actividad principal" debe ser a nivel de entidad reportante y basada en evidencia, no una simple aserción.

### IFRS-Converter (GitHub,… — Repositorio (código + README), sin licencia declarada…

- **Organización / Plataforma:** IFRS-Converter (GitHub, `joshuacoffeetumblr`)
- **Especificación oficial / Documento:** Repositorio (código + README), sin licencia declarada (`license: null` en la API de GitHub; HTTP 404 en `LICENSE`/`LICENSE.md`) — creado 2026-09-19, 0 estrellas/forks
- **URL / Referencia:** https://github.com/joshuacoffeetumblr/IFRS-Converter
- **Aplica a:** **Auditado 2026-09-22 (`PRD.md` §9.1-9.2)**: referencia arquitectónica únicamente — **no se copió código, por no tener licencia** (repositorio público sin licencia = todos los derechos reservados por defecto, ToS de GitHub §D.5). Valida el patrón reglas-deterministas + confirmación humana + bitácora append-only ya adoptado aquí, y aportó un hallazgo (método de participación sin excepción de actividad principal) que en su momento quedó sin confirmar por venir de fuente secundaria — **confirmado el 2026-09-23 con fuente oficial**, ver fila EBA/FINREP abajo.

### EBA (European Banking Authority) — Opinion of the European Banking Authority on the…

- **Organización / Plataforma:** EBA (European Banking Authority)
- **Especificación oficial / Documento:** *Opinion of the European Banking Authority on the interim period between the IFRS 18 EU endorsement date and the ITS on FINREP application date* (EBA/Op/2026/07, 8 de julio de 2026, firmado François-Louis Michaud) — documento público gratuito de una autoridad de la Unión Europea
- **URL / Referencia:** `docs/Opinion Finrep IFRS 18 - interim period.pdf` (recibido del propietario)
- **Aplica a:** **Usado en `PRD.md` §11.4 (2026-09-23)**: confirma que IFRS 18 **fue endosado** en la UE mediante el Reglamento de Ejecución (UE) 2026/338 de la Comisión Europea (13-feb-2026), vigente para períodos desde 1-ene-2027 — actualiza el estado "aún no endosado" registrado en §11.1 (correcto a oct-2025, la fecha de esa fuente). Describe la revisión de las plantillas FINREP (F 02.00, F 16.01-07, F 20.03, F 45.02-03) para alinearlas a IFRS 18, con período de transición hasta ~fin sept-2027.

### EBA (European Banking Authority) — FINREP Templates under IFRS 18 (Anexo III/IV,…

- **Organización / Plataforma:** EBA (European Banking Authority)
- **Especificación oficial / Documento:** *FINREP Templates under IFRS 18* (Anexo III/IV, plantilla "2 (post consultation)" = F 02.00, Estado de Resultados) — anexo técnico del Opinion EBA/Op/2026/07
- **URL / Referencia:** `docs/Annex 2 (Finrep templates IFRS 18- Annex III)_CV.xlsx` (recibido del propietario)
- **Aplica a:** **Usado en `PRD.md` §11.4 y `sala_clasificacion._service.clasificar_partida` (2026-09-23)**: primera fuente del proyecto con cita de párrafo exacto de IFRS 18 por línea de presentación (IFRS 18.69(a), .71, .75, .76(a)/(b), .118(e)/(f), IE13, Anexo V.Parte 2.54). **Confirma con fuente oficial** que el resultado por método de participación (fila 74) es línea propia de Inversión sin excepción de actividad principal — resuelve la pregunta pendiente. Adoptado solo como fuente de taxonomía/citas — es reporte supervisor bancario (EBA/FINREP), no un catálogo de líneas aplicable a una entidad no financiera genérica (público objetivo de este proyecto, `PRD.md` §1).

### ESMA (European Securities and Markets… — Statement — European common enforcement priorities for…

- **Organización / Plataforma:** ESMA (European Securities and Markets Authority)
- **Especificación oficial / Documento:** *Statement — European common enforcement priorities for 2025 corporate reporting* (14 de octubre de 2025, ESMA32-2064178921-9254) — documento público gratuito de una autoridad de la Unión Europea
- **URL / Referencia:** https://www.esma.europa.eu/sites/default/files/2025-10/ESMA32-2064178921-9254_Public_Statement_-_2025_European_Common_Enforcement_Priorities.pdf
- **Aplica a:** **Usado para corregir una imprecisión de un resumen de búsqueda aportado por el propietario (2026-09-22, PRD.md §11)**: confirma que IFRS 18 no era prioridad de cumplimiento 2025 de ESMA y que, según nota al pie de la propia ESMA, "although not yet endorsed" (aún no endosada) en la UE a esa fecha. Documenta también las modificaciones a IFRS 9/7 vigentes desde 1-ene-2026 (contratos de electricidad/PPAs, liquidación electrónica de pasivos, activos financieros con cláusulas ESG) y el estado de la taxonomía dual ESEF (IAS 1 / IFRS 18) — ninguna implementada en este proyecto, quedan como contexto regulatorio, no como RF.

### Superintendencia de Compañías, Valores… — Directorio de Compañías — descarga pública directa,…

- **Organización / Plataforma:** Superintendencia de Compañías, Valores y Seguros (SCVS)
- **Especificación oficial / Documento:** Directorio de Compañías — descarga pública directa, actualizada por la SCVS con fecha del propio día (verificado 2026-09-24), sin sesión ni autenticación, sin restricción en `robots.txt`. Tabla en pantalla verificada como **no filtrable por RUC** (solo 9 de 24 columnas tienen filtro habilitado por la propia SCVS) — no existe consulta puntual por RUC en este sitio.
- **URL / Referencia:** https://mercadodevalores.supercias.gob.ec/reportes/excel/directorio_companias.xlsx (página del reporte: https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf)
- **Aplica a:** RF-11 (Fase 4, v3.9, ya no es el flujo por defecto desde v3.10): `sala_entidad.actualizar_snapshot_directorio`/`cargar_directorio`/`buscar_entidad_por_ruc` se conservan como ruta alterna para resolver el código CIIU exacto (no inferido) — es el mismo archivo del botón "Descargar en formato Excel" de la página oficial, sin scrapear ninguna interfaz de búsqueda.

### Servicio de Rentas Internas (SRI,… — Consulta pública de RUC (Consolidado Contribuyente) —…

- **Organización / Plataforma:** Servicio de Rentas Internas (SRI, Ecuador)
- **Especificación oficial / Documento:** Consulta pública de RUC (Consolidado Contribuyente) — endpoint REST sin sesión ni autenticación, verificado 2026-09-24 con 3 RUCs reales de distinto sector (respuesta < 1s)
- **URL / Referencia:** https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc?&ruc={RUC}
- **Aplica a:** RF-11 (v3.10, fuente de datos por defecto): `sala_entidad.buscar_entidad_ruc_sri` — consulta en vivo por RUC, sin descargar ningún archivo masivo. Devuelve razón social, estado y actividad económica en texto libre (sin código CIIU) — el código CIIU se infiere por coincidencia de texto contra el catálogo local (`sala_entidad.inferir_ciiu_por_texto`), nunca se lee directamente de esta fuente.

### Instituto Nacional de Estadística y… — Clasificador Nacional de Actividades Económicas — CIIU…

- **Organización / Plataforma:** Instituto Nacional de Estadística y Censos (INEC, Ecuador)
- **Especificación oficial / Documento:** Clasificador Nacional de Actividades Económicas — CIIU (snapshot local: `data/ciiu.xlsx`)
- **URL / Referencia:** https://www.ecuadorencifras.gob.ec/
- **Aplica a:** RF-11: catálogo jerárquico de actividad económica. **Pendiente**: confirmar la URL exacta del clasificador vigente antes de citar una versión específica.

### Python Software Foundation — Documentación oficial de Python 3

- **Organización / Plataforma:** Python Software Foundation
- **Especificación oficial / Documento:** Documentación oficial de Python 3
- **URL / Referencia:** https://docs.python.org/3/
- **Aplica a:** Stack técnico del proyecto (`src/`, `requirements.txt`).

### Streamlit Inc. — Documentación oficial de Streamlit

- **Organización / Plataforma:** Streamlit Inc.
- **Especificación oficial / Documento:** Documentación oficial de Streamlit
- **URL / Referencia:** https://docs.streamlit.io/
- **Aplica a:** Framework de frontend (`src/app.py`, `.streamlit/config.toml`).

### pandas / NumFOCUS — Documentación oficial de pandas

- **Organización / Plataforma:** pandas / NumFOCUS
- **Especificación oficial / Documento:** Documentación oficial de pandas
- **URL / Referencia:** https://pandas.pydata.org/docs/
- **Aplica a:** Manipulación de balanzas contables (`clean_numeric_series`, `infer_columns_by_mathematical_weights`).

### OpenPyXL — Documentación oficial de OpenPyXL

- **Organización / Plataforma:** OpenPyXL
- **Especificación oficial / Documento:** Documentación oficial de OpenPyXL
- **URL / Referencia:** https://openpyxl.readthedocs.io/
- **Aplica a:** Lectura de balanzas Excel y generación del Estado de Resultados exportado.


---

## Bibliografía de aportes inéditos (`APORTES_INEDITOS.md`)

Tabla separada de la anterior a propósito: las filas de arriba son fuentes normativas y
de stack técnico ancladas a una capacidad de dominio;
las de abajo son citas académicas/técnicas que respaldan el *patrón de ingeniería*
detrás de un aporte inédito (`A-0N`), no una regla de negocio NIIF 18 — mezclarlas
perdería esa distinción. Generada según el criterio de la skill `aportes-ineditos`
(2026-09-24): una fila por fuente real y verificada, deduplicada, nunca una cita
fabricada solo porque el título suena relacionado.

### Rahm, E. & Bernstein, P. A. (2001) — A survey of approaches to automatic schema…

- **Autor(es):** Rahm, E. & Bernstein, P. A.
- **Año:** 2001
- **Título:** *A survey of approaches to automatic schema matching*
- **Fuente / Editorial:** The VLDB Journal, 10(4), 334–350
- **Aporte que respalda:** A-01
- **Nota:** Encuadra el problema general de schema matching sin metadatos confiables que `infer_columns_by_mathematical_weights` resuelve de forma acotada.

### Shannon, C. E. (1948) — A Mathematical Theory of Communication

- **Autor(es):** Shannon, C. E.
- **Año:** 1948
- **Título:** *A Mathematical Theory of Communication*
- **Fuente / Editorial:** Bell System Technical Journal, 27, 379–423
- **Aporte que respalda:** A-01
- **Nota:** Fundamento de usar dispersión/entropía de caracteres como señal discriminante entre texto libre y código estructurado.

### Amodei, D., Olah, C., Steinhardt,… (2016) — Concrete Problems in AI Safety

- **Autor(es):** Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J. & Mané, D.
- **Año:** 2016
- **Título:** *Concrete Problems in AI Safety*
- **Fuente / Editorial:** arXiv:1606.06565
- **Aporte que respalda:** A-02
- **Nota:** Problema de "supervisión escalable" — un sistema no debe ser autoridad final en decisiones costosas de revertir sin verificación humana explícita.

### Shneiderman, B. (2020) — Human-Centered AI: Reliable, Safe &…

- **Autor(es):** Shneiderman, B.
- **Año:** 2020
- **Título:** *Human-Centered AI: Reliable, Safe & Trustworthy*
- **Fuente / Editorial:** International Journal of Human–Computer Interaction, 36(6), 495–504
- **Aporte que respalda:** A-02
- **Nota:** Diseño de sistemas con control humano efectivo (no solo un botón de aprobar) sobre recomendaciones automatizadas.

### Fowler, M. (2004) — StranglerFigApplication

- **Autor(es):** Fowler, M.
- **Año:** 2004
- **Título:** *StranglerFigApplication*
- **Fuente / Editorial:** martinfowler.com (bliki)
- **Aporte que respalda:** A-03
- **Nota:** Nombra y describe el patrón de migración incremental que el proyecto ya declaraba en código antes de ejecutarlo.

### Cunningham, W. (1992) — The WyCash Portfolio Management System

- **Autor(es):** Cunningham, W.
- **Año:** 1992
- **Título:** *The WyCash Portfolio Management System*
- **Fuente / Editorial:** OOPSLA Experience Report
- **Aporte que respalda:** A-03
- **Nota:** Origen del concepto de deuda técnica como pasivo visible y cuantificable — por qué vale la pena registrar una migración a medias en vez de ocultarla.

### Parnas, D. L. (1972) — On the Criteria to Be Used in Decomposing…

- **Autor(es):** Parnas, D. L.
- **Año:** 1972
- **Título:** *On the Criteria to Be Used in Decomposing Systems into Modules*
- **Fuente / Editorial:** Communications of the ACM, 15(12), 1053–1058
- **Aporte que respalda:** A-04
- **Nota:** Ocultamiento de información: cada módulo (aquí, cada tarea) debe ser una unidad independiente con interfaz propia, no un fragmento indistinguible dentro de una unidad mayor.

### Reiter, R. (1980) — A Logic for Default Reasoning

- **Autor(es):** Reiter, R.
- **Año:** 1980
- **Título:** *A Logic for Default Reasoning*
- **Fuente / Editorial:** Artificial Intelligence, 13(1–2), 81–132
- **Aporte que respalda:** A-05
- **Nota:** Formaliza reglas por defecto y excepciones: una excepción bien formada no debe reemplazar una conclusión ya alcanzada por una regla más específica y confiable.

### Pollock, J. L. (1987) — Defeasible Reasoning

- **Autor(es):** Pollock, J. L.
- **Año:** 1987
- **Título:** *Defeasible Reasoning*
- **Fuente / Editorial:** Cognitive Science, 11(4), 481–518
- **Aporte que respalda:** A-05
- **Nota:** Distingue derrotadores "rebutting" de "undercutting" — el bug de los $690,000 fue un derrotador mal calibrado actuando como "rebutting" sobre una conclusión que no debía tocar.

### Beck, K. (2000) — Extreme Programming Explained: Embrace Change

- **Autor(es):** Beck, K.
- **Año:** 2000
- **Título:** *Extreme Programming Explained: Embrace Change*
- **Fuente / Editorial:** Addison-Wesley
- **Aporte que respalda:** A-06
- **Nota:** Origen del concepto de "spike solution" — investigación técnica acotada para resolver una incertidumbre concreta antes de comprometerse con un diseño.

### Postel, J. (1980) — DoD Standard Transmission Control Protocol

- **Autor(es):** Postel, J.
- **Año:** 1980
- **Título:** *DoD Standard Transmission Control Protocol*
- **Fuente / Editorial:** RFC 761
- **Aporte que respalda:** A-06
- **Nota:** Citado en sentido complementario: ser liberal al consumir una fuente externa no exime de ser estricto al verificar qué capacidades esa fuente realmente expone.

### Streamlit Inc. (—) — Session State: Widget behavior

- **Autor(es):** Streamlit Inc.
- **Año:** —
- **Título:** *Session State: Widget behavior*
- **Fuente / Editorial:** docs.streamlit.io
- **Aporte que respalda:** A-07
- **Nota:** Documentación oficial que especifica la precedencia de `session_state` sobre `value=` en corridas posteriores a la primera — ya registrada como fuente de stack en la tabla de arriba, referenciada aquí, no duplicada.

### Pacioli, L. (1494) — Summa de Arithmetica, Geometria, Proportioni…

- **Autor(es):** Pacioli, L.
- **Año:** 1494
- **Título:** *Summa de Arithmetica, Geometria, Proportioni et Proportionalita*
- **Fuente / Editorial:** Venecia
- **Aporte que respalda:** A-08
- **Nota:** Origen documentado del método de partida doble y la convención débito/crédito — fundamento de por qué sumar una cuenta contra-activo con `abs()` rompe la semántica contable en vez de solo el redondeo.

### Chen, T. Y., Cheung, S. C. & Yiu,… (1998) — Metamorphic Testing: A New Approach for…

- **Autor(es):** Chen, T. Y., Cheung, S. C. & Yiu, S. M.
- **Año:** 1998
- **Título:** *Metamorphic Testing: A New Approach for Generating Next Test Cases*
- **Fuente / Editorial:** Technical Report HKUST-CS98-01, Hong Kong University of Science and Technology
- **Aporte que respalda:** A-09
- **Nota:** Formaliza verificar una relación conocida entre entradas/salidas relacionadas (aquí, la identidad contable de cierre NIC 7.10) en vez de un oráculo de valores individuales — la relación misma es el oráculo.


---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
