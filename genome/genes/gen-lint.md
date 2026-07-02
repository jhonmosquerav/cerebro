---
id: gen-lint
trigger: operación LINT (mantenimiento)
status: active
version: 4
---

LINT mantiene sano el grafo. Detecta: (a) páginas huérfanas (sin relaciones entrantes ni
salientes, exceptuando `type: meta`); (b) contradicciones entre páginas; (c) conocimiento
vencido —por `last_reinforced` + `decay_rate` (blando), por `valido_hasta < hoy`, y por
`vigencia` en estado no-vigente (derogada/en-revision/no-vigente, vencimiento por evento)
([[gen-vigencia-temporal]], hallazgo **prioritario** en dominios de seguridad)—; (d) relaciones
con verbos fuera de la unión núcleo ∪ verbos declarados por genes activos ∪
`relation_types` del manifiesto ([[gen-frontmatter-obligatorio]]); (e) campos de frontmatter no reconocidos por ningún gen
(huérfanos de esquema). Para cada hallazgo PROPÓN una acción (conectar, fusionar, marcar
`contradice`, bajar `confidence`, deprecar, o declarar el verbo/campo) y aplícala solo tras mi
aprobación. No modifica el genoma por sí mismo; si detecta un patrón de regla, deriva a
[[gen-evolve]]. Deja constancia en `log.md`.
