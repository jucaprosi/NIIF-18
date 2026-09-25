"""
Verifica `sala_importacion.extraer_tabla_de_pdf` con PDFs sintéticos generados con
`reportlab` (dependencia de test únicamente, ver requirements.txt) -- no con archivos
reales del propietario, porque este proyecto no tiene todavía un PDF de balanza real
de ejemplo (a diferencia de `balance_prueba_niif18_sap_business_one.xlsx`).
"""
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sala_importacion import _service as imp_svc


def _pdf_con_tabla_real():
    # pdfplumber detecta tablas por las líneas de grilla dibujadas en el PDF (su
    # estrategia por defecto es "lines"), no solo por el texto -- un `Table` de
    # reportlab sin `TableStyle` con `GRID` no pinta ninguna línea, así que
    # pdfplumber no vería ninguna tabla aunque el texto sí sea perfectamente
    # extraíble. Se agrega el grid explícito para que la tabla sea detectable.
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    datos = [
        ["Codigo", "Nombre", "Saldo"],
        ["1.1.01.001", "Caja general", "180000.00"],
        ["1.1.01.002", "Banco cuenta corriente", "420000.00"],
        ["2.1.01.001", "Proveedores nacionales", "-630000.00"],
    ]
    tabla = Table(datos)
    tabla.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    doc.build([tabla])
    buffer.seek(0)
    return buffer


def _pdf_sin_texto_solo_imagen():
    # Simula un escaneo/foto: una página con un rectángulo dibujado (contenido gráfico
    # rasterizado en espíritu, sin ninguna operación de texto) -- pdfplumber no extrae
    # ningún carácter de esto, igual que de una imagen escaneada real sin OCR.
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.rect(1 * inch, 1 * inch, 4 * inch, 4 * inch, fill=1)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def test_extraer_tabla_de_pdf_con_tabla_real_devuelve_dataframe():
    df, motivos = imp_svc.extraer_tabla_de_pdf(_pdf_con_tabla_real())
    assert motivos == []
    assert df is not None
    assert list(df.columns) == ["Codigo", "Nombre", "Saldo"]
    assert len(df) == 3
    assert df.iloc[0]["Codigo"] == "1.1.01.001"


def test_extraer_tabla_de_pdf_rechaza_pdf_sin_texto_extraible():
    df, motivos = imp_svc.extraer_tabla_de_pdf(_pdf_sin_texto_solo_imagen())
    assert df is None
    assert motivos
    assert "escaneo" in motivos[0].lower() or "foto" in motivos[0].lower()


def test_extraer_tabla_de_pdf_luego_pasa_por_el_mismo_pipeline_de_inferencia():
    # El DataFrame crudo de un PDF debe ser indistinguible, para el resto del pipeline,
    # de uno leído de Excel/CSV -- se reusa infer_columns_by_mathematical_weights sin
    # ningún camino especial para PDF.
    df_crudo, _ = imp_svc.extraer_tabla_de_pdf(_pdf_con_tabla_real())
    cta, desc, saldo, confianza = imp_svc.infer_columns_by_mathematical_weights(df_crudo)
    assert cta == "Codigo"
    assert saldo == "Saldo"
    df_bal = imp_svc.construir_balanza_estandar(df_crudo, cta, desc, saldo)
    assert list(df_bal.columns) == ["Cuenta", "Descripcion", "Saldo"]
    assert df_bal.iloc[0]["Saldo"] == 180000.0
