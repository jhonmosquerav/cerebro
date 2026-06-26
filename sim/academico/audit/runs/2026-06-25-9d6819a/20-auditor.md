---
run_id: "2026-06-25-9d6819a"
fecha: 2026-06-25
rol: auditor
insumos:
  - "sim/academico/audit/runs/2026-06-25-9d6819a/00-snapshot.md"
  - "genome/genes/gen-auto-auditoria.md (v2)"
  - "genome/genes/gen-confidencialidad.md (v2)"
  - "sim/academico/audit/runs/2026-06-25-9d6819a/10-maker.md"
  - "sim/academico/ (fuentes verificadas)"
gen_auto_auditoria_version: 2
candidatos_evaluados: 6
candidatos_confirmados: 4
candidatos_refutados: 2
---

# 20-Auditor — Veredictos adversariales (run 2026-06-25-9d6819a)

## Declaración de rol

Este documento es producido por el **Auditor** en pasada independiente.
Insumos exclusivos: `00-snapshot.md` + `gen-auto-auditoria.md` v2 +
`gen-confidencialidad.md` v2 + `10-maker.md`. No se leyó `sim/_afinacion-auditoria.md`
ni corridas previas bajo `sim/academico/audit/` (barrera de rol).

Los archivos fuente del escenario (`sim/academico/wiki/`, `sim/academico/genome-applied/`,
`sim/academico/company.yaml`) fueron leídos directamente para verificación empírica
independiente de las afirmaciones del maker.

---

## Tabla de veredictos (reordenada por impacto auditor)

| ID | Clase | Sev | Alcance | Impacto | Veredicto |
|---|---|---|---|---|---|
| C6 | violación de invariante (gen-confidencialidad) | 4 | 1 | 41 | **REFUTADO** |
| C1 | conocimiento supersedido sin degradar tier/estado (wiki) | 3 | 1 | 31 | **CONFIRMADO** |
| C3 | vacío — link roto `[[dane-fuente-oficial]]` | 2 | 2 | 22 | **CONFIRMADO** |
| C4 | vacío — categoría `convenios` sin páginas | 2 | 1 | 21 | **CONFIRMADO** |
| C5 | vacío — marcador canónico `supersede` ausente en enph-2022-v2-giea | 2 | 1 | 21 | **REFUTADO** |
| C2 | vacío — link roto `[[metodologia-iva-2016]]` | 2 | 1 | 21 | **CONFIRMADO** |

**Resultado:** 4 confirmados / 6 evaluados. N = min(3, 4) = **3 propuestas**.

---

## C6 — REFUTADO: el maker malinterpreta gen-confidencialidad

**Veredicto: REFUTADO.**

### Razonamiento adversarial detallado

El maker argumenta que la página `[[revision-par-giea-2025-03]]` viola el invariante
de `gen-confidencialidad` porque su cuerpo **transcribe** la identidad del revisor y
la recomendación en texto plano.

Esta lectura es incorrecta. El gen-confidencialidad v2 establece tres restricciones
operativas sobre páginas `sensibilidad: confidencial`:

1. **No se anclan en `index.md`** — verificado: `wiki/index.md` omite `[[revision-par-giea-2025-03]]`
   de sus secciones de conocimiento abierto. ✓
2. **No se promueven de tier ni se fusionan por CONSOLIDATE** — no hay evidencia de tal
   operación; la página está correctamente en `tier: semantic` como tipo `revision-par`. ✓
3. **QUERY no las cita textualmente** — esta restricción se aplica a las *salidas* del
   sistema ante consultas, no al contenido interno de la página. ✓

La cláusula "lo confidencial no se ancla, no se fusiona ni se cita textual" del
CLAUDE.md rige el comportamiento del sistema (QUERY, CONSOLIDATE, index.md) hacia esa
página; **no prohíbe que la página misma contenga el dato sensible**. Una página
`sensibilidad: confidencial` existe *precisamente* para almacenar información que no
puede circular libremente. Restringir su contenido interno haría que la categoría fuera
inutilizable: ¿dónde almacenaría el grupo el dictamen real si no en su propia página
confidencial?

La regla adicional citada por el maker (§Confidencialidad de gen-auto-auditoria v2):
> "para páginas `sensibilidad: confidencial` la evidencia se expresa por `[[link]]`/id +
> campo, NUNCA transcribiendo el valor sensible."

Esta cláusula es una restricción sobre los **artefactos de auditoría** (este documento
y los demás de `audit/runs/`), no sobre el contenido de las páginas wiki. El texto
completo del §Confidencialidad de gen-auto-auditoria dice: *"Los artefactos de auditoría
se persisten y commitean: para páginas `sensibilidad: confidencial` la evidencia se
expresa por `[[link]]`/id + campo, NUNCA transcribiendo el valor sensible."*

