import os
import tempfile
from unittest.mock import patch, Mock
import pandas as pd
import requests
from sala_entidad import _service as ent_svc


def test_sugerir_actividad_principal_seccion_k_es_financiacion():
    sug = ent_svc.sugerir_actividad_principal("K")
    assert sug["financiacion_es_actividad_principal"] is True
    assert sug["inversion_es_actividad_principal"] is False
    assert sug["origen_actividad_principal"] == "sugerido_ciiu"
    assert "no usar en producción" in sug["advertencia"].lower()


def test_sugerir_actividad_principal_seccion_no_mapeada_no_sugiere_nada():
    sug = ent_svc.sugerir_actividad_principal("C")
    assert sug["financiacion_es_actividad_principal"] is False
    assert sug["inversion_es_actividad_principal"] is False


def test_buscar_entidad_por_ruc_sin_directorio_cargado_devuelve_none():
    assert ent_svc.buscar_entidad_por_ruc(None, "1790013731001") is None


def test_resolver_ciiu_sin_catalogo_cargado_devuelve_none():
    assert ent_svc.resolver_descripcion_ciiu(None, "A") is None


def test_actualizar_snapshot_directorio_exito_reemplaza_archivo():
    with tempfile.TemporaryDirectory() as tmp:
        destino = os.path.join(tmp, "directorio.xlsx")
        with open(destino, "wb") as f:
            f.write(b"contenido viejo")
        respuesta_mock = Mock(content=b"contenido nuevo descargado")
        respuesta_mock.raise_for_status = Mock()
        with patch("sala_entidad._service.requests.get", return_value=respuesta_mock):
            actualizado, motivo = ent_svc.actualizar_snapshot_directorio(destino, url="https://ejemplo.test/x.xlsx")
        assert actualizado is True
        assert "actualizado en vivo" in motivo.lower()
        with open(destino, "rb") as f:
            assert f.read() == b"contenido nuevo descargado"


def test_actualizar_snapshot_directorio_falla_conserva_archivo_existente():
    # Caso real: sin red, timeout, o sitio caído -- el snapshot local existente no debe
    # perderse ni corromperse (PRD.md §6, disponibilidad offline).
    with tempfile.TemporaryDirectory() as tmp:
        destino = os.path.join(tmp, "directorio.xlsx")
        with open(destino, "wb") as f:
            f.write(b"contenido original intacto")
        with patch("sala_entidad._service.requests.get", side_effect=requests.exceptions.ConnectionError("sin red")):
            actualizado, motivo = ent_svc.actualizar_snapshot_directorio(destino, url="https://ejemplo.test/x.xlsx")
        assert actualizado is False
        assert "no se pudo actualizar" in motivo.lower()
        with open(destino, "rb") as f:
            assert f.read() == b"contenido original intacto"
        assert not os.path.exists(destino + ".tmp_descarga")


def _respuesta_sri(payload):
    m = Mock()
    m.raise_for_status = Mock()
    m.json = Mock(return_value=payload)
    return m


def test_buscar_entidad_ruc_sri_exito():
    payload = [{
        "numeroRuc": "1790013731001",
        "razonSocial": "ACEITES TROPICALES S. A. ATSA",
        "estadoContribuyenteRuc": "ACTIVO",
        "actividadEconomicaPrincipal": "CULTIVO DE PALMAS DE ACEITE (PALMA AFRICANA).",
        "tipoContribuyente": "SOCIEDAD",
        "obligadoLlevarContabilidad": "SI",
    }]
    with patch("sala_entidad._service.requests.get", return_value=_respuesta_sri(payload)):
        r = ent_svc.buscar_entidad_ruc_sri("1790013731001")
    assert r["razon_social"] == "ACEITES TROPICALES S. A. ATSA"
    assert r["estado"] == "ACTIVO"
    assert r["fuente"] == "consulta_en_vivo_sri"
    assert "PALMAS" in r["actividad_economica_texto"]


def test_buscar_entidad_ruc_sri_no_encontrado_devuelve_none():
    with patch("sala_entidad._service.requests.get", return_value=_respuesta_sri([])):
        assert ent_svc.buscar_entidad_ruc_sri("0000000000000") is None


def test_buscar_entidad_ruc_sri_falla_de_red_devuelve_none():
    with patch("sala_entidad._service.requests.get", side_effect=requests.exceptions.Timeout("timeout")):
        assert ent_svc.buscar_entidad_ruc_sri("1790013731001") is None


def test_buscar_entidad_ruc_sri_ruc_vacio_devuelve_none():
    assert ent_svc.buscar_entidad_ruc_sri("") is None


def _catalogo_ciiu_prueba():
    return pd.DataFrame([
        {"CODIGO": "K", "DESCRIPCION": "ACTIVIDADES FINANCIERAS Y DE SEGUROS.", "NIVEL": 1},
        {"CODIGO": "K641", "DESCRIPCION": "INTERMEDIACIÓN MONETARIA.", "NIVEL": 3},
        {"CODIGO": "A", "DESCRIPCION": "AGRICULTURA, GANADERÍA, SILVICULTURA Y PESCA.", "NIVEL": 1},
        {"CODIGO": "A0126.01", "DESCRIPCION": "Cultivo de palmas de aceite (palma africana).", "NIVEL": 5},
    ])


def test_inferir_ciiu_por_texto_encuentra_mejor_match_nivel_especifico():
    # El texto del SRI para un banco matchea mejor contra la descripción específica
    # ("Intermediación monetaria") que contra la genérica de nivel 1 ("Actividades
    # financieras y de seguros") -- por eso nivel_minimo excluye nivel 1 por defecto.
    r = ent_svc.inferir_ciiu_por_texto(
        "ACTIVIDADES DE INTERMEDIACIÓN MONETARIA REALIZADA POR LA BANCA COMERCIAL.",
        _catalogo_ciiu_prueba(),
    )
    assert r["codigo_ciiu"] == "K641"
    assert r["ciiu_nivel_1"] == "K"
    assert r["score_confianza"] > 0


def test_inferir_ciiu_por_texto_sin_coincidencia_devuelve_none():
    r = ent_svc.inferir_ciiu_por_texto("XYZQWERTY SIN RELACION ALGUNA", _catalogo_ciiu_prueba())
    assert r is None


def test_inferir_ciiu_por_texto_sin_catalogo_devuelve_none():
    assert ent_svc.inferir_ciiu_por_texto("cualquier texto", None) is None


def test_inferir_ciiu_por_texto_vacio_devuelve_none():
    assert ent_svc.inferir_ciiu_por_texto("", _catalogo_ciiu_prueba()) is None
