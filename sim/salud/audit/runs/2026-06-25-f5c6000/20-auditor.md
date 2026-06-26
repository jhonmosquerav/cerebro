---
run_id: 2026-06-25-f5c6000
scenario: salud
role: auditor
date: 2026-06-25
gen_version: gen-auto-auditoria v1
insumos: [00-snapshot.md, gen-auto-auditoria.md, 10-maker.md]
candidatos_maker: 3
confirmados: 3
---

# 20-auditor — Veredictos de auditoría (Clínica Vida Serena)

> Pasada Auditor. Insumos: `00-snapshot.md` + `gen-auto-auditoria.md` + `10-maker.md`.
> Verificación independiente — re-deriva cada candidato desde el corpus fuente.

---

## Preámbulo: metodología

El Auditor re-derivó cada candidato directamente desde las páginas wiki de `sim/salud/`
(no desde la memoria del Maker). La re-derivación es por inspección de frontmatter +
relaciones de cada página afectada. Después, se contrasta con `10-maker.md` para
confirmar, refutar o corregir. El punto central de mayor escrutinio — la definición de
`alcance` en CAND-01 — se trata en profundidad antes de los veredictos individuales.

---

## Cuestión transversal: ¿el alcance debe incluir páginas que referencian al defecto?

### Texto canónico del gen

El gen-auto-auditoria v1 define:

> `impacto = severidad*10 + alcance`. `alcance` = nº de páginas/genes afectados.

"Afectados" no se define explícitamente. El gen solo añade que "la identidad de cada
candidato (qué página/gen, qué clase) la fija el detector". Esto produce ambigüedad:

- **Lectura estrecha**: solo la página que porta el defecto primario (el protocolo vencido
  en sí). Alcance = 1. Impacto = 5×10 + 1 = **51**.
- **Lectura de propagación**: la página defectuosa + toda página con relación tipada de
  primer nivel que apunta a ella sin advertir la caducidad. Esta es la lectura que adoptó
  el Maker. Alcance = 5 (protocolo + anafilaxia + adrenalina + PAC-7731 + INC-2026-014).

### Posición del Auditor: **la lectura de propagación es rúbrica-fiel y debe mantenerse**

La rúbrica dice "páginas **afectadas**". La clase asignada es "info vencida en **dominio
de seguridad**". Una página está "afectada" por el defecto si cualquier agente que
navegue el grafo a través de esa página puede ser inducido a confiar en información
vencida sin advertencia suficiente. Criterio de re-derivación:

| página | relación a protocolo-vencido | ¿advertencia inline? | ¿afectada? |
|---|---|---|---|
| [[protocolo-anafilaxia]] | es la página defectuosa (status: vencido) | sí — ⚠️ en cuerpo | SÍ — defecto primario |
| [[anafilaxia]] | `tratada_segun` → protocolo vencido | parcial — nota ⚠️ inline pero `confidence: 0.9` sin degradar | SÍ |
| [[adrenalina]] | `indicado_por` → protocolo vencido | NO — ninguna advertencia; `confidence: 0.92` sin tocar | SÍ — mayor riesgo |
| [[PAC-7731]] | `segun_protocolo` → protocolo vencido | ⚠️ inline presente | SÍ — pero confidencial (ver discusión) |
| [[INC-2026-014]] | `afecta_a` → protocolo vencido; `estado: abierto` | NO es advertencia sino registro activo de problema | SÍ — agrava el defecto |

Re-derivación confirma alcance = 5 con un matiz: [[adrenalina]] NO tiene ninguna
advertencia sobre el protocolo vencido (a diferencia de [[anafilaxia]] y [[PAC-7731]]),
lo que lo hace el satélite de mayor riesgo. Esto fortalece la inclusión en alcance.

### Sobre páginas confidenciales en el alcance

[[PAC-7731]] tiene `confidential: true`. El gen-auto-auditoria v1 hereda
`gen-confidencialidad` y dice: "para páginas `sensibilidad: confidencial` la evidencia
se expresa por `[[link]]`/id + campo, NUNCA transcribiendo el valor sensible". La norma
rige la **evidencia** (cómo se cita), no el **conteo de alcance**. La rúbrica dice
"nº de páginas/genes afectados" sin excluir las confidenciales del conteo. Por lo tanto:

- **Incluir [[PAC-7731]] en el conteo de alcance es correcto bajo la rúbrica vigente.**
- La evidencia sobre [[PAC-7731]] debe referirse solo por id + campo (`segun_protocolo`),
  nunca por valor sensible. El Maker cumplió esto. El Auditor mantiene la misma práctica.

