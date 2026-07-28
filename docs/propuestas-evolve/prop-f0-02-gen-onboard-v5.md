---
tipo: propuesta-evolve
tarea: F0-02
status: approved
fecha: 2026-07-12
genes_afectados: [gen-onboard]
---

# Propuesta EVOLVE F0-02 — `gen-onboard` v4 → v5: aplicado 100% mecánico

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

gen-onboard v4 promete "determinista e idempotente" pero el aplicado lo
ejecuta un LLM siguiendo prosa: la garantía era de protocolo, no de bytes.
Desde 2026-07-12 el aplicado ES un programa (`onboard apply`) con la prueba
en CI: mismo manifiesto + misma fecha ⇒ mismo hash; re-aplicar ⇒ no-op; los
casos `worked/` lo verifican byte a byte. La entrevista —el juicio— queda
donde siempre estuvo: en el agente.

## Diff propuesto (v4 → v5)

Reescribir la segunda mitad del gen:

```
El aplicado es MECÁNICO: tras tener onboard/company.yaml completo (modo a,
b, o el que produce la entrevista del modo c), el agente ejecuta
`python tools/cerebro.py onboard apply --date <hoy>` y reporta su salida.
La herramienta valida todo antes de escribir nada (placeholders sin
rellenar, gen en conflicto o lente sin backend ⇒ aborta sin escritura
parcial), renderiza company-profile.md, crea la taxonomía, siembra cada
seed_gene con su línea gene_added en events.jsonl (hash-chain) y actualiza
el bloque Estado de index.md. Mismo manifiesto + misma fecha → mismo hash
de estado (probado en CI: tests/test_onboard.py, worked/).
Siguen siendo del agente: la entrevista que escribe el manifiesto, la
pregunta única de graph_lens.backend cuando la lente está activa sin
backend (la herramienta aborta a propósito en ese caso), las
recomendaciones de vistas ([[gen-visualizacion]]) y el commit de la corrida.
```

## Evidencia

- `tools/cerebro_core/onboard.py` + `tests/test_onboard.py` (reproducibilidad,
  idempotencia, rechazo sin escritura parcial).
- `worked/agencia-demo` y `worked/legal-demo`: regeneración byte a byte en CI.

## Orden de aplicación

1. Editar `genome/genes/gen-onboard.md`; `version: 5`.
2. `events append --type gene_edited --target gen-onboard --signal "F0-02: aplicado mecánico probado en CI" --diff "v4 → v5 (onboard apply)"`
3. Commit + re-sync de espejo si aplica.
