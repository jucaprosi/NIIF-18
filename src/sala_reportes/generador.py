import io
import pandas as pd

# ¤sala_reportes
def generar_excel_estado_resultados(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estado_Resultados_NIIF18')
    return output.getvalue()
