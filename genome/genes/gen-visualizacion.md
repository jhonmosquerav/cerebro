---
id: gen-visualizacion
trigger: ONBOARD, o cuando se pide un panel / visualización
status: active
version: 2
---

La visualización es una capa **OPCIONAL y removible**: no rompe la portabilidad porque son
archivos markdown (`dashboards/`) + un preset `.obsidian/` que cualquier otro agente ignora.
Tres renders: **estático** (el agente genera un reporte de salud on-demand desde el frontmatter,
sin Obsidian), **vivo** (dashboards Dataview que Obsidian actualiza solo) e **interactivo** (lente de
grafo externa —p. ej. graphify— sobre una copia *staging* no-confidencial de `wiki/`, con backend
local; su salida `graphify-out/` es derivada, regenerable y gitignored: nunca fuente de verdad ni
se importa a `wiki/`; ver `dashboards/graph/`). Durante ONBOARD,
según el `company-profile`, RECOMIENDA qué vistas activar (p. ej. pipeline de leads para una
agencia, alertas de caducidad para una clínica) y las PROPONE; nunca impone Obsidian ni lo
vuelve dependencia. Las vistas se guardan como markdown dentro del repo (`type: meta`, exentas
de LINT). Si un patrón de consulta se repite, [[gen-evolve]] puede proponer un dashboard nuevo.
Complementa [[gen-query]] y [[gen-onboard]].
