---
tipo: spec-de-diseno
fecha: 2026-10-23
estado: aprobado-por-instruccion-del-operador
alcance: Fase 4.3 del roadmap (distribución) — catálogo de blueprints con versiones y requisito mínimo; cierre de la Fase 4 con el artículo del caso público colombiano (4.4)
origen: plan único 2026-10-20 (backlog 2 y 3) y revisión de obsidian-releases (`community-plugins.json`, `manifest.json` con `version`/`minAppVersion`, `versions.json`) en docs/revision-repos-2026-10-20.md
---

# Catálogo de blueprints con versiones y requisito mínimo — diseño

## Contexto y porqué

Los seis blueprints de `onboard/blueprints/` son el camino (b) de ONBOARD: una receta por
sector que `init --blueprint <sector>` copia a `onboard/company.yaml`. Hoy no tienen
**versión** ni declaran **qué CEREBRO necesitan**. Consecuencias concretas:

1. Un vault desplegado no sabe de qué versión de blueprint nació. Cuando el template publica
   un blueprint mejorado (un gen de sector nuevo, un `relation_type` más), la doctrina de
   distribución ([[gen-migracion-genoma]] v2, evento `genome_adopted`) no tiene contra qué
   comparar: "¿mi `seguridad-territorial` está al día?" no tiene respuesta mecánica.
2. Un blueprint puede exigir una capacidad del `tools/` que un clon viejo no tiene (p. ej.
   `tipos_extra` existe desde gen-frontmatter v8; `profile:` desde gen-perfiles v1). Hoy el
   fallo aparece tarde, al aplicar, y con un mensaje que no dice "actualiza CEREBRO".
3. La tabla de `onboard/blueprints/README.md` es prosa: nada comprueba que liste los seis
   archivos ni que los genes que anuncia sean los que el YAML siembra.

obsidian-releases resuelve lo mismo para plugins con tres piezas: `manifest.json` dentro
del plugin (`id`, `version` semver, `minAppVersion`), `community-plugins.json` como índice
y `versions.json` con el historial versión → requisito mínimo. CEREBRO adopta el patrón
tal cual, en YAML del subconjunto de `miniyaml`, y lo vuelve **verificable en `verify`**.

## Principio rector

> El blueprint lleva su identidad; el catálogo la indexa; `verify` prueba que coinciden.
> Nada de esto cambia el genoma que un manifiesto produce: el bloque es procedencia, no
> configuración, y el `state-hash` de los casos `worked/` no se mueve.

## Diseño

### 1. Bloque `blueprint:` dentro de cada blueprint (y del manifiesto que nace de él)

```yaml
blueprint:
  id: seguridad-territorial     # = nombre del archivo sin .yaml
  version: "1.0.0"              # semver del blueprint
  min_cerebro: "0.1.0"          # versión mínima de tools/cerebro_core (__version__)
```

- Viaja con el archivo: `init --blueprint` lo copia tal cual a `onboard/company.yaml`, así
  el vault conserva su procedencia (`hash --scope all` la cubre; `company-profile.md` **no**
  la renderiza, para que el cambio sea aditivo y `worked/` siga byte a byte).
- `manifest.validate` lo valida si existe: `id` slug, `version` y `min_cerebro` semver
  (`X.Y.Z`), y **`min_cerebro` ≤ `__version__`** — si no, error legible: "este manifiesto
  exige CEREBRO ≥ 0.2.0; tienes 0.1.0: actualiza `tools/`". `init` y `onboard apply`
  heredan el rechazo antes de escribir nada (misma garantía de [[gen-onboard]] v5).
- Un `company.yaml` artesanal (modo a o c) no necesita el bloque: su ausencia es legítima.

### 2. `onboard/blueprints/catalog.yaml` — el índice

```yaml
catalog_version: 1
cerebro_version: "0.1.0"          # tools/ con el que se validó este catálogo
blueprints:
  - id: seguridad-territorial
    name: "Seguridad y convivencia territorial (CO)"
    file: seguridad-territorial.yaml
    version: "1.0.0"
    min_cerebro: "0.1.0"
    origen: normativo                 # simulacion | normativo | piloto
    genes: [gen-dato-con-corte, gen-territorializacion, gen-linea-base-y-meta, gen-trazabilidad-fonset]
    versions:
      - { version: "1.0.0", min_cerebro: "0.1.0", fecha: 2026-10-23, cambios: "primera versión catalogada" }
```

