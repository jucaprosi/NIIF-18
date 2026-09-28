# Los 4 estados financieros completos + interfaz

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-24, v3.11) — decisión explícita del propietario de ir por la funcionalidad completa

## Origen

Reunión de producto (§12.1, v3.7): Roberto pidió cargar el juego completo de 4 estados
financieros; Giovanni pidió comparativo de 2 años con delta automático; Juan Carlos
propuso 4 casilleros + selector Año 1/Año 2. Quedó marcada explícitamente "Fase B — no
iniciar sin decisión explícita del propietario" porque contradecía el alcance de
entonces (`PRD.md` §1.3 solo permitía Estado de Resultados).

El 2026-09-24 el propietario pidió avanzar ("vamos a agregar a la pestaña de ingesta,
los 4 archivos que necesita la app") y, ante la pregunta explícita de alcance
(interfaz de carga solamente vs. motor de clasificación completo para los 3 estados
nuevos), eligió **funcionalidad completa**.

## Los 3 motores nuevos (cada uno verificado antes de darse por completo)

1. **`sala_situacion_financiera`** (NIC 1.60-76) — clasificación por código de cuenta,
   misma señal fuerte que ya usaba `sala_clasificacion` (código sobre palabra clave,
   aporte A-05). Verificado exacto contra `TB_ERP` real: Total Activo $5,455,000 =
   Pasivo+Patrimonio+resultado implícito, y ese resultado implícito ($550,000) coincide
   exactamente con la utilidad neta ya verificada en `sala_estados_financieros` — una
   verificación cruzada real entre dos salas independientes.
   - **Bug encontrado y corregido durante la construcción**: sumar por `abs()` cuenta
     por cuenta contaba las cuentas contra-activo genuinas (depreciación/deterioro
     acumulados) como si sumaran en vez de restar — error de $1,220,000 antes de la
     corrección. La suma correcta preserva el signo de `Saldo` (positivo=débito) y solo
     invierte el signo del total una vez, al final, para Pasivo/Patrimonio.

2. **`sala_flujo_efectivo`** (NIC 7.18(b), método indirecto) — requiere balanza
   comparativa de un segundo período, algo que `sala_estados_financieros`/
   `sala_situacion_financiera` no necesitan. Verificado con un escenario sintético de
   dos períodos construido por partida doble a mano (no existe todavía un caso de
   prueba real de dos años en este proyecto) contra la identidad contable fundamental
   del estado: CFO+CFI+CFF debe ser exactamente igual al cambio real de efectivo.
   - **3 bugs de signo encontrados y corregidos** al construir ese escenario:
     (a) CFI no sumaba de vuelta la depreciación ya neteada en el Activo No Corriente
     (subestimaba una compra real de $50 como $30); (b) el signo del cambio en Pasivo
     No Corriente estaba invertido (un pago de deuda se contaba como entrada de
     efectivo); (c) los dividendos pagados no pueden buscarse en el Estado de
     Resultados — por diseño (RF-03 Paso 0) un dividendo pagado se excluye de ahí, así
     que se derivan del cambio en Resultados Acumulados.

3. **`sala_cambios_patrimonio`** (NIC 1.106-110) — reutiliza la misma derivación de
   dividendos pagados de `sala_flujo_efectivo` (llamada vía compuerta ADPA, no
   duplicada) para que ambas salas nunca puedan reportar cifras distintas para el mismo
   par de balances — verificado con un test dedicado que compara ambas salidas.
   Verificado con el mismo escenario sintético: cada componente de patrimonio concilia
   exacto (Saldo Inicial + movimientos = Saldo Final).

## Interfaz

- `app.py`, Fase 1 (Ingesta): la balanza actual se etiqueta "Año 2" y se agregó un
  toggle "Agregar balanza comparativa (Año 1)" que revela un segundo uploader —
  reutiliza `procesar_balanza_subida`, una función extraída del bloque de ingesta
  original (antes duplicado, ahora parametrizado por prefijo de sesión) para no
  duplicar ~50 líneas de lectura/inferencia/puerta de calidad/remapeo manual.
- La pestaña "Árbol de EEFF" se renombró a "Estados Financieros" y ahora tiene 4
  sub-pestañas: Estado de Resultados (contenido original, sin cambios), Situación
  Financiera (siempre disponible con solo Año 2), Flujo de Efectivo y Cambios en
  Patrimonio (ambas muestran un aviso claro si no se cargó el comparativo, en vez de
  fallar o mostrar ceros sin explicación).

## Verificación

- 10 tests nuevos (`test_sala_situacion_financiera.py`, `test_sala_flujo_efectivo.py`,
  `test_sala_cambios_patrimonio.py`), incluyendo el escenario sintético de dos períodos
  compartido entre Flujo de Efectivo y Cambios en Patrimonio, y la verificación cruzada
  de que ambas salas reportan el mismo monto de dividendos.
- `python -m pytest tests/` — 66/66 en verde.
- App verificada corriendo (Streamlit real, `venv` del proyecto): la pestaña Ingesta
  muestra el toggle de comparativo y "Estados Financieros" renderiza sin errores en
  estado vacío. No se pudo probar con un archivo real de dos años arrastrado (mismo
  límite ya conocido del diálogo nativo de archivos en el entorno de verificación).

## Riesgo señalado, no resuelto

Ninguno de los 3 motores nuevos está validado contra un caso real de dos períodos —
`balance_prueba_niif18_sap_business_one.xlsx` (el único fixture real de este proyecto)
es de un solo período. La verificación actual es matemáticamente sólida (identidades
contables exactas con datos sintéticos) pero no reemplaza la validación con una balanza
real de un cliente con dos años de historia.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
