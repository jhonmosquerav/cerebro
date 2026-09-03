---
title: "{{title}}"
type: fuente
tier: semantic
tags: [fuente]
confidence: 0.9
created: "{{date}}"
last_reinforced: "{{date}}"
decay_rate: low
clase: estable
sensibilidad: interno
id_pagina: semantic/fuentes/<slug>
# valido_hasta: YYYY-MM-DD   # si la fuente caduca (gen-vigencia-temporal)
sources:
  - raw/<ruta-del-archivo>
relations: {}
---

# {{title}}

## Qué es
_Tipo de documento, emisor, fecha. La confianza inicial la fija el tipo de fuente
(`source_trust` del manifiesto) y la captura ([[gen-confianza-por-fuente]])._

## Qué sostiene
_Las afirmaciones clave que otras páginas citan (`cita`, `corrobora`)._

## Límites
_Qué NO dice, vigencia, y si hay contradicción con otra fuente (`contradice`)._
