from sala_auditoria import _service as aud_svc


def test_registrar_cambio_agrega_sin_mutar_registros_previos():
    bitacora = []
    aud_svc.registrar_cambio(bitacora, "ana", "100000", "1. Operación (Ingresos / Gastos Operativos)", "2. Inversión (Ingresos / Gastos por Inversiones)", "corrección")
    assert len(bitacora) == 1
    assert bitacora[0]["cuenta_codigo"] == "100000"
    assert bitacora[0]["categoria_anterior"] == "1. Operación (Ingresos / Gastos Operativos)"
    aud_svc.registrar_cambio(bitacora, "ana", "110000", "1. Operación (Ingresos / Gastos Operativos)", "1. Operación (Ingresos / Gastos Operativos)", "sin cambio real")
    assert len(bitacora) == 1  # no se registra si la categoría no cambió


def test_obtener_bitacora_devuelve_copia_no_la_lista_original():
    bitacora = []
    aud_svc.registrar_cambio(bitacora, "ana", "100000", "A", "B")
    copia = aud_svc.obtener_bitacora(bitacora)
    copia.append({"inyectado": True})
    assert len(bitacora) == 1  # la lista original (append-only) no se vio afectada
