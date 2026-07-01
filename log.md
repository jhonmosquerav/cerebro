# Bitácora operativa

Registro humano-legible del día a día (ingestas, consultas, mantenimiento).
Distinto de `genome/events.jsonl`, que registra solo mutaciones del genoma.
Formato: una línea por operación, lo más reciente arriba.

<!-- Anota aquí tus operaciones conforme uses CEREBRO (ONBOARD, INGEST, QUERY, LINT, CONSOLIDATE, EVOLVE, AUDIT). -->

## 2026-06-30
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
