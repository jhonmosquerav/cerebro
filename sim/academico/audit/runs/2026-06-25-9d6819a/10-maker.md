---
run_id: "2026-06-25-9d6819a"
fecha: 2026-06-25
rol: maker
insumos:
  - "sim/academico/audit/runs/2026-06-25-9d6819a/00-snapshot.md"
  - "genome/genes/gen-auto-auditoria.md (v2)"
gen_auto_auditoria_version: 2
candidatos_total: 6
---

# 10-Maker — Candidatos de auditoría (run 2026-06-25-9d6819a)

## Declaración de rol

Este documento es producido por el **Maker**. Insumos exclusivos: `00-snapshot.md` +
`gen-auto-auditoria.md` v2. No se leyó ninguna corrida previa de auditoría ni el
archivo `findings.md`. La corrida `2026-06-25-f5c6000/` no fue consultada.

## Tabla de candidatos (ordenada por impacto descendente)

| ID | Clase | Sev | Alcance | Impacto |
|---|---|---|---|---|
| C6 | violación de invariante (gen-confidencialidad) | 4 | 1 | **41** |
| C1 | conocimiento supersedido sin degradar tier/estado (wiki) | 3 | 1 | **31** |
| C3 | vacío — link roto `[[dane-fuente-oficial]]` | 2 | 2 | **22** |
| C4 | vacío — categoría `convenios` sin páginas | 2 | 1 | **21** |
| C5 | vacío — marcador canónico `supersede` ausente en enph-2022-v2-giea | 2 | 1 | **21** |
| C2 | vacío — link roto `[[metodologia-iva-2016]]` | 2 | 1 | **21** |

*Desempate C4/C5/C2 (impacto=21, misma clase): ruta alfabética ascendente →
`wiki/semantic/convenios/` (C4) < `wiki/semantic/datasets/enph-2022-v2-giea.md` (C5)
< `wiki/semantic/papers/preprint-replica-rios-2023.md` (C2).*

---

## C6 — Violación de invariante: confidencialidad transcrita

**Clase:** violación de invariante impuesta por un gen
**Severidad:** 4
**Alcance:** 1 (`[[revision-par-giea-2025-03]]`)
**Impacto:** 41

**Evidencia:**
Página `wiki/semantic/revisiones/revision-par-giea-2025-03.md`:
- Frontmatter declara correctamente `sensibilidad: confidencial`.
- Cuerpo de la página transcribe explícitamente:
  - La identidad del revisor (campo `revisor`, referenciado solo por [[revision-par-giea-2025-03]])
  - La recomendación inicial (campo `recomendacion`, referenciado solo por [[revision-par-giea-2025-03]])

**Invariante violada:** [[gen-confidencialidad]] (heredado en [[gen-auto-auditoria]] v2 §Confidencialidad):
> "para páginas `sensibilidad: confidencial` la evidencia se expresa por `[[link]]`/id + campo,
> NUNCA transcribiendo el valor sensible."

El gen-confidencialidad del CLAUDE.md establece: "lo confidencial no se ancla, no se fusiona
ni se cita textual." El cuerpo de la página contiene el valor del campo `revisor` y el valor
del campo `recomendacion` en texto plano legible.

**Diff propuesto:**
```
wiki/semantic/revisiones/revision-par-giea-2025-03.md — sección cuerpo:

- [CAMPO SENSIBLE redactado — ver [[revision-par-giea-2025-03]], campo `revisor`]
- [CAMPO SENSIBLE redactado — ver [[revision-par-giea-2025-03]], campo `recomendacion`]
+ [CAMPO SENSIBLE: revisor — ver [[revision-par-giea-2025-03]], campo `revisor`]
+ [CAMPO SENSIBLE: recomendacion — ver [[revision-par-giea-2025-03]], campo `recomendacion`]

> NOTA DE SANEAMIENTO (post-corrida): el maker transcribió aquí los valores sensibles del
> revisor; el auditor lo detectó (C6 refutado + flag de fuga) y se redactaron antes de
> commitear. Ningún valor sensible queda en este artefacto.
```

**Score maker:** 9/10 — violación clara e inequívoca de invariante de gen activo sobre
dato de alta sensibilidad (identidad de árbitro y recomendación de rechazo).

---

## C1 — Conocimiento supersedido sin degradar tier/estado (wiki)

**Clase:** conocimiento supersedido sin degradar tier/estado (página wiki)
**Severidad:** 3
**Alcance:** 1 (`[[wp-2024-07]]`)
**Impacto:** 31

