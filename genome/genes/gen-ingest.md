---
id: gen-ingest
trigger: operación INGEST sobre una fuente
status: active
version: 2
---

INGEST convierte una fuente en conocimiento enlazado siguiendo la cápsula
[[ingesta-de-fuente]]: consulta el ledger de ingesta (fuente ya procesada con el mismo hash →
no se reprocesa, salvo orden explícita; [[gen-identidad-de-pagina]]), lee desde `raw/` sin
tocarla, clasifica tipo y tier, calcula la clave `id_pagina` ANTES de crear, crea/actualiza
la página con frontmatter, extrae conceptos y entidades (creando sus páginas si faltan, cada
una con su propia `id_pagina`), enlaza con relaciones tipadas y `[[wiki-links]]`, y registra
ancla en `index.md` (si aplica) + línea en `log.md` + línea en `ingest-ledger.jsonl`.
Idempotente **por algoritmo**, no por prosa: misma `id_pagina` (o `id_alias`) → se actualiza
y refuerza esa página, nunca se crea otra. No inventa datos que no estén en la fuente.
