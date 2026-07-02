---
tipo: propuesta-evolve
tarea: A-05
eval_id: 2026-07-01-810f24e
status: approved
fecha: 2026-07-02
genes_afectados: [gen-ciclo-de-vida, gen-consolidate, gen-clase-temporal, gen-confianza-por-fuente]
---

# Propuesta EVOLVE A-05 — Umbrales numéricos del ciclo de vida de la memoria

**Bajo compuerta ([[gen-compuerta-mutacion]]): esta propuesta NO aplica nada.** Si el
operador la aprueba, la aplicación es mecánica siguiendo la "Ruta de aplicación" al final
de Cambios propuestos.

## Motivación

Hallazgo **sev-4** de la lente de gestión del conocimiento (evaluación
`audit/evaluations/2026-07-01-810f24e/`): *"La memoria por capas con decaimiento es
metáfora, no mecanismo: sin umbrales operativos de promoción ni función de decaimiento"*.

Evidencia (rutas):

- `audit/evaluations/2026-07-01-810f24e/10-panel.md` — sección "Gestión del conocimiento",
  primera debilidad sev-4: `decay_rate` solo existe como etiqueta high/low sin constantes de
  tiempo (verificado por grep en todo el genoma); `gen-consolidate` "promueve conocimiento
  confirmado" sin definir *confirmado* (nº de fuentes, piso de `confidence`, permanencia);
  LINT debe detectar "vencido blando por `last_reinforced` + `decay_rate`" sin criterio
  numérico; las magnitudes de ajuste de `confidence` quedan a juicio del LLM en cada corrida.
- `audit/evaluations/2026-07-01-810f24e/10-panel.md` — riesgo "Deriva no reproducible del
  estado del conocimiento" (prob. alta / impacto alto): dos corridas de CONSOLIDATE sobre el
  mismo historial pueden producir estados distintos, en tensión directa con el eje de
  reproducibilidad del sistema.
- `audit/evaluations/2026-07-01-810f24e/30-valoracion.md` — recomendación consolidada nº 5:
  "codificar […] umbrales numéricos de decay, promoción entre tiers y confianza — la
  'memoria por capas' deja de ser prosa".
- `audit/evaluations/2026-07-01-810f24e/60-backlog.md` — tarea **A-05 [genoma·gate]**.

Genes hoy afectados por el vacío: `genome/genes/gen-consolidate.md` (v2),
`genome/genes/gen-clase-temporal.md` (v1), `genome/genes/gen-confianza-por-fuente.md` (v1),
más `gen-lint` (v3) que ya declara el chequeo "vencido blando" pero sin número que lo defina.

## Diseño en una frase

Un **gen nuevo** concentra TODOS los números del ciclo de vida (fuente de verdad única,
sobreescribible por manifiesto), y los tres genes existentes pasan a **referenciarlo** en
vez de dejar la magnitud a juicio del LLM — mismo patrón que `sintesis_umbral`
([[gen-sintesis-de-volumen]]) y `source_trust` ([[gen-confianza-por-fuente]]).

Los valores default son **razonados, no calibrados**: quedan marcados como revisables y el
piloto Fase 0 (tareas B-03 idempotencia y B-04 recall del backlog) los medirá; este gen se
re-versionará entonces con evidencia, por la compuerta normal.

## Cambios propuestos

### C1 — Gen NUEVO: `genome/genes/gen-ciclo-de-vida.md` (v1)

Texto completo, listo para copiar:

