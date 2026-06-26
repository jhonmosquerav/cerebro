---
run_id: 2026-06-25-f5c6000
role: auditor
date: 2026-06-25
gene_version: gen-auto-auditoria v1
candidates_received: 5
confirmed: 5
refuted: 0
---

# Auditoría independiente — AUDIT 2026-06-25-f5c6000

Rol: AUDITOR (pasada fresca). Insumos únicos: `00-snapshot.md`, `gen-auto-auditoria.md`,
`10-maker.md` y los archivos fuente de `sim/agencia/` citados por cada candidato.
No se leyó ningún otro escenario `sim/<otro>/`. Nada fue modificado fuera de `sim/agencia/`.
Confidencialidad verificada: ninguna página tiene `sensibilidad: confidencial`; el maker no
transcribió valores sensibles — limpio.

---

## C1 — Precio vencido

**Veredicto: CONFIRMED**

**Re-derivación desde fuente:**
`sim/agencia/wiki/semantic/precios/precio-vertice-PROP-2026-038.md` leído directamente:
`valido_hasta: 2026-06-14`. Hoy 2026-06-25. Vencido 11 días. La página tiene advertencia
inline propia, pero `propuesta-vertice-PROP-2026-038.md` — que lleva `define_precio` en
relaciones apuntando a este precio — no tiene ningún campo `advertencia` ni repite el
aviso. `lead-inmobiliaria-vertice.md` conserva `estado: en-negociacion` sin ningún campo
que propague el vencimiento del precio. El defecto re-deriva exactamente como el maker lo
describe.

**Scores auditados:**

| Campo | Maker | Auditor | Coincide |
|---|---|---|---|
| clase | info vencida en dominio de seguridad | info vencida en dominio de seguridad | si |
| severidad | 5 | 5 | si |
| alcance | 3 | 3 | si |
| impacto | 53 | 53 | si |

**Nota**: el alcance 3 es correcto: `precio-vertice-PROP-2026-038` (fuente del vencimiento),
`propuesta-vertice-PROP-2026-038` (no advierte al lector), `lead-inmobiliaria-vertice`
(estado operativo no refleja precio caído). Tres páginas reales con el defecto.

---

## C2 — Follow-up vencido con estado operativo inconcluso

**Veredicto: CONFIRMED**

**Re-derivación desde fuente:**
`sim/agencia/wiki/working/followup-vertice-2026-05-16.md` leído directamente:
`fecha_objetivo: 2026-05-16`, `estado: vencido`. Hoy 2026-06-25 = 40 días de retraso.
`lead-inmobiliaria-vertice.md`: `estado: en-negociacion`; el cuerpo dice "decisión en
junta del lunes 2026-05-19" — ese hito ya tiene 37 días de antigüedad sin actualización.
El campo `tiene_followup: ["[[followup-vertice-2026-05-16]]"]` enlaza un artefacto vencido
sin señalizar ese estado al nivel del lead. Un QUERY sobre este lead devuelve `en-negociacion`
como si el proceso estuviera vivo. El defecto re-deriva exactamente.

**Scores auditados:**

| Campo | Maker | Auditor | Coincide |
|---|---|---|---|
| clase | info vencida en dominio de seguridad | info vencida en dominio de seguridad | si |
| severidad | 5 | 5 | si |
| alcance | 2 | 2 | si |
| impacto | 52 | 52 | si |

---

## C3 — Vacío de categoría: `onboarding-cliente` sin ninguna página

**Veredicto: CONFIRMED**

**Re-derivación desde fuente:**
`sim/agencia/company.yaml` leído directamente: `taxonomy.procedural: [sops-ventas,
onboarding-cliente]`. Glob sobre `sim/agencia/wiki/procedural/**/*` retorna exactamente
un archivo: `sops-ventas/sop-calificacion-y-cierre.md`. El directorio `onboarding-cliente`
no existe. Ninguna página del wiki enlaza hacia ese directorio. El defecto re-deriva.

**Scores auditados:**

| Campo | Maker | Auditor | Coincide |
|---|---|---|---|
| clase | vacío (categoría sin cobertura) | vacío (categoría sin cobertura) | si |
| severidad | 2 | 2 | si |
| alcance | 1 | 1 (ver nota) | si con aclaración |
| impacto | 21 | 21 | si |

