# PRD: Aplicación NIIF 18

**Fuente normativa**: NIIF 18 "Presentación e Información a Revelar en los Estados Financieros", emitida por el IASB en abril de 2024, sustituye a la NIC 1. Aplicación obligatoria para ejercicios que inicien a partir del 1 de enero de 2027 (adopción anticipada permitida). El desarrollo normativo operacionalizado en este PRD está documentado en detalle en `governance/artefactos/biblioteca_doctrinal/` (7 volúmenes) y contrastado contra fuentes oficiales gratuitas del IASB, ESMA y EBA (ver §9, Fuentes normativas) — debe validarse contra el texto oficial completo y con un asesor contable antes de certificar el motor de clasificación como fuente de verdad para producción (ver §7, Riesgos).

---

## 1. Visión y Alcance

### 1.1 Visión
Aplicación de escritorio/web (Streamlit) en Python que permite a una entidad importar su balanza de comprobación, identificar su actividad comercial, reclasificar automáticamente sus cuentas bajo las 5 categorías obligatorias de NIIF 18, generar el juego completo de estados financieros con los subtotales normativos, y gestionar sus Medidas de Rendimiento Definidas por la Gerencia (MPM) con conciliación auditable.

### 1.2 Público objetivo
`¤publico_objetivo_niif18`
Contadores y medianas/grandes empresas que aplican NIIF completas; también cooperativas, entidades de microcrédito, y bancos de primer y segundo piso (ej. CFN).

### 1.3 Alcance (in scope)
`¤alcance_in_scope`
- Importación de balanza de comprobación vía CSV, Excel o PDF generado por herramienta.
- Mapeo cuenta → categoría NIIF 18, con motor de clasificación jerárquica asistido.
- Identificación de la actividad comercial de la entidad vía RUC contra el SRI, con inferencia de sección CIIU, como precondición del árbol de clasificación.
- Generación del juego completo de 4 estados financieros: Estado de Resultados, Estado de Situación Financiera (NIC 1.60-76), Estado de Flujo de Efectivo método indirecto (NIC 7.18(b)) y Estado de Cambios en el Patrimonio (NIC 1.106-110). Flujo de Efectivo y Cambios en Patrimonio requieren balanza comparativa de un segundo período.
- Gestión de MPMs: definición, cálculo, conciliación y nota auditable.
- Comparativos entre periodos.
- Validación normativa de etiquetas/clasificaciones antes de exportar.
- Exportación de reportes (Excel).
- Registro de auditoría append-only (trazabilidad de cambios de clasificación).

### 1.4 Fuera de alcance (explícito)
`¤fuera_de_alcance`
- Consolidación de estados financieros multientidad.
- Integración directa con ERPs (solo CSV/Excel/PDF de herramienta).
- Determinación automática y sin confirmación de si "financiar clientes" o "invertir" es actividad principal de la entidad: el CIIU sugiere, pero la confirmación del usuario es siempre obligatoria.
- Multi-moneda / conversión de estados financieros.
- Reexpresión retrospectiva real de comparativos (NIC 8) — hoy solo se advierte, no se recalcula.
- Mapeo/exportación a plantillas FINREP (EBA) o formato ESEF/XBRL.
- Módulo de apalancamiento financiero, intermediación de crédito o scoring de riesgo crediticio — evaluado como producto distinto (fintech), fuera del alcance de este proyecto.
- Reglas de clasificación como tabla declarativa editable por no-programadores — hoy son listas de palabras clave en Python.

### 1.5 Glosario
`¤glosario_dominio_niif18`
| Término | Definición |
|---|---|
| MPM | Medida de Rendimiento Definida por la Gerencia (Management-defined Performance Measure). Métrica no-NIIF (ej. EBITDA ajustado) que la gerencia usa y que debe revelarse en nota, conciliada con el subtotal NIIF más similar, sujeta a auditoría. |
| Categoría residual | La categoría Operación: por definición normativa, incluye todo lo que no se clasifique en Inversión, Financiación, Impuestos u Operaciones discontinuadas. |
| ADPA | Arquitectura de módulos ("salas") con compuertas `_service.py`: cada dominio funcional vive en su propia sala, y toda dependencia cruzada transita únicamente por la compuerta `_service.py` de la sala destino. |
| CIIU | Clasificación Industrial Internacional Uniforme (adaptada por el INEC/SCVS en Ecuador). Código jerárquico (nivel 1 = letra de sección, hasta nivel 4/6 = actividad específica) que identifica la actividad económica de una entidad. Fuente local: `data/ciiu.xlsx` (3,052 filas). |
| SRI | Servicio de Rentas Internas (Ecuador), entidad que emite el RUC y expone una consulta pública puntual por RUC, fuente de datos por defecto de identificación de entidad. |
| SCVS | Superintendencia de Compañías, Valores y Seguros (Ecuador). Publica el Directorio de Compañías (RUC, razón social, CIIU, estado); ruta alterna de identificación de entidad cuando se necesita el código CIIU exacto en vez de inferido. |
| Actividad principal | Configuración por entidad que indica si financiar a clientes o invertir en activos específicos es el giro central del negocio; afecta la reclasificación de partidas hacia Operación. Se deriva por defecto del sector CIIU de la entidad y el usuario la confirma o corrige — nunca se aplica sin confirmación. |


---

## 2. Modelo de Datos

### 2.1 Categorías NIIF 18 (enum fijo)
`¤categorias_niif18_enum`
1. `OPERACION` — residual, incluye actividad principal + no clasificables + volátiles/no recurrentes.
2. `INVERSION` — método de participación; activos con retorno independiente de otros recursos.
3. `FINANCIACION` — pasivos que solo implican obtención de fondos; dividendos pagados; interés neto de beneficios definidos.
4. `IMPUESTOS` — impuesto a la renta.
5. `OPERACIONES_DISCONTINUADAS`.

