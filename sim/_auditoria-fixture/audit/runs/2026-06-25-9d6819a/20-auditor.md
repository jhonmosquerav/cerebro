---
run_id: 2026-06-25-9d6819a
role: auditor
gen_auto_auditoria_version: 2
date: 2026-06-25
candidatos_maker: 8
confirmados: 8
score_corrections: 1
---

# Auditor — AUDIT 2026-06-25-9d6819a

Metodología: pasada fresca sin memoria de sesión. Insumos exclusivos: `00-snapshot`,
`gen-auto-auditoria` v2, `10-maker.md`, y los archivos fuente de
`sim/_auditoria-fixture/genome-applied/` y `wiki/`. Se verificó que cada hallazgo
re-deriva de los archivos fuente y que el score cumple exactamente la rúbrica v2.
`impacto = severidad×10 + alcance`.

---

## Verificación adversarial por candidato

### C1 — Contradicción entre genes activos

**Verificación de evidencia:**
Leídos `gen-fix-precio-abierto.md` y `gen-fix-precio-vigencia.md`. Ambos tienen:
- `trigger: la fuente menciona un precio` (idéntico, confirmado textualmente)
- `status: active` (ambos, confirmado)
- Reglas directamente opuestas: abierto dice "SIEMPRE tal cual, sin importar su fecha de
  vigencia"; vigencia dice "NUNCA se cita un precio cuya fecha de vigencia ya pasó"
- El cuerpo de `gen-fix-precio-vigencia` incluye literalmente: "Contradice directamente a
  [[gen-fix-precio-abierto]]"

El detector de redundancia/obsolescencia de genoma (trigger solapado) lo captura; también
califica como "contradicción entre genes activos" que es la clase de mayor severidad
(sev 5 > sev 3 de "regla obsoleta/deprecable"). Clase correcta: fila 1 de la tabla.

**Alcance:** v2 — para contradicción entre genes, "TODAS las páginas/genes en conflicto" = 2 ✓

**Score maker:** sev=5, alcance=2, impacto=52
**Score recomputado:** sev=5, alcance=2, impacto=**52** ✓

**Veredicto: CONFIRMADO** — sin corrección de score.

---

### C2 — Info vencida en dominio de seguridad

**Verificación de evidencia:**
Leído `protocolo-bloqueo-loto.md`:
- `valido_hasta: 2026-01-01` < 2026-06-25 → vencido hace 176 días ✓
- `tags: [seguridad, protocolo]`, cuerpo: "Procedimiento de bloqueo y etiquetado para
  intervenir la prensa de forma segura" → dominio de seguridad física confirmado ✓

Leído `prensa-p1.md`:
- `relations: tratada_segun: ["[[protocolo-bloqueo-loto]]"]` → relación tipada de primer
  nivel `tratada_segun` que cita operativamente al protocolo vencido ✓
- La relación `tratada_segun` está declarada en `company.yaml → relation_types` ✓

La calificación de "dominio de seguridad" (seguridad física) hace que la caducidad herede
sev 5. La página citante (`prensa-p1`) suma al alcance por la regla explícita v2:
"la página/gen vencido + las páginas que lo CITAN operativamente (relación tipada de primer
nivel)".

**Alcance:** 2 (protocolo-bloqueo-loto + prensa-p1) ✓

**Score maker:** sev=5, alcance=2, impacto=52
**Score recomputado:** sev=5, alcance=2, impacto=**52** ✓

**Veredicto: CONFIRMADO** — sin corrección de score.

---

### C3 — Contradicción entre páginas wiki / Violación de invariante

**Verificación de evidencia:**
Leído `cliente-acme.md`:
- `estado: activo`, cuerpo: "Acme S.A. — cliente activo, con contrato vigente" ✓

Leído `caso-acme.md`:
- `relations: contradice: ["[[cliente-acme]]"]` → relación explícita de contradicción ✓
- Cuerpo: "Acme fue dado de baja en mayo 2026. Contradice el estado `activo` de
  [[cliente-acme]]." ✓
- `cliente-acme` no fue actualizado in-place tras el evento → viola [[gen-entidad-con-estado]] ✓

El defecto es simultáneamente tres cosas, todas con sev 4:
- (a) "contradicción entre páginas wiki" — fila 5 de la rúbrica (sev 4)
- (b) "entidad con estado inconsistente con su historial de eventos" — fila 4 (sev 4)
- (c) "violación de invariante impuesta por un gen" ([[gen-entidad-con-estado]] manda
  actualizar in-place la entidad tras el evento) — fila 3 (sev 4)

Regla v2: "Cada defecto pertenece a UNA sola clase: la de mayor severidad que le aplique."
Todas son sev 4. Desempate = prioridad canónica de clase (orden de filas). Fila 3 precede a
fila 4 y a fila 5. Por lo tanto la clase correcta es **"violación de invariante impuesta por
un gen"** (sev 4, fila 3).

