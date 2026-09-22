# NIIF 18 Financial Reporting Matrix - Manual de Operación
[¤protocolo_migracion_legacy]

Bienvenidos a la **Plataforma de Cumplimiento y Reclasificación NIIF 18**. 

Esta herramienta de nivel corporativo está diseñada específicamente para equipos contables y financieros que ya dominan los preceptos de la norma IFRS 18 (*Presentación e Información a Revelar en los Estados Financieros*). La plataforma automatiza la transición desde la estructura tradicional de la NIC 1 hacia el modelo de jerarquías y subtotales obligatorios de la NIIF 18, actuando como un puente entre su ERP actual y sus reportes de cierre.

---

## 🚀 Inicio Rápido (Despliegue Local)

La plataforma se despliega en un entorno local aislado (Zero-Trust) para proteger su información financiera.

1. **Instalación de Dependencias**: Haga doble clic en `setup.bat`. Esto creará un entorno virtual e instalará las librerías necesarias. Solo debe ejecutarse la primera vez.
2. **Ejecución de la Plataforma**: Haga doble clic en `run.bat`. Se abrirá automáticamente su navegador web predeterminado (por defecto en `http://localhost:8501`) mostrando el Dashboard corporativo.

---

## 🧭 Guía de Operación Funcional (Flujo de Cierre)

La plataforma está dividida en **6 módulos (pestañas)** que deben procesarse secuencialmente durante su ciclo de cierre contable:

### 📥 1. Ingesta (Dropzone)
*Punto de entrada de datos desde su ERP.*
- **Operación**: Arrastre y suelte la Balanza de Comprobación exportada desde su sistema contable (SAP, Oracle, Dynamics, etc.) en formato `.csv` o `.xlsx`.
- **Validación Cero**: El sistema verificará de inmediato que la balanza cuadre (Tolerancia Cero), mostrando el saldo de comprobación en el panel lateral.
- *Nota*: Puede utilizar el botón `Cargar Dataset Demo NIIF 18` para inyectar un juego de datos de prueba preconfigurado y familiarizarse con la herramienta.

### 🏷️ 2. Matriz de Reclasificación
*El motor de mapeo estructural. Aquí aplicará su juicio profesional.*
- **Operación**: Verá la grilla de alta densidad con sus cuentas contables. Utilice la columna **"Clasificación NIIF 18"** para asignar cada rubro a una de las 5 categorías mandatorias (Operativo, Inversión, Financiación, Impuestos, Operaciones Discontinuadas).
- **Residualidad**: Recuerde que, según la norma, la categoría *Operativa* es residual; asigne primero las partidas específicas de Inversión, Financiación e Impuestos, dejando el giro del negocio en la categoría por defecto.

### 📊 3. Árbol de EEFF (Estados Financieros)
*Renderizado jerárquico automatizado.*
- **Operación**: Una vez clasificada la balanza, esta pestaña calculará automáticamente y en tiempo real los 3 nuevos subtotales exigidos por el IASB:
  1. *Resultado Operativo*
  2. *Resultado antes de Financiación e Impuestos a las Ganancias*
  3. *Resultado del Periodo*
- Permite desplegar el árbol para auditar qué cuentas específicas de su balanza componen cada subtotal.

### 📈 4. Conciliación MPM (Medidas de Rendimiento Definidas por la Gerencia)
*Gestión del cumplimiento de divulgación de KPIs (ej. EBITDA, Utilidad Ajustada).*
- **Operación**: Si su compañía reporta métricas *Non-GAAP* a los inversores, IFRS 18 exige una conciliación obligatoria auditada en una nota única. 
- Utilice el **formulario izquierdo** para registrar la MPM, seleccionar el subtotal NIIF 18 de anclaje e insertar el ajuste monetario.
- Escriba la *Justificación Gerencial* requerida. Al enviar, la **tabla de conciliación derecha** se actualizará, generando la estructura exacta requerida para las notas a los estados financieros (incluyendo efectos fiscales automáticos).

### 📑 5. Centro de Exportación
*Extracción segura del paquete de cierre.*
- **Operación**: Descargue los *working papers* en Excel y CSV. 
- El sistema le permite exportar tanto el Estado de Resultados estructurado final como el log completo de trazabilidad (Mapeo de cuentas original vs. Categoría NIIF 18 asignada) indispensable para su firma auditora.

### 📚 6. Visor Doctrinal
*Referencia normativa integrada.*
- **Operación**: Un lector Markdown embebido que contiene la Biblioteca Doctrinal destilada. Permite a su equipo repasar los preceptos de agrupación/desagregación, guías de MPMs y exenciones de transición sin necesidad de salir de la aplicación.

---

> **Seguridad y Confidencialidad**: Al operar bajo el protocolo ZERAG BIOS y un marco arquitectónico Presentador-Puro (ADPA), sus datos procesados no salen de su máquina (On-Premise virtual). Las sesiones de memoria son volátiles y se destruyen al cerrar el navegador o la terminal.