`src/sala_catalogo/_service.py` implementa un enum de 6 valores, añadiendo "0. Balance General" como filtro previo de `sala_importacion` para partidas que no pertenecen al Estado de Resultados (no es una categoría NIIF 18).


### 2.2 Subtotales obligatorios
`¤subtotales_obligatorios`

- `RESULTADO_OPERATIVO` = suma de partidas en `OPERACION`.
- `RESULTADO_ANTES_FINANCIACION_IMPUESTOS` = `RESULTADO_OPERATIVO` + `INVERSION` + `FINANCIACION`.
- `RESULTADO_DEL_PERIODO` (resultado del año, tras impuestos y discontinuadas).


### 2.3 Entidades de datos
`¤entidades_de_datos`

```
Cuenta
- codigo (str, PK)
- nombre (str)
- naturaleza (DEBE/HABER)
- tipo_partida (ingreso/gasto)

MapeoCuenta
- cuenta_codigo (FK)
- categoria_niif18 (enum §2.1)
- subcategoria (ej: "interes_pasivo_beneficios_definidos")
- es_actividad_principal (bool)
- justificacion (str) — obligatorio para auditoría

ConfiguracionEntidad
- ruc (str, FK EntidadPublica)
- financiacion_es_actividad_principal (bool)
- inversion_es_actividad_principal (bool)
- metodo_gastos (funcion/naturaleza/mixto)
- origen_actividad_principal (enum: "sugerido_ciiu" | "confirmado_usuario" | "manual")

EntidadPublica
- ruc (str, PK)
- razon_social (str)
- ciiu_codigo (str, FK CatalogoCIIU)
- estado (str)
- fuente (enum: "consulta_sri" | "snapshot_scvs")
- fecha_consulta (datetime)

CatalogoCIIU — poblado desde `data/ciiu.xlsx`
- codigo (str, PK)
- descripcion (str)
- nivel (int, 1-4/6)
- sugerencia_actividad_principal (enum: "financiacion" | "inversion" | "ninguna")

MPM
- nombre (str)
- formula (str/expresión)
- subtotal_niif_relacionado (FK subtotal)
- conciliacion (tabla partida→ajuste)

RegistroAuditoria
- timestamp, usuario, cuenta_codigo, categoria_anterior, categoria_nueva, justificacion
```


---

## 3. Árbol de Decisión de Clasificación (RF-03)
`¤arbol_decision_clasificacion`

Orden de evaluación por partida (ingreso o gasto), implementado en `sala_clasificacion.clasificar_partida`:

0. **Filtro previo**: un dividendo pagado a accionistas no es partida del Estado de Resultados: se reconoce en el Estado de Cambios en el Patrimonio (reduce utilidades retenidas). Si la cuenta es un dividendo con saldo deudor (pagado), se excluye (`CATEGORIA_BALANCE_GENERAL`) y no continúa el árbol.
1. **¿Es impuesto a la renta?** → `IMPUESTOS`. Fin.
2. **¿Pertenece a una operación discontinuada?** → `OPERACIONES_DISCONTINUADAS`. Fin.
3. **¿Es financiación general?** (préstamos, bonos emitidos, interés neto de pasivos por beneficios definidos a empleados) → candidato `FINANCIACION`. Incluye el gasto por interés de todos los pasivos, sin excepción.
4. **¿Es rendimiento de método de participación, o de un activo que genera retorno en gran medida independiente de los demás recursos de la entidad?** (propiedades de inversión, acciones, instrumentos de deuda, dividendos de acciones en otras compañías, efectivo/equivalentes) → candidato `INVERSION`.
5. **Excepción de actividad principal**: si `ConfiguracionEntidad.financiacion_es_actividad_principal` o `inversion_es_actividad_principal` es verdadero para esta partida → reclasificar a `OPERACION`. **Excepciones a la excepción**: el interés de arrendamientos y de pasivos por beneficios definidos (pensiones) nunca se reclasifica a `OPERACION` por esta vía, ni siquiera para una entidad cuya actividad principal es financiar a clientes (ej. un banco). El resultado por método de participación tampoco tiene excepción de actividad principal: nunca se reclasifica a `OPERACION`.
6. **Intereses y dividendo recibido**: determinístico por dirección del flujo, no por actividad principal:
   - Gasto por interés (pagado) → siempre `FINANCIACION`.
   - Ingreso por interés (recibido) o dividendo recibido → `INVERSION` por defecto.
   - Dividendo pagado → ver paso 0.
7. **Si no aplicó ninguna regla anterior** → `OPERACION` (categoría residual; incluye también partidas volátiles o no recurrentes).

**Precondición**: `ConfiguracionEntidad` completa (RF-11) antes de correr la clasificación masiva; cada `MapeoCuenta` resultante deja `justificacion` obligatoria.

**Riesgo señalado**: este árbol debe validarse contra el texto oficial completo de NIIF 18 (párrafos B42 y siguientes) antes de release a producción — está contrastado hoy contra fuentes secundarias oficiales (IASB *Project Summary*, ESMA *Public Statement*, EBA *Opinion*/FINREP, ver §9), no contra el estándar completo con notas técnicas.


---

## 4. Módulos Funcionales (Salas ADPA)
`¤modulos_funcionales_salas`

