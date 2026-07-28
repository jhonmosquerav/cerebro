---
tipo: propuesta-evolve
tarea: F0-01
status: approved
fecha: 2026-07-12
genes_afectados: [gen-lint]
---

# Propuesta EVOLVE F0-01 — `gen-lint` v4 → v5: núcleo mecánico como detector

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

La evaluación `2026-07-01-810f24e` (brecha #3, señalada por 5 de 6 lentes):
*"cero invariantes tienen protección mecánica […] la deriva sería silenciosa
entre auditorías"*. Desde 2026-07-12 existe `python tools/cerebro.py lint`:
16 detectores deterministas con tests y CI que cubren los detectores (a),
(c), (d), (e) del gen — pero el gen aún manda al LLM a detectarlos leyendo.
Eso desperdicia contexto y reintroduce el no-determinismo que ya pagamos por
eliminar. gen-auto-auditoria v4 ya sentó la doctrina: *"la identidad de cada
candidato la fija el detector; el LLM solo juzga '¿importa?' y redacta"*.

## Diff propuesto (v4 → v5)

Añadir al inicio del cuerpo del gen:

```
La detección estructural es MECÁNICA: LINT arranca ejecutando
`python tools/cerebro.py lint --as-of <hoy>` y toma su salida como la lista
canónica de candidatos de los detectores (a) huérfanas, (c) vencidos duro y
blando, (d) verbos fuera de unión, (e) campos fuera de esquema, más
identidad de página, ledger vs raw/, espejo y cuarentena. El agente NO
re-deriva a mano lo que el script ya probó: su trabajo empieza donde el
script termina — (b) contradicciones semánticas entre páginas (leer
significado sigue siendo juicio), priorizar qué importa, y PROPONER el
arreglo de cada hallazgo. Si la herramienta no está disponible (clon sin
python), degrada al procedimiento manual de siempre y lo declara en log.md.
```

Y en la línea final: "Deja constancia en `log.md`" → "Deja constancia en
`log.md` (incluyendo el conteo del reporte mecánico: N errores / M avisos)".

## Evidencia

- `tools/cerebro_core/lint.py` + `tests/test_lint.py` (fixtures 1:1 por código).
- El repo real pasa hoy con 0 errores y 1 aviso legítimo (episódico
  `2026-07-02-f1fc904c` huérfano — LNK-02).

## Orden de aplicación

1. Editar `genome/genes/gen-lint.md` con el diff; `version: 5`.
2. `python tools/cerebro.py events append --type gene_edited --target gen-lint --signal "F0-01: detectores mecánicos como fuente canónica de candidatos" --diff "v4 → v5 (núcleo mecánico tools/cerebro.py lint)"`
3. Commit + `python tools/cerebro.py mirror --fix` si CLAUDE.md cambia.
