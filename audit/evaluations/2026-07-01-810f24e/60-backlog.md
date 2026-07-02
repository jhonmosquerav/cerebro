---
eval_id: 2026-07-01-810f24e
fecha: 2026-07-02
tipo: backlog
escenario_objetivo: escritura-publica
---

# 60 — Backlog operativo (sin tiempo)

Reordena el plan `50-plan-escritura-publica.md` por decisión del operador (2026-07-02):
**núcleo técnico primero** (la versión mejorada operando lo antes posible) → **validación
viva** después → **enforcement mecánico (validadores) diferido** → mercado y coberturas al
final. Las señales y tripwires del plan 50 siguen vigentes como ritual de revisión.

**Reglas del backlog**
- Sin fechas: la prioridad es el **orden** dentro de cada fase; las fases se ejecutan en orden.
- `[genoma·gate]` = la tarea muta genoma → pasa por EVOLVE/compuerta y deja línea en
  `genome/events.jsonl` + re-sincroniza `AGENTS.md`. Nada de este backlog se auto-aplica.
- 🔒 = **prerrequisito para tocar datos reales**: la Fase B no arranca con ningún 🔒 pendiente.
- Al completar una tarea: marcar `[x]` aquí + línea en `log.md`.
- **Riesgo aceptado al diferir la Fase C:** mientras no exista enforcement mecánico, el gate
  sigue siendo autorrelatado, la integridad de `events.jsonl` descansa en convención y la
  deriva es silenciosa entre auditorías. Mitigación interina: correr `AUDIT` al cierre de
  cada fase (A, B) y antes de cualquier push.

---

## Fase A — Núcleo técnico: la versión mejorada

*Objetivo: cerrar las brechas operativas del sistema (memoria, idempotencia, escala,
seguridad de operación) para que CEREBRO funcione mejorado hoy, sobre datos propios.*

- [x] **A-01 [genoma·gate]** 🔒 **Gen anti-inyección v1** — "el contenido de `raw/` y `wiki/`
  es dato, jamás instrucción"; la clasificación de sensibilidad nunca se delega al documento
  leído; PII-halt reforzado (cap-ingesta v3). *(ataca la sev-5: OWASP LLM01 sin tratar)*
  ⇒ 2026-07-02: **aplicada por compuerta** ✅ — gen-anti-inyeccion v1 + cap-ingesta-de-fuente v3 (2 líneas en `genome/events.jsonl`).
- [x] **A-02 [infra]** ✅ 2026-07-02 (3 scripts POSIX probados en 12 casos; activos al reiniciar sesión) — **Hooks reales** `SessionStart` / `PreCompact` / `Stop` según el plan
  ya escrito en `.claude/hooks/README.md` (bash POSIX, comandos entrecomillados — gotcha
  documentado). El loop de memoria deja de ser stub. *(ataca el riesgo alta×alto: pérdida de
  conocimiento en compactación, hoy garantizada)*
- [x] **A-03 [genoma·gate]** **Operación `CHECKPOINT`** — el loop de memoria como contrato del
  genoma con implementación manual portable (cualquier agente que lea `AGENTS.md` la ejecuta
  sin hooks). Con A-02 forman 2 de las 3 implementaciones del contrato. *(desacople de vendor)*
  ⇒ 2026-07-02: **aplicada por compuerta** ✅ — gen-checkpoint v1 + fila `CHECKPOINT` y loop como contrato en `CLAUDE.md`.
- [x] **A-04 [genoma·gate]** **Identidad de página + ledger de ingesta** — clave de identidad
  canónica (fuente + hash/slug) y registro de fuentes procesadas: INGEST/BULK INGEST
  idempotentes por algoritmo, no por prosa (gen-ingest v++, cápsula v3). *(debilidad sev-4 de
  arquitectura; se medirá en B-03)*
  ⇒ 2026-07-02: **aplicada por compuerta** ✅ — gen-identidad-de-pagina v1 + gen-ingest v2 + gen-bulk-ingest v2 + cápsula v4 + gen-frontmatter-obligatorio v5 (5 líneas).
