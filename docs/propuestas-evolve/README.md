# Propuestas EVOLVE — integración del núcleo mecánico al genoma

> **Gate resuelto el 2026-07-27**: el operador revisó las siete una por una y
> aprobó **seis**; `prop-f0-04` quedó **aplazada hasta la Fase B**. Las seis
> aprobadas están **aplicadas** (7 mutaciones, porque `gen-lint` recibió dos:
> v4→v5 y v5→v6), cada una con su línea encadenada en `genome/events.jsonl` y
> su commit. El genoma dejó de estar intacto: pasó de 25 genes v-mixtas a 25
> genes con el núcleo mecánico declarado.

Al aprobar una propuesta: aplicar el diff al gen, subir `version`, línea en
`genome/events.jsonl` (usa `python tools/cerebro.py events append` para que
lleve hash-chain), 1 commit, re-sincronizar `AGENTS.md` (`mirror --fix`).

| Propuesta | Muta | Qué integra | Estado |
|---|---|---|---|
| `prop-f0-01` | gen-lint v4→v5 | los detectores mecánicos como fuente de candidatos de LINT | ✅ aplicada 2026-07-27 |
| `prop-f0-02` | gen-onboard v4→v5 | el aplicado del manifiesto pasa a ser `onboard apply` (mecánico) | ✅ aplicada 2026-07-27 |
| `prop-f0-03` | gen-auto-auditoria v4→v5 | los detectores alimentan al maker de AUDIT | ✅ aplicada 2026-07-27 |
| `prop-f0-04` | gen-xray v1 (NUEVO) + fila en CLAUDE.md | la operación XRAY: deriva declarado vs inferido | ⏸ **aplazada hasta Fase B** |
| `prop-f0-05` | gen-compuerta-mutacion v1→v2 | toda línea nueva del ledger lleva hash-chain (`events append`) | ✅ aplicada 2026-07-27 |
| `prop-f0-06` | gen-lint v5→v6 | LNK-03 enlace sugerido: el detector preventivo de conectividad | ✅ aplicada 2026-07-27 |
| `prop-f0-07` | gen-graph-lens v3→v4 + gen-jerarquizacion-indice v2→v3 | la mitad estructural de GRAPH deja de necesitar backend externo (`graph`) | ✅ aplicada 2026-07-27 |

Orden en que se aplicaron: 01 → 02 → 05 → 03 → 06 → 07a → 07b (06 supone 01,
porque muta el mismo gen encima de la versión que 01 crea).

## Por qué F0-04 quedó fuera

Es la única que **crea** un gen (25 → 26) y la única cuyo valor no se ha visto:
la componente `deriva` de `health` sale `N/A` porque XRAY nunca corrió sobre un
vault poblado. Aprobarla ahora sería meter al genoma una operación que nadie ha
ejercitado. Se re-presenta cuando la Fase B dé corpus real. `cerebro xray` sigue
disponible como infra mientras tanto.

Las dos últimas (2026-07-26) nacen del repaso de ecosistemas comparables
—AgentCairn, Bedrock, claude-obsidian, librarian-mcp— y de una constatación
incómoda: tres genes activos declaraban consumir señales de grafo que el camino
por defecto no producía.
