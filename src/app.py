import streamlit as st
import pandas as pd

# [¤protocolo_migracion_legacy] ZERAG BIOS Clean-Room Pattern (Presentador Puro)
# Migración Fase 0 completada: toda la lógica de negocio vive en las compuertas
# _service.py de cada sala (PRD.md §10, TASKS.md ¤fase_migracion_adpa). Este archivo
# solo orquesta Streamlit y llama a las salas — no calcula ni clasifica nada por sí mismo.
from sala_importacion import _service as imp_svc
from sala_catalogo import _service as cat_svc
from sala_clasificacion import _service as class_svc
from sala_estados_financieros import _service as fs_svc
from sala_mpm import _service as mpm_svc
from sala_reportes import _service as rep_svc
from sala_validacion import _service as val_svc
from sala_auditoria import _service as aud_svc
from sala_entidad import _service as ent_svc

CIIU_PATH = "data/ciiu.xlsx"
DIRECTORIO_SCVS_PATH = "data/directorio_companias_scvs.xlsx"


def init_theme():
    st.set_page_config(page_title="NIIF 18 Reporting Matrix", layout="wide", page_icon=":material/account_balance:", initial_sidebar_state="expanded")


def reset_app_state():
    new_version = st.session_state.get('uploader_version', 0) + 1
    st.session_state.clear()
    st.session_state['uploader_version'] = new_version
    st.rerun()


@st.dialog("Confirmar reinicio")
def confirm_reset():
    st.write("Esto borrará la balanza cargada, la matriz de reclasificación, la configuración de entidad y las MPM registradas en esta sesión. Esta acción no se puede deshacer.")
    with st.container(horizontal=True):
        if st.button("Cancelar", width="stretch"):
            st.rerun()
        if st.button("Sí, reiniciar", type="primary", icon=":material/delete_forever:", width="stretch"):
            reset_app_state()


def cuentas_column_config(extra=None):
    config = {
        "Cuenta": st.column_config.TextColumn("Cuenta", pinned=True),
        "Descripcion": st.column_config.TextColumn("Descripción"),
        "Saldo": st.column_config.NumberColumn("Saldo", format="$ %.2f"),
    }
    if extra:
        config.update(extra)
    return config


@st.cache_data(show_spinner="Cargando directorio SCVS (una sola vez por sesión)...")
def _cargar_directorio_cacheado():
    df = ent_svc.cargar_directorio(DIRECTORIO_SCVS_PATH)
    fecha = ent_svc.fecha_snapshot_directorio(DIRECTORIO_SCVS_PATH)
    return df, fecha


@st.cache_data(show_spinner="Cargando catálogo CIIU (una sola vez por sesión)...")
def _cargar_ciiu_cacheado():
    return ent_svc.cargar_catalogo_ciiu(CIIU_PATH)


def configuracion_entidad_activa():
    cfg = st.session_state.get('configuracion_entidad')
    if cfg and cfg.get('origen_actividad_principal') in ('confirmado_usuario', 'manual'):
        return cfg
    return None


def clasificar_con_configuracion(df):
    cfg = st.session_state.get('configuracion_entidad') or {}
    return class_svc.clasificar_dataframe(
        df,
        financiacion_es_actividad_principal=cfg.get('financiacion_es_actividad_principal', False),
        inversion_es_actividad_principal=cfg.get('inversion_es_actividad_principal', False),
    )