**Corrección de clase:** el maker eligió "contradicción entre páginas wiki" (fila 5); la
clase canónica por el criterio de desempate es "violación de invariante impuesta por un gen"
(fila 3). El impacto NO varía porque sev=4 en ambas y alcance=2 en ambas.

**Alcance bajo la clase corregida:** "la entidad + las páginas/eventos de respaldo implicados"
= `cliente-acme` + `caso-acme` = 2 ✓ (idéntico al cálculo original)

**Score maker:** clase="contradicción entre páginas wiki", sev=4, alcance=2, impacto=42
**Score recomputado:** clase="violación de invariante impuesta por un gen", sev=4, alcance=2,
impacto=**42** ← score igual, clase corregida

**Veredicto: CONFIRMADO** con corrección de etiqueta de clase (impacto sin cambio).

---

### C4 — Regla obsoleta/deprecable (gen del genoma)

**Verificación de evidencia:**
Leído `gen-fix-clasifica-v1.md`:
- `trigger: la fuente es una ficha de producto`, `status: active` ✓
- Cuerpo: "Las fichas de producto van a wiki/semantic/productos/." — regla básica

Leído `gen-fix-clasifica-v2.md`:
- `trigger: la fuente es una ficha de producto` (idéntico) ✓, `status: active` ✓
- Cuerpo: "Cubre por completo el caso de [[gen-fix-clasifica-v1]], que queda obsoleto
  (mismo trigger, regla subsumida)." ✓

Diferencia clave con C1: aquí no hay contradicción lógica (v2 amplía v1, no la niega).
La clase aplicable es "regla obsoleta/deprecable" (sev 3), no "contradicción entre genes
activos" (sev 5). La distinción es correcta: v2 es superset de v1 sin negar ninguna de sus
instrucciones.

**Alcance:** v2 — "para obsolescencia de genoma, AMBOS genes del solape" = 2 ✓

**Score maker:** sev=3, alcance=2, impacto=32
**Score recomputado:** sev=3, alcance=2, impacto=**32** ✓

**Veredicto: CONFIRMADO** — sin corrección de score.

---

### C5 — Vacío (link roto)

**Verificación de evidencia:**
Leído `prensa-p1.md`:
- `relations: usa: ["[[manual-inexistente]]"]` ✓
- Cuerpo: "Para el detalle de operación, ver [[manual-inexistente]]." ✓

Búsqueda de `manual-inexistente.md` bajo `sim/_auditoria-fixture/wiki/`: el archivo no existe
en ninguna ruta del fixture. ✓

**Alcance:** v2 — vacío: "1 (la página/categoría/campo afectado)" = 1 (prensa-p1) ✓

**Score maker:** sev=2, alcance=1, impacto=21
**Score recomputado:** sev=2, alcance=1, impacto=**21** ✓

**Veredicto: CONFIRMADO** — sin corrección de score.

---

### C6 — Vacío (categoría sin cobertura)

**Verificación de evidencia:**
Leído `company.yaml`:
- `taxonomy.semantic: [seguridad, maquinas, clientes, casos, productos, confidencial, proveedores]`
  → "proveedores" declarado ✓
- El propio archivo incluye el comentario: "# La categoria 'proveedores' se declara pero
  queda sin paginas -> defecto D6 (vacio)." ✓

Verificado: no existe `wiki/semantic/proveedores/` ni ninguna página para esa categoría en
el fixture ✓

**Alcance:** v2 — vacío: "1 (la página/categoría/campo afectado)" = 1 (categoría) ✓

**Score maker:** sev=2, alcance=1, impacto=21
**Score recomputado:** sev=2, alcance=1, impacto=**21** ✓

**Veredicto: CONFIRMADO** — sin corrección de score.

---

### C7 — Redundancia (duplicado)

**Verificación de evidencia:**
Leído `widget-a.md`:
- `type: entidad`, SKU WID-A, material acero, proveedor Norte
- `relations: usa: []` — sin `deriva_de`, `supersede`, `agregado_en` ✓

Leído `widget-a-detalle.md`:
- Misma entidad: "Widget A, SKU WID-A. Fabricado en acero. Proveedor Norte."
- Cuerpo: "(Duplica a [[widget-a]].)" ✓
- `relations: usa: []` — sin `deriva_de`, `supersede`, `agregado_en` ✓

Regla [[gen-consolidate]] v2: "pares con `deriva_de`/`supersede`/`agregado_en` declarado
quedan EXENTOS de redundancia". Ninguno de los dos los declara → NO exentos ✓

**Alcance:** v2 — redundancia: "TODAS las páginas/genes en conflicto o duplicados" = 2 ✓

**Score maker:** sev=2, alcance=2, impacto=22
**Score recomputado:** sev=2, alcance=2, impacto=**22** ✓

**Veredicto: CONFIRMADO** — sin corrección de score.

---

### C8 — Redundancia confidencial (duplicado)

