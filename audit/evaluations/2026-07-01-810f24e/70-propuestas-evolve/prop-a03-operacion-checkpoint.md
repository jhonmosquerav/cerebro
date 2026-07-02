---
tipo: propuesta-evolve
tarea: A-03
status: approved
fecha: 2026-07-02
genes_afectados: [gen-checkpoint]
---

# Propuesta EVOLVE — operación `CHECKPOINT` (gen-checkpoint v1, nuevo)

Propuesta bajo [[gen-compuerta-mutacion]]: este documento **no aplica nada**. Si el operador
aprueba, la aplicación es mecánica: copiar el gen (§Cambios 1), aplicar los diffs de
`CLAUDE.md` (§Cambios 2), re-sincronizar `AGENTS.md` (§Cambios 3), añadir la línea a
`genome/events.jsonl` (§Línea draft), 1 commit + 1 línea en `log.md`.

## Motivación

La evaluación multidisciplinar `2026-07-01-810f24e` convergió en que el rasgo insignia del
sistema —el "loop de memoria infinita"— hoy (a) no opera en vivo (tres hooks stub `echo`) y
(b) está diseñado exclusivamente sobre el mecanismo de hooks de Claude Code, es decir,
acoplado a un solo vendor: un agente en Cursor/Codex/OpenClaw que lea `AGENTS.md` no tiene
NINGÚN procedimiento definido para persistir la memoria de sesión. Evidencia:

- `audit/evaluations/2026-07-01-810f24e/30-valoracion.md` — riesgos mayores: "Pérdida de
  conocimiento de sesión en compactación — hoy garantizada (alta/alto)" y "Dependencia del
  modelo de hooks/memoria de un solo vendor (alta/alto)"; recomendación consolidada nº 4:
  "Desacoplar el loop de memoria del vendor — especificar el loop como contrato del genoma
  con implementaciones intercambiables (hooks de Claude Code + procedimiento manual + script
  local)"; y entre las 5 apuestas robustas de los escenarios: "loop de memoria como contrato
  multi-implementación".
- `audit/evaluations/2026-07-01-810f24e/10-panel.md` — lente de ingeniería agéntica:
  "Ciclo de memoria REAL (hooks SessionStart/PreCompact/Stop) — 1.5/5", debilidad sev-4
  "El 'loop de memoria infinita' es hoy tres stubs: el pilar del producto no existe" y riesgo
  "Bifurcación de capacidades al implementar los hooks (lock-in suave a Claude Code)"; lente
  de arquitectura (portabilidad 3.5/5): "el loop de memoria (hooks) es específico de Claude
  Code — en Cursor/OpenClaw solo viaja la parte manual del sistema".
- Estado del repo que lo confirma: `wiki/working/` y `wiki/episodic/` solo contienen
  `.gitkeep`; `.claude/settings.json` declara los stubs (honesto en `CLAUDE.md`, vendido en
  presente en `README.md`).
- Mandato: `audit/evaluations/2026-07-01-810f24e/60-backlog.md`, tarea **A-03 [genoma·gate]**:
  "el loop de memoria como contrato del genoma con implementación manual portable (cualquier
  agente que lea `AGENTS.md` la ejecuta sin hooks). Con A-02 forman 2 de las 3 implementaciones
  del contrato. (desacople de vendor)".

Qué ataca esta propuesta: convierte el loop de memoria en un **contrato del genoma** (mismas
postcondiciones para toda implementación) y entrega su **implementación manual portable**: la
operación `CHECKPOINT`. Con A-02 (hooks reales, tarea paralela) quedan 2 de las 3
implementaciones previstas; la tercera (script local) queda fuera del alcance de esta
propuesta.

## Cambios propuestos

### 1. Gen NUEVO — `genome/genes/gen-checkpoint.md` (v1, texto completo listo para copiar)

