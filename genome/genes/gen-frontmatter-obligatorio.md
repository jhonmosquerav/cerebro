---
id: gen-frontmatter-obligatorio
trigger: crear o actualizar una página en wiki/
status: active
version: 7
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
`{usa, depende_de, contradice, reemplaza}`, ampliable con (a) los **verbos que los genes
activos declaran como esquema** —`agrega` / `agregado_en` ([[gen-sintesis-de-volumen]],
[[gen-consolidate]]), `sucede_a` / `proviene_de` ([[gen-entidad-con-estado]]), `corrobora`
([[gen-confianza-por-fuente]]), `deriva_de` ([[gen-consolidate]])— y (b) los `relation_types`
que la empresa declare en `onboard/company.yaml` (ej. `producido_en`, `cita`, `tratada_segun`,
`sobre_sku`). `supersede` no es verbo aparte: se unifica con el núcleo `reemplaza`.
LINT valida cada relación contra esa **unión** (núcleo ∪ verbos de genes activos ∪
`relation_types`) y marca verbos no declarados.

Los **CAMPOS** siguen la misma regla que los verbos: el núcleo es el listado de arriba
(obligatorios + opcionales), ampliable con (a) los campos que los genes activos declaren
como esquema y (b) los `campos_extra` que la empresa declare en `onboard/company.yaml`.
LINT valida cada campo contra esa unión y solo marca `FM-04` lo que no aparezca en ninguna
de las tres fuentes. Un gen sembrado que **exige** un campo lo está declarando: pedirlo y
que el validador lo rechace sería incoherente — y dejaría al vault con avisos permanentes
por cumplir su propio genoma. Quien siembre un gen con campo propio declara el campo en el
mismo manifiesto: gen y campo pasan por la misma compuerta.

Sin frontmatter no se considera conocimiento. Al actualizar una página existente por una
fuente que la confirma, sube `last_reinforced` a hoy y ajusta `confidence`; no dupliques.
Las páginas meta (`type: meta`, ej. `index.md`) quedan exentas de este gen y del LINT de huérfanos.
