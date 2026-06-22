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

## Ejemplo: pipeline (entidades con estado)

```dataview
TABLE estado AS "Estado", tier AS "Tier"
FROM "wiki"
WHERE estado
SORT estado ASC
```

> Tras `ONBOARD`, el agente reemplaza este ejemplo por las vistas concretas de tu sector
> (y `gen-visualizacion` propone cuáles).