| Sala | Rastro `¤` | Responsabilidad | RF |
|---|---|---|---|
| `sala_importacion` | | Importar y validar balanza de comprobación (CSV/Excel/PDF) | RF-01 |
| `sala_catalogo` | | Catálogo de cuentas, enum de categorías, paleta de colores | RF-02 |
| `sala_clasificacion` | | Motor de clasificación jerárquica (árbol §3) | RF-02, RF-03 |
| `sala_estados_financieros` | | Estado de Resultados y subtotales mandatorios | RF-04, RF-07 |
| `sala_mpm` | | Gestión, cálculo y conciliación de MPMs | RF-05, RF-06 |
| `sala_validacion` | | Validaciones normativas de etiquetas y estructura | RF-08 |
| `sala_reportes` | | Exportación de reportes | RF-09 |
| `sala_auditoria` | | Registro append-only de cambios | RF-10 |
| `sala_entidad` | | Identificación de entidad por RUC, resolución de CIIU, sugerencia de actividad principal | RF-11 |
| `sala_situacion_financiera` | | Estado de Situación Financiera (NIC 1.60-76) | RF-12 |
| `sala_flujo_efectivo` | | Estado de Flujo de Efectivo, método indirecto (NIC 7) | RF-13 |
| `sala_cambios_patrimonio` | | Estado de Cambios en el Patrimonio (NIC 1.106-110) | RF-14 |

`src/app.py` es el presentador puro : orquesta Streamlit y llama a las 12 salas; no calcula ni clasifica nada por sí mismo. Ninguna sala importa directamente de otra — toda dependencia cruzada pasa por la compuerta `_service.py` de la sala destino.

Cada RF de abajo documenta, además de su función orquestadora (**AST-L1**, punto de entrada público de la sala), sus **sub-funciones de tercer nivel (AST-L3 — Función Algorítmica)**: la lógica de cálculo/transformación pura que implementa el requisito, distinta de las funciones L2 (coordinación de flujo) y L4 (utilería de bajo nivel).


---

## RF-01 — Importar balanza de comprobación
`¤construir_balanza_estandar`

- Acepta CSV, Excel o PDF generado por herramienta (rechaza escaneos/fotos por ausencia de capa de texto extraíble, vía `pdfplumber`) con columnas mínimas: código de cuenta, nombre, naturaleza (debe/haber), monto — detectadas por forma de los datos, no por nombre de cabecera fijo.
- Valida: balanza cuadrada (suma debe = suma haber), sin códigos duplicados, sin montos no numéricos.
- **Criterio de aceptación**: ante un archivo mal formado, el sistema rechaza la importación completa (no parcial) y reporta línea y motivo exacto del error.

**AST-L1**: `construir_balanza_estandar` (`src/sala_importacion/_service.py`).

**AST-L3**:
- `infer_columns_by_mathematical_weights`: adivina cuáles 3 columnas crudas corresponden a Cuenta/Descripción/Saldo por forma matemática de los datos (densidad numérica, longitud de texto, unicidad).
- `clean_numeric_series`: coerción numérica tolerante (separadores de miles, paréntesis contables como negativo).


---

## RF-02 — Mapear cuentas a las 5 categorías NIIF 18
`¤mapeo_cuentas_categorias`

- Permite mapeo manual y sugerencia automática vía motor de clasificación.
- **Criterio de aceptación**: toda cuenta sin mapeo bloquea la generación del Estado de Resultados; el sistema lista cuentas pendientes.
- **Sin ancla de código propia**: la sugerencia automática la resuelve la misma función `¤clasificar_dataframe` que gobierna RF-03 (ver §4) — RF-02 y RF-03 comparten sala e implementación, no hay una segunda función distinta que anclar aquí.


---

## RF-03 — Aplicar prueba de clasificación jerárquica
`¤clasificar_dataframe`

- Implementa el árbol de decisión de §3, en el orden especificado.
- Requiere `ConfiguracionEntidad` completa antes de ejecutar clasificación masiva.
- **Criterio de aceptación**: dado un conjunto de partidas de prueba (préstamo bancario, dividendo pagado, resultado por método de participación, interés de pensiones, partida no recurrente sin categoría clara), el motor produce la categoría esperada según §3 en el 100% de los casos.

**AST-L1**: `clasificar_dataframe` (`src/sala_clasificacion/_service.py`).

**AST-L3**:
- `clasificar_partida`: implementa el árbol de decisión completo de §3 para una sola partida (cuenta, descripción, saldo) — es la función algorítmica pura que `clasificar_dataframe` invoca por fila.


---

## RF-04 — Generar Estado de Resultados con subtotales mandatorios
`¤calcular_subtotales`

- Genera los 3 subtotales de §2.2.
- Soporta presentación de gastos por función, naturaleza o mixta (configurable).
- **Criterio de aceptación**: el Estado de Resultados generado cuadra matemáticamente (subtotales = suma de sus partidas) y muestra las 5 categorías en el orden normativo.

**AST-L1**: `calcular_subtotales` (`src/sala_estados_financieros/_service.py`).

**AST-L3**:
- `is_income_account`: decide por código y descripción de cuenta si una partida es de ingreso o de gasto (prevalencia de vocabulario de gasto sobre términos ambiguos).
- `calculate_pl_contribution`: convierte una fila clasificada en su contribución con signo al PL_Neto.


---

## RF-05 — Calcular y reconciliar MPMs
`¤calcular_base_niif`

- Permite definir fórmulas de MPM (ej. EBITDA ajustado) referenciando partidas/subtotales del Estado de Resultados.
- Genera conciliación automática MPM ↔ subtotal NIIF más similar.
- **Criterio de aceptación**: cada MPM definida muestra su conciliación completa, con cada ajuste identificado y su origen (cuenta o partida).

**AST-L3**:
- `calcular_base_niif` (`src/sala_mpm/_service.py`): resuelve el valor del subtotal NIIF 18 de anclaje elegido para una MPM, invocando `sala_estados_financieros.calcular_subtotales` vía compuerta ADPA.


