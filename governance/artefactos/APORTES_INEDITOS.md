# Aportes Inéditos — Purgado
## **Proyecto:** NIIF 18

## Estatus

**Revisión (2026-09-22):** se auditó el contenido completo en busca de algo aplicable al
dominio NIIF 18 (contabilidad, clasificación de partidas, estados financieros). Casi todo
el archivo:
- referenciaba rutas de código inexistentes en este repositorio (`features/ip/`,
  `features/identificador_unico_simple/`, etc.), propias de otro proyecto;
- trataba temas ajenos a este proyecto: facturación electrónica SRI, scraping con
  Playwright de portales gubernamentales, el sistema interno de créditos del propio
  servidor MCP, pruebas E2E de dashboards, etc.

**Único hallazgo aprovechable — Teorema 99 (Inferencia Probabilística de Columnas
Contables):** describía, en la práctica, el mismo heurístico ya implementado en
`infer_columns_by_mathematical_weights` (`src/app.py`): inferir qué columna de una balanza
sin cabeceras estandarizadas es código, descripción o saldo, a partir de la forma de los
datos (proporción numérica, longitud léxica, patrón de código) en vez de depender del
nombre de la cabecera — relevante porque la app debe aceptar balanzas de distintos ERPs
(ver `balance_prueba_niif18_sap_business_one.xlsx` en la raíz del repo). Esa idea se dejó
como comentario breve directamente sobre la función en `src/app.py`, sin la aparatosidad
matemática del "teorema" original (que no aporta rigor real: es una heurística, no una
prueba). El resto del contenido se purgó.

Ver `governance/artefactos/VPA_MAP.md` para la nota de compilación del grafo estigmérgico
que originó esta revisión (`mcp_compile_stigmergy_graph`).

---

## Aportes inéditos válidos de esta sesión (2026-09-22)

Criterio de admisión (a pedido explícito del propietario): útil para este proyecto,
válido, verificable en el código/artefactos existentes, no refutado por literatura
posterior, y que no estuviera ya registrado en disco. Sin "demostraciones matemáticas"
de heurísticas — eso fue precisamente el defecto del contenido purgado. Cada entrada
es un patrón aplicado, con su soporte bibliográfico real y su verificación concreta.

### A-01. Inferencia de rol de columna por densidad de forma, no por nombre de cabecera

**Descripción:** `infer_columns_by_mathematical_weights` (`src/app.py`) decide si una
columna de una balanza importada es código, descripción o saldo a partir de la *forma*
de sus valores (proporción de celdas numéricas, patrón tipo-código, longitud léxica,
dispersión de espacios) en vez de buscar nombres de cabecera conocidos. Esto es una
instancia ligera y basada en heurísticas del problema de *schema matching* automático:
generaliza entre balanzas exportadas de ERPs distintos (SAP B1, Softland, QuickBooks…)
que nombran sus columnas de forma inconsistente, sin mantener un diccionario de alias.

**Por qué es útil aquí:** el repo ya incluye `balance_prueba_niif18_sap_business_one.xlsx`
como caso de prueba real con cabeceras no estandarizadas — el problema no es hipotético.

**Verificabilidad:** el código existe, corre y fue ejercitado en esta sesión con
`streamlit.testing.v1.AppTest` sobre `data/balanza_ejemplo_niif18.csv` sin excepciones.
No es una prueba matemática — es una heurística observable y falsable: puede fallar ante
balanzas atípicas, y su tasa de acierto solo se conoce empíricamente (no hay `ε → 0`
garantizado, a diferencia de lo que afirmaba el "Teorema 99" purgado).

**Soporte bibliográfico:**
- Rahm, E., & Bernstein, P. A. (2001). *A survey of approaches to automatic schema
  matching*. The VLDB Journal, 10(4), 334–350. — encuadra el problema general
  (schema matching sin metadatos confiables) que esta función resuelve de forma acotada.
- Shannon, C. E. (1948). *A Mathematical Theory of Communication*. Bell System Technical
  Journal, 27, pp. 379–423. — fundamento de usar dispersión/entropía de caracteres como
  señal discriminante entre texto libre (descripción) y código estructurado.

