---
title: SKU-CAF-2201 — Cafetera Espresso Aurora 15 bar (Negro Mate)
type: entidad
tier: semantic
tags: [producto, sku, cafeteras, cafetera-aurora, variante]
confidence: 0.9
created: 2026-06-22
last_reinforced: 2026-06-22
decay_rate: low
sources:
  - "[[raw/catalogo-2026-06]]"
  - "[[raw/tickets-soporte-2026-06]]"
relations:
  usa: ["[[cat-cafeteras]]"]
  depende_de: ["[[prov-electrohogar-import]]"]
  contradice: []
  reemplaza: []
  variante_de: ["[[SKU-CAF-2200]]"]
  referido_por: ["[[TKT-5544]]", "[[sintesis-portafiltro-aurora]]"]
volatile_fields:
  - { campo: precio, valido_a: 2026-06-20 }
  - { campo: stock,  valido_a: 2026-06-20 }
  - { campo: estado, valido_a: 2026-06-20 }
---

# SKU-CAF-2201 — Cafetera Espresso Aurora 15 bar (Negro Mate)

Variante de color de [[SKU-CAF-2200]] ([[gen-sku-identidad]]: misma familia, distinto SKU).
Specs idénticas salvo el acabado. Página separada por SKU para no fusionar inventarios.

## Datos volátiles (decay_rate: high)
| campo  | valor    | valido_a   |
|--------|----------|------------|
| precio | $389.900 | 2026-06-20 |
| stock  | 7 (Bogotá) | 2026-06-20 |
| estado | activo / publicado | 2026-06-20 |

## Señal de calidad
[[TKT-5544]] confirma el mismo defecto de portafiltro en la variante negra → el defecto NO
es de color sino de la familia/lote del proveedor. Ver [[sintesis-portafiltro-aurora]].
