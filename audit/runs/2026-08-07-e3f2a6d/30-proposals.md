---
run_id: 2026-08-07-e3f2a6d
fecha: 2026-08-07
rol: proposals
sha: e3f2a6d95ac4894a6bbb6903e9c3d3d47d01669b
propuestas: 3
---

# 30 — Propuestas · corrida AUDIT 2026-08-07-e3f2a6d

Ensambladas por el orquestador desde `10-maker.md` (4 candidatos) y `20-auditor.md`
(4 confirmados + 1 omisión marginal A-05). N = min(3, 4 confirmadas) = **3**, rankeadas
por la rúbrica de [[gen-auto-auditoria]] v5. Contexto mecánico: detectores EN VERDE
(lint 0/0/0, health 100/100, xray deriva 1.000) — las tres propuestas son deuda
documental (wiki/docs), ninguna toca `genome/`.

M-01 (H-10, impacto 21) quedó fuera del corte pero **confirmado**: por regla del gen
("AUDIT … deriva a [[gen-evolve]] las propuestas de regla"), su arreglo se tramita como
propuesta EVOLVE (`docs/propuestas-evolve/prop-f0-12`), no como propuesta de esta corrida.
A-05 (impacto 21, marginal) queda registrado en `20-auditor.md` sin propuesta.

---

## P1 (M-03) — Sincronizar `60-backlog.md` con la Fase C ejecutada y el arranque real de la Fase B

- **id**: P1 · **fecha**: 2026-08-07 · **score**: 33 (sev 3 × 10 + alcance 3) · **status**: pending
- **motivo**: el backlog marca `[ ]`/"diferida" la Fase C construida el 2026-07-12 y no
  registra B-01 hecho ni B-02 en curso en el piloto; viola su propia regla ("al completar:
  marcar `[x]`"). El único pendiente genuino de Fase C (C-04) queda indistinguible de lo hecho.
- **evidencia**: `60-backlog.md:87-89,104-114` vs `log.md` 2026-07-12 y 2026-07-29,
  `docs/roadmap-endurecimiento.md` (Fase 0 cerrada), git: último commit al backlog `057d5f6` (2026-07-02).
- **diff**: marcar `[x]` C-01/C-02/C-03/C-05/C-06 con anotación "⇒ 2026-07-12 ejecutada
  como Fase 0 del roadmap"; encabezado de Fase C actualizado (solo C-04 sigue diferida,
  con motivo); nota de riesgo aceptado anotada como cerrada; B-01 `[x]` (piloto) y B-02
  anotada "en curso (4/73)".

## P2 (M-02) — `CLAUDE.md`/`AGENTS.md` afirman que la integración del núcleo mecánico "espera compuerta"

- **id**: P2 · **fecha**: 2026-08-07 · **score**: 32 (sev 3 × 10 + alcance 2) · **status**: pending
- **motivo**: la línea contradice el gate resuelto (2026-07-27/29, 10 de 11 aplicadas) y
  al propio manual, que tres bullets antes describe los genes que ya consumen el núcleo.
- **evidencia**: `CLAUDE.md:106` ≡ `AGENTS.md:106` vs `docs/propuestas-evolve/README.md`
  ("Gate resuelto el 2026-07-27") y `genome/events.jsonl` (70→75).
- **diff**: reemplazar la línea por la redacción del maker (aplicado por compuerta en los
  gates 2026-07-27/29; solo `prop-f0-04` pendiente, aplazada a Fase B) + `mirror --fix`.

## P3 (M-04) — README del producto desactualizado tras el gate y el arranque del piloto

- **id**: P3 · **fecha**: 2026-08-07 · **score**: 31 (sev 3 × 10 + alcance 1) · **status**: pending
- **motivo**: el escaparate público afirma que el piloto "es el siguiente paso" (ya arrancó
  y devolvió 4 mutaciones al genoma) y repite la falsedad de P2.
- **evidencia**: `README.md:72-74,102,181-183` vs `log.md` 2026-07-29 y
  `docs/propuestas-evolve/README.md` (tanda del piloto).
- **diff**: (a) piloto arrancado con hallazgos ya devueltos al genoma (F0-08…F0-11);
  (b) misma redacción que P2; (c) comentario del árbol → "histórico + pendientes".

---

**Gate**: aprobadas por el operador en la instrucción de la sesión 2026-08-07
("ejecútalo end to end para lograr que cerebro evolucione") — aplicadas una por una con
línea en `log.md` + commit cada una. Revertir = `git revert` + `status: reverted`.