```markdown
---
id: gen-checkpoint
trigger: operación CHECKPOINT / "checkpoint" — o el agente la propone ante contexto largo o cierre de sesión sin hooks activos
status: active
version: 1
---

CHECKPOINT es la implementación **manual y portable** del loop de memoria: vuelca a disco lo
valioso de la sesión ANTES de que se pierda (compactación de contexto, cierre de sesión,
cambio de agente). El loop de memoria es un **contrato del genoma** con implementaciones
intercambiables que deben cumplir estas mismas postcondiciones: la **automática** son los
hooks de Claude Code (`PreCompact` ≈ paso 1; `Stop` ≈ pasos 2–4 + derivación a EVOLVE; ver
`.claude/hooks/README.md`); la **manual** es esta operación — cualquier agente que lea
`AGENTS.md` la ejecuta sin hooks ni harness específico. Ambas comparten la clave de
idempotencia: si coexisten sobre la misma sesión, actualizan los mismos archivos, no duplican.

## Disparador
El usuario escribe `CHECKPOINT`. Además, el agente lo PROPONE (nunca lo ejecuta sin OK, pero
tampoco lo calla) cuando nota: contexto cercano a compactarse, cierre de sesión sin hooks
activos, o ≥3 hallazgos valiosos aún sin persistir. Ejecutarlo escribe en `wiki/`, `index.md`
y `log.md` — NO muta genoma, así que no pasa por [[gen-compuerta-mutacion]].

## Clave de idempotencia
`session_key = <YYYY-MM-DD>-<slug-del-tema-dominante>` (kebab-case, sin acentos; si el harness
expone un id de sesión estable, se usa ese como slug). Se fija en el primer checkpoint de la
sesión y se reutiliza en los siguientes: **re-ejecutar CHECKPOINT actualiza, no duplica**.
Continuar el mismo tema el mismo día reutiliza la clave (es continuación); temas o días
distintos → claves distintas. **Regla de adopción** (convivencia con la implementación
automática): si ya existe un artefacto del loop para la MISMA sesión con otro nombre (p. ej.
la nota `<fecha>-precompact-<session8>.md` que deja el hook `PreCompact`), CHECKPOINT lo
adopta y lo actualiza en vez de crear un segundo archivo — nunca dos notas de working ni dos
episódicos para la misma sesión.

## Qué es "valioso" (se vuelca) y qué NO
SÍ se vuelca — solo lo que aún no está persistido en `wiki/`:
- **decisiones** tomadas en la sesión, con su porqué;
- **hechos nuevos** sobre entidades/conceptos del negocio que ninguna página recoge;
- **correcciones del usuario** a datos, clasificaciones o supuestos del agente;
- **pendientes y acuerdos** accionables (qué quedó abierto, próximos pasos);
- **fricciones/patrones repetidos** → se anotan como candidatos y se derivan a [[gen-evolve]]
  en modo propuesta (CHECKPOINT jamás muta genoma por sí mismo).
NO se vuelca:
- ruido conversacional (saludos, tanteos, razonamiento intermedio del agente);
- lo ya persistido: si la página existe, no se re-copia — a lo sumo se refuerza
  (`last_reinforced`, [[gen-frontmatter-obligatorio]]) y se enlaza;
- contenido literal de fuentes de `raw/` (eso es INGEST, no CHECKPOINT);
- secretos/credenciales; ante PII real sin anonimizar se DETIENE y pregunta, igual que
  INGEST ([[gen-confidencialidad]]).

## Pasos (deterministas e idempotentes)
1. **Volcado a working/** — crea o actualiza `wiki/working/<session_key>.md` (UNA nota por
   sesión; la separación fina en páginas propias la hará CONSOLIDATE) con frontmatter válido
   ([[gen-frontmatter-obligatorio]]): `type: observacion`, `tier: working`,
   `decay_rate: high`, `sources: ["sesion <session_key>"]`, `sensibilidad` = default del
   manifiesto ([[gen-confidencialidad]]), `confidence` inicial de fuente interna
   ([[gen-confianza-por-fuente]]); cuerpo = lo valioso, con `[[wiki-links]]` a las páginas
   que toca. En `relations` usa SOLO verbos del esquema vigente (núcleo ∪ `relation_types`
   del manifiesto): este gen no introduce verbos nuevos. Si no hubo nada valioso nuevo, este
   paso se omite (no nacen notas vacías).
2. **Episódico** — crea o actualiza `wiki/episodic/<session_key>.md`: resumen de la sesión
   (qué se hizo, operaciones corridas, decisiones, pendientes), con `type: sesion`,
   `tier: episodic`, `clase: evento`, `fecha_evento` = fecha de la sesión, `decay_rate: high`
   ([[gen-clase-temporal]]: hecho fechado, no se refuerza).
3. **Anclas** — solo si nacieron páginas nuevas NO confidenciales, refresca en `index.md` las
   anclas de los tiers `working/` y `episodic/` (apuntan a lo más reciente); no se añade un
   ancla por nota: el índice se mantiene corto.
4. **Bitácora** — UNA línea en `log.md` bajo la fecha de hoy:
   `CHECKPOINT: <session_key> — N nota(s) a working/, episódico actualizado[, M candidato(s) a EVOLVE]`.
   Si ya existe la línea de esa clave, se actualiza en vez de duplicarse.

## Qué NO hace
No procesa `raw/` (eso es INGEST), no promueve de tier ni fusiona (eso es CONSOLIDATE — las
notas quedan en `working/` esperándolo), no clasifica fino a `semantic/`, no muta genoma
(deriva a [[gen-evolve]] + compuerta) y no borra nada. Falla elegante: si un paso no puede
completarse, persiste lo que sí pudo y lo declara en su línea de `log.md` — nunca deja la
sesión sin rastro.

## Criterio de hecho
Al terminar existen (a) 0..1 nota en `working/` y (b) el episódico de la sesión, ambos con
frontmatter válido; (c) anclas al día si hubo página nueva no confidencial; (d) exactamente
una línea en `log.md` para esa `session_key`. Re-ejecutar con la misma clave no crea archivos
ni líneas nuevas: actualiza.
```

