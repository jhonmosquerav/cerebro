---
run_id: 2026-07-02-51690cb
fecha: 2026-07-02
rol: auditor
gen_version: gen-auto-auditoria v3
tipo: auditor
---

# 20 — Auditor independiente: veredictos

Pasada fresca. Insumos exclusivos: `00-snapshot.md` + [[gen-auto-auditoria]] v3 +
`10-maker.md` (sin memoria de sesión; subagente limpio como barrera). Toda la evidencia
re-verificada contra HEAD `51690cb`.

## Veredictos

### C1 — Genes base exigen verbos que el esquema de `relations` rechaza → CONFIRMED
- verificación: abrí gen-frontmatter-obligatorio (núcleo `{usa, depende_de, contradice, reemplaza}`, líneas 17-18), gen-lint (chequeo (d) contra "núcleo ∪ `relation_types`", líneas 12-14), y confirmé que gen-sintesis-de-volumen:10 prescribe `agrega`, gen-confianza-por-fuente:11 `corrobora`, gen-entidad-con-estado:12 `sucede_a`/`proviene_de`, gen-consolidate:12-13 y gen-auto-auditoria:25-26 la exención `deriva_de`/`supersede`/`agregado_en`. Grep sobre `onboard/`: solo ecommerce.yaml:48 declara `agrega`; ningún manifiesto declara `corrobora`, `sucede_a`, `deriva_de`, `supersede` ni `agregado_en` (`proviene_de` solo en example y agencia). Intenté refutar por la vía "los genes declaran esquema como gen-jerarquizacion declara `type: hub`": no aplica — el chequeo (e) de campos admite "reconocidos por algún gen", pero el chequeo (d) de **verbos** solo admite núcleo ∪ manifiesto, sin cláusula de gen. El defecto se re-deriva mecánicamente.
- clase adjudicada: **contradicción entre genes activos** · severidad 5 · alcance 7 (gen-frontmatter-obligatorio, gen-lint, gen-sintesis-de-volumen, gen-confianza-por-fuente, gen-entidad-con-estado, gen-consolidate, gen-auto-auditoria — los 7 verificados en conflicto real) · **impacto 57**
- adjudicación entre las dos clases propuestas: la sev-5 REALMENTE aplica — no hay aún página con verbo inválido (eso sería la clase sev-2, que califica páginas), el defecto vive en el canon: un gen ordena crear la relación (`agrega` es mandato de gen-sintesis-de-volumen) y otro ordena marcarla inválida. Órdenes incompatibles entre genes `active` = fila 1 de la tabla. Regla del gen ("la de mayor severidad que le aplique") → sev 5.
- objeción al diff: la variante E3 mete `supersede` al núcleo junto a `reemplaza`, consagrando la duplicación semántica que el propio candidato señala; y omite `proviene_de` (prescrito por gen-entidad-con-estado y NO declarado en salud/produccion/ecommerce/legal) — fix incompleto. Resolver en compuerta (la variante E1 lo cubre mejor).

### C2 — Cuarentena `riesgo_inyeccion` ausente de promoción/fusión de CONSOLIDATE → CONFIRMED
- verificación: gen-anti-inyeccion:48-49 dice literalmente "CONSOLIDATE **no** la promueve de tier ni la fusiona"; gen-ciclo-de-vida:40-45 define la promoción como lista cerrada "(CONSOLIDATE la aplica directo…) cuando se cumplen TODAS" que SÍ incorpora `sensibilidad ≠ confidencial` y omite la cuarentena; gen-consolidate:9-10 delega en "TODOS los criterios verificables de promoción de ese gen" y su regla de fusión (12-15, aplicada directo por la línea 24 "cambios de contenido… se aplican directo") no excluye cuarentena. Intenté refutar por composición ("un gen añade restricción, no contradice"): falla porque la lista es condición suficiente de acción directa — página en cuarentena que cumple TODAS recibe "promuévela directo" y "no la promuevas" a la vez, y el que la lista incorpore el bloqueo de confidencialidad muestra que pretende ser el set completo de bloqueos.
- clase adjudicada: contradicción entre genes activos · severidad 5 · alcance 3 (gen-anti-inyeccion, gen-ciclo-de-vida, gen-consolidate) · **impacto 53**

