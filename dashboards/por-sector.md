---
title: Vistas por sector (plantilla)
type: meta
---

# Vistas por sector

`ONBOARD` adapta esta página a tu negocio. Según el `company-profile`, el agente recomienda
(no impone) algo así:

- **Agencia / ventas** → pipeline de leads por `estado`, precios vencidos, objeciones más usadas.
- **Clínica / salud** → protocolos vencidos (alerta de seguridad), confidencialidad de pacientes.
- **Producción** → no-conformidades abiertas por lote/máquina, mantenimientos próximos.
- **E-commerce** → SKUs con stock/precio vencido, síntesis de tickets por producto.
- **Legal** → contratos por vigencia, precedentes citados, conflictos de interés.

## Vista nativa (Bases, plugin core — nada que instalar)

Plantilla en [[por-sector.base]]: tras `ONBOARD`, el agente añade ahí las vistas concretas
de tu sector (una vista por pregunta recurrente) y las embebe aquí.

### Ejemplo: pipeline (entidades con estado)
![[por-sector.base#Pipeline por estado]]

### Ejemplo: tarjetas por tipo
![[por-sector.base#Tarjetas por tipo]]

## Alternativa Dataview (plugin comunitario, opcional)

```dataview
TABLE estado AS "Estado", tier AS "Tier"
FROM "wiki"
WHERE estado
SORT estado ASC
```

> Tras `ONBOARD`, el agente reemplaza estos ejemplos por las vistas concretas de tu sector
> (y `gen-visualizacion` propone cuáles).