```markdown
---
id: gen-ciclo-de-vida
trigger: reforzar, degradar, promover o archivar páginas de wiki/ (CONSOLIDATE, LINT, QUERY, INGEST)
status: active
version: 1
---

La memoria por capas deja de ser metáfora: estos son los **números** del ciclo de vida.
Son defaults del genoma base, sobreescribibles por empresa en el bloque `ciclo_de_vida` de
`onboard/company.yaml` (esquema en `company.example.yaml`). Valores **razonados, no
calibrados**: el piloto Fase 0 los medirá y este gen se re-versionará con evidencia.

**Ventanas de decaimiento** (`decay_ventana_dias`). `decay_rate` significa "días sin
refuerzo antes de empezar a decaer": `high` = 14 · `medium` = 60 · `low` = 180. Default al
crear o mover una página, si no lo declara: `working/` y `episodic/` = high, `semantic/` =
medium, `procedural/` = low; `clase: evento` siempre high ([[gen-clase-temporal]]) y
`type: sintesis` low ([[gen-sintesis-de-volumen]]). El `decay_rate` declarado en la página
gana sobre el default del tier.

**Refuerzo** — qué cuenta y su efecto: (1) una fuente nueva que confirma el contenido
(INGEST / BULK INGEST) pone `last_reinforced: hoy`, se añade a `sources` y sube
`confidence` según su tipo (`refuerzo_delta`): oficial +0.10, interna +0.05, blanda +0.03 y
solo si concuerda; (2) citar la página para sostener una respuesta de QUERY refresca
`last_reinforced` (el uso reinicia el reloj) pero **no** sube `confidence` (uso no es
verificación); (3) agregar eventos nuevos a una página `type: sintesis` refuerza la
síntesis. Techo del refuerzo automático: `confidence` nunca supera
`min(max(source_trust de sus fuentes) + 0.10, 0.95)` — con los `source_trust` del
manifiesto de ejemplo, una página solo-blanda topa en 0.5: lo blando corrobora, no
sustituye ([[gen-confianza-por-fuente]]). Las `clase: evento` no se refuerzan, nunca.

**Degradación** (la aplica CONSOLIDATE; LINT la detecta como "vencido blando"): por cada
ventana completa transcurrida sin refuerzo, `confidence -= 0.05` (`decaimiento_delta`). Al
aplicarla se anota `decay_aplicado: YYYY-MM-DD` y las ventanas siguientes se cuentan desde
`max(last_reinforced, decay_aplicado)`: re-correr CONSOLIDATE no descuenta dos veces
(idempotencia). Excepción: en `clase: evento` la degradación **no toca** `confidence` (que
algo ocurrió no se vuelve falso); su ciclo es el archivo por antigüedad. La vigencia dura
([[gen-vigencia-temporal]]) es ortogonal: ni el refuerzo ni el uso "des-vencen" un
`valido_hasta` pasado ni una `vigencia` no-vigente.

**Promoción `working → semantic`** (CONSOLIDATE la aplica directo y la reporta) cuando se
cumplen TODAS: `clase: estable` · `confidence ≥ 0.70` · ≥2 fuentes en `sources` **o** ≥2
páginas distintas que la referencian · edad ≥7 días desde `created` **y** ≥1 refuerzo
posterior (`last_reinforced > created`, proxy verificable de "confirmada en más de una
sesión") · sin `contradice` abierta · `sensibilidad ≠ confidencial`
([[gen-confidencialidad]] prohíbe promoverlas). Procesos repetidos promueven a
`procedural/` con las mismas condiciones. Al promover: mover el archivo a la carpeta de
taxonomía que corresponda (los `[[wiki-links]]` van por nombre y no se rompen), ajustar
`decay_rate` al default del tier destino salvo declaración explícita, y dejar línea en
`log.md`.

**Suelo y archivo** (CONSOLIDATE lo **propone**, aplica solo tras OK): página
`clase: estable` con `confidence ≤ 0.30` (`piso_archivo`) y sin refuerzo → mover a
`wiki/archive/` añadiendo `archivado: YYYY-MM-DD` (frontmatter intacto, `raw/` jamás se
toca, el ancla en `index.md` se retira). `clase: evento` con `fecha_evento` a más de 180
días (`archivo_eventos_dias`) → candidata a archivo, de bajo riesgo si ya está agregada en
una síntesis; los resúmenes de `episodic/` siguen esta misma regla de eventos. **Nunca** se
archiva una página con `estado` operativo abierto ([[gen-entidad-con-estado]], accionables
de sector). Lo archivado no se cita en QUERY salvo pedido explícito de histórico.
```

### C2 — `genome/genes/gen-consolidate.md` v2 → v3 (diff por secciones)

Los criterios y magnitudes NO se duplican aquí (fuente de verdad única = el gen nuevo;
evita la clase de contradicción entre genes que la corrida AUDIT 2026-06-30 ya corrigió).

