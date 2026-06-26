# Loop de auto-auditoría — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir a CEREBRO la operación `AUDIT` (gen `gen-auto-auditoria`) que audita la propia base y propone las ≤3 mejoras de mayor impacto, de forma reproducible, con separación maker≠auditor y gate humano.

**Architecture:** Es un orquestador en markdown, no código. La detección reusa los chequeos de [[gen-lint]]/[[gen-consolidate]] sobre el *esqueleto* (frontmatter + grafo) y abre contenido solo de candidatos (drill-down). Un *maker* escribe candidatos a disco; un *auditor* (pasada fresca, solo lee `00-snapshot`+gen+`10-maker.md`) los refuta y re-puntúa; el orquestador ensambla ≤3 propuestas `pending`. La identidad del estado es el SHA de git; la rúbrica de impacto va embebida en el gen (gateada por `version`).

**Tech Stack:** Markdown + YAML frontmatter + JSONL. Git como identidad de estado y registro de mutaciones. Sin runtime, sin código ejecutable obligatorio. La verificación es un fixture con defectos plantados (`sim/_auditoria-fixture/`) cuyo `expected.md` es el oráculo determinista.

**Referencia de diseño:** [docs/superpowers/specs/2026-06-25-loop-auto-auditoria-design.md](../specs/2026-06-25-loop-auto-auditoria-design.md)

**Convención TDD del dominio:** "test" = el fixture + `expected.md` (oráculo). "Implementación" = el gen. "Correr el test" = ejecutar la operación AUDIT (leyendo el gen) sobre el fixture y comparar la salida con `expected.md`. El oráculo se deriva de la **fórmula del spec**, no del gen, así que puede (y debe) escribirse antes que el gen.

**Nota sobre la compuerta:** crear `gen-auto-auditoria` ES una mutación de genoma → pasa por [[gen-compuerta-mutacion]]. Hay un checkpoint de aprobación humana explícito en la Task 6 antes de registrar el evento.

---

## Estructura de archivos

**Fixture (banco de prueba aislado, NO toca el cerebro real):**
- Create: `sim/_auditoria-fixture/README.md` — qué es el fixture.
- Create: `sim/_auditoria-fixture/company.yaml` — manifiesto mínimo.
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-precio-abierto.md` — defecto D1 (gen).
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-precio-vigencia.md` — defecto D1 (gen).
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-clasifica-v1.md` — defecto D4 (gen obsoleto).
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-clasifica-v2.md` — el gen que subsume a v1.
- Create: `sim/_auditoria-fixture/wiki/index.md` — entrada del fixture.
- Create: `sim/_auditoria-fixture/wiki/semantic/seguridad/protocolo-bloqueo-loto.md` — D2 (vencido seguridad).
- Create: `sim/_auditoria-fixture/wiki/semantic/maquinas/prensa-p1.md` — cita el protocolo (alcance de D2) + D5 (link roto).
- Create: `sim/_auditoria-fixture/wiki/semantic/clientes/cliente-acme.md` — D3 (contradicción wiki).
- Create: `sim/_auditoria-fixture/wiki/semantic/casos/caso-acme.md` — D3 (contradicción wiki).
- Create: `sim/_auditoria-fixture/wiki/semantic/productos/widget-a.md` — D7 (redundancia).
- Create: `sim/_auditoria-fixture/wiki/semantic/productos/widget-a-detalle.md` — D7 (redundancia).
- Create: `sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x.md` — D8 (redundancia confidencial, prueba §8).
- Create: `sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x-copia.md` — D8.
- Create: `sim/_auditoria-fixture/expected.md` — oráculo (candidatos + scores + top-3).
- Create: `sim/_auditoria-fixture/regresion.md` — registro de corrida (se llena en Task 7-8).
- Create: `sim/_auditoria-fixture/audit/runs/.gitkeep` — donde la corrida de prueba escribe.

**Capacidad (cerebro real):**
- Create: `genome/genes/gen-auto-auditoria.md` — el gen nuevo con rúbrica embebida.
- Create: `audit/README.md` — qué es `audit/`.
- Create: `audit/runs/.gitkeep`.
- Modify: `CLAUDE.md` — tabla de operaciones (+AUDIT), índice de genes (+gen-auto-auditoria), mapa de memoria (+audit/).
- Modify: `index.md` — registrar `audit/` y la operación.
- Modify: `AGENTS.md` — re-sync exacto de `CLAUDE.md`.
- Modify: `genome/events.jsonl` — 1 línea por el alta del gen (append).
- Modify: `log.md` — 1 línea operativa.

---

## Task 1: Shell del fixture (mini-CEREBRO aislado)

**Files:**
- Create: `sim/_auditoria-fixture/README.md`
- Create: `sim/_auditoria-fixture/company.yaml`
- Create: `sim/_auditoria-fixture/wiki/index.md`
- Create: `sim/_auditoria-fixture/audit/runs/.gitkeep`

