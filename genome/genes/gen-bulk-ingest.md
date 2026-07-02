---
id: gen-bulk-ingest
trigger: operación BULK INGEST
status: active
version: 2
---

BULK INGEST procesa todas las fuentes pendientes de `raw/` aplicando [[gen-ingest]] a cada
una, **una por una** (no en lote ciego), para preservar la calidad de clasificación y
enlazado. "Pendiente" lo decide el ledger de ingesta ([[gen-identidad-de-pagina]]): se salta
toda fuente cuya última línea tenga su mismo hash (`git hash-object`) y resultado terminal
(`creada | actualizada | omitida`) — sin añadir líneas nuevas al saltar —, se reintentan las
`detenida`, y una ruta ya registrada cuyo hash cambió detiene esa fuente con alerta
([[gen-raw-inmutable]] violado). Una corrida interrumpida se reanuda segura: lo no registrado
se procesa y la clave de página evita duplicados. Al final, actualiza `index.md` y deja un
resumen en `log.md` con totales (procesadas / omitidas / reintentadas / detenidas) y
cualquier fuente que requirió decisión humana.
