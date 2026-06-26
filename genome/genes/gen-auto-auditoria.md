---
id: gen-auto-auditoria
trigger: operación AUDIT (auto-auditoría de la base)
status: active
version: 3
---

AUDIT audita la propia base CEREBRO y PROPONE las **≤3 mejoras de mayor impacto**
(contradicciones, vacíos, reglas obsoletas o redundantes) de forma **reproducible**, con
separación maker≠auditor y gate humano. No aplica nada solo. No toca `raw/`.

## Disparador y meta
Disparador: invocación manual `AUDIT`. La corrida TERMINA solo cuando existe
`audit/runs/<run-id>/` con `00-snapshot`, `10-maker`, `20-auditor` y `30-proposals`, este
último con `N = min(3, candidatos confirmados por el auditor)` propuestas `status: pending`
(cada una con `id, fecha, motivo, evidencia, diff, score`), y hay una línea en `log.md`.

## Lectura en dos tiempos (respeta el presupuesto de contexto)
1. **Esqueleto:** lee solo frontmatter + grafo de relaciones de las páginas (no la prosa).
2. **Drill-down:** abre el contenido completo SOLO de las páginas que un detector marcó.

## Detección (reusa LINT + CONSOLIDATE; no la reimplementa)
- Huérfanos, contradicciones (`contradice`), vencidos (`valido_hasta < hoy` o `vigencia` por
  evento: derogada/en-revision/no-vigente), verbos/campos fuera de esquema → [[gen-lint]].
- Duplicados / near-duplicados → [[gen-consolidate]] (pares con `deriva_de`/`supersede`/`agregado_en`
  declarado quedan EXENTOS de redundancia; ver [[gen-consolidate]] v2).
- **Redundancia/obsolescencia de genoma (detector nuevo):** dos genes `active` con `trigger`
  solapado, o uno cuya regla quedó subsumida/contradicha por otro.
La **identidad** de cada candidato (qué página/gen, qué clase) la fija el detector; el LLM solo
juzga "¿importa?" y redacta el `diff`. Esto acota el no-determinismo a la prosa del diff.
Cada defecto produce UN solo candidato: si dos detectores marcan el mismo defecto sobre el
**mismo objeto** ("mismo defecto" = misma página/gen, NO misma causa raíz; p. ej. LINT ya anotó
`contradice`), se fusionan en un candidato; no se cuenta dos veces.

## Roles maker ≠ auditor (barrera en disco)
- **Maker:** insumos = `00-snapshot` + este gen. Produce TODOS los candidatos con evidencia +
  `diff` + score. Escribe `10-maker.md`.
- **Auditor:** pasada fresca; únicos insumos = `00-snapshot` + este gen + `10-maker.md` (NO la
  memoria de sesión). Refuta cada candidato, verifica que la evidencia re-deriva el hallazgo y
  recalcula el score. Escribe `20-auditor.md`.
- El orquestador ensambla `30-proposals.md` (≤3 confirmadas, rankeadas). Nunca juzga lo propio.
- Subagentes son optimización opcional; el canon portable es el hand-off en disco.

## Rúbrica de impacto (versionada con este gen)
`impacto = severidad*10 + alcance`. **`alcance` — conteo explícito y determinista por clase:**
- contradicción / redundancia: TODAS las páginas/genes en conflicto o duplicados.
- vencido / supersedido: la página/gen vencido + las páginas que lo CITAN operativamente (relación
  tipada de primer nivel); para obsolescencia de **genoma**, AMBOS genes del solape.
- vacío / verbo-o-campo fuera de esquema: 1 (la página/categoría/campo afectado).
- entidad con estado inconsistente / violación de invariante: la entidad + las páginas/eventos de
  respaldo implicados.
- Las páginas `sensibilidad: confidencial` SÍ cuentan en el número (su evidencia se cita solo por
  `[[link]]`/campo, nunca el valor — ver Confidencialidad).

`severidad` por clase de defecto (el orden de filas ES la prioridad canónica de desempate):
| Clase | severidad |
|---|---|
| contradicción entre genes activos | 5 |
| info vencida en dominio de seguridad | 5 |
| violación de invariante impuesta por un gen | 4 |
| entidad con estado inconsistente con su historial de eventos | 4 |
| contradicción entre páginas wiki | 4 |
| regla obsoleta/deprecable (gen del genoma) | 3 |
| conocimiento supersedido sin degradar tier/estado (página wiki) | 3 |
| vacío (link roto / categoría sin cobertura) | 2 |
| redundancia (duplicado) | 2 |
| verbo de relación / campo fuera de esquema | 2 |

**"Dominio de seguridad"** (califica la clase sev-5 de vencido) = seguridad física, salud, o
cumplimiento regulatorio con consecuencia legal. Fuera de esos dominios, la caducidad NO hereda
sev 5 (cae en la clase que corresponda: obsolescencia, supersedido, o vacío).
Desempate, en orden: (1) mayor `impacto`; (2) si empatan, prioridad de clase = el orden de
filas de la tabla de arriba a abajo (ese orden ES la prioridad canónica de clase); (3) si aún
empatan, ruta de archivo alfabética. Cada defecto pertenece a UNA sola clase: la de mayor
severidad que le aplique; **si varias clases de IGUAL severidad aplican, gana la que aparece
primero en la tabla** (orden de filas = prioridad de clase) — la elección de clase es determinista.
Top-N = las N de mayor impacto tras el desempate, con N = min(3, confirmadas por auditor).
Cambiar esta rúbrica = subir `version` = pasa por [[gen-compuerta-mutacion]].

## Estado, identidad y reproducibilidad
Identidad del estado: `git -C <raíz-cerebro> rev-parse HEAD` con árbol limpio (`git status`); si
está sucio, registra `HEAD + dirty` + lista de modificados. (El `-C <raíz>` da el mismo SHA aunque
AUDIT se corra desde un subdirectorio o sandbox.) `run-id = <YYYY-MM-DD>-<short-SHA>`. El orquestador crea `audit/runs/<run-id>/` si no existe.
Idempotente por SHA: si ya existe `runs/` para ese SHA, no se duplica. Todo insumo, criterio (esta `version`)
y salida queda en disco → la corrida se reconstruye y reaudita sin re-correr el LLM.

## Confidencialidad (hereda [[gen-confidencialidad]])
Los artefactos de auditoría se persisten y commitean: para páginas `sensibilidad: confidencial`
la evidencia se expresa por `[[link]]`/id + campo, NUNCA transcribiendo el valor sensible. Esto
aplica a **TODO el artefacto**: ni en la evidencia, ni en el `diff` propuesto (incluido su lado
"antes"), ni al describir el defecto se copia el valor. Si el defecto es "la página confidencial
contiene/expone X", se refiere X por **nombre de campo**, jamás por su valor.

## Gate humano y aplicación
Las ≤3 quedan `status: pending`. El humano aprueba/rechaza una por una. Un hallazgo sev-5 ligado a
un incidente abierto lleva además `incident_ref` en la propuesta (refuerza el gate, no lo reemplaza).
Aprobada que toca
genoma → por [[gen-compuerta-mutacion]] (events.jsonl + version + commit + re-sync `AGENTS.md`),
y tras aplicarla [[gen-migracion-genoma]] re-valida manifiesto y páginas;
que toca wiki → cambio directo + línea en `log.md` + commit. Revertir = `git revert` + marcar
`status: reverted`. AUDIT consume LINT/CONSOLIDATE y deriva a [[gen-evolve]] las propuestas de
regla; no reimplementa esas operaciones.