- [ ] **Step 1: Crear el README del fixture**

Create `sim/_auditoria-fixture/README.md`:

```markdown
# sim/_auditoria-fixture — prueba de capacidad (no es un vertical)

Base CEREBRO mínima con **defectos plantados y conocidos** para verificar la operación
`AUDIT` de forma reproducible. El prefijo `_` la marca como prueba de capacidad, no como
industria. Sandbox aislado: NO toca `D:/cerebro/genome` ni `D:/cerebro/wiki`.

## Defectos plantados
- D1 — contradicción entre 2 genes activos (`gen-fix-precio-abierto` vs `gen-fix-precio-vigencia`).
- D2 — info vencida en dominio de seguridad (`protocolo-bloqueo-loto`, citado por `prensa-p1`).
- D3 — contradicción entre 2 páginas wiki (`cliente-acme` vs `caso-acme`).
- D4 — gen obsoleto: `gen-fix-clasifica-v1` subsumido por `gen-fix-clasifica-v2` (trigger solapado).
- D5 — vacío: `prensa-p1` enlaza `[[manual-inexistente]]` (link roto).
- D6 — vacío: la taxonomía declara la categoría `proveedores` sin ninguna página.
- D7 — redundancia: `widget-a` y `widget-a-detalle` casi-duplicadas.
- D8 — redundancia confidencial: `expediente-x` y `expediente-x-copia` (prueba de [[gen-confidencialidad]]).

El top-3 esperado por la fórmula del gen está en `expected.md`.
```

- [ ] **Step 2: Crear el manifiesto mínimo**

Create `sim/_auditoria-fixture/company.yaml`:

```yaml
company:
  name: "FixtureCo"
  sector: "prueba de capacidad de auditoría"
  language: es
  domains: ["fixture.local"]

document_types: [ficha, protocolo, caso]

entities:
  clientes: []
  productos: ["widget-a"]
  maquinas: ["prensa-p1"]

roles:
  contributors: ["ops"]
  mutation_approver: "fundador"

relation_types: [tratada_segun, sobre_producto]

source_trust:
  oficial: 0.9
  interna: 0.7
  blanda: 0.4

sintesis_umbral: 3

seed_genes: []

# La categoria 'proveedores' se declara pero queda sin paginas -> defecto D6 (vacio).
taxonomy:
  semantic: [seguridad, maquinas, clientes, casos, productos, confidencial, proveedores]
  procedural: []
```

- [ ] **Step 3: Crear el index del fixture**

Create `sim/_auditoria-fixture/wiki/index.md`:

```markdown
---
title: FixtureCo — índice
type: meta
updated: 2026-06-25
---

# FixtureCo — mapa (fixture de auditoría)

Páginas-ancla del fixture. Base mínima con defectos plantados (ver `../README.md`).

- semantic/seguridad — [[protocolo-bloqueo-loto]]
- semantic/maquinas — [[prensa-p1]]
- semantic/clientes — [[cliente-acme]]
- semantic/productos — [[widget-a]]
```

- [ ] **Step 4: Crear el placeholder de corridas**

Create `sim/_auditoria-fixture/audit/runs/.gitkeep` with empty content.

- [ ] **Step 5: Verificar estructura**

Run: `git status --porcelain sim/_auditoria-fixture/`
Expected: 4 archivos nuevos listados (`README.md`, `company.yaml`, `wiki/index.md`, `audit/runs/.gitkeep`).

- [ ] **Step 6: Commit**

```bash
git add sim/_auditoria-fixture/
git commit -m "test(audit): shell del fixture de auto-auditoria"
```

---

## Task 2: Plantar defectos de genoma en el fixture (D1, D4)

**Files:**
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-precio-abierto.md`
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-precio-vigencia.md`
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-clasifica-v1.md`
- Create: `sim/_auditoria-fixture/genome-applied/gen-fix-clasifica-v2.md`

- [ ] **Step 1: Plantar D1 — gen que contradice (lado A)**

Create `sim/_auditoria-fixture/genome-applied/gen-fix-precio-abierto.md`:

```markdown
---
id: gen-fix-precio-abierto
trigger: la fuente menciona un precio
status: active
version: 1
---

Todo precio se cita SIEMPRE tal cual aparece, sin importar su fecha de vigencia.
La frescura del precio no es responsabilidad de QUERY.
```

- [ ] **Step 2: Plantar D1 — gen que contradice (lado B)**

Create `sim/_auditoria-fixture/genome-applied/gen-fix-precio-vigencia.md`:

```markdown
---
id: gen-fix-precio-vigencia
trigger: la fuente menciona un precio
status: active
version: 1
---

NUNCA se cita un precio cuya fecha de vigencia ya pasó. Si `valido_hasta < hoy`,
QUERY debe abstenerse de citarlo. Contradice directamente a [[gen-fix-precio-abierto]].
```

- [ ] **Step 3: Plantar D4 — gen obsoleto (v1, subsumido)**

Create `sim/_auditoria-fixture/genome-applied/gen-fix-clasifica-v1.md`:

```markdown
---
id: gen-fix-clasifica-v1
trigger: la fuente es una ficha de producto
status: active
version: 1
---

