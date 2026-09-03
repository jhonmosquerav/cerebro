---
title: "{{title}}"
type: entidad
tier: semantic
tags: [entidad]
confidence: 0.7
created: "{{date}}"
last_reinforced: "{{date}}"
decay_rate: medium
clase: estable
sensibilidad: interno
id_pagina: semantic/<categoria>/<slug>
# estado: activo        # solo si la entidad cambia de estado (gen-entidad-con-estado)
sources: []
relations: {}
---

# {{title}}

## Ficha
- **Categoría:** _(clientes / productos / herramientas / …)_
- **Identificador natural:** _(el que declare `identity.<categoría>` en el manifiesto)_

## Qué sabemos
_Hechos estables, cada uno con su fuente._

## Historial de estado
_Si tiene `estado`, cada cambio va con evento de respaldo (`sucede_a` / `proviene_de`)._
