---
tipo: propuesta-evolve
tarea: OBS-02
status: approved
fecha: 2026-09-07
genes_afectados: [gen-identidad-de-pagina]
origen: backlog de OBS-01 (revisión de obsidianmd): Obsidian resuelve enlaces y detecta menciones sin vincular por `aliases`, no por `id_alias`
---

# Propuesta EVOLVE OBS-02 — `gen-identidad-de-pagina` v3 → v4: `aliases` nativo junto a `id_alias`

## Motivación

`id_alias` guarda claves canónicas (rutas) que solo entiende CEREBRO. Obsidian resuelve
`[[nombre-viejo]]`, sugiere el alias al enlazar y detecta *menciones sin vincular* por el
campo nativo `aliases`. Sin él, un humano en Obsidian y el agente en `tools/` no llegaban
a la misma página, y LNK-03 no veía los nombres que sí ve Obsidian.

## Diff (v3 → v4)

- `aliases` (lista de nombres) queda **declarado por este gen** como campo del esquema.
- `id_alias` = claves; `aliases` = nombres. Toda clave que entra a `id_alias` (fusión,
  movimiento de tier) mete su slug en `aliases`; los nombres con los que la fuente llama
  al sujeto (sigla, apodo, "formerly") van a `aliases` desde INGEST.
- Resolución de `[[enlaces]]` y sugeridor LNK-03 usan los mismos términos: basename,
  `title`, `id_alias`, `aliases`. Un alias jamás roba el slug de una página existente.

## Infra (mismo cambio, probada)

`schema.py` (campo + validación de lista), `vault.py` (resolución, al final del índice),
`graph.py` (términos de LNK-03). Tests: `test_vault.TestAliasNativo`,
`test_graph.TestAliasNativoLNK03`, `test_lint.TestPublishYAlias`.

## Compuerta

Aprobada por el operador en sesión Claude Code del 2026-09-07 ("Ejecutar pendientes según
recomendación"). Registro: `genome/events.jsonl` (`gene_edited`, v3 -> v4), commit firmado.
