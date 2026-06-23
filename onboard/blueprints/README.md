# Blueprints de sector

Recetas de `ONBOARD` listas para usar, destiladas de **5 industrias validadas en simulación**.
Un blueprint es un `company.yaml` semilla: trae los `relation_types`, `source_trust`,
`sintesis_umbral`, taxonomía, glosario y los **genes específicos del sector** ya pensados.

## Cómo se usa

```bash
# 1. Copia el blueprint de tu sector
cp onboard/blueprints/<sector>.yaml onboard/company.yaml
# 2. Reemplaza los placeholders "<tu ...>" por tus datos reales
# 3. Corre ONBOARD  →  genoma adaptado y determinista
```

**Mismo manifiesto → mismo genoma.** Esa es la garantía reproducible.

## Disponibles

| Sector | Archivo | Genes de sector |
|---|---|---|
| Producción / manufactura | `produccion.yaml` | `gen-trazabilidad-lote`, `gen-integridad-ncr` |
| Agencia automatización / marketing | `agencia.yaml` | `gen-accionables`, `gen-objecion-transversal` |
| Bufete legal | `legal.yaml` | `gen-vigencia-normativa`, `gen-conflicto-interes`, `gen-version-clausula` |
| Clínica / salud | `salud.yaml` | `gen-triada-clinica` |
| E-commerce / retail | `ecommerce.yaml` | `gen-sku-identidad` |

> **Los blueprints son livianos a propósito.** Todo lo universal (vigencia, confidencialidad,
> clase estable/evento, entidad con estado, confianza por fuente, síntesis de volumen) ya vive
> en el genoma base — el blueprint solo añade lo propio del sector. Mientras más madura el base,
> más livianos los blueprints. Salud y e-commerce ya quedaron con un solo gen de sector.

¿Tu sector no está? Copia `../company.example.yaml`, ajústalo, y al usarlo `EVOLVE` te irá
proponiendo los genes que tu negocio necesite.