**Conclusión sobre CAND-01 alcance:** alcance = 5 es rúbrica-fiel. El Maker no inflated el número. El score Maker de 55 es correcto. El Auditor lo confirma sin corrección.

---

## CAND-01 — Protocolo clínico vencido sin reemplazo (dominio de seguridad)

**Veredicto: CONFIRMADO. Score Auditor: 55 (sin variación).**

### Re-derivación independiente

Verificación directa de `protocolo-anafilaxia.md`:
- `valid_until: 2026-03-01` → hoy 2026-06-25 → **116 días vencido**. Verificado.
- `status: vencido`. Verificado.
- `reemplaza: []` → sin v4. Verificado.
- `confidence: 0.55` (degradado). Verificado.
- `decay_rate: high`. Verificado — la clase "info vencida en dominio de seguridad" aplica.

`gen-vigencia-protocolo` establece explícitamente: "[[gen-lint]] señala cualquier
protocolo `status: vencido` aún sin reemplazo como **hallazgo de seguridad prioritario**".
Este es exactamente el estado del protocolo. El detector LINT habría marcado este defecto.

El incidente [[INC-2026-014]] tiene `estado: abierto` y ninguna acción correctiva tiene
fecha de cierre ni responsable asignado (verificado en la página fuente). Esto agrava
el defecto pero no cambia la clase ni la severidad dentro de la rúbrica v1.

### Corrección al diff del Maker

El diff propuesto en `10-maker.md` es operativamente correcto pero el Auditor señala
que el campo sugerido `responsable_accion_2` no existe en el schema del frontmatter de
`INC-2026-014.md` (ni del scenario). El diff es una propuesta de hoja de ruta, no un
cambio de schema — esto es aceptable como diff de propuesta pero debe marcarse como
fuera de schema existente.

### Score recomputado

| campo | Maker | Auditor | delta |
|---|---|---|---|
| severidad | 5 | 5 | 0 |
| alcance | 5 | 5 | 0 |
| impacto | 55 | **55** | 0 |

---

## CAND-02 — Contradicción de relación tipada en la tríada clínica

**Veredicto: CONFIRMADO. Score Auditor: 42 (sin variación).**

### Re-derivación independiente

`gen-trazabilidad-clinica` define el schema canónico:
- el **fármaco** lleva `tratamiento_de` → patología ✅
- la **patología** lleva `tratada_segun` → protocolo ✅
- la **patología** NO lleva `tratamiento_de` (no existe ese verbo en el esquema de patología)

Verificación directa de `anafilaxia.md` frontmatter:
```
relations:
  tratada_segun: ["[[protocolo-anafilaxia]]"]
  tratamiento_de: ["[[adrenalina]]"]   ← CAMPO EXTRA NO CANÓNICO
```

Verificación directa de `adrenalina.md` frontmatter:
```
relations:
  tratamiento_de: ["[[anafilaxia]]"]   ← correcto
```

El resultado es que el grafo contiene `tratamiento_de` tanto en `adrenalina.md`
(→ patología, correcto) como en `anafilaxia.md` (→ fármaco, incorrecto). Una query
sobre el verbo `tratamiento_de` sin filtrar por tipo de nodo devolvería ambas
entidades en ambas direcciones, creando ambigüedad semántica real.

La clase "contradicción entre páginas wiki" (severidad 4) es la correcta: dos páginas
expresan la misma relación con semantica inversa en el mismo tipo de verbo.

El diff propuesto (eliminar `tratamiento_de` de `anafilaxia.md`) es correcto, mínimo
e idempotente.

### Score recomputado

| campo | Maker | Auditor | delta |
|---|---|---|---|
| severidad | 4 | 4 | 0 |
| alcance | 2 | 2 | 0 |
| impacto | 42 | **42** | 0 |

---

## CAND-03 — Vacío de cobertura: entidades del manifiesto sin página wiki

**Veredicto: CONFIRMADO. Score Auditor: 27 (sin variación).**

### Re-derivación independiente

Verificación contra `company.yaml` (fuente de verdad del manifiesto) + glob del
directorio `sim/salud/wiki/`:

| entidad declarada en company.yaml | página wiki existente |
|---|---|
| protocolos: sepsis-adulto | NO |
| protocolos: dolor-toracico | NO |
| patologias: sepsis | NO |
| patologias: neumonia-adquirida-comunidad | NO |
| farmacos: amoxicilina-clavulanico | NO |
| farmacos: noradrenalina | NO |
| profesionales: dr-nunez-mi | NO |

