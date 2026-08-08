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
- [x] **El caso de dominio propio ✅ 2026-07-27**: `worked/piscc-demo` +
      `onboard/blueprints/seguridad-territorial.yaml`. Cuatro genes de sector
      que codifican obligaciones legales colombianas verificadas en fuente
      primaria (Ley 1801/2016 art. 205 nº 4 — el alcalde DEBE elaborar y
      ejecutar el PISCC; Decreto 399/2011 — el CTOP aprueba la destinación del
      FONSET; Ley 1421/2010 art. 8 — informe anual al MinInterior), no
      prácticas opinables. Regenera byte a byte en CI como los otros dos.
      Límite declarado en su `review.md`: sin estudio de vigencia exhaustivo y
      sin lectura de la guía DNP en su fuente (el PDF no se pudo extraer).
- [x] Piloto B-01…B-06 del backlog (corpus real 50–200 docs, 20 preguntas
      doradas, re-AUDIT poblado). **Salto TRL 4→5. Sin esto no hay Fase 4.**
      ⇒ 2026-08-07: **cerrado** — corpus 73/73 (extractor PDF stdlib v5),
      idempotencia 0 duplicados, recall 20/20, AUDIT poblado `2026-08-07-a09385e`,
      salud 100/100. Caso público: `docs/caso-fase-b.md`.

## Fase 2 — XRAY (el foso) ✅ herramienta construida

- [x] `cerebro xray`: declarado-sin-evidencia · evidenciado-sin-declarar ·
      contradicciones · score de deriva. Propone, jamás aplica. graphify es
      evidencia OPCIONAL (`--inferred graph.json`); sin él funciona.
- [x] Corridas persistentes en `audit/xray/<fecha>-<sha8>/`.
- [x] Gen + operación por compuerta (`prop-f0-04`) — **presentada en el gate
      del 2026-07-27 y APLAZADA a propósito**: es la única que crea un gen
      nuevo (25 → 26) y su componente `deriva` de `health` sale `N/A` porque
      XRAY nunca corrió sobre un vault poblado. Aprobar una operación cuyo
      valor no se ha visto contradice la regla de oro de este roadmap. Se
      re-presenta con la Fase B.
      ⇒ 2026-08-07: **aplicada** — la condición se cumplió de verdad: XRAY corrió
      sobre el vault poblado del piloto (deriva medida, hallazgo M-05 incluido)
      ANTES de entrar al genoma. gen-xray v1, genoma 25 → 26.
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

- C-04 (firma/atribución criptográfica de aprobaciones del gate) quedaba
  DIFERIDA: exigía decisión de diseño del operador (¿GPG? ¿allowed_signers?).
  El hash-chain de C-03 ya da tamper-evidence; C-04 añade autoría fuerte.
  ⇒ 2026-08-07: **resuelta y ACTIVA** — diseño elegido `allowed_signers` (SSH,
  verificable con git puro), gen-compuerta-mutacion v4, clave del operador
  registrada, commits de ambos vaults firmados. Runbook:
  `ops/runbook-firma-aprobaciones.md`.
- D-03 (paquete de cumplimiento ISO 27001 / AI Act) se apoya directamente
  en events.jsonl + audit/runs/ + este enforcement: madura tras Fase B.