Las fichas de producto van a wiki/semantic/productos/. (Regla básica de clasificación.)
```

- [ ] **Step 4: Plantar D4 — gen que subsume a v1 (trigger solapado)**

Create `sim/_auditoria-fixture/genome-applied/gen-fix-clasifica-v2.md`:

```markdown
---
id: gen-fix-clasifica-v2
trigger: la fuente es una ficha de producto
status: active
version: 1
---

Las fichas de producto van a wiki/semantic/productos/ con SKU, material y proveedor,
y se enlazan al proveedor. Cubre por completo el caso de [[gen-fix-clasifica-v1]],
que queda obsoleto (mismo trigger, regla subsumida).
```

- [ ] **Step 5: Verificar y commit**

Run: `git status --porcelain sim/_auditoria-fixture/genome-applied/`
Expected: 4 archivos nuevos.

```bash
git add sim/_auditoria-fixture/genome-applied/
git commit -m "test(audit): plantar defectos de genoma D1 (contradiccion) y D4 (obsoleto)"
```

---

## Task 3: Plantar defectos de wiki en el fixture (D2, D3, D5, D6, D7, D8)

**Files:**
- Create: `sim/_auditoria-fixture/wiki/semantic/seguridad/protocolo-bloqueo-loto.md`
- Create: `sim/_auditoria-fixture/wiki/semantic/maquinas/prensa-p1.md`
- Create: `sim/_auditoria-fixture/wiki/semantic/clientes/cliente-acme.md`
- Create: `sim/_auditoria-fixture/wiki/semantic/casos/caso-acme.md`
- Create: `sim/_auditoria-fixture/wiki/semantic/productos/widget-a.md`
- Create: `sim/_auditoria-fixture/wiki/semantic/productos/widget-a-detalle.md`
- Create: `sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x.md`
- Create: `sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x-copia.md`

- [ ] **Step 1: D2 — protocolo de seguridad vencido**

Create `sim/_auditoria-fixture/wiki/semantic/seguridad/protocolo-bloqueo-loto.md`:

```markdown
---
title: Protocolo de bloqueo y etiquetado (LOTO)
type: concepto
tier: semantic
tags: [seguridad, protocolo]
confidence: 0.9
created: 2024-01-10
last_reinforced: 2024-01-10
decay_rate: low
valido_hasta: 2026-01-01
sources: [interna]
relations:
  usa: []
---

Procedimiento de bloqueo y etiquetado para intervenir la prensa de forma segura.
Vencido el 2026-01-01: requiere revalidación antes de citarse como vigente.
```

- [ ] **Step 2: D2 (alcance) + D5 (link roto) — página de máquina**

Create `sim/_auditoria-fixture/wiki/semantic/maquinas/prensa-p1.md`:

```markdown
---
title: Prensa P-1
type: entidad
tier: semantic
tags: [maquina]
confidence: 0.8
created: 2026-02-01
last_reinforced: 2026-02-01
decay_rate: medium
sources: [oficial]
relations:
  tratada_segun: ["[[protocolo-bloqueo-loto]]"]
  usa: ["[[manual-inexistente]]"]
---

Prensa hidráulica P-1. Se interviene según [[protocolo-bloqueo-loto]].
Referencia a [[manual-inexistente]] (página que no existe → vacío D5).
```

- [ ] **Step 3: D3 — contradicción wiki (lado A)**

Create `sim/_auditoria-fixture/wiki/semantic/clientes/cliente-acme.md`:

```markdown
---
title: Cliente Acme
type: entidad
tier: semantic
tags: [cliente]
confidence: 0.8
created: 2026-03-01
last_reinforced: 2026-06-01
decay_rate: medium
estado: activo
sources: [oficial]
relations:
  usa: []
---

Acme S.A. — cliente **activo**, con contrato vigente.
```

- [ ] **Step 4: D3 — contradicción wiki (lado B)**

Create `sim/_auditoria-fixture/wiki/semantic/casos/caso-acme.md`:

```markdown
---
title: Caso de baja — Acme
type: concepto
tier: semantic
tags: [cliente, caso]
confidence: 0.8
created: 2026-05-20
last_reinforced: 2026-05-20
decay_rate: medium
sources: [oficial]
relations:
  contradice: ["[[cliente-acme]]"]
---

Registro del cierre de cuenta: Acme fue **dado de baja** en mayo 2026.
Contradice el estado `activo` de [[cliente-acme]].
```

- [ ] **Step 5: D7 — redundancia (página A)**

Create `sim/_auditoria-fixture/wiki/semantic/productos/widget-a.md`:

```markdown
---
title: Widget A
type: entidad
tier: semantic
tags: [producto]
confidence: 0.8
created: 2026-04-01
last_reinforced: 2026-04-01
decay_rate: low
sources: [oficial]
relations:
  usa: []
