---
tipo: propuesta-evolve
tarea: F0-14
status: approved
fecha: 2026-08-07
genes_afectados: [gen-lint]
origen: piloto B-02 (lotes 6-11) y CONSOLIDATE+LINT 2026-08-07 — 5 falsos positivos LNK-03 recurrentes
---

# Propuesta EVOLVE F0-14 — `gen-lint` v6 → v7: LNK-03 con memoria de descartes y sin nombres de archivo

## Motivación

En el piloto, 5 LNK-03 evaluados y rechazados con criterio (menciones dentro de nombres
de archivo como `events.jsonl`, y una línea-plantilla meta) **reaparecen en cada corrida**:
la señal se erosiona y nadie volverá a leerlos. Además el detector matcheaba basenames
dentro de filenames sin backticks. Y ningún gen decía QUIÉN aplica los LNK-03 que nacen
en cascada cuando otra operación crea una página muy mencionada.

## Diff (v6 → v7) — la infra ya existe (commit 57acf8b, 214 tests)

Al detector (f): (1) se excluyen menciones que son parte de un nombre de archivo
(`termino.ext`); (2) descartes persistentes en `lint-descartes.jsonl` (raíz, append-only,
`{ts, pagina, termino, motivo}`): lo descartado con motivo no se vuelve a sugerir y el
reporte muestra un contador único de omitidos; línea malformada → aviso DSC-01;
(3) dueño declarado: aplicar o descartar un LNK-03 es trabajo de la operación LINT,
incluida la cascada que provoque una página nueva de INGEST/CONSOLIDATE.
