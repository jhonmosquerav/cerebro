---
id: gen-onboard
trigger: operación ONBOARD (primera vez o cambio de empresa)
status: active
version: 5
---

ONBOARD adapta el cerebro a una empresa de forma **REPRODUCIBLE**. Fuente de verdad: el
manifiesto `onboard/company.yaml` (esquema en `onboard/company.example.yaml`). Tres modos:
(a) aplicar un `company.yaml` existente; (b) copiar un blueprint de `onboard/blueprints/`;
(c) entrevista que **escribe primero** `company.yaml` y luego aplica.

El aplicado es MECÁNICO: tras tener `onboard/company.yaml` completo (modo a,
b, o el que produce la entrevista del modo c), el agente ejecuta
`python tools/cerebro.py onboard apply --date <hoy>` y reporta su salida.
La herramienta valida todo antes de escribir nada (placeholders sin
rellenar, gen en conflicto o lente sin backend ⇒ aborta sin escritura
parcial), renderiza `company-profile.md`, crea la taxonomía, siembra cada
`seed_gene` con su línea `gene_added` en `events.jsonl` (hash-chain) y
actualiza el bloque Estado de `index.md`. Mismo manifiesto + misma fecha →
mismo hash de estado (probado en CI: `tests/test_onboard.py`, `worked/`).
Siguen siendo del agente: la entrevista que escribe el manifiesto, la
pregunta única de `graph_lens.backend` cuando la lente está activa sin
backend (la herramienta aborta a propósito en ese caso), las
recomendaciones de vistas ([[gen-visualizacion]]) y el commit de la corrida.

No ingiere contenido: ONBOARD solo configura.
