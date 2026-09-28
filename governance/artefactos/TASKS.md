# Bitácora Viva de Tareas y Roadmap
## **Proyecto:** NIIF 18

Este archivo es el **índice** de la bitácora. Cada tarea vive en su propio markdown bajo
`governance/artefactos/tasks/`, con su propio rastro `¤` como encabezado H1 — no como
texto en negrita dentro de una lista plana en un solo archivo. Ver la corrección de
alcance en y el aporte inédito A-04 en
`APORTES_INEDITOS.md` para el porqué de este cambio.

| | Rastro | Descripción | Detalle |
|---|---|---|---|
| ✅ | | Nido de 5 artefactos vivos materializado en `governance/artefactos/`. | [tasks/genesis_artefactos_vivos.md](tasks/genesis_artefactos_vivos.md) |
| ✅ | | Diseño de salas y compuertas `_service.py` (7 salas creadas como stubs). | [tasks/fase_boceto_adpa.md](tasks/fase_boceto_adpa.md) |
| ✅ | | `PRD.md` reestructurado como fuente única de verdad (fusión de 2 versiones previas + trazabilidad RF↔sala↔doctrina). | [tasks/prd_consolidacion.md](tasks/prd_consolidacion.md) |
| ✅ | | Fase 0: lógica extraída de `app.py` hacia las 9 compuertas `_service.py`; `app.py` quedó como presentador puro. | [tasks/fase_migracion_adpa.md](tasks/fase_migracion_adpa.md) |
| ✅ | | Sala `sala_auditoria` (RF-10) — registro append-only, integrado en la Matriz de reclasificación. | [tasks/sala_auditoria_nueva.md](tasks/sala_auditoria_nueva.md) |
| ✅ | | Árbol de decisión real (PRD.md §3) reemplazando la heurística plana; 2 regresiones reales corregidas + validación IASB. | [tasks/clasificacion_arbol_normativo.md](tasks/clasificacion_arbol_normativo.md) |
| ✅ | | Suite de tests unitarios por sala + verificación de flujo completo con `AppTest`. | [tasks/fase_sellado_tests.md](tasks/fase_sellado_tests.md) |
| 🟡 | | Validación parcial contra el *Project Summary* oficial gratuito del IASB; falta el texto completo (pago). | [tasks/fuentes_iasb_oficial.md](tasks/fuentes_iasb_oficial.md) |
| ✅ | | Sala `sala_entidad` (RF-11) — búsqueda RUC → CIIU contra los datasets SCVS/INEC reales. | [tasks/sala_entidad_nueva.md](tasks/sala_entidad_nueva.md) |
| ✅ | | `ciiu1.xlsx` y `directorio_companias(1).xlsx` movidos a `data/` con nombres limpios. | [tasks/datasets_a_data.md](tasks/datasets_a_data.md) |
| ⬜ | | Mapeo DRAFT (K→financiación, L→inversión) — requiere revisión de un contador para las 21 secciones CIIU. | [tasks/mapeo_ciiu_actividad_principal.md](tasks/mapeo_ciiu_actividad_principal.md) |
| ✅ | | `ConfiguracionEntidad` con `ruc`/`origen_actividad_principal`; gatea RF-03 hasta confirmación. | [tasks/configuracion_entidad_extendida.md](tasks/configuracion_entidad_extendida.md) |
| ✅ | | Caché en disco (`.parquet`) para el directorio SCVS: de 29.4s a 0.35s en cargas repetidas. | [tasks/optimizar_carga_directorio_scvs.md](tasks/optimizar_carga_directorio_scvs.md) |
| ✅ | | Tema nativo, iconografía Material, KPIs con borde, badges de estado, estados vacíos consistentes. | [tasks/frontend_usabilidad.md](tasks/frontend_usabilidad.md) |
| ✅ | | `APORTES_INEDITOS.md` (copiado de otro proyecto) auditado y purgado; 1 hallazgo real rescatado. | [tasks/purga_aportes_ineditos.md](tasks/purga_aportes_ineditos.md) |
| ✅ | | `FUENTES_Y_BIBLIOGRAFIA.md` (copiado de otro proyecto) auditado y reconstruido con fuentes reales. | [tasks/purga_fuentes_bibliografia.md](tasks/purga_fuentes_bibliografia.md) |
| ✅ | | 3 aportes genuinos (A-01 a A-03) agregados a `APORTES_INEDITOS.md` con soporte bibliográfico real. | [tasks/aportes_ineditos_validos.md](tasks/aportes_ineditos_validos.md) |
| ✅ | | Pestaña "Visor doctrinal" retirada de la UI — la biblioteca doctrinal es insumo de backend, no de usuario final. | [tasks/doctrina_fuera_de_frontend.md](tasks/doctrina_fuera_de_frontend.md) |
| ✅ | | Corrección normativa (interés de arrendamientos/pensiones) validada contra el *Public Statement* de ESMA. | [tasks/validacion_europea_esma.md](tasks/validacion_europea_esma.md) |
| ⬜ | | FX, derivados de cobertura, contraprestación contingente, provisiones de largo plazo — documentados, no implementados. | [tasks/excepciones_finas_pendientes.md](tasks/excepciones_finas_pendientes.md) |
| ✅ | | Exportación del Estado de Resultados bloqueada si la balanza no cuadra o hay cuentas pendientes. | [tasks/puerta_reconciliacion_beta.md](tasks/puerta_reconciliacion_beta.md) |
| ⬜ | | Requiere que el propietario acceda a IFRS Digital Subscription / IFRS Shop — no es tarea de código. | [tasks/acceso_pago_ifrs_beta.md](tasks/acceso_pago_ifrs_beta.md) |
| ✅ | | Resumen de búsqueda del propietario verificado y corregido contra la fuente primaria de ESMA (ECEP 2025). | [tasks/contexto_regulatorio_ue.md](tasks/contexto_regulatorio_ue.md) |
| ⬜ | | Exportación ESEF/XBRL — fuera de alcance, no iniciar sin confirmar mercado objetivo UE con el propietario. | [tasks/esef_xbrl_futuro.md](tasks/esef_xbrl_futuro.md) |
| ✅ | | `IFRS-Converter` (GitHub) auditado: sin licencia, no se copia código, solo referencia arquitectónica. | [tasks/auditoria_ifrs_converter.md](tasks/auditoria_ifrs_converter.md) |
| ✅ | | Confirmado con fuente oficial (EBA/FINREP F 02.00, fila 74) y aplicado en `sala_clasificacion`: método de participación nunca se mueve a Operación. | [tasks/excepcion_metodo_participacion_pendiente.md](tasks/excepcion_metodo_participacion_pendiente.md) |
| ✅ | | `LICENSE` cambiado de MIT a propietario ("Todos los derechos reservados"). | [tasks/licencia_propietaria.md](tasks/licencia_propietaria.md) |
| ✅ | | `TASKS.md` dividido en `tasks/*.md` para que cada rastro sea inyectable/trazable individualmente. | Ver `APORTES_INEDITOS.md` aporte A-04. |
| ✅ | | `VPA_MAP.md` NO se fragmentó (es la raíz donde nacen los rastros) — se conectó físicamente a 10 archivos reales bajo `src/` vía marcas `# inyectadas con `mcp_inject_stigmergic_trace`. | [tasks/conectar_vpa_map_a_archivos.md](tasks/conectar_vpa_map_a_archivos.md) |
| ✅ | | `PRD.md` recorrido completo: cada rastro de `VPA_MAP.md` aparece inline en la sección que describe la funcionalidad de la que nace (estructura de esa versión del PRD; ver estructura vigente en `PRD.md`). | [tasks/conectar_prd_a_vpa_map.md](tasks/conectar_prd_a_vpa_map.md) |
| ✅ | | Un archivo Excel puede traer hojas de referencia (no balanzas reales) que el motor de inferencia aceptaba ciegamente. Nueva `evaluar_calidad_balanza` bloquea la carga si la columna de saldo inferida no es mayoritariamente numérica sobre el total de filas — verificado contra las 3 hojas reales de `balance_prueba_niif18_sap_business_one.xlsx`. | [tasks/validar_calidad_hoja_balanza.md](tasks/validar_calidad_hoja_balanza.md) |
| ✅ | | `docs/` recibió documentos oficiales EBA/FINREP nuevos: confirmado el endoso de IFRS 18 en la UE (Reglamento 2026/338) y usada la plantilla F 02.00 como primera fuente del proyecto con cita de párrafo exacto de IFRS 18 por línea (`PRD.md` §11.4). | [tasks/docs_finrep_eba_analisis.md](tasks/docs_finrep_eba_analisis.md) |
| ✅ | | Resuelta: 4 cuentas de balance (depreciación/deterioro acumulados, provisión) se filtraban al Estado de Resultados por error ($690,000 de brecha). Corregido en `sala_clasificacion` — el motor ahora reproduce `ER_NIIF18` exacto ($813,000/$898,000/$550,000). | [tasks/discrepancia_motor_tb_erp_pendiente.md](tasks/discrepancia_motor_tb_erp_pendiente.md) |
| ⬜ | | NIC 8: recalcular periodos comparativos bajo NIIF 18 cuando fueron preparados bajo el formato antiguo — hoy RF-07 solo *señala* que se requiere, no reexpresa. | [tasks/reexpresion_retrospectiva.md](tasks/reexpresion_retrospectiva.md) |
| ⬜ | | Generar salida simultánea en formato antiguo (NIC 1) y nuevo (NIIF 18) para el período interino EBA (ene-sept 2027). No implementado. | [tasks/doble_reporte_transitorio.md](tasks/doble_reporte_transitorio.md) |
| ⬜ | | Detectar partidas genéricas ("Gastos varios", "Otros") y sugerir desglose — el motor hoy las clasifica sin señalar que requieren desagregación (caso real: `5.2.99.001` en `TB_ERP`). | [tasks/desagregacion_inteligente.md](tasks/desagregacion_inteligente.md) |
| ⬜ | | Mapear/exportar las partidas clasificadas a las plantillas FINREP oficiales (F 02.00 y relacionadas) — hoy FINREP solo se usa como fuente de criterios, no hay mapeo ni exportación real. | [tasks/mapeo_finrep.md](tasks/mapeo_finrep.md) |
| ✅ | | Paleta de colores por categoría NIIF 18 (`sala_catalogo.COLORES_NIIF18`) aplicada en `app.py`; categorías renombradas a forma corta; `sala_clasificacion` ahora deriva sus constantes de `sala_catalogo` en vez de duplicarlas. | [tasks/categorizacion_colores_niif18.md](tasks/categorizacion_colores_niif18.md) |
| ✅ | | Funcionalidad completa de los 4 estados financieros (RF-12/13/14, decisión del propietario, amplía §1.3). 3 motores nuevos (Situación Financiera, Flujo de Efectivo, Cambios en Patrimonio) + interfaz de Ingesta con balanza comparativa Año1/Año2 + pestaña "Estados Financieros" con 4 sub-pestañas. 66/66 tests en verde. No validado aún contra datos reales de dos períodos. | [tasks/carga_multi_eeff_comparativo.md](tasks/carga_multi_eeff_comparativo.md) |
| ✅ | | Estado de Resultado Integral (NIC 1.81A): detección automática de Otro Resultado Integral (ORI) desde movimientos de reserva en `sala_cambios_patrimonio`, excluyendo capital y reserva legal. Confirmado con el contador que las 5 categorías NIIF 18 son exclusivas del Estado de Resultados. 68/68 tests en verde. | [tasks/estado_resultado_integral_ori.md](tasks/estado_resultado_integral_ori.md) |
| ✅ | | Ingesta acepta PDF generado por herramienta (rechaza escaneos/fotos por ausencia de capa de texto) vía `pdfplumber`, reusando el mismo pipeline de inferencia que CSV/Excel. | [tasks/carga_pdf_ingesta.md](tasks/carga_pdf_ingesta.md) |
| ⬜ | | Reestructurar las listas de palabras clave hardcodeadas de `sala_clasificacion` (y, extensión 2026-09-24, el mapeo CIIU de `sala_entidad` + futuro FINREP) a una tabla de reglas declarativa editable desde la app, con persistencia y auditoría — el criterio contable no es estático. | [tasks/motor_reglas_declarativo.md](tasks/motor_reglas_declarativo.md) |
| ⬜ | | Módulo de apalancamiento financiero/crédito (scoring, firma electrónica, hosting en la nube) — evaluado como producto distinto, riesgo regulatorio alto, requiere decisión de negocio antes de diseñar. | [tasks/modulo_apalancamiento_financiero.md](tasks/modulo_apalancamiento_financiero.md) |
| ✅ | | Índice de los 4 bloques de la reunión de producto (2026-09-23), cada uno desglosado en su propia tarea. | [tasks/plan_reunion_producto.md](tasks/plan_reunion_producto.md) |
| ✅ | | `PRD.md` completo reestructurado (versión posterior a esta tarea): cada H2 lleva su rastro en línea propia y su cierre , siguiendo la gramática de `GLOSARIO.md` de ZERAG. Cada RF y cada hallazgo sustantivo pasó a ser su propio H2 (wrappers §2/§5 retirados de esa versión; el PRD se reescribió después sin changelog, ver `PRD.md` vigente). | [tasks/reestructuracion_estigmergica_prd.md](tasks/reestructuracion_estigmergica_prd.md) |
| ✅ | | RF-11 Fase 4 (superada por , código conservado como ruta alterna): descarga masiva del directorio SCVS con fallback local. | [tasks/consulta_en_vivo_scvs.md](tasks/consulta_en_vivo_scvs.md) |
| ✅ | | RF-11 rediseñado: consulta puntual al SRI por RUC (sin descarga masiva, sin base de datos) + inferencia de sección CIIU por coincidencia de texto contra el catálogo local. Verificado en la app real con 3 RUCs de distinto sector. | [tasks/consulta_sri_ruc_en_vivo.md](tasks/consulta_sri_ruc_en_vivo.md) |

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