### 2. Diff exacto de `CLAUDE.md`

Tres toques obligatorios (2a–2c) + uno opcional recomendado (2d). Cada bloque es texto exacto
del `CLAUDE.md` vigente (@ evaluación `810f24e` + backlog) → texto propuesto.

#### 2a. Tabla "Operaciones (gatillos)" — fila nueva entre `QUERY` y `LINT`

ANTES (dos filas contiguas existentes):

```markdown
| `QUERY <X>` | "busca / qué sabemos de" | Navega desde `index.md` por relaciones; responde citando páginas-fuente. |
| `LINT` | mantenimiento | Detecta huérfanos, contradicciones y páginas vencidas por `decay_rate`; propone y aplica tras OK. |
```

DESPUÉS (se inserta la fila `CHECKPOINT` entre ambas):

```markdown
| `QUERY <X>` | "busca / qué sabemos de" | Navega desde `index.md` por relaciones; responde citando páginas-fuente. |
| `CHECKPOINT` | "checkpoint" / el agente lo propone ante contexto largo o cierre de sesión sin hooks | Implementación manual portable del loop de memoria: vuelca lo valioso no persistido a `wiki/working/`, actualiza el episódico de la sesión, refresca anclas si nacieron páginas y deja línea en `log.md`. Idempotente por clave de sesión (re-ejecutar actualiza, no duplica). Regla: [[gen-checkpoint]]. |
| `LINT` | mantenimiento | Detecta huérfanos, contradicciones y páginas vencidas por `decay_rate`; propone y aplica tras OK. |
```

#### 2b. "Índice de genes activos" — sección **Operativos**

ANTES:

```markdown
- [[gen-onboard]] · [[gen-ingest]] · [[gen-bulk-ingest]] · [[gen-query]] · [[gen-lint]] · [[gen-consolidate]] · [[gen-evolve]] · [[gen-auto-auditoria]] · [[gen-graph-lens]]
```

DESPUÉS (se añade `gen-checkpoint` tras `gen-query`, mismo orden que la tabla):

```markdown
- [[gen-onboard]] · [[gen-ingest]] · [[gen-bulk-ingest]] · [[gen-query]] · [[gen-checkpoint]] · [[gen-lint]] · [[gen-consolidate]] · [[gen-evolve]] · [[gen-auto-auditoria]] · [[gen-graph-lens]]
```

#### 2c. Sección "Loop de memoria infinita (hooks)" — pasa a contrato multi-implementación

ANTES (sección completa):

