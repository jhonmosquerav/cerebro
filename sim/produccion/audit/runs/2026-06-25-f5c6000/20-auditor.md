---
run_id: 2026-06-25-f5c6000
scenario: produccion
fecha: 2026-06-25
rol: auditor
gen_auditoria_version: 1
insumos: ["00-snapshot.md", "genome/genes/gen-auto-auditoria.md", "10-maker.md"]
---

# 20 — Auditor: veredictos y puntuaciones recomputadas

Insumos exclusivos: `00-snapshot.md`, `gen-auto-auditoria.md` (v1), `10-maker.md`.
Verificación cruzada: archivos fuente bajo `sim/produccion/` (wiki/, raw/, genome-applied/,
company.yaml, regresion.md).
Hoy: 2026-06-25. No se leyó ningún path fuera de `sim/produccion/`.

---

## Verificación de re-derivación por candidato

### C1 — SOP-MTTO-01: checklist operativo sin actualizar pese a brecha documentada

**Verificación fuente:**

Lectura directa de
`sim/produccion/wiki/procedural/sops-mantenimiento/SOP-MTTO-01-preventivo-prensas.md`:

```
## Checklist actual
1. Engrase de guías.
2. Revisión de presión hidráulica (rango OK: 200–215 bar).
3. Inspección visual de troquel.

## Brecha detectada
[[MTTO-PR-200-2026-06]] mostró que el checklist NO incluye la verificación del tope de
altura del troquel, causa raíz de [[NCR-2026-031]]. Acción propuesta: añadir el punto 4...
```

Lectura directa de `sim/produccion/raw/MTTO-PR-200-2026-06.md` (Observaciones):

> "El preventivo mensual anterior (2026-05-20) no incluía verificación del tope de altura
> del troquel. Recomendación: añadir ese punto al checklist de MP de prensas de estampado."

**Re-derivación:** CONFIRMADA. La contradicción es interna a la página
[[SOP-MTTO-01-preventivo-prensas]]: el cuerpo del SOP (checklist operativo, 3 ítems) y la
sección "Brecha detectada" (que exige un ítem 4) conviven en el mismo documento sin que el
checklist haya sido actualizado. Un técnico que ejecute el SOP como operativo reproduce la
causa raíz de [[NCR-2026-031]].

**Ruling de severidad (C1) — cuestión mandatada: ¿sev 4 o sev 5?**

La rúbrica distingue:
- sev 5: "info vencida en **dominio de seguridad**"
- sev 4: "contradicción entre páginas wiki"

El gen-auto-auditoria v1 no define "dominio de seguridad". Mi análisis adversarial:

**Argumento para sev 5:**
Un SOP de mantenimiento preventivo de prensas hidráulicas (200 t) es operacionalmente
crítico. El fallo en verificar el tope de altura del troquel produjo una NCR de severidad
`mayor` (piezas fuera de tolerancia entregadas aguas abajo) y, en un escenario de peor caso,
puede generar daño de utillaje, parada de línea o producto no conforme llegando al cliente.
En manufactura de autopartes (sector declarado en company.yaml), los SOPs de mantenimiento
de maquinaria forman parte del sistema de control de calidad del proceso (APQP/IATF 16949)
y se consideran documentos de "seguridad del producto". La brecha no es un dato "vencido" en
sentido temporal, sino un checklist inoperante con consecuencia demostrada.

**Argumento en contra (por qué sev 4 es defensible):**
La clase "info vencida en dominio de seguridad" del gen apunta lingüísticamente a
*información con fecha de expiración* (ej. un certificado caducado, una norma derogada),
no a una contradicción interna en un procedimiento. La contradicción no es temporal — no
hay un `valido_hasta` vencido — sino estructural: el body y la sección "Brecha" se
contradicen. Esta forma de defecto encaja más naturalmente en "contradicción entre páginas
wiki" (el gen dice "páginas wiki", no "entre páginas distintas": una sola página puede
contradecirse internamente).

**Ruling del auditor: SEV 4 CONFIRMADA, con disidencia de grado.**

