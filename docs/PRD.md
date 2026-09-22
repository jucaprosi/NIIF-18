# PRD: Aplicación NIIF 18
[¤vocabulario_precision_agentica]

## 1. Visión y Alcance
App de escritorio/CLI en Python para implementar NIIF 18, permitiendo importar, reclasificar y generar estados financieros con las 5 categorías obligatorias y MPMs.

## 2. Módulos Funcionales (Salas ADPA)
- `sala_catalogo`: Gestión del catálogo de cuentas y mapeo.
- `sala_clasificacion`: Motor de clasificación jerárquica.
- `sala_estados_financieros`: Generación del Estado de Resultados.
- `sala_mpm`: Gestión de Medidas de Rendimiento Definidas por la Gerencia.
- `sala_importacion`: Importación desde CSV.
- `sala_reportes`: Exportación de reportes.
- `sala_validacion`: Validaciones normativas.

## 3. Requisitos Funcionales
- RF-01: Importar balanza de comprobación desde CSV.
- RF-02: Mapear cuentas a las 5 categorías NIIF 18.
- RF-03: Aplicar prueba de clasificación jerárquica.
- RF-04: Generar Estado de Resultados con subtotales mandatorios.
- RF-05: Calcular y reconciliar MPMs.
- RF-06: Generar nota de MPMs auditables.
- RF-07: Comparativos.
- RF-08: Validar etiquetas.
- RF-09: Exportar reportes.
- RF-10: Auditoría.

## 4. Arquitectura
- Python 3.11+
- Estructura ADPA con compuertas `_service.py`