Sección "promoción" — antes:

```diff
- CONSOLIDATE gestiona el ciclo de vida de la memoria entre tiers. Promueve conocimiento
- confirmado hacia tiers más estables (`working → semantic`, procesos repetidos → `procedural`),
+ CONSOLIDATE gestiona el ciclo de vida de la memoria entre tiers con los **umbrales
+ numéricos de [[gen-ciclo-de-vida]]**. Promueve conocimiento confirmado —TODOS los
+ criterios verificables de promoción de ese gen— hacia tiers más estables
+ (`working → semantic`, procesos repetidos → `procedural`),
```

Sección "decaimiento y archivo" — antes/después (la exención de duplicados
`deriva_de`/`supersede`/`agregado_en` queda intacta):

```diff
- duplicados: no se fusionan ni se marcan como redundancia; solo se verifica que el marcador
- canónico/de síntesis esté presente—, y aplica decaimiento: baja
- `confidence` de lo no reforzado y archiva o deprecia lo obsoleto (sin borrar fuentes de
- `raw/`). Sube `confidence` y `last_reinforced` de lo que múltiples fuentes confirman.
- Cambios de contenido se aplican directo; cambios de regla pasan por [[gen-evolve]].
+ duplicados: no se fusionan ni se marcan como redundancia; solo se verifica que el marcador
+ canónico/de síntesis esté presente—, y aplica el decaimiento numérico de
+ [[gen-ciclo-de-vida]]: resta `decaimiento_delta` por ventana de `decay_rate` vencida sin
+ refuerzo, anotando `decay_aplicado` (re-ejecutable sin doble descuento); al tocar el
+ `piso_archivo` **propone** archivar en `wiki/archive/` — tras OK, sin borrar fuentes de
+ `raw/`. Sube `confidence` y `last_reinforced` de lo que múltiples fuentes confirman, con
+ los deltas y el techo de [[gen-ciclo-de-vida]]. Cambios de contenido (promoción y
+ decaimiento incluidos) se aplican directo; el archivo se propone; cambios de regla pasan
+ por [[gen-evolve]].
```

Frontmatter: `version: 2` → `version: 3`.

### C3 — `genome/genes/gen-clase-temporal.md` v1 → v2 (diff por secciones)

Sección "eventos" — antes/después:

```diff
- no se fusiona ni sube su `confidence` al re-verlo. Las `estable` (ficha de producto, concepto,
+ no se fusiona ni sube su `confidence` al re-verlo. Su decaimiento tampoco degrada
+ `confidence` (el registro histórico no se vuelve falso): su ciclo es el **archivo por
+ antigüedad** (`archivo_eventos_dias`, [[gen-ciclo-de-vida]]). Las `estable` (ficha de producto, concepto,
```

(la línea original continúa con "Las `estable` …"; el resto del párrafo no cambia, solo
re-fluir el ancho de línea si hace falta)

Sección final — antes/después:

```diff
- CONSOLIDATE y LINT actúan según `clase`: los eventos no se promueven como conocimiento durable
- (pero sí se agregan, ver [[gen-sintesis-de-volumen]]). Es base de [[gen-entidad-con-estado]].
+ CONSOLIDATE y LINT actúan según `clase`, con los umbrales de [[gen-ciclo-de-vida]]
+ (ventanas de `decay_rate`, archivo de eventos): los eventos no se promueven como
+ conocimiento durable (pero sí se agregan, ver [[gen-sintesis-de-volumen]]). Es base de
+ [[gen-entidad-con-estado]].
```

Frontmatter: `version: 1` → `version: 2`.

### C4 — `genome/genes/gen-confianza-por-fuente.md` v1 → v2 (diff por secciones)

Última sección — antes/después:

```diff
- (`source_trust`). Varias señales blandas concordantes pueden subir la `confidence` de un hecho,
- pero no sustituyen a una fuente primaria. Complementa [[gen-ingest]].
+ (`source_trust`). Varias señales blandas concordantes pueden subir la `confidence` de un hecho,
+ pero no sustituyen a una fuente primaria: el **refuerzo también se ancla a la fuente** —
+ los deltas de subida por tipo y el techo anclado a `source_trust` viven en
+ [[gen-ciclo-de-vida]]; con los valores de ejemplo, una página solo-blanda topa en 0.5.
+ Complementa [[gen-ingest]] y [[gen-ciclo-de-vida]].
```

