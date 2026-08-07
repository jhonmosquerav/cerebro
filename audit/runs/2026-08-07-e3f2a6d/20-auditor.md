---
run_id: 2026-08-07-e3f2a6d
fecha: 2026-08-07
rol: auditor
sha: e3f2a6d95ac4894a6bbb6903e9c3d3d47d01669b
insumos: [00-snapshot/, genome/genes/gen-auto-auditoria.md (v5), 10-maker.md]
veredictos:
  M-01: confirmado
  M-02: confirmado
  M-03: confirmado
  M-04: confirmado
omitidos_detectados: 1
---

# 20 — Auditor · corrida AUDIT 2026-08-07-e3f2a6d

Pasada fresca, sin memoria de sesión. Insumos: `00-snapshot/` (SHA verificado contra
`git rev-parse HEAD` = `e3f2a6d…`; lint `0/0/0` sobre 4 páginas; consolidate sin
pendientes; health 100; xray sin contradicciones), [[gen-auto-auditoria]] v5 leído
entero, `10-maker.md`. Todos los archivos citados por el maker fueron abiertos y las
citas re-derivadas; nada se aceptó por estar escrito.

Nota de estado: el árbol está limpio de modificaciones, pero hay dos rutas untracked
(`audit/runs/2026-08-07-e3f2a6d/` — inherente a la corrida — y `audit/xray/`). No
invalida la identidad del run; se deja constancia porque el gen pide registrar
`HEAD + dirty` cuando aplique.

---

## M-01 — H-10 sin propuesta EVOLVE (migración de genoma entre vaults) → **CONFIRMADO**

**Veredicto: confirmado. Clase: vacío (categoría sin cobertura), severidad 2 — la
clasificación del maker resiste el intento de escalarla.**