**Estado:** ya implementado; sin token nuevo en `VPA_MAP.md` (documenta código existente,
no introduce una sala o concepto de dominio nuevo — ver nota de compilación arriba).

### A-02. Sugerencia algorítmica con confirmación humana obligatoria antes de alimentar una decisión regulatoria

**Descripción:** en `PRD.md` v3.1 (RF-11), el código CIIU de una entidad puede *sugerir*
si financiación o inversión es su actividad principal (`ConfiguracionEntidad`), pero esa
sugerencia queda marcada `origen_actividad_principal = "sugerido_ciiu"` y el sistema
**bloquea** la clasificación masiva (RF-03) hasta que el usuario la confirme o corrija
explícitamente. El patrón: un algoritmo puede acelerar una decisión de cumplimiento
normativo, pero no puede ser la autoridad final — la responsabilidad profesional se
preserva como invariante, no como fricción de UI incidental.

**Por qué es útil aquí:** NIIF 18 exige juicio profesional explícito para clasificar
partidas de financiación/inversión (`PRD.md` §3, nota de implementación); un sistema que
aplicara la sugerencia CIIU sin confirmación estaría tomando esa decisión por el
preparador contable, lo cual es tanto un riesgo de auditoría como, potencialmente, un
sistema de "alto riesgo" bajo marcos regulatorios de IA que exigen supervisión humana
efectiva (no solo nominal) sobre decisiones automatizadas con impacto normativo.

**Verificabilidad:** es una regla de diseño registrada en `PRD.md` (RF-11) y en el
backlog de `TASKS.md` ; se verifica por inspección
del PRD y, cuando `sala_entidad` se implemente, por un test que confirme que RF-03 se
bloquea con `origen_actividad_principal = "sugerido_ciiu"` sin confirmar.

**Soporte bibliográfico:**
- Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016).
  *Concrete Problems in AI Safety*. arXiv:1606.06565. — el problema de "supervisión
  escalable" (scalable oversight): un sistema no debe actuar como autoridad final en
  decisiones costosas de revertir sin verificación humana explícita.
- Shneiderman, B. (2020). *Human-Centered AI: Reliable, Safe & Trustworthy*. International
  Journal of Human–Computer Interaction, 36(6), 495–504. — diseño de sistemas con control
  humano efectivo (no solo un botón de aprobar) sobre recomendaciones automatizadas.

**Estado:** ya registrado como token de dominio en `VPA_MAP.md`;
esta entrada documenta el *patrón* detrás de esa fila, no introduce un token nuevo.

### A-03. Imports declarados-pero-no-usados como marcador legible de una migración "Strangler Fig" incompleta

**Descripción:** `src/app.py` importa las 7 compuertas `_service.py` de las salas ADPA
bajo el comentario ` ZERAG BIOS Clean-Room Pattern` — pero,
hasta esta sesión, ninguna se usaba: toda la lógica seguía en el monolito. Ese import
"muerto" no era un descuido: es una señal legible por máquina de que la migración del
monolito hacia salas independientes (patrón *Strangler Fig*: el sistema nuevo crece
alrededor del viejo hasta reemplazarlo) fue anunciada en el código pero no ejecutada.
Detectar esto no requirió herramientas especiales: `grep` de imports sin uso correspondiente
en el cuerpo del archivo, cruzado con el tamaño de cada `_service.py` (5 líneas, vacíos)
fue suficiente para confirmar el diagnóstico que después quedó en `PRD.md` §10.

**Por qué es útil aquí:** convierte una intuición ("esto parece a medio migrar") en un
chequeo mecánico y repetible: contar líneas por `_service.py` y verificar si el símbolo
importado se invoca en `app.py`. Ya se usó para escribir el backlog de .

**Verificabilidad:** reproducible con `wc -l src/*/_service.py` y una búsqueda de cada
alias importado (`imp_svc`, `cat_svc`, etc.) en el cuerpo de `app.py` — exactamente lo que
se hizo en esta sesión para fundamentar `PRD.md` §10.

