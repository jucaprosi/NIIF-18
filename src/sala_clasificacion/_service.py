"""
Compuerta _service.py para sala_clasificacion.
[¤vocabulario_precision_agentica]

Responsabilidad (PRD.md RF-02, RF-03): motor de clasificación jerárquica. Implementa
el árbol de decisión normativo de PRD.md §3, en el orden ahí especificado — no la
heurística plana que tenía antes `auto_classify_niif18_series` en src/app.py.

Reestructuración (no parche): la versión anterior evaluaba reglas en un orden
arbitrario y no recibía `ConfiguracionEntidad`. Esta versión sigue el árbol §3 paso a
paso y expone `financiacion_es_actividad_principal` / `inversion_es_actividad_principal`
como parámetros explícitos (ver PRD.md RF-11), en vez de ignorarlos.

Limitación conocida (heredada, señalada en PRD.md §8): la detección de cada paso sigue
basada en palabras clave y prefijos de código de cuenta, no en un catálogo contable
tipado. Debe validarse contra el texto oficial de NIIF 18 antes de producción
(TASKS.md ¤fuentes_iasb_oficial).
"""
from sala_catalogo import _service as cat_svc

__all__ = ["clasificar_partida", "clasificar_dataframe"]

# Fuente única de los nombres de categoría: `sala_catalogo` (compuerta oficial del
# catálogo NIIF 18, PRD.md RF-02). Antes esta sala redefinía los mismos literales por su
# cuenta -- riesgo de que un cambio de nombre (p. ej. el renombrado corto de 2026-09-23)
# se aplicara en un archivo y no en el otro. Ahora se derivan por posición de
# `cat_svc.CATEGORIAS_NIIF18`, que es la única lista que se edita para renombrar.
CATEGORIA_BALANCE_GENERAL = cat_svc.CATEGORIA_BALANCE_GENERAL
CATEGORIA_OPERACION = cat_svc.CATEGORIAS_NIIF18[1]
CATEGORIA_INVERSION = cat_svc.CATEGORIAS_NIIF18[2]
CATEGORIA_FINANCIACION = cat_svc.CATEGORIAS_NIIF18[3]
CATEGORIA_IMPUESTOS = cat_svc.CATEGORIAS_NIIF18[4]
CATEGORIA_DISCONTINUADAS = cat_svc.CATEGORIAS_NIIF18[5]

_PALABRAS_BALANCE = (
    'activo', 'pasivo', 'patrimonio', 'capital', 'bancos', 'caja', 'proveedor',
    'cliente', 'inventario', 'edificio', 'terreno', 'obligacion', 'cuenta por',
)
# Palabras que, si aparecen en la descripción, indican que la partida es un movimiento
# de resultados (P&L) aunque también mencione un sustantivo de balance (p. ej. "interés
# neto de pasivo por beneficios definidos" es gasto financiero, no una cuenta de
# balance). Sin esta lista, el prefiltro de Categoría 0 producía falsos positivos sobre
# gastos que solo *referencian* activo/pasivo/patrimonio en su descripción — detectado
# por tests/test_sala_clasificacion.py::test_interes_de_pension_sin_actividad_principal_configurada.
_PALABRAS_MOVIMIENTO_PL = (
    'ingreso', 'gasto', 'costo', 'interes', 'interés', 'depreciaci', 'amortizaci',
    'comisi', 'provisi', 'perdida', 'pérdida', 'deterioro', 'dividendo', 'ganancia',
)
_PALABRAS_IMPUESTO = ('impuesto a la renta', 'impuesto a las ganancias', 'gasto por impuesto', 'impuesto diferido')
_PALABRAS_DISCONTINUADA = ('discontinuad', 'interrumpid', 'abandonad')
_PALABRAS_FINANCIACION = ('prestamo', 'préstamo', 'bono', 'obligacion financiera', 'obligación financiera', 'arrendamiento financiero', 'deuda')
_PALABRAS_INVERSION = ('inversion', 'inversión', 'asociada', 'negocio conjunto', 'participacion', 'participación', 'propiedad de inversion', 'propiedad de inversión', 'instrumento de deuda')
# Interés de arrendamiento o de beneficios a empleados (pensiones): según el Public
# Statement de ESMA sobre IFRS 18 (17-feb-2026, p. 4 — autoridad europea, ver
# FUENTES_Y_BIBLIOGRAFIA.md), incluso una entidad cuya actividad principal es financiar
# a clientes (p. ej. un banco) debe seguir clasificando ESTE interés en FINANCIACION —
# la excepción de actividad principal (paso 5) solo mueve a OPERACION el interés que
# proviene de "transacciones que involucran obtención de fondos" (préstamos/bonos), no
# el de arrendamientos ni de pasivos por beneficios definidos.
_PALABRAS_INTERES_SIEMPRE_FINANCIACION = ('arrendamiento', 'pension', 'pensión', 'beneficios definidos', 'beneficio definido')
# Resultado por método de participación (asociadas, negocios conjuntos): la plantilla
# FINREP oficial F 02.00 bajo IFRS 18 (fila 74, "Share of profit/loss of investments...
# equity method", citando Anexo V.Parte 2.54 — EBA/Op/2026/07, 8-jul-2026, ver
# FUENTES_Y_BIBLIOGRAFIA.md y PRD.md §11.4) la presenta como línea propia dentro de
# Inversión, inmediatamente después del Resultado Operativo — nunca dentro de Operación.
# A diferencia del interés/dividendo de inversión (que sí puede moverse a OPERACION si
# invertir es la actividad principal declarada, Paso 5), el método de participación no
# tiene esa excepción: confirma con fuente oficial lo que antes solo tenía el respaldo
# de la nota de auto-corrección de IFRS-Converter (PRD.md, antes ¤excepcion_metodo_
# participacion_pendiente).
_PALABRAS_METODO_PARTICIPACION = ('asociada', 'negocio conjunto', 'metodo de participacion', 'método de participación')


