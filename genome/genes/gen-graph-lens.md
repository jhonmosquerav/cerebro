---
id: gen-graph-lens
trigger: operación GRAPH / "visualiza o analiza el grafo"
status: active
version: 4
---

GRAPH tiene dos mitades con garantías distintas. La mitad ESTRUCTURAL es mecánica,
determinista y sin dependencias: `python tools/cerebro.py graph [--scope wiki|genome|all]`
deriva componentes conexas, grado, hubs contra el `hub_umbral` del manifiesto, huérfanas,
puntos de articulación (páginas-puente cuya pérdida parte el grafo) y camino más corto entre
dos páginas (`graph <origen> <destino>`). Corre siempre, también en un clon sin graphify, y
da el mismo resultado en cada máquina — es la fuente canónica de las señales de hub para
[[gen-jerarquizacion-indice]] y [[gen-consolidate]], y de islas para [[gen-lint]]. Al no salir
del proceso no necesita copia staging: el filtro de allowlist rige solo para lo que se exporta
a un motor externo. La mitad SEMÁNTICA (comunidades por modularidad, conexiones sorprendentes,
resúmenes narrados) sigue siendo de la lente externa descrita abajo, con su staging
fail-closed intacto. Si ambas discrepan, manda la estructural: es reproducible.

GRAPH corre una lente de grafo externa (p. ej. graphify) sobre una copia *staging* de `wiki/`
filtrada por **allowlist fail-closed**: solo entra la página que declara explícitamente
`sensibilidad: publico|interno` ([[gen-confidencialidad]]) y no está en cuarentena
`riesgo_inyeccion: true` ([[gen-anti-inyeccion]]); página sin campo, con typo o con
frontmatter ilegible NO entra. **Este es el invariante duro — lo confidencial y lo
en-cuarentena nunca salen, sea cual sea el motor**. El **backend lo elige el
usuario** (`claude` = conexión Claude Code · `local` = Ollama · `structural` = sin LLM) y queda
**registrado en `graph_lens.backend` del manifiesto**: si está vacío, el agente **pregunta una
vez** y persiste la elección; si ya está puesto, lo usa sin volver a preguntar (mismo manifiesto →
mismo comportamiento). Su salida (`graphify-out/`, gitignored)
es un artefacto **derivado y regenerable**: una *lente*, nunca fuente de verdad; no se importa a
`wiki/` ni a `genome/` (no dos verdades). De `graph.json` deriva SEÑALES y las PROPONE a las
operaciones existentes, sin aplicar nada por sí mismo ([[gen-compuerta-mutacion]]):
god-nodes/hubs → candidatos de [[gen-consolidate]]; comunidades → candidatas a síntesis
([[gen-sintesis-de-volumen]]) o panel `por-sector`; caminos entre entidades → enriquecen
[[gen-query]]; islas/huérfanos → segunda opinión que cruza con [[gen-lint]]; conexiones
sorprendentes → patrón candidato para [[gen-evolve]]. Respeta el presupuesto de contexto: lee un
resumen de `graph.json` y emite ≤N señales priorizadas, no vuelca el grafo entero al contexto.
Cada corrida deja una línea en `log.md`. Es OPCIONAL y removible ([[gen-visualizacion]]): CEREBRO
funciona igual sin graphify instalado. Runbook en `dashboards/graph/00-leeme.md`.