```markdown
## Loop de memoria infinita (hooks)
Declarados en `.claude/settings.json` (hoy stubs; ver `.claude/hooks/README.md`):
- `SessionStart` → carga index + log reciente + genes activos.
- `PreCompact` → antes de compactar, vuelca lo valioso a `wiki/working/` (memoria infinita).
- `Stop` → escribe resumen episódico + corre `EVOLVE` en modo propuesta.
```

DESPUÉS (sección completa; las 3 viñetas de hooks se conservan tal cual, anidadas):

```markdown
## Loop de memoria infinita (contrato multi-implementación)
El loop (volcar lo valioso antes de perderlo → cerrar con resumen episódico) es un **contrato
del genoma** con implementaciones intercambiables que cumplen las mismas postcondiciones:
- **Automática — hooks de Claude Code**, declarados en `.claude/settings.json` (hoy stubs; ver `.claude/hooks/README.md`):
  - `SessionStart` → carga index + log reciente + genes activos.
  - `PreCompact` → antes de compactar, vuelca lo valioso a `wiki/working/` (memoria infinita).
  - `Stop` → escribe resumen episódico + corre `EVOLVE` en modo propuesta.
- **Manual portable — operación `CHECKPOINT`** ([[gen-checkpoint]]): cualquier agente que lea
  `AGENTS.md` la ejecuta sin hooks ni harness específico. Hooks y CHECKPOINT comparten la
  clave de idempotencia: sobre la misma sesión actualizan los mismos archivos, no duplican.
```

Nota de aplicación: si A-02 (hooks reales) aterrizó primero y cambió la frase "(hoy stubs;
ver `.claude/hooks/README.md`)", conservar SU redacción de esa línea y solo envolver las tres
viñetas bajo la viñeta "Automática" + añadir la viñeta "Manual portable".

#### 2d. (Opcional, recomendado) "Mapa de la memoria (tiers de `wiki/`)" — coherencia

ANTES:

```markdown
- `working/` — observaciones recientes, `decay_rate: high`. Lo que el hook `PreCompact` vuelca aquí.
- `episodic/` — resúmenes por sesión (los escribe el hook `Stop`).
```

DESPUÉS:

```markdown
- `working/` — observaciones recientes, `decay_rate: high`. Lo que el hook `PreCompact` o un `CHECKPOINT` vuelca aquí.
- `episodic/` — resúmenes por sesión (los escribe el hook `Stop` o un `CHECKPOINT`).
```

Sin 2d, `CLAUDE.md` seguiría implicando que solo los hooks alimentan esos tiers. Es un cambio
de dos palabras por línea; si el operador lo rechaza, el resto de la propuesta no se ve
afectado.

### 3. Re-sincronización de `AGENTS.md`

Paso obligatorio de [[gen-compuerta-mutacion]] (punto 4): tras aplicar los diffs de
`CLAUDE.md`, `AGENTS.md` se regenera como copia exacta. No es un cambio adicional que decidir:
es parte mecánica de la aplicación.

## Compatibilidad e impacto

**Compone con (sin editar el texto de ningún gen existente):**
- [[gen-frontmatter-obligatorio]] — las notas y episódicos nacen con frontmatter válido. El
  gen NO introduce verbos de relación nuevos (evita deliberadamente la clase de contradicción
  latente de esquema que el panel señaló en otros genes: verbos exigidos fuera de la unión que
  LINT valida).
- [[gen-confidencialidad]] — `sensibilidad` = default del manifiesto; PII-halt idéntico al de
  INGEST; lo confidencial no se ancla (el paso 3 lo respeta: en despliegues salud/legal con
  `default_sensibilidad: confidencial`, las notas de sesión nacen sin ancla).
- [[gen-clase-temporal]] — el episódico es `clase: evento` con `fecha_evento` (hecho fechado,
  no se refuerza).
- [[gen-confianza-por-fuente]] — la sesión cuenta como fuente interna para la `confidence`
  inicial (usa el `source_trust` del manifiesto; no inventa números propios).
- [[gen-consolidate]] — consumidor aguas abajo: promueve/fusiona/decae lo que CHECKPOINT dejó
  en `working/`. CHECKPOINT no promueve (frontera de responsabilidad limpia).
