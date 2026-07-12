---
tipo: propuesta-evolve
tarea: F0-05
status: pending
fecha: 2026-07-12
genes_afectados: [gen-compuerta-mutacion]
---

# Propuesta EVOLVE F0-05 — `gen-compuerta-mutacion` v1 → v2: hash-chain obligatorio en líneas nuevas

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

C-03 del backlog (diferido, hoy construido): la integridad de
`events.jsonl` descansaba en convención. Ya existe la verificación
append-only contra la historia de git (probada sobre los 90 commits reales)
y el hash-chain para líneas nuevas (`prev` = sha256 de la línea anterior).
Falta que el gen lo exija: toda línea nueva debe nacer encadenada. Las 63
líneas históricas sin `prev` siguen siendo válidas (migración honesta: la
cadena se verifica desde la primera portadora).

## Diff propuesto (v1 → v2)

En el paso (3) del flujo, sustituir "añade una línea a `genome/events.jsonl`
con `approved_by:"user"`" por:

```
añade la línea a genome/events.jsonl CON hash-chain usando
`python tools/cerebro.py events append --type <tipo> --target <gen>
--signal "<señal>" --diff "<diff>"` (valida el esquema y encadena
prev=sha256 de la línea anterior; escribir la línea a mano deja la cadena
con aviso EVT-06 en verify)
```

Y añadir al final del gen:

```
Verificación mecánica del ledger: `python tools/cerebro.py events verify`
(esquema por línea + cadena + append-only contra la historia de git). El
pre-commit (.githooks/pre-commit) bloquea cualquier commit que reescriba o
borre líneas existentes.
```

## Evidencia

- `tools/cerebro_core/events.py` + `tests/test_events.py` (manipular una
  línea intermedia rompe la cadena de forma detectable; la historia real
  del repo pasa el append-only).

## Orden de aplicación

1. Editar `genome/genes/gen-compuerta-mutacion.md`; `version: 2`.
2. La MISMA aprobación se registra ya con la herramienta:
   `events append --type gene_edited --target gen-compuerta-mutacion --signal "F0-05: hash-chain obligatorio en líneas nuevas" --diff "v1 → v2"`
3. Commit + re-sync de espejo si aplica.
