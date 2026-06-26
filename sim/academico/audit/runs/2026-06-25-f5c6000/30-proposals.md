---
run_id: 2026-06-25-f5c6000
scenario: academico
role: proposals
fecha: 2026-06-25
gen_auditoria_version: 1
insumos: [20-auditor.md]
propuestas_total: 3
status_global: pending
---

# 30-Proposals — Top-3 mejoras · Run 2026-06-25-f5c6000

Producido por el orquestador a partir de `20-auditor.md`.
N = min(3, 4 candidatos confirmados) = **3**.
Ranking final del auditor: C-01 (42) > C-04 (22) > C-02 (21).
Ninguna propuesta se aplica sin aprobación humana explícita (ver gen-auto-auditoria § Gate humano).

---

## P1 — Añadir nota de discrepancia numérica en contexto de cifra en [[wp-2024-07]]

| Campo | Valor |
|---|---|
| **id** | P1 |
| **fecha** | 2026-06-25 |
| **candidato_origen** | C-01 |
| **clase** | contradicción entre páginas wiki |
| **severidad** | 4 |
| **alcance** | 2 páginas |
| **score (impacto)** | **42** |
| **status** | pending |

**Motivo.**
`[[wp-2024-07]]` y `[[giea-2025-03]]` coexisten activas en `semantic/` con el mismo campo
empírico (elasticidad precio demanda residencial) expresado en cifras distintas: −0.8 (WP)
vs −0.5 (publicado). La discrepancia es 37% en valor relativo y metodológicamente significativa
(controles de ingreso + corrección de muestra de estrato 1). El WP ya tiene un bloque de
nota general que redirige a [[giea-2025-03]] para QUERY, pero no aclara en el contexto de
la cifra −0.8 que el valor publicado es −0.5.

**Evidencia.**
- `[[wp-2024-07]]`: cuerpo confirma elasticidad −0.8; nota general de supersesión presente.
- `[[giea-2025-03]]`: cuerpo confirma elasticidad −0.5 y explica la corrección.
- Relación `supersede` correctamente declarada en frontmatter de [[giea-2025-03]].

**Diff propuesto.**
En `sim/academico/wiki/semantic/papers/wp-2024-07.md`, inmediatamente después de la
línea "Estimación de elasticidad precio de corto plazo: **-0.8** ...", añadir:

```
> ⚠ Estimación preliminar. La versión publicada [[giea-2025-03]] revisa este resultado
> a −0.5 tras controles de ingreso y corrección de muestra de estrato 1. Para toda
> cita o consulta usar [[giea-2025-03]] (ver [[gen-version-paper]]).
```

No se modifica el número −0.8 (preserva el historial de estimaciones preliminares).

**Tipo de aplicación:** cambio en wiki → cambio directo + línea en `log.md` + commit.

---

## P2 — Marcar [[enph-2022-v2-giea]] como versión canónica para [[giea-2025-03]] y aclarar uso de [[enph-2022-giea]]

| Campo | Valor |
|---|---|
| **id** | P2 |
| **fecha** | 2026-06-25 |
| **candidato_origen** | C-04 (reclasificado) |
| **clase** | vacío (campo canónico ausente) |
| **severidad** | 2 |
| **alcance** | 2 páginas |
| **score (impacto)** | **22** |
| **status** | pending |

**Motivo.**
`[[enph-2022-v2-giea]]` tiene relación `deriva_de: [[enph-2022-giea]]` correctamente
declarada, pero ninguna de las dos páginas indica cuál es la versión canónica para el
paper publicado [[giea-2025-03]]. `[[giea-2025-03]]` cita ambas en `relations.cita`,
lo que genera ambigüedad sobre cuál dataset reproduce el resultado publicado.
Nota: este par NO es una redundancia (la relación `deriva_de` documenta la genealogía
intencional); el defecto es la ausencia del campo canónico.

**Evidencia.**
- `[[enph-2022-v2-giea]]` frontmatter: `deriva_de: ["[[enph-2022-giea]]"]`; confidence 0.85
  igual a v1 pese a ser metodológicamente más limpia.
- `[[giea-2025-03]]` cuerpo: "muestra ENPH 2022 corregida, n ≈ 26.800" → corresponde a v2.
- `[[enph-2022-v2-giea]]` cuerpo: "Usado en la versión final [[giea-2025-03]]." — sin
  tag canónico formal.

**Diff propuesto.**