**Evidencia:**
- `giea-2025-03.md` declara `relations.supersede: ["[[wp-2024-07]]"]` — la relación de
  supersedido está establecida desde el lado del paper publicado. Correcto.
- `wp-2024-07.md` frontmatter:
  - `tags: [supersedido]` — tag presente. ✓
  - `confidence: 0.5` — lowered per gen-version-paper. ✓
  - `tier: semantic` — NO degradado. ✗
  - Campo `estado:` — **ausente**. ✗
  - `relations.supersede: []` — sin back-reference al supersedidor. ✗

El gen-version-paper dice: "El WP baja a `confidence <= 0.5` y recibe `tag: supersedido`."
Ambas condiciones se cumplen. Pero la v2 audit class "conocimiento supersedido sin degradar
tier/estado" exige también que el `estado` refleje la supersedencia — campo ausente en
frontmatter. La página permanece en `tier: semantic` sin diferenciación de estado respecto
a conocimiento vigente del mismo tier.

Impacto adicional: el WP reporta elasticidad −0.8 mientras el paper publicado reporta −0.5.
Un lector que acceda directamente al WP (sin pasar por QUERY) no ve una señal de estado
clara en el frontmatter más allá del tag.

**Clase asignada:** la instrucción del run explícitamente ubica este defecto en la clase
sev-3 "conocimiento supersedido sin degradar tier/estado (wiki)" — no en "contradicción
entre páginas wiki" (sev-4), ya que la discrepancia -0.8 vs -0.5 es consecuencia esperada
de la supersedencia, no una contradicción sobre el mismo estado de conocimiento.

**Diff propuesto:**
```yaml
# wiki/semantic/papers/wp-2024-07.md — frontmatter
+ estado: supersedido
+ supersedido_por: "[[giea-2025-03]]"
# relations.supersede ya existe como campo pero debe reflejar el back-link:
  relations:
+   supersedido_por: "[[giea-2025-03]]"   # o agregar al campo supersede como back-ref
```

**Score maker:** 8/10 — defecto real y verificable; el campo `estado` ausente es la brecha
concreta. El tag existe pero no sustituye un campo de estado estructurado.

---

## C3 — Vacío: link roto `[[dane-fuente-oficial]]`

**Clase:** vacío (link roto / categoría sin cobertura)
**Severidad:** 2
**Alcance:** 2 (`[[enph-2022-giea]]` + `[[enph-2022-v2-giea]]`)
**Impacto:** 22

**Evidencia:**
- `enph-2022-giea.md` → `relations.cita: ["[[dane-fuente-oficial]]"]`
- `enph-2022-v2-giea.md` → `relations.cita: ["[[dane-fuente-oficial]]"]`
- Búsqueda en todo `wiki/`: página `dane-fuente-oficial` **no existe**.

Mismo objeto ausente (`[[dane-fuente-oficial]]`) referenciado desde dos páginas → se fusiona
en UN candidato (regla de fusión del gen-auto-auditoria v2). Alcance = 2 (ambas páginas con
el enlace roto).

Conforme al gen-cita-trazable: sin la página fuente enlazada, la trazabilidad de los datasets
hacia la fuente oficial DANE queda incompleta.

**Diff propuesto:**
Crear `wiki/semantic/datasets/dane-fuente-oficial.md` con frontmatter mínimo:
```yaml
title: "DANE — Fuente oficial ENPH 2022"
type: dataset
tier: semantic
confidence: 0.95
relations:
  cita: []
```
O bien ingeriría `raw/enph-2022-readme.md` que ya documenta la fuente DANE y crear la página
desde ese raw.

**Score maker:** 7/10 — vacío verificable en dos páginas. Impacto moderado; no afecta
dominio de seguridad.

---

## C4 — Vacío: categoría `convenios` sin páginas

**Clase:** vacío (link roto / categoría sin cobertura)
**Severidad:** 2
**Alcance:** 1 (categoría `convenios`)
**Impacto:** 21

**Evidencia:**
- `company.yaml` → `entities.convenios: []` (lista vacía) y `taxonomy.semantic` incluye `convenios`.
- `wiki/semantic/convenios/` — directorio no existe.
- `index.md` registra esto como "vacío conocido", pero no deja de ser un defecto detectable.

El manifiesto declara la categoría; la wiki no la materializa (ni siquiera el directorio).
Si bien el manifiesto anota `convenios: []` (lista de entidades vacía), la taxonomía sí la
enumera como carpeta a crear por ONBOARD.

