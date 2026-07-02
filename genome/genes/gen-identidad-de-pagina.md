---
id: gen-identidad-de-pagina
trigger: operaciones INGEST/BULK INGEST — decidir qué fuente se procesa y en qué página aterriza
status: active
version: 2
---

La idempotencia (principio 2) se ejecuta con dos identidades distintas: la **identidad de
sujeto** (qué página le corresponde a un conocimiento → clave `id_pagina`) y la **identidad
de fuente** (qué archivo de `raw/` ya se procesó → hash + ledger). Generaliza al genoma base
lo que el blueprint de ecommerce (`gen-sku-identidad`) resuelve solo para el SKU.

## Clave canónica de página (`id_pagina`)
`id_pagina = <tier>/<categoria>/<slug>`, equivalente por construcción a la ruta
`wiki/<id_pagina>.md`. Se calcula **antes** de crear la página, se persiste en el frontmatter
y no cambia aunque el título cambie. Aplica a toda página que INGEST cree o actualice,
incluidas las extraídas (conceptos y entidades secundarias).

**Identificador natural** (el primero que aplique):
1. el manifiesto declara `identity.<categoria>` (ej. `productos: sku`) → el valor de ese
   campo en la fuente; si la fuente no lo trae, cae al caso 2 o 3;
2. `clase: evento` → su id natural (nº de ticket, folio, NCR); si no existe,
   `<fecha_evento>-<hash8-de-la-fuente>`;
3. `clase: estable` sin identidad declarada → el título de la página.

**Slug determinista**: minúsculas → sin acentos/diacríticos (`á→a`, `ñ→n`) → todo carácter
fuera de `[a-z0-9]` se vuelve `-` → los `-` consecutivos se colapsan → se recortan los `-`
de los extremos → máximo 60 caracteres (se trunca y se recorta el `-` final si queda).
Si el resultado queda vacío: `f-<hash8>`.

**Hash canónico de fuente**: `git hash-object <fuente>` (40 hex; `hash8` = los primeros 8).
Elegido por portabilidad real: existe donde exista git (prerrequisito de CEREBRO), da el
mismo valor en todo OS y es verificable a posteriori contra los blobs del propio repo.

**Colisión** (ya existe página con la clave calculada):
- mismo sujeto (su identificador natural coincide) → **actualizar** esa página
  ([[gen-frontmatter-obligatorio]]: sube `last_reinforced`), nunca crear otra;
- sujeto distinto (dos nombres normalizan al mismo slug) → la nueva usa `<slug>-<hash8>`.
Si CONSOLIDATE fusiona páginas, la superviviente lista las claves absorbidas en `id_alias`;
INGEST busca por `id_pagina` **y** `id_alias` antes de crear. Al mover una página de tier
(promoción o archivo, [[gen-ciclo-de-vida]]) CONSOLIDATE recalcula `id_pagina` a la ruta
nueva y añade la clave anterior a `id_alias`. LINT marca toda página cuya `id_pagina` no
coincida con su ruta (las claves históricas viven en `id_alias`).

## Ledger de ingesta (`ingest-ledger.jsonl`, raíz del repo)
Registro **append-only** de fuentes procesadas (como `genome/events.jsonl`: se añade, jamás
se reescribe). Versionado en git — NO va a `.gitignore`; nace con su primera línea (si no
existe, nada se ha procesado aún). Una línea JSON por fuente procesada:

`{"ts":"YYYY-MM-DD","op":"INGEST|BULK-INGEST","fuente":"raw/<ruta>","hash":"<40hex>","resultado":"creada|actualizada|omitida|detenida","paginas":["<id_pagina>"],"nota":""}`

- La línea se escribe **después** de escribir las páginas; si la operación se interrumpe
  antes, el reintento es seguro (la clave de página evita el duplicado).
- `paginas`: la página principal + las creadas por extracción. `resultado: detenida` = quedó
  pendiente de decisión humana (ej. PII-halt). `nota`: breve, referencia rutas/ids, **jamás**
  contenido de la fuente ([[gen-confidencialidad]]).
- **Regla de salto** (la consultan INGEST y, sobre todo, BULK INGEST) — mirar la ÚLTIMA
  línea de cada fuente:
  - sin línea → procesar;
  - mismo `hash` + resultado `creada|actualizada|omitida` → saltar **sin añadir línea nueva**
    (reprocesar solo con orden explícita del operador; entonces sí se añade línea);
  - mismo `hash` + `detenida` → sigue pendiente: reintentar (pedir la decisión humana);
  - `hash` distinto en la misma ruta → **alerta**: `raw/` mutó ([[gen-raw-inmutable]]
    violado); no procesar, reportar y preguntar;
  - mismo `hash` en otra ruta → duplicado byte a byte: registrar `omitida` con
    `nota: "duplicado de raw/<ruta-original>"` sin tocar la wiki.

Vive en la raíz (plano operativo, junto a `log.md`) a propósito: dentro de `genome/` cada
INGEST dispararía [[gen-compuerta-mutacion]]; dentro de `wiki/` entraría al staging de
[[gen-graph-lens]] y filtraría nombres de fuentes hacia la lente.