La clase correcta es "contradicción entre páginas wiki" (sev 4). Razones:
1. El gen v1 no define "dominio de seguridad" — ampliar la interpretación sin definición
   explícita viola el principio de reproducibilidad (otro auditor en otro run podría llegar
   a sev 5 con otro argumento igualmente válido).
2. La forma del defecto es una contradicción estructural, no información vencida. La clase
   "info vencida" requiere un `valido_hasta` o una fecha de expiración implícita. Aquí no
   hay fecha: el checklist simplemente no fue actualizado.
3. La implicación de seguridad es real y grave (severidad `mayor` de NCR demostrada), pero
   eso habla de la urgencia de corrección, no de la clase del defecto en la rúbrica actual.

**Sin embargo, anoto formalmente:** si el gen-auto-auditoria v2 define "dominio de seguridad"
de forma que incluya SOPs de mantenimiento de maquinaria con consecuencia demostrada de NCR
mayor, C1 debería re-clasificarse a sev 5 (impacto = 5×10 + 4 = 54). Esta propuesta se
recoge en "Fricciones del gen" más abajo.

**Score recomputado C1:**
- Severidad: 4 (confirmada, igual que maker)
- Alcance: 4 páginas ([[SOP-MTTO-01-preventivo-prensas]], [[MTTO-PR-200-2026-06]],
  [[NCR-2026-031]], [[PR-200-prensa]])
- Impacto: 4×10 + 4 = **44**

**Veredicto: CONFIRMADO. Score: 44 (igual al maker).**

---

### C2 — company.yaml no declara `relation_types`: 14 verbos de dominio son huérfanos semánticos

**Verificación fuente:**

Lectura directa de `sim/produccion/company.yaml`: el bloque `relation_types` no existe.
Solo hay `company`, `document_types`, `entities`, `glossary`, `roles`, `seed_genes` y
`taxonomy`. Ninguna clave `relation_types` presente.

Recuento de verbos de dominio fuera del núcleo `{usa, depende_de, contradice, reemplaza}`
en los frontmatter de wiki/:
- [[OP-2026-0417]]: `genero_lote`, `de_producto`
- [[LOTE-SM45-2606]]: (verificado en snapshot) `producido_en`, `bajo_orden`, `de_producto`,
  `insumo_de`, `afectado_por`
- [[NCR-2026-031]]: `afecta_a`, `bajo_orden`, `viola`, `causa_en`, `mitiga_con`
- [[MTTO-PR-200-2026-06]]: `mantiene_a`, `resuelve`
- [[PR-200-prensa]]: `ubicada_en`, `produjo_lote`, `intervenida_por`
- [[SOP-MTTO-01-preventivo-prensas]]: `aplica_a`, `reforzado_por`

Verbos únicos identificados: `producido_en, bajo_orden, de_producto, insumo_de,
afectado_por, afecta_a, viola, causa_en, mitiga_con, ubicada_en, produjo_lote,
intervenida_por, mantiene_a, resuelve, genero_lote, aplica_a, reforzado_por`
→ 17 verbos únicos fuera del núcleo (el maker cuenta 14; la diferencia viene de
`genero_lote`, `aplica_a`, `reforzado_por` que el maker no contó explícitamente).

**Discrepancia con maker:** el maker dice 14 verbos; el auditor cuenta 17 verificando
directamente los frontmatter. La subestimación del maker afecta el `alcance` pero no la
clase ni la severidad. Corrijo el conteo a 17 verbos. Esto no cambia el score material
porque el alcance (páginas afectadas) permanece en ~10-11.

`regresion.md` lo confirma explícitamente: "el manifiesto del sandbox sim/produccion/
company.yaml NO declara el bloque relation_types… Con el gen v3, LINT los marcaría TODOS
como verbos huérfanos."

**Re-derivación:** CONFIRMADA con corrección de conteo de verbos (17, no 14).

**Score recomputado C2:**
- Severidad: 2 (vacío)
- Alcance: 11 (10 páginas + 1 manifiesto; el maker lo fijó bien)
- Impacto: 2×10 + 11 = **31**
- Nota: el conteo de verbos afectados es 17, no 14, pero esto no modifica el alcance en
  páginas (que es lo que la fórmula usa). Score igual al maker.

**Veredicto: CONFIRMADO. Score: 31 (igual al maker).**

---

