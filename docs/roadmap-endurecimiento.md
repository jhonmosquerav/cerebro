---
titulo: CEREBRO — Roadmap de endurecimiento
tipo: nota-de-arquitectura
estado: en-ejecucion
fecha: 2026-07-12
relacion_backlog: ejecuta la Fase C diferida de audit/evaluations/2026-07-01-810f24e/60-backlog.md
---

# CEREBRO — Roadmap de endurecimiento

## Tesis

CEREBRO no compite con Obsidian (capa de visualización) ni con graphify
(capa de inferencia). Compite en un eje que ninguno disputa: **gobierno del
conocimiento con trazabilidad de grado auditoría**. La evaluación externa
(`2026-07-01-810f24e`, 2.8/5, TRL 4) lo dijo sin anestesia: diseño y
gobernanza 3.5–4.5, *enforcement por convención* 1.5–2. Este roadmap cierra
esa brecha en un orden que no se negocia: **verdad → evidencia → alcance →
distribución**.

**Regla de oro**: ninguna fase avanza sin su criterio de salida. Un sistema
que no se somete a sus propias compuertas no puede pedir confianza.

## Fase 0 — Verdad (bloqueante) ✅ construida 2026-07-12 · **cerrada 2026-07-27**

El LLM nunca decide lo que un script puede decidir; el script nunca redacta
juicio.

- [x] Núcleo mecánico en `tools/` (Python stdlib, 0 dependencias): lint (16
      detectores), espejo AGENTS≡CLAUDE (C-02), integridad + hash-chain +
      append-only del ledger (C-03), hash de estado, onboard aplicado.
- [x] LA prueba: mismo manifiesto + misma fecha ⇒ mismo hash; re-aplicar ⇒
      no-op (`tests/test_onboard.py`).
- [x] CI ubuntu + windows con la suite completa + `verify` (badge en README).
- [x] Pre-commit que bloquea mutación de raw/, reescritura del ledger y
      espejo roto (C-05).
- [x] README sin afirmaciones que el CI no pruebe (tabla probado vs juicio).
- [x] **Compuerta resuelta 2026-07-27**: el operador revisó las 7 propuestas
      EVOLVE una por una y aprobó 6 → **7 mutaciones aplicadas** (gen-lint
      recibió dos: v4→v5→v6; más gen-onboard v5, gen-compuerta-mutacion v2,
      gen-auto-auditoria v5, gen-graph-lens v4, gen-jerarquizacion-indice v3),
      cada una con evento encadenado y commit. **Los genes ya consumen el
      núcleo mecánico.** Única excluida: `prop-f0-04` (gen-xray), aplazada
      hasta Fase B — ver Fase 2.
- [x] Agujero cerrado el 2026-07-27: el pre-commit corría `verify --quick` y
      se saltaba el lint entero (se podía commitear un enlace roto). Ahora
      corre `verify --exclude temporales`: lint estructural completo, sin que
      un vencimiento por calendario bloquee commits ajenos.

## Fase 1 — Evidencia 🟡 iniciada

- [x] `worked/` con contrato + 2 casos sintéticos re-corribles byte a byte
      en CI (agencia, legal), cada uno con `review.md` honesto que documenta
      fallos reales del desarrollo.
- [ ] El caso de dominio propio (PISCC u observatorio, con fuentes
      normativas reales) — el activo que nadie más puede producir.
- [ ] Piloto B-01…B-06 del backlog (corpus real 50–200 docs, 20 preguntas
      doradas, re-AUDIT poblado). **Salto TRL 4→5. Sin esto no hay Fase 4.**

## Fase 2 — XRAY (el foso) ✅ herramienta construida

- [x] `cerebro xray`: declarado-sin-evidencia · evidenciado-sin-declarar ·
      contradicciones · score de deriva. Propone, jamás aplica. graphify es
      evidencia OPCIONAL (`--inferred graph.json`); sin él funciona.
- [x] Corridas persistentes en `audit/xray/<fecha>-<sha8>/`.
- [ ] Gen + operación por compuerta (`prop-f0-04`) — **presentada en el gate
      del 2026-07-27 y APLAZADA a propósito**: es la única que crea un gen
      nuevo (25 → 26) y su componente `deriva` de `health` sale `N/A` porque
      XRAY nunca corrió sobre un vault poblado. Aprobar una operación cuyo
      valor no se ha visto contradice la regla de oro de este roadmap. Se
      re-presenta con la Fase B.
- [ ] Primera deriva real confirmada por humano sobre un vault poblado
      (requiere Fase B).

## Fase 3 — Salud ✅ construida

- [x] `cerebro health`: 6 componentes deterministas, N/A honestos que
      renormalizan, score único 0–100, test negativo (degradar baja el
      número), tablero estático `--write` + Dataview existente.

## Fase 4 — Distribución 🔒 bloqueada a propósito

No se empaqueta ni promociona un sistema cuyo piloto real no corrió:
distribuir antes de verificar amplifica el problema. Se desbloquea al
cerrar Fase 1 completa. (Cuando toque: skill instalable, catálogo de
blueprints, el artículo del caso público colombiano.)

## Lo que NO se va a hacer

- Editor/app propia (Obsidian ya ganó esa guerra).
- Competir en cobertura de extracción con graphify (equipo financiado,
  36 gramáticas: terreno perdido e irrelevante para la tesis).
- Perseguir estrellas: la métrica es que **un auditor pueda fiarse**.
- Features nuevos sobre base no verificada.

## Mapa a C-04 y siguientes

- C-04 (firma/atribución criptográfica de aprobaciones del gate) queda
  DIFERIDA: exige decisión de diseño del operador (¿GPG? ¿allowed_signers?).
  El hash-chain de C-03 ya da tamper-evidence; C-04 añadiría autoría fuerte.
- D-03 (paquete de cumplimiento ISO 27001 / AI Act) se apoya directamente
  en events.jsonl + audit/runs/ + este enforcement: madura tras Fase B.
