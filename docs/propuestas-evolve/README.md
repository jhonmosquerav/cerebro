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
| `prop-f0-04` | gen-xray v1 (NUEVO) + fila en CLAUDE.md | la operación XRAY: deriva declarado vs inferido | ✅ aplicada 2026-08-07 (Fase B cerrada: condición cumplida) |
| `prop-f0-05` | gen-compuerta-mutacion v1→v2 | toda línea nueva del ledger lleva hash-chain (`events append`) | ✅ aplicada 2026-07-27 |
| `prop-f0-06` | gen-lint v5→v6 | LNK-03 enlace sugerido: el detector preventivo de conectividad | ✅ aplicada 2026-07-27 |
| `prop-f0-07` | gen-graph-lens v3→v4 + gen-jerarquizacion-indice v2→v3 | la mitad estructural de GRAPH deja de necesitar backend externo (`graph`) | ✅ aplicada 2026-07-27 |
| `prop-f0-08` | gen-frontmatter-obligatorio v6→v7 | los **campos** se extienden como los verbos (`campos_extra`) — cierra H-08 | ✅ aplicada 2026-07-29 |
| `prop-f0-09` | gen-identidad-de-pagina v2→v3 | el `resultado` del ledger es vocabulario cerrado y validado — cierra H-09 | ✅ aplicada 2026-07-29 |
| `prop-f0-10` | cap-ingesta-de-fuente v5→v6 + gen-ingest v3→v4 | el eslabón del derivado para fuentes no legibles — cierra H-06 | ✅ aplicada 2026-07-29 |
| `prop-f0-11` | gen-onboard v5→v6 | avisar si la taxonomía no cubre los tipos declarados — cierra H-07 | ✅ aplicada 2026-07-29 |
| `prop-f0-12` | gen-migracion-genoma v1→v2 + gen-compuerta-mutacion v2→v3 | doctrina de distribución: cadena por vault + evento `genome_adopted` — cierra H-10 | ✅ aplicada 2026-08-07 |

Orden en que se aplicaron: 01 → 02 → 05 → 03 → 06 → 07a → 07b (06 supone 01,
porque muta el mismo gen encima de la versión que 01 crea).

## Por qué F0-04 quedó fuera

Es la única que **crea** un gen (25 → 26) y la única cuyo valor no se ha visto:
la componente `deriva` de `health` sale `N/A` porque XRAY nunca corrió sobre un
vault poblado. Aprobarla ahora sería meter al genoma una operación que nadie ha
ejercitado. Se re-presenta cuando la Fase B dé corpus real. `cerebro xray` sigue
disponible como infra mientras tanto.

F0-06 y F0-07 (2026-07-26) nacen del repaso de ecosistemas comparables
—AgentCairn, Bedrock, claude-obsidian, librarian-mcp— y de una constatación
incómoda: tres genes activos declaraban consumir señales de grafo que el camino
por defecto no producía.

## La tanda del piloto (F0-08…F0-11, 2026-07-29)

Estas cuatro **no salen de leer el repo: salen de usarlo**. Son los hallazgos
H-06 a H-09 del piloto de Fase B (`C:\cerebro-piloto`, `piloto/hallazgos.md`),
encontrados al construir un corpus de 73 fuentes reales y correr un ONBOARD y un
primer lote de ingesta de verdad.

Prioridad recomendada, y el orden importa:

1. **F0-09** primero. Rompe la cobertura de `health`, que es el indicador con el
   que se va a medir el avance de B-02 lote a lote. Medir con un contador que
   puede marcar 0 cuando van 40 haría inútil el seguimiento.
2. **F0-08** después. Cada comparación nueva suma un aviso FM-04 permanente y
   baja la higiene por cumplir un gen aprobado. Con 4 documentos son 2 avisos;
   con 73 serán decenas, y entonces nadie lee los avisos.
3. **F0-10** cuando se retome B-02: formaliza lo que el piloto ya hace.
4. **F0-11** es la más pequeña y la primera que se puede recortar.

Las dos primeras conviene aplicarlas **antes** de escalar la ingesta: arreglarlas
con 4 documentos ingeridos cuesta nada; con 73 hay que revisar todas las páginas.