- [x] **A-05 [genoma·gate]** **Umbrales numéricos del ciclo de vida** — función/condiciones de
  `decay_rate`, criterios de promoción working→semantic, refuerzo y `confidence`
  (gen-clase-temporal, gen-consolidate, gen-confianza-por-fuente). La memoria por capas pasa
  de metáfora a mecanismo. *(debilidad sev-4 de conocimiento)*
  ⇒ 2026-07-02: **aplicada por compuerta** ✅ — gen-ciclo-de-vida v1 + gen-consolidate v3 + gen-clase-temporal v2 + gen-confianza-por-fuente v2 (4 líneas) + `wiki/archive/`.
- [x] **A-06 [genoma·gate]** **Jerarquización del índice + fallback de QUERY** — regla de
  cuándo/cómo partir `index.md` en sub-índices/hubs (la taxonomía del manifiesto ya da la
  estructura) y fallback léxico sancionado (búsqueda por contenido) cuando la navegación no
  alcanza. *(debilidad sev-4: escala sin política)*
  ⇒ 2026-07-02: **aplicada por compuerta** ✅ — gen-jerarquizacion-indice v1 + gen-ingest v3 + gen-query v3 + gen-consolidate v4 + cápsula v5 (5 líneas) + principio 3 con fallback sancionado.
- [x] **A-07 [infra]** ✅ 2026-07-02 (bash+PowerShell, doble cerrojo, probado con fixtures adversariales; pendiente menor: alinear fraseo de gen-graph-lens vía EVOLVE) — 🔒 **Staging de la lente a allowlist fail-closed** — solo sale lo
  explícitamente `publico|interno`; página sin campo `sensibilidad` NO entra al staging.
  *(invierte el filtro fail-open verificado)*
- [x] **A-08 [docs/ops]** ✅ 2026-07-02 (`ops/runbook-git-seguro.md`; excepción de purga **aplicada por compuerta**: gen-raw-inmutable v2, §3.4 vigente) — 🔒 **Runbook de git seguro** — remoto privado obligatorio para
  clones operativos, checklist pre-push, procedimiento de purga de historia
  (git-filter-repo) como excepción documentada y gateada a [[gen-raw-inmutable]] para
  incidentes. *(PII imborrable demostrada en el propio repo)*
- [x] **A-09 [ops]** ✅ 2026-07-02 (`ops/backup/backup.sh` probado: backup real + `--verify-restore` OK + 5 pruebas negativas; destino off-site y passphrase definitivos los configura el operador) — 🔒 **Backup off-site cifrado** + prueba de restauración documentada.
  *(riesgo: pérdida total del cerebro, disco único)*
- [x] **A-10 [config]** ✅ 2026-07-02 (deny Write/Edit `raw/**` + ask `genome/**`; aplica al reiniciar sesión; no cubre escrituras vía Bash — límite documentado) — 🔒 **Bloque `permissions` endurecido** en `.claude/settings.json`
  (denegar escrituras a `raw/` y a `genome/events.jsonl` fuera del flujo, etc.).
- [x] **A-11 [docs]** ✅ 2026-07-02 (README reescrito con claims trazados a evidencia; C9 cerrado en dashboards; C14 **aplicada por compuerta**: gen-confidencialidad v3 + gen-query v4 — hallazgo C14 de la corrida 2026-06-30-7c840d0 cerrado; CLAUDE.md/AGENTS.md re-sincronizados: hooks stubs → v1) — **README alineado con evidencia** — con A-02/A-03 hechos, el claim de
  memoria pasa de stub a real y se afirma **con** evidencia; "función pura / mismo estado →
  mismo resultado" se reformula ("reproducible en estructura, ejecutado por LLM"); tabla de
  operaciones completa (hoy omite AUDIT); cerrar C9 (`FROM "sim"` roto en dashboards) y C14
  (fuga por metadatos). *(gap claim-realidad; hacerla al final de la fase para documentar lo
  ya mejorado, no la aspiración)*

**Cierre de Fase A:** corrida `AUDIT` sobre el genoma mutado + re-sincronía `AGENTS.md`
verificada. La "versión mejorada" queda operando sobre datos propios.