- [[gen-evolve]] + [[gen-compuerta-mutacion]] — los patrones detectados en sesión se derivan a
  EVOLVE en modo propuesta; la operación en sí jamás muta genoma.
- [[gen-visualizacion]] — los dashboards leen `working/`/`episodic/` vía frontmatter estándar;
  sin cambios.

**No choca con:** [[gen-ingest]] / [[gen-bulk-ingest]] (CHECKPOINT no toca `raw/` ni crea
páginas semánticas), [[gen-raw-inmutable]], [[gen-auto-auditoria]] (las notas de checkpoint
son páginas wiki normales, auditables por AUDIT/LINT).

**Coordinación con tareas paralelas del backlog:**
- **A-02 (hooks reales)** — los hooks son la implementación AUTOMÁTICA de este mismo
  contrato. Estado observado al redactar (scripts de A-02 ya en el árbol de trabajo):
  `stop.sh` usa `wiki/episodic/<YYYY-MM-DD>-<session8>.md` — coincide con la clave de este
  gen (fecha + id de sesión como slug); `pre-compact.sh` usa
  `wiki/working/<YYYY-MM-DD>-precompact-<session8>.md`, con infijo `precompact-`. La
  divergencia la absorbe la **regla de adopción** del gen (CHECKPOINT actualiza la nota
  automática existente de la misma sesión en vez de crear otra): no se requiere ningún cambio
  en los archivos de A-02. Ver criterio de aceptación 6.
- **A-05 (umbrales numéricos)** — este gen se ancla cualitativamente a decay/confidence; los
  números los fijará A-05 sin necesidad de tocar este gen.
- **A-06 (jerarquización del índice)** — el paso 3 solo refresca las anclas de tier (no añade
  un ancla por nota); compatible con cualquier política de hubs que A-06 defina.
- **`type` nuevos** (`observacion`, `sesion`) — no requieren declaración en el manifiesto: no
  son `document_types` de fuentes sino tipos del loop de memoria, y LINT no valida `type`
  contra un set cerrado (valida relaciones y campos), así que no generan falsos positivos.

**Migración ([[gen-migracion-genoma]]):** wiki vacía pre-ONBOARD → no hay páginas que
re-validar. La migración se reduce a verificar la sincronía `AGENTS.md` ≡ `CLAUDE.md` y que el
índice de genes lista el gen nuevo. Ningún manifiesto ni blueprint necesita campos nuevos.

## Línea draft para `genome/events.jsonl`

Lista para pegar al aprobar (append al final del archivo, nunca reescribiendo líneas previas).
Ajustar `ts` a la fecha real de aprobación si no es 2026-07-02:

```json
{"ts":"2026-07-02","type":"gene_added","target":"gen-checkpoint","signal":"evaluacion 2026-07-01-810f24e (backlog A-03): loop de memoria dependiente de hooks stub de un solo vendor; perdida de conocimiento en compactacion hoy garantizada; falta implementacion manual portable del contrato","diff":"∅ -> gen-checkpoint v1 (operacion CHECKPOINT: volcado idempotente por clave de sesion de lo valioso a wiki/working/ + episodico + anclas + linea en log.md; contrato multi-implementacion compartido con los hooks) + fila CHECKPOINT y loop como contrato en CLAUDE.md","approved_by":"user","status":"applied"}
```

Mismo esquema de claves que las 29 líneas existentes (`ts`, `type`, `target`, `signal`,
`diff`, `approved_by`, `status`); `type: gene_added` como en gen-graph-lens (línea 24), sin
acentos en los valores, como las entradas recientes.

## Criterios de aceptación (comprobables tras aplicar)

1. `genome/genes/gen-checkpoint.md` existe con el texto exacto de §Cambios 1 (frontmatter
   `id: gen-checkpoint`, `status: active`, `version: 1`).
2. `CLAUDE.md` contiene: (a) la fila `CHECKPOINT` en la tabla de Operaciones entre `QUERY` y
   `LINT`; (b) `[[gen-checkpoint]]` en el índice de genes, sección Operativos; (c) la sección
   "Loop de memoria infinita (contrato multi-implementación)" con las dos implementaciones;
   (d) si se aceptó 2d, las menciones en el mapa de memoria. Sanidad:
   `grep -c "gen-checkpoint" CLAUDE.md` ≥ 3.
