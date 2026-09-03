---
title: Dashboards — léeme
type: meta
---

# Panel de CEREBRO (capa opcional)

Estos dashboards son la capa de **visualización opcional**. Son archivos de texto (markdown
y `.base` en YAML): si no usas Obsidian, no estorban ni rompen nada. Para activarlos en vivo:

1. Abre la carpeta del cerebro como Vault en Obsidian (1.9 o superior).
2. No hay nada que instalar: los paneles usan **Bases**, plugin core ya activo en el preset.
3. Abre cualquier dashboard en modo lectura (Ctrl/Cmd + E) o el `.base` directamente.

¿Prefieres Dataview? Cada panel conserva sus consultas Dataview como **alternativa
opcional** (Settings → Community plugins → Dataview). ¿Sin Obsidian? Pídele al agente el
equivalente: *"genera el reporte de salud del conocimiento"* — lee el mismo frontmatter y
lo arma en markdown. Misma información, render estático.

## Índice
- [[salud-del-genoma]] — qué genes hay, su versión y estado. Vista: [[salud-del-genoma.base]].
- [[salud-del-conocimiento]] — confianza, vencimientos, confidenciales, eventos y cuarentena
  de la wiki. Vista: [[salud-del-conocimiento.base]].
- [[salud-mecanica]] — el score determinista 0–100; se regenera con
  `python tools/cerebro.py health --write` (render estático, sin Obsidian ni LLM).
- [[por-sector]] — vistas que `ONBOARD` adapta a tu negocio. Vista: [[por-sector.base]].

> Las consultas de conocimiento apuntan a `wiki/`, que en el template nace **vacía**: es
> normal ver tablas sin filas hasta correr `ONBOARD` + `INGEST`. Para ver un panel con
> datos desde ya, abre [[salud-del-genoma]]: lee `genome/genes/`, que sí viene poblado.

## Qué más trae el preset `.obsidian/` (todo opcional, removible)
- **Propiedades tipadas** (`types.json`): `confidence` es número, `created`/`valido_hasta`
  son fechas, `riesgo_inyeccion` es checkbox. Espejo del esquema de
  [[gen-frontmatter-obligatorio]]; si el esquema muta, el tipado muta en el mismo cambio.
  Límite conocido: `relations` es un mapa anidado y Obsidian lo muestra como objeto no
  editable (no soporta propiedades anidadas). No se cambia el esquema por eso.
- **Grafo nativo con grupos** (`graph.json`): rojo = confidencial, naranja = cuarentena,
  amarillo = hub, verde = semantic, azul = procedural, morado = episodic, gris = archive,
  índigo = genoma. Vista → Graph view.
- **Plantillas por `type`** (`templates/`, ver `templates/00-leeme.md`): para crear
  páginas a mano que pasen LINT.
- **CLI oficial de Obsidian** (1.12+): equivalente opcional para el operador humano —
  `obsidian base:query file=salud-del-conocimiento view="Vencidas" format=json` saca un
  panel a JSON sin plugins. Mapa completo y reglas en `ops/runbook-obsidian-cli.md`. Las
  señales canónicas siguen siendo las de `tools/` (no exigen la app abierta).
- **Skills para agentes** (opcional): [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)
  (MIT) enseña a Claude Code y compatibles a escribir markdown de Obsidian, `.base` y
  `.canvas` correctos. Se instalan en `.claude/skills/` del clon; no se versionan aquí.
- **Lente de grafo interactiva** (externa, opcional): `dashboards/graph/00-leeme.md`.