---

Widget A — SKU WID-A. Material: acero. Proveedor: Norte.
```

- [ ] **Step 6: D7 — redundancia (página B, casi-duplicada)**

Create `sim/_auditoria-fixture/wiki/semantic/productos/widget-a-detalle.md`:

```markdown
---
title: Widget A (detalle)
type: entidad
tier: semantic
tags: [producto]
confidence: 0.8
created: 2026-04-02
last_reinforced: 2026-04-02
decay_rate: low
sources: [oficial]
relations:
  usa: []
---

Widget A, SKU WID-A. Fabricado en acero. Proveedor Norte. (Duplica a [[widget-a]].)
```

- [ ] **Step 7: D8 — redundancia confidencial (página A)**

Create `sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x.md`:

```markdown
---
title: Expediente X
type: entidad
tier: semantic
tags: [expediente]
confidence: 0.9
created: 2026-05-01
last_reinforced: 2026-05-01
decay_rate: low
sensibilidad: confidencial
sources: [oficial]
relations:
  usa: []
---

DATO SENSIBLE PLANTADO (no debe citarse en artefactos de auditoría):
titular Juan Pérez, DNI 12.345.678, diagnóstico reservado.
```

- [ ] **Step 8: D8 — redundancia confidencial (página B)**

Create `sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x-copia.md`:

```markdown
---
title: Expediente X (copia)
type: entidad
tier: semantic
tags: [expediente]
confidence: 0.9
created: 2026-05-02
last_reinforced: 2026-05-02
decay_rate: low
sensibilidad: confidencial
sources: [oficial]
relations:
  usa: []
---

DATO SENSIBLE PLANTADO duplicado: titular Juan Pérez, DNI 12.345.678.
Duplica a [[expediente-x]].
```

- [ ] **Step 9: Verificar y commit**

Run: `git status --porcelain sim/_auditoria-fixture/wiki/semantic/`
Expected: 8 archivos nuevos en 6 subcarpetas.

```bash
git add sim/_auditoria-fixture/wiki/semantic/
git commit -m "test(audit): plantar defectos wiki D2,D3,D5,D6,D7,D8"
```

---

## Task 4: Escribir el oráculo `expected.md` (deriva de la fórmula del spec)

**Files:**
- Create: `sim/_auditoria-fixture/expected.md`

La fórmula del spec: `impacto = severidad*10 + alcance`. Severidad por clase:
contradicción genes=5, vencido-seguridad=5, contradicción wiki=4, regla obsoleta=3,
vacío=2, redundancia=2. Desempate: prioridad de clase (orden de esa lista) → ruta alfabética.

- [ ] **Step 1: Calcular a mano cada candidato**

| ID | Clase | severidad | alcance | impacto |
|----|-------|-----------|---------|---------|
| D1 | contradicción genes | 5 | 2 | 52 |
| D2 | vencido-seguridad | 5 | 2 | 52 |
| D3 | contradicción wiki | 4 | 2 | 42 |
| D4 | regla obsoleta | 3 | 1 | 31 |
| D5 | vacío (link roto) | 2 | 1 | 21 |
| D6 | vacío (categoría sin cobertura) | 2 | 1 | 21 |
| D7 | redundancia | 2 | 2 | 22 |
| D8 | redundancia (confidencial) | 2 | 2 | 22 |

Top-3 por impacto: D1(52) y D2(52) empatan → prioridad de clase (genes antes que vencido) → **D1, D2**; luego **D3**(42). **Top-3 = [D1, D2, D3].**

- [ ] **Step 2: Escribir el oráculo**

Create `sim/_auditoria-fixture/expected.md`:

```markdown
# expected.md — oráculo del fixture de auto-auditoría

Derivado de la fórmula de `gen-auto-auditoria` (`impacto = severidad*10 + alcance`).
Mismo estado (mismo SHA) + misma versión del gen ⇒ mismo conjunto de candidatos y mismo
ranking. Solo la redacción de los diffs puede variar entre corridas.

## Conjunto de candidatos esperado (8)

| ID | Clase | severidad | alcance | impacto | Páginas/genes |
|----|-------|-----------|---------|---------|---------------|
| D1 | contradicción genes | 5 | 2 | 52 | gen-fix-precio-abierto, gen-fix-precio-vigencia |
| D2 | vencido-seguridad | 5 | 2 | 52 | protocolo-bloqueo-loto, prensa-p1 |
| D3 | contradicción wiki | 4 | 2 | 42 | cliente-acme, caso-acme |
| D4 | regla obsoleta | 3 | 1 | 31 | gen-fix-clasifica-v1 |
| D5 | vacío (link roto) | 2 | 1 | 21 | prensa-p1 → [[manual-inexistente]] |
| D6 | vacío (cat. sin cobertura) | 2 | 1 | 21 | taxonomy.semantic: proveedores |
| D7 | redundancia | 2 | 2 | 22 | widget-a, widget-a-detalle |
| D8 | redundancia (confidencial) | 2 | 2 | 22 | expediente-x, expediente-x-copia |