**Evidencia re-derivada (toda existe):**
- `log.md`, sección 2026-07-29, línea 10: la entrada H-10 completa, con las frases
  citadas por el maker textualmente presentes ("el ledger del genoma se bifurca al
  clonar"; "no hay camino declarado para llevar una mejora del genoma a un vault ya
  desplegado"; "Toca [[gen-compuerta-mutacion]] … y [[gen-migracion-genoma]], que hoy
  solo contempla migrar *dentro* de un vault"). Verificado.
- `wiki/episodic/2026-07-29-30246132.md:65-68`: "H-10, el bloqueo real … Va a compuerta
  como EVOLVE: toca [[gen-compuerta-mutacion]] y [[gen-migracion-genoma]]". Verificado.
- `genome/genes/gen-migracion-genoma.md` (v1, leído completo): su trigger es "tras
  aplicar una mutación de genoma" y su cuerpo solo re-valida manifiesto y páginas del
  MISMO vault. Ninguna sección cubre template→clon. Verificado.
- `genome/genes/gen-compuerta-mutacion.md` (v2, leído completo): hash-chain
  (`prev`=sha256 de la línea anterior) + append-only bloqueado por pre-commit. Dos
  vaults que parten del mismo eslabón producen cadenas válidas e irreconciliables:
  coherente con lo que H-10 describe. Verificado.
- Ausencia de propuesta: listado en disco de `docs/propuestas-evolve/` = 11 propuestas
  (`prop-f0-01` … `prop-f0-11`) + `README.md`. **No existe propuesta para H-10.**
  Verificado. `gen-evolve` (v1) define EVOLVE como "PROPONE … muestra señal + diff";
  la señal está registrada dos veces desde 2026-07-29, el diff no existe.

**Análisis de clase (el punto que este auditor debía forzar):**
- ¿"Contradicción entre genes activos" (sev-5)? **No.** [[gen-compuerta-mutacion]] y
  [[gen-migracion-genoma]] no prescriben conductas incompatibles: uno gobierna el
  ledger, el otro la re-validación post-mutación intra-vault. Ninguno afirma nada que
  el otro niegue. La tensión de H-10 se materializa entre dos **repos** (template y
  clon), no entre dos genes; el silencio compartido sobre el caso inter-vault es
  exactamente un hueco de cobertura, no una contradicción.
- ¿"Violación de invariante impuesta por un gen" (sev-4)? **No en este repo y este
  SHA.** El snapshot lo prueba mecánicamente: lint `0/0/0`, componente `genoma` de
  health = 100 ("espejo + ledger + genes en verde"). Ningún invariante de este vault
  está violado; la bifurcación vive en la relación con `C:\cerebro-piloto` (fuera del
  alcance de esta corrida) y aun allí **cada cadena es internamente válida** — lo que
  falta es un camino declarado, es decir, cobertura.
- Clase de mayor severidad aplicable = **vacío (categoría sin cobertura), sev-2**. La
  nota del maker ("si se juzgara por la consecuencia en implantaciones, el defecto es
  mayor de lo que el score expresa") es honesta y correcta: la rúbrica puntúa el
  defecto en ESTE estado, no el daño potencial en despliegues. Escalarlo sin clase que
  lo sostenga sería romper la rúbrica versionada.

**Score recalculado:** clase vacío → alcance = **1** (regla fija de la rúbrica: la
categoría sin cobertura). `impacto = 2*10 + 1 = **21**`. Coincide con el maker.

---

## M-02 — CLAUDE.md/AGENTS.md: "la integración … espera compuerta" ya aplicada → **CONFIRMADO**

**Veredicto: confirmado. Clase: conocimiento supersedido sin degradar estado, sev 3.**

**Evidencia re-derivada:**
- `CLAUDE.md:106`: "- La integración formal de esto a los genes espera compuerta:
  `docs/propuestas-evolve/`." Verificado carácter a carácter. `AGENTS.md:106`: misma
  línea, misma posición. Verificado.
- Supersesión: `docs/propuestas-evolve/README.md` — "**Gate resuelto el 2026-07-27**"
  (encabezado) y tabla con 10 de 11 filas "✅ aplicada" (7 el 2026-07-27, 4 el
  2026-07-29 contando F0-10 como una); única excepción `prop-f0-04` "⏸ aplazada hasta
  Fase B". Verificado. `log.md` 2026-07-27 (APPLY, 7 mutaciones, events 63→70) y
  2026-07-29 (APPLY, 5 mutaciones, events 70→75). Verificado.
- Auto-contradicción interna: `CLAUDE.md:100-101` manda `events append` ("jamás la
  escribas a mano" — eso ES gen-compuerta-mutacion v2, aplicada), `:98` `onboard apply`
  (gen-onboard v5, aplicada). El manual describe los genes ya mutados y cuatro líneas
  después afirma que la integración está pendiente. Verificado.

**Score recalculado:** página supersedida + citas operativas de primer nivel. Cuento
**2**: `CLAUDE.md` y `AGENTS.md` portan cada uno la afirmación supersedida y son
manuales operativos leídos por harnesses distintos (el espejo distribuye el defecto,
no lo deduplica). `impacto = 3*10 + 2 = **32**`. Coincide con el maker.
(Robustez: incluso bajo la lectura estricta de que el espejo es el mismo objeto —
alcance 1, impacto 31 — el ranking final no cambia: M-02 ganaría a M-04 por ruta
alfabética dentro de la misma clase.)

---

## M-03 — `60-backlog.md` marca pendiente/diferida la Fase C ejecutada el 2026-07-12 → **CONFIRMADO**

**Veredicto: confirmado. Clase: conocimiento supersedido sin degradar estado, sev 3.**

**Evidencia re-derivada:**
- `60-backlog.md:104`: "## Fase C — Enforcement mecánico (validadores) — **diferida por
  decisión del operador**"; `:109-114`: C-01, C-02, C-03, C-05 y C-06 todos en `[ ]`
  (C-04 también, pero ese SÍ está genuinamente pendiente); `:87-89`: B-01 y B-02 en
  `[ ]`. Verificado.
- Supersesión: `log.md` 2026-07-12 ("Fase C del backlog … ejecutada como Fase 0 …
  C-01 lint de 16 detectores · C-02 espejo · C-03 … hash-chain … append-only … C-05
  pre-commit (probado en 5 casos) · C-06 runbook de replay … ensayado de verdad").
  `docs/roadmap-endurecimiento.md:24` ("Fase 0 … ✅ construida 2026-07-12 · cerrada
  2026-07-27") con C-02/C-03/C-05 citados por id en `:29-36`. B-01/B-02:
  `docs/propuestas-evolve/README.md` (corpus de 73 fuentes, ONBOARD y primer lote
  reales en el piloto) y `wiki/episodic/2026-07-29-30246132.md:63` (B-02 en curso, 69
  restantes). Verificado.
- Regla del propio documento violada: `60-backlog.md:20` "Al completar una tarea:
  marcar `[x]` aquí + línea en `log.md`" — las líneas de log existen, los `[x]` no.
  Nota de riesgo aceptado (`:21-24`) sigue en el texto ya cerrada por los validadores.
  Verificado.
- Git: último commit que tocó `60-backlog.md` = `057d5f6` (2026-07-02), anterior a
  toda la Fase C. Re-derivado con `git log -1 -- <ruta>`. Verificado.

**Score recalculado:** página supersedida (`60-backlog.md`) + citas operativas
tipadas de primer nivel: `docs/roadmap-endurecimiento.md` (frontmatter
`relacion_backlog: ejecuta la Fase C diferida de …/60-backlog.md` — verificado en
`:6`) y `docs/specs/2026-07-12-enforcement-mecanico-design.md` (frontmatter
`alcance: Fase C del backlog (validadores diferidos)…` verificado en `:5`, más la
prosa de `:16`). Alcance = **3**. `impacto = 3*10 + 3 = **33**`. Coincide con el
maker. (Robustez: si solo se admitiera la relación tipada del roadmap — alcance 2,
impacto 32 — M-03 empataría con M-02 y seguiría primero por ruta alfabética
`audit/…` < `CLAUDE.md`. El ranking es invariante a la discrepancia.)

---

## M-04 — README del producto con dos afirmaciones supersedidas → **CONFIRMADO**

**Veredicto: confirmado. Clase: conocimiento supersedido sin degradar estado, sev 3.
La fusión en un solo candidato (mismo objeto `README.md`) es la aplicación correcta
de la regla del gen ("mismo defecto" = misma página, no misma causa raíz).**

**Evidencia re-derivada:**
- `README.md:72-74`: "el piloto con datos reales de una empresa es el siguiente paso
  del backlog" — supersedido: el piloto arrancó (B-01 hecho, B-02 4/73) y devolvió
  F0-08…F0-11 aplicadas (`log.md` 2026-07-29; `docs/propuestas-evolve/README.md`
  sección "La tanda del piloto"). Verificado.
- `README.md:181-183`: "La integración formal de estas herramientas a los genes espera
  compuerta en `docs/propuestas-evolve/`" — misma falsedad que M-02 en el escaparate
  público. Verificado. (Objeto distinto → candidato separado: correcto según el gen.)
- `README.md:102`: comentario del árbol "propuestas EVOLVE pendientes" — hoy 10/11
  aplicadas, 1 pendiente. Verificado.

**Score recalculado:** página supersedida = `README.md`; citas operativas tipadas de
primer nivel = ninguna encontrada (nada opera citando al README; se re-verificó que
CLAUDE.md no lo referencia operativamente). Alcance = **1**.
`impacto = 3*10 + 1 = **31**`. Coincide con el maker.

---

## Candidato omitido por el maker

### A-05 — Pendiente arquitectónico "index.md como único punto de articulación" declarado abierto y sin ningún artefacto de seguimiento

El maker revisó los pendientes del episódico 2026-07-29 (B-02, H-10, prop-f0-04,
C-04) pero **no evaluó ni descartó el quinto**:
`wiki/episodic/2026-07-29-30246132.md:71` — "**`index.md` como único punto de
articulación**: decisión abierta." La señal viene de `log.md` 2026-07-26 ("`index.md`
es el único punto de articulación del grafo completo (31 nodos / 111 aristas) —
confirma el principio 3 y mide su fragilidad") y del episódico
`2026-07-26-30246132.md:141` ("…decidir si … es diseño aceptado o riesgo a mitigar").
Grep del repo completo: la decisión no existe en backlog, roadmap, propuestas ni
ningún gen — solo en dos episódicos (`decay_rate: high`) y la bitácora.

**Juicio del auditor:** clase aplicable = vacío (categoría sin cobertura), sev **2**,
alcance **1**, `impacto = 2*10 + 1 = **21**`. Lo registro como **omisión confirmada
del maker** pero como **candidato marginal**: a diferencia de H-10, aquí no hubo
compromiso incumplido ("va a compuerta como EVOLVE") y existe doctrina parcial que
lo ampara ([[gen-jerarquizacion-indice]] particiona en hubs al crecer; el principio 3
hace del índice el punto de entrada por diseño). El defecto estricto es que una
decisión arquitectónica abierta vive únicamente en memoria de alto decay. No altera
el top-3 (los tres sev-3 lo superan); si el orquestador lo admite, empata con M-01
en 21 y queda detrás por ruta alfabética (`genome/…` < `wiki/…`).

## Imprecisiones menores del maker (no cambian veredictos)

1. "4 páginas, todas `interno`": inexacto — 3 declaran `sensibilidad: interno`;
   `wiki/episodic/2026-07-02-f1fc904c.md` **no tiene el campo**. Sin consecuencia
   aquí (lint la da por válida y el staging de la lente es fail-closed para páginas
   sin campo), pero la afirmación no re-deriva tal cual.
2. "árbol limpio": limpio de modificaciones, con `audit/xray/` untracked además de la
   carpeta de esta corrida.

## Ranking verificado (desempate del gen: impacto → orden de clase → ruta)

| # | id | veredicto | clase | sev | alcance | impacto |
|---|----|-----------|-------|-----|---------|---------|
| 1 | M-03 | confirmado | supersedido sin degradar estado | 3 | 3 | 33 |
| 2 | M-02 | confirmado | supersedido sin degradar estado | 3 | 2 | 32 |
| 3 | M-04 | confirmado | supersedido sin degradar estado | 3 | 1 | 31 |
| 4 | M-01 | confirmado | vacío (categoría sin cobertura) | 2 | 1 | 21 |
| 5 | A-05 | omitido — añadido con reserva | vacío (categoría sin cobertura) | 2 | 1 | 21 |

Top-N para `30-proposals` = min(3, confirmadas) = **M-03, M-02, M-04**. Nada aplicado:
todo queda `status: pending` para el gate humano.
