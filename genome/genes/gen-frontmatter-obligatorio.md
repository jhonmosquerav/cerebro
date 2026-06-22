---
id: gen-frontmatter-obligatorio
trigger: crear o actualizar una página en wiki/
status: active
version: 2
---

Toda página de `wiki/` nace y se mantiene con frontmatter YAML válido:
`title, type, tier, tags, confidence (0.0-1.0), created, last_reinforced, decay_rate,
sources, relations`. Campos **opcionales** según contexto: `valido_hasta`
(ver [[gen-vigencia-temporal]]) y `sensibilidad` (ver [[gen-confidencialidad]], default `interno`).

`relations` ya **no es un set cerrado**: su núcleo reservado es
`{usa, depende_de, contradice, reemplaza}`, ampliable con los `relation_types` que la empresa
declare en `onboard/company.yaml` (ej. `producido_en`, `cita`, `tratada_segun`, `sobre_sku`).
LINT valida cada relación contra esa **unión** (núcleo ∪ declarados) y marca verbos no declarados.

Sin frontmatter no se considera conocimiento. Al actualizar una página existente por una
fuente que la confirma, sube `last_reinforced` a hoy y ajusta `confidence`; no dupliques.
Las páginas meta (`type: meta`, ej. `index.md`) quedan exentas de este gen y del LINT de huérfanos.
