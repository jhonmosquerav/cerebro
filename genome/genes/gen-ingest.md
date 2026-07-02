---
id: gen-ingest
trigger: operación INGEST sobre una fuente
status: active
version: 3
---

INGEST convierte una fuente en conocimiento enlazado siguiendo la cápsula
[[ingesta-de-fuente]]: consulta el ledger de ingesta (fuente ya procesada con el mismo hash →
no se reprocesa, salvo orden explícita; [[gen-identidad-de-pagina]]), lee desde `raw/` sin
tocarla, clasifica tipo y tier, calcula la clave `id_pagina` ANTES de crear, crea/actualiza
la página con frontmatter, extrae conceptos y entidades (creando sus páginas si faltan, cada
una con su propia `id_pagina`), enlaza con relaciones tipadas y `[[wiki-links]]`, y registra
ancla **según los criterios deterministas de [[gen-jerarquizacion-indice]]** (en `index.md`,
o en el `hub-<área>` si el área ya se partió; si los criterios dicen que no, no se ancla)
+ línea en `log.md` + línea en `ingest-ledger.jsonl`.
Idempotente **por algoritmo**, no por prosa: misma `id_pagina` (o `id_alias`) → se actualiza
y refuerza esa página, nunca se crea otra. No inventa datos que no estén en la fuente.
