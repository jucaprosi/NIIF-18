"""
Verifica la caché en disco (.parquet) de sala_entidad.cargar_directorio
(TASKS.md ¤optimizar_carga_directorio_scvs), sin depender del xlsx real de 227k filas.
"""
import os
import time
import pandas as pd
from sala_entidad import _service as ent_svc


def _crear_xlsx_directorio_falso(path):
    filas_metadata = pd.DataFrame([[None], [None], [None], [None]])
    encabezado = pd.DataFrame([["RUC", "NOMBRE", "SITUACIÓN LEGAL", "CIIU NIVEL 1", "CIIU NIVEL 6"]])
    datos = pd.DataFrame([["1790013731001", "EMPRESA DE PRUEBA", "ACTIVA", "K", "K6419.01"]])
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.concat([filas_metadata, encabezado, datos], ignore_index=True).to_excel(
            writer, index=False, header=False
        )


def test_cargar_directorio_genera_y_reutiliza_cache_parquet(tmp_path, monkeypatch):
    xlsx_path = str(tmp_path / "directorio_falso.xlsx")
    parquet_path = str(tmp_path / "directorio_falso.parquet")
    _crear_xlsx_directorio_falso(xlsx_path)

    assert not os.path.exists(parquet_path)
    df1 = ent_svc.cargar_directorio(xlsx_path)
    assert os.path.exists(parquet_path), "Debe generar la caché .parquet en la primera carga"
    assert len(df1) == 1
    assert df1.iloc[0]["RUC"] == "1790013731001"

    # Segunda carga: no debe volver a parsear el xlsx (la señal de rendimiento real).
    # Se verifica haciendo que pd.read_excel explote si se invoca de nuevo.
    def _read_excel_no_debe_llamarse(*args, **kwargs):
        raise AssertionError("cargar_directorio no debió releer el xlsx teniendo un .parquet vigente")
    monkeypatch.setattr(ent_svc.pd, "read_excel", _read_excel_no_debe_llamarse)

    df2 = ent_svc.cargar_directorio(xlsx_path)
    assert df2 is not None
    assert df2.iloc[0]["RUC"] == "1790013731001"


def test_cargar_directorio_regenera_cache_si_xlsx_es_mas_reciente(tmp_path):
    xlsx_path = str(tmp_path / "directorio_falso2.xlsx")
    parquet_path = str(tmp_path / "directorio_falso2.parquet")
    _crear_xlsx_directorio_falso(xlsx_path)
    ent_svc.cargar_directorio(xlsx_path)
    assert os.path.exists(parquet_path)

    # Simula un snapshot xlsx actualizado (mtime más reciente que el .parquet existente).
    time.sleep(0.05)
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        pd.concat([
            pd.DataFrame([[None], [None], [None], [None]]),
            pd.DataFrame([["RUC", "NOMBRE", "SITUACIÓN LEGAL", "CIIU NIVEL 1", "CIIU NIVEL 6"]]),
            pd.DataFrame([["9999999999999", "EMPRESA ACTUALIZADA", "ACTIVA", "L", "L6810.01"]]),
        ], ignore_index=True).to_excel(writer, index=False, header=False)

    df = ent_svc.cargar_directorio(xlsx_path)
    assert df.iloc[0]["RUC"] == "9999999999999", "Debe regenerar la caché cuando el xlsx cambia"
