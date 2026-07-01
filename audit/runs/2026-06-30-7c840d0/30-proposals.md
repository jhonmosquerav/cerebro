---
run_id: 2026-06-30-7c840d0
fecha: 2026-06-30
rol: orquestador
gen_version: gen-auto-auditoria v3
tipo: proposals
---

# 30 — Propuestas (≤3, rankeadas) · GATE HUMANO

Ensambladas por el orquestador a partir de `20-auditor.md`. `N = min(3, confirmadas) = 3`.
El humano aprueba/rechaza **una por una**. Nada se aplica sin tu OK.

- Maker: equipo de 7 especialistas (ver `10-maker.md`).
- Auditor independiente: 13 confirmadas · 1 refutada (C10) · 1 degradada (C2 sev5→2).
- Desempate aplicado: (1) impacto; (2) prioridad de clase por orden de filas; (3) ruta alfabética.

---

## P1 — Unificar el default de `sensibilidad` entre genes activos
- id: `AUDIT-2026-06-30-P1` (candidato C1)
- fecha: 2026-06-30
- clase: **contradicción entre genes activos** · sev 5 · alcance 2 · **impacto 52** · status: **applied**
- motivo: Dos genes activos definen distinto el valor por defecto de `sensibilidad`. Cuando el manifiesto fija `default_sensibilidad: confidencial` (caso legal/salud previsto por el propio genoma), `gen-frontmatter-obligatorio` ordena nacer `interno` y `gen-confidencialidad` ordena nacer `confidencial`. La divergencia decide si una página se ancla, se fusiona y se cita textual → dominio de confidencialidad (sev 5).
- evidencia:
  - `genome/genes/gen-frontmatter-obligatorio.md:11-12` → "`sensibilidad` ([[gen-confidencialidad]], **default `interno`**)"
  - `genome/genes/gen-confidencialidad.md:9-10` → "(default tomado de `default_sensibilidad` del manifiesto si lo declara …; **si no existe, `interno`**)"
- diff:
  ```diff
  - sensibilidad ([[gen-confidencialidad]], default `interno`)
  + sensibilidad ([[gen-confidencialidad]], default = `default_sensibilidad` del manifiesto;
  +   si no se declara, `interno`)
  ```
  Se edita el enunciado-resumen de `gen-frontmatter-obligatorio` (no la regla detallada de `gen-confidencialidad`, que es la fuente de verdad del eje).
- ruta de aplicación: toca **genoma** → [[gen-compuerta-mutacion]] (línea en `events.jsonl` + `version` de `gen-frontmatter-obligatorio` 3→4 + commit + **re-sync `AGENTS.md`**); luego [[gen-migracion-genoma]] re-valida manifiesto y páginas.

## P2 — Añadir el bloque `graph_lens` a los 5 blueprints
- id: `AUDIT-2026-06-30-P2` (candidato C4)
- fecha: 2026-06-30
- clase: **violación de invariante impuesta por un gen** · sev 4 · alcance 4 · **impacto 44** · status: **applied**
- motivo: `gen-onboard` v4 + `gen-graph-lens` v2 declaran que ONBOARD persiste la elección de backend en `graph_lens.backend`, pero ningún blueprint contiene la clave `graph_lens` → el flujo "pregunta una vez y registra" no tiene nodo YAML donde escribir. Rompe el contrato campo↔gen. (Gana el desempate sobre P3 por ruta alfabética: `agencia.yaml` < `legal.yaml`.)
- evidencia:
  - `genome/genes/gen-onboard.md:14-15` y `gen-graph-lens.md:12-14` → persisten en `graph_lens.backend`.
  - `onboard/company.example.yaml:62-67` tiene el bloque; `grep graph_lens onboard/blueprints/*` → **0 coincidencias** (los 5 terminan en `taxonomy:`).
- diff: anexar a cada `onboard/blueprints/*.yaml` (tras `taxonomy:`):
  ```yaml
  graph_lens:
    enable: false
    backend:                       # el agente lo pregunta 1 vez y lo registra aquí
    exclude_sensibilidad: [confidencial]
    out_dir: graphify-out
  ```
- ruta de aplicación: **config de onboard** (ni gen ni wiki) → cambio directo bajo gate + línea en `log.md` (sin `events.jsonl`).