(el techo `min(max(source_trust de sus fuentes) + 0.10, 0.95)` NO se re-declara aquí:
solo se apunta al gen nuevo; el 0.5 sí se menciona porque ya era un número propio de este
gen — "nacen bajas (≤0.5)")

Frontmatter: `version: 1` → `version: 2`.

### C5 — `CLAUDE.md` (y re-sync byte a byte de `AGENTS.md`)

(1) Índice de genes activos, bloque **Ciclo de vida y calidad** — insertar como primera
viñeta, antes de `- [[gen-clase-temporal]] …`:

```diff
 **Ciclo de vida y calidad**
+- [[gen-ciclo-de-vida]] — los números de la memoria por capas: ventanas de decay, refuerzo, promoción working→semantic y piso de archivo; overridable por manifiesto.
 - [[gen-clase-temporal]] — conocimiento estable vs evento fechado; decaen distinto.
```

(2) Tabla de operaciones, fila `CONSOLIDATE` — antes/después:

```diff
-| `CONSOLIDATE` | mantenimiento | Promueve conocimiento confirmado de tier (working→semantic), fusiona duplicados, baja confidence de lo no reforzado. |
+| `CONSOLIDATE` | mantenimiento | Promueve conocimiento confirmado de tier (working→semantic), fusiona duplicados, baja confidence de lo no reforzado — con los umbrales numéricos de [[gen-ciclo-de-vida]]. |
```

(3) Mapa de la memoria (tiers de `wiki/`) — añadir al final de la lista:

```diff
 - `procedural/` — SOPs y procesos de la empresa.
+- `archive/` — retirado de circulación por CONSOLIDATE (piso de confidence, eventos viejos); histórico consultable solo a pedido. Regla: [[gen-ciclo-de-vida]].
```

Tras editar `CLAUDE.md`, copiar íntegro a `AGENTS.md` (regla de la casa: copia exacta).

### C6 — `onboard/company.example.yaml`: bloque nuevo OPCIONAL + nota para blueprints

Insertar entre `sintesis_umbral: 3` y el comentario de `default_sensibilidad`:

```yaml
# Umbrales del ciclo de vida de la memoria (gen-ciclo-de-vida). OPCIONAL: si se omite el
# bloque (o cualquier clave), aplican estos mismos defaults del genoma base.
# Defaults v1 razonados pero NO calibrados: se revisan con las métricas del piloto Fase 0.
ciclo_de_vida:
  decay_ventana_dias: { high: 14, medium: 60, low: 180 }   # días sin refuerzo = 1 ventana
  decaimiento_delta: 0.05     # confidence que se resta por ventana vencida
  refuerzo_delta: { oficial: 0.10, interna: 0.05, blanda: 0.03 }  # subida por confirmación
  confidence_techo: 0.95      # techo absoluto del refuerzo automático
  piso_archivo: 0.30          # confidence <= piso => CONSOLIDATE propone archivar
  archivo_eventos_dias: 180   # eventos más viejos => candidatos a archivo
  promocion:                  # working -> semantic (todas las condiciones a la vez)
    confidence_min: 0.70
    fuentes_min: 2            # fuentes distintas en `sources`...
    refs_min: 2               # ...o páginas distintas que la referencien
    edad_min_dias: 7          # y >= 1 refuerzo posterior a `created`
```

Las claves de `refuerzo_delta` son las mismas categorías que `source_trust`
(oficial/interna/blanda), a propósito.

**Nota para blueprints (`onboard/blueprints/*.yaml`): NO se les añade el bloque.** A
diferencia de `graph_lens` (P2 de la corrida AUDIT 2026-06-30, donde un gen necesitaba un
nodo YAML donde escribir), `ciclo_de_vida` es puramente opcional-con-defaults y ninguna
operación escribe en él: los blueprints se mantienen livianos por diseño declarado
(`onboard/blueprints/README.md`: "todo lo universal ya vive en el genoma base"). Si el
piloto muestra que un vertical necesita otras ventanas (p. ej. legal/salud con `low` más
largo para conocimiento normativo), se añadirá entonces con evidencia.