Total: 7 entidades declaradas sin página. Coincide exactamente con el Maker.

`gen-trazabilidad-clinica` requiere que "toda ficha de fármaco enlaza al menos una
patología o protocolo; ninguna queda huérfana". Con amoxicilina-clavulanico y
noradrenalina sin página, la regla no puede verificarse — su ausencia es auditable
como vacío de cobertura.

`INC-2026-014.md` acción 4 menciona explícitamente dolor torácico y sepsis como
protocolos a auditar, lo que implica que podrían existir como fuentes en `raw/` sin
página wiki. Esto es coherente con el hallazgo.

Alcance = 7 entidades. Clase "vacío (link roto / categoría sin cobertura)", severidad 2.

### Score recomputado

| campo | Maker | Auditor | delta |
|---|---|---|---|
| severidad | 2 | 2 | 0 |
| alcance | 7 | 7 | 0 |
| impacto | 27 | **27** | 0 |

---

## Tabla resumen de veredictos

| id | clase | sev | alcance | impacto Maker | impacto Auditor | delta | veredicto |
|---|---|---|---|---|---|---|---|
| CAND-01 | info vencida en dominio de seguridad | 5 | 5 | 55 | **55** | 0 | CONFIRMADO |
| CAND-02 | contradicción entre páginas wiki | 4 | 2 | 42 | **42** | 0 | CONFIRMADO |
| CAND-03 | vacío (link roto / categoría sin cobertura) | 2 | 7 | 27 | **27** | 0 | CONFIRMADO |

**Confirmados: 3 / 3. Sin refutaciones. Sin correcciones numéricas.**

Ranking final (por impacto): CAND-01 (55) > CAND-02 (42) > CAND-03 (27).
Desempate no fue necesario — impactos distintos.

---

## Verificación de fuga de PII / datos confidenciales (leak-check)

**Método:** grep sobre todos los archivos bajo `sim/salud/audit/` con los siguientes
patrones: identificadores del paciente, valores clínicos privados (edad, sexo, alérgeno,
resultado de triaje, episodio numérico), nombres de persona.

**Patrones buscados:**
- Identificadores: `PAC-7731`, `EP-2026-0488`, `HC-EP`
- Valores clínicos de PAC-7731: `Femenino`, `34 años`, `frutos secos`, `alérgeno alimentario`, `Manchester`
- Nombres de persona con valor sensible: coincidencias de valores biográficos

**Resultado:**

Los archivos `00-snapshot.md` y `10-maker.md` contienen:
- `PAC-7731` y `EP-2026-0488` — únicamente como **identificadores seudonimizados** e
  **id de wiki** (`[[PAC-7731]]`), nunca como valores de dato personal. Estos son los
  IDs internos del sistema, no PII real.
- `enf-rivas` y `dra-soto-urg` — identificadores de profesionales (pseudónimos de rol),
  no datos biográficos.

**Ningún valor sensible de `PAC-7731.md` (sexo, edad, alérgeno, triaje, diagnóstico
concreto del episodio) aparece en ningún artefacto de `sim/salud/audit/`.** Los
identificadores seudonimizados son esperados y correctos según `gen-confidencialidad-paciente`
y `gen-auto-auditoria` (evidencia por [[link]]/id + campo).

**Veredicto de leak-check: LIMPIO. No hay fuga de PII ni de datos confidenciales
de paciente en ningún artefacto de auditoría.**

---

## Fricciones del gen (gen-auto-auditoria v1 — perspectiva adversarial del Auditor)

### 1. Sev-5 + incidente abierto: ¿debe escalar con un incidente vinculado?

**Fricción real. El Auditor difiere del Maker en la prescripción.**

El Maker propone como "propuesta de afinación" escalar severidad a 6 cuando existe un
incidente abierto vinculado. El Auditor considera esto insuficiente y más prescriptivo:

**La fricción concreta:** CAND-01 tiene severidad 5 y hay un incidente `INC-2026-014`
con `estado: abierto` explícitamente enlazado al defecto. El gen v1 no establece ningún
mecanismo de escalada ni de "open incident = action required". Un agente que vea el
candidato aprobado como propuesta `status: pending` no sabe que existe un incidente
activo ya abierto que debería cerrarse en paralelo o antes.