## P3 — Fijar `default_sensibilidad: confidencial` en los blueprints sensibles
- id: `AUDIT-2026-06-30-P3` (candidato C3)
- fecha: 2026-06-30
- clase: **violación de invariante impuesta por un gen** · sev 4 · alcance 4 · **impacto 44** · status: **applied**
- motivo: `salud.yaml` y `legal.yaml` no fijan `default_sensibilidad`, así que en una clínica/bufete onboardeado cada historia clínica/minuta nace `interno` → se ancla en `index.md`, se fusiona en CONSOLIDATE y **entra a la copia staging de graphify** (que solo excluye `confidencial`). El propio `gen-confidencialidad` afirma que estos sectores fijan `confidencial`; la omisión lo contradice.
- evidencia:
  - `genome/genes/gen-confidencialidad.md:9-10` → "dominios sensibles como legal/salud suelen fijar `confidencial`".
  - `grep default_sensibilidad onboard/blueprints/*` → **0 coincidencias**; `salud.yaml` marca `pacientes` SENSIBLE en comentario pero no implementa el campo que el gen lee.
- diff: añadir a `salud.yaml` y `legal.yaml`:
  ```yaml
  default_sensibilidad: confidencial   # dominio sensible: páginas nuevas nacen confidencial
  ```
  (idealmente, refinar por taxonomía para que solo `pacientes/`,`clientes/`,`casos/` nazcan `confidencial`).
- ruta de aplicación: **config de onboard** → cambio directo bajo gate + línea en `log.md`.

---

## Fuera del corte (siguiente en fila si rechazas alguna)
- **C5** (impacto 43) — la cápsula `ingesta-de-fuente` no compone `gen-confidencialidad` (sin PII-halt; ancla sin exclusión). Defecto de confidencialidad sólido; entra si rechazas P3 o P2.
- **C6** (impacto 41) — filtro de staging de graphify frágil (grep literal + aplanamiento de rutas + sin verificación bloqueante).

## Confirmadas de menor impacto (registro; no entran al Top-3)
C7 (33, index.md desactualizado), C8 (33→alcance 1, runbook "backend local"), C9 (26→alcance 2, `FROM "sim"` inexistente), C11/C12/C13/C15 (nits de doc/redundancia), C14 (fuga indirecta por metadatos en QUERY), C2 (degradado a 21: `gen-vigencia-normativa` es seed, no gen activo).

---

## Decisiones del humano
Veredicto registrado (2026-06-30). La corrida queda reconstruible por SHA:
- P1: ✅ **approved → applied** — `gen-frontmatter-obligatorio` v3→v4; línea en `events.jsonl`; `AGENTS.md` re-verificado en sync (CLAUDE.md no cambió).
- P2: ✅ **approved → applied** — bloque `graph_lens` añadido a los 5 blueprints; línea en `log.md`.
- P3: ✅ **approved → applied** — `default_sensibilidad: confidencial` en `salud.yaml` y `legal.yaml`; línea en `log.md`.

Revertir cualquiera → `git revert` del commit correspondiente + marcar `status: reverted` aquí.

---

## Ronda 2 — gate posterior sobre confirmadas fuera del Top-3 (2026-06-30)
El humano decidió actuar también sobre las siguientes confirmadas (C5, C6) + una adyacente (C8):
- **P4 (C5)**: ✅ approved → applied — `cap-ingesta-de-fuente` v1→v2 compone `gen-confidencialidad` (paso de sensibilidad + PII-halt; anclado condicionado). Genoma → `events.jsonl`. impacto 43.
- **P5 (C6)**: ✅ approved → applied — filtro de staging de graphify endurecido (patrón tolerante + rutas preservadas + verificación bloqueante). Doc → `log.md`. impacto 41.
- **C8**: ✅ approved → applied — runbook "backend local" → "con el backend de `graph_lens.backend`". Doc → `log.md`. impacto 31.

- **C7**: ✅ approved → applied — `index.md` actualizado (anclas de `GRAPH`/gen-graph-lens + visualización; `updated` 2026-06-30). Wiki/índice → `log.md`. impacto 33.

Restantes confirmadas de menor impacto (C9 `FROM "sim"`, C11–C15, C2-degradado) siguen anotadas, sin aplicar.
