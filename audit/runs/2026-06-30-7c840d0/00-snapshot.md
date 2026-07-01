---
run_id: 2026-06-30-7c840d0
fecha: 2026-06-30
gen_version: gen-auto-auditoria v3
tipo: snapshot
---

# 00 — Snapshot de identidad de la corrida

Identidad reproducible de esta auto-auditoría (regla: [[gen-auto-auditoria]]).

## Estado de git
- `git -C D:/cerebro rev-parse HEAD` → `7c840d072fe1687d786077afc254d86e86ee3212`
- short-SHA → `7c840d0`
- `git status --porcelain` → **vacío (árbol limpio)** al inicio de la corrida.
- HEAD: `feat(genome): gen-onboard v4 - ONBOARD pregunta y registra el backend de la lente`
- **run-id = `2026-06-30-7c840d0`** (`<YYYY-MM-DD>-<short-SHA>`). Idempotente por SHA: misma base ⇒ misma corrida reconstruible.

> Nota de transparencia: la carpeta `audit/runs/2026-06-30-7c840d0/` que contiene este
> artefacto se crea DESPUÉS de capturar el SHA, por lo que al re-correr la auditoría el árbol
> ya no estará limpio (tendrá estos artefactos sin commitear). La identidad canónica de la
> corrida es el SHA `7c840d0`, capturado con árbol limpio.

## Criterio aplicado
- Rúbrica: `gen-auto-auditoria` **v3** (`impacto = severidad*10 + alcance`; tabla de severidad y desempate por orden de filas).
- Confidencialidad: no aplica redacción de valores — `wiki/` está vacío (solo `.gitkeep`); toda la evidencia es texto de genoma/configuración, no datos sensibles.

## Alcance auditado (52 archivos de contenido; `.git/` excluido)
- `CLAUDE.md`, `AGENTS.md`, `index.md`, `log.md`, `README.md`, `LICENSE`
- `genome/` → 20 genes en `genome/genes/`, `genome/capsules/ingesta-de-fuente.md`, `genome/company-profile.md`, `genome/events.jsonl`
- `onboard/` → `company.example.yaml`, `README.md`, `blueprints/` (5 sectores + README)
- `dashboards/` → 4 paneles + `graph/00-leeme.md`
- `.obsidian/` (preset), `.claude/settings.json` + `.claude/hooks/README.md`, `.gitignore`
- `audit/README.md`

## Equipo de auditoría (maker = 7 especialistas; auditor = pase independiente)
Esta corrida usó subagentes como optimización (canon = hand-off en disco, `gen-auto-auditoria:42`):
1. **Coherencia del genoma** — contradicciones/redundancia/obsolescencia entre genes.
2. **Reproducibilidad y sincronización** — AGENTS.md≡CLAUDE.md, versión-gen↔events.jsonl, integridad JSONL, .gitignore, árbol git.
3. **Enlaces y frontmatter** — resolución de todo `[[wiki-link]]`, validez de frontmatter, frescura de index.md.
4. **Operaciones y gobernanza** — matriz operación↔gen, meta-auditoría (AUDIT obedece su propio protocolo), rutas de mutación bajo gate.
5. **Onboard y manifiesto** — contrato campo↔gen entre `company.example.yaml`/blueprints y los genes que los leen.
6. **Confidencialidad, vigencia y seguridad** — invariante "confidencial nunca sale", caducidad en dominios de seguridad, fugas indirectas.
7. **Visualización, dashboards y hooks** — validez Dataview, runbook de grafo, honestidad de los hooks-stub.