**Soporte bibliográfico:**
- Fowler, M. (2004). *StranglerFigApplication*. martinfowler.com (bliki). — nombra y
  describe el patrón de migración incremental que este proyecto ya había empezado a
  declarar en código antes de ejecutarlo.
- Cunningham, W. (1992). *The WyCash Portfolio Management System*. OOPSLA Experience
  Report. — origen del concepto de "deuda técnica" como pasivo visible y cuantificable,
  aplicable a por qué vale la pena registrar (no ocultar) una migración a medias.

**Estado:** sin token nuevo — es un método de auditoría, no un concepto de dominio;
su resultado ya está capturado en `PRD.md` §10 y en `TASKS.md` .

### A-04. Un artefacto de gobernanza multi-entidad en un solo archivo es invisible para herramientas de indexación por archivo

**Descripción:** el propietario detectó que `TASKS.md` no podía recibir rastros
estigmérgicos individuales por tarea (`mcp_inject_stigmergic_trace`). Antes de corregir,
se verificó la causa raíz con `mcp_compile_stigmergy_graph`: de ~27 tareas escritas como
texto en negrita dentro de una única lista plana en un solo archivo, el grafo solo
detectaba **2** como nodos — y solo por coincidencia, porque esos 2 tokens también
aparecían citados dentro de comentarios de código Python (que el compilador sí escanea
vía AST, a diferencia del Markdown, donde solo lee un token por archivo desde el
encabezado). El patrón general: cuando una herramienta de indexación opera a
granularidad de **archivo** (un token/entidad esperado por documento — el mismo patrón
que ya usan `PRD.md`, `INVARIANTS.md`, `VPA_MAP.md`, `FUENTES_Y_BIBLIOGRAFIA.md`, cada
uno con su propio encabezado raíz), meter *varias* entidades lógicas independientes
dentro de un solo archivo las vuelve invisibles para esa herramienta, sin importar cuán
bien etiquetadas estén internamente con negrita o viñetas — la unidad de indexación no
es el token, es el archivo.

**Corrección aplicada:** se dividió `TASKS.md` en `governance/artefactos/tasks/<token>.md`
— un archivo por tarea, cada uno con su propio encabezado H1 , igual patrón
que el resto de artefactos vivos. `TASKS.md` pasó a ser un índice (tabla con estado,
token, resumen y enlace), no el contenedor del contenido.

**Por qué es útil aquí:** no es un capricho estético — es la diferencia entre que una
tarea pueda o no participar del grafo de trazabilidad que el propio proyecto declara
como su mecanismo de gobernanza ( en `AGENTS.md`). Un artefacto de
gobernanza que no puede ser indexado por su propia herramienta de gobernanza es, en la
práctica, invisible para ella.

**Verificabilidad:** reproducible ejecutando `mcp_compile_stigmergy_graph` antes (10
intents totales, de los cuales solo 2 eran tareas) y después de la migración (36 intents,
28 de ellos tareas — una por archivo nuevo) en esta misma sesión.

**Soporte bibliográfico:**
- Parnas, D. L. (1972). *On the Criteria to Be Used in Decomposing Systems into
  Modules*. Communications of the ACM, 15(12), 1053–1058. — principio de descomposición
  por ocultamiento de información: cada módulo (aquí, cada tarea) debe ser una unidad
  independiente con una interfaz propia (aquí, un archivo con su propio token), no un
  fragmento indistinguible dentro de una unidad mayor.
- Se decidió no citar aquí ningún principio de "granularidad de indexación" en
  recuperación de información porque no se verificó una fuente específica y aplicable —
  mejor omitir la cita que forzar una que no se comprobó (mismo criterio de admisión que
  A-01/A-02/A-03).

**Estado:** aplicado — ver `governance/artefactos/tasks/corregir_logica_inyeccion_rastros_tasks.md`
y `TASKS.md`. Sin token de dominio nuevo (es un método de gobernanza documental, no un
concepto del negocio NIIF 18).

---

