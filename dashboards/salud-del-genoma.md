---
title: Salud del genoma
type: meta
---

# Salud del genoma

Genes activos, su versión y cuándo se disparan.

## Vista nativa (Bases, plugin core — nada que instalar)

![[salud-del-genoma.base#Genes activos]]

### Genes deprecados (si los hay)
![[salud-del-genoma.base#Genes deprecados]]

### Cápsulas
![[salud-del-genoma.base#Cápsulas]]

## Alternativa Dataview (plugin comunitario, opcional)

```dataview
TABLE WITHOUT ID id AS "Gen", status AS "Estado", version AS "v", trigger AS "Se activa cuando"
FROM "genome/genes"
SORT id ASC
```

```dataview
TABLE WITHOUT ID id AS "Gen", version AS "v"
FROM "genome/genes"
WHERE status = "deprecated"
```

> La historia completa de mutaciones (con señal y diff) vive en `genome/events.jsonl`.
