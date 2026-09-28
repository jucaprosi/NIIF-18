# Optimizar carga directorio scvs
## **Proyecto:** NIIF 18

**Estado:** Completada

`sala_entidad.cargar_directorio` ahora mantiene una caché en disco (`data/directorio_companias_scvs.parquet`, hermano del `.xlsx`, regenerado automáticamente si el `.xlsx` cambia — comparación de `mtime`). Medido: primera carga (genera la caché) 29.4s, cargas siguientes 0.35s (~84x). El `.xlsx` sigue siendo la única fuente declarada en RF-11; el `.parquet` es una caché derivada, no una fuente aparte. 2 tests nuevos con un xlsx sintético (no dependen del archivo real de 227k filas) — uno de ellos expuso una decisión de diseño real: si el `.xlsx` no existe, la función retorna `None` sin mirar la caché (intencional: sin fuente configurada, no hay dato que devolver). 29/29 tests en verde.

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
