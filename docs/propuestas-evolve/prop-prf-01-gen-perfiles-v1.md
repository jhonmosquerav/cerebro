---
tipo: propuesta-evolve
tarea: PRF-01
status: approved
fecha: 2026-10-20
genes_afectados: [gen-perfiles]
origen: revisión de kepano/obsidian-skills, thedotmack/claude-mem, obsidianmd + obsidian-releases, AgriciDaniel/claude-obsidian y Ar9av/obsidian-wiki (docs/revision-repos-2026-10-20.md); pedido del operador de una instalación con opciones activables ("solo memoria" vs "completa con auditoría")
---

# Propuesta EVOLVE PRF-01 — `gen-perfiles` v1 (NUEVO, 26 → 27 genes)

## Motivación

CEREBRO solo se instalaba de una forma: todo encendido. Los cinco repos revisados
convergen en un patrón que al template le faltaba: **un interruptor por pieza** (plugins
core de Obsidian, `CLAUDE_MEM_*` en claude-mem, `WIKI_STOP_CAPTURE`/`--no-hooks` en
obsidian-wiki, `setup-*.sh` en claude-obsidian). La diferencia de CEREBRO es que el
interruptor tiene que ser **reproducible** (vive en el manifiesto), **auditable** (deja
evento) y **verificable** (lint detecta deriva). El roadmap desbloqueó la Fase 4
(distribución) al cerrar la Fase 1 el 2026-08-07; esta es su primera entrega.

## Diff (∅ → v1)

Gen nuevo que declara: seis **capacidades** (`memoria`, `ciclo_de_vida`, `evolucion`,
`auditoria`, `visualizacion`, `grafo`) con los genes, operaciones, comandos y carpetas que
cada una gobierna; el **núcleo** no desactivable (19 genes, incluido este); cuatro
**perfiles** en escalera estricta (`minimo` ⊂ `memoria` ⊂ `gobernanza` ⊂ `completo`);
el estado efectivo en `genome/perfil.md` (frontmatter plano, greppable); la regla de
apagado (no se ejecuta, no se borra, exit 2 con `--ignore-profile`, hooks no-op sin
memoria); ausencia ⇒ `completo` sin archivo (compatibilidad total). Texto completo:
`genome/genes/gen-perfiles.md`.

`CLAUDE.md`/`AGENTS.md`: regla de arranque (leer `genome/perfil.md`), columna *Capacidad*
en la tabla de operaciones, sección "Perfiles de instalación", entrada en el índice de genes,
nota en el loop de memoria y comando `profile` entre los validadores.

## Infra (mismo cambio, probada)

`schema.py` (`CAPABILITIES`, `PROFILES`, `CORE_GENES`, `capability_of`),
`cerebro_core/profile.py` (efectivo, render, lectura, edición textual del manifiesto),
`cerebro.py profile [show|set|enable|disable]` + gating con exit 2 en `consolidate`,
`health`, `xray`, `graph`; hooks `.claude/hooks` y `.codex/hooks` con `cap_on`;
`onboard/company.example.yaml` con el bloque; `.obsidian/types.json`. Tests:
`tests/test_profile.py` (escalera, cobertura de genes, overrides, render↔parse, edición
textual, ONBOARD, lint, CLI punta a punta). Los tres casos de `worked/` regeneran sin
cambios.

## Compuerta

Aprobada por el operador en sesión Claude Code del 2026-10-20 con la instrucción explícita
"planea y ejecuta de inicio a fin … hasta el final". Registro: `genome/events.jsonl`
(`gene_added`, ∅ → v1), commit firmado.
