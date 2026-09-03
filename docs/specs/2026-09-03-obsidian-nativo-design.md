---
tipo: spec-de-diseno
fecha: 2026-09-03
estado: aprobado-en-conversacion
alcance: capa de visualización opcional (dashboards/, .obsidian/, templates/) + gen-visualizacion v3
---

# CEREBRO habla Obsidian nativo — diseño (enfoque A)

## Contexto y porqué

Revisión completa de la organización `github.com/obsidianmd` (18 repos) y de la ayuda
oficial. De todo eso, lo que cambia el juego para CEREBRO son tres cosas que Obsidian ya
trae **de serie**, sin plugins comunitarios:

- **Bases** (core desde 1.9): vistas tipo base de datos sobre el frontmatter, en archivos
  `.base` (YAML abierto) consultables también desde la CLI (`base:query format=json`).
- **Properties tipadas**: `.obsidian/types.json` fija el tipo de cada propiedad para todo
  el vault (fecha, número, checkbox, lista), lo que da pickers y filtros correctos.
- **CLI oficial** (1.12+): `search`, `orphans`, `unresolved`, `backlinks`, `property:set`.

Brechas detectadas en el template: preset `.obsidian/` en formato legado y sin Bases,
dashboards atados a Dataview (plugin comunitario), sin tipado de propiedades, plugin de
plantillas activo sin plantillas, grafo nativo sin grupos, y una ruta obsoleta en el léeme.

## Principio rector

**Obsidian sigue siendo opcional y removible.** Todo lo que se añade son archivos que
cualquier otro agente ignora. Ninguna operación del genoma depende de Obsidian ni de su
CLI: los validadores de `tools/` siguen siendo la fuente canónica de señales estructurales
(cero dependencias, mismo resultado en cada máquina). La CLI se documenta como
*equivalente para el operador humano*, nunca como dependencia — exige la app abierta.

## Enfoques considerados

- **A. Nativo mínimo (elegido)**: preset moderno, tipado, dashboards en Bases, plantillas,
  grupos de grafo, runbook de la CLI, plantilla de Web Clipper. Cero Python. Un gate.
- **B. A + `graph --canvas`**: emitir un `.canvas` (JSON Canvas 1.0) del grafo estructural
  con allowlist fail-closed. Aplazado a un segundo gate, cuando haya wiki poblada donde
  verlo (misma doctrina que F0-04).
- **C. QUERY/LINT sobre la CLI**: descartado, rompe "sin servidores" y la portabilidad.

## Componentes

| Pieza | Archivo(s) | Compuerta |
|---|---|---|
| Preset moderno | `.obsidian/core-plugins.json` (objeto; activa `bases`, `properties`, `canvas`, `templates`, `bookmarks`) | no (preset) |
| Tipado de propiedades | `.obsidian/types.json` — espejo de `tools/cerebro_core/schema.py` | no (preset) |
| Grafo nativo legible | `.obsidian/graph.json` — grupos por tier, genoma, hub y confidencial | no (preset) |
| Plantillas por `type` | `templates/*.md` + `.obsidian/templates.json` | no (fuera de `wiki/`) |
| Dashboards nativos | `dashboards/*.base` (3) embebidos en los `.md` existentes; Dataview queda como alternativa | no (`type: meta`) |
| Runbook CLI | `ops/runbook-obsidian-cli.md` — operación CEREBRO ↔ comando, con reglas | no |
| Captura web | `onboard/clipper/cerebro-captura-web.json` → deposita en `raw/web/` | no |
| Gen | `gen-visualizacion` v2 → v3 (render vivo = Bases; Dataview opcional; preset tipado; CLI como equivalente) | **sí** — aprobada en sesión 2026-09-03 |
| Espejo y mapa | `CLAUDE.md` ≡ `AGENTS.md`, `index.md`, `README.md` | mirror --fix |

### Decisiones de detalle

- `relations` es un mapa anidado y Obsidian no soporta propiedades anidadas: se muestra
  como objeto no editable y Bases no filtra por él. **No se cambia el esquema** por esto.
- `types.json` declara solo campos del esquema (obligatorios + opcionales de genes +
  frontmatter de genes). `relations` queda sin tipo a propósito.
- Las plantillas viven en `templates/` (raíz): fuera del alcance de LINT de frontmatter
  (solo `wiki/`) y fuera de la resolución de `[[wikilinks]]` (solo `wiki/`, `genome/`,
  `index.md`). Usan `{{date}}` / `{{title}}` del plugin core Templates, entre comillas
  para que el YAML siga siendo válido antes de sustituir.
- Los `.base` replican 1:1 las consultas Dataview existentes y añaden una vista de
  cuarentena (`riesgo_inyeccion`). Los `.md` de `dashboards/` embeben la base
  (`![[x.base#Vista]]`) y conservan el bloque Dataview bajo "alternativa".
- El grupo `confidencial` va **primero** en `graph.json`: en Obsidian gana el primer
  grupo que coincide, y lo confidencial debe verse distinto aunque esté en `semantic/`.
- El Web Clipper escribe en `raw/web/` con metadatos de **captura** (url, fecha): encaja
  con [[gen-confianza-por-fuente]] v3 (la confianza se ancla a la captura) y con
  [[gen-raw-inmutable]] (añadir fuentes es legítimo; modificarlas no).

## Fuera de alcance (backlog con compuerta)

- Mapear `id_alias` al campo nativo `aliases` (resolución de enlaces y menciones sin
  vincular en Obsidian, que alimentarían LNK-03).
- Detector LINT: `publish: true` en página `sensibilidad: confidencial` es error.
- `cerebro graph --canvas` (enfoque B).

## Verificación

- `python tools/cerebro.py verify` en verde antes y después.
- Los `.base` y `.json` se validan por sintaxis (YAML/JSON cargan) y por revisión contra
  la referencia oficial de Bases (`filters` and/or/not, `formulas`, `views[].sort`,
  `groupBy`, `limit`, `file.inFolder`, `file.hasProperty`, `date()`, `today()`).
- Un commit por pieza; la mutación del gen lleva su línea encadenada en
  `genome/events.jsonl` y commit firmado (C-04).
