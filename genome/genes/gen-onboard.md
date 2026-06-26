---
id: gen-onboard
trigger: operación ONBOARD (primera vez o cambio de empresa)
status: active
version: 3
---

ONBOARD adapta el cerebro a una empresa de forma **REPRODUCIBLE**. Fuente de verdad: el
manifiesto `onboard/company.yaml` (esquema en `onboard/company.example.yaml`). Tres modos:
(a) aplicar un `company.yaml` existente; (b) copiar un blueprint de `onboard/blueprints/`;
(c) entrevista que **escribe primero** `company.yaml` y luego aplica. El aplicado es
**determinista e idempotente**: lee el manifiesto, completa `genome/company-profile.md`
(`status: configurado`), fija la sensibilidad por defecto desde `default_sensibilidad` si el
manifiesto lo declara (ver [[gen-confidencialidad]]), crea la taxonomía de carpetas, siembra cada `seed_genes` en
`genome/genes/` pasando por [[gen-compuerta-mutacion]] (1 línea por gen en
`genome/events.jsonl` + commit), y actualiza `index.md`. Mismo manifiesto → mismo genoma.
No ingiere contenido: ONBOARD solo configura.