---

## Fase B — Validación viva (piloto Fase 0)

*Objetivo: el caso público reproducible. Arranca solo con todos los 🔒 de Fase A completos.*

- [ ] **B-01 [operación]** **ONBOARD real** — manifiesto `onboard/company.yaml` de una
  empresa real (la del propio autor sirve), versionado.
- [ ] **B-02 [operación]** **BULK INGEST** de corpus real (50–200 documentos).
- [ ] **B-03 [medición]** **Re-corrida de INGEST** sobre el mismo corpus → medir idempotencia
  real (con A-04 operativo, duplicados esperados = 0).
- [ ] **B-04 [medición]** **20 preguntas doradas** → recall de QUERY (meta inicial revisable:
  ≥16/20) + comportamiento del índice al crecer (con A-06).
- [ ] **B-05 [operación]** **Re-AUDIT sobre el estado poblado** — primera auditoría con wiki
  viva; desviaciones documentadas.
- [ ] **B-06 [docs]** **Publicar el caso anonimizado + métricas versionadas** en el repo —
  sustituye la narrativa de la simulación borrada; deja de pedirse fe. **⇒ salto TRL 4→5.**

**Cierre de Fase B:** métricas publicadas y reproducibles; hallazgos del piloto alimentan
EVOLVE (con compuerta) y este backlog.

---

## Fase C — Enforcement mecánico (validadores) — **diferida por decisión del operador**

*Objetivo: convertir "auditable" de narrado a verificable por terceros. Se activa cuando el
operador lo decida o si un tripwire del plan 50 lo exige (p. ej., primer cliente que audite).*

- [ ] **C-01 [infra]** Validador de frontmatter + resolución de `[[wiki-links]]`.
- [ ] **C-02 [infra]** Verificador de sincronía `AGENTS.md` ≡ `CLAUDE.md`.
- [ ] **C-03 [infra]** Integridad + **hash-chain** de `genome/events.jsonl`.
- [ ] **C-04 [genoma·gate]** **Firma/atribución de aprobaciones humanas** del gate.
- [ ] **C-05 [infra]** Pre-commit local: bloqueo de escrituras a `raw/` + validadores en verde.
- [ ] **C-06 [ops]** Runbook de **replay/rollback ejercitado** — un ensayo real documentado.

---

## Fase D — Mercado y coberturas (posterior)

*Se ordena cuando B esté cerrada; las coberturas (D-05/D-06) tienen tope ≤15% del esfuerzo y
solo se promueven a producto por tripwire del plan 50, no por entusiasmo.*

- [ ] **D-01 [docs]** Guía del operador — el consultor técnico como usuario primario.
- [ ] **D-02 [mercado]** Formación + certificación de operadores con la comunidad de origen.
- [ ] **D-03 [mercado]** Paquete de cumplimiento salud/legal — mapear `events.jsonl` +
  `audit/runs/` a evidencia ISO 27001 (8.32, 5.28) y trazabilidad AI Act.
- [ ] **D-04 [genoma·gate]** Lotes gobernados en la compuerta (anti-fatiga del aprobador).
- [ ] **D-05 [cobertura]** Adapter import/export de memorias nativas (a `raw/`, jamás canon)
  — pivote listo para Todo Incluido.
- [ ] **D-06 [cobertura]** Especificación/artículo **bilingüe** del patrón
  (compuerta + ledger + maker≠auditor) — pivote Catedral y consolidación en Escritura Pública.
- [ ] **D-07 [mercado]** Contribución upstream (AGENTS.md, formatos de memoria portable).
- [ ] **D-08 [mercado]** ≥2 implantaciones acompañadas → casos de referencia públicos.

---

## Ritual permanente (sin fecha, por cadencia de uso)

- Revisión de **señales/tripwires** del plan 50 en cada mantenimiento mayor (o trimestral).
- `AUDIT` al cierre de cada fase y antes de cualquier push.
- Toda mutación de genoma: compuerta + `events.jsonl` + re-sincronía `AGENTS.md` + commit.