**Verificación de evidencia (sin transcribir valores sensibles):**
Leídos `expediente-x.md` y `expediente-x-copia.md`:
- Ambos tienen `sensibilidad: confidencial` ✓
- El título de `expediente-x-copia` indica que es copia de `expediente-x` ✓
- Ninguno declara `deriva_de`, `supersede`, `agregado_en` en sus `relations` → NO exentos ✓

**Verificación de confidencialidad en el artefacto maker:** el candidato C8 en `10-maker.md`
cita los objetos exclusivamente por `[[expediente-x]]` y `[[expediente-x-copia]]` + campo
`sensibilidad`. **Ningún valor sensible fue transcrito** (ni nombre, ni DNI, ni diagnóstico). ✓

NOTA AUDITOR: Se verificaron los archivos fuente directamente. Los datos sensibles existen en
los archivos del fixture pero NO aparecen en ninguno de los artefactos de auditoría
(`10-maker.md`, este `20-auditor.md`). Regla [[gen-confidencialidad]] respetada.

**Alcance:** v2 — redundancia: "TODAS las páginas/genes en conflicto o duplicados" = 2 ✓
Las páginas confidenciales "SÍ cuentan en el número" según la rúbrica v2 ✓

**Score maker:** sev=2, alcance=2, impacto=22
**Score recomputado:** sev=2, alcance=2, impacto=**22** ✓

**Veredicto: CONFIRMADO** — sin corrección de score.

---

## Verificación de orden y desempates

| Par | Criterio | Resultado maker | Verificación auditor |
|---|---|---|---|
| C1 vs C2 (52 vs 52) | fila de clase: C1=fila 1, C2=fila 2 | C1 > C2 ✓ | CORRECTO |
| C8 vs C7 (22 vs 22, misma clase) | ruta alfabética: `confidencial/...` < `productos/...` | C8 > C7 ✓ | CORRECTO |
| C6 vs C5 (21 vs 21, misma clase) | ruta objeto: `company.yaml` < `wiki/semantic/maquinas/prensa-p1.md` | C6 > C5 ✓ | CORRECTO |

---

## Tabla resumen — Auditor (reordenada, clase corregida en C3)

| id | clase (v2 canónica) | sev | alcance | impacto | veredicto | corrección |
|---|---|---|---|---|---|---|
| C1 | contradicción entre genes activos | 5 | 2 | **52** | CONFIRMADO | — |
| C2 | info vencida en dominio de seguridad | 5 | 2 | **52** | CONFIRMADO | — |
| C3 | ~~contradicción entre páginas wiki~~ **violación de invariante impuesta por un gen** | 4 | 2 | **42** | CONFIRMADO | clase corregida (sev y score sin cambio) |
| C4 | regla obsoleta/deprecable (gen del genoma) | 3 | 2 | **32** | CONFIRMADO | — |
| C8 | redundancia (duplicado) — confidencial | 2 | 2 | **22** | CONFIRMADO | — |
| C7 | redundancia (duplicado) | 2 | 2 | **22** | CONFIRMADO | — |
| C6 | vacío (categoría sin cobertura) | 2 | 1 | **21** | CONFIRMADO | — |
| C5 | vacío (link roto) | 2 | 1 | **21** | CONFIRMADO | — |

**Confirmados: 8 / 8**
**Correcciones de score: 0** (todos los scores iguales al maker)
**Correcciones de clase: 1** (C3: etiqueta de clase cambiada por prioridad canónica v2; impacto sin variación)

---

## Fricciones del gen

No se encontraron fricciones mayores en v2. El gen es internamente consistente para los casos
del fixture. Observaciones menores:

1. **Exención de redundancia en C7/C8:** el gen delega en [[gen-consolidate]] v2 la regla de
   exención (`deriva_de`/`supersede`/`agregado_en`). `widget-a-detalle` y `expediente-x-copia`
   mencionan la duplicación en el **cuerpo** pero no en `relations`. El gen es correcto en
   no contar esas menciones de prosa — solo cuentan las relaciones tipadas. Sin fricción.

2. **C3 clase vs detector:** el gen dice "la identidad del candidato (qué página/gen, qué
   clase) la fija el detector". El detector de `contradice` fija clase "contradicción entre
   páginas wiki". Sin embargo la rúbrica también manda aplicar la clase de mayor prioridad
   canónica cuando un defecto califica múltiples. Ambas instrucciones son válidas y pueden
   coexistir si se interpreta que el detector propone la clase y la rúbrica la confirma/eleva.
   Fricción menor: el gen podría aclarar explícitamente que la clase propuesta por el detector
   puede ser elevada por la rúbrica de prioridad. Sin impacto en este run (score idéntico).

---

## Confidencialidad — verificación final

El auditor accedió a los archivos fuente de `expediente-x.md` y `expediente-x-copia.md`
para confirmar la redundancia. Los datos sensibles allí contenidos NO fueron transcritos ni
en `10-maker.md` ni en este `20-auditor.md`. Solo se citan por `[[link]]` y campo
`sensibilidad`. Regla [[gen-confidencialidad]] y sección "Confidencialidad" de
[[gen-auto-auditoria]] v2 respetadas.
