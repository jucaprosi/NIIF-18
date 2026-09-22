import streamlit as st
import pandas as pd
import numpy as np
import os
import re

# [¤protocolo_migracion_legacy] ZERAG BIOS Clean-Room Pattern (Presentador Puro)
from sala_importacion import _service as imp_svc
from sala_catalogo import _service as cat_svc
from sala_clasificacion import _service as class_svc
from sala_estados_financieros import _service as fs_svc
from sala_mpm import _service as mpm_svc
from sala_reportes import _service as rep_svc
from sala_validacion import _service as val_svc

CATEGORIAS_NIIF18 = [
    "0. Balance General (No P&L / Excluir)",
    "1. Operación (Ingresos / Gastos Operativos)",
    "2. Inversión (Ingresos / Gastos por Inversiones)",
    "3. Financiación (Costos / Pasivos Financieros)",
    "4. Impuestos a las Ganancias",
    "5. Operaciones Discontinuadas"
]

TITULOS_DOCTRINALES = {
    "01_resumen_niif18.md": "Volumen 1: Marco General y Alcance de la NIIF 18",
    "02_categorias_estado_resultados.md": "Volumen 2: Las 5 Categorías Obligatorias de Resultados",
    "03_subtotales_mandatorios.md": "Volumen 3: Los 3 Subtotales Mandatorios de Rendimiento",
    "04_mpm_medidas_gerencia.md": "Volumen 4: Medidas Definidas por la Gerencia (MPM)",
    "05_agregacion_desagregacion.md": "Volumen 5: Principios de Agregación y Desagregación",
    "06_transicion_comparativos.md": "Volumen 6: Disposiciones Transitorias y Periodos Comparativos",
    "07_catalogo_cuentas_mapeo.md": "Volumen 7: Guía de Reclasificación y Mapeo Contable"
}

def init_theme():
    st.set_page_config(page_title="NIIF 18 Reporting Matrix", layout="wide", page_icon="🏛️", initial_sidebar_state="expanded")
    st.markdown("""
        <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stDataFrame { font-size: 0.85rem !important; }
        .metric-card { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 1rem; margin-bottom: 1rem; }
        h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .stButton>button { border-radius: 4px; border: 1px solid #ced4da; font-weight: 500; }
        </style>
    """, unsafe_allow_html=True)

def reset_app_state():
    new_version = st.session_state.get('uploader_version', 0) + 1
    st.session_state.clear()
    st.session_state['uploader_version'] = new_version
    st.rerun()

def clean_numeric_series(series):
    return pd.to_numeric(
        series.astype(str).str.replace('$', '', regex=False).str.replace('€', '', regex=False)
        .str.replace('£', '', regex=False).str.replace(',', '', regex=False)
        .str.replace('(', '-', regex=False).str.replace(')', '', regex=False).str.strip(),
        errors='coerce'
    ).fillna(0.0)

def auto_classify_niif18_series(df):
    categories = []
    for _, row in df.iterrows():
        cta, desc = str(row['Cuenta']).strip(), str(row['Descripcion']).strip().lower()
        if cta.startswith(('1', '2', '3')) or any(w in desc for w in ['activo', 'pasivo', 'patrimonio', 'capital', 'bancos', 'caja', 'proveedor', 'cliente', 'inventario', 'edificio', 'terreno', 'obligacion', 'cuenta por']):
            if not any(w in desc for w in ['ingreso', 'gasto', 'costo']):
                categories.append("0. Balance General (No P&L / Excluir)")
                continue
        if any(w in desc for w in ['dividendo', 'inversion', 'inversión', 'asociada', 'negocio conjunto', 'participacion']):
            categories.append("2. Inversión (Ingresos / Gastos por Inversiones)")
        elif cta.startswith(('54', '6')) or any(w in desc for w in ['interes', 'interés', 'financier', 'bancari', 'prestamo', 'préstamo', 'deuda', 'arrendamiento financiero']):
            categories.append("3. Financiación (Costos / Pasivos Financieros)")
        elif cta.startswith(('55', '59')) or any(w in desc for w in ['impuesto a la renta', 'impuesto a las ganancias', 'gasto por impuesto', 'impuesto diferido']):
            categories.append("4. Impuestos a las Ganancias")
        elif any(w in desc for w in ['discontinuad', 'interrumpid', 'abandonad']):
            categories.append("5. Operaciones Discontinuadas")
        else:
            categories.append("1. Operación (Ingresos / Gastos Operativos)")
    return categories

