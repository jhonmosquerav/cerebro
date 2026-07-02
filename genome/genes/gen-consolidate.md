---
id: gen-consolidate
trigger: operación CONSOLIDATE (mantenimiento)
status: active
version: 3
---

CONSOLIDATE gestiona el ciclo de vida de la memoria entre tiers con los **umbrales
numéricos de [[gen-ciclo-de-vida]]**. Promueve conocimiento confirmado —TODOS los
criterios verificables de promoción de ese gen— hacia tiers más estables
(`working → semantic`, procesos repetidos → `procedural`),
fusiona duplicados conservando la página con más relaciones —**exención**: pares con relación
declarada `deriva_de` / `supersede` / `agregado_en` son versionado o síntesis legítimos, NO
duplicados: no se fusionan ni se marcan como redundancia; solo se verifica que el marcador
canónico/de síntesis esté presente—, y aplica el decaimiento numérico de
[[gen-ciclo-de-vida]]: resta `decaimiento_delta` por ventana de `decay_rate` vencida sin
refuerzo, anotando `decay_aplicado` (re-ejecutable sin doble descuento); al tocar el
`piso_archivo` **propone** archivar en `wiki/archive/` — tras OK, sin borrar fuentes de
`raw/`. Sube `confidence` y `last_reinforced` de lo que múltiples fuentes confirman, con
los deltas y el techo de [[gen-ciclo-de-vida]]. Cambios de contenido (promoción y
decaimiento incluidos) se aplican directo; el archivo se propone; cambios de regla pasan
por [[gen-evolve]].
