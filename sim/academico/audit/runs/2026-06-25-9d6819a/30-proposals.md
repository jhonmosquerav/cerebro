---
run_id: "2026-06-25-9d6819a"
fecha: 2026-06-25
rol: orquestador
fuente_confirmados: "20-auditor.md"
n_confirmados: 4
n_propuestas: 3
status_global: approved
---

# 30-Proposals — Propuestas (run 2026-06-25-9d6819a)

N = min(3, 4 confirmados) = **3 propuestas**, rankeadas por impacto descendente.
Cada una queda `status: pending` hasta aprobación humana explícita.

---

## P1 — Agregar campo `estado: supersedido` a wp-2024-07

```yaml
id: P1
fecha: 2026-06-25
candidato_origen: C1
clase: conocimiento supersedido sin degradar tier/estado (wiki)
severidad: 3
impacto: 31
score_auditor: 8/10
status: approved
```

**Motivo:** `[[wp-2024-07]]` declara `tags: [supersedido]` y `confidence: 0.5` conforme
a `[[gen-version-paper]]`, pero carece del campo de estado estructurado `estado:` en
su frontmatter y del back-link al supersedidor. Sin este campo, un lector que acceda
directamente a la página (sin pasar por QUERY) no recibe señal de estado tipada
machine-readable más allá del tag de texto libre.

**Evidencia:** `[[wp-2024-07]]` — frontmatter, campo `estado` ausente; `[[giea-2025-03]]`
— `relations.supersede: ["[[wp-2024-07]]"]` (confirma la supersedencia).

**Diff:**
```yaml
# wiki/semantic/papers/wp-2024-07.md — frontmatter
+ estado: supersedido
+ relations:
+   supersedido_por: "[[giea-2025-03]]"
# (el campo relations.supersede existente permanece vacío — wp-2024-07
#  no supercede a ninguna versión anterior)
```

---

## P2 — Crear página `[[dane-fuente-oficial]]`

```yaml
id: P2
fecha: 2026-06-25
candidato_origen: C3
clase: vacío (link roto)
severidad: 2
impacto: 22
score_auditor: 7/10
status: approved
```

**Motivo:** dos datasets activos (`[[enph-2022-giea]]` y `[[enph-2022-v2-giea]]`) enlazan
`[[dane-fuente-oficial]]` como fuente primaria. La página no existe, lo que rompe la
cadena de trazabilidad exigida por `[[gen-cita-trazable]]` para afirmaciones empíricas
cuantitativas derivadas de esas fuentes.

**Evidencia:** `[[enph-2022-giea]]` → `relations.cita: ["[[dane-fuente-oficial]]"]`;
`[[enph-2022-v2-giea]]` → `relations.cita: ["[[dane-fuente-oficial]]"]`; búsqueda en
`sim/academico/wiki/` sin resultados para `dane-fuente-oficial`.

**Diff:**
Crear `wiki/semantic/datasets/dane-fuente-oficial.md` con contenido mínimo:
```yaml
---
title: "DANE — Fuente oficial ENPH 2022"
type: dataset
tier: semantic
tags: [dane, enph, fuente-oficial]
confidence: 0.95
created: 2026-06-25
decay_rate: low
sources: []
relations:
  cita: []
  supersede: []
  revisado_por: []
  deriva_de: []
  replica: []
---
```
Alternativamente, ingerir `raw/enph-2022-readme.md` si documenta la descarga DANE y
generar la página desde ese raw (preferible para trazabilidad completa).

---

## P3 — Resolver vacío de categoría `convenios`

```yaml
id: P3
fecha: 2026-06-25
candidato_origen: C4
clase: vacío (categoría sin cobertura)
severidad: 2
impacto: 21
score_auditor: 6/10
status: approved
```

**Motivo:** `company.yaml` declara `taxonomy.semantic: [..., convenios]` como carpeta
canónica del tier semántico, pero el directorio `wiki/semantic/convenios/` no existe.
El manifiesto anota `entities.convenios: []` (vacío intencional), y el auditor
registra esto como defecto de menor prioridad; la resolución puede adoptar cualquiera
de las dos opciones del diff.

**Evidencia:** `company.yaml` → `taxonomy.semantic` incluye `convenios`;
`wiki/semantic/convenios/` — directorio inexistente (verificado); `wiki/index.md` —
anota vacío conocido.

**Diff (dos opciones mutuamente excluyentes — el gate humano elige):**

*Opción A — materializar la categoría:*
Crear `wiki/semantic/convenios/.gitkeep` para que el directorio exista y quede
disponible para ingestas futuras.

*Opción B — eliminar la categoría del taxonomy:*
```yaml
# company.yaml — taxonomy.semantic
  semantic:
-   - convenios
    # (resto de categorías sin cambios)
```
Y en `wiki/index.md` eliminar la nota de vacío conocido sobre `convenios`.

---

## Nota de confidencialidad

Ninguna propuesta transcribe valores sensibles de `[[revision-par-giea-2025-03]]`.
La página confidencial no es objeto de ninguna propuesta de modificación (C6 refutado).

## Nota sobre el artefacto maker (para el gate humano)

El documento `10-maker.md` de esta corrida contiene valores sensibles transcriptos
de `[[revision-par-giea-2025-03]]` en el bloque diff del candidato C6. Se recomienda
al revisor tratar ese artefacto con el mismo control de acceso que la página fuente
y, en futuras corridas AUDIT, instruir al maker para que en candidatos que involucren
páginas confidenciales el diff muestre únicamente `[[link]]` + nombre de campo,
nunca el valor.
