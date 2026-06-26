---
run_id: 2026-06-25-f5c6000
role: orquestador
scenario: legal
date: 2026-06-25
gen_auditoria_version: 1
confirmed_by_auditor: 5
total_candidates: 6
top_n: 3
---

# 30-proposals — Propuestas de mejora (sandbox legal)

Ensambla los `min(3, confirmados)` = 3 candidatos de mayor impacto confirmados
por el auditor (`20-auditor.md`). Status `pending` — requieren aprobación humana
antes de aplicarse. Todas las referencias a páginas `secreto_profesional: true`
se expresan por `[[link]]`/id + campo. Ningún valor sensible transcrito.

---

## P1 — Campo `vigencia:` sin gen respaldo (C1)

| Campo | Valor |
|---|---|
| id | P1 |
| fuente | C1 |
| fecha | 2026-06-25 |
| status | approved |
| clase | contradicción entre páginas wiki (campo sin gen que lo defina ni valide) |
| severidad | 4 |
| alcance | 4 |
| score | **44** |

**Motivo:**
El campo `vigencia:` aparece en las páginas de normativa y jurisprudencia
(`vigente`, `en-revision`, `no-vigente`) pero no está definido en ningún gen
activo del sandbox (`genome-applied/` contiene solo `gen-secreto-profesional`,
`gen-version-contrato`, `gen-conflicto-interes`). El genoma base tampoco lo
define en el conjunto de genes del sandbox legal. Como consecuencia:

1. LINT no puede validar el campo (valores permitidos, obligatoriedad, semántica).
2. `art-1124-codigo-civil.md` no tiene el campo mientras las otras tres páginas
   de normativa/jurisprudencia sí lo tienen: asimetría de esquema.
3. Una página con `vigencia: derogada` o `vigencia: en-revision` pasaría
   desapercibida para cualquier detector automático.

**Evidencia:**
- [[reforma-cc-2026]] — campo: `vigencia` (valor `no-vigente`)
- [[art-1154-codigo-civil]] — campo: `vigencia` (valor `vigente`)
- [[art-1124-codigo-civil]] — campo: `vigencia` (ausente — asimetría)
- [[jurisprudencia-moderacion-clausula-penal]] — campo: `vigencia` (valor `en-revision`)
- `genome-applied/` — ningún gen define este campo
- `regresion.md` — confirma explícitamente que el campo es "residuo del run anterior"

**Diff propuesto:**

Opción A (recomendada): crear `sim/legal/genome-applied/gen-vigencia-normativa.md`
con al menos:

```yaml
---
id: gen-vigencia-normativa
trigger: "la página es de tipo concepto/normativa o jurisprudencia"
status: active
version: 1
seeded_from: company.yaml (extensión)
---
```

```
Las páginas de tipo normativa y jurisprudencia declaran el campo
`vigencia: {vigente | en-revision | derogada | no-vigente}`.
- `vigente`: plenamente en vigor.
- `en-revision`: bajo amenaza de modificación por evento (reforma, sentencia
  superior); QUERY debe advertir siempre.
- `derogada`: sin efecto jurídico; confidence baja a ≤0.1 automáticamente.
- `no-vigente`: anteproyecto o norma no promulgada; confidence ≤0.5.
La vigencia la actualiza un evento (sentencia, promulgación), no el tiempo.
LINT valida el campo contra estos cuatro valores en toda página normativa/jurisprudencia.
```

Opción B (menor): eliminar el campo `vigencia` de las 3 páginas que lo tienen y
documentar la ausencia hasta que exista el gen.

Nota: la propuesta que toca `genome-applied/` pasa por [[gen-compuerta-mutacion]]
(events.jsonl + re-sync AGENTS.md); la opción B toca wiki → cambio directo +
línea en log.md.

---

## P2 — `contradice` asimétrico: reforma no declarada como amenaza en páginas afectadas (C3)

| Campo | Valor |
|---|---|
| id | P2 |
| fuente | C3 |
| fecha | 2026-06-25 |
| status | approved |
| clase | contradicción entre páginas wiki (asimetría de relación bilateral) |
| severidad | 4 |
| alcance | 3 |
| score | **43** |

