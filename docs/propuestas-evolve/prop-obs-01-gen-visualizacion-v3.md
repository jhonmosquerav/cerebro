---
tipo: propuesta-evolve
tarea: OBS-01
status: approved
fecha: 2026-09-03
genes_afectados: [gen-visualizacion]
origen: revisión de github.com/obsidianmd (18 repos) + ayuda oficial — Bases es plugin core desde 1.9, Properties tipadas, CLI oficial 1.12+
---

# Propuesta EVOLVE OBS-01 — `gen-visualizacion` v2 → v3: el render vivo es nativo (Bases); Dataview pasa a alternativa

## Motivación

El gen v2 nombraba a Dataview —un plugin comunitario— como el único render vivo. Desde
Obsidian 1.9, **Bases** hace lo mismo de serie, en un formato YAML abierto (`.base`) que
además se consulta desde fuera (`obsidian base:query … format=json`). Mantener la
dependencia de un plugin externo cuando existe el equivalente core contradice la promesa
de "sin infraestructura". Además, el preset `.obsidian/` estaba en formato legado, sin
tipado de propiedades y con el plugin de plantillas activo sin plantillas.

Diseño aprobado: `docs/specs/2026-09-03-obsidian-nativo-design.md` (enfoque A).

## Diff (v2 → v3)

- **vivo** = vistas nativas Bases en `dashboards/*.base` (plugin core); Dataview queda como
  alternativa opcional equivalente.
- El preset `.obsidian/` declara el **tipado de propiedades** (`types.json`) como espejo
  del esquema de [[gen-frontmatter-obligatorio]] — si el esquema muta, el tipado muta en el
  mismo cambio —, grupos de color del grafo nativo y las plantillas por `type` de
  `templates/` (fuera de `wiki/`: no son conocimiento).
- La **CLI oficial de Obsidian** es equivalente opcional para el operador humano
  (`ops/runbook-obsidian-cli.md`), nunca dependencia: exige la app abierta y las señales
  canónicas siguen siendo las de `tools/`.
- El resto del gen (render estático, lente interactiva con staging fail-closed, ONBOARD
  recomienda y propone, dashboards `type: meta` exentos de LINT) no cambia.

## Compuerta

Aprobada por el operador en sesión Claude Code del 2026-09-03 ("Sí pero ejecutar completo
de una vez", tras presentación de tres enfoques con recomendación explícita). Registro:
`genome/events.jsonl` (`gene_edited`, gen-visualizacion, v2 -> v3), commit firmado (C-04).

## Fuera de esta propuesta (backlog con compuerta)

- `id_alias` ↔ `aliases` nativo (resolución de enlaces y menciones sin vincular).
- Detector LINT: `publish: true` en página `confidencial` es error.
- `cerebro graph --canvas` (JSON Canvas 1.0 con allowlist fail-closed) — enfoque B.
