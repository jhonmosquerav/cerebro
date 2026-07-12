# Propuestas EVOLVE — integración del núcleo mecánico al genoma

> **Bajo compuerta** ([[gen-compuerta-mutacion]]): estos archivos solo
> PROPONEN. El genoma quedó **intacto** durante toda la construcción del
> enforcement mecánico (2026-07-12) — los validadores son `[infra]`, como
> los hooks de A-02; que los GENES los consuman es mutación y espera tu OK.

Al aprobar una propuesta: aplicar el diff al gen, subir `version`, línea en
`genome/events.jsonl` (usa `python tools/cerebro.py events append` para que
lleve hash-chain), 1 commit, re-sincronizar `AGENTS.md` (`mirror --fix`).

| Propuesta | Muta | Qué integra |
|---|---|---|
| `prop-f0-01` | gen-lint v4→v5 | los detectores mecánicos como fuente de candidatos de LINT |
| `prop-f0-02` | gen-onboard v4→v5 | el aplicado del manifiesto pasa a ser `onboard apply` (mecánico) |
| `prop-f0-03` | gen-auto-auditoria v4→v5 | los detectores alimentan al maker de AUDIT |
| `prop-f0-04` | gen-xray v1 (NUEVO) + fila en CLAUDE.md | la operación XRAY: deriva declarado vs inferido |
| `prop-f0-05` | gen-compuerta-mutacion v1→v2 | toda línea nueva del ledger lleva hash-chain (`events append`) |

Orden recomendado: 01 → 02 → 05 → 03 → 04 (cada una es independiente; el
orden solo minimiza referencias adelantadas).