---

## RF-06 — Generar nota de MPMs auditables
`¤construir_registro_mpm`

- Exporta la nota de MPMs en el formato requerido para el Estado de Resultados (una sola nota consolidada).
- **Criterio de aceptación**: la nota incluye, por cada MPM: definición, fórmula, conciliación, y periodo comparativo.

**AST-L1**: `construir_registro_mpm` (`src/sala_mpm/_service.py`).


---

## RF-07 — Comparativos entre periodos
`¤comparativos_entre_periodos`

- Genera comparativo entre 2+ periodos con las mismas categorías y subtotales.
- **Criterio de aceptación**: si un periodo comparativo fue preparado antes de la reclasificación NIIF 18, el sistema señala explícitamente que requiere reexpresión (solo advertencia; la reexpresión real, NIC 8, no está implementada — ver §5).


---

## RF-08 — Validar etiquetas
`¤puede_exportar`

- Verifica que toda partida tenga categoría válida (una de las 5), que los subtotales estén completos, y que no haya cuentas sin `justificacion`.
- Puerta de reconciliación obligatoria: bloquea la exportación (RF-09) si la balanza no cuadra o quedan cuentas sin categoría válida.
- **Criterio de aceptación**: el sistema no permite exportar un reporte con validaciones pendientes sin advertencia explícita al usuario.

**AST-L1**: `puede_exportar` (`src/sala_validacion/_service.py`).

**AST-L3**:
- `balanza_cuadrada`: compara la suma neta de saldos contra la tolerancia de cuadre.
- `contar_cuentas_pendientes`: cuenta filas sin categoría NIIF 18 válida.


---

## RF-09 — Exportar reportes
`¤generar_excel_estado_resultados`

- Exporta a Excel (`src/sala_reportes/generador.py`, `generar_excel_estado_resultados`).
- **Criterio de aceptación**: pendiente de definir formatos adicionales (PDF, CSV son candidatos).


---

## RF-10 — Auditoría
`¤registrar_cambio`

- Registra cada cambio de clasificación: quién, cuándo, categoría anterior/nueva, justificación.
- **Criterio de aceptación**: el registro de auditoría es append-only (no editable ni borrable desde la UI/CLI).

**AST-L1**: `registrar_cambio` (`src/sala_auditoria/_service.py`).


---

## RF-11 — Identificar actividad comercial de la entidad (SRI / CIIU)
`¤buscar_entidad_ruc_sri`

- El usuario ingresa el RUC de la entidad; el sistema consulta en vivo al SRI (`srienlinea.sri.gob.ec`, endpoint público sin sesión) y resuelve razón social, estado y actividad económica de forma instantánea.
- **Limitación real**: el SRI no devuelve código CIIU, solo texto libre de actividad económica. `inferir_ciiu_por_texto` compara ese texto contra el catálogo CIIU local (`data/ciiu.xlsx`) por solapamiento de tokens significativos (Jaccard, sobre descripciones de nivel ≥2) y devuelve el código/sección más probable junto con un `score_confianza` expuesto en la UI.
- El código/sección CIIU inferido se mapea a una sugerencia de `financiacion_es_actividad_principal` / `inversion_es_actividad_principal` en `ConfiguracionEntidad`, mostrada como checkbox pre-marcado que el usuario debe confirmar explícitamente (`¤sugerencia_confirmacion_actividad_principal`) — nunca se aplica sola.
- La actividad principal derivada es entrada obligatoria del árbol de clasificación (§3): sin una entidad identificada y su actividad principal confirmada, el sistema bloquea la clasificación masiva.
- El usuario puede corregir la sugerencia; la corrección queda registrada (`origen_actividad_principal = "manual"`) y es auditable (RF-10).
- **Ruta alterna**: descarga y consulta del Directorio SCVS completo (`actualizar_snapshot_directorio` / `cargar_directorio` / `buscar_entidad_por_ruc`) cuando se necesita el código CIIU exacto en vez de inferido — no es el flujo por defecto de la UI por su costo de descarga (~35 MB, ~70-80s la primera vez por sesión).
- **Criterio de aceptación**: dado un RUC existente, el sistema resuelve razón social + estado + actividad económica + sección CIIU inferida (con score de confianza) en una sola consulta instantánea, y no permite avanzar a RF-03 sin que el usuario confirme o corrija la sugerencia. Dado un RUC no encontrado o un fallo del servicio del SRI, el sistema permite continuar con configuración 100% manual.
- **Riesgo señalado (doble)**: (a) el mapeo sección CIIU → sugerencia de actividad principal es una regla de negocio propia del proyecto, no un dato oficial de la SCVS ni del IASB; (b) la sección CIIU en sí misma es inferida por coincidencia de texto, no leída de un código oficial — el `score_confianza` existe para que el usuario sepa cuánto confiar en la inferencia antes de aceptarla.

**AST-L1**: `buscar_entidad_ruc_sri` (`src/sala_entidad/_service.py`).

**AST-L3**:
- `inferir_ciiu_por_texto`: compara el texto libre de actividad económica del SRI contra el catálogo CIIU local por solapamiento de tokens y devuelve el código más probable con `score_confianza`.
- `sugerir_actividad_principal`: mapea una sección CIIU nivel 1 a la sugerencia `financiacion`/`inversion`/`ninguna`.


---

## RF-12 — Generar Estado de Situación Financiera (NIC 1.60-76)
`¤clasificar_dataframe_balance`

