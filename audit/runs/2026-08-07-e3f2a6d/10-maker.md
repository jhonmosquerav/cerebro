---
run_id: 2026-08-07-e3f2a6d
fecha: 2026-08-07
rol: maker
sha: e3f2a6d95ac4894a6bbb6903e9c3d3d47d01669b
candidatos: 4
---

# 10 — Maker · corrida AUDIT 2026-08-07-e3f2a6d

Insumos: `00-snapshot/` (lint 0/0/0 · consolidate sin pendientes · health 100/100 ·
xray deriva 1.000 · árbol limpio en `e3f2a6d`) + [[gen-auto-auditoria]] v5. Lectura en
dos tiempos: esqueleto (frontmatter de los 25 genes, `index.md`, `CLAUDE.md`, `README.md`,
`log.md`, `docs/propuestas-evolve/README.md`, `docs/roadmap-endurecimiento.md`,
`audit/evaluations/2026-07-01-810f24e/60-backlog.md`) y drill-down solo de lo marcado
(gen-migracion-genoma, gen-compuerta-mutacion, gen-evolve, episódico `2026-07-29-30246132`,
prop-f0-04).

**Universo**: con los detectores mecánicos en verde, el universo del maker es lo no
mecanizable que el gen asigna: contradicciones semánticas, redundancia/obsolescencia de
genoma por solape de triggers, vacíos de doctrina y documentación operativa desincronizada
con la evidencia. No hay páginas `sensibilidad: confidencial` en el vault (4 páginas, todas
`interno`); no aplica cita-por-campo.

**Barrido de solape de triggers** (los 25 frontmatter leídos): ningún par de genes `active`
con trigger solapado ni regla subsumida. Los pares que rozan (gen-clase-temporal vs
gen-frontmatter-obligatorio en "crear página"; gen-ciclo-de-vida vs gen-consolidate en
mantenimiento; gen-migracion-genoma vs gen-lint en el pase post-mutación) gobiernan aspectos
distintos y se citan entre sí como complemento. **0 candidatos por esta clase.**

---

## M-01 — H-10 registrado como candidato a EVOLVE, sin propuesta redactada: vacío de doctrina para migrar el genoma entre vaults

**Clase**: vacío (categoría sin cobertura) → severidad **2**.

**Evidencia (verificada, no aceptada por estar escrita)**:
- `log.md` (sección 2026-07-29): *"H-10: el ledger del genoma se bifurca al clonar"* …
  *"no hay camino declarado para llevar una mejora del genoma a un vault ya desplegado"* …
  *"Toca [[gen-compuerta-mutacion]] … y [[gen-migracion-genoma]], que hoy solo contempla
  migrar dentro de un vault"*.
- `wiki/episodic/2026-07-29-30246132.md:65-68`: *"H-10, el bloqueo real … **Va a compuerta
  como EVOLVE**: toca [[gen-compuerta-mutacion]] y [[gen-migracion-genoma]]"*.
- Verificación propia del vacío: `genome/genes/gen-migracion-genoma.md` (v1, completo) solo
  re-valida manifiesto y páginas **dentro** del vault tras una mutación; ninguna sección
  cubre template→clon. `genome/genes/gen-compuerta-mutacion.md` (v2) exige hash-chain
  append-only por mutación — dos vaults que parten del mismo eslabón producen dos cadenas
  válidas irreconciliables por merge, exactamente lo que H-10 describe.
- Verificación de la ausencia: `docs/propuestas-evolve/` termina en `prop-f0-11` (11
  archivos + README; listado en disco). **No existe propuesta para H-10**, pese a que
  [[gen-evolve]] define EVOLVE como "PROPONE … muestra señal + diff": la señal está
  registrada dos veces desde el 2026-07-29 y el diff nunca se redactó. El README del
  producto agrava el vacío: promete clonabilidad y evolución (*"Cualquier empresa lo
  clona…"*, `README.md:11`) sin que el genoma cubra el camino de actualización.

**Diff propuesto**: crear `docs/propuestas-evolve/prop-f0-12-migracion-entre-vaults.md`
(`status: pending`) que proponga [[gen-migracion-genoma]] v1→v2: sección nueva "Migración
entre vaults (producto→implantación)" con el camino elegido entre las tres salidas ya
esbozadas en `C:\cerebro-piloto\piloto\hallazgos.md`, y —si el camino elegido introduce un
tipo de evento de importación (p. ej. `genome_import` con referencia al SHA/hash del
template)— el toque correspondiente a [[gen-compuerta-mutacion]]. Añadir la fila a la tabla
de `docs/propuestas-evolve/README.md`. La mutación misma queda bajo compuerta; este AUDIT
solo cierra el hueco "señal sin propuesta".

**Score**: rúbrica de vacío → alcance = **1** (la categoría sin cobertura: migración
entre vaults). `impacto = 2*10 + 1 = **21**`.
Nota para el auditor: la clase sev-2 es la única de la tabla que aplica (no hay dos genes
que se contradigan entre sí ni invariante violada *en este repo*); si se juzgara por la
consecuencia en implantaciones, el defecto es mayor de lo que el score expresa.

---

## M-02 — CLAUDE.md/AGENTS.md afirman que la integración del núcleo mecánico "espera compuerta" cuando se aprobó y aplicó hace dos gates

**Clase**: conocimiento supersedido sin degradar estado → severidad **3**.

**Evidencia**:
- `CLAUDE.md:106` (y espejo `AGENTS.md:106`, byte-idéntico): *"La integración formal de
  esto a los genes espera compuerta: `docs/propuestas-evolve/`."*
- Supersedido desde 2026-07-27/29: `docs/propuestas-evolve/README.md` — *"Gate resuelto el
  2026-07-27"* y tabla con **10 de 11 propuestas "✅ aplicada"** (solo `prop-f0-04` sigue
  *"⏸ aplazada hasta Fase B"*); `log.md` 2026-07-27 (7 mutaciones) y 2026-07-29 (5
  mutaciones), con sus líneas en `genome/events.jsonl` (70→75).
