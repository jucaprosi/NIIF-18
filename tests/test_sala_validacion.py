import pandas as pd
from sala_validacion import _service as val_svc


def test_balanza_cuadrada_dentro_de_tolerancia():
    assert val_svc.balanza_cuadrada(0.0) is True
    assert val_svc.balanza_cuadrada(0.005) is True
    assert val_svc.balanza_cuadrada(1.0) is False


def test_contar_cuentas_pendientes():
    df = pd.DataFrame({"Categoria_NIIF18": ["1. Operación", "CATEGORIA_INVALIDA", None]})
    assert val_svc.contar_cuentas_pendientes(df, ["1. Operación"]) == 2


def test_puede_exportar_bloquea_si_no_cuadra():
    df = pd.DataFrame({
        "Saldo": [100.0, -50.0],
        "Categoria_NIIF18": ["1. Operación"] * 2,
    })
    ok, motivos = val_svc.puede_exportar(df, ["1. Operación"])
    assert ok is False
    assert len(motivos) == 1
    assert "no cuadra" in motivos[0]


def test_puede_exportar_bloquea_si_hay_pendientes():
    df = pd.DataFrame({
        "Saldo": [100.0, -100.0],
        "Categoria_NIIF18": ["1. Operación", "CATEGORIA_INVALIDA"],
    })
    ok, motivos = val_svc.puede_exportar(df, ["1. Operación"])
    assert ok is False
    assert "1 cuenta" in motivos[0]


def test_puede_exportar_permite_si_todo_esta_bien():
    df = pd.DataFrame({
        "Saldo": [100.0, -100.0],
        "Categoria_NIIF18": ["1. Operación"] * 2,
    })
    ok, motivos = val_svc.puede_exportar(df, ["1. Operación"])
    assert ok is True
    assert motivos == []
