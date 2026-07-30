---
tipo: propuesta-evolve
tarea: F0-09
status: pending
fecha: 2026-07-29
genes_afectados: [gen-identidad-de-pagina]
origen: piloto Fase B, hallazgo H-09
---

# Propuesta EVOLVE F0-09 — `gen-identidad-de-pagina` v2 → v3: el `resultado` del ledger es vocabulario cerrado y se valida

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

Dos herramientas del núcleo discrepan sobre el campo `resultado` de
`ingest-ledger.jsonl`, y la discrepancia **no produce ningún error**: produce una métrica
falsa.

- `lint.py` (`_check_ledger`) valida que existan las 5 claves
  (`ts, op, fuente, hash, resultado`) y **no mira qué valor toma `resultado`**.
- `health.py` (`_cobertura`) solo cuenta una fuente como ingerida si
  `resultado ∈ {creada, actualizada, omitida}`. Ese vocabulario **no está documentado en
  ningún gen** ni validado en ninguna parte.

Reproducido en el piloto con 4 fuentes realmente ingeridas y sus 4 líneas en el ledger:

```
resultado: "ok"      →  cobertura 0/100 — 0/73 fuentes de raw/ ingeridas
resultado: "creada"  →  cobertura 5/100 — 4/73 fuentes de raw/ ingeridas
```

Una cadena de texto, sin tocar nada más.

**Por qué esto es peor que un bug corriente.** Falla en silencio y **en la dirección que
parece normal**. Un 0 % de cobertura en un piloto recién arrancado se lee como "aún no has
empezado a ingerir", no como "tu vocabulario es inválido". Nadie va a depurar un cero que
tiene todo el sentido del mundo. El ledger decía 4, la salud decía 0, y **ninguna
herramienta señaló la contradicción**.

Es la misma patología que el enforcement mecánico existe para cazar —un dato que dejó de
derivar de su fuente declarada— pero alojada en un **indicador de gestión**, que es donde
sale más caro: es el número que uno mira para decidir si avanza.

## Diff propuesto (v2 → v3)

Donde el gen describe el ledger de ingesta, fijar el vocabulario:

```
Cada línea del ledger lleva `ts, op, fuente, hash, resultado`. El campo `resultado`
es VOCABULARIO CERRADO: `creada` (nació una página), `actualizada` (se reforzó una
existente), `omitida` (salto por hash idéntico, regla de idempotencia) o `error`
(la ingesta no completó; la fuente sigue pendiente). Solo los tres primeros cuentan
como fuente procesada para la cobertura de `health`. Un valor fuera del vocabulario
es un hallazgo de LINT (LED-02), no un detalle de estilo: la cobertura se calcula
sobre este campo y un valor libre la falsea en silencio. Claves ADICIONALES sí son
libres y se recomiendan para trazar la procedencia cuando la fuente no es legible
directamente (ver [[gen-ingest]]).
```

## Cambio de infraestructura que lo acompaña

- `lint.py`: `LED-02` pasa a marcar `resultado` fuera del vocabulario.
- `health.py`: leer el vocabulario de un único sitio compartido con lint, no de una tupla
  literal incrustada en la función.
- Tests: una línea con `resultado` inválido produce LED-02; la cobertura cuenta lo que
  debe.

## Evidencia

- Reproducido y medido en `C:\cerebro-piloto`: `piloto/hallazgos.md`, hallazgo H-09, con
  las dos salidas de `health` antes y después de cambiar la cadena.
- Código: `lint.py:256` (valida solo presencia de claves) frente a `health.py:86`
  (vocabulario cerrado incrustado).

## Por qué conviene aplicarla ANTES de seguir con B-02

La cobertura de `health` es el indicador con el que se va a reportar el avance de la
ingesta lote a lote. Escalar de 4 a 73 documentos midiendo con un contador que puede
marcar 0 cuando van 40 haría inútil el seguimiento — y B-03/B-04 heredarían la duda.

## Orden de aplicación

1. Infra primero (`lint.py`, `health.py`, vocabulario en un único sitio, tests).
2. Editar `genome/genes/gen-identidad-de-pagina.md` con el diff; `version: 3`.
3. `python tools/cerebro.py events append --type gene_edited --target gen-identidad-de-pagina --signal "F0-09: resultado del ledger es vocabulario cerrado y validado (H-09 del piloto)" --diff "v2 -> v3 (creada|actualizada|omitida|error; LED-02 lo valida)"`
4. Commit + `python tools/cerebro.py mirror --fix` si `CLAUDE.md` cambia.