- Clasifica cada cuenta de balance (código 1.x/2.x/3.x, las que RF-02 excluye del Estado de Resultados a Categoría 0) en 5 categorías: Activo Corriente, Activo No Corriente, Pasivo Corriente, Pasivo No Corriente, Patrimonio.
- **Señal de clasificación**: prefijo de código de cuenta (`1.1`→Activo Corriente, `1.2`→Activo No Corriente, `2.1`→Pasivo Corriente, `2.2`→Pasivo No Corriente, `3`→Patrimonio) — misma señal fuerte de `sala_clasificacion` (código de cuenta sobre palabra clave de la descripción). NIC 1.66-68 define "corriente" por criterio operativo que no puede derivarse de una balanza por sí sola; el código de cuenta es una aproximación que asume que el plan de cuentas del cliente ya codificó esa distinción, no un sustituto del criterio profesional.
- **Criterio de aceptación**: dada una balanza clasificada, el sistema genera los 5 totales y valida la ecuación contable fundamental (Activo = Pasivo + Patrimonio + Resultado del período no cerrado).
- **Riesgo señalado**: sumar por valor absoluto en vez de por signo produce un error grave con cuentas contra-activo/contra-pasivo genuinas (ej. depreciación acumulada) — corregido en el motor actual.

**AST-L1**: `clasificar_dataframe_balance` (`src/sala_situacion_financiera/_service.py`).

**AST-L3**:
- `clasificar_partida_balance`: clasifica una cuenta de balance en una de las 5 categorías por prefijo de código.
- `calcular_totales`: suma por categoría y valida la ecuación contable fundamental.


---

## RF-13 — Generar Estado de Flujo de Efectivo, método indirecto (NIC 7.18(b))
`¤calcular_flujo_efectivo_indirecto`

- Concilia el resultado neto del período (RF-04) con el cambio real de efectivo, mediante: partidas no monetarias (depreciación/amortización/deterioro, resultado por método de participación), cambios en capital de trabajo, y los cambios netos en Activo No Corriente (Inversión) y Pasivo No Corriente/Patrimonio contribuido (Financiación).
- **Requiere balanza comparativa de un segundo período**: el Flujo de Efectivo es por definición (NIC 7.10) el cambio de efectivo entre dos fechas, no calculable de un solo período. Sin comparativo, el sistema muestra CFO limitado a partidas no monetarias, con CFI/CFF en cero.
- **Simplificación reconocida**: usa el cambio neto de cada categoría de balance entre los dos períodos (NIC 7.20) — no distingue compras brutas de disposiciones dentro de Activo No Corriente ni préstamos nuevos de pagos de capital dentro de Pasivo No Corriente. Los dividendos pagados se derivan del cambio en Resultados Acumulados (nunca del Estado de Resultados, por diseño del Paso 0 de §3).
- **Criterio de aceptación**: dado un par de balanzas Año 1/Año 2 y el resultado neto de Año 2, CFO + CFI + CFF debe ser exactamente igual al cambio real de efectivo entre los dos balances — identidad contable fundamental del estado (NIC 7.10).
- **Riesgo señalado**: no validado aún contra un caso real de dos períodos, solo contra un escenario sintético construido por partida doble.

**AST-L1**: `calcular_flujo_efectivo_indirecto` (`src/sala_flujo_efectivo/_service.py`).

**AST-L3**:
- `_cambio_por_categoria`: calcula el delta Año2-Año1 de una categoría del Estado de Situación Financiera, insumo de CFI/CFF.
- `_suma_por_palabras`: suma partidas del P&L clasificado cuya descripción contiene alguna de las palabras dadas (depreciación, deterioro, método de participación), para las partidas no monetarias de CFO.


---

## RF-14 — Generar Estado de Cambios en el Patrimonio (NIC 1.106-110)
`¤construir_cambios_patrimonio`

- Concilia cada cuenta de Patrimonio entre el saldo inicial (Año 1) y el saldo final (Año 2): resultado del período, dividendos pagados, y aportes/otros movimientos — mismo requisito de balanza comparativa que RF-13.
- Reutiliza la misma derivación de dividendos pagados que RF-13 (`sala_flujo_efectivo.calcular_flujo_efectivo_indirecto`, vía compuerta ADPA) en vez de duplicarla, para que ambas salas nunca reporten cifras de dividendos distintas para el mismo par de balances.
- **Criterio de aceptación**: para cada componente de patrimonio, Saldo Inicial + Utilidad del Período + Dividendos + Aportes y Otros Movimientos = Saldo Final, exacto.
- **Otro Resultado Integral (ORI, NIC 1.81A)**: además de la conciliación de patrimonio, el sistema calcula el Resultado Integral Total (Resultado del Período + ORI). El ORI se detecta a partir de movimientos en cuentas de reserva del Patrimonio no explicados por utilidad ni dividendos (ej. reserva de revaluación de PP&E) — excluye explícitamente capital/aportes y reservas de apropiación estatutaria (traslado interno desde Resultados Acumulados, no ORI). **Heurística marcada como borrador en la UI**: requiere revisión contable cuenta por cuenta antes de reportarse, no es una detección normativa cerrada.
- **Riesgo señalado**: no validado contra un caso real de dos períodos; asume que el cambio en cuentas de resultados acumulados se explica solo por utilidad y dividendos. La heurística de ORI puede sobre/sub-detectar si el plan de cuentas del cliente no distingue con claridad reservas de revaluación de otras reservas de patrimonio.

**AST-L1**: `construir_cambios_patrimonio` (`src/sala_cambios_patrimonio/_service.py`).

**AST-L3**:
- `_saldo_por_cuenta`: resuelve el saldo de una cuenta de patrimonio en un balance dado.
- `_es_cuenta_resultados`: identifica si una cuenta de patrimonio corresponde a Resultados Acumulados, para separar el efecto utilidad/dividendos del resto de movimientos.
- `calcular_resultado_integral`: identifica movimientos de reserva no explicados por utilidad/dividendos como ORI (excluyendo capital y reservas de apropiación estatutaria) y devuelve el Resultado Integral Total con desglose por cuenta.