En `sim/academico/wiki/semantic/datasets/enph-2022-v2-giea.md`:
- Añadir en `tags`: `canonica-giea-2025-03`
- Añadir nota al final del cuerpo:
  ```
  Versión canónica para reproducir [[giea-2025-03]]. Para estudios que requieran
  la muestra completa (n ≈ 28.000) usar [[enph-2022-giea]] (base de [[wp-2024-07]]).
  ```

En `sim/academico/wiki/semantic/datasets/enph-2022-giea.md`:
- Añadir nota al final del cuerpo:
  ```
  Versión base de [[wp-2024-07]]. Para reproducir [[giea-2025-03]] usar
  [[enph-2022-v2-giea]] (versión corregida con exclusión de estrato 1).
  ```

No se fusionan páginas ni se cambia `deriva_de` (la genealogía ya está correctamente
documentada).

**Tipo de aplicación:** cambio en wiki → cambio directo + línea en `log.md` + commit.

---

## P3 — Resolver vacío estructural: categoría `convenios` en manifiesto sin páginas

| Campo | Valor |
|---|---|
| **id** | P3 |
| **fecha** | 2026-06-25 |
| **candidato_origen** | C-02 |
| **clase** | vacío (categoría sin cobertura) |
| **severidad** | 2 |
| **alcance** | 1 estructura |
| **score (impacto)** | **21** |
| **status** | pending |

**Motivo.**
`company.yaml` declara la categoría `convenios` en `entities` y en `taxonomy.semantic`
(con `convenios: []` y comentario "vacío intencional"). No existe carpeta
`sim/academico/wiki/semantic/convenios/` ni página de tipo `convenio`. El vacío es
conocido y registrado en `index.md`, pero no ha sido resuelto. Genera ruido en auditorías
futuras si no se toma una decisión: eliminar la categoría del manifiesto (si el grupo no
tiene convenios) o crear un stub de cobertura (si los tiene pero no los ingirió).

**Evidencia.**
- `sim/academico/company.yaml` línea `convenios: []` con nota "vacío intencional".
- `sim/academico/wiki/semantic/convenios/` no existe.
- `sim/academico/wiki/index.md` vacíos conocidos: "Categoría `convenios`: declarada en
  manifiesto, sin páginas aún."

**Diff propuesto (opción A — recomendada si el grupo no tiene convenios vigentes).**
En `sim/academico/company.yaml`:
- Eliminar `convenios: []` de `entities`
- Eliminar `convenios` de `taxonomy.semantic`
- Añadir comentario al final de la sección entities:
  ```
  # convenios: eliminado AUDIT 2026-06-25 — sin páginas tras periodo de operación.
  #   Si se formaliza un convenio, re-añadir la categoría mediante EVOLVE.
  ```

**Diff propuesto (opción B — si el grupo tiene convenios pendientes de ingerir).**
Crear `sim/academico/wiki/semantic/convenios/README.md` con frontmatter mínimo:
```yaml
---
title: "Convenios — GIEA (pendiente)"
type: meta
tier: semantic
tags: [convenios, pendiente]
confidence: 0.0
created: 2026-06-25
---
Sin convenios ingresados a 2026-06-25. Categoría reservada para documentar
acuerdos institucionales del grupo. Ver company.yaml § entities.convenios.
```

**Tipo de aplicación (opción A):** cambio en manifiesto → por [[gen-compuerta-mutacion]]
(events.jsonl + commit). Tras aplicar: [[gen-migracion-genoma]] re-valida manifiesto y páginas.
**Tipo de aplicación (opción B):** cambio en wiki → cambio directo + línea en `log.md` + commit.

---

## Candidatos fuera del top-3 (documentados, no propuestos)

| ID | Score | Motivo de exclusión |
|---|---|---|
| C-03 | 21 | Cuarto en ranking (desempate por ruta: C-02 < C-03 < C-05). |
| C-05 | 21 | Quinto en ranking. Score reducido de 31→21 por auditor (sev 3→2). |

C-03 y C-05 son defectos reales y pueden abordarse en la próxima corrida de AUDIT o
en una operación LINT manual.

---

## Confidencialidad — verificación final (propuestas)

Este archivo `30-proposals.md` NO transcribe ningún valor sensible de
[[revision-par-giea-2025-03]]. La página confidencial no genera ninguna propuesta de cambio
y se referencia únicamente por `[[link]]`. Confirmado: cero valores confidenciales.