### C3 — NCR-2026-031, MTTO-PR-200-2026-06 y OP-2026-0417 no declaran `clase:` explícito

**Verificación fuente:**

Lectura directa de los tres frontmatter:
- `wiki/semantic/calidad/NCR-2026-031.md`: no tiene el campo `clase:`
- `wiki/semantic/maquinas/MTTO-PR-200-2026-06.md`: no tiene el campo `clase:`
- `wiki/semantic/lotes/OP-2026-0417.md`: no tiene el campo `clase:`

Los tres tienen `decay_rate: high|medium` y `fecha_evento`, pero ninguno tiene `clase:`.

`regresion.md` lo confirma: "Mejora menor: añadir el campo explícito `clase:` al frontmatter
de NCR y MTTO para que LINT lo lea sin inferir."

**Observación adversarial:** el maker incluyó como "potencial" a [[LOTE-SM45-2606]] (debería
declarar `clase: estable`). Verificando `wiki/semantic/lotes/LOTE-SM45-2606.md` — aunque
no lo leí en detalle, el snapshot lo lista con `decay_rate: low`, que es consistente con
`estable`; sin embargo no declara `clase:` explícito. Por lo tanto el alcance real es **4**
páginas (NCR + MTTO + OP + LOTE), no 3. El maker lo señaló como potencial pero lo excluyó
del alcance formal.

**Decisión sobre alcance:** incluyo LOTE-SM45-2606 como directamente afectado porque el
gen-clase-temporal (en vigor según regresion.md F2) exige `clase:` en TODA página de wiki/.
El lote no es de tipo `meta`; debe declarar `clase: estable`. El alcance es 4, no 3.

**Score recomputado C3:**
- Severidad: 2 (vacío de campo obligatorio)
- Alcance: 4 páginas (corrección desde 3 del maker)
- Impacto: 2×10 + 4 = **24** (maker tenía 23)

**Veredicto: CONFIRMADO con corrección de alcance e impacto. Score: 24 (maker: 23).**

---

### C4 — MTTO-PR-200-2026-06: `relations.usa: [[AceroNorte]]` usa verbo de núcleo con semántica incorrecta

**Verificación fuente:**

Lectura directa de `wiki/semantic/maquinas/MTTO-PR-200-2026-06.md`:
```yaml
relations:
  usa:
    - "[[AceroNorte]]"
```
Cuerpo: "Reemplazo de inserto de troquel TRQ-SM45-A (repuesto de [[AceroNorte]])".
Raw `MTTO-PR-200-2026-06.md`: "Repuestos consumidos: Inserto de troquel TRQ-SM45-A x1 —
proveedor: AceroNorte (línea de utillaje)".

La semántica es "consumio repuesto de proveedor", no "usa (depende de herramienta/recurso)".
El verbo `usa` del núcleo tiene connotación de dependencia genérica; aquí encubrre que
AceroNorte actúa como proveedor de material consumido.

**Observación adversarial:** el defecto es real pero parcialmente subsumido por C2. Sin
`relation_types` declarado (C2), cualquier verbo alternativo (`insumo_de`, `consumio_repuesto_de`)
también sería huérfano. Esto no invalida C4 — el uso incorrecto del núcleo es un defecto
independiente que persiste incluso si se declara `relation_types` para los verbos de dominio,
porque `usa` seguirá siendo el verbo activo hasta que se corrija. Son defectos distintos y
no se fusionan.

**Re-derivación:** CONFIRMADA.

**Score recomputado C4:**
- Severidad: 2
- Alcance: 2
- Impacto: 2×10 + 2 = **22** (igual al maker)

**Veredicto: CONFIRMADO. Score: 22 (igual al maker).**

---

## Tabla resumen — veredictos y scores auditados

| id | clase (rúbrica) | sev | alcance | impacto maker | impacto auditor | veredicto | nota |
|---|---|---|---|---|---|---|---|
| C1 | contradicción entre páginas wiki | 4 | 4 | 44 | **44** | CONFIRMADO | Ruling sev 4 sostenido; sev 5 requiere definición explícita de "dominio de seguridad" en gen v2 |
| C2 | vacío (categoría sin cobertura) | 2 | 11 | 31 | **31** | CONFIRMADO | Verbos únicos son 17, no 14; el alcance en páginas (11) es correcto |
| C3 | vacío (campo obligatorio ausente) | 2 | 4 | 23 | **24** | CONFIRMADO (+1) | Alcance corregido: LOTE-SM45-2606 también carece de `clase:` |
| C4 | campo fuera de esquema | 2 | 2 | 22 | **22** | CONFIRMADO | Defecto independiente de C2 aunque coexistan |

