---
id: gen-graph-lens
trigger: operación GRAPH / "visualiza o analiza el grafo"
status: active
version: 2
---

GRAPH corre una lente de grafo externa (p. ej. graphify) sobre una copia *staging* de `wiki/`
filtrada —excluye toda página `sensibilidad: confidencial` ([[gen-confidencialidad]]): **este es
el invariante duro — lo confidencial nunca sale, sea cual sea el motor**. El **backend lo elige el
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