### C7 — Estructura: `wiki/archive/`

Al aplicar, crear `wiki/archive/.gitkeep` (mismo patrón que los otros tiers). No es
mutación de genoma: es la carpeta que el gen referencia.

### Ruta de aplicación (mecánica, tras el OK)

1. Crear `genome/genes/gen-ciclo-de-vida.md` con el texto de C1.
2. Aplicar diffs C2, C3, C4 con sus bumps de `version`.
3. Aplicar C5 en `CLAUDE.md`; copiar `CLAUDE.md` → `AGENTS.md` y verificar byte a byte.
4. Aplicar C6 en `onboard/company.example.yaml`.
5. Crear `wiki/archive/.gitkeep` (C7).
6. Añadir las 4 líneas de abajo a `genome/events.jsonl` (ajustar `ts` a la fecha real de
   aprobación) — el historial usa 1 commit por línea de evento; seguir ese patrón.
7. Correr el pase de migración ([[gen-migracion-genoma]]): pre-ONBOARD (wiki vacía) la
   deuda esperada es nula; verificar que el manifiesto de ejemplo quedó al día.
8. Marcar A-05 `[x]` en `60-backlog.md` + línea en `log.md` (lo hace el operador u otra
   tarea; fuera del alcance de este archivo).

## Compatibilidad e impacto

**Compone con (sin editar esos genes):**

- [[gen-lint]] v3 — su chequeo (c) "vencido blando por `last_reinforced` + `decay_rate`"
  gana por fin criterio numérico; y su chequeo (e) deja de marcar `decay_aplicado`/
  `archivado` como huérfanos de esquema porque ahora un gen los reconoce. Texto de gen-lint
  ya es genérico: no requiere bump.
- [[gen-query]] — la regla "re-cita refresca `last_reinforced`" vive en el gen nuevo; mismo
  patrón de asignación cruzada que [[gen-sintesis-de-volumen]] usa con CONSOLIDATE. QUERY
  no sube `confidence` jamás.
- [[gen-ingest]] v1 / cápsula `ingesta-de-fuente` v2 — "actualiza y refuerza" ya existía;
  ahora el refuerzo tiene delta y techo. Sin cambios de texto.
- [[gen-vigencia-temporal]] v2 — ortogonalidad explícita: refuerzo/uso no "des-vencen"
  vigencia dura. Sin cambios.
- [[gen-confidencialidad]] v2 — la promoción excluye `confidencial` (ya lo prohibía);
  archivarlas no cambia su régimen (nunca tuvieron ancla).
- [[gen-entidad-con-estado]] v1 — actualizar `estado` in-place con evento de respaldo
  cuenta como refuerzo natural; páginas con `estado` operativo abierto no se archivan.
- [[gen-sintesis-de-volumen]] v1 — `type: sintesis` conserva `decay_rate: low`; agregarle
  eventos la refuerza; los eventos ya agregados son los candidatos de archivo de bajo riesgo.
- [[gen-onboard]] v4 — sin cambios: el bloque `ciclo_de_vida` se lee en tiempo de operación
  (patrón `sintesis_umbral`), ONBOARD no escribe en él.
- [[gen-frontmatter-obligatorio]] v4 — `decay_aplicado` y `archivado` quedan amparados por
  su "lista no exhaustiva" de campos opcionales. Registrarlos formalmente (bump a v5) se
  DIFIERE a propósito para no colisionar con otras propuestas de esta tanda que puedan
  bumpear ese gen (precedente: evento 10 de `events.jsonl` hizo ese registro a posteriori).

**Superficies nuevas / tensiones conocidas:**

- `decay_rate: medium` es valor nuevo (hoy el repo solo usa high/low). Los dashboards solo
  muestran la columna (`dashboards/salud-del-conocimiento.md`), no filtran por valor: no se
  rompen. Los paneles podrían querer excluir `wiki/archive/` de sus consultas `FROM "wiki"`;
  ajuste opcional de dashboards fuera de esta propuesta (dashboards no son archivo de esta
  tarea).
