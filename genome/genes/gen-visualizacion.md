---
id: gen-visualizacion
trigger: ONBOARD, o cuando se pide un panel / visualización
status: active
version: 4
---

La visualización es una capa **OPCIONAL y removible**: no rompe la portabilidad porque son
archivos de texto (`dashboards/` en markdown y `.base` YAML, `templates/`) + un preset
`.obsidian/` que cualquier otro agente ignora. Tres renders: **estático** (el agente —o
`cerebro health --write`— genera un reporte de salud on-demand desde el frontmatter, sin
Obsidian), **vivo** (vistas nativas **Bases** de Obsidian en `dashboards/*.base` —plugin
core, nada que instalar; consultables desde fuera con `obsidian base:query … format=json`—,
con los paneles Dataview como alternativa opcional equivalente) e **interactivo**, en dos
sabores: el **nativo** (`graph --canvas` emite JSON Canvas con allowlist fail-closed;
Obsidian lo abre sin plugin ni LLM, [[gen-graph-lens]]) y el **externo** (lente de grafo
—p. ej. graphify— sobre una copia *staging* no-confidencial de `wiki/`, con backend local).
La salida de ambos (`dashboards/graph/*.canvas`, `graphify-out/`) es derivada, regenerable y
gitignored: nunca fuente de verdad ni se importa a `wiki/`; ver `dashboards/graph/`.
El preset `.obsidian/` declara además el **tipado de propiedades** (`types.json`), espejo
del esquema de [[gen-frontmatter-obligatorio]] —si el esquema muta, el tipado muta en el
mismo cambio—, grupos de color del grafo nativo por tier/sensibilidad y las plantillas por
`type` de `templates/` (fuera de `wiki/`: no son conocimiento ni resuelven enlaces). La
**CLI oficial de Obsidian** es un equivalente opcional para el operador humano
(`ops/runbook-obsidian-cli.md`), nunca dependencia: exige la app abierta, y las señales
canónicas siguen siendo las de `tools/` ([[gen-lint]], [[gen-graph-lens]]).
Durante ONBOARD, según el `company-profile`, RECOMIENDA qué vistas activar (p. ej. pipeline
de leads para una agencia, alertas de caducidad para una clínica) y las PROPONE como vistas
nuevas de `por-sector.base`; nunca impone Obsidian ni lo vuelve dependencia. Las vistas se
guardan como texto dentro del repo (`type: meta` en los `.md`, exentas de LINT). Si un patrón
de consulta se repite, [[gen-evolve]] puede proponer un dashboard nuevo.
Complementa [[gen-query]] y [[gen-onboard]].