**Nota de alcance**: la rúbrica define alcance como "nº de páginas/genes afectados". Para
un vacío puro, el conteo literal de páginas existentes es 0. El maker usó alcance=1
contando la categoría como unidad — interpretación defensible, pero la rúbrica no lo
especifica. Mantengo alcance=1 por coherencia con el maker y porque la categoría declarada
en el manifiesto es la unidad afectada. Esto es una fricción del gen (ver sección de
fricciones).

---

## C4 — Asimetría en relaciones lead-cliente (trazabilidad incompleta)

**Veredicto: CONFIRMED — con matiz en la clasificación**

**Re-derivación desde fuente:**
`sim/agencia/genome-applied/gen-lead-a-cliente.md` leído directamente: "Todo el historial
del lead (calls, objeciones encontradas, propuesta origen) se conserva y **se enlaza desde
el cliente con `[[wiki-links]]`**". Este es el invariante exigido por el gen.

`lead-dental-sonrisa.md`: `usa: ["[[objecion-bot-malo]]"]`; cuerpo menciona "Propuesta
origen: PROP-2026-019". `reemplaza_por: ["[[cliente-dental-sonrisa]]"]` — correcto.

`cliente-dental-sonrisa.md`: tiene `proviene_de: ["[[lead-dental-sonrisa]]"]` (correcto).
El bloque `relations` NO contiene ninguna relación estructurada hacia `objecion-bot-malo`
ni hacia PROP-2026-019. El cuerpo dice "historial y objeciones del lead se conservan y
enlazan aquí" — esta afirmación propia de la página contradice lo que el bloque de
relaciones efectivamente contiene (no hay enlace estructurado hacia la objeción ni hacia
la propuesta origen). La contradicción es entre lo que la página declara en prosa y lo
que su estructura de relaciones materializa: defecto confirmado.

**Matiz sobre la clase**: "contradicción entre páginas wiki" (sev 4) es la clase más cercana
disponible en la rúbrica actual. Técnicamente el defecto es una "violación de invariante
de gen" — la regla del gen exige el enlace estructurado, la página no lo cumple — pero
esa clase no existe en la rúbrica. Bajo la regla de asignar la clase de mayor severidad
que aplique, "contradicción entre páginas wiki" (la página afirma que enlaza, pero no lo
hace) es la asignación correcta dentro del esquema vigente.

**Scores auditados:**

| Campo | Maker | Auditor | Coincide |
|---|---|---|---|
| clase | contradicción entre páginas wiki | contradicción entre páginas wiki | si (con matiz) |
| severidad | 4 | 4 | si |
| alcance | 2 | 2 | si |
| impacto | 42 | 42 | si |

---

## C5 — Near-duplicado funcional: `n8n` y `Make`

**Veredicto: CONFIRMED — marginalmente**

**Re-derivación desde fuente:**
`make.md` leído: "Cumple el mismo rol que [[n8n]]; la elección depende del proyecto."
`n8n.md` leído: "Alternativa a [[Make]] según el proyecto." Tags idénticos:
`[herramienta, orquestacion, automatizacion]`. Mismo `type: entidad`, `tier: semantic`,
`decay_rate: low`.

El defecto de near-duplicado por rol/tags re-deriva según gen-consolidate. Apunte
adversarial: los dos artefactos tienen `usado_por` hacia clientes/proyectos **distintos**
(`Make` → Dental Sonrisa; `n8n` → Vértice propuesta). No son duplicados de hecho, sino
alternativas en uso paralelo. Sin embargo, la ausencia de una página de síntesis o campo
`group` crea una brecha real: si se agrega contenido diferencial a cada una (precios,
limitaciones, versiones), el riesgo de contenido divergente es real y detectable por
gen-consolidate. El defecto es genuino aunque más débil que los anteriores.

**Scores auditados:**

| Campo | Maker | Auditor | Coincide |
|---|---|---|---|
| clase | redundancia (duplicado) | redundancia (duplicado) | si |
| severidad | 2 | 2 | si |
| alcance | 2 | 2 | si |
| impacto | 22 | 22 | si |

---

## Tabla de veredictos

