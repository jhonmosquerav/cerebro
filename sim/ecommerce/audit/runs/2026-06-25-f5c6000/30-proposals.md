---
run_id: 2026-06-25-f5c6000
gen_version: 1
audit_date: 2026-06-25
candidates: 6
confirmed: 6
proposals: 3
status: pending
---

# Propuestas de auditoría — ecommerce 2026-06-25-f5c6000

N = min(3, 6 confirmados) = **3 propuestas**, rankeadas por impacto desc.
Todas en `status: pending`. Ninguna se aplica sin aprobación del humano.

---

## P1 — Añadir `volatile_fields` en frontmatter de las 4 fichas SKU y actualizar `gen-dato-volatil`

| campo | valor |
|---|---|
| id | P1 |
| fecha | 2026-06-25 |
| origen candidato | C6 |
| clase | contradicción entre páginas wiki |
| severidad | 4 |
| alcance | 4 |
| impacto | **44** |
| status | pending |

**Motivo.** `gen-dato-volatil` prescribe que si `valido_a` es anterior a hoy, QUERY debe
ADVERTIR el dato como vencido. Hoy (2026-06-25) los campos de precio, stock y estado en las
4 fichas de producto tienen `valido_a: 2026-06-20` (5 días vencidos). El campo `valido_a`
está enterrado en una tabla markdown del cuerpo de cada ficha, no en el frontmatter
estructurado. LINT y QUERY no pueden detectar ese vencimiento sin parsear prosa libre, lo que
hace imposible cumplir la advertencia prescrita por el gen. Esto es una contradicción entre la
regla activa y el estado observable del corpus.

**Evidencia.**
- `[[sim/ecommerce/genome-applied/gen-dato-volatil]]` regla: "si `valido_a` es anterior a hoy, el agente lo ADVIERTE".
- `[[sim/ecommerce/wiki/semantic/productos/SKU-CAF-2200]]` tabla body: precio/stock/estado con `valido_a: 2026-06-20`.
- `[[sim/ecommerce/wiki/semantic/productos/SKU-CAF-2201]]` mismo patrón.
- `[[sim/ecommerce/wiki/semantic/productos/SKU-OLL-0900]]` mismo patrón.
- `[[sim/ecommerce/wiki/semantic/productos/SKU-ORG-1450]]` mismo patrón.
- `[[sim/ecommerce/regresion]]` propone M4 (`volatile_fields` en frontmatter) para resolver exactamente esta fricción.

**Diff.**
```yaml
# Añadir en frontmatter de cada una de las 4 fichas SKU
# (SKU-CAF-2200, SKU-CAF-2201, SKU-OLL-0900, SKU-ORG-1450):
volatile_fields:
  - { campo: precio, valido_a: 2026-06-20 }
  - { campo: stock,  valido_a: 2026-06-20 }
  - { campo: estado, valido_a: 2026-06-20 }
# Mantener la tabla en el body solo como display humano.
```

```diff
# sim/ecommerce/genome-applied/gen-dato-volatil.md — aclarar ubicación del campo:
- "campo `valido_a: <fecha>`"
+ "campo `valido_a: <fecha>` en `volatile_fields` del frontmatter (no en el cuerpo);
+  el cuerpo puede mostrar la tabla como display, pero el frontmatter es lo estructurado
+  y detectable por LINT/QUERY."
```

---

## P2 — Actualizar `company.yaml` entities.productos para incluir SKU-CAF-2201 y SKU-ORG-1450

| campo | valor |
|---|---|
| id | P2 |
| fecha | 2026-06-25 |
| origen candidato | C5 |
| clase | contradicción entre páginas wiki |
| severidad | 4 |
| alcance | 3 |
| impacto | **43** |
| status | pending |

**Motivo.** `company.yaml` declara `entities.productos: ["SKU-CAF-2200", "SKU-OLL-0900"]`.
El wiki tiene 4 páginas de producto (`SKU-CAF-2200`, `SKU-CAF-2201`, `SKU-OLL-0900`,
`SKU-ORG-1450`) con frontmatter completo, sources apuntando a `raw/catalogo-2026-06`, e
índice actualizado. El manifiesto es la fuente de verdad del manifiesto de configuración del
sistema; su desactualización lo convierte en una fuente contradictoria con el estado real del
corpus. No está documentado como defecto conocido en `regresion.md`.