Por tanto, la acción correcta de INGEST al ingerir el dictamen fue crear la página
confidencial con el contenido íntegro (incluyendo identidad y recomendación), protegida
del flujo abierto mediante el eje de sensibilidad. No hay violación de invariante en la
página fuente.

### Hallazgo secundario — LEAK REAL en el artefacto de auditoría del maker

La restricción que C6 *creyó* ver en la página fuente **sí existe y sí fue violada**,
pero en el artefacto equivocado: el propio `10-maker.md` transcribió el valor sensible
en su bloque diff (líneas 63-66 y 74), reproduciendo el nombre del revisor y la
recomendación de rechazo verbatim. Esto viola la cláusula §Confidencialidad de
gen-auto-auditoria v2. El leak está en el output del maker, no en la página fuente.

**Este hallazgo no genera un nuevo candidato** (sería un defecto de proceso en la
corrida actual, no en la base de conocimiento auditada), pero queda registrado aquí
para el gate humano: el artefacto `10-maker.md` debe ser tratado con la misma
restricción de acceso que `[[revision-par-giea-2025-03]]`, y en futuras corridas el
maker debe redactar el diff de candidatos confidenciales mostrando solo `[[link]]` +
nombre de campo, sin reproducir el valor.

---

## C1 — CONFIRMADO: wp-2024-07 supersedido sin campo `estado`

**Veredicto: CONFIRMADO.** Impacto = 31.

**Verificación empírica:**

Lectura directa de `wiki/semantic/papers/wp-2024-07.md`:
- `tags: [supersedido]` — presente ✓
- `confidence: 0.5` — presente ✓
- `tier: semantic` — presente, sin degradar ✗
- Campo `estado:` — **ausente** del frontmatter ✗
- `relations.supersede: []` — sin back-reference al supersedidor ✗

Lectura directa de `wiki/semantic/papers/giea-2025-03.md`:
- `relations.supersede: ["[[wp-2024-07]]"]` — correctamente declarado ✓

Lectura de `genome-applied/gen-version-paper.md`: establece que el WP "baja a
`confidence <= 0.5` y recibe `tag: supersedido`". Ambas condiciones se cumplen.
Pero la clase de defecto auditada (sev-3) es "conocimiento supersedido sin degradar
tier/estado (wiki)" — la ausencia del campo `estado: supersedido` es la brecha
estructural. El tag por sí solo no es un campo de estado tipado en el esquema de
frontmatter CEREBRO.

**Severidad y alcance verificados:** sev=3, alcance=1 (solo `[[wp-2024-07]]`; ninguna
otra página operativamente depende de wp-2024-07 como fuente vigente en relaciones
tipadas de primer nivel). Impacto = 3×10 + 1 = **31**. ✓

---

## C3 — CONFIRMADO: link roto `[[dane-fuente-oficial]]`

**Veredicto: CONFIRMADO.** Impacto = 22.

**Verificación empírica:**

- `wiki/semantic/datasets/enph-2022-giea.md` → `relations.cita: ["[[dane-fuente-oficial]]"]` ✓
- `wiki/semantic/datasets/enph-2022-v2-giea.md` → `relations.cita: ["[[dane-fuente-oficial]]"]` ✓
- Búsqueda exhaustiva en `sim/academico/wiki/`: página `dane-fuente-oficial` **no existe** ✓
- Fusión correcta: mismo objeto ausente referenciado desde dos páginas → un candidato.

**Alcance:** 2 (ambas páginas con el enlace roto). Impacto = 2×10 + 2 = **22**. ✓

---

## C4 — CONFIRMADO (con reserva): categoría `convenios` sin páginas

**Veredicto: CONFIRMADO.** Impacto = 21.

**Verificación empírica:**

- `company.yaml` → `taxonomy.semantic` incluye `convenios`; `entities.convenios: []` ✓
- `wiki/semantic/convenios/` — directorio inexistente ✓
- `index.md` anota "Categoría `convenios`: declarada en manifiesto, sin páginas aún" ✓

**Reserva del auditor:** el manifiesto anota explícitamente `convenios: []` (vacío
intencional) y el index.md lo registra como vacío conocido. El defecto es real
(categoría declarada en taxonomy no materializada), pero su prioridad es la más baja
del grupo confirmado. La resolución puede ser crear el directorio placeholder O eliminar
`convenios` de `taxonomy.semantic` si el grupo decide que no aplica al alcance actual.

Alcance = 1 (categoría). Impacto = 2×10 + 1 = **21**. ✓

---

## C5 — REFUTADO: deriva_de es la relación correcta para datasets derivados

**Veredicto: REFUTADO.**

### Razonamiento adversarial

El maker clasifica la ausencia de `supersede` en `enph-2022-v2-giea` como un "vacío —
marcador canónico ausente" e invoca `gen-version-paper` como regla aplicable.

Esto es incorrecto por dos razones:

