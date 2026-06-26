# Bitácora operativa

Registro humano-legible del día a día (ingestas, consultas, mantenimiento).
Distinto de `genome/events.jsonl`, que registra solo mutaciones del genoma.
Formato: una línea por operación, lo más reciente arriba.

## 2026-06-25
- `EVOLVE` (compuerta) — lote **v2** tras afinación verificada en 6 sandboxes: `gen-auto-auditoria` v2 (alcance explícito, +4 clases, dominio-seguridad, exime derivación, incident_ref), `gen-vigencia-temporal` v2 (vigencia por evento), `gen-lint` v3, `gen-consolidate` v2, `gen-onboard` v3 + `gen-confidencialidad` v2 (`default_sensibilidad`). Detalle en `sim/_afinacion-auditoria.md`.
- `EVOLVE` (compuerta) — alta de [[gen-auto-auditoria]] v1: nueva operación `AUDIT` (auto-auditoría reproducible). Fixture en `sim/_auditoria-fixture/`. Ver spec `docs/superpowers/specs/2026-06-25-loop-auto-auditoria-design.md`.

## 2026-06-22
- `SCAFFOLD` — creado el esqueleto de CEREBRO (estructura, genoma base, cápsula de ingesta, hooks, git). Sistema en pie, pendiente `ONBOARD`.
