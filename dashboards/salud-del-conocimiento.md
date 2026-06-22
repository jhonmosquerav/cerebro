---
title: Salud del conocimiento
type: meta
---

# Salud del conocimiento

> Apunta a `wiki/`. Cambia `FROM "wiki"` por `FROM "sim"` para ver los escenarios simulados con datos.

## Confianza más baja primero (candidatas a reforzar o decaer)

```dataview
TABLE tier AS "Tier", confidence AS "Conf", last_reinforced AS "Reforzado", decay_rate AS "Decae"
FROM "wiki"
WHERE type != "meta"
SORT confidence ASC
LIMIT 25
```

## Vencidas (su valido_hasta ya pasó)

```dataview
TABLE valido_hasta AS "Venció", tier AS "Tier"
FROM "wiki"
WHERE valido_hasta AND valido_hasta < date(today)
SORT valido_hasta ASC
```

## Confidenciales (no se anclan ni se citan textual)

```dataview
TABLE tier AS "Tier", sensibilidad AS "Sensibilidad"
FROM "wiki"
WHERE sensibilidad = "confidencial"
```

## Eventos recientes

```dataview
TABLE fecha_evento AS "Fecha", tier AS "Tier"
FROM "wiki"
WHERE clase = "evento"
SORT fecha_evento DESC
LIMIT 15
```