### C3 — gen-checkpoint ancla working/episodic; gen-jerarquizacion-indice lo prohíbe sin zona gris → CONFIRMED
- verificación: gen-jerarquizacion-indice:18-19 ("lo de `working/` y `episodic/` no se ancla") y :22 ("Sin zona gris… falla uno → no se ancla"), con anclado "si y solo si"; sus consumidores (líneas 11-12) son INGEST/CONSOLIDATE/QUERY — CHECKPOINT no figura. gen-checkpoint:64-66 (paso 3) ordena "refresca en `index.md` las anclas de los tiers `working/` y `episodic/`", y su criterio de hecho (c) lo exige. index.md:30-31 confirma el régimen determinista. Intenté refutar leyendo el paso 3 como "línea meta del tier, no ancla de página": no se sostiene — el propio gen las llama "anclas" y apuntan a páginas concretas de working/episodic; ningún texto del canon declara la excepción.
- clase adjudicada: contradicción entre genes activos · severidad 5 · alcance 2 (gen-checkpoint, gen-jerarquizacion-indice) · **impacto 52**

### C4 — `id_pagina` inmutable y atada a la ruta vs promoción/archivo que mueven el archivo → CONFIRMED
- verificación: gen-identidad-de-pagina:14-16 ("equivalente por construcción a la ruta… se persiste… y no cambia") y :40-41 ("LINT marca toda página cuya `id_pagina` no coincida con su ruta"); gen-ciclo-de-vida:46-47 ("Al promover: mover el archivo…") y :52-54 (archivo a `wiki/archive/` con "frontmatter intacto"). El único texto de transición de clave es para fusión (`id_alias` en fusiones de CONSOLIDATE), no para promoción/archivo. El caso archivo es contradicción estricta: "frontmatter intacto" + ruta nueva ⇒ estado que LINT debe marcar, por construcción.
- clase adjudicada: contradicción entre genes activos · severidad 5 · alcance 2 (gen-identidad-de-pagina, gen-ciclo-de-vida) · **impacto 52**

### C5 — gen-checkpoint declara equivalencia de postcondiciones que el hook Stop no cumple → CONFIRMED
- verificación: gen-checkpoint:10-12 ("implementaciones intercambiables que **deben cumplir estas mismas postcondiciones**… `Stop` ≈ pasos 2–4 + derivación a EVOLVE") y :60-63 (paso 2 exige `type: sesion`, `clase: evento`, `fecha_evento`, `decay_rate: high`); stop.sh:46 instruye un frontmatter sin esos campos y sin línea de `log.md`; hooks README:59-60 niega explícitamente la derivación a EVOLVE. El "≈" no salva: la frase "deben cumplir estas mismas postcondiciones" es el invariante, y el README lo contradice de frente en el punto EVOLVE.
- clase adjudicada: violación de invariante impuesta por un gen · severidad 4 · alcance 3 (gen-checkpoint + stop.sh + hooks README) · **impacto 43**
- objeción al diff: ninguna sustantiva; solo que ambos lados (gen por compuerta y stop.sh/README por gate directo) deben aterrizar juntos o la brecha se reabre en otro sentido — el maker ya los rutea juntos.

### C6 — Staging de GRAPH ignora la cuarentena; gen-graph-lens aún frasea denylist → CONFIRMED
- verificación: gen-anti-inyeccion:3 incluye GRAPH en el trigger y :48-49 solo operacionaliza la cuarentena para QUERY/CONSOLIDATE; el runbook (dashboards/graph/00-leeme.md:52-53 bash y :100-101 PowerShell) filtra ÚNICAMENTE por `sensibilidad`, y el checklist (:159-166) no verifica `riesgo_inyeccion` — mecánicamente verificable: una página `interno` con `riesgo_inyeccion: true` y payload transcrito pasa el ALLOW y llega al backend (`claude` incluido). gen-graph-lens:8-10 sigue fraseando "excluye toda página confidencial" (denylist) mientras la allowlist fail-closed vive solo en el runbook (nota de cambio 2026-07-02, :168-178); el episódico :59-60 reconoce el pendiente A-07 vigente en HEAD.
- clase adjudicada: violación de invariante impuesta por un gen · severidad 4 · alcance 3 (gen-graph-lens, runbook del staging, gen-anti-inyeccion) · **impacto 43**

