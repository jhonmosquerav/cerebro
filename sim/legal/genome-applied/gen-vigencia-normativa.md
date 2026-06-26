---
id: gen-vigencia-normativa
trigger: "la página es de tipo concepto/normativa o jurisprudencia"
status: active
version: 1
seeded_from: "company.yaml (extensión, aprobado 2026-06-26)"
---

Las páginas de tipo normativa y jurisprudencia declaran el campo
`vigencia: {vigente | en-revision | derogada | no-vigente}`.

- `vigente`: plenamente en vigor.
- `en-revision`: bajo amenaza de modificación por evento (reforma, sentencia
  superior); QUERY debe advertir siempre.
- `derogada`: sin efecto jurídico; confidence baja a ≤0.1 automáticamente.
- `no-vigente`: anteproyecto o norma no promulgada; confidence ≤0.5.

La vigencia la actualiza un evento (sentencia, promulgación), no el tiempo.
LINT valida el campo contra estos cuatro valores en toda página normativa/jurisprudencia.
