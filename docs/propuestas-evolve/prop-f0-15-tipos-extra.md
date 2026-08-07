---
tipo: propuesta-evolve
tarea: F0-15
status: approved
fecha: 2026-08-07
genes_afectados: [gen-frontmatter-obligatorio]
origen: piloto B-02 (lotes 2 y 5) — FM-03 rechazó `type: spec` y `type: norma` declarados por la taxonomía
---

# Propuesta EVOLVE F0-15 — `gen-frontmatter-obligatorio` v7 → v8: el `type` se extiende como los verbos y los campos

## Motivación

La misma asimetría código/manifiesto que H-08 cerró para los campos seguía viva para los
tipos: el manifiesto del piloto declara las categorías `specs` y `normativa` y su
`document_types` incluye `norma`, pero `TYPES` en código es cerrado — dos lotes tuvieron
que degradar `spec`/`norma` a `concepto`/`entidad` por criterio de sesión.

## Diff (v7 → v8) — la infra ya existe (commit f873387, 214 tests)

Párrafo nuevo: el `type` sigue la misma regla que verbos y campos — núcleo del código,
ampliable con los `tipos_extra` que la empresa declare en `onboard/company.yaml`
(validados: minúsculas/guion_bajo, sin duplicar el núcleo); FM-03 valida contra la unión.
Quien declare una categoría taxonómica que implique un tipo nuevo, declara el tipo en el
mismo manifiesto: categoría y tipo pasan por la misma compuerta.