- El propio `CLAUDE.md` lo contradice tres bullets antes: manda usar `events append`
  (*"jamás la escribas a mano"*), `onboard apply` como aplicado mecánico y `lint` como
  detector canónico — es decir, describe los genes v5–v7 que **ya** consumen el núcleo, y
  luego afirma que esa integración está pendiente.

**Diff propuesto**: en `CLAUDE.md:106` reemplazar la línea por:
*"- La integración de estas herramientas a los genes se aprobó y aplicó por compuerta
(gates 2026-07-27 y 2026-07-29); solo `prop-f0-04` (gen-xray) sigue pendiente, aplazada
hasta la Fase B: `docs/propuestas-evolve/`."* — y re-sincronizar con
`python tools/cerebro.py mirror --fix`. (No toca `genome/`: es el manual; basta el gate de
este AUDIT + línea en `log.md` + commit.)

**Score**: alcance = página supersedida + citas operativas de primer nivel =
`CLAUDE.md` + `AGENTS.md` (espejo obligatorio, ambos archivos portan el defecto) = **2**.
`impacto = 3*10 + 2 = **32**`.

---

## M-03 — El backlog 60-backlog.md marca como pendiente/diferida la Fase C que se ejecutó el 2026-07-12 (y no registra el arranque real de la Fase B)

**Clase**: conocimiento supersedido sin degradar estado → severidad **3**.

**Evidencia**:
- `audit/evaluations/2026-07-01-810f24e/60-backlog.md:104-114`: encabezado *"Fase C —
  Enforcement mecánico (validadores) — **diferida por decisión del operador**"* con
  **C-01, C-02, C-03, C-05 y C-06 en `[ ]`**; y `:87-89` con **B-01 y B-02 en `[ ]`**.
- Supersedido por: `log.md` 2026-07-12 — *"INFRA (Fase C del backlog `2026-07-01-810f24e`
  … ejecutada como Fase 0…): C-01 lint de 16 detectores · C-02 espejo · C-03 … hash-chain …
  append-only · C-05 pre-commit (probado en 5 casos) · C-06 runbook de replay … ensayado
  de verdad"*; `docs/roadmap-endurecimiento.md:24-48` (Fase 0 `[x]`, *"cerrada
  2026-07-27"*, con C-02/C-03/C-05 citados por id). Para B-01/B-02:
  `docs/propuestas-evolve/README.md` — *"corpus de 73 fuentes reales y correr un ONBOARD y
  un primer lote de ingesta de verdad"* (piloto `C:\cerebro-piloto`) y
  `wiki/episodic/2026-07-29-30246132.md:63` (*"B-02 … 69 fuentes"* pendientes de 73).
- El defecto viola la regla del propio documento (`60-backlog.md:20`): *"Al completar una
  tarea: marcar `[x]` aquí + línea en `log.md`"* — la línea de log existe, el `[x]` no.
  Consecuencia operativa: el único ítem de Fase C genuinamente pendiente (**C-04**, firma
  de aprobaciones, diferido con motivo documentado en `roadmap-endurecimiento.md:103-107`)
  queda indistinguible de cinco ítems ya construidos, y la nota de *"Riesgo aceptado al
  diferir la Fase C"* (`:21-24`) sigue vigente en el texto cuando el riesgo ya fue cerrado
  por los validadores.
- Git lo confirma: el último commit que tocó `60-backlog.md` es `057d5f6` (2026-07-02),
  anterior a toda la Fase C.

**Diff propuesto** (solo estado documental; nada de genoma):
1. Marcar `[x]` C-01, C-02, C-03, C-05, C-06 con anotación *"⇒ 2026-07-12: ejecutada como
   Fase 0 del roadmap de endurecimiento (ver `log.md` y `docs/roadmap-endurecimiento.md`)"*.