**Propuesta de fricción:** el gen debería añadir una regla operativa: cuando un
candidato de clase "info vencida en dominio de seguridad" (sev 5) tiene evidencia de un
incidente con `estado: abierto` vinculado al mismo defecto, la propuesta debe incluir
un campo `incident_ref` con el id del incidente, y el gate humano debe confirmar que el
incidente fue revisado antes de aprobar la propuesta. Esto no cambia el score (la rúbrica
es de impacto, no de proceso de cierre), pero añade una compuerta de seguridad operativa
que el gen actual no tiene.

**Nota:** el Auditor NO propone subir la severidad a 6 porque eso requeriría cambiar la
rúbrica versionada, lo que pasa por [[gen-compuerta-mutacion]]. La propuesta correcta
es añadir un campo de proceso, no escalar una clase.

### 2. ¿Las páginas confidenciales cuentan en el alcance?

**Fricción confirmada. El gen es ambiguo y debe aclararse.**

Como se analizó en la cuestión transversal: la rúbrica dice "nº de páginas/genes
afectados" sin distinguir `confidential: true`. Bajo la lectura textual, [[PAC-7731]]
cuenta en el alcance de CAND-01 (alcance = 5). El Auditor considera esto **correcto pero
no explícito** en el gen.

La ambigüedad tiene consecuencia: un Auditor con lectura estrecha podría excluir [[PAC-7731]]
del alcance (alcance = 4, impacto = 54 en lugar de 55), variando el ranking potencialmente
si hubiese candidatos con impacto 54. En este run el ranking no cambia, pero la inconsistencia
puede surgir en escenarios con scores más ajustados.

**Propuesta de fricción:** el gen debería añadir explícitamente: "Las páginas con
`confidential: true` se incluyen en el conteo de alcance (incrementan el impacto del
defecto); su evidencia se expresa solo por [[link]]/id + campo, nunca por valor sensible."

### 3. El gen no define "afectado" para el alcance de propagación

**Fricción técnica — ambigüedad estructural.**

Como se demostró en la cuestión transversal, la pregunta "¿qué páginas están afectadas?"
admite respuestas de alcance 1, 3, 4 o 5 según la interpretación de "primer nivel",
"sin advertencia", "con relación tipada", etc. El Maker adoptó la lectura de propagación
de primer nivel (razonable). El Auditor coincide. Pero el gen no lo prescribe.

**Propuesta de fricción:** definir en el gen: `alcance` para defectos de "info vencida
en dominio de seguridad" = (página defectuosa) + (páginas con relación tipada directa
que no tienen campo `status` de la referencia ni advertencia inline verificable). Esto
haría el alcance reproducible entre distintos agentes.

### 4. El gen usa `usa` e `indica` como verbos separados pero no resuelve coexistencia

**Fricción menor. El Maker la identificó correctamente.**

`protocolo-anafilaxia.md` tiene tanto `usa: ["[[adrenalina]]"]` como
`indica: ["[[adrenalina]]"]`. `gen-trazabilidad-clinica` define `indica` como el verbo
canónico. `usa` es un verbo genérico heredado del schema base. El gen no prohíbe la
coexistencia y LINT no la marca como contradicción. El resultado es redundancia semántica
no detectada automáticamente.

**Posición del Auditor:** no genera candidato porque el gen no lo clasifica como defecto
auditable (correcto: el Maker tampoco lo generó). Pero es una fricción real de afinación:
el gen debería especificar si `usa` se permite cuando ya existe `indica` para el mismo
nodo destino, o si LINT debe marcarlo como redundancia.

### 5. Sandbox sin SHA: el run-id no es derivable del estado de git del scenario

**Fricción de reproducibilidad.**

El gen define `run-id = <YYYY-MM-DD>-<short-SHA>` basado en `git rev-parse HEAD`. El
directorio `sim/salud/` no tiene su propio repositorio git (está dentro del repo
principal de CEREBRO). El snapshot indica "sandbox (no git SHA — sim/ aislado)". El
run-id fue dado por el orquestador, no derivado del estado.

**Consecuencia:** la idempotencia por SHA ("si ya existe runs/ para ese SHA, no se
duplica") no aplica aquí. Una re-ejecución del mismo scenario el mismo día podría
generar una segunda corrida con el mismo prefijo de fecha pero diferente sufijo.

**Propuesta de fricción:** el gen debería añadir: "En modo sandbox/sim sin SHA propio,
el run-id usa `<YYYY-MM-DD>-sim-<token-aleatorio>` y la idempotencia se verifica por
run-id, no por SHA."

---

## Candidatos confirmados: 3 / 3

Top-N para `30-proposals.md`: N = min(3, 3) = **3**.
Candidatos a promover: CAND-01, CAND-02, CAND-03 (en ese orden de prioridad).