- Migración: pre-ONBOARD no hay páginas → deuda nula. Con wiki poblada, el pase de
  [[gen-migracion-genoma]] propondría completar `decay_rate` faltantes con el default del
  tier.
- Paralelismo de la tanda: esta propuesta NO toca `gen-ingest`, la cápsula ni `index.md`
  (territorio de A-01/A-04/A-06). Si otra propuesta aprobada edita los mismos genes o
  `company.example.yaml`, el operador encadena versiones/orden al aplicar.

**Ejemplo operado (sanity check de los números):** página nueva en `working/` desde fuente
interna (0.7, high=14d). Confirmada por segunda fuente interna al día 3 → `confidence` 0.75,
2 fuentes; al día 7 cumple promoción → `semantic/` (medium=60d). La misma página sin ningún
refuerzo: -0.05 por ventana de 14d → toca 0.30 a los ~112 días → CONSOLIDATE propone
archivarla. Una página solo-blanda (0.4) jamás llega a 0.70 (techo 0.5): nunca asciende sin
fuente primaria/interna — exactamente la epistemología de [[gen-confianza-por-fuente]].

## Líneas draft para `genome/events.jsonl` (pegar al aprobar; ajustar `ts`)

Una línea por mutación, mismo esquema de claves que las existentes:

```json
{"ts":"2026-07-02","type":"gene_added","target":"gen-ciclo-de-vida","signal":"eval 2026-07-01-810f24e sev-4 (KM) + backlog A-05: memoria por capas sin umbrales operativos de promocion ni funcion de decaimiento","diff":"∅ -> gen-ciclo-de-vida v1 (ventanas decay high=14d/medium=60d/low=180d por tier; refuerzo +0.10/+0.05/+0.03 por tipo de fuente con techo min(max(source_trust)+0.10, 0.95); re-cita en QUERY refresca last_reinforced sin subir confidence; degradacion -0.05/ventana con decay_aplicado idempotente; promocion working->semantic = estable + conf>=0.70 + >=2 fuentes o >=2 refs + >=7d con refuerzo posterior + sin contradice + no confidencial; piso 0.30 -> propone archivar en wiki/archive/; eventos sin decay de confidence, archivo a 180d; bloque ciclo_de_vida overridable en manifiesto)","approved_by":"user","status":"applied"}
{"ts":"2026-07-02","type":"gene_edited","target":"gen-consolidate","signal":"A-05: 'promueve conocimiento confirmado' y 'baja confidence' no definian confirmado ni magnitud","diff":"v2 -> v3 (promocion por los criterios verificables de gen-ciclo-de-vida; decaimiento numerico con decay_aplicado; al tocar el piso propone archivar en wiki/archive/ tras OK)","approved_by":"user","status":"applied"}
{"ts":"2026-07-02","type":"gene_edited","target":"gen-clase-temporal","signal":"A-05: decay high de eventos no tenia semantica operativa (no debe degradar confidence de un registro historico)","diff":"v1 -> v2 (eventos: la degradacion no toca confidence, su ciclo es archivo por antiguedad via archivo_eventos_dias; umbrales delegados a gen-ciclo-de-vida)","approved_by":"user","status":"applied"}
{"ts":"2026-07-02","type":"gene_edited","target":"gen-confianza-por-fuente","signal":"A-05: 'varias señales blandas pueden subir la confidence' sin delta ni tope dejaba la magnitud a juicio del LLM","diff":"v1 -> v2 (el refuerzo tambien se ancla a la fuente: deltas por tipo y techo anclado a source_trust delegados a gen-ciclo-de-vida; pagina solo-blanda topa en 0.5)","approved_by":"user","status":"applied"}
```

## Criterios de aceptación (comprobables tras aplicar)

1. `genome/genes/gen-ciclo-de-vida.md` existe, frontmatter `id: gen-ciclo-de-vida`,
   `status: active`, `version: 1`, y contiene los defaults exactos de C1
   (14/60/180 · 0.05 · 0.10/0.05/0.03 · 0.95 · 0.30 · 180 · 0.70/2/2/7).
2. `grep -l "gen-ciclo-de-vida" genome/genes/gen-consolidate.md genome/genes/gen-clase-temporal.md genome/genes/gen-confianza-por-fuente.md`
   → los 3 archivos; sus `version` quedan en 3, 2 y 2 respectivamente.