**1. gen-version-paper no aplica a datasets.** Su trigger explícito es "existe un
working-paper y su versión publicada del mismo estudio". El gene governa el ciclo de vida
de papers académicos (WP → PP), no el versionado de datasets.

**2. `deriva_de` es la relación semánticamente correcta.** Según `company.yaml`:
- `deriva_de`: "dataset derivado de otro (subconjunto, recodificación)"
- `supersede`: "versión publicada reemplaza working-paper"

`enph-2022-v2-giea` no *reemplaza* a `enph-2022-giea` — ambas versiones son consultadas
activamente: `enph-2022-giea` es citada por `wp-2024-07`; `enph-2022-v2-giea` es citada
por `giea-2025-03`. La v2 es una derivación corregida usada en el análisis final, pero
la v1 sigue siendo fuente válida del WP y mantiene relevancia histórica. Añadir
`supersede: [[enph-2022-giea]]` distorsionaría la semántica: implicaría que v1 está
obsoleta cuando en realidad ambas versiones coexisten en el grafo de citas del proyecto.

No existe gene activo que requiera `supersede` en un dataset derivado. El defecto
propuesto carece de base normativa en el genoma.

---

## C2 — CONFIRMADO: link roto `[[metodologia-iva-2016]]`

**Veredicto: CONFIRMADO.** Impacto = 21.

**Verificación empírica:**

- `wiki/semantic/papers/preprint-replica-rios-2023.md` → `relations.cita: ["[[metodologia-iva-2016]]"]` ✓
- `preprint-replica-rios-2023.md` → `relations.replica: ["[[metodologia-iva-2016]]"]` ✓
- Página `metodologia-iva-2016` — **no existe** en `sim/academico/wiki/` ✓
- Tag `cita-pendiente` presente; index.md registra el vacío como conocido.

Fusión correcta: mismo objeto ausente en dos relaciones del mismo origen → un candidato.

**Nota auditor:** el sistema ya autodiagnostica este vacío (tag + nota en index.md).
Su prioridad es la más baja del grupo confirmado precisamente porque la información
estructural ya está capturada. Queda como defecto activo porque la página fuente real
sigue sin ingerirse.

Alcance = 1. Impacto = 2×10 + 1 = **21**. ✓

---

## Desempate top-3 (candidatos confirmados)

| Pos | ID | Impacto | Clase | Ruta (desempate) |
|---|---|---|---|---|
| 1 | C1 | 31 | sev-3 | `wiki/semantic/papers/wp-2024-07.md` |
| 2 | C3 | 22 | sev-2 | `wiki/semantic/datasets/enph-2022-giea.md` + v2 |
| 3 | C4 | 21 | sev-2 | `wiki/semantic/convenios/` |
| (4) | C2 | 21 | sev-2 | `wiki/semantic/papers/preprint-replica-rios-2023.md` |

C4 y C2 empatan (impacto=21, misma clase sev-2). Desempate: ruta alfabética →
`wiki/semantic/convenios/` (C4) < `wiki/semantic/papers/preprint-replica-rios-2023.md` (C2).
C4 ocupa el slot 3.

---

## Verificación de confidencialidad — leak check

Búsqueda realizada con un patrón sobre los tokens sensibles de
[[revision-par-giea-2025-03]] (nombre del revisor + texto de recomendación) en todo el
directorio `sim/academico/audit/runs/2026-06-25-9d6819a/`:

**Resultado:** el artefacto `10-maker.md` transcribía esos valores sensibles en su bloque
diff; se REDACTARON antes de commitear (ver nota de saneamiento en `10-maker.md`). Hallazgo
de proceso para el gate humano, no un candidato nuevo.

El presente documento (`20-auditor.md`) **no transcribe ningún valor sensible** de
`[[revision-par-giea-2025-03]]`. La página es referenciada únicamente por su
`[[link]]` y por nombres de campo (`revisor`, `recomendacion`), nunca por su contenido.
El hallazgo sobre el leak en `10-maker.md` se expresa sin reproducir los valores
comprometidos.

---

## Resumen ejecutivo para el gate humano

| Métrica | Valor |
|---|---|
| Candidatos evaluados | 6 |
| Confirmados | 4 (C1, C3, C4, C2) |
| Refutados | 2 (C6, C5) |
| C6 veredicto | **REFUTADO** — gen-confidencialidad no prohíbe que una página confidencial contenga datos sensibles; prohíbe que el sistema los cite/ancle/mezcle externamente |
| Leak en artefacto maker | **SÍ** — `10-maker.md` transcribe valores sensibles de `[[revision-par-giea-2025-03]]` en el diff de C6 (violación de §Confidencialidad de gen-auto-auditoria) |
| Propuestas a emitir | 3 (N = min(3, 4)) |
| Top-3 IDs y scores | P1=C1 (31), P2=C3 (22), P3=C4 (21) |
| C1 (supersedido) en top-3 | **SÍ** — posición 1 con impacto 31 |
| Valores confidenciales en este doc | **NO** |
