---
title: SKU-CAF-2200 — Cafetera Espresso Aurora 15 bar (Plata)
type: entidad
tier: semantic
tags: [producto, sku, cafeteras, cafetera-aurora]
confidence: 0.95
created: 2026-06-22
last_reinforced: 2026-06-22
decay_rate: low          # los specs estables son de baja decadencia
sources:
  - "[[raw/catalogo-2026-06]]"
  - "[[raw/tickets-soporte-2026-06]]"
  - "[[raw/resenas-cafetera-aurora]]"
relations:
  usa: ["[[cat-cafeteras]]"]
  depende_de: ["[[prov-electrohogar-import]]"]
  contradice: []
  reemplaza: []
  # relaciones del sector (gen-sku-identidad):
  variante_de: []
  variantes: ["[[SKU-CAF-2201]]"]
  referido_por: ["[[TKT-5521]]", "[[TKT-5530]]", "[[TKT-5561]]", "[[resenas-aurora]]", "[[sintesis-portafiltro-aurora]]"]
volatile_fields:
  - { campo: precio, valido_a: 2026-06-20 }
  - { campo: stock,  valido_a: 2026-06-20 }
  - { campo: estado, valido_a: 2026-06-20 }
---

# SKU-CAF-2200 — Cafetera Espresso Aurora 15 bar (Plata)

Página única y estable del SKU ([[gen-sku-identidad]]). Una sola ficha por SKU; las demás
entidades enlazan aquí, no la duplican.

## Specs estables (decay_rate: low, confidence 0.95)
- Categoría: [[cat-cafeteras]]
- Presión: 15 bar · Depósito: 1.2 L · Cuerpo: acero inoxidable
- 220V / 1100W · 30x20x33 cm · 4.1 kg
- Garantía: 12 meses (proveedor [[prov-electrohogar-import]])
- Variante de color: [[SKU-CAF-2201]] (negro mate)

## Datos volátiles (decay_rate: high — [[gen-dato-volatil]])
| campo  | valor       | valido_a   |
|--------|-------------|------------|
| precio | $389.900    | 2026-06-20 |
| stock  | 42 (Bogotá) / 11 (Medellín) | 2026-06-20 |
| estado | activo / publicado | 2026-06-20 |

> ⚠️ Al consultar después de `valido_a`, advertir que precio/stock pueden estar vencidos.

## Señal de calidad
3 tickets + reseñas reportan **portafiltro flojo** → ver [[sintesis-portafiltro-aurora]].
