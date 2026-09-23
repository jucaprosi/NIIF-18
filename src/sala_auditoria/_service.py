"""
Compuerta _service.py para sala_auditoria.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-10, sala antes propuesta en TASKS.md ¤sala_auditoria_nueva):
registro de cada cambio de clasificación (quién, cuándo, categoría anterior/nueva,
justificación). Append-only: este módulo no expone ninguna función de edición o borrado
de un registro ya escrito — solo `registrar_cambio` (agrega) y `obtener_bitacora` (lee).

Persistencia (MVP): vive en `st.session_state`, inyectado por quien llama — este módulo
es agnóstico de Streamlit (no lo importa) para mantenerlo testeable sin un `AppTest`.
Cuando exista persistencia real entre sesiones, esta compuerta es el único punto que
debe cambiar (ver PRD.md §6, invariante de auditabilidad).
"""
from datetime import datetime, timezone

__all__ = ["registrar_cambio", "obtener_bitacora"]


# ¤sala_auditoria
def registrar_cambio(bitacora, usuario, cuenta_codigo, categoria_anterior, categoria_nueva, justificacion=""):
    """Agrega un registro append-only a `bitacora` (lista) y la devuelve.

    No modifica ni elimina registros existentes — solo agrega al final.
    """
    if categoria_anterior == categoria_nueva:
        return bitacora
    bitacora.append({
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "usuario": usuario,
        "cuenta_codigo": cuenta_codigo,
        "categoria_anterior": categoria_anterior,
        "categoria_nueva": categoria_nueva,
        "justificacion": justificacion,
    })
    return bitacora


def obtener_bitacora(bitacora):
    """Devuelve una copia de solo lectura de la bitácora (nunca la lista original)."""
    return list(bitacora)
