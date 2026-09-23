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