def is_income_account(cta, desc, saldo):
    # Los términos de gasto prevalecen: "Costo de ventas" o "Gasto por impuesto a las ganancias" no son ingresos.
    if cta.startswith('4'):
        return True
    if any(w in desc for w in ['costo', 'gasto', 'impuesto', 'depreciaci', 'amortizaci', 'comisi', 'provisi', 'perdida', 'pérdida', 'deterioro']):
        return False
    if any(w in desc for w in ['ingreso', 'venta', 'honorario', 'ganancia', 'rendimiento', 'dividendo', 'utilidad']):
        return True
    if 'interes' in desc or 'interés' in desc:
        return saldo < 0
    if cta[:1] in ('5', '6', '7', '8', '9'):
        return False
    return saldo < 0

def calculate_pl_contribution(row):
    if str(row['Categoria_NIIF18']).startswith('0.'):
        return 0.0
    cta, desc, saldo = str(row['Cuenta']).strip(), str(row['Descripcion']).strip().lower(), float(row['Saldo'])
    return abs(saldo) if is_income_account(cta, desc, saldo) else -abs(saldo)

def read_excel_smart_header(excel_file, sheet_name):
    df_preview = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, nrows=15)
    best_row, max_non_na = 0, 0
    for r in range(len(df_preview)):
        non_na = df_preview.iloc[r].dropna().count()
        if non_na > max_non_na and non_na >= 2:
            max_non_na, best_row = non_na, r
    df_full = pd.read_excel(excel_file, sheet_name=sheet_name, header=best_row)
    return df_full.dropna(how='all', axis=1).dropna(how='all', axis=0)

def infer_columns_by_mathematical_weights(df):
    cols = list(df.columns)
    if len(cols) < 2:
        return cols[0], cols[0], cols[0], 1.0
    sample = df.head(min(len(df), 120))
    scores_cta, scores_desc, scores_saldo = {}, {}, {}
    total_cols = max(1, len(cols) - 1)
    for i, col in enumerate(cols):
        s = sample[col].astype(str).str.strip()
        ordinal = i / total_cols
        clean_num = clean_numeric_series(s)
        num_ratio = float((~clean_num.isna()).mean())
        has_neg = 1.0 if (clean_num < 0).any() else 0.0
        code_ratio = float((s.str.match(r'^[0-9A-Za-z\.\-_/]+$') & (~s.str.contains(' ', regex=False))).mean()) if len(s) > 0 else 0.0
        spaces_ratio = float(s.str.contains(r'\s+', regex=True).mean()) if len(s) > 0 else 0.0
        avg_char_len, uniq_ratio = float(s.str.len().mean()) if len(s) > 0 else 0.0, float(s.nunique() / max(1, len(s)))
        scores_saldo[col] = (0.50 * num_ratio) + (0.20 * has_neg) + (0.15 * (1.0 - code_ratio)) + (0.15 * ordinal)
        scores_cta[col] = (0.40 * code_ratio) + (0.30 * uniq_ratio) + (0.20 * (1.0 - spaces_ratio)) + (0.10 * (1.0 - ordinal))
        scores_desc[col] = (0.50 * spaces_ratio) + (0.30 * (1.0 - num_ratio)) + (0.20 * min(1.0, avg_char_len / 15.0))
    best_score, best_assignment = -1.0, (cols[0], cols[min(1, len(cols)-1)], cols[-1])
    for c_i in cols:
        for d_j in cols:
            if d_j == c_i and len(cols) >= 3: continue
            for s_k in cols:
                if (s_k == c_i or s_k == d_j) and len(cols) >= 3: continue
                total = scores_cta[c_i] + scores_desc[d_j] + scores_saldo[s_k]
                if total > best_score:
                    best_score, best_assignment = total, (c_i, d_j, s_k)
    return best_assignment[0], best_assignment[1], best_assignment[2], min(100.0, max(10.0, (best_score / 3.0) * 100.0))