## Top-3 esperado (la salida que AUDIT debe proponer)

1. **D1** — contradicción entre `gen-fix-precio-abierto` y `gen-fix-precio-vigencia` (impacto 52).
2. **D2** — `protocolo-bloqueo-loto` vencido (valido_hasta 2026-01-01) y citado por `prensa-p1` (impacto 52).
3. **D3** — `cliente-acme` (estado activo) contradice a `caso-acme` (dado de baja) (impacto 42).

Desempate aplicado: D1 y D2 empatan en 52 → D1 primero por prioridad de clase (genes > vencido).

## Invariante de confidencialidad (§8 del spec)

D8 toca páginas `sensibilidad: confidencial`. En `10-maker.md` y `20-auditor.md` la evidencia
de D8 DEBE referenciar por `[[expediente-x]]` / `[[expediente-x-copia]]`, **sin** transcribir
el DNI, el titular ni el diagnóstico. Si algún artefacto cita ese contenido, la prueba FALLA.
```

- [ ] **Step 3: Commit**

```bash
git add sim/_auditoria-fixture/expected.md
git commit -m "test(audit): oraculo expected.md (candidatos + top-3 deterministas)"
```

---

## Task 5: Escribir `gen-auto-auditoria` (implementación)

**Files:**
- Create: `genome/genes/gen-auto-auditoria.md`

- [ ] **Step 1: Escribir el gen con la rúbrica embebida**

Create `genome/genes/gen-auto-auditoria.md`:

```markdown
---
id: gen-auto-auditoria
trigger: operación AUDIT (auto-auditoría de la base)
status: active
version: 1
---

AUDIT audita la propia base CEREBRO y PROPONE las **≤3 mejoras de mayor impacto**
(contradicciones, vacíos, reglas obsoletas o redundantes) de forma **reproducible**, con
separación maker≠auditor y gate humano. No aplica nada solo. No toca `raw/`.

## Disparador y meta
Disparador: invocación manual `AUDIT`. La corrida TERMINA solo cuando existe
`audit/runs/<run-id>/` con `00-snapshot`, `10-maker`, `20-auditor` y `30-proposals`, este
último con `N = min(3, candidatos confirmados por el auditor)` propuestas `status: pending`
(cada una con `id, fecha, motivo, evidencia, diff, score`), y hay una línea en `log.md`.

## Lectura en dos tiempos (respeta el presupuesto de contexto)
1. **Esqueleto:** lee solo frontmatter + grafo de relaciones de las páginas (no la prosa).
2. **Drill-down:** abre el contenido completo SOLO de las páginas que un detector marcó.

## Detección (reusa LINT + CONSOLIDATE; no la reimplementa)
- Huérfanos, contradicciones (`contradice`), vencidos (`valido_hasta < hoy`), verbos/campos
  fuera de esquema → [[gen-lint]].
- Duplicados / near-duplicados → [[gen-consolidate]].
- **Redundancia/obsolescencia de genoma (detector nuevo):** dos genes `active` con `trigger`
  solapado, o uno cuya regla quedó subsumida/contradicha por otro.
La **identidad** de cada candidato (qué página/gen, qué clase) la fija el detector; el LLM solo
juzga "¿importa?" y redacta el `diff`. Esto acota el no-determinismo a la prosa del diff.

## Roles maker ≠ auditor (barrera en disco)
- **Maker:** insumos = `00-snapshot` + este gen. Produce TODOS los candidatos con evidencia +
  `diff` + score. Escribe `10-maker.md`.
- **Auditor:** pasada fresca; únicos insumos = `00-snapshot` + este gen + `10-maker.md` (NO la
  memoria de sesión). Refuta cada candidato, verifica que la evidencia re-deriva el hallazgo y
  recalcula el score. Escribe `20-auditor.md`.
- El orquestador ensambla `30-proposals.md` (≤3 confirmadas, rankeadas). Nunca juzga lo propio.
- Subagentes son optimización opcional; el canon portable es el hand-off en disco.

## Rúbrica de impacto (versionada con este gen)
`impacto = severidad*10 + alcance`. `alcance` = nº de páginas/genes afectados.
`severidad` por clase de defecto:
| Clase | severidad |
|---|---|
| contradicción entre genes activos | 5 |
| info vencida en dominio de seguridad | 5 |
| contradicción entre páginas wiki | 4 |
| regla obsoleta/deprecable | 3 |
| vacío (link roto / categoría sin cobertura) | 2 |
| redundancia (duplicado) | 2 |
Desempate: prioridad de clase (orden de la tabla, de arriba a abajo) → ruta de archivo
alfabética. Top-N = las N de mayor impacto, con N = min(3, confirmadas por auditor).
Cambiar esta rúbrica = subir `version` = pasa por [[gen-compuerta-mutacion]].

