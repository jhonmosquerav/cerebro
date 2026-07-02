# Bitácora operativa

Registro humano-legible del día a día (ingestas, consultas, mantenimiento).
Distinto de `genome/events.jsonl`, que registra solo mutaciones del genoma.
Formato: una línea por operación, lo más reciente arriba.

<!-- Anota aquí tus operaciones conforme uses CEREBRO (ONBOARD, INGEST, QUERY, LINT, CONSOLIDATE, EVOLVE, AUDIT). -->

## 2026-07-02
- EJECUCIÓN Fase A (9 agentes en paralelo, dominios de archivos disjuntos): **A-02** hooks reales v1 (`.claude/hooks/*.sh`, 12 casos probados; activos al reiniciar sesión) · **A-10** `permissions` (deny `raw/**`, ask `genome/**`) · **A-07** staging de la lente a allowlist fail-closed (doble cerrojo, probado con fixtures) · **A-08/A-09** `ops/` (git seguro + backup cifrado con `--verify-restore` probado) · **A-11** README alineado a evidencia + C9 cerrado en dashboards. **7 propuestas EVOLVE `pending`** en `audit/evaluations/2026-07-01-810f24e/70-propuestas-evolve/` (a01 anti-inyección, a03 CHECKPOINT, a04 identidad+ledger, a05 umbrales, a06 índice+QUERY, a08 excepción purga, c14 metadatos) — **genoma intacto**, esperando compuerta. `CLAUDE.md`≡`AGENTS.md` re-sincronizados (nota de hooks: stubs → v1; SHA-256 verificado).
- BACKLOG (decisión del operador sobre el plan 50): reordenado a **técnico → validación → validadores diferidos → mercado**, sin tiempo, prioridad por orden. Fase A = versión mejorada operando (anti-inyección, hooks reales, CHECKPOINT, idempotencia por identidad de página, umbrales de ciclo de vida, jerarquización de índice, allowlist staging, git seguro, backup, README honesto); Fase B = piloto Fase 0; Fase C (validadores/hash-chain/firma) diferida con riesgo aceptado documentado. Ver `audit/evaluations/2026-07-01-810f24e/60-backlog.md`.
- PLAN (derivado de la evaluación `2026-07-01-810f24e`): escenario objetivo **Escritura Pública** elegido por deseabilidad (5/5) y fit con fortalezas verificadas (5/5), con advertencia explícita de que no es el más probable hoy (la señal actual favorece Todo Incluido). Plan F0–F4 (seguridad+honestidad → piloto Fase 0 ≤90 días → garantía mecánica "fe pública" → fabricar operadores → capturar categoría) + coberturas ≤15% + watchlist trimestral con tripwires. Ver `audit/evaluations/2026-07-01-810f24e/50-plan-escritura-publica.md`. Sin mutaciones de genoma (las propuestas del plan pasarán por EVOLVE/compuerta cuando se ejecuten).

## 2026-07-01
- EVALUACIÓN (ejercicio externo, no operación del genoma): `2026-07-01-810f24e` — panel multidisciplinar de 6 lentes de industria (ISO 25010+ATAM, APQC KM, COBIT+ISO 31000, 12-Factor Agents, STRIDE+OWASP LLM, TRL+SWOT) con auditoría cruzada maker≠auditor (119 afirmaciones re-derivadas: 104 confirmadas, 15 matizadas, 0 refutadas) + escenarios método Schwartz/GBN. Valoración global **2.8/5** (diseño/gobernanza 3.5–4.5; validación viva y enforcement 1.5–2), **TRL 4**. Artefactos en `audit/evaluations/2026-07-01-810f24e/` (sin commitear; genoma intacto).

## 2026-06-30
- APPLY (AUDIT C7): `index.md` actualizado (updated 2026-06-30) — anclas de operación `GRAPH`/[[gen-graph-lens]] y de la capa de visualización; el mapa de entrada refleja el genoma vigente.
- APPLY (AUDIT C8): runbook de grafo — "backend local" → "con el backend de `graph_lens.backend`" (coherente con gen-graph-lens v2).
- APPLY (AUDIT P5/C6): `dashboards/graph/00-leeme.md` — filtro de staging endurecido (patrón tolerante espacios/comillas, rutas preservadas en PowerShell, verificación bloqueante antes de graphify).
- APPLY (AUDIT P4/C5): cap-ingesta-de-fuente v1->v2 — el workflow de INGEST ahora compone `gen-confidencialidad` (clasifica sensibilidad + PII-halt; no ancla confidenciales). Ver `genome/events.jsonl`.
- APPLY (AUDIT P3): `default_sensibilidad: confidencial` en `salud.yaml` y `legal.yaml` — las páginas sensibles nacen confidencial (no se anclan/fusionan/exportan).
- APPLY (AUDIT P2): bloque `graph_lens` añadido a los 5 blueprints de onboard — ONBOARD v4 ya tiene dónde persistir `graph_lens.backend`.
- APPLY (AUDIT P1): gen-frontmatter-obligatorio v3->v4 — default de `sensibilidad` = `default_sensibilidad` del manifiesto (antes fijo `interno`, contradecía gen-confidencialidad). Ver `genome/events.jsonl`.
- AUDIT: corrida `2026-06-30-7c840d0` — equipo de 7 especialistas (maker) + auditor independiente (barrera maker≠auditor en disco). 15 candidatos → 13 confirmados, 1 refutado, 1 degradado. Top-3 `status: pending` (gate humano): P1 contradicción default `sensibilidad` entre genes (sev5), P2 blueprints sin bloque `graph_lens` (sev4), P3 blueprints sensibles sin `default_sensibilidad` (sev4). Ver `audit/runs/2026-06-30-7c840d0/`.
- EVOLVE: gen-onboard v3->v4 — al configurar, si la lente está activa sin backend, ONBOARD pregunta una vez y lo registra. Ver `genome/events.jsonl`.
- EVOLVE: gen-graph-lens v1->v2 — backend elegible por el usuario (claude|local|structural), registrado en el manifiesto; invariante = lo confidencial nunca sale. Ver `genome/events.jsonl`.
- EVOLVE: gen-graph-lens v1 (nuevo) + operación `GRAPH` — analítica de grafo como señales a CONSOLIDATE/QUERY/LINT/EVOLVE. Ver `genome/events.jsonl`.
- EVOLVE: gen-visualizacion v1->v2 — render interactivo (lente de grafo graphify, opcional/local). Ver `genome/events.jsonl`.

## YYYY-MM-DD
- _(tu primera operación: corre `ONBOARD` y regístrala aquí)_