## Aportes inéditos válidos — sesión 2026-09-23/24

Mismo criterio de admisión que arriba: útil para este proyecto, válido, verificable en
el código/artefactos existentes, no refutado por literatura posterior, y que no
estuviera ya registrado en disco como patrón generalizable (aunque su resultado
puntual sí conste en `PRD.md`/`TASKS.md`/tests — lo nuevo aquí es el patrón detrás).

### A-05. En una excepción de rescate para un falso positivo, la señal fuerte que ya decidió correctamente nunca debe ser revertida por la señal débil que motivó el rescate

**Descripción:** `sala_clasificacion.clasificar_partida` (Paso 0) tenía dos señales
independientes para excluir una partida de balance del Estado de Resultados: el código
de cuenta (señal **fuerte** — en un plan de cuentas estándar, el prefijo 1/2/3 es
inequívoco) y una palabra de la descripción (señal **débil** — "pasivo" puede aparecer
tanto en una cuenta de balance real como en el nombre de un gasto, ej. "interés neto de
pasivo por beneficios definidos"). Para corregir los falsos positivos que la señal débil
producía sobre gastos reales, se había agregado un rescate por palabra clave
(`_PALABRAS_MOVIMIENTO_PL`). El bug (verificado con datos reales, `TB_ERP` del archivo
de prueba, $690,000 de brecha): ese mismo rescate se aplicaba también cuando el
disparador había sido la señal *fuerte*, revirtiendo correctamente clasificaciones de
balance genuinas ("Depreciación acumulada edificios", "Provisión por litigios" — cuentas
1.x/2.x cuyo nombre usa vocabulario de flujo por convención contable). La corrección: el
rescate solo puede anular una decisión tomada por la señal débil que lo motivó — nunca
una decisión ya tomada por la señal fuerte. El patrón generaliza: en cualquier árbol de
reglas con una regla por defecto y una excepción diseñada para corregir *esa* regla, la
excepción no debe poder revertir una decisión que vino de una regla distinta y más
confiable, aunque ambas hayan concluido en el mismo destino aparente.

**Por qué es útil aquí:** es exactamente el mismo tipo de error, en la misma sala, que
ya se había corregido una vez antes (la excepción de actividad principal indebidamente
aplicada al interés de arrendamientos/pensiones, v3.3, y luego al método de
participación, v3.5) — son 3 instancias del mismo patrón de fondo (una excepción de
rescate demasiado amplia) encontradas y corregidas por separado en 3 sesiones distintas.
Nombrar el patrón explícitamente sirve para revisar el resto del árbol §3 buscando la
misma forma de error antes de que aparezca una cuarta vez.

**Verificabilidad:** reproducible con
`tests/test_sala_clasificacion.py::test_deterioro_acumulado_es_cuenta_de_balance_no_movimiento_pl`
(y los 2 tests hermanos) y con el test de integración
`tests/test_sala_importacion_hojas_reales.py::test_motor_completo_sobre_tb_erp_reproduce_er_niif18_esperado`,
que fija los 3 subtotales exactos de `ER_NIIF18` tras la corrección.

**Soporte bibliográfico:**
- Reiter, R. (1980). *A Logic for Default Reasoning*. Artificial Intelligence, 13(1–2),
  81–132. — formaliza el razonamiento con reglas por defecto y excepciones; una
  excepción bien formada solo debe activarse en ausencia de información más específica
  y confiable, no reemplazar una conclusión ya alcanzada por una regla de mayor
  especificidad.
- Pollock, J. L. (1987). *Defeasible Reasoning*. Cognitive Science, 11(4), 481–518. —
  distingue derrotadores "rebutting" (contradicen la conclusión) de "undercutting"
  (invalidan la razón que llevó a ella); el bug corregido es un caso de un derrotador mal
  calibrado que actuaba como "rebutting" sobre una conclusión que no debía poder tocar.

**Estado:** ya corregido en código (`sala_clasificacion/_service.py`, Paso 0); esta
entrada documenta el patrón general detrás del fix, no introduce un token nuevo.

### A-06: Verificar la capacidad real de una fuente de datos en vivo por introspección del mecanismo subyacente, no por lo que la interfaz visible sugiere

**Descripción:** antes de integrar una fuente pública externa (el directorio de
compañías de la SCVS), se investigó si permitía búsqueda por RUC ejecutando JavaScript
directamente en la página para inspeccionar el DOM y las peticiones AJAX reales de su
tabla `PrimeFaces`/JSF — no solo observando qué campos de filtro se veían en pantalla.
El resultado invalidó una asunción razonable pero incorrecta: de 24 columnas, solo 9
tenían filtro habilitado por el propio sitio, y RUC no era una de ellas — ni en la UI
visible ni en el mecanismo de filtrado subyacente que la sostiene. Esa verificación
evitó construir una integración basada en una capacidad que no existía (scraping de una
búsqueda por RUC inexistente) y motivó buscar una fuente alterna (la API pública del
SRI) que sí la tenía — verificada con el mismo criterio: una petición HTTP real, no la
documentación ni la apariencia del sitio.

**Por qué es útil aquí:** el proyecto ya integra 2 fuentes públicas externas (SCVS, SRI)
fuera de su control, y probablemente integrará más (,
dependen de fuentes UE). El patrón "verificar la capacidad real antes de diseñar la
integración" ya evitó una implementación equivocada una vez en esta sesión (se estuvo a
punto de invertir esfuerzo en automatizar una búsqueda por RUC contra la SCVS antes de
confirmar que no existía) y debería aplicarse por defecto a la próxima fuente externa
que se integre.