---

## 5. Requisitos No Funcionales
`¤requisitos_no_funcionales`

- **Codificación:** todo archivo del proyecto se mantiene en UTF-8 estricto sin BOM (`INVARIANTS.md` `INV_ZERO_UTF8_BOM`).
- **Manejo de errores en importación**: fallos de archivo deben ser deterministas y reproducibles (mismo archivo → mismo error).
- **Trazabilidad**: toda clasificación debe ser explicable (mostrar qué regla del árbol §3 se aplicó).
- **Rendimiento**: sin objetivo definido aún — pendiente de definir volumen esperado de cuentas por balanza.
- **Auditabilidad**: los registros de `sala_auditoria` deben sobrevivir a reprocesos y reimportaciones.
- **Aislamiento ADPA**: ninguna sala importa directamente de otra; toda dependencia cruzada pasa por la compuerta `_service.py` de la sala destino.
- **Vigencia del dato público (RF-11)**: al ser una consulta en vivo por RUC al SRI, el dato es siempre actual por diseño. El catálogo CIIU local sí es estático y no requiere esta nota.
- **Disponibilidad offline (RF-11)**: la resolución de RUC depende de conectividad (consulta en vivo al SRI); si el SRI no responde, el sistema permite continuar con configuración 100% manual sin bloquear el resto del flujo, nunca falla de forma dura.


---

## 6. Arquitectura
`¤arquitectura_sistema`

- Python 3.11+, Streamlit para UI (`src/app.py` es el presentador puro; las 12 salas en conjunto son la lógica central).
- Estructura ADPA con compuertas `_service.py` por sala (§4).
- Gobernanza del proyecto: invariantes en `governance/artefactos/INVARIANTS.md`, trazabilidad de rastros en `VPA_MAP.md`, backlog vivo en `TASKS.md`, fuentes en `FUENTES_Y_BIBLIOGRAFIA.md`.
- Datasets públicos locales (RF-11): `data/ciiu.xlsx` (catálogo CIIU, estático) y `data/directorio_companias_scvs.xlsx` (directorio SCVS, ruta alterna).
- Cada rastro `¤` de dominio nace en `VPA_MAP.md` y está físicamente conectado a un archivo de código real bajo `src/` (comentario `# ¤rastro` sobre la función que lo implementa, verificable con `grep -rn "^# ¤" src/`).
- **Referencias de diseño**: se investigó `IFRS-Converter` (proyecto europeo de código abierto, sin licencia declarada — no se copió código, solo se usó como validación cruzada de decisiones ya tomadas: motor de reglas determinista con revisión humana como autoridad final, bitácora append-only, puerta de reconciliación obligatoria antes de exportar). Prioridad de diseño compartida: *Accuracy > Automation, Traceability > Convenience, Explainability > Black-box AI*.


---

## 7. Riesgos y Supuestos
`¤riesgos_supuestos`

- **Riesgo normativo**: el árbol de clasificación (§3) y los volúmenes de `biblioteca_doctrinal/` están basados en fuentes secundarias oficiales (IASB, ESMA, EBA) verificadas por búsqueda directa, no en el texto oficial completo con notas técnicas del IASB (requiere suscripción paga). Debe completarse antes de certificar el motor de clasificación como fuente de verdad para producción.
- **Supuesto**: la app asume que el usuario (contador/preparador) tiene el juicio profesional para configurar `ConfiguracionEntidad`; el sistema nunca infiere sin confirmación si financiación/inversión es actividad principal.
- **Riesgo de alcance**: RF-09 no tiene formato de exportación adicional definido más allá de Excel.
- **Riesgo de mapeo CIIU→actividad principal (RF-11)**: es una regla de negocio construida para este proyecto, no un dato oficial de la SCVS ni del IASB. Un sector CIIU puede agrupar entidades con giros muy distintos; la sugerencia debe tratarse siempre como punto de partida, nunca como clasificación final.
- **Riesgo de inferencia CIIU (RF-11)**: la sección CIIU se infiere por coincidencia de texto sobre la actividad económica que reporta el SRI, no se lee de un código oficial — se suma incertidumbre sobre la ya existente en el mapeo CIIU→actividad principal; el `score_confianza` en la UI existe para que el usuario dosifique cuánto confiar en cada inferencia.
- **Riesgo de datos no validados con caso real de dos períodos**: `sala_flujo_efectivo` y `sala_cambios_patrimonio` están verificados contra un escenario sintético construido por partida doble, no contra un caso real de balanza comparativa de dos años.


---

## 8. Estado de Implementación
`¤estado_implementacion`

Las 12 salas de §4 están implementadas (ninguna es un stub); `src/app.py` es presentador puro. Verificación exógena: suite de tests unitarios/integración (`tests/`, `pytest`) cubre las salas de lógica pura, incluyendo el test de extremo a extremo que fija los subtotales exactos del Estado de Resultados contra una balanza real, la verificación exacta del Estado de Situación Financiera contra la misma balanza, y la identidad CFO+CFI+CFF=ΔEfectivo de `sala_flujo_efectivo` con datos sintéticos.

**Pendiente real** (ver `TASKS.md`): validar el mapeo CIIU→actividad principal con criterio contable, completar `FUENTES_Y_BIBLIOGRAFIA.md` con el texto oficial completo del IASB, implementar reexpresión retrospectiva real (NIC 8), validar `sala_flujo_efectivo`/`sala_cambios_patrimonio` contra un caso real de dos períodos, evaluar mapeo a plantillas FINREP, y decidir si se construye un motor de reglas de clasificación declarativo (no hardcodeado en Python).