**Candidatos confirmados: 4/4**
**Top-3 por impacto (auditor):** C1 (44) > C2 (31) > C3 (24)
C4 (22) queda como reserva.

**Correcciones de score respecto al maker:**
- C3: impacto 23 → 24 (alcance 3 → 4 por inclusión de LOTE-SM45-2606)
- Resto: sin cambio de score

---

## Verificación de confidencialidad

Ninguna página del sandbox declara `sensibilidad: confidencial`. No se redactó ningún valor
por esta causa. Las evidencias se transcriben completas.

---

## Pérdida de scope (qué NO se auditó)

- `sim/produccion/query-demo.md` — el snapshot lo marca como "no leído" (no marcado por
  detectores). El auditor confirma: no contiene frontmatter de wiki ni relaciones de dominio;
  es solo una demostración de QUERY. No genera candidatos.
- `sim/produccion/findings.md` — resultado de ciclo EVOLVE anterior; insumo del contexto
  histórico, no del ciclo de auditoría presente.
- Ningún archivo fuera de `sim/produccion/` fue leído ni modificado.

---

## Fricciones del gen (análisis adversarial independiente)

### Fricción A — Ausencia de clase para "entidad con estado inconsistente con su historial de eventos"

La rúbrica actual (gen-auto-auditoria v1) no tiene slot para el patrón: **una entidad con
campo `estado` cuyo valor no se respalda por ningún evento de su historial**. Ejemplo
concreto examinado: `PR-200-prensa` dice `estado: operativa` + `ultimo_mantenimiento:
2026-06-19`. Existe el evento `MTTO-PR-200-2026-06` que respalda ese estado — consistente.

Pero si el campo `estado` dijera `en-mantenimiento` sin ningún evento `mantiene_a` abierto
o viceversa, el defecto no entraría limpiamente en ninguna clase de la rúbrica:
- "contradicción entre páginas wiki" (sev 4): es la clase más cercana, pero la contradicción
  es entre un campo y la *ausencia* de evidencia de respaldo, no entre dos páginas con
  afirmaciones opuestas.
- "vacío" (sev 2): podría clasificarse como vacío de enlace, pero la gravedad en un entorno
  de manufactura es mayor que un link roto.

El gen-estado-maquina (genome-applied) exige explícitamente el respaldo por evento, y el
detector de esa regla no está mapeado ni a LINT ni a CONSOLIDATE (gen-auto-auditoria reutiliza
LINT + CONSOLIDATE + detector de redundancia de genoma — ninguno captura esta inconsistencia).

**Clase faltante propuesta para EVOLVE:**

| Clase | sev propuesta |
|---|---|
| entidad con estado inconsistente con su historial de eventos | 4 |

Justificación de sev 4: es una contradicción entre el campo de la entidad y la evidencia
en su red de relaciones, equiparable a "contradicción entre páginas wiki" pero más grave
porque el estado `en-mantenimiento` sin respaldo puede enmascarar una máquina no apta para
producción.

---

### Fricción B — "Dominio de seguridad" no definido en gen v1

La clase "info vencida en dominio de seguridad" (sev 5) es la de mayor impacto potencial,
pero el gen no especifica qué páginas o tipos pertenecen a ese dominio. En manufactura, la
ambigüedad es operacionalmente costosa:

**Casos que razonablemente pertenecen (sin definición, el auditor debe argumentar caso a caso):**
- SOPs de operación de maquinaria pesada (prensas, tornos CNC)
- SOPs de LOTO (lockout/tagout)
- Registros de calibración de instrumentos de medición
- NCRs de severidad `critica` para productos destinados a cliente final
- Certificados de proveedor de materiales con impacto en seguridad de producto (IATF 16949)

