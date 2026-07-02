---
id: gen-frontmatter-obligatorio
trigger: crear o actualizar una página en wiki/
status: active
version: 5
---

Toda página de `wiki/` nace y se mantiene con frontmatter YAML válido:
`title, type, tier, tags, confidence (0.0-1.0), created, last_reinforced, decay_rate,
sources, relations`. Campos **opcionales** según contexto (lista no exhaustiva):
`valido_hasta` ([[gen-vigencia-temporal]]), `sensibilidad` ([[gen-confidencialidad]], default =
`default_sensibilidad` del manifiesto; si no se declara, `interno`), `clase` / `fecha_evento` /
`volatile_fields` ([[gen-clase-temporal]]), `estado`
([[gen-entidad-con-estado]]) e `id_pagina` / `id_alias` ([[gen-identidad-de-pagina]];
INGEST siempre escribe `id_pagina` al crear una página).

`relations` ya **no es un set cerrado**: su núcleo reservado es
`{usa, depende_de, contradice, reemplaza}`, ampliable con los `relation_types` que la empresa
declare en `onboard/company.yaml` (ej. `producido_en`, `cita`, `tratada_segun`, `sobre_sku`).
LINT valida cada relación contra esa **unión** (núcleo ∪ declarados) y marca verbos no declarados.

Sin frontmatter no se considera conocimiento. Al actualizar una página existente por una
fuente que la confirma, sube `last_reinforced` a hoy y ajusta `confidence`; no dupliques.
Las páginas meta (`type: meta`, ej. `index.md`) quedan exentas de este gen y del LINT de huérfanos.