2. Encabezado de Fase C: *"ejecutada 2026-07-12 como Fase 0 del roadmap, salvo C-04 —
   diferida: espera decisión de diseño del operador (GPG/allowed_signers)"*; anotar la nota
   de riesgo aceptado como históricamente cerrada.
3. B-01: marcar `[x]` con *"⇒ hecho en el clon del piloto (`C:\cerebro-piloto`), manifiesto
   versionado allí; ver `log.md` 2026-07-29"*; B-02: anotar *"en curso en el piloto (primer
   lote 4/73)"* sin marcar.

**Score**: alcance = página supersedida (`60-backlog.md`) + citas operativas de primer
nivel = `docs/roadmap-endurecimiento.md` (frontmatter `relacion_backlog: ejecuta la Fase C
diferida de …/60-backlog.md`) + `docs/specs/2026-07-12-enforcement-mecanico-design.md:16`
(*"El backlog (`60-backlog.md`) difería ese enforcement"*) = **3**. (Las `prop-a*` también
lo citan, pero son propuestas cerradas: registro histórico, no cita operativa.)
`impacto = 3*10 + 3 = **33**`.

---

## M-04 — README del producto desactualizado tras el gate y el arranque del piloto (dos afirmaciones supersedidas, fusionadas por objeto)

**Clase**: conocimiento supersedido sin degradar estado → severidad **3**.
(Un solo candidato: dos causas distintas, mismo objeto `README.md` — regla de fusión del gen.)

**Evidencia**:
- `README.md:72-74`: *"el piloto con datos reales de una empresa es el siguiente paso del
  backlog"* — supersedido: el piloto **arrancó** (B-01 hecho, B-02 en curso) y ya devolvió
  4 mutaciones aprobadas al genoma (F0-08…F0-11, `log.md` 2026-07-29;
  `docs/propuestas-evolve/README.md`, sección "La tanda del piloto").
- `README.md:181-183`: *"La integración formal de estas herramientas a los genes espera
  compuerta en `docs/propuestas-evolve/`"* — misma falsedad que M-02, en el escaparate
  público del producto (10 de 11 aplicadas).
- Menor, mismo objeto: `README.md:102`, comentario del árbol *"propuestas EVOLVE
  pendientes"* — hoy es histórico + 1 pendiente.

**Diff propuesto**: (a) `:72-74` → *"…el piloto con datos reales arrancó en un clon
(corpus de 73 fuentes); sus primeros hallazgos ya volvieron al genoma como mutaciones
aprobadas (F0-08…F0-11)"*; (b) `:181-183` → misma redacción que el diff de M-02 (aplicado
2026-07-27/29; solo `prop-f0-04` pendiente); (c) `:102` → *"propuestas EVOLVE (histórico +
pendientes)"*.

**Score**: alcance = página supersedida (`README.md`) + citas operativas de primer nivel
(ninguna: nada opera citando al README) = **1**. `impacto = 3*10 + 1 = **31**`.

---

## Ranking del maker (desempate del gen: impacto → orden de clase → ruta)

| # | id | clase | sev | alcance | impacto |
|---|----|-------|-----|---------|---------|
| 1 | M-03 | supersedido sin degradar estado | 3 | 3 | 33 |
| 2 | M-02 | supersedido sin degradar estado | 3 | 2 | 32 |
| 3 | M-04 | supersedido sin degradar estado | 3 | 1 | 31 |
| 4 | M-01 | vacío (categoría sin cobertura) | 2 | 1 | 21 |

## Evaluados y descartados (para que el auditor no re-derive en vano)

- **C-04 (firma de aprobaciones)**: NO es defecto por sí mismo. El aplazamiento es
  deliberado y está documentado con motivo y alternativa técnica
  (`docs/roadmap-endurecimiento.md:103-107`); el rastro en episódicos es registro, no
  desincronización. Su único problema es de visibilidad dentro del backlog → cubierto por M-03.
- **`prop-f0-04`**: frontmatter internamente consistente (`status: pending` +
  `gate: aplazada-hasta-fase-b`), coherente con README de propuestas y roadmap. Sin defecto.
- **`docs/propuestas-evolve/README.md` (encabezado "aprobó seis")**: describe con exactitud
  el gate del 2026-07-27 y la tabla + sección del piloto documentan el del 2026-07-29. El
  documento como un todo es veraz. Sin defecto.
- **`index.md` ("scaffolding listo — pendiente correr ONBOARD", memoria "Aún vacío")**:
  estado CORRECTO del template (el ONBOARD real va en un clon, `README.md:196`); las 4
  episódicas existentes no se anclan por regla ([[gen-jerarquizacion-indice]]). Sin defecto.
- **Solape de triggers del genoma**: barrido completo de los 25 frontmatter, 0 hallazgos
  (detalle arriba).