**Verificabilidad:** reproducible ejecutando el mismo script de inspección
(`document.querySelectorAll('th[role=columnheader]')` cruzado con los inputs de filtro
del DOM) contra `https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf`
— documentado con su resultado exacto en
`governance/artefactos/tasks/consulta_sri_ruc_en_vivo.md`.

**Soporte bibliográfico:**
- Beck, K. (2000). *Extreme Programming Explained: Embrace Change*. Addison-Wesley. —
  origen del concepto de "spike solution": una investigación técnica acotada y
  desechable para resolver una incertidumbre concreta *antes* de comprometerse con un
  diseño, en vez de asumir una capacidad y descubrir su ausencia a mitad de la
  implementación.
- Postel, J. (1980). *DoD Standard Transmission Control Protocol*, RFC 761 (origen de
  "be liberal in what you accept" / principio de robustez) — citado aquí en sentido
  inverso y complementario: ser liberal al *consumir* una fuente externa no exime de ser
  estricto al *verificar* qué capacidades esa fuente realmente expone antes de depender
  de ellas.

**Estado:** aplicado — ver `governance/artefactos/tasks/consulta_sri_ruc_en_vivo.md`. Sin
token de dominio nuevo (es un método de verificación, no un concepto del negocio NIIF 18).

### A-07: El valor por defecto de un widget con estado persistente solo se respeta en su primer renderizado — un identificador dinámico es la corrección de causa raíz, no releer el estado

**Descripción:** en `app.py`, los checkboxes de actividad principal no se pre-marcaban
con la sugerencia calculada (verificada correcta por separado) tras buscar un nuevo RUC.
Causa raíz: en Streamlit, el parámetro `value=` de un widget con `key` fija solo se
aplica la primera vez que esa `key` se renderiza; en cada corrida posterior, el valor
mostrado proviene de `st.session_state[key]`, sin importar qué `value=` se pase — un
comportamiento de precedencia de estado, no un bug del framework. Como la `key` era fija
(`"chk_fin_principal"`), el checkbox quedaba congelado en el valor de su primer render
(antes de cualquier búsqueda) para el resto de la sesión. La corrección de causa raíz —
no un parche como vaciar manualmente `session_state` en cada búsqueda — fue atar la
`key` al dato que determina el valor por defecto (`f"chk_fin_principal_{ruc_buscado}"`):
cada RUC nuevo genera una `key` nueva, por lo que Streamlit la trata como un widget
recién nacido y sí respeta su `value=`.