## Estado, identidad y reproducibilidad
Identidad del estado: `git rev-parse HEAD` con árbol limpio (`git status`); si está sucio,
registra `HEAD + dirty` + lista de modificados. `run-id = <YYYY-MM-DD>-<short-SHA>`. Idempotente
por SHA: si ya existe `runs/` para ese SHA, no se duplica. Todo insumo, criterio (esta `version`)
y salida queda en disco → la corrida se reconstruye y reaudita sin re-correr el LLM.

## Confidencialidad (hereda [[gen-confidencialidad]])
Los artefactos de auditoría se persisten y commitean: para páginas `sensibilidad: confidencial`
la evidencia se expresa por `[[link]]`/id + campo, NUNCA transcribiendo el valor sensible.

## Gate humano y aplicación
Las ≤3 quedan `status: pending`. El humano aprueba/rechaza una por una. Aprobada que toca
genoma → por [[gen-compuerta-mutacion]] (events.jsonl + version + commit + re-sync `AGENTS.md`);
que toca wiki → cambio directo + línea en `log.md` + commit. Revertir = `git revert` + marcar
`status: reverted`. AUDIT consume LINT/CONSOLIDATE y deriva a [[gen-evolve]] las propuestas de
regla; no reimplementa esas operaciones.
```

- [ ] **Step 2: Verificar frontmatter y enlaces**

Run: `git status --porcelain genome/genes/gen-auto-auditoria.md`
Expected: 1 archivo nuevo (sin commit todavía — el commit ocurre en Task 6 tras la compuerta).

**NO COMMIT aún.** El alta del gen es una mutación de genoma y se finaliza en la Task 6 tras el checkpoint de aprobación.

---

## Task 6: Compuerta + registro del gen + sincronización

**Files:**
- Modify: `CLAUDE.md`
- Modify: `index.md`
- Create: `audit/README.md`
- Create: `audit/runs/.gitkeep`
- Modify: `genome/events.jsonl`
- Modify: `log.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: CHECKPOINT DE COMPUERTA (aprobación humana)**

Presentar al humano (fundador / `mutation_approver`):
- **Señal:** "Nueva capacidad de auto-auditoría reproducible aprobada en el spec 2026-06-25."
- **Diff:** `∅ → genome/genes/gen-auto-auditoria.md v1` (mostrar el contenido de Task 5).

Esperar **aprobación explícita**. Si se rechaza, detener el plan. Solo tras el "OK" seguir.

- [ ] **Step 2: Registrar la operación en `CLAUDE.md` (tabla de operaciones)**

Modify `CLAUDE.md`: en la tabla "## Operaciones (gatillos)", añadir tras la fila `EVOLVE`:

```markdown
| `AUDIT` | "auto-audítate / audita el cerebro" | Audita la base y PROPONE ≤3 mejoras de mayor impacto (contradicciones, vacíos, reglas obsoletas/redundantes), reproducible, con maker≠auditor y gate. Estado en `audit/runs/`. |
```

- [ ] **Step 3: Registrar el gen en el índice de genes de `CLAUDE.md`**

Modify `CLAUDE.md`: en "**Operativos**", cambiar la línea:

```markdown
- [[gen-onboard]] · [[gen-ingest]] · [[gen-bulk-ingest]] · [[gen-query]] · [[gen-lint]] · [[gen-consolidate]] · [[gen-evolve]]
```

por:

```markdown
- [[gen-onboard]] · [[gen-ingest]] · [[gen-bulk-ingest]] · [[gen-query]] · [[gen-lint]] · [[gen-consolidate]] · [[gen-evolve]] · [[gen-auto-auditoria]]
```

- [ ] **Step 4: Registrar `audit/` en el mapa de memoria de `CLAUDE.md`**

Modify `CLAUDE.md`: tras la sección "## Mapa de la memoria (tiers de `wiki/`)", añadir:

```markdown
## Auditoría (estado de corridas)
- `audit/runs/<run-id>/` — corridas de la operación `AUDIT` (snapshot, maker, auditor,
  propuestas). Estado operacional reproducible, claveado al SHA de git. Regla: [[gen-auto-auditoria]].
```

- [ ] **Step 5: Registrar en `index.md`**

Modify `index.md`: en la sección "## Genoma", añadir tras la línea de "Auditoría de mutaciones":

```markdown
- Auto-auditoría: operación `AUDIT` → corridas en `audit/runs/`. Regla: [[gen-auto-auditoria]].
```

- [ ] **Step 6: Crear el scaffolding de `audit/`**

Create `audit/README.md`:

