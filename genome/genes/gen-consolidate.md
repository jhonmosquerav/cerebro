---
id: gen-consolidate
trigger: operación CONSOLIDATE (mantenimiento)
status: active
version: 2
---

CONSOLIDATE gestiona el ciclo de vida de la memoria entre tiers. Promueve conocimiento
confirmado hacia tiers más estables (`working → semantic`, procesos repetidos → `procedural`),
fusiona duplicados conservando la página con más relaciones —**exención**: pares con relación
declarada `deriva_de` / `supersede` / `agregado_en` son versionado o síntesis legítimos, NO
duplicados: no se fusionan ni se marcan como redundancia; solo se verifica que el marcador
canónico/de síntesis esté presente—, y aplica decaimiento: baja
`confidence` de lo no reforzado y archiva o deprecia lo obsoleto (sin borrar fuentes de
`raw/`). Sube `confidence` y `last_reinforced` de lo que múltiples fuentes confirman.
Cambios de contenido se aplican directo; cambios de regla pasan por [[gen-evolve]].