**Por qué es útil aquí:** el mismo patrón de "`key` fija + valor por defecto que debería
cambiar con los datos" puede reaparecer en cualquier otro widget de la app que muestre
una sugerencia derivada de una búsqueda (ya ocurrió una vez con este mismo componente).
Nombrar la causa raíz explícitamente (precedencia de `session_state` sobre `value=`, no
"el checkbox no funciona") evita que se repita como un misterio a depurar cada vez.

**Verificabilidad:** reproducido y corregido en vivo en esta sesión (Streamlit corriendo
en el `venv` real del proyecto, navegador): antes del fix, `document.querySelectorAll
('input[type=checkbox]')[0].checked` devolvía `false` tras buscar el RUC del Banco
Pichincha (debería ser `true`, sección CIIU K); después del fix con `key` dinámica,
devuelve `true`. Documentado en `governance/artefactos/tasks/consulta_sri_ruc_en_vivo.md`.

**Soporte bibliográfico:**
- Streamlit Inc. — *Session State: Widget behavior* (docs.streamlit.io) — documentación
  oficial que especifica esta precedencia (`session_state` sobre `value`/`default` en
  reruns posteriores al primero); ya registrada como fuente oficial del stack técnico de
  este proyecto en `FUENTES_Y_BIBLIOGRAFIA.md`.

**Estado:** aplicado — ver `src/app.py` (checkboxes de la pestaña Entidad) y
`governance/artefactos/tasks/consulta_sri_ruc_en_vivo.md`. Sin token de dominio nuevo
(es un patrón de UI, no un concepto del negocio NIIF 18).

---

## Aportes inéditos válidos — sesión 2026-09-24/27

Mismo criterio de admisión que arriba, con el ajuste explícito ya incorporado a la
skill `aportes-ineditos`: la rigurosidad matemática (criterio 6) no es un filtro de
admisión — un gotcha empírico reproducible, sin causa formalizable más allá de "así
está implementada la herramienta", puede valer tanto como un invariante formal si evita
perder tiempo la próxima vez.

### A-08. Sumar cuentas contables por valor absoluto en vez de por signo neto anula el propósito de las cuentas contra-activo/contra-pasivo

**Descripción:** al construir `sala_situacion_financiera`, un primer intento sumó el
saldo de cada cuenta con `abs()` fila por fila dentro de cada categoría (Activo
Corriente, Pasivo Corriente, etc.) para reportar magnitudes positivas. Esto es
incorrecto para cualquier cuenta **contra-activo/contra-pasivo** genuina (depreciación
acumulada, deterioro acumulado): su función contable es reducir el valor neto de su
cuenta principal mediante un saldo de signo contrario (crédito) — sumarla por `abs()`
la convierte en una suma en vez de una resta, inflando el total exactamente por el
doble de su magnitud. El patrón generaliza: al agregar un grupo de cuentas contables
para reportar una magnitud, hay que sumar **con signo** (preservando la convención
débito/crédito) y solo invertir el signo del *total* una vez al final si la categoría
completa es de naturaleza crédito — nunca tomar `abs()` por fila cuando el grupo puede
contener una cuenta contraria a las demás.

**Por qué es útil aquí:** es la segunda vez que una cuenta contra-activo produce un bug
real en este proyecto (la primera fue A-05, un problema de clasificación, no de suma) —
cualquier nueva agregación de cuentas contables en este código merece la misma cautela
por defecto, no solo cuando ya se vio fallar una vez.

**Verificabilidad:** `Σ Saldo` (con signo) para Activo Corriente = $2,430,000 exacto
contra `TB_ERP` real; `Σ |Saldo|` (por fila, el bug) para la misma categoría = $2,510,000
— una discrepancia de $80,000, exactamente `2 × 40,000` (el doble de la única cuenta
contra-activo del grupo, "Deterioro acumulado de cartera") — la firma matemática
inconfundible de una cuenta contraria sumada con el signo equivocado, no un redondeo.
Test: `tests/test_sala_situacion_financiera.py::test_calcular_totales_neta_contra_cuentas_por_signo_no_por_abs`.

