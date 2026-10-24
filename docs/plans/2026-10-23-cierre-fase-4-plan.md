---
tipo: plan-de-implementacion
fecha: 2026-10-23
estado: en-ejecucion
spec: docs/specs/2026-10-23-catalogo-blueprints-design.md
cierra: Fase 4 del roadmap (4.3 y 4.4); sucede al plan 2026-10-20
---

# Cierre de la Fase 4 — catálogo de blueprints (4.3) y artículo del caso (4.4)

Instrucción del operador (sesión 2026-10-23): "termina la actualización de inicio a fin y
actualiza el README". Igual que el 2026-10-20, la instrucción end-to-end abre la compuerta
para lo que toque el genoma: se redacta la propuesta, se aplica con evento firmado y se
registra. Orden: infra con TDD primero (genoma intacto), después la mutación, al final
docs, artículo y push con checklist.

## Entrega 4.3 — catálogo

- [x] Spec en `docs/specs/2026-10-23-catalogo-blueprints-design.md`.
- [ ] `tests/test_blueprints.py` (rojo primero): catálogo del repo válido; CAT-01…CAT-06
      disparados sobre copia temporal; `manifest.validate` rechaza `min_cerebro` > versión;
      `init --blueprint` y `onboard apply` abortan sin escribir; CLI `blueprints` y `--json`.
- [ ] `tools/cerebro_core/blueprints.py`: semver, carga del catálogo, `check(root)`,
      `estado_manifiesto(root)`; `manifest.py`: propiedad `blueprint` + validación;
      `cerebro.py`: subcomando `blueprints [--json]` y línea en `verify`.
- [ ] `onboard/blueprints/catalog.yaml`; bloque `blueprint:` en los 6 blueprints y en los 3
      `worked/*/company.yaml` (para que no diverjan de su blueprint); bloque comentado en
      `company.example.yaml`. `tests/test_worked.py` debe seguir en verde sin regenerar nada.
- [ ] Docs de infra: `onboard/blueprints/README.md` (tabla con versión y requisito, cómo
      publicar una versión nueva), `onboard/README.md`, `tools/README.md`,
      `plugin/skills/cerebro/SKILL.md` (una línea: `blueprints` lista el catálogo).
- [ ] `docs/propuestas-evolve/prop-cat-01-catalogo-blueprints.md` + fila en su README;
      aplicar gen-onboard v9→v10 y gen-migracion-genoma v2→v3 con `events append` (2
      eventos, 2 commits firmados); `CLAUDE.md` + `mirror --fix`.

## Entrega 4.4 — artículo

- [ ] `docs/caso-piscc-colombia.md` con la voz editorial del operador (skills
      `redaccion-humana` + `redaccion-clara`), fuentes y límites explícitos, enlazado desde
      README y desde `worked/piscc-demo/review.md`.

## Cierre

- [ ] README: blueprints catalogados, verbo `blueprints`, fila XRAY, caso colombiano, lista
      de blueprints al día (seis, con seguridad territorial).
- [ ] Roadmap: 4.3 y 4.4 ✅, Fase 4 cerrada; este plan marcado.
- [ ] `verify` + suite en verde (Windows); `worked/` byte a byte.
- [ ] Commits firmados; checklist pre-push §2 del runbook; push a `origin/main`.
- [ ] `log.md`, episódico `wiki/episodic/2026-10-23-<session8>.md`, memoria del agente.
