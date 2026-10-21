---
titulo: Revisión de repos de referencia — 2026-10-20
tipo: nota-de-arquitectura
fecha: 2026-10-20
estado: cerrada
deriva_a: docs/specs/2026-10-20-perfiles-capacidades-design.md
---

# Revisión de repos de referencia (2026-10-20)

Pedido del operador: analizar cinco repos y mejorar CEREBRO con lo que aporten, en
particular que la instalación permita **activar y desactivar opciones** (p. ej. una
versión "solo memoria" y una "completa con auditoría"). Lectura hecha por agentes de
fetch sobre README, docs y archivos de configuración de cada repo; lo que no se pudo
verificar se marca como tal.

## Qué aporta cada uno

| Repo | Qué es | Mecanismo de activación que expone | Qué tomamos |
|---|---|---|---|
| **kepano/obsidian-skills** (MIT) | 6 skills Agent-Skills para Claude Code/Codex: markdown de Obsidian, Bases, JSON Canvas, CLI, defuddle, knap | Instalación por marketplace (`/plugin marketplace add kepano/obsidian-skills`) o `npx skills add`; cada skill es una carpeta `SKILL.md` independiente | Convenciones ya alineadas (wikilinks, `aliases`, Bases, Canvas 1.0). Pitfalls de Bases como futuros detectores de lint (`formula.X` sin definir, fechas sin `.days`). `%%…%%` no oculta nada: confirma SEN-02 |
| **thedotmack/claude-mem** (Apache-2.0) | Memoria persistente para Claude Code: hooks → cola → worker Bun → SQLite+FTS5 (+Chroma) | `~/.claude-mem/settings.json` con toggles `CLAUDE_MEM_*` por pieza (observación, resumen, inyección semántica, redacción, dedup, skip de herramientas) | El **patrón de toggles por pieza**; "summaries are checkpoints, not endings" (encaja con CHECKPOINT); índice-primero con coste en tokens. **No** se copia la infraestructura (servidor, SQLite, vectores): contradice el principio de CEREBRO |
| **obsidianmd** (org) + **obsidian-releases** | Repos oficiales: API, sample-plugin, releases (`community-plugins.json`), jsoncanvas, clipper, importer, eslint/stylelint | `core-plugins.json`: cada plugin core se enciende o apaga; plugins de comunidad con `manifest.json` (id, version semver, minAppVersion) y `versions.json` | **El modelo de capacidades = plugins core**: un conjunto fijo, cada uno con interruptor, y un núcleo que no se apaga. Para la Fase 4.3: catálogo de blueprints con `versions`/`min_cerebro` |
| **AgriciDaniel/claude-obsidian** (v2.2.0) | Sistema local-first: 15 skills, hooks SessionStart/Stop, transacciones con SHA-256, planes con hash aprobado | Extensiones opcionales con `setup-*.sh` explícitos; `wiki-mode` (Generic/LYT/PARA/Zettelkasten); hooks se quitan desinstalando el plugin | Separación producto/vault (CEREBRO ya la tiene: template vs clon). Idea diferida: `apply --approved-plan-sha256` (plan con hash) |
| **Ar9av/obsidian-wiki** | 39 skills markdown sobre un vault; ingesta por etapas; `.manifest.json` de delta | `.env`/config: `WIKI_SESSION_RECAP`, `WIKI_STOP_CAPTURE`, `setup --no-hooks`, `WIKI_STAGED_WRITES`, `OBSIDIAN_TRUST_STRICT`, backends opcionales | Confirma que **memoria de sesión y captura al cierre son opcionales** en la práctica; `hot.md` con tope de palabras (diferido); escritura con lock (diferido) |

## Síntesis: lo que CEREBRO ya tenía y lo que le faltaba

Ya tenía: manifiesto reproducible, genes atómicos, ledger con hash-chain, hooks POSIX
tolerantes a fallo, capa Obsidian nativa, allowlist de confidencialidad, validadores
mecánicos. Le faltaba exactamente lo que los cinco repos resuelven cada uno a su manera:
**un interruptor por pieza**. La diferencia de CEREBRO es que el interruptor debe ser
reproducible (vive en el manifiesto), auditable (deja evento) y verificable (lint
detecta deriva). De ahí el diseño de perfiles y capacidades.

## Decisiones

- **Capacidades (6)**: memoria · ciclo_de_vida · evolucion · auditoria · visualizacion ·
  grafo. **Perfiles (4)**, escalera estricta: minimo ⊂ memoria ⊂ gobernanza ⊂ completo.
- El mapeo gen ↔ capacidad vive en un gen nuevo (gen-perfiles) y su espejo en
  `schema.py`, no en 26 ediciones de genes.
- El estado efectivo es `genome/perfil.md` (markdown, frontmatter plano, greppable).
- Apagar nunca borra.

## Ideas adoptadas en esta entrega
1. Toggles por pieza con presets (claude-mem, obsidian-wiki, core-plugins de Obsidian).
2. Hooks que se pueden apagar sin desinstalar (obsidian-wiki `--no-hooks`).
3. Núcleo no desactivable, como los plugins core que Obsidian no deja quitar del todo.

## Ideas diferidas (backlog del plan)
- Lint de `.base` (kepano) y validación de `.canvas` (kepano).
- Plan con hash aprobado antes de `apply` (claude-obsidian).
- Escritura atómica con lock para JSONL e índice (obsidian-wiki, Obsidian `Vault.process`).
- `hot.md` con tope de palabras que lint haga cumplir (obsidian-wiki).
- Catálogo de blueprints con versiones y requisito mínimo (obsidian-releases).
- Empaquetado como plugin/skill de marketplace (kepano, claude-mem).

## Lo que NO se adopta
- Worker HTTP, SQLite, FTS5, vectores (claude-mem): contradicen "sin servidores, sin
  vectores".
- Compresión automática de observaciones con API (claude-mem): el destilado es juicio
  del agente bajo compuerta.
- Dependencia de la CLI de Obsidian en hooks o CI (kepano): sigue siendo equivalente
  opcional del operador (`ops/runbook-obsidian-cli.md`).