---

## 9. Fuentes Normativas Principales
`¤fuentes_normativas_principales`

- IASB, *IFRS 18 Presentation and Disclosure in Financial Statements* — *Project Summary* (abril 2024).
- ESMA, *Reshaping performance: Implementation of IFRS 18* — *Public Statement*.
- EBA, *Opinion* `EBA/Op/2026/07` y plantillas FINREP revisadas (Annex III/IV, hoja "2 (post consultation)" = F 02.00 Estado de Resultados) — primera fuente del proyecto con cita de párrafo exacto de IFRS 18 por línea de subtotal.
- Reglamento de Ejecución (UE) 2026/338 de la Comisión Europea — endoso de IFRS 18 en la Unión Europea, aplicable desde el 1-ene-2027.
- NIC 1 (revisada por IFRS 18), NIC 7 y NIC 8 — para Estado de Situación Financiera, Estado de Flujo de Efectivo y reexpresión retrospectiva pendiente, respectivamente.

Registro completo de citas y trazabilidad epistémica en `FUENTES_Y_BIBLIOGRAFIA.md`.

---

> **Nota de reconstrucción (2026-09-30):** `TASKS.md` registra que este PRD fue
> reescrito en algún momento sin changelog, perdiendo las secciones §11 y §12 que
> `governance/artefactos/tasks/*.md` y varios comentarios de `src/` siguen citando como
> vigentes. Se reconstruyen aquí a partir de esas tareas — ninguna normativa nueva se
> introduce, solo se restituye lo ya decidido y verificado. §10 no se recrea: su
> contenido (Estado de Implementación) ya existe íntegro en §8 de este documento, bajo
> un número distinto al citado en algunos comentarios antiguos de `src/` — ver limpieza
> de citas asociada a esta reconstrucción.

## 11. Contexto Regulatorio Ampliado — Unión Europea

### 11.1 Estado de endoso de IFRS 18 en la Unión Europea
`¤endoso_ifrs18_ue`

El propietario aportó un resumen de búsqueda (Gemini) sobre IFRS 18/9/7 en Europa,
verificado contra la fuente primaria (ESMA, *European Common Enforcement Priorities
2025*, 14-oct-2025) antes de incorporarlo: el resumen tenía una imprecisión real
—presentaba IFRS 18 como prioridad de cumplimiento 2025, cuando el propio documento dice
en nota al pie "although not yet endorsed" (aún no endosada en la UE a esa fecha) y la
menciona solo como recordatorio general, no como prioridad.

**Actualización posterior (2026-09-23):** IFRS 18 **ya fue endosado** en la Unión
Europea mediante el Reglamento de Ejecución (UE) 2026/338 de la Comisión Europea
(13-feb-2026), aplicable desde el 1-ene-2027 — corrige el estado "aún no endosado" de
la fuente de oct-2025 citada arriba.

Confirmado también: modificaciones a IFRS 9/7 vigentes desde el 1-ene-2026 (contratos
de electricidad/PPAs, liquidación electrónica de pasivos, activos financieros con
cláusulas ESG) y el estado de la taxonomía dual ESEF (IAS 1 / IFRS 18) — documentadas
como contexto de mercado, sin acción de código (fuera del alcance RF-01 a RF-11). Si el
proyecto apunta a futuro a emisores cotizados en la UE, exportar en formato ESEF/XBRL
(no solo Excel/CSV como hoy en RF-09) sería un RF nuevo, condicionado a que la UE
publique el RTS on ESEF correspondiente — no iniciar sin confirmar el mercado objetivo
real con el propietario (`tasks/esef_xbrl_futuro.md`).

### 11.2 Plantillas FINREP de la EBA: qué se adoptó y qué no
`¤finrep_eba_adopcion`

El propietario agregó documentos oficiales de la European Banking Authority (EBA):
`Opinion Finrep IFRS 18 - interim period.pdf` (EBA/Op/2026/07, 8-jul-2026) y sus anexos
técnicos (plantillas FINREP en Excel — F 02.00, F 16.xx, F 20.03, F 45.02-03). Se leyó
completo el Opinion y la hoja "2 (post consultation)" (= F 02.00, Estado de Resultados,
160 filas), con cita de párrafo IFRS 18 por línea.

**No se adopta el catálogo de líneas de FINREP como funcionalidad de la app.** FINREP es
el reporte supervisor bancario de la EBA — decenas de líneas específicas a instrumentos
financieros, deterioro por etapas de IFRS 9, garantías de depósito, etc., diseñadas para
entidades de crédito bajo supervisión prudencial europea. El público objetivo de este
proyecto (§1) es una entidad genérica, no necesariamente financiera ni europea; adoptar
el catálogo completo añadiría decenas de campos irrelevantes y un costo de mantenimiento
que no se sostiene sin un cliente bancario europeo real (`tasks/mapeo_finrep.md`).

**Sí se adoptó** del análisis de FINREP:
- La taxonomía de categorías y el orden de subtotales, como validación cruzada del árbol
  §3 y de `calcular_subtotales` — ya coincidía (Operación → Inversión → Resultado
  Operativo+Inversión → Financiación → antes de impuesto → impuesto → resultado del
  período), sin cambios de código más allá de la regla de método de participación.
- La confirmación con fuente oficial de que el resultado por método de participación en
  asociadas/negocios conjuntos no tiene excepción de actividad principal — aplicado en
  `sala_clasificacion._service.clasificar_partida`.
- Las citas de párrafo exactas (IFRS 18.69(a), .71, .75, .76(a)/(b), .118(e)/(f), IE13)
  como reemplazo progresivo de las citas por página de fuentes secundarias en §3 y
  `biblioteca_doctrinal/` — trabajo de limpieza incremental, no bloqueante.