**Evidencia.**
- `[[sim/ecommerce/company.yaml]]` campo `entities.productos` — lista incompleta.
- `[[sim/ecommerce/wiki/semantic/productos/SKU-CAF-2201]]` — existe con fuentes y relaciones.
- `[[sim/ecommerce/wiki/semantic/productos/SKU-ORG-1450]]` — existe con fuentes y relaciones.
- `[[sim/ecommerce/wiki/index]]` — lista los 4 productos en sección `semantic/productos`.

**Diff.**
```yaml
# sim/ecommerce/company.yaml — entities.productos:
# antes:
productos: ["SKU-CAF-2200", "SKU-OLL-0900"]
# después:
productos: ["SKU-CAF-2200", "SKU-CAF-2201", "SKU-OLL-0900", "SKU-ORG-1450"]
```

---

## P3 — Crear páginas de categoría faltantes y actualizar index

| campo | valor |
|---|---|
| id | P3 |
| fecha | 2026-06-25 |
| origen candidato | C1 |
| clase | vacío (link roto / categoría sin cobertura) |
| severidad | 2 |
| alcance | 3 |
| impacto | **23** |
| status | pending |

**Motivo.** `SKU-OLL-0900.md` declara `relations.usa: ["[[cat-ollas-y-sartenes]]"]` y
`SKU-ORG-1450.md` declara `relations.usa: ["[[cat-organizadores]]"]`. Ninguna de las dos
páginas de categoría existe bajo `wiki/semantic/categorias/`. La taxonomía del manifiesto
lista las 3 categorías (`cafeteras`, `ollas-y-sartenes`, `organizadores`) pero solo
`cat-cafeteras.md` fue creada. Los 2 links son huérfanos; el grafo de relaciones está
incompleto y QUERY no puede navegar de SKU a categoría para ollas y organizadores.

**Evidencia.**
- `[[sim/ecommerce/wiki/semantic/productos/SKU-OLL-0900]]` — `relations.usa: ["[[cat-ollas-y-sartenes]]"]`.
- `[[sim/ecommerce/wiki/semantic/productos/SKU-ORG-1450]]` — `relations.usa: ["[[cat-organizadores]]"]`.
- `[[sim/ecommerce/wiki/index]]` — `categorias` lista solo `[[cat-cafeteras]]`.
- `[[sim/ecommerce/company.yaml]]` — `entities.categorias: ["cafeteras", "ollas-y-sartenes", "organizadores"]`.

**Diff.**
```
Crear: sim/ecommerce/wiki/semantic/categorias/cat-ollas-y-sartenes.md
  ---
  title: Ollas y Sartenes — categoría
  type: concepto
  tier: semantic
  tags: [categoria, ollas-y-sartenes]
  confidence: 0.85
  created: 2026-06-25
  last_reinforced: 2026-06-25
  decay_rate: low
  sources:
    - "[[raw/catalogo-2026-06]]"
  relations:
    usa: []
    depende_de: []
    contradice: []
    reemplaza: []
    agrupa: ["[[SKU-OLL-0900]]"]
  ---
  # Categoría: Ollas y Sartenes
  Nodo de taxonomía del catálogo. Agrupa los SKUs de ollas y sartenes.
  Productos: [[SKU-OLL-0900]] (Set Cumbre 7 piezas).

Crear: sim/ecommerce/wiki/semantic/categorias/cat-organizadores.md
  ---
  title: Organizadores — categoría
  type: concepto
  tier: semantic
  tags: [categoria, organizadores]
  confidence: 0.85
  created: 2026-06-25
  last_reinforced: 2026-06-25
  decay_rate: low
  sources:
    - "[[raw/catalogo-2026-06]]"
  relations:
    usa: []
    depende_de: []
    contradice: []
    reemplaza: []
    agrupa: ["[[SKU-ORG-1450]]"]
  ---
  # Categoría: Organizadores
  Nodo de taxonomía del catálogo. Agrupa los SKUs de almacenamiento y organización.
  Productos: [[SKU-ORG-1450]] (Organizador Modular Closet 12 cubos).

Actualizar: sim/ecommerce/wiki/index.md — sección "categorias":
  antes: - **categorias** — [[cat-cafeteras]]
  después: - **categorias** — [[cat-cafeteras]] · [[cat-ollas-y-sartenes]] · [[cat-organizadores]]
```