### C7 — Formato obligatorio del log de fallback léxico expone el nombre de páginas confidenciales → CONFIRMED
- verificación: gen-query:21-22 manda el formato literal `QUERY fallback-lexico: <tema> → [[página]]` como "señal para gen-lint de que a esas páginas les faltan relaciones o ancla"; gen-confidencialidad:13-14 prohíbe exponer "nombre de archivo… el seudónimo cubre también el enlace o mención"; gen-jerarquizacion-indice:16-17 prohíbe anclar confidenciales. Intenté refutar por dos vías del canon: (a) gen-query:19 "respeta TODAS las reglas de abajo (confidencialidad incluida)" — insuficiente: es un caveat genérico contra un formato literal mandatorio, sin precedencia declarada; (b) la regla de nombrado de gen-confidencialidad — insuficiente: cubre solo "el nombre de la **persona**" (PII), no clientes jurídicos, deals o casos cuyo slug reidentifica igual. Además la señal de "falta ancla" para una confidencial es espuria bajo cualquier lectura — ese prong nadie lo resuelve.
- clase adjudicada: violación de invariante impuesta por un gen · severidad 4 · alcance 2 (gen-query, gen-confidencialidad) · **impacto 42**

### C8 — Lista de advertencias de QUERY omite la cuarentena → ADJUSTED
- verificación: gen-anti-inyeccion:48-49 y gen-query:30-31 existen tal cual. Pero el defecto NO se re-deriva como violación/contradicción: la enumeración de gen-query no es excluyente ni autoriza acción contraria — un agente que obedece ambos genes advierte las cuatro cosas sin incompatibilidad (a diferencia de C2, donde la lista cerrada autoriza promoción directa contra una prohibición). Lo que sí queda: la lista "Advierte siempre" es el set canónico de advertencias de QUERY y gen-anti-inyeccion la referencia por analogía ("como advierte lo vencido") — la cuarentena carece de cobertura ahí.
- clase adjudicada: **vacío (categoría sin cobertura)** · severidad 2 · alcance 1 (la enumeración de advertencias de gen-query) · **impacto 21**
- qué corregí: clase sev 4 → sev 2 (no hay órdenes incompatibles ni invariante violado; ambos genes componen sin conflicto), alcance 2 → 1 por definición de vacío; impacto 42 → 21. El diff propuesto sigue siendo el fix correcto.

### C9 — Categorías de `entities` sin carpeta en `taxonomy` → ADJUSTED
- verificación: contrasté los 6 manifiestos. example: faltan `productos` y `herramientas`; agencia: falta `productos`; legal: faltan `juzgados`, `abogados`; salud, produccion y ecommerce cubiertos (línea a línea). onboard/README.md:18 confirma que ONBOARD solo crea carpetas desde `taxonomy:`. Defecto real: el comentario-contrato de los propios manifiestos queda roto.
- clase adjudicada: vacío (categoría sin cobertura) · severidad 2 · alcance 1 · **impacto 21**
- qué corregí: alcance 5 → 1. La rúbrica es explícita y determinista: "vacío / verbo-o-campo fuera de esquema: **1** (la página/categoría/campo afectado)" — no admite sumar las 5 categorías dentro de un solo candidato. Impacto 25 → 21.
- objeción al diff: ninguna — los tres parches son correctos y no crean contradicción.

### C10 — README.md sin `CHECKPOINT` ni `archive/` → ADJUSTED
- verificación: README.md:109-119 — la tabla salta de `QUERY <X>` (114) a `LINT` (115); README.md:79-83 — árbol con 4 tiers, sin `archive/`. Contraste con CLAUDE.md:28 y :65; `wiki/archive/.gitkeep` trackeado en HEAD (git ls-files verificado). Defecto real.
- clase adjudicada: vacío (categoría sin cobertura) · severidad 2 · alcance 1 (README.md, la página afectada) · **impacto 21**
- qué corregí: alcance 2 → 1 por la misma definición determinista de vacío (los dos huecos viven en el mismo objeto y ya fueron fusionados en un candidato). Impacto 22 → 21.

### C11 — Fila LINT de CLAUDE.md invisibiliza el vencido duro y (d)/(e) → CONFIRMED
- verificación: CLAUDE.md:29 dice solo "páginas vencidas por `decay_rate`"; gen-lint:9-15 detecta además `valido_hasta < hoy`, `vigencia` no-vigente (prioritario en dominios de seguridad), verbos fuera de la unión (d) y campos huérfanos (e). La divergencia resumen↔canon existe tal como se afirma.
- clase adjudicada: vacío (categoría sin cobertura) · severidad 2 · alcance 1 · **impacto 21**