3. **`AGENTS.md` re-sincronizado** como copia exacta de `CLAUDE.md` (paso 4 de la compuerta):
   `diff AGENTS.md CLAUDE.md` sin salida (o `cmp -s` con exit 0).
4. `genome/events.jsonl`: la línea draft añadida por APPEND al final (`git diff` muestra solo
   la línea nueva; ninguna previa reescrita) y cada línea del archivo sigue parseando como
   JSON (`python -m json.tool` línea a línea o equivalente).
5. Un único commit contiene gen + `CLAUDE.md` + `AGENTS.md` + `events.jsonl`, y `log.md`
   registra la mutación con el estilo de la casa
   (`EVOLVE: gen-checkpoint v1 (nuevo) + operación CHECKPOINT — ... Ver genome/events.jsonl.`).
6. Contrato compartido con A-02: para una misma sesión NUNCA existen dos notas de working ni
   dos episódicos (hooks + CHECKPOINT convergen en los mismos archivos). Verificable leyendo
   `.claude/hooks/` (el episódico ya coincide: `<fecha>-<session8>.md`) y, en vivo, con el
   smoke del criterio 7 en una sesión con hooks activos.
7. Smoke funcional (opcional, post-aplicación): correr `CHECKPOINT` dos veces en la misma
   sesión de prueba → la segunda corrida no crea archivos nuevos ni una segunda línea en
   `log.md` para la misma clave; solo actualiza.

## Riesgos y alternativas consideradas

**Riesgos**
1. *Doble escritura hooks + manual* → mitigado por la clave de idempotencia compartida más la
   regla de adopción (CHECKPOINT actualiza el artefacto automático existente de la misma
   sesión; criterio 6, cruzado con A-02). Residual: nombres de hook futuros no anticipados —
   la regla de adopción es por sesión, no por nombre, así que lo cubre.
2. *"Valioso" sigue siendo juicio del LLM* → mitigado con lista cerrada de criterios y
   anti-criterios en el gen; el residual (la prosa varía entre corridas) es el mismo trade-off
   ya aceptado en todo el genoma: reproducible en estructura, no en bit.
3. *Crecimiento de `working/` y del índice* → contenido por diseño: una nota por sesión,
   anclas de tier fijas (no una por nota); el decaimiento/promoción es de CONSOLIDATE y A-05
   lo cuantificará.
4. *Fuga de sensible vía nota de sesión* → hereda `default_sensibilidad` + PII-halt; lo
   confidencial no se ancla. Mismo perímetro que INGEST.
5. *El paso 4 edita una línea existente de `log.md`* (cuando se re-ejecuta con la misma
   clave), lo que roza el estilo "una línea por operación" → decisión consciente: idempotencia
   antes que cronología duplicada; el registro duro (`events.jsonl`) no se toca nunca.

**Alternativas consideradas**
- (a) *Solo hooks (A-02), sin gen* — rechazada: mantiene el lock-in suave al vendor señalado
  por el panel; el hallazgo pide un contrato portable que viaje en `AGENTS.md`.
- (b) *Absorber el volcado en CONSOLIDATE* — rechazada: mezcla captura de sesión con
  mantenimiento quincenal; el momento del volcado es "antes de perder el contexto", no "cuando
  toque mantenimiento".
- (c) *Cápsula en vez de gen* — rechazada: las cápsulas componen genes para workflows de
  ingesta; CHECKPOINT es una operación de primer nivel con gatillo propio (como AUDIT/GRAPH) y
  debe estar en la tabla de operaciones.
- (d) *Una página por observación en vez de una nota por sesión* — rechazada por ahora:
  reintroduce el problema abierto de identidad/slug de página (lo ataca A-04); la nota única
  por clave es determinista hoy y CONSOLIDATE hace la separación fina después.
- (e) *Registrar cada checkpoint en `events.jsonl`* — rechazada: `events.jsonl` registra SOLO
  mutaciones de genoma; el rastro operativo de CHECKPOINT va a `log.md`, como el de
  INGEST/QUERY.