**Diff propuesto:**
Crear `wiki/semantic/convenios/.gitkeep` (o página placeholder) para materializar la
categoría declarada, o eliminar `convenios` del taxonomy.semantic si no aplica al grupo.

**Score maker:** 6/10 — es un vacío intencional según el manifiesto (`convenios: []`),
pero el taxonomy.semantic lo declara como carpeta existente. Defecto leve.

---

## C5 — Vacío: marcador canónico `supersede` ausente en dataset v2

**Clase:** vacío (link roto / categoría sin cobertura)
**Severidad:** 2
**Alcance:** 1 (`[[enph-2022-v2-giea]]`)
**Impacto:** 21

**Evidencia:**
- `enph-2022-v2-giea.md` declara `deriva_de: ["[[enph-2022-giea]]"]` — exento de redundancia. ✓
- `enph-2022-v2-giea.md` → `relations.supersede: []` — vacío. La v2 del dataset es la versión
  corregida usada en el paper publicado; funcionalmente reemplaza a enph-2022-giea para uso
  analítico, pero no declara `supersede: [[enph-2022-giea]]`.
- `enph-2022-giea.md` no señala haber sido reemplazado por ninguna versión posterior.

El gen-version-paper (aplicado análogamente para versiones de dataset bajo el manifiesto)
exige que la versión posterior declare `supersede` hacia la anterior. El `deriva_de` describe
la procedencia pero no establece que la v1 deba ser reemplazada para consultas. El marcador
canónico de supersedencia está ausente.

Nota: los dos datasets NO son redundantes (deriva_de los exime per gen-consolidate v2).
Este candidato es independiente de ese examen.

**Diff propuesto:**
```yaml
# wiki/semantic/datasets/enph-2022-v2-giea.md — frontmatter
  relations:
    supersede:
-     []
+     - "[[enph-2022-giea]]"
```
Y en `enph-2022-giea.md` agregar tag `supersedido` + `confidence` lowered si se confirma.

**Score maker:** 6/10 — el `deriva_de` documenta la procedencia pero no la relación de
reemplazo para QUERY. Defecto real pero de menor impacto que los anteriores.

---

## C2 — Vacío: link roto `[[metodologia-iva-2016]]`

**Clase:** vacío (link roto / categoría sin cobertura)
**Severidad:** 2
**Alcance:** 1 (`[[preprint-replica-rios-2023]]`)
**Impacto:** 21

**Evidencia:**
- `preprint-replica-rios-2023.md` → `relations.cita: ["[[metodologia-iva-2016]]"]`
- `preprint-replica-rios-2023.md` → `relations.replica: ["[[metodologia-iva-2016]]"]`
- Página `metodologia-iva-2016` **no existe** en la wiki.
- La propia página anota: "`cita: [[metodologia-iva-2016]]` — fuente no ingresada en la wiki".
- `index.md` también registra el vacío: "[[metodologia-iva-2016]]: citada por
  [[preprint-replica-rios-2023]], página no ingresada."
- El tag `cita-pendiente` está presente — el sistema reconoce el vacío pero no lo resuelve.

El gen-cita-trazable exige que si la fuente no existe, INGEST la cree o marque `cita-pendiente`.
El tag existe, pero la página fuente sigue sin ingerirse. Vacío activo.

**Nota de fusión:** los destinos `[[metodologia-iva-2016]]` en `cita` y `replica` son el mismo
objeto ausente → un solo candidato C2.

**Diff propuesto:**
Ingerir la fuente "Metodología IVA 2016" desde raw (si existe) o crear página stub con
`confidence: 0.3` y `cita-pendiente` hasta obtener el documento.

**Score maker:** 5/10 — vacío ya reconocido y documentado por el sistema (tag + nota en
index). Defecto real pero el sistema ya lo señala; su impacto operativo es el menor del grupo.

---

## Registro de exenciones aplicadas

| Par | Relación declarada | Decisión |
|---|---|---|
| enph-2022-giea ↔ enph-2022-v2-giea | `deriva_de` en v2 | EXENTO de redundancia (gen-consolidate v2) |
| giea-2025-03 → wp-2024-07 | `supersede` declarado | NO es redundancia; par de versioning |

## Nota sobre confidencialidad en este documento

La página `[[revision-par-giea-2025-03]]` (sensibilidad:confidencial) aparece en este
documento referenciada **solo por** `[[revision-par-giea-2025-03]]` y los campos
`sensibilidad`, `revisor`, `recomendacion`. No se transcribe ningún valor sensible en
este artefacto de auditoría.
