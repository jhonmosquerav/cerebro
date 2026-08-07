---
tipo: propuesta-evolve
tarea: F0-04
status: approved
gate: aplicada-2026-08-07-tras-fase-b
fecha: 2026-07-12
genes_afectados: [gen-xray (nuevo), CLAUDE.md (fila de operación)]
---

# Propuesta EVOLVE F0-04 — `gen-xray` v1 (nuevo) + operación `XRAY`

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

> **APLAZADA en el gate del 2026-07-27** (decisión del operador). Es la única de
> las siete que no se aplicó. Motivo: sería el único gen NUEVO del lote (25 → 26)
> y su componente de salud sale hoy `N/A` porque XRAY nunca corrió sobre un vault
> poblado — se estaría aprobando una operación cuyo valor real no se ha visto.
> Se re-presenta cuando la Fase B (B-01…B-06) dé corpus real sobre el que la
> deriva declarado↔evidencia se pueda medir de verdad. Mientras tanto
> `cerebro xray` sigue disponible como infra, sin gen que la gobierne.

## Motivación

El riesgo estructural de un grafo declarativo es la **deriva**: lo que el
frontmatter afirma deja de coincidir con lo que el corpus demuestra, y nadie
se entera (la evaluación lo llamó "deriva silenciosa entre auditorías"). Un
sistema declarativo no puede auditarse a sí mismo: necesita comparar su
declaración contra evidencia independiente. La herramienta ya existe
(`cerebro xray`, con tests); falta el gen que la gobierne. Es complementaria
a GRAPH ([[gen-graph-lens]]): GRAPH deriva señales topológicas con una lente
externa; XRAY mide la deriva declarado↔evidencia, local y sin LLM.

## Gen propuesto (`genome/genes/gen-xray.md`, v1)

```
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
```

## Fila de operación (CLAUDE.md, tabla de gatillos)

```
| `XRAY` | "mide la deriva" / mantenimiento | Compara grafo declarado vs evidencia (local u --inferred). Tres buckets + score de deriva → PROPONE a LINT/CONSOLIDATE/EVOLVE. Corridas en `audit/xray/`. Regla: [[gen-xray]]. |
```

## Orden de aplicación

1. Crear `genome/genes/gen-xray.md` (v1) + fila en CLAUDE.md.
2. `events append --type gene_added --target gen-xray --signal "F0-04: la deriva declarado vs inferido entra al genoma" --diff "∅ → v1"`
3. Commit + `mirror --fix` (CLAUDE.md cambia).
