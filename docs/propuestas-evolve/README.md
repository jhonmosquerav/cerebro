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
| `prop-f0-06` | gen-lint v5→v6 | LNK-03 enlace sugerido: el detector preventivo de conectividad (depende de F0-01) |
| `prop-f0-07` | gen-graph-lens v3→v4 + gen-jerarquizacion-indice v2→v3 | la mitad estructural de GRAPH deja de necesitar backend externo (`graph`) |

Orden recomendado: 01 → 02 → 05 → 03 → 04 → 06 → 07. Las cinco primeras son
independientes entre sí (el orden solo minimiza referencias adelantadas); 06
supone 01 aplicada, y 07 es independiente pero se lee mejor al final.

Las dos últimas (2026-07-26) nacen del repaso de ecosistemas comparables
—AgentCairn, Bedrock, claude-obsidian, librarian-mcp— y de una constatación
incómoda: tres genes activos declaraban consumir señales de grafo que el camino
por defecto no producía.
