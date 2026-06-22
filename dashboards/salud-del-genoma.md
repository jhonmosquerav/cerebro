---
title: Salud del genoma
type: meta
---

# Salud del genoma

Genes activos, su versión y cuándo se disparan. (Requiere Dataview.)

```dataview
TABLE WITHOUT ID id AS "Gen", status AS "Estado", version AS "v", trigger AS "Se activa cuando"
FROM "genome/genes"
SORT id ASC
```

## Genes deprecados (si los hay)

```dataview
TABLE WITHOUT ID id AS "Gen", version AS "v"
FROM "genome/genes"
WHERE status = "deprecated"
```

> La historia completa de mutaciones (con señal y diff) vive en `genome/events.jsonl`.