```markdown
# audit/ — estado de corridas de auto-auditoría

Salida de la operación `AUDIT` (regla: [[gen-auto-auditoria]]). Estado operacional, NO genoma
ni conocimiento. Una carpeta por corrida:

```
audit/runs/<YYYY-MM-DD>-<short-SHA>/
├── 00-snapshot.md   # SHA, arbol limpio/sucio, archivos auditados, version del gen, fecha
├── 10-maker.md      # todos los candidatos: evidencia + diff + score
├── 20-auditor.md    # veredicto por candidato + re-derivacion + score recalculado
└── 30-proposals.md  # <=3 propuestas rankeadas, status: pending|approved|reverted
```

Claveado al SHA de git: misma base ⇒ misma corrida reconstruible. Las decisiones humanas se
anotan en `30-proposals.md`. Las mejoras aprobadas que tocan genoma pasan por
[[gen-compuerta-mutacion]] (`events.jsonl`); las de wiki, por `log.md`.
```

Create `audit/runs/.gitkeep` with empty content.

- [ ] **Step 7: Append a `genome/events.jsonl`**

Modify `genome/events.jsonl`: añadir al final (append-only, 1 línea):

```json
{"ts":"2026-06-25","type":"gene_added","target":"gen-auto-auditoria","signal":"capacidad nueva: loop de auto-auditoria reproducible (spec 2026-06-25)","diff":"∅ → gen-auto-auditoria v1 (operacion AUDIT: detecta via LINT/CONSOLIDATE + detector de redundancia de genoma, maker!=auditor por barrera en disco, ranking por impacto, identidad por git SHA, gate humano)","approved_by":"user","status":"applied"}
```

- [ ] **Step 8: Append a `log.md`**

Modify `log.md`: bajo `## 2026-06-22` añadir un nuevo bloque arriba (lo más reciente arriba):

```markdown
## 2026-06-25
- `EVOLVE` (compuerta) — alta de [[gen-auto-auditoria]] v1: nueva operación `AUDIT` (auto-auditoría reproducible). Fixture en `sim/_auditoria-fixture/`. Ver spec `docs/superpowers/specs/2026-06-25-loop-auto-auditoria-design.md`.
```

- [ ] **Step 9: Re-sync `AGENTS.md`**

Run: `cp CLAUDE.md AGENTS.md`
Expected: `AGENTS.md` queda idéntico a `CLAUDE.md` (el genoma dice que `AGENTS.md` es copia exacta).

Run: `git diff --stat AGENTS.md CLAUDE.md` — confirmar que ambos se modificaron igual.

- [ ] **Step 10: Commit (finaliza la mutación de genoma)**

```bash
git add genome/genes/gen-auto-auditoria.md CLAUDE.md AGENTS.md index.md audit/ genome/events.jsonl log.md
git commit -m "feat(genome): gen-auto-auditoria v1 + operacion AUDIT

Capacidad de auto-auditoria reproducible. Detecta via LINT/CONSOLIDATE +
detector de redundancia de genoma; maker!=auditor por barrera en disco;
ranking por impacto; identidad por git SHA; gate humano. Pasa por la
compuerta (events.jsonl) y re-sincroniza AGENTS.md."
```

---

## Task 7: Ejecutar AUDIT sobre el fixture y verificar contra el oráculo

Esta es la "corrida del test": ejecutar la operación leyendo `gen-auto-auditoria`, con el
fixture como base, escribiendo en `sim/_auditoria-fixture/audit/runs/`.

**Files:**
- Create: `sim/_auditoria-fixture/audit/runs/<run-id>/00-snapshot.md`
- Create: `sim/_auditoria-fixture/audit/runs/<run-id>/10-maker.md`
- Create: `sim/_auditoria-fixture/audit/runs/<run-id>/20-auditor.md`
- Create: `sim/_auditoria-fixture/audit/runs/<run-id>/30-proposals.md`
- Modify: `sim/_auditoria-fixture/regresion.md`

- [ ] **Step 1: Snapshot — fijar identidad del estado**

Run: `git rev-parse --short HEAD` y `git status --porcelain`
Tomar el short-SHA como `<sha>`. `run-id = 2026-06-25-<sha>`.

Create `sim/_auditoria-fixture/audit/runs/2026-06-25-<sha>/00-snapshot.md` con: el SHA, si el
árbol está limpio, la lista de archivos del fixture auditados (genome-applied/ + wiki/), la
versión del gen (`gen-auto-auditoria v1`) y la fecha `2026-06-25`.

- [ ] **Step 2: Maker — correr detectores y producir candidatos**

Sobre el esqueleto del fixture, ejecutar mentalmente los detectores del gen y hacer drill-down.
Create `10-maker.md` con los 8 candidatos D1–D8, cada uno con: clase, páginas/genes afectados,
evidencia (por `[[link]]`; para D8 SIN transcribir el dato sensible), `diff` propuesto y score
calculado por la fórmula.

Expected: los 8 candidatos coinciden en clase/alcance/score con la tabla de `expected.md`.

- [ ] **Step 3: Auditor — pasada fresca que refuta y re-puntúa**

Tratando como únicos insumos `00-snapshot` + el gen + `10-maker.md`, refutar cada candidato y
recalcular score. Create `20-auditor.md` con un veredicto por candidato (confirmado/refutado) +
score recalculado. Para este fixture los 8 son defectos reales → 8 confirmados.