**Motivo:**
`reforma-cc-2026.md` declara `relations.contradice` apuntando a
[[jurisprudencia-moderacion-clausula-penal]] y a [[art-1154-codigo-civil]].
Esas dos páginas tienen `relations.contradice: []` — no declaran que son
contradichas. Un agente (o abogado) navegando desde [[jurisprudencia-moderacion-
clausula-penal]] o [[art-1154-codigo-civil]] no descubre la amenaza de la reforma
a través del grafo de relaciones, salvo que lea el body text de `art-1154-cc.md`
(que sí menciona la amenaza en prosa pero no en campo navigable). Esta opacidad
es especialmente grave en legal: la vigencia de un precedente jurisprudencial es
crítica para el caso activo.

**Evidencia:**
- [[reforma-cc-2026]] — campo: `relations.contradice` (apunta a los otros dos)
- [[jurisprudencia-moderacion-clausula-penal]] — campo: `relations.contradice` (vacío)
- [[art-1154-codigo-civil]] — campo: `relations.contradice` (vacío)

**Diff propuesto:**

En `sim/legal/wiki/semantic/jurisprudencia/jurisprudencia-moderacion-clausula-penal.md`,
sección `relations`:

```yaml
# Antes:
  contradice: []

# Después:
  contradice:
    - "[[reforma-cc-2026]]"
```

En `sim/legal/wiki/semantic/normativa/art-1154-codigo-civil.md`,
sección `relations`:

```yaml
# Antes:
  contradice: []

# Después:
  contradice:
    - "[[reforma-cc-2026]]"
```

Estos cambios hacen el grafo simétrico y navegable desde ambos extremos.
Son cambios de wiki (no de genoma): cambio directo + línea en log.md.

---

## P3 — `sources` de `contrato-distribucion-v2` apunta a fuente raw de v3 (C2)

| Campo | Valor |
|---|---|
| id | P3 |
| fuente | C2 |
| fecha | 2026-06-25 |
| status | approved |
| clase | contradicción entre páginas wiki (sources incorrecto) |
| severidad | 4 |
| alcance | 2 |
| score | **42** |

**Motivo:**
`contrato-distribucion-v2.md` declara `sources: ["[[raw/2026-05-20-contrato-
distribucion-v3]]"]` — el mismo raw que la página v3. La función de `sources`
es la trazabilidad de procedencia: cada página debe citar el documento raw que
la originó. Una página histórica (v2) apuntando al raw de su sucesor (v3) rompe
esa trazabilidad: no es posible saber qué documento dio origen a la versión v2.
`gen-version-contrato` especifica que cada versión cita su fuente en `raw/`.

**Evidencia:**
- [[contrato-distribucion-v2]] — campo: `sources` (valor: raw de v3)
- [[contrato-distribucion-v3]] — campo: `sources` (valor: mismo raw)
- `genome-applied/gen-version-contrato.md` — campo: regla ("cada versión cita su fuente en `raw/`")

**Diff propuesto:**

En `sim/legal/wiki/semantic/contratos/contrato-distribucion-v2.md`:

```yaml
# Antes:
sources:
  - "[[raw/2026-05-20-contrato-distribucion-v3]]"

# Después (opción A — si existe el raw original del v2):
sources:
  - "[[raw/<fecha>-contrato-distribucion-v2]]"   # sustituir por ruta real si existe

# Después (opción B — si el raw original del v2 no existe en raw/):
sources: []
# Añadir nota en body:
# > Fuente raw de la versión v2 no disponible en `raw/`. La versión fue
# > reconstruida desde el rastro de negociación en [[contrato-distribucion-v3]].
```

Cambio de wiki: cambio directo + línea en log.md.

---

## Tabla resumen de propuestas

| id | fuente | Clase | Sev | Alcance | Score | Status |
|---|---|---|---|---|---|---|
| P1 | C1 | contradicción wikis (campo huérfano) | 4 | 4 | **44** | approved |
| P2 | C3 | contradicción wikis (contradice asimétrico) | 4 | 3 | **43** | approved |
| P3 | C2 | contradicción wikis (sources incorrecto) | 4 | 2 | **42** | approved |

---

## Nota sobre candidatos no incluidos

- **C4 (score 21)** y **C5 (score 23)**: confirmados por el auditor pero fuera
  del top-3 por impacto. Quedan disponibles para un siguiente ciclo AUDIT o para
  aprobación discrecional del `mutation_approver`. No se incluyen en este lote
  porque `N = min(3, confirmados) = 3`.
- **C6**: falso positivo confirmado. Descartado.

---

## Confidencialidad

Este artefacto referencia páginas `secreto_profesional: true` exclusivamente por
`[[link]]` y nombre de campo. **Ningún valor sensible** ha sido transcrito.
