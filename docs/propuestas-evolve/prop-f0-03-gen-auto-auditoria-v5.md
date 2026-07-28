---
tipo: propuesta-evolve
tarea: F0-03
status: approved
fecha: 2026-07-12
genes_afectados: [gen-auto-auditoria]
---

# Propuesta EVOLVE F0-03 — `gen-auto-auditoria` v4 → v5: detectores mecánicos alimentan al maker

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

El gen v4 ya dice "reusa LINT + CONSOLIDATE; no la reimplementa" y "la
identidad de cada candidato la fija el detector". Ahora esos detectores son
programas. El maker debe partir de sus salidas — así el no-determinismo de
AUDIT queda acotado exactamente donde el gen ya lo quería: en el juicio de
"¿importa?" y en la prosa del diff, jamás en la detección.

## Diff propuesto (v4 → v5)

En la sección **Detección**, sustituir la primera línea por:

```
- El orquestador ejecuta ANTES del maker: `python tools/cerebro.py lint
  --as-of <hoy> --json`, `consolidate scan --json`, `health --json` y (si
  hay corrida) el último `audit/xray/*/reporte.json`, y guarda las salidas
  en `00-snapshot` junto al SHA. El maker toma ESOS candidatos como
  universo de partida para huérfanos, vencidos, verbos/campos fuera de
  esquema, duplicados y deriva; el LLM añade solo lo no mecanizable
  (contradicciones semánticas, redundancia de genoma por solape de
  triggers) y juzga/redacta.
```

En **Estado, identidad y reproducibilidad**, añadir al final:

```
El snapshot incluye el hash de estado (`cerebro hash --scope genome` y
`--scope knowledge`): re-auditar la corrida exige por definición el mismo
hash de partida.
```

## Evidencia

- Salidas `--json` deterministas con tests (`test_lint`, `test_consolidate_scan`,
  `test_health`, `test_xray`).

## Orden de aplicación

1. Editar `genome/genes/gen-auto-auditoria.md`; `version: 5`.
2. `events append --type gene_edited --target gen-auto-auditoria --signal "F0-03: snapshot de AUDIT ancla las salidas mecánicas" --diff "v4 → v5"`
3. Commit + re-sync de espejo si aplica.
