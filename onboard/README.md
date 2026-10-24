# ONBOARD reproducible

`ONBOARD` adapta el cerebro genérico a una empresa concreta **de forma reproducible**.
La fuente de verdad es un manifiesto declarativo: `onboard/company.yaml`.

> Regla de oro: **mismo `company.yaml` → mismo genoma.** La parte no determinista (una
> entrevista) solo sirve para *generar* el manifiesto; el aplicado es una función pura.

## Tres modos (todos reproducibles)
1. **Manifiesto** — `python tools/cerebro.py init --profile <perfil>` copia
   `company.example.yaml` a `company.yaml` con el perfil fijado; edítalo y aplica `ONBOARD`.
2. **Blueprint** — `python tools/cerebro.py init --profile <perfil> --blueprint <sector>` copia
   la receta de `onboard/blueprints/<sector>.yaml` (sus placeholders `<...>` se conservan tal
   cual: rellénalos) y aplica. Onboardea muchas empresas del mismo vertical igual.
3. **Entrevista** — el agente te pregunta, **escribe primero** `company.yaml` y luego aplica.

`init` no pisa un `company.yaml` existente (salvo `--force`), es idempotente y no aplica nada;
también puedes copiar el archivo a mano, como antes. Los blueprints están **catalogados con
versión y requisito mínimo** (`blueprints/catalog.yaml`, Fase 4.3): `python tools/cerebro.py
blueprints` lista qué hay, qué siembra cada uno y si tu `company.yaml` está al día; `init` y
`onboard apply` rechazan un blueprint que exija un CEREBRO más nuevo que el instalado.

## Qué hace el aplicado (determinista e idempotente)
1. Lee `company.yaml`.
2. Completa `genome/company-profile.md` (`status: configurado`).
3. Fija la sensibilidad por defecto desde `default_sensibilidad` si el manifiesto la
   declara (`gen-confidencialidad`); si `graph_lens.enable` está activo sin `backend`,
   pregunta una vez cuál usar y lo registra en el manifiesto (`gen-graph-lens`).
4. Crea la taxonomía de carpetas de `taxonomy:` en `wiki/semantic/` y `wiki/procedural/`.
5. Siembra cada `seed_genes` en `genome/genes/` pasando por `gen-compuerta-mutacion`,
   registrando una línea por gen en `genome/events.jsonl` + commit.
6. Actualiza `index.md` con la empresa y las anclas iniciales.
7. Si el manifiesto declara `profile:`/`capabilities:`, renderiza `genome/perfil.md` (el
   estado efectivo de las capacidades) y registra `profile_applied` cuando cambia
   (`gen-perfiles`). Sin declaración: `completo`, sin archivo.
8. Re-sincroniza `AGENTS.md`. **No ingiere contenido**: ONBOARD solo configura.

## Elegir cuánto CEREBRO quieres: perfiles y capacidades

| Perfil | Enciende | Para quién |
|---|---|---|
| `minimo` | solo núcleo (ONBOARD, INGEST, QUERY, LINT, compuerta, ledger, confidencialidad) | una wiki gobernada, sin memoria entre sesiones |
| `memoria` | + `memoria` (hooks, CHECKPOINT, working/episodic) + `ciclo_de_vida` (CONSOLIDATE) | "solo memoria": recuerda, decae y promueve |
| `gobernanza` | + `evolucion` (EVOLVE) + `auditoria` (AUDIT, XRAY, health) | un genoma que se audita y propone sus reglas, sin Obsidian |
| `completo` | + `visualizacion` (dashboards, .obsidian) + `grafo` (GRAPH, canvas, lente) | todo (el comportamiento por defecto) |

Cada capacidad se puede encender o apagar aparte con `capabilities:` (p. ej. `memoria` +
`{ auditoria: true }`). Sin tocar YAML:

```bash
python tools/cerebro.py profile set memoria        # o: enable auditoria · disable grafo
python tools/cerebro.py onboard apply --date 2026-10-20
python tools/cerebro.py profile                    # qué rige, y si está aplicado
```

Apagar nunca borra: la operación deja de ejecutarse, sus comandos avisan (exit 2) y los
hooks de memoria son no-op; lo que exista en sus carpetas se respeta.

Reaplicar el mismo manifiesto no duplica nada; reaplicar uno editado genera un diff limpio.

## Capturar fuentes desde el navegador (opcional, Obsidian Web Clipper)

`onboard/clipper/cerebro-captura-web.json` es una plantilla para el
[Web Clipper oficial](https://github.com/obsidianmd/obsidian-clipper): deposita la página
capturada como markdown en `raw/web/` con metadatos de **captura** (`captura_url`,
`captura_fecha`, `publicado`, `autor`), que es justo lo que `gen-confianza-por-fuente`
necesita para anclar la confianza a la captura y no solo al emisor. Importar: extensión →
Settings → Templates → *Import*. Luego, como con cualquier fuente: `INGEST raw/web/<archivo>`.
Añadir a `raw/` es legítimo; modificar o borrar lo capturado, no (`gen-raw-inmutable`).