**Soporte bibliográfico:**
- Pacioli, L. (1494). *Summa de Arithmetica, Geometria, Proportioni et Proportionalita*.
  Venecia. — origen documentado del método de partida doble y la convención
  débito/crédito que hace que una cuenta "contraria" reduzca, no sume, el valor de su
  cuenta principal; es el fundamento de por qué `abs()` rompe la semántica contable.

**Estado:** corregido en `src/sala_situacion_financiera/_service.py`
(`calcular_totales`); sin token de dominio nuevo.

### A-09. Verificar un estado financiero derivado de dos períodos contra su propia identidad contable de cierre, con un escenario sintético construido por partida doble, expone bugs que una inspección línea por línea no detecta

**Descripción:** al construir `sala_flujo_efectivo` (NIC 7, método indirecto), la única
forma de saber si el motor estaba realmente bien construido — no solo "cada línea se ve
razonable" — fue construir un escenario de dos balances de comprobación relacionados
por partida doble real (ingresos, gastos, compras de activos, pagos de deuda,
dividendos, todo cuadrando entre sí por diseño) y verificar la **identidad de cierre**
del propio estado: CFO + CFI + CFF debe ser exactamente igual al cambio real de
efectivo entre los dos balances (NIC 7.10). Esa única aserción de alto nivel expuso 3
bugs de signo independientes que ninguna revisión línea por línea había detectado,
porque cada línea por separado parecía plausible — el error solo se hizo visible al
exigir que el conjunto cuadrara exacto.

**Por qué es útil aquí:** aplica a cualquier estado financiero derivado que tenga una
identidad de cierre conocida por norma — Situación Financiera (Activo = Pasivo +
Patrimonio, ya usado para A-08) y Cambios en Patrimonio (Saldo Inicial + movimientos =
Saldo Final) ya se verificaron con el mismo criterio en esta sesión. El patrón: cuando
el dominio provee una ecuación de cierre exacta, construir el caso de prueba sintético
para que esa ecuación sea la aserción de más alto nivel, en vez de (o antes que)
verificar cada línea por separado — atrapa errores compensatorios y de signo que la
verificación línea por línea no puede, porque dos errores de signo opuesto en líneas
distintas pueden hacer que cada línea "se vea mal" pero el total "se vea bien", o
viceversa.

**Verificabilidad:**
`tests/test_sala_flujo_efectivo.py::test_calcular_flujo_efectivo_indirecto_reconcilia_con_cambio_real_de_efectivo`
fija `flujo_neto_efectivo == 30.0` (el cambio real de caja del escenario, $130-$100)
como la aserción que certifica la corrección global del motor — las aserciones sobre
`cfo`/`cfi`/`cff` individuales están ahí para diagnóstico, pero es la suma contra el
cambio real de efectivo la que no admite compensación de errores.

**Soporte bibliográfico:**
- Chen, T. Y., Cheung, S. C., & Yiu, S. M. (1998). *Metamorphic Testing: A New Approach
  for Generating Next Test Cases*. Technical Report HKUST-CS98-01, Hong Kong University
  of Science and Technology. — formaliza verificar una relación conocida entre
  entradas/salidas relacionadas (aquí, la identidad contable de cierre NIC 7.10) en vez
  de un oráculo de valores individuales — la relación misma es el oráculo.

**Estado:** aplicado en 3 correcciones de signo en `src/sala_flujo_efectivo/_service.py`;
documenta un patrón de verificación/testing, no introduce un token de dominio nuevo.

### A-10. Una librería de extracción de tablas puede depender de líneas de grilla visibles en el documento, no solo de la disposición del texto — una tabla "sin bordes" puede fallar en silencio (0 tablas, sin excepción)

