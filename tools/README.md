# tools/ — el núcleo mecánico de CEREBRO

> **Principio rector: el LLM nunca decide lo que un script puede decidir;
> el script nunca redacta juicio.** Esto ejecuta la Fase C del backlog
> (validadores diferidos) y la Fase 0 del roadmap de endurecimiento.

Python ≥ 3.10, **stdlib puro, cero dependencias** — un auditor lo corre con
cualquier Python, sin pip, sin red. Todo es determinista: salidas ordenadas,
fechas por parámetro (impresas en el reporte), normalización LF (mismo hash
en Windows y Linux, probado en CI en ambos).

## Uso

```bash
python tools/cerebro.py init --profile memoria [--blueprint legal] [--force]  # deja onboard/company.yaml listo (Fase 4.2)
python tools/cerebro.py verify                      # todos los invariantes de una vez
python tools/cerebro.py lint --as-of 2026-07-12     # 16 detectores; --json estable
python tools/cerebro.py mirror [--fix]              # AGENTS.md ≡ CLAUDE.md (C-02)
python tools/cerebro.py events verify               # esquema + hash-chain + append-only vs git (C-03)
python tools/cerebro.py events append --type … --target … --signal … --diff …
python tools/cerebro.py hash --scope genome|knowledge|all [--detail]
python tools/cerebro.py onboard apply --date 2026-07-12 [--dry-run]
python tools/cerebro.py profile [set <perfil>|enable <cap>|disable <cap>] [--json]  # gen-perfiles
python tools/cerebro.py consolidate scan --as-of …  # decaimiento/promoción/duplicados
python tools/cerebro.py health [--write]            # score 0–100; tablero estático
python tools/cerebro.py xray [--inferred graph.json] [--write]   # deriva declarada↔evidencia
python tools/cerebro.py graph --canvas dashboards/graph/wiki.canvas  # render nativo JSON Canvas (allowlist fail-closed)
```

Todos aceptan `--vault DIR` para operar sobre otro clon (así corren los
tests y los casos de `worked/`). Exit codes: 0 limpio · 1 hallazgos · 2 uso.
`init` es el primer paso de una instalación: copia `onboard/company.example.yaml` (o el
blueprint de `--blueprint <sector>`) a `onboard/company.yaml` fijando `profile:` con la
misma edición textual de `profile set`; idempotente, no pisa un manifiesto distinto sin
`--force`, conserva los placeholders `<...>` del blueprint y no aplica nada (eso es
`onboard apply`). Lógica en `cerebro_core/init_manifest.py`; tests en `tests/test_init.py`.
`consolidate`, `health`, `xray` y `graph` respetan el perfil de instalación
(`genome/perfil.md`, gen-perfiles): capacidad apagada ⇒ aviso y exit 2;
`--ignore-profile` fuerza la corrida.

Pre-commit local (C-05): `git config core.hooksPath .githooks` — bloquea
mutaciones de `raw/`, reescrituras del ledger y espejo roto.

## Qué es mecánico y qué sigue siendo juicio

| Operación | Núcleo mecánico (aquí, 0 LLM) | Juicio (agente + compuerta) |
|---|---|---|
| LINT | huérfanas, enlaces rotos, frontmatter, verbos/campos fuera de esquema, vencidos, identidad, ledger, confidencial anclada | contradicciones semánticas, redactar arreglos |
| ONBOARD | `init` (manifiesto semilla con perfil) + aplicar el manifiesto (perfil de empresa, perfil de instalación, taxonomía, seeds, events, index) | la entrevista que rellena el manifiesto, la pregunta de graph_lens, recomendaciones |
| perfil | efectivo = preset + overrides; `genome/perfil.md`; deriva PRF-01/02; gating de comandos | explicar qué apaga cada perfil; no ejecutar una operación apagada |
| CONSOLIDATE | ventanas de decaimiento, elegibilidad de promoción, candidatos a archivo/duplicado | decidir fusiones, redactar consolidados |
| AUDIT | los reportes `--json` como insumo del maker | ¿importa?, diff, score argumentado |
| XRAY | buckets de deriva + score | interpretar derivas, proponer relaciones |
| salud | las 6 componentes y el score | recomendaciones |
| QUERY | *(pendiente: resolutor de subgrafo)* | navegación fina y síntesis citada |

## El contrato de mantenimiento

`cerebro_core/schema.py` es el **espejo ejecutable del genoma**: cada
constante cita el gen que la origina. Si una mutación de genoma cambia el
esquema (campo, verbo, enum), ese MISMO cambio debe tocar `schema.py` —
los tests de corpus (`tests/`) delatan la deriva si se olvida. La
integración formal de estas herramientas a los genes **se aplicó por compuerta**
(18/18 propuestas en los gates 2026-07-27/29 y 2026-08-07): `docs/propuestas-evolve/`.

## Verdades incómodas que este código no oculta

- El parser YAML es un **subconjunto estricto** (mapas, listas, flow,
  bloques `|`/`>` uniformes, comentarios). YAML exótico = error ruidoso con
  línea. Es un rasgo: el estado de CEREBRO queda definido validable.
- `lint` NO detecta contradicciones semánticas (detector b del gen): leer
  significado es juicio. Decir lo contrario sería vender humo.
- Las líneas históricas de `events.jsonl` (previas a 2026-07-12) no llevan
  `prev`: su integridad la prueba el append-only contra git, no la cadena.