# ¤sala_clasificacion ¤arbol_clasificacion ¤configuracion_entidad
def clasificar_partida(cuenta, descripcion, saldo, financiacion_es_actividad_principal=False, inversion_es_actividad_principal=False):
    """Árbol de decisión de clasificación NIIF 18 — PRD.md §3, en su orden normativo."""
    cta = str(cuenta).strip()
    desc = str(descripcion).strip().lower()
    saldo = float(saldo)

    # Paso 0 (filtro previo de la app, no un paso del árbol NIIF 18 en sí — ver PRD.md
    # §2.1): partidas de Balance General que no son ingreso/gasto no entran al Estado de
    # Resultados y por tanto no participan del árbol de clasificación.
    #
    # Dos señales distintas, con distinta fuerza probatoria — no deben tratarse igual:
    #   (a) el CÓDIGO de cuenta empieza con 1/2/3: en un plan de cuentas estándar (el de
    #       este proyecto y el de SAP Business One usado en el archivo de prueba) esto es
    #       la convención MÁS confiable de todas -- 1=activo, 2=pasivo, 3=patrimonio,
    #       4=ingreso, 5=gasto. No debe revertirse por palabras de la descripción.
    #   (b) la DESCRIPCIÓN contiene una palabra de balance (p. ej. "pasivo"): señal débil
    #       y ambigua -- una cuenta de gasto real puede *mencionar* "pasivo" en su nombre
    #       ("Interés neto de pasivo por beneficios definidos" es GASTO, no balance). Por
    #       eso existe `_PALABRAS_MOVIMIENTO_PL` como rescate.
    #
    # Detectado en esta sesión contra datos reales (`TB_ERP` del archivo de prueba): el
    # rescate por `_PALABRAS_MOVIMIENTO_PL` se aplicaba también cuando el disparador era
    # (a), no solo (b) -- eso dejaba pasar al Estado de Resultados cuentas de balance
    # legítimas cuyo nombre usa vocabulario de flujo por convención contable ("Depreciación
    # acumulada de edificios/maquinaria", "Deterioro acumulado de cartera", "Provisión por
    # litigios" -- todas cuentas 1.x/2.x, el saldo ACUMULADO, no el movimiento del período,
    # que ya tiene su propia cuenta de gasto separada, p. ej. "Depreciación edificios"
    # 5.2.03.001). Esto inflaba/desinflaba el resultado operativo en $690,000 sobre la
    # balanza de prueba real -- exactamente la brecha entre el resultado del motor y el
    # de `ER_NIIF18` (ver TASKS.md ¤discrepancia_motor_tb_erp_pendiente). El rescate por
    # palabra clave ahora solo aplica cuando el disparador fue (b), nunca cuando fue (a).
    _por_codigo = cta.startswith(('1', '2', '3'))
    _por_palabra_balance = any(w in desc for w in _PALABRAS_BALANCE)
    if _por_codigo or _por_palabra_balance:
        if _por_codigo or not any(w in desc for w in _PALABRAS_MOVIMIENTO_PL):
            return CATEGORIA_BALANCE_GENERAL

    # Paso 1: ¿Es impuesto a la renta?
    if cta.startswith(('55', '59')) or any(w in desc for w in _PALABRAS_IMPUESTO):
        return CATEGORIA_IMPUESTOS

    # Paso 2: ¿Pertenece a una operación discontinuada?
    if any(w in desc for w in _PALABRAS_DISCONTINUADA):
        return CATEGORIA_DISCONTINUADAS

    es_dividendo = 'dividendo' in desc
    es_interes = 'interes' in desc or 'interés' in desc

    # Corrección normativa (2026-09-22, validada contra el Project Summary oficial del
    # IASB para IFRS 18, abril 2024, p. 6-7 — fuente gratuita del propio IASB, ver
    # FUENTES_Y_BIBLIOGRAFIA.md): un dividendo PAGADO a los accionistas no es una
    # partida del Estado de Resultados en absoluto — se reconoce directamente en el
    # Estado de Cambios en el Patrimonio (reduce utilidades retenidas), no como gasto.
    # La versión anterior de este árbol (heredada de fuentes secundarias, PRD.md §8)
    # lo forzaba a FINANCIACION "sin excepción", confundiendo la regla del Estado de
    # Flujos de Efectivo (donde IFRS 18 sí clasifica los dividendos pagados como
    # actividad de financiación, p. 14) con la del Estado de Resultados, que son
    # estados distintos. Si una cuenta de "dividendo" tiene saldo deudor (pagado), no
    # participa del Estado de Resultados.
    if es_dividendo and saldo > 0:
        return CATEGORIA_BALANCE_GENERAL

    # Paso 3: ¿Es financiación general? (préstamos, bonos, interés neto de beneficios
    # definidos — el Project Summary oficial, p. 7, confirma que la categoría de
    # financiación incluye "gastos por interés de TODOS los pasivos", sin excepción).
    candidato = None
    if not es_interes and (cta.startswith(('54', '6')) or any(w in desc for w in _PALABRAS_FINANCIACION)):
        candidato = CATEGORIA_FINANCIACION
    # Paso 4: ¿Es rendimiento de método de participación o de un activo con retorno
    # independiente de los demás recursos de la entidad? El Project Summary oficial
    # (p. 6) incluye explícitamente "dividendos de acciones en otras compañías" e
    # "ingresos de efectivo y equivalentes" dentro de Inversión.
    elif any(w in desc for w in _PALABRAS_INVERSION):
        candidato = CATEGORIA_INVERSION
    elif es_interes:
        # Gasto por interés (saldo > 0, pagado) -> FINANCIACION siempre (p. 7: "interés
        # de CUALQUIER pasivo"). Ingreso por interés (saldo < 0, recibido) -> INVERSION
        # por defecto (p. 6: rendimiento de efectivo/equivalentes), salvo excepción de
        # actividad principal (Paso 5).
        candidato = CATEGORIA_INVERSION if saldo < 0 else CATEGORIA_FINANCIACION
    elif es_dividendo:
        # Ya se descartó arriba el caso "pagado" (saldo > 0). Solo llega aquí un
        # dividendo recibido (saldo < 0) -> INVERSION (p. 6).
        candidato = CATEGORIA_INVERSION

    # Interés de arrendamiento/pensiones nunca se mueve a OPERACION por la excepción de
    # actividad principal (ver ESMA, comentario en _PALABRAS_INTERES_SIEMPRE_FINANCIACION).
    excepcion_actividad_principal_aplica = not (
        candidato == CATEGORIA_FINANCIACION and es_interes and any(w in desc for w in _PALABRAS_INTERES_SIEMPRE_FINANCIACION)
    )

    es_metodo_participacion = any(w in desc for w in _PALABRAS_METODO_PARTICIPACION)

    # Paso 5: verificación de excepción de actividad principal — reclasifica a OPERACION
    # si la entidad declaró que financiar clientes o invertir es su giro central.
    if candidato == CATEGORIA_FINANCIACION and financiacion_es_actividad_principal and excepcion_actividad_principal_aplica:
        return CATEGORIA_OPERACION
    if candidato == CATEGORIA_INVERSION and inversion_es_actividad_principal and not es_metodo_participacion:
        return CATEGORIA_OPERACION
    if candidato is not None:
        return candidato

    # Paso 7: categoría residual — nada de lo anterior aplicó.
    return CATEGORIA_OPERACION


# ¤core
def clasificar_dataframe(df, financiacion_es_actividad_principal=False, inversion_es_actividad_principal=False):
    """Aplica `clasificar_partida` fila a fila; devuelve la lista de categorías en orden."""
    return [
        clasificar_partida(
            row['Cuenta'], row['Descripcion'], row['Saldo'],
            financiacion_es_actividad_principal, inversion_es_actividad_principal,
        )
        for _, row in df.iterrows()
    ]