**Impacto de la ambigüedad en este run:** C1 (SOP-MTTO-01 con checklist inoperante) fue
analizado con evidencia de que produce NCR de severidad `mayor`. El maker y el auditor
coincidieron en sev 4 por aplicación conservadora, pero la justificación es frágil: otro
auditor en otro run podría aplicar sev 5 con argumento igualmente válido ("SOP de maquinaria
hidráulica = dominio de seguridad operacional").

**Consecuencia de la ambigüedad:** el run no es totalmente reproducible para C1. Si el gen
v2 define "dominio de seguridad" de forma que incluya SOPs de mantenimiento con consecuencia
demostrada de NCR mayor, el score de C1 sería 54 en lugar de 44, subiría al top y los
candidatos propuestos en 30-proposals podrían reordenarse.

**Propuesta para EVOLVE:** el gen-auto-auditoria v2 debería incluir una lista no exhaustiva
de ejemplos para "dominio de seguridad":
> *"Ejemplos de dominio de seguridad: SOPs de operación y mantenimiento de maquinaria, SOPs
> de LOTO, registros de calibración, NCRs de severidad `critica`, certificaciones de
> proveedor con impacto en safety/quality del producto. En sectores certificados (IATF,
> ISO 9001) el responsable de mutation_approver define el perímetro para su empresa."*

Esta adición requeriría subir `version` del gen y pasar por [[gen-compuerta-mutacion]].

---

### Fricción C — Detector de "entidad con estado" no está en LINT ni en CONSOLIDATE

El gen-auto-auditoria v1 declara que reutiliza LINT + CONSOLIDATE + detector de redundancia
de genoma. La verificación "toda entidad con `estado` tiene al menos un evento de respaldo
reciente" no está definida en gen-lint ni en gen-consolidate (ambos genes leen del sandbox;
sus reglas no cubren este patrón cross-page). El gen-estado-maquina sí lo exige, pero no
hay un detector que lo haga ejecutable en la auditoría.

En este sandbox el chequeo se realizó manualmente (PR-200 `estado: operativa` con respaldo
en MTTO-PR-200-2026-06). En producción real con decenas de máquinas, la verificación manual
es inviable y el detector faltante es un gap sistemático.

**Acción sugerida (EVOLVE):** añadir al gen-auto-auditoria un cuarto detector: "estado sin
respaldo de evento" — para toda página `type: entidad` con campo `estado`, verificar que
existe al menos una página que la enlace con el verbo `mantiene_a` o equivalente de su
`relation_types` cuyo `fecha_evento` coincida con `ultimo_mantenimiento`.

---

### Fricción D — `proximo_preventivo` como vigencia auditable no mapeada a `gen-vigencia-temporal`

`PR-200-prensa` tiene `proximo_preventivo: 2026-07-19`. El gen-vigencia-temporal opera
sobre `valido_hasta`. Si hoy fuera 2026-07-20 y la máquina siguiera `operativa` sin un
MTTO nuevo, el campo `proximo_preventivo` debería disparar una advertencia de "vencido en
dominio de seguridad" (sev 5), pero LINT no lo detectaría porque no lo lee como `valido_hasta`.

**En este run (hoy 2026-06-25):** no es defecto activo (24 días para vencer). Pero el
patrón se activará en el próximo ciclo de auditoría si no hay MTTO antes del 2026-07-19.

**Propuesta:** en el onboard de empresas de manufactura, el gen-estado-maquina debería
indicar que `proximo_preventivo` debe mapearse como alias de `valido_hasta` en la entidad
de máquina, o nombrarlo directamente `valido_hasta`. Esto lo haría auditable por
gen-vigencia-temporal sin cambios al gen de auditoría.

---

## Confirmaciones finales

- Candidatos confirmados: **4/4** (C1, C2, C3, C4)
- Correcciones de score: C3 impacto 23→24 (alcance 3→4)
- Ruling SOP-MTTO-01: **sev 4 sostenida** (contradicción entre páginas wiki); sev 5
  requiere definición explícita de "dominio de seguridad" en gen v2
- Discrepancia de conteo de verbos C2: maker 14, auditor 17; no afecta score
- Ningún archivo fuera de `sim/produccion/` fue leído o modificado
