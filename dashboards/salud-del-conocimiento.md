---
title: Salud del conocimiento
type: meta
---

# Salud del conocimiento

> Apunta a `wiki/`, que en el template nace vacía: estas tablas se llenan tras `ONBOARD` +
> `INGEST`. Mientras tanto, verlas sin filas es lo esperado (panel con datos ya: [[salud-del-genoma]]).

## Vista nativa (Bases, plugin core — nada que instalar)

Cada sección embebe una vista de [[salud-del-conocimiento.base]]. Abre el `.base` para
ordenar, agrupar o añadir columnas sin tocar este archivo.

### Confianza más baja primero (candidatas a reforzar o decaer)
![[salud-del-conocimiento.base#Confianza más baja]]

### Vencidas (su valido_hasta ya pasó)
![[salud-del-conocimiento.base#Vencidas]]

### Confidenciales (no se anclan ni se citan textual)
![[salud-del-conocimiento.base#Confidenciales]]

### Eventos recientes
![[salud-del-conocimiento.base#Eventos recientes]]

### En cuarentena (`riesgo_inyeccion`, [[gen-anti-inyeccion]])
![[salud-del-conocimiento.base#En cuarentena]]

## Alternativa Dataview (plugin comunitario, opcional)

Mismas consultas para quien ya use Dataview. Si no está instalado, estos bloques se ven
como código y no rompen nada.

```dataview
TABLE tier AS "Tier", confidence AS "Conf", last_reinforced AS "Reforzado", decay_rate AS "Decae"
FROM "wiki"
WHERE type != "meta"
SORT confidence ASC
LIMIT 25
```

```dataview
TABLE valido_hasta AS "Venció", tier AS "Tier"
FROM "wiki"
WHERE valido_hasta AND valido_hasta < date(today)
SORT valido_hasta ASC
```

```dataview
TABLE tier AS "Tier", sensibilidad AS "Sensibilidad"
FROM "wiki"
WHERE sensibilidad = "confidencial"
```

```dataview
TABLE fecha_evento AS "Fecha", tier AS "Tier"
FROM "wiki"
WHERE clase = "evento"
SORT fecha_evento DESC
LIMIT 15
```
