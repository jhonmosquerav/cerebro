---
id: gen-visualizacion
trigger: ONBOARD, o cuando se pide un panel / visualización
status: active
version: 1
---

La visualización es una capa **OPCIONAL y removible**: no rompe la portabilidad porque son
archivos markdown (`dashboards/`) + un preset `.obsidian/` que cualquier otro agente ignora.
Dos renders: **estático** (el agente genera un reporte de salud on-demand desde el frontmatter,
sin Obsidian) y **vivo** (dashboards Dataview que Obsidian actualiza solo). Durante ONBOARD,
según el `company-profile`, RECOMIENDA qué vistas activar (p. ej. pipeline de leads para una
agencia, alertas de caducidad para una clínica) y las PROPONE; nunca impone Obsidian ni lo
vuelve dependencia. Las vistas se guardan como markdown dentro del repo (`type: meta`, exentas
de LINT). Si un patrón de consulta se repite, [[gen-evolve]] puede proponer un dashboard nuevo.
Complementa [[gen-query]] y [[gen-onboard]].
