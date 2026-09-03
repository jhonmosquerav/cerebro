# Runbook — CLI oficial de Obsidian como equivalente opcional

Obsidian 1.12+ trae una CLI (`obsidian <comando> clave=valor`). Este runbook la mapea a
las operaciones de CEREBRO **para el operador humano**. No es una dependencia del genoma.

## Reglas (no negociables)

1. **Exige la app abierta.** La CLI es un control remoto de Obsidian en ejecución (si no
   está abierta, la lanza). Por eso **jamás** entra en hooks, pre-commit ni CI: ahí manda
   `python tools/cerebro.py …`, que corre con Python puro en cualquier máquina.
2. **La fuente canónica de señales es `tools/`.** `orphans`, `unresolved` o `backlinks`
   de la CLI cuentan distinto (no eximen `type: meta`, ven `templates/`, `docs/`, `ops/`).
   Si discrepan, manda `lint` / `graph`: son reproducibles y están probados.
3. **Escritura acotada.** `property:set`, `append`, `create`, `move` solo sobre `wiki/`
   y bajo las mismas reglas que cualquier edición (frontmatter válido, `id_pagina` = ruta,
   `last_reinforced` al reforzar). Nunca sobre `genome/` (compuerta, [[gen-compuerta-mutacion]])
   ni sobre `raw/` (inmutable, [[gen-raw-inmutable]]). `delete … permanent` está prohibido.
4. **Confidencialidad.** Lo que la CLI imprime en tu terminal puede quedar en historiales
   y logs. No vuelques páginas `sensibilidad: confidencial` con `read` a canales que se
   persisten ([[gen-confidencialidad]]).
5. **Apunta al vault correcto**: `obsidian vault=<nombre> …` antes del comando cuando
   tengas varios abiertos (el template y tu clon con datos reales son vaults distintos).

## Activar

Settings → General → **Command line interface** → registrar. Reinicia la terminal.
Verifica con `obsidian version` y `obsidian vault`.

## Mapa operación ↔ comando

| Operación CEREBRO | Canónico (`tools/`) | Equivalente CLI (operador humano) |
|---|---|---|
| `QUERY` paso 2, fallback léxico ([[gen-query]]) | grep sobre `wiki/` | `obsidian search:context query="<tema>" path=wiki` |
| `LINT` huérfanas (LNK-02) | `cerebro lint` | `obsidian orphans` (ver regla 2) |
| `LINT` enlaces rotos (LNK-01) | `cerebro lint` | `obsidian unresolved counts` |
| `GRAPH` grado / hubs | `cerebro graph --scope all` | `obsidian backlinks file=<página> counts` |
| Dashboards a JSON/CSV | `cerebro health --write` | `obsidian base:query file=salud-del-conocimiento view="Vencidas" format=json` |
| Refuerzo manual de una página | editar frontmatter | `obsidian property:set file=<página> name=last_reinforced value=<YYYY-MM-DD> type=date` |
| Marcar vigencia | editar frontmatter | `obsidian property:set file=<página> name=vigencia value=en-revision type=text` |
| Crear página con plantilla | copiar de `templates/` | `obsidian create name="<título>" template=concepto path="wiki/semantic/<cat>/<slug>.md" open` |
| Inventario de tags / propiedades | — | `obsidian tags counts` · `obsidian properties counts format=json` |
| Ver esquema real de una página | `cerebro lint` | `obsidian properties file=<página> format=yaml` |
| Recuperar una versión local | git | `obsidian history file=<página>` · `history:restore … version=<n>` (git sigue siendo la verdad) |

Todo comando de lectura acepta `format=json|csv|tsv|md|yaml` y `--copy` (portapapeles).

## Ejemplos útiles

```bash
obsidian base:query file=salud-del-conocimiento view="Confianza más baja" format=csv
```

```bash
obsidian search:context query="precio" path=wiki/semantic format=json
```

```bash
obsidian tags counts format=json
```

## Lo que NO hace la CLI por CEREBRO

- No sustituye a `verify`, `lint`, `graph`, `xray` ni `health`: esos son los invariantes.
- No escribe en el ledger (`events append` es la única vía con hash-chain).
- No aplica mutaciones de genoma: la compuerta es humana y queda en `genome/events.jsonl`.
- Sync/Publish (`obsidian-headless`, `publish:*`) son servicios de pago ajenos al diseño:
  CEREBRO usa git. Si algún día publicas, una página `confidencial` jamás lleva
  `publish: true` (candidato a detector de LINT, en backlog).
