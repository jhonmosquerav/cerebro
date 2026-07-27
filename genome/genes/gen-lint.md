---
id: gen-lint
trigger: operación LINT (mantenimiento)
status: active
version: 5
---

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
[[gen-evolve]]. Deja constancia en `log.md` (incluyendo el conteo del reporte
mecánico: N errores / M avisos).
