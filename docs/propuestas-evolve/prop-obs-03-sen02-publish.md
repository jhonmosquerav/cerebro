---
tipo: propuesta-evolve
tarea: OBS-03
status: approved
fecha: 2026-09-07
genes_afectados: [gen-confidencialidad]
origen: backlog de OBS-01: Obsidian Publish decide qué sale del vault por la propiedad `publish`; nada lo cruzaba con `sensibilidad`
---

# Propuesta EVOLVE OBS-03 — `gen-confidencialidad` v3 → v4: `publish: true` solo en `publico` (SEN-02)

## Motivación

La lente de grafo y su render nativo ya aplican allowlist fail-closed, y la CLI tiene su
runbook. Faltaba el canal más directo: la propiedad nativa `publish`, que Obsidian Publish
(o cualquier exportador que la respete) usa para publicar una página. Una página `interno`
o `confidencial` con `publish: true` saldría del vault sin que ningún detector lo viera.

## Diff (v3 → v4)

- `publish` (booleano) queda declarado por este gen.
- Regla: **nada que no sea `publico` sale del vault por ningún canal**. `publish: true`
  en `interno`, `confidencial` o sin campo (hereda el default del manifiesto, nunca
  `publico` por omisión) es **error SEN-02 de LINT**, mecánico. Error y no aviso porque
  publicar por descuido no se deshace.

## Infra (mismo cambio, probada)

`schema.py` (campo + validación booleana), `lint.py` (`_check_publish`, código SEN-02,
usa `default_sensibilidad` del manifiesto), `.obsidian/types.json` (`publish: checkbox`).
Tests: `test_lint.TestPublishYAlias` (confidencial, interno, sin campo → error; publico →
pasa; `false` nunca dispara; no booleano → FM-03).

## Compuerta

Aprobada por el operador en sesión Claude Code del 2026-09-07. Registro:
`genome/events.jsonl` (`gene_edited`, v3 -> v4), commit firmado.
