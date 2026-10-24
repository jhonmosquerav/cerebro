---
tipo: plan-de-implementacion
fecha: 2026-10-20
spec: docs/specs/2026-10-20-perfiles-capacidades-design.md
estado: en-ejecucion
absorbe:
  - docs/plans/2026-07-12-enforcement-mecanico-plan.md (ejecutado 2026-07-12..27; cerrado)
  - docs/roadmap-endurecimiento.md → Fase 4 (distribución), desbloqueada al cerrar Fase 1
  - docs/specs/2026-09-03-obsidian-nativo-design.md → "Fuera de alcance" (OBS-02..04, ya aplicados 2026-09-07)
  - docs/caso-fase-b.md → candidatos a EVOLVE del piloto aún sin gate (se listan abajo como backlog)
---

# Plan único — perfiles de instalación y capacidades activables

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (ejecución
> inline en esta sesión). Pasos con checkbox. TDD por tarea: test en rojo →
> implementación mínima → verde. Infra en commits propios; cada mutación de genoma en su
> commit firmado con línea encadenada en `genome/events.jsonl`.

**Goal:** que CEREBRO se instale con un perfil (`minimo` · `memoria` · `gobernanza` ·
`completo`) y que cada capacidad (`memoria`, `ciclo_de_vida`, `evolucion`, `auditoria`,
`visualizacion`, `grafo`) se pueda encender o apagar por manifiesto, con efecto real en
agente, hooks, CLI y lint — sin dependencias nuevas y sin cambiar el hash de los vaults
que no declaran perfil.

**Por qué este plan es el único:** el plan del 2026-07-12 se ejecutó completo (Fase 0 y
Fase C cerradas el 2026-07-27); el roadmap dejó la Fase 4 bloqueada hasta cerrar la Fase 1,
que cerró el 2026-08-07; el backlog de la spec Obsidian se aplicó el 2026-09-07. Lo que
quedaba vivo en los tres es **distribución**: este plan la empieza (4.1) y deja el resto
como backlog ordenado al final.

## Restricciones

- Cero dependencias (stdlib + `sh` POSIX). Salida determinista. Mensajes en español.
- `worked/` debe regenerar byte a byte sin tocar sus esperados (ausencia de perfil ⇒
  `completo` ⇒ sin `genome/perfil.md`).
- Nada se borra al apagar. Núcleo no desactivable.
- Genoma: 3 mutaciones (gen-perfiles nuevo, gen-onboard v8, gen-lint v8), compuerta
  abierta por instrucción explícita del operador en esta sesión.

---

### Tarea 1 — Esquema y módulo `profile`
- [ ] `schema.py`: `CAPABILITIES` (id → descripción, genes, operaciones, comandos,
      carpetas), `PROFILES` (escalera), `CORE_GENES`, `capability_of(gen_id)`.
- [ ] `tools/cerebro_core/profile.py`: `effective(manifest)` → dict cap→bool;
      `render(manifest, date)` → `genome/perfil.md`; `read_applied(root)` → dict desde
      el frontmatter; `is_on(root, cap)` (sin archivo ⇒ True); `edit_manifest(...)` para
      `set/enable/disable` (edición textual de solo `profile:` y `capabilities:`).
- [ ] Tests `tests/test_profile.py`: escalera estricta; todo gen del repo está en núcleo o
      en exactamente una capacidad; `effective` con overrides; render determinista;
      edición textual conserva el resto del manifiesto.

### Tarea 2 — Manifiesto y ONBOARD
- [ ] `manifest.py`: propiedades `profile`, `capabilities`, `declares_profile`; validación.
- [ ] `onboard.py`: si declara perfil → escribe `genome/perfil.md`, línea `- Perfil:` en
      `## Estado`, evento `profile_applied` solo si cambia el conjunto efectivo.
- [ ] Tests: ejemplo (declara `completo`) escribe perfil y es idempotente; `worked/` intacto;
      cambiar `memoria`→`completo` añade un evento; misma fecha ⇒ mismo hash.