Expected: 8 confirmados; scores idénticos a `expected.md`.

- [ ] **Step 4: Propuestas — ensamblar el top-3**

Create `30-proposals.md` con las 3 de mayor impacto tras desempate: **D1, D2, D3**, cada una
`status: pending` con `id, fecha (2026-06-25), motivo, evidencia, diff, score`.

- [ ] **Step 5: Registrar la corrida en `log.md` del fixture (meta verificable)**

Modify `sim/_auditoria-fixture/wiki/log.md` (créalo si no existe) añadiendo:

```markdown
## 2026-06-25
- `AUDIT` run 2026-06-25-<sha> — 8 candidatos, 8 confirmados, top-3 [D1,D2,D3] pending.
```

- [ ] **Step 6: VERIFICAR contra el oráculo (la aserción del test)**

Comparar `30-proposals.md` y `10-maker.md` con `expected.md`:
- [ ] El conjunto de candidatos = 8 con los mismos `(clase, alcance, impacto)` que la tabla.
- [ ] El top-3 = `[D1, D2, D3]` en ese orden (desempate D1 antes que D2 por clase).
- [ ] La evidencia de D8 en `10-maker.md` y `20-auditor.md` NO transcribe DNI/titular/diagnóstico
      (solo `[[expediente-x]]` / `[[expediente-x-copia]]`).

Expected: las 3 casillas se cumplen. Si alguna falla, corregir el gen o el fixture y repetir.

- [ ] **Step 7: Llenar `regresion.md` y commit**

Create `sim/_auditoria-fixture/regresion.md` documentando: run-id, los 8 candidatos obtenidos vs
esperados, el top-3 obtenido vs esperado, y el resultado de la verificación de confidencialidad.
Veredicto final: **PASS** si las 3 casillas del Step 6 se cumplen.

```bash
git add sim/_auditoria-fixture/
git commit -m "test(audit): corrida del fixture reproduce expected.md (PASS)"
```

---

## Task 8: Verificación de reproducibilidad (segunda corrida)

**Files:**
- Modify: `sim/_auditoria-fixture/regresion.md`

- [ ] **Step 1: Confirmar que el estado no cambió**

Run: `git rev-parse --short HEAD`
Nota: si el SHA cambió respecto a la Task 7 (por el commit de la Task 7), eso es esperado; lo que
importa es que el **contenido del fixture auditado** (genome-applied/ + wiki/) no cambió. Confírmalo:
Run: `git diff HEAD~1 -- sim/_auditoria-fixture/genome-applied sim/_auditoria-fixture/wiki`
Expected: sin cambios en esas rutas (el commit anterior solo añadió artefactos de corrida/regresion).

- [ ] **Step 2: Segunda corrida del maker (mentalmente, mismos detectores)**

Re-derivar el conjunto de candidatos sobre el mismo esqueleto.
Expected: **mismo conjunto de 8 candidatos y mismo top-3** que la primera corrida. La prosa de los
`diff` puede diferir; las tuplas `(clase, alcance, impacto)` y el ranking, NO.

- [ ] **Step 3: Registrar el resultado de reproducibilidad**

Modify `sim/_auditoria-fixture/regresion.md`: añadir sección "Reproducibilidad" confirmando que la
segunda derivación produjo idéntico conjunto y ranking, y notando explícitamente qué varió (solo
prosa de diffs) como la frontera de no-determinismo declarada en el spec §4.

- [ ] **Step 4: Commit**

```bash
git add sim/_auditoria-fixture/regresion.md
git commit -m "test(audit): verificacion de reproducibilidad (mismo conjunto + ranking)"
```

---

## Self-review (cobertura del spec)

- §3 contrato del loop → Task 5 (gen) define disparador/meta/roles/gate.
- §4 detección reproducible en 2 tiempos → Task 5 (gen) + verificado en Task 7/8.
- §5 maker≠auditor por disco + rúbrica → Task 5 (gen) + artefactos 10/20/30 en Task 7.
- §6 estado, git SHA, idempotencia → Task 5 (gen) + Task 7 Step 1.
- §7 gate y aplicación → Task 5 (gen) + checkpoint Task 6 Step 1.
- §8 confidencialidad → fixture D8 (Task 3) + invariante en `expected.md` (Task 4) + verif. Task 7 Step 6.
- §9 principios inviolables → P1 (no toca raw/), P2 (idempotente Task 8), P3 (2 tiempos), P4 (compuerta Task 6), P5 (events.jsonl Task 6), P6 (frontmatter del gen), P7 (propone, no aplica).
- §10 fixture → Tasks 1–4, 7, 8.
- §12 entregables → gen (T5), CLAUDE.md+AGENTS+index (T6), audit/ (T6), fixture (T1–4), events.jsonl (T6).

Sin placeholders. Nombres consistentes (`gen-auto-auditoria`, `run-id`, `00/10/20/30`, D1–D8).
```
