---
id: gen-xray
trigger: operación XRAY / "mide la deriva del grafo"
status: active
version: 1
---

XRAY compara el grafo DECLARADO (relations del frontmatter) contra la
evidencia mecánica local (wikilinks, sources compartidas, co-mención en
raw/ y páginas terceras) y, opcionalmente, contra una lente externa
(--inferred graph.json, p. ej. graphify vía GRAPH). Corre con
`python tools/cerebro.py xray --as-of <hoy> --write`, que persiste la
corrida reproducible en `audit/xray/<fecha>-<sha8>/`.

Tres salidas, todas PROPUESTAS (jamás aplica; [[gen-compuerta-mutacion]]):
- **declarado sin evidencia** → candidato a decaimiento o revisión (LINT/
  CONSOLIDATE deciden bajo compuerta);
- **evidenciado sin declarar** → candidato a relación nueva (INGEST/LINT);
- **contradicciones** (contradice declarado, reemplaza recíproco) →
  escalamiento inmediato al operador.

El **score de deriva** (aristas con evidencia / declaradas) alimenta la
componente `deriva` de la salud (`cerebro health`). Las páginas
`confidencial` se citan solo por ruta/id ([[gen-confidencialidad]]); el
reporte jamás copia cuerpos. Cada corrida deja línea en `log.md`.