### Tarea 3 — LINT, CLI y gating
- [ ] `lint.py`: PRF-01 (error, deriva/ausente) y PRF-02 (aviso, sin declaración).
- [ ] `cerebro.py`: subcomando `profile [set|enable|disable]`; gating con exit 2 y
      `--ignore-profile` en `consolidate`, `health`, `xray`, `graph`.
- [ ] Tests CLI: `profile` imprime tabla; `disable grafo` + `onboard apply` ⇒ `graph`
      sale 2 y con `--ignore-profile` sale 0; lint PRF-01 tras editar manifiesto sin aplicar.

### Tarea 4 — Hooks
- [ ] `.claude/hooks/*.sh` y copia `.codex/hooks/*.sh`: helper `cap_on`; `pre-compact` y
      `stop` no-op con memoria apagada; `session-start` anuncia perfil.
- [ ] Prueba manual sobre vault temporal (memoria on/off) con la salida citada en el log.
- [ ] `.claude/hooks/README.md` (y `.codex/hooks/README.md`) documentan el gating.

### Tarea 5 — Genoma por compuerta
- [ ] `docs/propuestas-evolve/prop-prf-01..03.md` + fila en su README.
- [ ] gen-perfiles v1 (nuevo) · gen-onboard v7→v8 · gen-lint v7→v8; `CLAUDE.md` (regla de
      arranque, columna Capacidad, sección Perfiles, índice de genes, loop de memoria,
      validadores) + `mirror --fix`; 3 × `events append` + 3 commits firmados.

### Tarea 6 — Documentación e instalación
- [ ] `onboard/company.example.yaml` (bloque `profile`/`capabilities` comentado y activo),
      blueprints (bloque comentado), `onboard/README.md`, `tools/README.md`, `README.md`
      (instalación con perfiles), `.obsidian/types.json` (`perfil`, `cap_*`),
      `docs/revision-repos-2026-10-20.md`, roadmap Fase 4 desbloqueada, plan 2026-07-12
      marcado como absorbido.

### Tarea 7 — Cierre
- [ ] `verify` + suite en verde; push a `origin/main` alineado.
- [ ] `log.md`, episódico `wiki/episodic/2026-10-20-<session8>.md`, memoria del agente.

---

## Backlog que este plan deja ordenado (Fase 4, siguientes entregas)

1. ~~**4.2 Empaquetado instalable**~~ ✅ infra entregada 2026-10-20 (sesión hija):
   `cerebro.py init --profile <p> [--blueprint <s>]` (`cerebro_core/init_manifest.py`,
   `tests/test_init.py`), plugin mínimo (`.claude-plugin/marketplace.json` → `plugin/`,
   `tests/test_plugin.py`), README/tools/onboard documentados. Genoma intacto: la mención
   de `init` en gen-onboard espera compuerta en `docs/propuestas-evolve/prop-prf-04-*.md`.
2. ~~**4.3 Catálogo de blueprints**~~ ✅ 2026-10-23 (plan `2026-10-23-cierre-fase-4-plan.md`) con `versions`/`min_cerebro` al estilo
   `community-plugins.json` (obsidian-releases), consumido por `genome_adopted`.
3. ~~**4.4 Artículo del caso público colombiano**~~ ✅ 2026-10-23 `docs/caso-piscc-colombia.md` (roadmap Fase 4).
4. Candidatos de `docs/caso-fase-b.md` aún sin gate: pasan por EVOLVE cuando el uso los
   vuelva a señalar (regla de oro del roadmap: nada entra al genoma sin ejercitarse).
5. Ideas de la revisión de repos **no adoptadas aún** (ver `docs/revision-repos-2026-10-20.md`):
   lint de `.base` (pitfalls de fórmulas), validación mecánica de `.canvas`, escritura
   atómica con lock para JSONL, `hot.md` con tope de palabras, plan con hash para apply.
