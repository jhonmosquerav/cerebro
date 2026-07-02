---
tipo: propuesta-evolve
tarea: A-06
eval_id: 2026-07-01-810f24e
status: pending
fecha: 2026-07-02
genes_afectados: [gen-jerarquizacion-indice, gen-ingest, gen-query, gen-consolidate, cap-ingesta-de-fuente]
---

# Propuesta EVOLVE A-06 — Jerarquización del índice + fallback léxico de QUERY

Propuesta bajo [[gen-compuerta-mutacion]]: **nada de lo que sigue está aplicado**. Este
archivo contiene el diseño completo, los diffs exactos y las líneas de evento listas para
que, tras el OK del operador, la aplicación sea mecánica (secciones 1–8 de "Cambios
propuestos" + eventos + commit + re-sync `AGENTS.md`).

## Motivación

Ataca la debilidad **sev-4 de arquitectura** de la evaluación 2026-07-01-810f24e:
*"Sin política de jerarquización del índice: la escalabilidad estructural es fe en la
curación"*, y su recomendación P2 (esfuerzo bajo). Evidencia:

- `audit/evaluations/2026-07-01-810f24e/10-panel.md` — debilidad sev-4 (sección
  Arquitectura → Debilidades): `index.md` es el único punto de entrada y su única regla de
  crecimiento es "Mantener corto"; el anclado de INGEST es **"si aplica"** sin criterio;
  ningún gen define cuándo partir el índice ni un fallback léxico sancionado para QUERY
  (el principio 3 de `CLAUDE.md` lo desincentiva). Puntuación de escalabilidad estructural:
  **2.5/5**. Recomendación P2: umbral de N anclas + hubs por categoría de taxonomía +
  sanción del grep léxico como último recurso.
- `audit/evaluations/2026-07-01-810f24e/30-valoracion.md` — brecha dominante #5 ("Escala
  sin política: […] índice único sin regla de jerarquización; QUERY sin fallback
  sancionado") y riesgo mayor "Degradación silenciosa de la recuperación al crecer el
  corpus" (probabilidad alta / impacto alto): QUERY hoy **no distingue "no existe" de
  "existe y no lo encontré"**.
- `audit/evaluations/2026-07-01-810f24e/60-backlog.md` — tarea A-06 `[genoma·gate]`.
- Defecto en el repo: `genome/genes/gen-ingest.md` ("registra ancla en `index.md` (si
  aplica)"), `genome/genes/gen-query.md` (solo navegación, sin paso 2), `index.md` líneas
  9-10 ("Mantener corto: solo páginas-ancla" sin regla de partición), `CLAUDE.md` principio
  3 ("navega SIEMPRE […] por relaciones; no leas todo").

Beneficio lateral (lente KM del panel): en verticales con `default_sensibilidad:
confidencial` (legal/salud) la mayoría de páginas nace **sin ancla** — el fallback léxico
les da una vía de alcance sancionada sin romper [[gen-confidencialidad]] (se hallan, se
citan solo de forma indirecta).

La oportunidad que la evaluación ya señaló: *"la taxonomía del manifiesto ya contiene la
estructura para páginas-hub: jerarquizar el índice es extensión natural, no rediseño"*
(`10-panel.md`, Oportunidades). Esta propuesta usa exactamente esa estructura.

## Diseño en una vista

| Pieza | Qué fija | Dónde queda |
|---|---|---|
| Anclado determinista | 3 criterios (sensibilidad, tier, clase) — muere el "si aplica" | gen **nuevo** + gen-ingest v2 + cápsula v3 |
| Umbral de partición | sección > `hub_umbral` (default **7**, manifiesto) → `hub-<área>.md` | gen nuevo + gen-consolidate v3 (parte CONSOLIDATE) |
| Idempotencia | identidad del hub = su ruta; re-anclar y re-partir son no-op | gen nuevo |
| Fallback léxico de QUERY | paso 2 explícito tras agotar navegación, con transparencia y señal a LINT | gen-query v3 + principio 3 de CLAUDE.md |

**N = 7, razonado:** (a) cognitivo: más de ~7 ítems por sección ya no se escanean de un
vistazo (7±2), y el índice existe para escanearse, no para leerse; (b) presupuesto de
contexto: con secciones ≤7 anclas y áreas partidas a 1 línea, `index.md` se sostiene en ~1
pantalla — cuantifica el "mantener corto" que hoy es prosa; (c) alcanzabilidad: 1 nivel de
hubs cubre cientos de páginas en 2 saltos (index → hub → página) y la regla recursiva
(sub-hubs) cubre miles en 3 — exactamente la ventana "2-3 saltos" que la evaluación pedía
sostener; (d) es configurable por empresa (`hub_umbral`), mismo patrón que
`sintesis_umbral` (default 3) — el default aplica si el manifiesto calla, así el
comportamiento es determinista también para quien no configura.

**Quién parte: CONSOLIDATE (no LINT), justificado:** CONSOLIDATE ya es el dueño de la
reestructuración de la memoria — promueve entre tiers, fusiona duplicados y **ya crea
páginas agregadoras por umbral** ([[gen-sintesis-de-volumen]]: ≥N eventos → página de
síntesis); partir una sección en hub es la misma forma de operación (N ítems → página que
los agrega) y exige mirada de conjunto, que es la suya. LINT es diagnóstico: detecta y
PROPONE acción por hallazgo, no reestructura; darle escritura estructural le cambiaría el
carácter. LINT no necesita bump: la señal de secciones sobre umbral la deja INGEST en
`log.md` (ver gen nuevo), y la declaración de fallback léxico de QUERY le llega también
por `log.md` como insumo de su chequeo existente de relaciones faltantes.

## Cambios propuestos

### 1. Gen NUEVO — `genome/genes/gen-jerarquizacion-indice.md` (texto completo, listo para copiar)

```markdown
---
id: gen-jerarquizacion-indice
trigger: anclar una página nueva / una sección de index.md supera el umbral de anclas
status: active
version: 1
---

El índice crece con política, no con fe en la curación. `index.md` se mantiene corto
(~1 pantalla: secciones de ≤`hub_umbral` anclas, áreas partidas a 1 línea) porque el
anclado es **determinista** y toda sección que supere el umbral se parte en **página-hub**.
Consumidores: INGEST ancla ([[gen-ingest]], cápsula [[ingesta-de-fuente]]), CONSOLIDATE
parte ([[gen-consolidate]]), QUERY navega index → hub → página ([[gen-query]]).

## Anclado determinista (sustituye el "si aplica" de INGEST)
Una página **SE ancla** si y solo si cumple TODO:
1. `sensibilidad != confidencial` ([[gen-confidencialidad]]: lo confidencial jamás se
   ancla, ni en `index.md` ni en un hub);
2. tier `semantic/` o `procedural/` (lo de `working/` y `episodic/` no se ancla: llega al
   índice solo cuando CONSOLIDATE lo promueve);
3. `clase != evento` ([[gen-clase-temporal]]: los eventos se alcanzan por su síntesis
   ([[gen-sintesis-de-volumen]]) o por su entidad, no anclados uno a uno).
Sin zona gris: cumple los tres → se ancla SIEMPRE; falla uno → no se ancla.
**Dónde:** en la sección de su **área** dentro de `index.md`; si el área ya tiene hub, en
`hub-<área>.md` (esa área ya no crece en el index). Área = la categoría de la taxonomía
del manifiesto a la que pertenece la página (= su subcarpeta bajo el tier, slug exacto de
la carpeta); una página en la raíz del tier ancla en la línea general del tier.
**Idempotente:** verifica antes de añadir — re-anclar una página ya anclada es no-op. Cada
página vive en exactamente UN punto de la jerarquía (index o su hub, nunca ambos).

## Umbral y partición en hubs (parte CONSOLIDATE, nunca INGEST)
Cuando una sección/área acumula más de **`hub_umbral`** anclas (configurable en
`onboard/company.yaml`; default **7** — más de ~7 ítems ya no se escanean de un vistazo),
CONSOLIDATE la parte:
1. crea `wiki/<tier>/hub-<área>.md` con TODAS las anclas del área (agrupadas por
   subcarpeta o `type` cuando son muchas);
2. sustituye la sección del área en `index.md` por una sola línea:
   `**<área>** → [[hub-<área>]]`;
3. deja una línea en `log.md`. Partir es cambio de CONTENIDO, no de genoma: no pasa por
   la compuerta.
INGEST nunca parte: si al anclar ve la sección sobre el umbral, ancla normal y deja en
`log.md` la señal `seccion <área> sobre hub_umbral` para el próximo CONSOLIDATE.
**Idempotencia de partición:** la identidad del hub es su ruta — misma área → mismo
`hub-<área>.md`; si ya existe, se ACTUALIZA (merge de anclas sin duplicar líneas), jamás
nace un `hub-<área>-2`. Re-partir un área ya partida es no-op. Si una sección interna de
un hub supera a su vez el umbral, aplica la misma regla de forma recursiva
(`hub-<área>-<subclave>.md`): la jerarquía index → hub → sub-hub → página mantiene todo
lo anclado alcanzable en ≤3 saltos.

## Página-hub (`type: hub`)
`type: hub` queda definido por este gen (LINT lo reconoce como esquema, chequeo (e)). El
hub es estructura de navegación derivada del índice, no conocimiento con fuente:
frontmatter completo de [[gen-frontmatter-obligatorio]] con `confidence: 1.0`,
`decay_rate: low`, `sources: []`, `relations: {}`; su cuerpo son las anclas `[[...]]` del
área. Nunca queda huérfano (`index.md` lo enlaza; él enlaza sus anclas) y NUNCA lista
páginas `confidencial`. Plantilla:

    ---
    title: Hub — <área>
    type: hub
    tier: <tier del área>
    tags: [hub, <área>]
    confidence: 1.0
    created: <hoy>
    last_reinforced: <hoy>
    decay_rate: low
    sources: []
    relations: {}
    ---
```

### 2. `genome/genes/gen-ingest.md` — v1 → v2 (diff por secciones)

Frontmatter: `version: 1` → `version: 2`.

**Antes** (cuerpo, único cambio en la frase del ancla):

> enlaza con relaciones tipadas y `[[wiki-links]]`, y registra ancla en `index.md` (si aplica)
> + línea en `log.md`.

**Después**:

> enlaza con relaciones tipadas y `[[wiki-links]]`, y registra ancla **según los criterios
> deterministas de [[gen-jerarquizacion-indice]]** (en `index.md`, o en el `hub-<área>` si el
> área ya se partió; si los criterios dicen que no, no se ancla) + línea en `log.md`.

El resto del gen (lectura desde `raw/`, idempotencia, no inventar) queda intacto.

### 3. `genome/genes/gen-query.md` — v2 → v3 (cuerpo completo antes → después)

Frontmatter: `version: 2` → `version: 3`.

**Antes** (cuerpo íntegro v2):

> QUERY responde navegando el grafo, no leyendo todo. Empieza en `index.md`, sigue las
> relaciones `[[...]]` relevantes y abre solo las páginas necesarias (presupuesto de contexto).
> Cita las páginas-fuente consultadas y su `confidence`, **excepto las `sensibilidad: confidencial`**
> ([[gen-confidencialidad]]): de esas no revela contenido sensible ni las cita textualmente —
> responde con referencia indirecta o ID seudonimizado. Advierte **siempre** lo vencido por
> `valido_hasta` ([[gen-vigencia-temporal]]), lo contradictorio (`relations.contradice`) y la baja
> `confidence`, en vez de afirmar con falsa seguridad. Si no hay información, dilo: no inventes.

**Después** (cuerpo íntegro v3):

> QUERY responde navegando el grafo, no leyendo todo, en dos pasos sancionados:
>
> **Paso 1 — navegación (siempre primero).** Empieza en `index.md`, baja por el hub del área
> si existe ([[gen-jerarquizacion-indice]]), sigue las relaciones `[[...]]` relevantes y abre
> solo las páginas necesarias (presupuesto de contexto).
>
> **Paso 2 — fallback léxico (solo tras agotar el paso 1).** Si la navegación no halla el
> tema (2-3 saltos desde `index.md` — secciones/hubs plausibles y sus relaciones — sin
> resultado), busca por CONTENIDO sobre `wiki/`: grep de los términos del tema y sus
> variantes, incluido el `glossary` del manifiesto (en Obsidian equivale al buscador). Abre
> SOLO las páginas que matchean y cítalas igual que en el paso 1 — el fallback localiza
> candidatos, no lee todo, y respeta TODAS las reglas de abajo (confidencialidad incluida).
> **Transparencia obligatoria:** declara en la respuesta "hallado por búsqueda léxica, no
> por navegación" y deja línea en `log.md` (`QUERY fallback-lexico: <tema> → [[página]]`) —
> es la señal para [[gen-lint]] de que a esas páginas les faltan relaciones o ancla.
>
> En ambos pasos: cita las páginas-fuente consultadas y su `confidence`, **excepto las
> `sensibilidad: confidencial`** ([[gen-confidencialidad]]): de esas no revela contenido
> sensible ni las cita textualmente — responde con referencia indirecta o ID seudonimizado.
> Advierte **siempre** lo vencido por `valido_hasta` ([[gen-vigencia-temporal]]), lo
> contradictorio (`relations.contradice`) y la baja `confidence`, en vez de afirmar con
> falsa seguridad. Si ni la navegación ni la búsqueda léxica encuentran, dilo — "no hay
> información" significa que TAMPOCO el contenido lo contiene, no solo que el grafo no
> llegó. No inventes.

### 4. `genome/genes/gen-consolidate.md` — v2 → v3 (diff por secciones)

Frontmatter: `version: 2` → `version: 3`.

**Antes** (cierre del cuerpo):

> Sube `confidence` y `last_reinforced` de lo que múltiples fuentes confirman.
> Cambios de contenido se aplican directo; cambios de regla pasan por [[gen-evolve]].

**Después**:

> Sube `confidence` y `last_reinforced` de lo que múltiples fuentes confirman.
> Mantiene además la jerarquía del índice ([[gen-jerarquizacion-indice]]): cuando una
> sección de `index.md` supera `hub_umbral` anclas, la parte en `hub-<área>.md` de forma
> idempotente (misma área → mismo hub; re-partir no duplica).
> Cambios de contenido se aplican directo; cambios de regla pasan por [[gen-evolve]].

### 5. `genome/capsules/ingesta-de-fuente.md` — v2 → v3 (diff por secciones)

Frontmatter — **antes**:

```yaml
version: 2
composes: [gen-raw-inmutable, gen-frontmatter-obligatorio, gen-confidencialidad, gen-ingest]
```

**después**:

```yaml
version: 3
composes: [gen-raw-inmutable, gen-frontmatter-obligatorio, gen-confidencialidad, gen-jerarquizacion-indice, gen-ingest]
```

Paso 7 — **antes**:

> 7. **Registrar**: añade ancla en `index.md` **solo si `sensibilidad != confidencial`**
>    ([[gen-confidencialidad]]) y una línea en `log.md`.

**después**:

> 7. **Registrar**: añade ancla según los criterios deterministas de
>    [[gen-jerarquizacion-indice]] (`sensibilidad != confidencial`
>    ([[gen-confidencialidad]]), tier `semantic|procedural`, `clase != evento`; destino:
>    `index.md`, o el `hub-<área>` si el área ya se partió) y una línea en `log.md`.

### 6. `CLAUDE.md` — 4 diffs exactos (y re-sync de `AGENTS.md`)

**(a) Principio 3** (la evaluación lo señala como el desincentivo del fallback; sin este
diff, gen-query v3 contradiría un principio — la clase sev-5 que AUDIT ya caza):

Antes (línea 14):

```
3. **Presupuesto de contexto**: navega SIEMPRE desde `index.md` por relaciones; no leas todo.
```

Después:

```
3. **Presupuesto de contexto**: navega primero y SIEMPRE desde `index.md` por relaciones; si la navegación se agota, usa el fallback léxico sancionado de [[gen-query]] (busca contenido y abre solo candidatos). Nunca leas la wiki entera.
```

**(b) Tabla de operaciones — fila QUERY** (línea 27):

Antes:

```
| `QUERY <X>` | "busca / qué sabemos de" | Navega desde `index.md` por relaciones; responde citando páginas-fuente. |
```

Después:

```
| `QUERY <X>` | "busca / qué sabemos de" | Navega desde `index.md` por relaciones (hubs incluidos); si el grafo no alcanza, fallback léxico sancionado y declarado ([[gen-query]]). Responde citando páginas-fuente. |
```

**(c) Tabla de operaciones — fila CONSOLIDATE** (línea 29; evita la divergencia
resumen↔canon que AUDIT P1 ya cazó una vez):

Antes:

```
| `CONSOLIDATE` | mantenimiento | Promueve conocimiento confirmado de tier (working→semantic), fusiona duplicados, baja confidence de lo no reforzado. |
```

Después:

```
| `CONSOLIDATE` | mantenimiento | Promueve conocimiento confirmado de tier (working→semantic), fusiona duplicados, baja confidence de lo no reforzado; parte secciones del índice que superen `hub_umbral` en páginas-hub ([[gen-jerarquizacion-indice]]). |
```

**(d) Índice de genes activos — bloque "Ciclo de vida y calidad"**: insertar entre
`[[gen-sintesis-de-volumen]]` (línea 48) y `[[gen-migracion-genoma]]` (línea 49):

```
- [[gen-jerarquizacion-indice]] — el índice crece con política: anclado determinista y partición en páginas-hub al superar `hub_umbral`.
```

Tras aplicar: **re-sincronizar `AGENTS.md`** copia exacta de `CLAUDE.md` (paso 4 de
[[gen-compuerta-mutacion]]; hoy están verificados byte-idénticos).

### 7. `index.md` — cabecera normativa (diff exacto)

Antes (líneas 9-10):

```
Punto de entrada del cerebro. El agente lee este archivo primero y navega desde aquí
por las relaciones `[[...]]`. Mantener corto: solo páginas-ancla, no todo el contenido.
```

Después:

```
Punto de entrada del cerebro. El agente lee este archivo primero y navega desde aquí
por las relaciones `[[...]]`. Mantener corto: solo páginas-ancla, no todo el contenido;
si una sección supera `hub_umbral` anclas, se parte en página-hub y aquí queda solo
`[[hub-<área>]]` ([[gen-jerarquizacion-indice]]).
```

Y la línea de la sección "Memoria (anclas por tier)" — antes (línea 28):

```
Aún vacío. Conforme ingieras fuentes, enlaza aquí las páginas-ancla de cada área.
```

Después:

```
Aún vacío. Conforme ingieras fuentes, ancla aquí según [[gen-jerarquizacion-indice]]
(determinista: ni confidencial, ni working/episodic, ni `clase: evento`).
```

### 8. `onboard/company.example.yaml` — clave nueva (diff exacto)

Insertar inmediatamente después del bloque de `sintesis_umbral` (línea 42):

```yaml
# Umbral de anclas por sección de index.md: al superarlo, CONSOLIDATE parte la sección
# en una página-hub wiki/<tier>/hub-<área>.md (gen-jerarquizacion-indice)
hub_umbral: 7
```

## Compatibilidad e impacto

**Compone (sin choque):**
- [[gen-confidencialidad]] — el criterio 1 del anclado ES su regla (1) actual; los hubs la
  heredan explícitamente ("un hub nunca lista confidenciales"). El fallback léxico de QUERY
  mantiene sus restricciones de cita en el paso 2 (texto explícito en gen-query v3).
- [[gen-clase-temporal]] + [[gen-sintesis-de-volumen]] — los eventos no se anclan uno a
  uno; se alcanzan por su síntesis (relación `agrega`) o su entidad. El hub NO compite con
  la síntesis: hub = navegación, síntesis = conocimiento destilado.
- [[gen-frontmatter-obligatorio]] — el hub cumple el esquema completo (no es `type: meta`
  exento: debe ser nodo visible del grafo para Dataview/graphify/LINT). `type: hub` queda
  definido por el gen nuevo, así el chequeo (e) de [[gen-lint]] lo reconoce como esquema
  válido. No requiere bump de gen-frontmatter-obligatorio: ese gen no cierra el set de
  valores de `type`.
- [[gen-lint]] — sin bump: sus chequeos no cambian. Gana dos insumos nuevos vía `log.md`
  (señal `sobre hub_umbral` de INGEST; `QUERY fallback-lexico:` como evidencia de
  relaciones/anclas faltantes). Un hub nunca es huérfano (enlace entrante desde `index.md`,
  salientes hacia sus anclas).
- [[gen-onboard]] — sin bump: `hub_umbral` lo lee gen-jerarquizacion-indice directamente
  del manifiesto, mismo patrón que `sintesis_umbral` (que no pasa por gen-onboard).
  Manifiesto sin la clave → default 7 (determinista también para quien no configura).
- [[gen-migracion-genoma]] — pase de migración tras aplicar: **no-op comprobable** en el
  estado actual (pre-ONBOARD, `wiki/` vacía: 0 páginas que re-validar; `index.md` no tiene
  ninguna sección con anclas, mucho menos sobre umbral). Blueprints: ninguno declara
  `hub_umbral` → aplica el default 7; añadirlo a los 5 blueprints es opcional y NO bloquea
  esta mutación (puede ir en una pasada posterior de blueprints).

**Interacciones conocidas (aceptadas, sin cambio de gen):**
- [[gen-graph-lens]] — los hubs entrarán a la lente y aparecerán como god-nodes
  **deliberados**; la señal "hub → candidato de CONSOLIDATE" podría proponer fusionarlos.
  Mitigación suficiente hoy: `type: hub` es visible en el frontmatter y toda señal de GRAPH
  solo se PROPONE (gate humano). Si en la práctica genera ruido, una mutación menor futura
  eximiría `type: hub` en la lectura de señales.
- Principio 3 de `CLAUDE.md` — se edita (diff 6a) precisamente para que la sanción del
  fallback no contradiga un principio inviolable; conserva el espíritu (grafo primero,
  jamás leer todo) y añade la válvula sancionada.

**Colisiones de esta tanda (versionado, no semántica):** A-01 propone cápsula v3
(anti-inyección), A-04 propone gen-ingest v++ y cápsula v3 (identidad/ledger), A-05
propone gen-consolidate v++ (umbrales de ciclo de vida). Los diffs de ESTA propuesta están
escritos contra las versiones vigentes hoy (gen-ingest v1, gen-query v2, gen-consolidate
v2, cápsula v2). Al aprobar más de una propuesta que toque el mismo archivo, aplicarlas en
secuencia y renumerar `version` en orden de aplicación (la segunda que toque la cápsula
será v4, etc.); las reglas no chocan semánticamente — identidad de página (A-04) y destino
del ancla (A-06) son ortogonales, y el paso 7 de la cápsula admite ambas ediciones.

**Impacto en operación:** INGEST gana 1 decisión determinista (3 checks) por página;
CONSOLIDATE gana 1 tarea por corrida (contar anclas por sección, partir si procede);
QUERY gana 1 paso condicional. La partición es cambio de contenido (log.md + commit
normal), NO mutación de genoma: cero fatiga extra de compuerta en régimen.

## Líneas draft para `genome/events.jsonl`

Una línea por objetivo mutado, mismo esquema de claves que las existentes
(`ts,type,target,signal,diff,approved_by,status`), listas para pegar al aprobar
(ajustar `ts` al día real de aplicación):

```jsonl
{"ts":"2026-07-02","type":"gene_added","target":"gen-jerarquizacion-indice","signal":"evaluacion 2026-07-01-810f24e sev-4 (A-06): escala sin politica - index unico sin regla de jerarquizacion, anclado de INGEST 'si aplica', QUERY sin fallback sancionado","diff":"∅ -> gen-jerarquizacion-indice v1 (anclado determinista: !confidencial + tier semantic|procedural + clase != evento; particion en hub-<area> al superar hub_umbral (default 7, manifiesto); parte CONSOLIDATE; idempotente por ruta de hub; type: hub definido)","approved_by":"user","status":"applied"}
{"ts":"2026-07-02","type":"gene_edited","target":"gen-ingest","signal":"A-06: el anclado 'si aplica' era la brecha de determinismo del indice","diff":"v1 -> v2 (ancla segun criterios de gen-jerarquizacion-indice, en index.md o hub del area; 'si aplica' eliminado)","approved_by":"user","status":"applied"}
{"ts":"2026-07-02","type":"gene_edited","target":"gen-query","signal":"A-06: QUERY no distinguia 'no existe' de 'existe y no lo encontre'; el fallback lexico no estaba sancionado","diff":"v2 -> v3 (paso 1 navegacion via hubs + paso 2 fallback lexico sobre wiki/ tras agotar navegacion, transparencia 'hallado por busqueda lexica' + senal a LINT en log.md; confidencialidad y vigencia rigen en ambos pasos)","approved_by":"user","status":"applied"}
{"ts":"2026-07-02","type":"gene_edited","target":"gen-consolidate","signal":"A-06: la particion del indice necesita dueno; CONSOLIDATE ya reestructura por umbral (sintesis-de-volumen)","diff":"v2 -> v3 (+ mantiene la jerarquia del indice: parte secciones sobre hub_umbral en hub-<area>, idempotente, cambio de contenido sin compuerta)","approved_by":"user","status":"applied"}
{"ts":"2026-07-02","type":"capsule_edited","target":"cap-ingesta-de-fuente","signal":"A-06: el paso 7 anclaba con la regla vieja (solo el filtro de confidencialidad)","diff":"v2 -> v3 (paso 7 ancla segun gen-jerarquizacion-indice; composes += gen-jerarquizacion-indice)","approved_by":"user","status":"applied"}
```

## Criterios de aceptación (comprobables tras aplicar)

1. `genome/genes/gen-jerarquizacion-indice.md` existe con frontmatter
   `id: gen-jerarquizacion-indice`, `status: active`, `version: 1`; contiene `hub_umbral`,
   `type: hub` y la plantilla de hub.
2. `grep -c "si aplica" genome/genes/gen-ingest.md` devuelve **0**; el gen queda
   `version: 2` y referencia `[[gen-jerarquizacion-indice]]`.
3. `genome/genes/gen-query.md` queda `version: 3`; contiene "fallback léxico", la frase de
   transparencia "hallado por búsqueda léxica" y el formato de línea para `log.md`;
   conserva las reglas de `confidencial` y `valido_hasta` (grep de ambas).
4. `genome/genes/gen-consolidate.md` queda `version: 3` y contiene `hub_umbral`.
5. `genome/capsules/ingesta-de-fuente.md` queda `version: 3`, `composes` incluye
   `gen-jerarquizacion-indice` y el paso 7 lo referencia.
6. `CLAUDE.md`: principio 3 con el fallback sancionado; filas QUERY y CONSOLIDATE
   actualizadas; `[[gen-jerarquizacion-indice]]` listado en "Ciclo de vida y calidad".
   `diff AGENTS.md CLAUDE.md` sin salida (re-sync hecho).
7. `index.md`: cabecera menciona la partición en hub y la sección Memoria referencia el
   gen (su `updated` sube al día de aplicación).
8. `onboard/company.example.yaml` contiene `hub_umbral: 7` (una sola vez).
9. `genome/events.jsonl`: exactamente 5 líneas nuevas al final, cada una JSON válido
   (`python -m json.tool` línea a línea, o el chequeo POSIX equivalente); `git diff` del
   archivo muestra solo adiciones (append-only intacto).
10. Comportamiento (se mide en Fase B, B-04 ya lo prevé: "comportamiento del índice al
    crecer (con A-06)"): en un ensayo en un directorio temporal FUERA del repo, un área con
    8 anclas produce exactamente 1 `hub-<área>.md`, `index.md` queda con 1 línea para esa
    área, y re-ejecutar la partición produce 0 cambios (idempotencia observable).

## Riesgos y alternativas consideradas

**Alternativas descartadas:**
- *Repartir la política entre genes existentes sin gen nuevo* — la política tiene tres
  consumidores (INGEST, CONSOLIDATE, QUERY); sin un canon único se recrea el patrón de
  divergencia resumen↔canon que AUDIT P1 ya cazó. Precedente a favor del gen-política:
  [[gen-confidencialidad]] (multi-consumidor) y [[gen-sintesis-de-volumen]] (umbral +
  página agregadora, consumido por CONSOLIDATE).
- *Partición por LINT* — LINT diagnostica y propone hallazgo a hallazgo; no reestructura.
  CONSOLIDATE ya hace exactamente esta forma de trabajo (N ítems → página agregadora).
- *Hubs como `type: meta`* — quedarían exentos de frontmatter y fuera del grafo
  (invisibles para Dataview/graphify y para el LINT de esquema); el hub debe ser nodo.
- *Léxico-primero (buscar siempre antes de navegar)* — invierte el diseño: el grafo
  primero ES el presupuesto de contexto y, además, la métrica de salud (si el léxico
  encuentra lo que el grafo no, faltan relaciones — esa señal desaparecería si el léxico
  fuera el camino normal).
- *N fijo sin configuración / configurable sin default* — lo primero ignora que el tamaño
  de área varía por sector; lo segundo rompe el determinismo para quien no configura.
  `hub_umbral: 7` con default replica el patrón probado de `sintesis_umbral`.

**Riesgos residuales y mitigación:**
- *Hubs leídos como god-nodes por GRAPH* → señal espuria de fusión; mitigado por `type:
  hub` visible + gate de señales (ver Compatibilidad). Reevaluar tras la primera corrida
  GRAPH con hubs reales.
- *Umbral 7 mal calibrado para algún sector* → `hub_umbral` en el manifiesto lo corrige
  por empresa sin mutar genoma; B-04 dará el primer dato real.
- *Fallback léxico con morfología del español (tildes, flexiones)* → falsos negativos del
  grep; el gen ordena buscar variantes del término e incluir el `glossary` del manifiesto
  (sinónimos internos). Si B-04 muestra recall bajo por esto, se afina con una mutación
  menor de gen-query.
- *Deriva "todo por léxico" (pereza de navegación)* → el paso 2 exige agotar el paso 1 y
  declarar el fallback en la respuesta y en `log.md`: el abuso queda visible para LINT y
  para AUDIT (la transparencia es el freno).
- *Ventana entre INGEST y CONSOLIDATE con secciones sobre umbral* → aceptada: el índice
  tolera desborde temporal; la señal en `log.md` garantiza que el próximo CONSOLIDATE lo
  cierre. No se le da la partición a INGEST para mantenerlo barato y de responsabilidad
  única.
