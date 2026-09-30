# Excepción de método de participación — RESUELTA

## **Proyecto:** NIIF 18

**Estado:** Completada (2026-09-23, v3.5)

## Hallazgo original (v3.4, sin confirmar)

`IFRS-Converter` documentaba (con fuente secundaria, no oficial) que el resultado por
método de participación en asociadas/negocios conjuntos es Inversión **sin excepción de
actividad principal** — a diferencia de otras partidas de Inversión, nunca se
reclasifica a Operación aunque invertir sea el giro central de la entidad.
`sala_clasificacion` no distinguía este caso (el Paso 5 se aplicaba igual a todo
candidato de Inversión). No implementado — se dejó pendiente de confirmar contra texto
oficial.

## Confirmación con fuente oficial (2026-09-23)

El propietario aportó documentos oficiales nuevos en `docs/`: el `Opinion`
`EBA/Op/2026/07` (8-jul-2026) de la European Banking Authority y sus anexos técnicos
(plantillas FINREP bajo IFRS 18). La hoja `"2 (post consultation)"` del Anexo III/IV
(= plantilla oficial F 02.00, Estado de Resultados bajo IFRS 18) trae, fila 74:

> "Share of the profit or (-) loss of investments in subsidiaries, joint ventures and
> associates accounted for using the equity method" — citando **Anexo V.Parte 2.54**

Esta línea aparece **dentro de la sección de Inversión, inmediatamente después del
Resultado Operativo** (fila 73, ), como partida independiente — no
hay ninguna nota ni columna que la condicione a la actividad principal de la entidad, a
diferencia de cómo la propia plantilla sí distingue "intereses de activos de inversión"
con matices adicionales. Esto confirma, con fuente oficial (una autoridad de la UE,
citando el propio Anexo V del estándar), el hallazgo secundario de `IFRS-Converter`.

## Corrección aplicada

`src/sala_clasificacion/_service.py`: se agregó `_PALABRAS_METODO_PARTICIPACION`
(`asociada`, `negocio conjunto`, `metodo de participacion`) y la variable
`es_metodo_participacion`. El Paso 5 ahora excluye estas partidas de la reclasificación
a Operación aunque `inversion_es_actividad_principal=True`:

```python
if candidato == CATEGORIA_INVERSION and inversion_es_actividad_principal and not es_metodo_participacion:
    return CATEGORIA_OPERACION
```

Mismo patrón ya existente para intereses de arrendamiento/pensión en Financiación
(`_PALABRAS_INTERES_SIEMPRE_FINANCIACION`, v3.3, fuente ESMA).

## Verificación

- Nuevo test: `tests/test_sala_clasificacion.py::test_metodo_participacion_no_se_mueve_a_operacion_aunque_inversion_sea_actividad_principal`.
- `python -m pytest tests/` — 39/39 en verde (38 previos + 1 nuevo).

---

© 2026 Juan Carlos Proaño. Todos los derechos reservados.
