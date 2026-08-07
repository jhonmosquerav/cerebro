---
id: gen-lint
trigger: operación LINT (mantenimiento)
status: active
version: 7
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
(huérfanos de esquema); (f) **enlaces sugeridos** — MECÁNICO: `lint` emite LNK-03 (severidad
`info`) por cada página de `wiki/` que menciona en prosa el basename, `title` o `id_alias` de
otra página existente sin enlazarla. Es una PROPUESTA, no un defecto: el agente decide si la
relación es real y, si lo es, la aplica editando la página (cuerpo o `relations`) — el detector
JAMÁS reescribe la página, ni siquiera cuando la mención es inequívoca. Dos invariantes acotan
el detector: nunca propone como destino una página `sensibilidad: confidencial` (nombrarla
expondría su título, metadato reidentificador — [[gen-confidencialidad]]) y nunca toma como
origen una página en cuarentena `riesgo_inyeccion: true` (su texto es dato no confiable y no
debe dirigir la topología del grafo — [[gen-anti-inyeccion]]). Se excluyen del rastreo el
código en bloque y en línea, las URLs, los wikilinks ya puestos y las menciones que son
parte de un nombre de archivo (`termino.ext`). El LNK-03 tiene **memoria de descartes**:
un hallazgo evaluado y rechazado se registra en `lint-descartes.jsonl` (raíz, append-only,
`{ts, pagina, termino, motivo}`) y no se vuelve a sugerir; el reporte muestra un contador
único de omitidos (línea malformada → aviso DSC-01). Aplicar o descartar un LNK-03 es
trabajo de la operación LINT — incluida la cascada que provoque una página nueva creada
por INGEST o CONSOLIDATE. Para cada hallazgo PROPÓN una acción (conectar, fusionar, marcar
`contradice`, bajar `confidence`, deprecar, o declarar el verbo/campo) y aplícala solo tras mi
aprobación. No modifica el genoma por sí mismo; si detecta un patrón de regla, deriva a
[[gen-evolve]]. Deja constancia en `log.md` (incluyendo el conteo del reporte
mecánico: N errores / M avisos).