Mapear automáticamente cada cuenta clasificada a una fila específica de una plantilla
FINREP, o exportar en el formato/estructura que exige la EBA, sigue **fuera de alcance**
(`tasks/mapeo_finrep.md`): el modelo de datos actual (5 categorías + Balance General) es
demasiado grueso para mapear 1:1 a FINREP sin extender el catálogo con un nivel de
detalle adicional, y no se justifica sin confirmar que el mercado objetivo incluye
entidades supervisadas por la EBA.

### 11.3 Doble reporte transitorio para entidades supervisadas por la EBA
`¤doble_reporte_transitorio`

El `Opinion EBA/Op/2026/07` (§11.2) describe un periodo de transición para entidades
supervisadas en la UE: entre el endoso de IFRS 18 (13-feb-2026) y la fecha de aplicación
del ITS sobre FINREP (~fin sept-2027), esas entidades pueden necesitar reportar tanto en
formato antiguo (NIC 1 / FINREP pre-IFRS 18) como en el nuevo simultáneamente.

**No implementado.** `sala_reportes` (RF-09) genera un único Estado de Resultados en el
formato NIIF 18 de este proyecto (§2.2) — no existe una plantilla "formato antiguo" para
generar en paralelo. Esta funcionalidad **solo es relevante para entidades supervisadas
en la UE bajo FINREP** (bancos y entidades de crédito reguladas por la EBA); el público
objetivo declarado de este proyecto (§1) es una entidad genérica. No priorizar hasta
confirmar con el propietario si el mercado objetivo real incluye entidades bajo
supervisión EBA (`tasks/doble_reporte_transitorio.md`).

## 12. Reunión de Producto (2026-09-23)

El propietario aportó la transcripción de una reunión de producto (Roberto, Giovanni,
Juan Carlos) con 4 bloques de discusión, analizados contra el estado real de la app:

### 12.1 Carga de los 4 estados financieros + comparativo de 2 años
`¤carga_multi_eeff_comparativo`

Roberto pidió cargar el juego completo de 4 estados financieros; Giovanni pidió
comparativo de 2 años con delta automático. Quedó marcado inicialmente "no iniciar sin
decisión explícita del propietario" por contradecir el alcance de entonces (§1.3 solo
permitía Estado de Resultados). El propietario pidió avanzar con **funcionalidad
completa** (no solo interfaz de carga) — implementado: `sala_situacion_financiera`
(NIC 1.60-76), `sala_flujo_efectivo` (NIC 7.18(b)) y `sala_cambios_patrimonio`
(NIC 1.106-110), los tres verificados con un escenario sintético de dos períodos por
partida doble contra sus identidades contables exactas (`tasks/carga_multi_eeff_comparativo.md`).
**Riesgo señalado, no resuelto:** ninguno de los 3 motores está validado contra un caso
real de dos períodos — el único fixture real del proyecto es de un solo período.

### 12.2 Categorización por colores y motor de reglas declarativo
`¤colores_motor_reglas`

Roberto pidió colores diferenciadores por categoría; Giovanni observó que las reglas de
clasificación de la NIIF 18 deberían parametrizarse en una tabla en vez de depender del
criterio del contador. Dos resultados distintos:

- **Paleta de colores — implementada** (`tasks/categorizacion_colores_niif18.md`):
  extraída por muestreo de píxeles sobre la imagen de referencia del propietario
  (`sala_catalogo.COLORES_NIIF18`). Las categorías Impuestos y Discontinuadas no eran
  visibles en el recorte compartido y se extendieron siguiendo el mismo estilo pastel —
  **quedan sujetas a confirmación** si el propietario comparte la guía de colores del
  IASB que Roberto mencionó; hasta donde se investigó, el IASB no publica una paleta
  normativa para NIIF 18 y esta debe presentarse como convención de producto propia, no
  como requisito oficial.
- **Motor de reglas declarativo — no implementado, en plan** (`tasks/motor_reglas_declarativo.md`):
  extraer las listas de palabras clave hardcodeadas de `sala_clasificacion` (y, por
  extensión 2026-09-24, el mapeo CIIU de `sala_entidad`) a una tabla de reglas editable
  con persistencia y auditoría — el árbol normativo de 7 pasos (§3) permanece en código,
  no editable; solo se externalizarían los patrones que alimentan cada paso. No iniciado
  por riesgo de regresión alto (el árbol ya tuvo 2 bugs reales corregidos) y porque
  requiere antes decidir persistencia real entre sesiones (hoy la app es 100%
  `st.session_state`).

### 12.3 Módulo de apalancamiento financiero
`¤modulo_apalancamiento_evaluado`

Giovanni y Roberto propusieron un módulo que dirija al usuario a crédito/financiamiento,
con scoring de riesgo crediticio, firma electrónica y hosting de reportes en la nube.
**Evaluado y no recomendado sin decisión de negocio explícita** (`tasks/modulo_apalancamiento_financiero.md`):
no es una extensión del motor de clasificación NIIF 18 sino un producto distinto
(fintech/bróker de crédito) que requiere infraestructura, firma electrónica certificada
y expertise de riesgo crediticio que este proyecto no tiene, además de riesgo regulatorio
no evaluado (posible calificación como intermediación financiera bajo regulación
ecuatoriana) — requiere asesoría legal antes de diseñar cualquier flujo, no solo antes de
lanzar.

### 12.4 Ampliación del público objetivo
`¤ampliacion_publico_objetivo`

Ya aplicado directamente: el público objetivo (§1.2) se amplió para incluir
cooperativas, entidades de microcrédito y bancos de primer y segundo piso.


---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