def main():
    init_theme()
    if 'uploader_version' not in st.session_state:
        st.session_state['uploader_version'] = 0
    with st.sidebar:
        st.header("⚙️ Control de Sesión")
        if st.button("🗑️ Resetear Todos los Valores", width="stretch"):
            reset_app_state()
        st.divider()
        st.info("📐 **NIIF 18 P&L:** La norma aplica al Estado de Resultados. Cuentas de Balance (1, 2, 3) se segregan a la Categoría 0.")

    st.title("🏛️ NIIF 18 Financial Reporting Matrix")
    tabs = st.tabs(["📥 1. Ingesta (Dropzone)", "🏷️ 2. Matriz de Reclasificación", "📊 3. Árbol de EEFF", "📈 4. Conciliación MPM", "📑 5. Centro de Exportación", "📚 6. Visor Doctrinal"])
    
    # ----------------- FASE 1: Ingesta -----------------
    with tabs[0]:
        st.subheader("Bandeja de Entrada de Balanzas Contables")
        v_key = st.session_state.get('uploader_version', 0)
        uploaded_file = st.file_uploader(
            "📂 Arrastre aquí su archivo contable (Excel o CSV) o pinche para seleccionarlo:",
            type=["csv", "xlsx", "xls"], key=f"uploader_{v_key}",
            help="Soporta cualquier archivo contable (.xlsx, .xls, .csv). El procesamiento es automático al soltarlo."
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_raw = pd.read_csv(uploaded_file)
                    st.session_state['raw_filename'] = uploaded_file.name
                else:
                    xl = pd.ExcelFile(uploaded_file)
                    sheet_names = xl.sheet_names
                    default_sheet_idx = next((i for i, s in enumerate(sheet_names) if any(k in s.lower() for k in ['tb', 'balanza', 'trial', 'balance', 'saldos', 'datos', 'data', 'cuentas'])), 0)
                    sel_sheet = st.selectbox("📑 Seleccione la pestaña del libro Excel:", sheet_names, index=default_sheet_idx) if len(sheet_names) > 1 else sheet_names[0]
                    df_raw = read_excel_smart_header(uploaded_file, sel_sheet)
                    st.session_state['raw_filename'] = f"{uploaded_file.name} [{sel_sheet}]"
                
                cols_available = list(df_raw.columns)
                inf_cta, inf_desc, inf_saldo, conf_pct = infer_columns_by_mathematical_weights(df_raw)
                df_p = pd.DataFrame({'Cuenta': df_raw[inf_cta].astype(str), 'Descripcion': df_raw[inf_desc].astype(str), 'Saldo': clean_numeric_series(df_raw[inf_saldo])})
                df_p = df_p[df_p['Cuenta'].str.strip() != 'nan']
                df_p['Categoria_NIIF18'] = auto_classify_niif18_series(df_p)
                
                st.session_state['df_balanza'] = df_p
                st.session_state['df_clasificado'] = df_p
                st.session_state['fuente_origen'] = f"{st.session_state.get('raw_filename', 'Archivo')}"
                
                with st.expander("🛠️ Personalizar Mapeo de Columnas (Opcional)", expanded=False):
                    st.caption(f"Inferencia Matemática: {conf_pct:.1f}% de confianza.")
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1: s_cta = st.selectbox("Código/Cuenta:", cols_available, index=cols_available.index(inf_cta))
                    with col_m2: s_desc = st.selectbox("Descripción:", cols_available, index=cols_available.index(inf_desc))
                    with col_m3: s_saldo = st.selectbox("Saldo/Importe:", cols_available, index=cols_available.index(inf_saldo))
                    if s_cta != inf_cta or s_desc != inf_desc or s_saldo != inf_saldo:
                        df_m = pd.DataFrame({'Cuenta': df_raw[s_cta].astype(str), 'Descripcion': df_raw[s_desc].astype(str), 'Saldo': clean_numeric_series(df_raw[s_saldo])})
                        df_m['Categoria_NIIF18'] = auto_classify_niif18_series(df_m)
                        st.session_state['df_balanza'] = df_m
                        st.session_state['df_clasificado'] = df_m
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
                
        if 'df_balanza' in st.session_state and st.session_state['df_balanza'] is not None:
            st.divider()
            c_inf1, c_inf2, c_inf3 = st.columns(3)
            c_inf1.metric("Archivo Procesado", st.session_state.get('fuente_origen', 'Balanza'))
            c_inf2.metric("Total Registros Contables", f"{len(st.session_state['df_balanza']):,} cuentas")
            st_val = float(st.session_state['df_balanza']['Saldo'].sum())
            c_inf3.metric("Balance de Comprobación", f"$ {st_val:,.2f}", delta="Cuadre Perfecto" if abs(st_val) < 0.01 else "Neto en Libros")
            st.markdown("#### Previsualización Estandarizada")
            st.dataframe(st.session_state['df_balanza'][['Cuenta', 'Descripcion', 'Saldo']], width="stretch", height=300)

    # ----------------- FASE 2: Matriz -----------------
    with tabs[1]:
        st.subheader("Matriz de Asignación de Categorías NIIF 18")
        if 'df_balanza' in st.session_state and st.session_state['df_balanza'] is not None:
            df_reclass = st.session_state.get('df_clasificado', st.session_state['df_balanza']).copy()
            if 'Categoria_NIIF18' not in df_reclass.columns:
                df_reclass['Categoria_NIIF18'] = auto_classify_niif18_series(df_reclass)
            c_m1, c_m2 = st.columns([3, 1])
            with c_m2:
                if st.button("✨ Re-aplicar Auto-Clasificación", width="stretch"):
                    df_reclass['Categoria_NIIF18'] = auto_classify_niif18_series(df_reclass)
                    st.session_state['df_clasificado'] = df_reclass
                    st.rerun()
            v_key = st.session_state.get('uploader_version', 0)
            edited_df = st.data_editor(
                df_reclass,
                column_config={"Categoria_NIIF18": st.column_config.SelectboxColumn("Clasificación NIIF 18", options=CATEGORIAS_NIIF18, required=True)},
                width="stretch", height=420, key=f"editor_matriz_{v_key}"
            )
            st.session_state['df_clasificado'] = edited_df
        else:
            st.info("ℹ️ No hay datos para clasificar. Realice la carga en la pestaña 1 (Ingesta).")

    # ----------------- FASE 3: Árbol EEFF -----------------
    with tabs[2]:
        st.subheader("Árbol de Rendimiento Estructurado")
        if 'df_clasificado' in st.session_state and st.session_state['df_clasificado'] is not None:
            df_c = st.session_state['df_clasificado'].copy()
            df_c['PL_Neto'] = df_c.apply(calculate_pl_contribution, axis=1)
            v_op = float(df_c[df_c['Categoria_NIIF18'].str.startswith('1.')]['PL_Neto'].sum())
            v_inv = float(df_c[df_c['Categoria_NIIF18'].str.startswith('2.')]['PL_Neto'].sum())
            v_fin = float(df_c[df_c['Categoria_NIIF18'].str.startswith('3.')]['PL_Neto'].sum())
            v_imp = float(df_c[df_c['Categoria_NIIF18'].str.startswith('4.')]['PL_Neto'].sum())
            v_disc = float(df_c[df_c['Categoria_NIIF18'].str.startswith('5.')]['PL_Neto'].sum())
            sub_1, sub_2, sub_3 = v_op, v_op + v_inv, v_op + v_inv + v_fin + v_imp + v_disc
            
            st.markdown("### Subtotales Mandatorios (Cálculo en Vivo)")
            c1, c2, c3 = st.columns(3)
            c1.metric("1. Resultado Operativo", f"$ {sub_1:,.2f}")
            c2.metric("2. Antes de Fin. e Imptos", f"$ {sub_2:,.2f}")
            c3.metric("3. Resultado del Periodo", f"$ {sub_3:,.2f}")
            st.divider()
            st.markdown("#### Análisis Gráfico de Subtotales")
            chart_df = pd.DataFrame({"Subtotal": ["1. Operativo", "2. Pre-Fin/Imp", "3. Periodo Neto"], "Monto ($)": [sub_1, sub_2, sub_3]}).set_index("Subtotal")
            st.bar_chart(chart_df, width="stretch")
            st.divider()
            with st.expander("Ver desglose operativo (Categoría 1)", expanded=True):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('1.')][['Cuenta', 'Descripcion', 'Saldo', 'PL_Neto']], width="stretch")
            with st.expander("Ver desglose de inversión (Categoría 2)", expanded=False):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('2.')][['Cuenta', 'Descripcion', 'Saldo', 'PL_Neto']], width="stretch")
            with st.expander("Ver desglose de financiación (Categoría 3)", expanded=False):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('3.')][['Cuenta', 'Descripcion', 'Saldo', 'PL_Neto']], width="stretch")
            with st.expander("Ver cuentas excluidas de Balance General (Categoría 0)", expanded=False):
                st.dataframe(df_c[df_c['Categoria_NIIF18'].str.startswith('0.')][['Cuenta', 'Descripcion', 'Saldo']], width="stretch")
        else:
            st.info("ℹ️ No hay estados financieros generados. Cargue y clasifique su balance en las fases 1 y 2.")

    # ----------------- FASE 4: MPMs -----------------
    with tabs[3]:
        st.subheader("Medidas de Rendimiento Definidas por la Gerencia (MPM)")
        c_form, c_table = st.columns([1, 1.5])
        with c_form:
            plantilla = st.selectbox("Seleccionar Plantilla MPM:", ["EBITDA Ajustado", "Resultado Operativo Normalizado", "Personalizado"])
            p_nombres = {"EBITDA Ajustado": "EBITDA Ajustado", "Resultado Operativo Normalizado": "Resultado Operativo Normalizado", "Personalizado": ""}
            p_ajustes = {"EBITDA Ajustado": 50000.0, "Resultado Operativo Normalizado": 35000.0, "Personalizado": 0.0}
            p_justif = {
                "EBITDA Ajustado": "Exclusión de costos no recurrentes de reestructuración para reflejar el desempeño operativo recurrente.",
                "Resultado Operativo Normalizado": "Ajuste por contingencias legales atípicas de ejercicios anteriores.",
                "Personalizado": ""
            }
            with st.form("mpm_form"):
                st.markdown("**Registrar Nueva MPM**")
                mpm_name = st.text_input("Denominación MPM", value=p_nombres[plantilla], placeholder="ej. EBITDA Ajustado")
                subtotal_base = st.selectbox("Subtotal NIIF 18 de Anclaje", ["1. Resultado Operativo", "3. Resultado del Periodo"])
                ajuste = st.number_input("Monto del Ajuste (+/-)", value=p_ajustes[plantilla])
                rationale = st.text_area("Justificación / Nota Explicativa", value=p_justif[plantilla], placeholder="Indique la justificación para los inversionistas...")
                if st.form_submit_button("Validar e Incluir"):
                    if mpm_name.strip():
                        val_base = 0.0
                        if 'df_clasificado' in st.session_state and st.session_state['df_clasificado'] is not None:
                            df_calc = st.session_state['df_clasificado'].copy()
                            df_calc['PL_Neto'] = df_calc.apply(calculate_pl_contribution, axis=1)
                            val_base = float(df_calc[df_calc['Categoria_NIIF18'].str.startswith('1.')]['PL_Neto'].sum()) if "1. Resultado Operativo" in subtotal_base else float(df_calc['PL_Neto'].sum())
                        if 'mpm_records' not in st.session_state:
                            st.session_state['mpm_records'] = []
                        st.session_state['mpm_records'].append({
                            "Métrica": mpm_name, "Anclaje NIIF": subtotal_base, "Base NIIF ($)": f"{val_base:,.2f}",
                            "Ajuste ($)": f"{ajuste:,.2f}", "Efecto Fiscal ($)": f"{-(ajuste * 0.25):,.2f}",
                            "Total MPM ($)": f"{(val_base + ajuste):,.2f}", "Justificación": rationale
                        })
                        st.success(f"✅ Medida '{mpm_name}' validada y registrada.")
                        st.rerun()
                    else:
                        st.error("Ingrese una denominación para la MPM.")
        with c_table:
            st.markdown("**Tabla de Conciliación Auditada (Nota NIIF 18)**")
            if 'mpm_records' in st.session_state and st.session_state['mpm_records']:
                st.dataframe(pd.DataFrame(st.session_state['mpm_records']), width="stretch")
                if st.button("🗑️ Limpiar MPMs"):
                    st.session_state['mpm_records'] = []
                    st.rerun()
            else:
                st.info("ℹ️ No hay MPMs registradas. Seleccione una plantilla a la izquierda y presione 'Validar e Incluir'.")

    # ----------------- FASE 5: Exportación -----------------
    with tabs[4]:
        st.subheader("Centro de Exportación Regulatoria")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            if 'df_clasificado' in st.session_state and st.session_state['df_clasificado'] is not None:
                st.download_button("📥 Descargar Mapeo y Trazabilidad (CSV)", data=st.session_state['df_clasificado'].to_csv(index=False).encode('utf-8'), file_name="mapeo_niif18.csv", mime="text/csv", width="stretch")
            else:
                st.button("📥 Descargar Mapeo y Trazabilidad (CSV)", disabled=True, width="stretch")
        with col_dl2:
            if 'df_clasificado' in st.session_state and st.session_state['df_clasificado'] is not None:
                excel_data = rep_svc.generar_excel_estado_resultados(st.session_state['df_clasificado'])
                st.download_button(
                    label="📥 Descargar Estado de Resultados (Excel)", 
                    data=excel_data, 
                    file_name="estado_resultados_niif18.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    width="stretch"
                )
            else:
                st.button("📥 Descargar Estado de Resultados (Excel)", disabled=True, width="stretch")

    # ----------------- FASE 6: Visor Doctrinal Saneado (INV-019) -----------------
    with tabs[5]:
        st.subheader("Consulta del Marco Teórico IASB")
        doctrinas_dir = "docs/biblioteca_doctrinal"
        if os.path.exists(doctrinas_dir):
            archivos = sorted(os.listdir(doctrinas_dir))
            sel_file = st.selectbox(
                "Seleccione el volumen doctrinal a consultar:", 
                archivos, 
                format_func=lambda x: TITULOS_DOCTRINALES.get(x, x.replace(".md", "").replace("_", " ").title())
            )
            if sel_file:
                with open(os.path.join(doctrinas_dir, sel_file), 'r', encoding='utf-8') as f:
                    content_clean = re.sub(r'\[[¤¦][^\]]*\]', '', f.read()).strip()
                    st.markdown(f"---\n{content_clean}")
        else:
            st.error("No se encontró la biblioteca doctrinal.")

if __name__ == "__main__":
    main()