### C12 — `refuerzo_delta` no cubre tipos custom (`doctrina` en legal) → CONFIRMED
- verificación: gen-ciclo-de-vida:22 define deltas solo para `{oficial, interna, blanda}`; legal.yaml:44 declara `doctrina: 0.6` y el blueprint no trae bloque `ciclo_de_vida` (verificado en el archivo completo). Una fuente `doctrina` que confirma no tiene delta definido en ninguna parte del canon.
- clase adjudicada: vacío (campo sin cobertura) · severidad 2 · alcance 1 · **impacto 21**
- objeción al diff: ninguna — "trust inmediatamente inferior" resuelve determinista (doctrina 0.6 → blanda +0.03) sin contradicción nueva.

### C13 — onboard/README.md enumera un "aplicado" incompleto vs gen-onboard v4 → CONFIRMED
- verificación: onboard/README.md:15-22 lista 6 pasos sin `default_sensibilidad` ni la pregunta única de `graph_lens.backend`; gen-onboard:13-15 exige ambos. En un doc que promete "el aplicado es una función pura", el procedimiento de referencia incompleto es el defecto afirmado.
- clase adjudicada: vacío (categoría sin cobertura) · severidad 2 · alcance 1 · **impacto 21**

### C14 — README de hooks sobredeclara las barreras de permissions → CONFIRMED
- verificación: settings.json:4-11 — deny/ask cubren exclusivamente `Write(...)`/`Edit(...)`; hooks README:88-90 afirma "hecho mecánico" y "toda escritura al genoma pide confirmación humana". Cierto que una escritura vía Bash/PowerShell no pasa por esas reglas: el claim sobredeclara y el hueco no está documentado.
- clase adjudicada: vacío (categoría sin cobertura) · severidad 2 · alcance 1 · **impacto 21**
- objeción al diff: ninguna — el texto "límite honesto" es exactamente el estilo del resto del README.

### C15 — Referencia de versión muerta "(gen v4)" en pre-compact.sh y su README → CONFIRMED
- verificación: pre-compact.sh:120 y hooks README:28 citan "(gen v4)" sin nombrar el gen; gen-frontmatter-obligatorio:5 está en `version: 5`. Pin de versión obsoleto tal como se afirma.
- clase adjudicada: vacío (link roto) · severidad 2 · alcance 1 · **impacto 21**

### C16 — El retiro de ancla al archivar solo contempla `index.md`, no los hubs → CONFIRMED
- verificación: gen-ciclo-de-vida:53-54 ("el ancla en `index.md` se retira"); gen-jerarquizacion-indice:27-28 ("Cada página vive en exactamente UN punto de la jerarquía"). Archivar una página anclada en hub deja, siguiendo la letra, un ancla colgante hacia una página que "no se cita en QUERY". Busqué texto que lo resuelva (regla de mantenimiento de hubs en gen-consolidate y gen-jerarquizacion): no existe.
- clase adjudicada: vacío (categoría sin cobertura) · severidad 2 · alcance 1 · **impacto 21**

## Resumen
- **CONFIRMED: 13 · ADJUSTED: 3 (C8, C9, C10) · REFUTED: 0**
- Nota de forma al maker: el archivo contiene **16 entradas** (C1..C16, sin huecos) y su línea "Total: 14 candidatos (16 brutos − 2 fusiones)" no cuadra consigo misma — los brutos referenciados son 18 (E1-01..07, E3-01..06, E4-01..05) y 18 − 2 fusiones = 16 candidatos, que es lo que hay. Error de contabilidad, no afecta ningún candidato.
- Ranking final (desempates del gen aplicados explícitamente: (1) impacto; (2) empates 52/52 y 43/43 son de la misma fila de clase, así que decide (3) ruta alfabética del objeto primario — `gen-checkpoint` < `gen-ciclo-de-vida`/`gen-identidad-de-pagina` y `gen-checkpoint` < `gen-graph-lens`; en el bloque de 21 todos son fila "vacío", orden ASCII de ruta `.claude/` < `CLAUDE.md` < `README.md` < `genome/` < `onboard/`; el doble empate C16/C12 sobre `gen-ciclo-de-vida.md` se resuelve por la segunda ruta implicada: `genome/genes/gen-jerarquizacion-indice.md` < `onboard/blueprints/legal.yaml`):

1. C1 (57) · 2. C2 (53) · 3. C3 (52) · 4. C4 (52) · 5. C5 (43) · 6. C6 (43) · 7. C7 (42) · 8. C14 (21) · 9. C15 (21) · 10. C11 (21) · 11. C10 (21) · 12. C16 (21) · 13. C12 (21) · 14. C8 (21) · 15. C13 (21) · 16. C9 (21)

Top-3 para `30-proposals` según la regla `N = min(3, confirmadas)`: **C1, C2, C3**.