# ¤interfaz
def main():
    init_theme()
    if 'uploader_version' not in st.session_state:
        st.session_state['uploader_version'] = 0
    if 'bitacora_auditoria' not in st.session_state:
        st.session_state['bitacora_auditoria'] = []

    with st.sidebar:
        st.header("Control de sesión", icon=":material/tune:")
        tiene_datos = st.session_state.get('df_balanza') is not None
        if tiene_datos:
            st.caption(f"Fuente activa: {st.session_state.get('fuente_origen', 'balanza cargada')}")
        cfg_activa = configuracion_entidad_activa()
        if cfg_activa:
            st.caption(f"Entidad: {cfg_activa.get('ruc', 'configuración manual')}")
        if st.button("Resetear todos los valores", icon=":material/restart_alt:", width="stretch", disabled=not tiene_datos):
            confirm_reset()
        st.caption("La norma NIIF 18 aplica al Estado de Resultados. Las cuentas de Balance (1, 2, 3) se segregan a la Categoría 0.")

    st.title("NIIF 18 Financial Reporting Matrix", icon=":material/account_balance:")
    tabs = st.tabs([
        ":material/domain: Entidad",
        ":material/upload_file: Ingesta",
        ":material/rule: Matriz de reclasificación",
        ":material/account_tree: Árbol de EEFF",
        ":material/insights: Conciliación MPM",
        ":material/folder_zip: Centro de exportación",
    ])

    # ----------------- FASE 0: Entidad (RF-11) -----------------
    with tabs[0]:
        st.subheader("Identificación de la entidad", icon=":material/domain:")
        st.caption("Busque el RUC en el directorio SCVS para obtener una sugerencia de actividad principal, o configure manualmente. Esta configuración condiciona el árbol de clasificación (RF-03).")
        with st.form("form_entidad"):
            ruc_input = st.text_input("RUC", max_chars=13, placeholder="1790013731001")
            buscar = st.form_submit_button("Buscar en SCVS", icon=":material/search:", type="primary")
        if buscar and ruc_input.strip():
            df_directorio, fecha_snapshot = _cargar_directorio_cacheado()
            entidad = ent_svc.buscar_entidad_por_ruc(df_directorio, ruc_input.strip(), fecha_snapshot)
            st.session_state['entidad_encontrada'] = entidad
            st.session_state['entidad_ruc_buscado'] = ruc_input.strip()

        entidad = st.session_state.get('entidad_encontrada')
        ruc_buscado = st.session_state.get('entidad_ruc_buscado')
        if ruc_buscado and entidad is None:
            st.warning(f"RUC '{ruc_buscado}' no encontrado en el snapshot local de la SCVS. Puede continuar con configuración 100% manual.", icon=":material/warning:")

        if entidad:
            with st.container(border=True):
                st.markdown(f"**{entidad['razon_social']}**")
                st.caption(f"RUC {entidad['ruc']} · {entidad['estado']} · snapshot SCVS del {entidad['fecha_snapshot_origen']}")
                desc_ciiu = ent_svc.resolver_descripcion_ciiu(_cargar_ciiu_cacheado(), entidad['ciiu_nivel_1'])
                st.write(f"CIIU nivel 1: **{entidad['ciiu_nivel_1']}** — {desc_ciiu or 'descripción no encontrada'}")
                st.caption(f"CIIU nivel 6 (detalle): {entidad['ciiu_nivel_6']}")
                sugerencia = ent_svc.sugerir_actividad_principal(entidad['ciiu_nivel_1'])
                st.badge(sugerencia['advertencia'], icon=":material/warning:", color="orange")
            fin_default = sugerencia['financiacion_es_actividad_principal']
            inv_default = sugerencia['inversion_es_actividad_principal']
        else:
            fin_default, inv_default = False, False

        st.markdown("##### Confirmar configuración de actividad principal")
        col_a, col_b = st.columns(2)
        with col_a:
            fin_principal = st.checkbox("Financiar clientes es la actividad principal de la entidad", value=fin_default, key="chk_fin_principal")
        with col_b:
            inv_principal = st.checkbox("Invertir en activos específicos es la actividad principal de la entidad", value=inv_default, key="chk_inv_principal")

        if st.button("Confirmar configuración", icon=":material/check_circle:", type="primary"):
            origen = "confirmado_usuario" if entidad else "manual"
            st.session_state['configuracion_entidad'] = {
                "ruc": entidad['ruc'] if entidad else (ruc_buscado or None),
                "financiacion_es_actividad_principal": fin_principal,
                "inversion_es_actividad_principal": inv_principal,
                "origen_actividad_principal": origen,
            }
            st.toast("Configuración de entidad confirmada. La clasificación masiva (RF-03) ya está habilitada.", icon=":material/check_circle:")

        cfg = configuracion_entidad_activa()
        if cfg:
            st.badge(f"Configuración confirmada ({cfg['origen_actividad_principal']})", icon=":material/check_circle:", color="green")
        else:
            st.badge("Configuración pendiente de confirmar — bloquea la clasificación masiva (RF-03)", icon=":material/lock:", color="orange")

    # ----------------- FASE 1: Ingesta -----------------
    with tabs[1]:
        st.subheader("Bandeja de entrada de balanzas contables", icon=":material/upload_file:")
        st.caption("Arrastre su balanza de comprobación (Excel o CSV); las columnas de cuenta, descripción y saldo se detectan automáticamente.")
        v_key = st.session_state.get('uploader_version', 0)
        uploaded_file = st.file_uploader(
            "Archivo contable",
            type=["csv", "xlsx", "xls"], key=f"uploader_{v_key}",
            help="Soporta .xlsx, .xls y .csv. El procesamiento es automático al soltar el archivo.",
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_raw = pd.read_csv(uploaded_file)
                    st.session_state['raw_filename'] = uploaded_file.name
                else:
                    xl = pd.ExcelFile(uploaded_file)
                    sheet_names = xl.sheet_names
                    default_sheet_idx = imp_svc.sugerir_hoja_balanza(sheet_names)
                    sel_sheet = st.selectbox("Pestaña del libro Excel", sheet_names, index=default_sheet_idx) if len(sheet_names) > 1 else sheet_names[0]
                    df_raw = imp_svc.read_excel_smart_header(uploaded_file, sel_sheet)
                    st.session_state['raw_filename'] = f"{uploaded_file.name} [{sel_sheet}]"

                cols_available = list(df_raw.columns)
                inf_cta, inf_desc, inf_saldo, conf_pct = imp_svc.infer_columns_by_mathematical_weights(df_raw)

                # Puerta de calidad (no solo advertencia): un archivo puede traer hojas de
                # referencia (respuesta esperada, EEFF ya resumido) con otra estructura —
                # `infer_columns_by_mathematical_weights` nunca valida esa premisa, solo
                # elige la mejor opción entre columnas malas. Ver TASKS.md
                # ¤validar_calidad_hoja_balanza y PRD.md §10 para el caso real que lo motivó.
                es_balanza_valida, motivos_calidad = imp_svc.evaluar_calidad_balanza(df_raw, inf_cta, inf_saldo)
                if not es_balanza_valida:
                    st.session_state['df_balanza'] = None
                    st.session_state['df_clasificado'] = None
                    st.error(" ".join(motivos_calidad), icon=":material/error:")
                else:
                    df_p = imp_svc.construir_balanza_estandar(df_raw, inf_cta, inf_desc, inf_saldo)
                    df_p['Categoria_NIIF18'] = clasificar_con_configuracion(df_p)
                    st.session_state['df_balanza'] = df_p
                    st.session_state['df_clasificado'] = df_p
                    st.session_state['fuente_origen'] = f"{st.session_state.get('raw_filename', 'Archivo')}"

                with st.expander("Personalizar mapeo de columnas (opcional)", icon=":material/tune:", expanded=not es_balanza_valida):
                    st.caption(f"Inferencia matemática: {conf_pct:.1f}% de confianza.")
                    if not es_balanza_valida:
                        st.caption("La detección automática de columnas falló (ver el error arriba). Ajuste el mapeo manualmente si esta pestaña sí es una balanza válida.")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1: s_cta = st.selectbox("Código / cuenta", cols_available, index=cols_available.index(inf_cta))
                    with col_m2: s_desc = st.selectbox("Descripción", cols_available, index=cols_available.index(inf_desc))
                    with col_m3: s_saldo = st.selectbox("Saldo / importe", cols_available, index=cols_available.index(inf_saldo))
                    if s_cta != inf_cta or s_desc != inf_desc or s_saldo != inf_saldo:
                        ok_manual, motivos_manual = imp_svc.evaluar_calidad_balanza(df_raw, s_cta, s_saldo)
                        if not ok_manual:
                            st.error(" ".join(motivos_manual), icon=":material/error:")
                        else:
                            df_m = imp_svc.construir_balanza_estandar(df_raw, s_cta, s_desc, s_saldo)
                            df_m['Categoria_NIIF18'] = clasificar_con_configuracion(df_m)
                            st.session_state['df_balanza'] = df_m
                            st.session_state['df_clasificado'] = df_m
                            st.session_state['fuente_origen'] = f"{st.session_state.get('raw_filename', 'Archivo')}"
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}", icon=":material/error:")

        if 'df_balanza' in st.session_state and st.session_state['df_balanza'] is not None:
            st_val = float(st.session_state['df_balanza']['Saldo'].sum())
            cuadrado = val_svc.balanza_cuadrada(st_val)
            with st.container(horizontal=True):
                st.metric("Archivo procesado", st.session_state.get('fuente_origen', 'Balanza'), border=True)
                st.metric("Registros contables", f"{len(st.session_state['df_balanza']):,}", border=True)
                st.metric("Balance de comprobación", f"$ {st_val:,.2f}", border=True)
            st.badge("Cuadre perfecto" if cuadrado else "Neto en libros distinto de cero", icon=":material/check_circle:" if cuadrado else ":material/warning:", color="green" if cuadrado else "orange")
            if not configuracion_entidad_activa():
                st.caption("Clasificación provisional (sin configuración de entidad confirmada, ver pestaña Entidad) — usa financiación/inversión = actividad no principal por defecto.")
            st.markdown("#### Previsualización estandarizada")
            st.dataframe(
                st.session_state['df_balanza'][['Cuenta', 'Descripcion', 'Saldo']],
                column_config=cuentas_column_config(),
                hide_index=True, width="stretch", height=300,
            )
        else:
            with st.container(border=True, horizontal_alignment="center"):
                st.markdown(":material/upload_file:")
                st.write("Aún no hay una balanza cargada.")
                st.caption("Cargue un archivo arriba para empezar el flujo: entidad → ingesta → matriz de reclasificación → estados financieros.")

    # ----------------- FASE 2: Matriz -----------------
    with tabs[2]:
        st.subheader("Matriz de asignación de categorías NIIF 18", icon=":material/rule:")
        if 'df_balanza' in st.session_state and st.session_state['df_balanza'] is not None:
            df_reclass = st.session_state.get('df_clasificado', st.session_state['df_balanza']).copy()
            if 'Categoria_NIIF18' not in df_reclass.columns:
                df_reclass['Categoria_NIIF18'] = clasificar_con_configuracion(df_reclass)
            pendientes = val_svc.contar_cuentas_pendientes(df_reclass, cat_svc.CATEGORIAS_NIIF18)
            with st.container(horizontal=True):
                if pendientes == 0:
                    st.badge("Todas las cuentas están clasificadas", icon=":material/check_circle:", color="green")
                else:
                    st.badge(f"{pendientes} cuentas sin categoría válida", icon=":material/warning:", color="orange")

            cfg_ok = configuracion_entidad_activa() is not None
            c_m1, c_m2 = st.columns([3, 1])
            with c_m2:
                if not cfg_ok:
                    st.caption("Confirme la configuración de entidad (pestaña Entidad) para habilitar RF-03.")
                if st.button("Re-aplicar auto-clasificación", icon=":material/auto_awesome:", width="stretch", disabled=not cfg_ok):
                    df_reclass['Categoria_NIIF18'] = clasificar_con_configuracion(df_reclass)
                    st.session_state['df_clasificado'] = df_reclass
                    st.rerun()

            v_key = st.session_state.get('uploader_version', 0)
            editor_key = f"editor_matriz_{v_key}"
            edited_df = st.data_editor(
                df_reclass,
                column_config=cuentas_column_config({
                    "Categoria_NIIF18": st.column_config.SelectboxColumn("Clasificación NIIF 18", options=cat_svc.CATEGORIAS_NIIF18, required=True),
                }),
                hide_index=True, width="stretch", height=420, key=editor_key,
            )

            # RF-10: registrar en la bitácora append-only cada cambio de clasificación
            # detectado por el data_editor (sala_auditoria nunca edita/borra, solo agrega).
            edited_rows = st.session_state.get(editor_key, {}).get("edited_rows", {})
            for row_idx, cambios in edited_rows.items():
                if "Categoria_NIIF18" in cambios:
                    cuenta_codigo = df_reclass.iloc[row_idx]['Cuenta']
                    categoria_anterior = df_reclass.iloc[row_idx]['Categoria_NIIF18']
                    aud_svc.registrar_cambio(
                        st.session_state['bitacora_auditoria'],
                        usuario="usuario_sesion", cuenta_codigo=cuenta_codigo,
                        categoria_anterior=categoria_anterior, categoria_nueva=cambios["Categoria_NIIF18"],
                        justificacion="Edición manual en Matriz de reclasificación",
                    )
            st.session_state['df_clasificado'] = edited_df

            with st.expander(f"Bitácora de auditoría ({len(st.session_state['bitacora_auditoria'])} cambios)", icon=":material/history:", expanded=False):
                bitacora = aud_svc.obtener_bitacora(st.session_state['bitacora_auditoria'])
                if bitacora:
                    st.dataframe(pd.DataFrame(bitacora), hide_index=True, width="stretch")
                else:
                    st.caption("Sin cambios manuales registrados todavía.")
        else:
            with st.container(border=True, horizontal_alignment="center"):
                st.markdown(":material/rule:")
                st.write("No hay datos para clasificar todavía.")
                st.caption("Cargue una balanza en la pestaña Ingesta para generar la matriz de reclasificación.")

    # ----------------- FASE 3: Árbol EEFF -----------------
    with tabs[3]:
        st.subheader("Árbol de rendimiento estructurado", icon=":material/account_tree:")
        if 'df_clasificado' in st.session_state and st.session_state['df_clasificado'] is not None:
            df_c, subtotales = fs_svc.calcular_subtotales(st.session_state['df_clasificado'])
            sub_1 = subtotales['sub_1_resultado_operativo']
            sub_2 = subtotales['sub_2_antes_fin_imp']
            sub_3 = subtotales['sub_3_resultado_periodo']

            st.markdown("##### Subtotales mandatorios (cálculo en vivo)")
            with st.container(horizontal=True):
                st.metric("1. Resultado operativo", f"$ {sub_1:,.2f}", border=True)
                st.metric("2. Antes de fin. e imptos.", f"$ {sub_2:,.2f}", border=True)
                st.metric("3. Resultado del periodo", f"$ {sub_3:,.2f}", border=True)

            with st.container(border=True):
                st.markdown("**Análisis gráfico de subtotales**")
                chart_df = pd.DataFrame({"Subtotal": ["1. Operativo", "2. Pre-fin/imp", "3. Periodo neto"], "Monto ($)": [sub_1, sub_2, sub_3]}).set_index("Subtotal")
                st.bar_chart(chart_df, width="stretch")

            pl_col = st.column_config.NumberColumn("Efecto en resultados", format="$ %.2f")
            with st.expander("Ver desglose operativo (Categoría 1)", icon=":material/work:", expanded=True):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('1.')][['Cuenta', 'Descripcion', 'Saldo', 'PL_Neto']], column_config=cuentas_column_config({"PL_Neto": pl_col}), hide_index=True, width="stretch")
            with st.expander("Ver desglose de inversión (Categoría 2)", icon=":material/trending_up:", expanded=False):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('2.')][['Cuenta', 'Descripcion', 'Saldo', 'PL_Neto']], column_config=cuentas_column_config({"PL_Neto": pl_col}), hide_index=True, width="stretch")
            with st.expander("Ver desglose de financiación (Categoría 3)", icon=":material/account_balance:", expanded=False):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('3.')][['Cuenta', 'Descripcion', 'Saldo', 'PL_Neto']], column_config=cuentas_column_config({"PL_Neto": pl_col}), hide_index=True, width="stretch")
            with st.expander("Ver cuentas excluidas de Balance General (Categoría 0)", icon=":material/block:", expanded=False):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('0.')][['Cuenta', 'Descripcion', 'Saldo']], column_config=cuentas_column_config(), hide_index=True, width="stretch")
        else:
            with st.container(border=True, horizontal_alignment="center"):
                st.markdown(":material/account_tree:")
                st.write("Aún no hay estados financieros generados.")
                st.caption("Cargue y clasifique su balance en las pestañas Ingesta y Matriz de reclasificación.")

    # ----------------- FASE 4: MPMs -----------------
    with tabs[4]:
        st.subheader("Medidas de rendimiento definidas por la gerencia (MPM)", icon=":material/insights:")
        c_form, c_table = st.columns([1, 1.5])
        with c_form:
            with st.container(border=True):
                nombres_plantilla = list(mpm_svc.PLANTILLAS_MPM.keys())
                plantilla = st.segmented_control("Plantilla MPM", nombres_plantilla, default=nombres_plantilla[0])
                plantilla = plantilla or "Personalizado"
                datos_plantilla = mpm_svc.PLANTILLAS_MPM[plantilla]
                with st.form("mpm_form"):
                    st.markdown("**Registrar nueva MPM**")
                    mpm_name = st.text_input("Denominación MPM", value=plantilla if plantilla != "Personalizado" else "", placeholder="ej. EBITDA Ajustado")
                    subtotal_base = st.segmented_control("Subtotal NIIF 18 de anclaje", [mpm_svc.SUBTOTAL_RESULTADO_OPERATIVO, mpm_svc.SUBTOTAL_RESULTADO_PERIODO], default=mpm_svc.SUBTOTAL_RESULTADO_OPERATIVO)
                    ajuste = st.number_input("Monto del ajuste (+/-)", value=datos_plantilla["ajuste"])
                    rationale = st.text_area("Justificación / nota explicativa", value=datos_plantilla["justificacion"], placeholder="Indique la justificación para los inversionistas...")
                    if st.form_submit_button("Validar e incluir", type="primary", icon=":material/check:", width="stretch"):
                        if mpm_name.strip():
                            df_base = st.session_state.get('df_clasificado')
                            val_base = mpm_svc.calcular_base_niif(df_base, subtotal_base)
                            if 'mpm_records' not in st.session_state:
                                st.session_state['mpm_records'] = []
                            st.session_state['mpm_records'].append(
                                mpm_svc.construir_registro_mpm(mpm_name, subtotal_base, val_base, ajuste, rationale)
                            )
                            st.toast(f"Medida '{mpm_name}' validada y registrada.", icon=":material/check_circle:")
                            st.rerun()
                        else:
                            st.error("Ingrese una denominación para la MPM.", icon=":material/error:")
        with c_table:
            with st.container(border=True):
                st.markdown("**Tabla de conciliación auditada (nota NIIF 18)**")
                if 'mpm_records' in st.session_state and st.session_state['mpm_records']:
                    money_cfg = lambda label: st.column_config.NumberColumn(label, format="$ %.2f")
                    st.dataframe(
                        pd.DataFrame(st.session_state['mpm_records']),
                        column_config={
                            "Base NIIF ($)": money_cfg("Base NIIF ($)"),
                            "Ajuste ($)": money_cfg("Ajuste ($)"),
                            "Efecto fiscal ($)": money_cfg("Efecto fiscal ($)"),
                            "Total MPM ($)": money_cfg("Total MPM ($)"),
                        },
                        hide_index=True, width="stretch",
                    )
                    if st.button("Limpiar MPMs", icon=":material/delete:"):
                        st.session_state['mpm_records'] = []
                        st.rerun()
                else:
                    st.markdown(":material/insights:")
                    st.write("No hay MPMs registradas todavía.")
                    st.caption("Seleccione una plantilla a la izquierda y presione 'Validar e incluir'.")

    # ----------------- FASE 5: Exportación -----------------
    with tabs[5]:
        st.subheader("Centro de exportación regulatoria", icon=":material/folder_zip:")
        hay_datos = 'df_clasificado' in st.session_state and st.session_state['df_clasificado'] is not None
        if not hay_datos:
            st.caption("Los archivos de exportación se habilitan luego de cargar y clasificar una balanza.")

        # Puerta de reconciliación obligatoria (TASKS.md ¤puerta_reconciliacion_beta,
        # inspirada en IFRS-Converter: "no reconciliation, no finalized result"). Bloquea
        # el Estado de Resultados regulatorio — el CSV de mapeo/trazabilidad sigue
        # disponible siempre porque es precisamente la herramienta para diagnosticar por
        # qué no reconcilia, no el entregable final.
        puede_exportar_eeff, motivos_bloqueo = (False, [])
        if hay_datos:
            puede_exportar_eeff, motivos_bloqueo = val_svc.puede_exportar(st.session_state['df_clasificado'], cat_svc.CATEGORIAS_NIIF18)
            if not puede_exportar_eeff:
                st.warning("El Estado de Resultados regulatorio está bloqueado hasta reconciliar: " + " ".join(motivos_bloqueo), icon=":material/lock:")

        with st.container(horizontal=True):
            with st.container(border=True, width="stretch"):
                st.markdown("**Mapeo y trazabilidad**")
                st.caption("CSV con cada cuenta y su categoría NIIF 18 asignada. Disponible siempre, incluso sin reconciliar — es la herramienta para diagnosticar pendientes.")
                if hay_datos:
                    st.download_button("Descargar CSV", icon=":material/download:", data=st.session_state['df_clasificado'].to_csv(index=False).encode('utf-8'), file_name="mapeo_niif18.csv", mime="text/csv", type="primary", width="stretch")
                else:
                    st.button("Descargar CSV", icon=":material/download:", disabled=True, width="stretch")
            with st.container(border=True, width="stretch"):
                st.markdown("**Estado de Resultados**")
                st.caption("Excel con las 5 categorías y los 3 subtotales mandatorios. Requiere balanza cuadrada y sin cuentas pendientes.")
                if hay_datos and puede_exportar_eeff:
                    excel_data = rep_svc.generar_excel_estado_resultados(st.session_state['df_clasificado'])
                    st.download_button(
                        "Descargar Excel", icon=":material/download:",
                        data=excel_data,
                        file_name="estado_resultados_niif18.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary", width="stretch",
                    )
                else:
                    st.button("Descargar Excel", icon=":material/lock:", disabled=True, width="stretch")


if __name__ == "__main__":
    main()
