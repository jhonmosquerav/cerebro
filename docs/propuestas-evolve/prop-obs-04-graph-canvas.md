---
tipo: propuesta-evolve
tarea: OBS-04
status: approved
fecha: 2026-09-07
genes_afectados: [gen-graph-lens, gen-visualizacion]
origen: enfoque B del diseño 2026-09-03 (JSON Canvas 1.0, spec abierta de obsidianmd/jsoncanvas); aplazado hasta tener wiki poblada — condición cumplida con el piloto de Fase B
---

# Propuesta EVOLVE OBS-04 — `gen-graph-lens` v4 → v5 y `gen-visualizacion` v3 → v4: render nativo del grafo (`graph --canvas`)

## Motivación

La mitad estructural de GRAPH ya era mecánica y sin dependencias, pero solo se leía en
texto; el render interactivo dependía de graphify y de un backend. JSON Canvas es un
formato abierto que Obsidian abre de serie: el mismo grafo se puede **dibujar** sin
plugin ni LLM, con la misma garantía de confidencialidad que el staging.

## Diff

- **gen-graph-lens v5**: `graph --canvas <ruta>` emite JSON Canvas 1.0 (grupo por
  tier/genoma, nodos por grado, hubs en amarillo, aristas etiquetadas por verbo) con la
  **misma allowlist fail-closed** del staging; lo excluido no aparece ni por ruta ni por
  título, solo como conteo. Derivado y regenerable (`dashboards/graph/*.canvas`,
  gitignored).
- **gen-visualizacion v4**: el render interactivo tiene dos sabores, nativo (canvas) y
  externo (lente), ambos derivados.

## Infra (mismo cambio, probada)

`cerebro_core/canvas.py` (nuevo), flag `--canvas` en `graph`, `.gitignore`, runbook
`dashboards/graph/00-leeme.md`. Tests: `test_canvas` (allowlist: confidencial, sin campo y
cuarentena fuera; nada excluido se filtra por texto; aristas solo entre nodos presentes;
forma JSON Canvas; determinismo; grupos) y `test_cli.TestGraphCanvas`.

## Evidencia en corpus real (piloto Fase B, solo lectura, 2026-09-07)

| Scope | Nodos | Aristas | Excluidas por allowlist |
|---|---|---|---|
| all | 107 | 429 | 4 (sin `sensibilidad` explícita) |
| wiki | 75 | 226 | 4 |
| genome (template) | 28 | 108 | 0 |

## Compuerta

Aprobada por el operador en sesión Claude Code del 2026-09-07. Registro: dos líneas en
`genome/events.jsonl` (`gene_edited`, gen-graph-lens v4 -> v5; gen-visualizacion v3 -> v4),
commit firmado.