3. Los genes editados no re-declaran las constantes del gen nuevo (fuente de verdad única):
   `grep -E '0\.(05|10|30|95)|= ?14' genome/genes/gen-consolidate.md genome/genes/gen-clase-temporal.md genome/genes/gen-confianza-por-fuente.md`
   → sin coincidencias (los números preexistentes de gen-confianza —0.85, 0.5— no cuentan y
   no los captura ese patrón).
4. `CLAUDE.md` contiene `[[gen-ciclo-de-vida]]` en el índice de genes, en la fila
   CONSOLIDATE y en el mapa de tiers (línea `archive/`); `AGENTS.md` es copia byte a byte
   (`cmp CLAUDE.md AGENTS.md` sin salida).
5. `onboard/company.example.yaml` contiene el bloque `ciclo_de_vida:` con los mismos
   valores que el gen (verificable a ojo o con un parser YAML si está disponible).
6. Las 4 líneas nuevas de `genome/events.jsonl` son JSON válido línea a línea
   (`python -m json.tool` sobre cada una) con `targets` = los 4 de esta propuesta, y el
   archivo sigue siendo append-only (todas las líneas previas intactas, sea cual sea su
   número si otras propuestas de la tanda se aplicaron antes).
7. `wiki/archive/.gitkeep` existe.
8. Pase de migración corrido y reportado sin deuda (estado pre-ONBOARD).

## Riesgos y alternativas consideradas

**Riesgos:**

- *Defaults sin calibrar.* Son juicio razonado, no medición. Mitigación: marcados como
  revisables en el propio gen y en el manifiesto; B-03/B-04 (piloto Fase 0) los medirán y
  el re-ajuste pasará por la compuerta con datos.
- *Aritmética ejecutada por LLM sin validador* (Fase C diferida por decisión del operador).
  Mitigación: ventanas discretas + `decay_aplicado` hacen el cómputo trivial, idempotente y
  auditable en el diff de cada página; la deriva posible es estrictamente menor que el statu
  quo (juicio libre sin números).
- *El uso en QUERY mantiene vivo lo popular aunque sea dudoso.* Acotado: el uso solo
  reinicia el reloj, no sube `confidence`; `contradice`, LINT y la vigencia dura siguen
  mandando por encima.
- *Asimetría refuerzo (+0.10 máx) vs degradación (−0.05).* Deliberada: una verificación
  positiva es evidencia más fuerte que la ausencia de uso. Se re-evalúa con el piloto.
- *`wiki/archive/` como superficie nueva.* Los dashboards `FROM "wiki"` la incluirían;
  ajuste de paneles documentado como opcional (fuera de esta propuesta).

**Alternativas consideradas y descartadas:**

- *Función de decaimiento continua (exponencial `e^-λt`)* — más "correcta" en teoría, pero
  no computable de forma fiable ni auditable por un LLM sin herramienta; las ventanas
  discretas dan el mismo efecto con aritmética de restas verificable a ojo.
- *Repartir los números entre los genes existentes sin gen nuevo* — dispersa la fuente de
  verdad y multiplica el riesgo de contradicción entre genes (la clase de defecto que la
  corrida AUDIT 2026-06-30 ya tuvo que corregir); un gen = un lugar + un override.
- *Archivar in-place con un campo `status`/`estado` en el mismo tier* — ensucia los tiers y
  obliga a QUERY/dashboards a filtrar siempre; además colisiona semánticamente con el
  `estado` de [[gen-entidad-con-estado]]. Mover a `wiki/archive/` conserva el histórico sin
  ruido (y los `[[wiki-links]]` no se rompen: resuelven por nombre).
- *Borrar lo decaído en vez de archivarlo* — viola el espíritu del sistema (histórico
  reproducible, `raw/` inmutable) y el principio 7 de `CLAUDE.md`.
- *Exigir "confirmada en ≥M sesiones" literal para promover* — no hay registro de IDs de
  sesión en el frontmatter; se adoptó el proxy verificable `last_reinforced > created` +
  edad mínima, que no requiere campos nuevos.