| id | clase | sev | alcance | impacto_maker | impacto_auditor | veredicto |
|---|---|---|---|---|---|---|
| C1 | info vencida en dominio de seguridad | 5 | 3 | 53 | 53 | CONFIRMED |
| C2 | info vencida en dominio de seguridad | 5 | 2 | 52 | 52 | CONFIRMED |
| C4 | contradicción entre páginas wiki | 4 | 2 | 42 | 42 | CONFIRMED |
| C5 | redundancia (near-duplicado) | 2 | 2 | 22 | 22 | CONFIRMED |
| C3 | vacío (categoría sin cobertura) | 2 | 1 | 21 | 21 | CONFIRMED |

**Confirmados: 5 / 5. Refutados: 0 / 5.**
**Correcciones de score vs maker: ninguna.** Todos los scores re-derivan idénticos.
**Confidencialidad: limpia.** Ninguna página `sensibilidad: confidencial`; el maker no
transcribió valores sensibles.

Top-3 por impacto para `30-proposals.md`: **C1 (53), C2 (52), C4 (42)**.

---

## Fricciones del gen (afinación) — perspectiva del auditor

### F-A1. Clase "dominio de seguridad" mal nombrada para sectores no-IT
La rúbrica nombra la clase de mayor severidad "info vencida en dominio de seguridad". En
el contexto de una agencia de ventas, el dominio de riesgo alto no es seguridad IT sino
precios y hitos comerciales. El gen hereda nomenclatura de seguridad informática que resulta
confusa cuando el auditor debe decidir si un precio vencido o un follow-up muerto califican.
En este run, ambos (C1 y C2) lo califican correctamente, pero la ambigüedad requirió
interpretación. Señal de afinación: renombrar la clase a "info vencida en dominio de alto
riesgo operativo" o añadir en el gen ejemplos de dominios equivalentes por sector (precios,
SLAs, hitos de decisión, credenciales de acceso). Cambio de nombre de clase = subir
`version` del gen.

### F-A2. Ausencia de clase "violación de invariante de gen"
C4 no es estrictamente una "contradicción entre páginas wiki": es que una página no cumple
la obligación impuesta por un gen activo (`gen-lead-a-cliente`). La clase actual de mayor
severidad disponible (sev 4) se usa por aproximación, no por encaje exacto. Una clase
"violación de invariante de gen" (¿sev 4 o 5?) haría la detección más precisa y evitaría
que el auditor deba inferir la clase más cercana. La falta también impide que el detector
de genoma de AUDIT genere este candidato directamente — hoy lo genera el detector LINT
(campos/relaciones faltantes), lo que es una asignación indirecta.

### F-A3. Alcance de "vacío" — ambigüedad en la rúbrica
La rúbrica define `alcance` como "nº de páginas/genes afectados". Para la clase "vacío",
ninguna página existe aún, por lo que el conteo literal es 0. Esto hace el impacto = 2*10+0
= 20, en lugar de 21. El maker usó alcance=1 (contando la categoría declarada en el
manifiesto como unidad). Mantengo esa decisión como la más defensible, pero la rúbrica
debería especificar: para vacíos, alcance = nº de categorías/entidades declaradas sin
cobertura. Eso fija el comportamiento y hace el score determinista.

### F-A4. Near-duplicado vs alternativas en uso paralelo — umbral no especificado
C5 (n8n/Make) es un near-duplicado por rol/tags pero ambas páginas tienen `usado_por`
apuntando a proyectos distintos. La rúbrica no especifica si "páginas distintas con rol
funcional idéntico pero uso real diferenciado" califican como redundancia. El auditor
confirmó el defecto porque el riesgo de divergencia futura es real, pero otro auditor
podría refutarlo argumentando que son alternativas legítimas con usos diferenciados. El gen
debería aclarar: "near-duplicado aplica aunque las páginas tengan usos distintos si
comparten rol, tags y estructura" (o lo contrario).

### F-A5. El maker identificó la misma fricción de relaciones ad-hoc (F-A3 del maker)
El maker señaló que `relation_types` no está declarado en el manifiesto. El auditor
confirma esta observación como fricción real: verbos como `recibio_propuesta`,
`tiene_followup`, `usado_por` aparecen en los frontmatters pero no están en ningún
`relation_types` del `company.yaml`. El gen-lint debería poder validar esto, pero sin la
lista canónica en el manifiesto, no hay base de comparación. Esta fricción se hereda y
confirma — no es un candidato AUDIT en este run (no hay contradicción activa entre genes)
pero es señal para un futuro EVOLVE sobre gen-lint o sobre el esquema del manifiesto.