Es la única lista que un tercero necesita leer para saber qué hay, qué siembra y qué
requiere. Se mantiene a mano (como `community-plugins.json`) pero **nunca se le cree**:
el validador la contrasta con los archivos.

### 3. Validador `cerebro_core/blueprints.py` + subcomando `blueprints`

Detectores (todos `error`, código `CAT-xx`, salida determinista):

| Código | Qué comprueba |
|---|---|
| CAT-01 | el catálogo parsea, `catalog_version` es entero, `blueprints` es lista no vacía; cada entrada trae `id`, `file`, `version`, `min_cerebro`, `genes`, `versions` con los tipos correctos |
| CAT-02 | correspondencia 1:1 entre entradas y archivos `*.yaml` de la carpeta (sin huérfanos en ningún sentido); `id` = nombre del archivo; `file` existe |
| CAT-03 | el bloque `blueprint:` del archivo coincide con la entrada (`id`, `version`, `min_cerebro`); un blueprint sin bloque es error |
| CAT-04 | `genes` del catálogo = ids de `seed_genes` del archivo, en orden |
| CAT-05 | `versions` no vacío, semver estrictamente creciente, la última = `version` y su `min_cerebro` = el de la entrada |
| CAT-06 | ningún `min_cerebro` supera `__version__` (el template no distribuye lo que no puede correr); `cerebro_version` del catálogo = `__version__` |

`python tools/cerebro.py blueprints [--json]` imprime la tabla (id, versión, min_cerebro,
origen, genes) y, si el vault tiene `onboard/company.yaml` con bloque `blueprint:`, su
**estado frente al catálogo**: `al día` · `desactualizado (1.0.0 → 1.1.0)` ·
`desconocido en el catálogo` · `sin bloque blueprint (manifiesto artesanal)`. Exit 0
limpio · 1 con hallazgos. `verify` gana la línea `catálogo de blueprints (N)` cuando el
archivo existe (un vault sin `onboard/blueprints/` no falla: la línea no aparece).

### 4. Genoma (bajo compuerta, `docs/propuestas-evolve/prop-cat-01-*.md`)

- [[gen-onboard]] v9 → v10: párrafo "Catálogo de blueprints (v10)": qué declara un
  blueprint, qué indexa el catálogo, que `init`/`onboard apply` rechazan `min_cerebro`
  mayor que la versión instalada, y que el bloque queda en el manifiesto como procedencia.
- [[gen-migracion-genoma]] v2 → v3: al adoptar una release, además de los genes, se compara
  `blueprint.version` del manifiesto local con el catálogo del template; un blueprint con
  versión mayor se adopta en el mismo `genome_adopted` (sus genes de sector cambian de
  versión como cualquier otro) y el `diff` del evento lo nombra.
- `CLAUDE.md`: `blueprints` en la lista de validadores; fila ONBOARD menciona el catálogo.

### 5. Lo que NO hace

- No renderiza la procedencia en `company-profile.md` (cambiaría los bytes esperados de
  `worked/`; si el uso lo pide, va por compuerta aparte).
- No descarga nada ni consulta red: el catálogo es el del clon.
- No sube `__version__`: `0.1.0` sigue siendo la versión del `tools/`; el catálogo nace
  con `min_cerebro: "0.1.0"` en los seis porque los seis corren con lo que hay.
- No auto-corrige el catálogo: la deriva se reporta y la arregla quien edita el blueprint.

## Fase 4.4 — artículo del caso público colombiano

`docs/caso-piscc-colombia.md`: el caso del blueprint `seguridad-territorial` y del caso
trabajado `worked/piscc-demo`, escrito para lectores de alcaldías, observatorios del delito
y equipos de datos de LATAM, con el estilo editorial del operador (historia que ilustra el
problema → análisis → solución → impacto; fuentes y límites explícitos). Verdades que el
artículo no maquilla: municipio ficticio, cero datos ingeridos, verificación normativa sin
estudio de vigencia exhaustivo, guía del DNP no leída en su fuente. Enlazado desde el README.

## Verificación

- `tests/test_blueprints.py`: catálogo del repo en verde; cada detector con un caso que
  lo dispara sobre copia temporal; `init --blueprint` rechaza `min_cerebro` futuro sin
  escribir; `onboard apply` idem; CLI `blueprints` exit 0 y `--json` estable.
- `tests/test_worked.py` sin cambios y en verde: `state-hash` de los 3 casos intacto.
- `verify` en verde con la línea nueva; `mirror` en verde tras la mutación.
