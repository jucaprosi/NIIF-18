# Mapeo y exportación a plantillas FINREP oficiales

## **Proyecto:** NIIF 18

**Estado:** Pendiente — nueva (2026-09-23)

## Origen

Detectada en el análisis de brecha entre la herramienta y el documento de exposición del
propietario: el documento describe "Mapeo a FINREP" como funcionalidad — vincular las
partidas clasificadas del balance con las plantillas FINREP oficiales bajo IFRS 18
(F 02.00, F 16.xx, F 20.03, F 45.02-03).

## Estado actual — distinción importante

Ya se usó FINREP en este proyecto (,
), pero **solo como fuente de criterios
normativos** (para confirmar reglas de clasificación con cita de párrafo oficial de
IFRS 18) — **no** como funcionalidad operativa de la app. Hoy no existe ningún mapeo
automático de una cuenta clasificada a una fila específica de una plantilla FINREP, ni
exportación en el formato/estructura que la EBA exige.

## Por qué no se adoptó ya (ver `PRD.md` §11.2)

FINREP es el reporte **supervisor bancario** de la EBA — diseñado para entidades de
crédito bajo supervisión prudencial europea, con decenas de líneas específicas a
instrumentos financieros, deterioro por etapas de IFRS 9, garantías de depósito, etc. El
público objetivo declarado de este proyecto (`PRD.md` §1) es una entidad genérica, no
necesariamente bancaria ni europea — adoptar el catálogo completo de FINREP como
funcionalidad estándar añadiría un costo de mantenimiento que no se justifica sin un
cliente bancario europeo real.

## Qué implicaría implementarlo (si se confirma el mercado objetivo)

- Tabla de mapeo `Categoria_NIIF18` (+ subcategoría más granular, hoy no modelada) →
  fila de plantilla FINREP (p. ej. "Operación" → filas 1-73 de F 02.00 según naturaleza
  del ingreso/gasto; "Inversión" → filas 74-87; método de participación → fila 74
  específicamente, ya con regla propia en `sala_clasificacion`).
- El modelo de datos actual (`sala_catalogo`, 5 categorías + Balance General) es
  **demasiado grueso** para mapear 1:1 a FINREP, que tiene decenas de sub-líneas por
  categoría (ver hoja `"2 (post consultation)"` de `docs/Annex 2 ... Annex III)_CV.xlsx`,
 leída en ) — se requeriría extender el catálogo de
  categorías con un nivel de detalle adicional antes de poder mapear con fidelidad.
- Exportación en el formato exigido por la EBA (DPM/taxonomía XBRL, ver §4 del documento
  de exposición del propietario — "Paquete técnico 4.4") — fuera de alcance actual, ver
 también .

## Precondición antes de iniciar

Confirmar con el propietario si el mercado objetivo incluye entidades supervisadas por
la EBA/bancos europeos — si no, esta tarea permanece correctamente fuera de alcance
(mismo criterio que y ).

## No implementado — solo documentado

Este archivo registra el gap para que quede trazable en `VPA_MAP.md`/`TASKS.md`. No se
ha escrito código.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
