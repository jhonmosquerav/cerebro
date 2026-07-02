---
run_id: 2026-07-02-51690cb
fecha: 2026-07-02
gen_version: gen-auto-auditoria v3
tipo: snapshot
motivo: cierre de Fase A (backlog 2026-07-01-810f24e) — AUDIT sobre el genoma mutado
---

# 00 — Snapshot de identidad de la corrida

Identidad reproducible de esta auto-auditoría (regla: [[gen-auto-auditoria]]).

## Estado de git
- `git -C D:/cerebro rev-parse HEAD` → `51690cb03abeaf6ab50f23f46ce6911e91f69fb1`
- short-SHA → `51690cb`
- `git status --porcelain` → **vacío (árbol limpio)** al inicio de la corrida.
- HEAD: `chore(memoria): episodico de sesion 86919843 - tanda EVOLVE aplicada`
- **run-id = `2026-07-02-51690cb`** (`<YYYY-MM-DD>-<short-SHA>`). Idempotente por SHA: misma base ⇒ misma corrida reconstruible.

> Nota de transparencia: la carpeta `audit/runs/2026-07-02-51690cb/` que contiene este
> artefacto se crea DESPUÉS de capturar el SHA, por lo que al re-correr la auditoría el árbol
> ya no estará limpio (tendrá estos artefactos sin commitear). La identidad canónica de la
> corrida es el SHA `51690cb`, capturado con árbol limpio.

## Contexto de la corrida
Es la primera auditoría tras la **tanda EVOLVE completa** de la evaluación
`2026-07-01-810f24e` (20 mutaciones: 5 genes nuevos, genoma 20→25, cápsula v5, 48 eventos)
y tras la ejecución de la **Fase A** (hooks reales v1, permissions, ops/, staging allowlist).
El backlog exige esta corrida como cierre de fase. El foco natural: coherencia del genoma
recién mutado (las 7 propuestas se redactaron en paralelo contra el estado pre-tanda y se
aplicaron encadenadas — la clase de defecto más probable es contradicción o desalineación
entre genes/documentos editados por propuestas distintas).

## Criterio aplicado
- Rúbrica: `gen-auto-auditoria` **v3** (`impacto = severidad*10 + alcance`; tabla de severidad y desempate por orden de filas).
- Confidencialidad: las 2 páginas de `wiki/episodic/` son `sensibilidad: interno` — se citan por link/campo con normalidad; no hay páginas `confidencial` en el árbol.

## Alcance auditado (88 archivos trackeados; `.git/` excluido)
- `CLAUDE.md`, `AGENTS.md`, `index.md`, `log.md`, `README.md`, `LICENSE`
- `genome/` → **25 genes** en `genome/genes/`, `genome/capsules/ingesta-de-fuente.md` (v5), `genome/company-profile.md`, `genome/events.jsonl` (48 líneas)
- `onboard/` → `company.example.yaml` (con `identity`, `ciclo_de_vida`, `hub_umbral`), `README.md`, `blueprints/` (5 sectores + README)
- `wiki/` → 2 páginas en `episodic/`, `.gitkeep` en tiers (incluido `archive/` nuevo)
- `dashboards/` → paneles + `graph/00-leeme.md`
- `.obsidian/` (preset), `.claude/settings.json` + `.claude/hooks/*.sh` + `.claude/hooks/README.md`, `.gitignore`
- `ops/` → `runbook-git-seguro.md`, `backup/`
- `audit/README.md` (las corridas y evaluaciones previas son registro histórico claveado a SHA: NO se auditan como estado vigente)

## Equipo de auditoría (maker = 4 especialistas; auditor = pase independiente)
Esta corrida usa subagentes como optimización (canon = hand-off en disco, `gen-auto-auditoria`):
1. **Coherencia del genoma post-tanda** — contradicciones/redundancia/obsolescencia entre los 25 genes y la cápsula v5; foco en piezas editadas por propuestas distintas (gen-ingest, gen-query, gen-consolidate, cápsula) y en genes nuevos vs preexistentes.
2. **Reproducibilidad, sincronización y enlaces** — AGENTS.md≡CLAUDE.md, versión-de-gen-en-disco ↔ última línea de events.jsonl por target, integridad JSONL, .gitignore, resolución de `[[wiki-links]]`, frontmatter de las páginas wiki, frescura de index.md.
3. **Operaciones, gobernanza y manifiesto** — tabla de operaciones ↔ genes (incluida la fila nueva CHECKPOINT), resumen-de-una-línea del índice de genes ↔ canon de cada gen, contrato campo↔gen del manifiesto (`identity`, `ciclo_de_vida`, `hub_umbral`, `graph_lens`) en example + 5 blueprints.
4. **Confidencialidad, seguridad, hooks y ops** — invariantes ("confidencial nunca sale", anti-inyección, excepción de purga), coherencia genes↔hooks reales↔staging allowlist↔runbooks de ops, dashboards.
