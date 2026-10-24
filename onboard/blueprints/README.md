# Blueprints de sector

Recetas de `ONBOARD` listas para usar: **5 destiladas de industrias validadas en simulación** y
**1 (`seguridad-territorial`) derivada de marco normativo real verificado en fuente primaria**.
Un blueprint es un `company.yaml` semilla: trae los `relation_types`, `source_trust`,
`sintesis_umbral`, taxonomía, glosario y los **genes específicos del sector** ya pensados.

## Cómo se usa

```bash
# 1. Copia el blueprint de tu sector con el perfil de instalación ya fijado
python tools/cerebro.py init --profile memoria --blueprint <sector>   # o: cp onboard/blueprints/<sector>.yaml onboard/company.yaml
# 2. Reemplaza los placeholders "<tu ...>" por tus datos reales (init los deja tal cual a propósito)
# 3. Corre ONBOARD  →  genoma adaptado y determinista
```

**Mismo manifiesto → mismo genoma.** Esa es la garantía reproducible.

## Disponibles (catálogo `catalog.yaml`)

La lista canónica es [`catalog.yaml`](catalog.yaml): `python tools/cerebro.py blueprints` la
imprime y prueba que coincide con los archivos. Esta tabla es solo una copia legible.

| Sector | Archivo | Versión | CEREBRO mín. | Origen | Genes de sector |
|---|---|---|---|---|---|
| Producción / manufactura | `produccion.yaml` | 1.0.0 | 0.1.0 | simulación | `gen-trazabilidad-lote`, `gen-integridad-ncr` |
| Agencia automatización / marketing | `agencia.yaml` | 1.0.0 | 0.1.0 | simulación | `gen-accionables`, `gen-objecion-transversal` |
| Bufete legal | `legal.yaml` | 1.0.0 | 0.1.0 | simulación | `gen-vigencia-normativa`, `gen-conflicto-interes`, `gen-version-clausula` |
| Clínica / salud | `salud.yaml` | 1.0.0 | 0.1.0 | simulación | `gen-triada-clinica` |
| E-commerce / retail | `ecommerce.yaml` | 1.0.0 | 0.1.0 | simulación | `gen-sku-identidad` |
| Seguridad y convivencia territorial (CO) | `seguridad-territorial.yaml` | 1.0.0 | 0.1.0 | normativo | `gen-dato-con-corte`, `gen-territorializacion`, `gen-linea-base-y-meta`, `gen-trazabilidad-fonset` |

## Versiones y requisito mínimo (Fase 4.3)

Cada blueprint lleva su identidad dentro del archivo, al estilo del `manifest.json` de un
plugin de Obsidian:

```yaml
blueprint:
  id: legal              # = nombre del archivo sin .yaml
  version: "1.0.0"       # semver del blueprint
  min_cerebro: "0.1.0"   # versión mínima de tools/cerebro_core que necesita
```

- `init --blueprint` copia el bloque **tal cual** a `onboard/company.yaml`: el vault conserva
  de qué versión nació. ONBOARD no lo renderiza (es procedencia, no configuración), así que el
  genoma que produce el manifiesto no cambia y los casos de `worked/` siguen byte a byte.
- `init` y `onboard apply` **rechazan sin escribir nada** un blueprint cuyo `min_cerebro` sea
  mayor que la versión de `tools/` instalada, con el mensaje "actualiza tools/".
- `catalog.yaml` indexa los seis con su historial (`versions`: versión → requisito, fecha,
  cambios). `verify` corre los detectores CAT-01…CAT-06: correspondencia 1:1 entradas↔archivos,
  bloque coincidente, `genes` = `seed_genes`, historial creciente que termina en la versión
  actual, y ningún requisito por encima de lo instalado.
- Un vault desplegado ve su estado con `python tools/cerebro.py blueprints` (`al día` ·
  `desactualizado 1.0.0 → 1.1.0` · `artesanal`) y adopta una versión nueva como cualquier
  mejora del template: vía `genome_adopted` ([`gen-migracion-genoma`](../../genome/genes/gen-migracion-genoma.md)).

**Publicar una versión nueva**: sube `blueprint.version` en el YAML del sector (y
`min_cerebro` si exige algo nuevo de `tools/`), refleja ambos en `catalog.yaml` y añade la
línea al historial; `python tools/cerebro.py blueprints` debe salir en verde.

> **Los blueprints son livianos a propósito.** Todo lo universal (vigencia, confidencialidad,
> clase estable/evento, entidad con estado, confianza por fuente, síntesis de volumen) ya vive
> en el genoma base — el blueprint solo añade lo propio del sector. Mientras más madura el base,
> más livianos los blueprints. Salud y e-commerce ya quedaron con un solo gen de sector.

¿Tu sector no está? Copia `../company.example.yaml`, ajústalo, y al usarlo `EVOLVE` te irá
proponiendo los genes que tu negocio necesite.