**Descripción:** al construir la extracción de PDF con `pdfplumber`, un primer intento
de generar un PDF de prueba con `reportlab` (`Table` sin `TableStyle`) producía un
documento con texto perfectamente extraíble y una disposición tabular clara a la vista
— pero `extract_tables()` devolvía una lista vacía, sin ningún error. La causa: la
estrategia de detección de tablas por defecto de `pdfplumber` (`"lines"`) busca líneas
de grilla efectivamente dibujadas en el PDF, no solo la alineación/posición del texto;
un `Table` de `reportlab` sin estilo de grilla explícito no dibuja ninguna línea, así
que para `pdfplumber` "no hay tabla" aunque para un lector humano claramente la haya.
Agregar `TableStyle([("GRID", ...)])` resolvió el problema sin tocar el código de
extracción en sí.

**Por qué es útil aquí:** es un gotcha silencioso — no lanza excepción, solo devuelve
una lista vacía — que en producción se interpretaría como "el PDF no tiene tabla"
(mensaje correcto para un escaneo, incorrecto para un PDF con tabla real sin bordes
dibujados). Cualquier PDF de una herramienta que no dibuje bordes de celda explícitos
(algunos reportes de ERP usan solo espaciado/alineación) fallaría de la misma forma
silenciosa — vale la pena saberlo antes de depurarlo en un archivo real de un cliente.
No hay una causa más profunda que documentar aquí más allá de "así está implementada la
heurística de la librería" — es exactamente el tipo de hallazgo empírico que el
criterio 6 de esta skill admite sin exigirle un predicado matemático, solo la
observación reproducible.

**Verificabilidad:** reproducible con `tests/test_sala_importacion_pdf.py` — un `Table()`
de `reportlab` sin `GRID` produce `extract_tables() == []` (confirmado manualmente
durante la construcción del test, antes de la corrección); con `GRID`, devuelve la
tabla completa. Condición exacta: `pdfplumber` 0.11.10 (ver `requirements.txt`),
estrategia de detección por defecto (`"lines"`).

**Soporte bibliográfico:**
- No se encontró una fuente académica o de ingeniería de software aplicable al patrón
  general más allá de la documentación de la propia herramienta — se decidió no forzar
  una cita externa (mismo criterio que A-04/A-06). Referencia técnica válida: pdfplumber,
  *"Extracting Tables"* (github.com/jsvine/pdfplumber#extracting-tables) — documentación
  oficial de la librería, no un principio general de la industria.

**Estado:** resuelto en el fixture de prueba (`tests/test_sala_importacion_pdf.py`); no
afectó código de producción (`src/sala_importacion/_service.py` ya estaba correcto, el
problema era solo en cómo se generaba el PDF de prueba) — se documenta igual porque el
gotcha reaparecería si alguien reusa `reportlab` para otro PDF de prueba sin saberlo.

---

## Candidatos considerados y descartados en esta ejecución (2026-09-27)

Para que la selectividad sea verificable en vez de un criterio de confianza ciega:

- **La aclaración del contador** (las 5 categorías NIIF 18 son exclusivas del Estado de
  Resultados) — descartada: es un **hecho normativo contable**, no un patrón de
  ingeniería; ya vive correctamente en `PRD.md` RF-14 v3.13, duplicarlo aquí no agrega
  nada.
- **La heurística de exclusión de ORI** (capital/reserva legal no son Otro Resultado
  Integral) — descartada por el mismo motivo: es una regla de negocio contable
  específica, no un patrón generalizable a otro tipo de código.
- **Reutilizar la derivación de dividendos entre `sala_flujo_efectivo` y
  `sala_cambios_patrimonio` vía compuerta ADPA** — considerado, descartado por
  insuficientemente novedoso: es una aplicación directa de "no dupliques lógica entre
  módulos", ya un principio de diseño extremadamente conocido (DRY); el único elemento
  algo más específico (un test de consistencia cruzada entre dos salas) no alcanza por
  sí solo el umbral de "útil más allá de lo obvio".
- **El descubrimiento de la regla global de git** (`~/.config/git/ignore` ya cubre
  `**/.claude/settings.local.json` en todos los repos) — descartado: es un hallazgo real
  y verificado, pero es una nota de *tooling* de la sesión sobre configuración de Git,
  no un patrón que vaya a reaparecer en el desarrollo futuro de la app NIIF 18 en sí.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
