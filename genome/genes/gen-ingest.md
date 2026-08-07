---
id: gen-ingest
trigger: operación INGEST sobre una fuente
status: active
version: 5
---

INGEST convierte una fuente en conocimiento enlazado siguiendo la cápsula
[[ingesta-de-fuente]]: consulta el ledger de ingesta (fuente ya procesada con el mismo hash →
no se reprocesa, salvo orden explícita; [[gen-identidad-de-pagina]]), lee la fuente sin
tocarla —directamente si es texto, o a través de un **derivado declarado** si no lo es
(cápsula [[ingesta-de-fuente]], paso 1: no escribe en `raw/`, vive aparte, y registra hash
de origen, hash propio y versión del extractor)—, clasifica tipo y tier, calcula la clave `id_pagina` ANTES de crear, crea/actualiza
la página con frontmatter, extrae conceptos y entidades (creando sus páginas si faltan, cada
una con su propia `id_pagina`), enlaza con relaciones tipadas y `[[wiki-links]]`, y registra
ancla **según los criterios deterministas de [[gen-jerarquizacion-indice]]** (en `index.md`,
o en el `hub-<área>` si el área ya se partió; si los criterios dicen que no, no se ancla)
+ línea en `log.md` + línea en `ingest-ledger.jsonl`.
Idempotente **por algoritmo**, no por prosa: misma `id_pagina` (o `id_alias`) → se actualiza
y refuerza esa página, nunca se crea otra. No inventa datos que no estén en la fuente.

Reglas de agrupación (destiladas del piloto; la idempotencia semántica exige que la
clasificación no dependa de la sesión): (1) N documentos cortos del mismo emisor sobre
features de un mismo objeto → una **entidad agregadora + conceptos satélite**, no una
página por documento; (2) un benchmark se ancla con `mide` a una **página-capacidad**
(se crea si falta); (3) `cita` apunta a la página que el trabajo citado **sostiene** (no
existen páginas-fuente); (4) concepto vs entidad se decide por lo que la fuente sostiene,
jamás por el nombre propio; (5) renombre declarado ("X, formerly Y") → página nueva con
`reemplaza` documentando el renombre, sin degradar la anterior si su fuente sigue válida.
