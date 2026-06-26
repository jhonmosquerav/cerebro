---
run_id: 2026-06-25-f5c6000
scenario: academico
role: auditor
fecha: 2026-06-25
gen_auditoria_version: 1
insumos: [00-snapshot.md, gen-auto-auditoria.md, 10-maker.md]
candidatos_totales: 5
candidatos_confirmados: 4
candidatos_refutados: 1
---

# 20-Auditor — Veredictos y rúbrica recomputada · Run 2026-06-25-f5c6000

Pasada **independiente y adversarial**: el auditor relee las fuentes primarias del escenario
(`sim/academico/wiki/`, `sim/academico/genome-applied/`, `sim/academico/company.yaml`) y
re-deriva cada candidato sin tomar la narrativa del maker como verdad. Cada claim del maker
se contrasta contra el archivo real.

---

## Verificación de fuga de confidencialidad (pre-flight)

Se ejecutó búsqueda exhaustiva de tokens sensibles del archivo
`[[revision-par-giea-2025-03]]` en todo el directorio `sim/academico/audit/`:

| Token buscado | Encontrado en artefactos de auditoría |
|---|---|
| Nombre del revisor | **NO** — solo aparece dentro de la página fuente `revision-par-giea-2025-03.md`, no en `audit/` |
| Institución del revisor | **NO** |
| Recomendación de primera ronda (rechazar) | **NO** |
| Recomendación de segunda ronda (condicional) | **NO** |
| "árbitro" / "revisor" con contenido sensible | **NO** — menciones en maker solo en afirmación meta "no se transcribe la identidad del revisor" |
| "segunda ronda" / "controles" como req. del dictamen | **NO** |

**Veredicto de leak-check: LIMPIO.** Ningún artefacto de auditoría (`00`, `10`) transcribe valor
sensible de [[revision-par-giea-2025-03]]. La página solo se referencia por `[[link]]` y campo
`sensibilidad: confidencial`. Este archivo `20-auditor.md` continúa el mismo protocolo: ningún
valor sensible de esa página se reproduce aquí.

---

## Veredictos por candidato

### C-01 — Contradicción de estimaciones entre versiones del mismo estudio

**Veredicto: CONFIRMADO** (sin ajuste de score)

**Re-derivación independiente.**
Leído `[[wp-2024-07]]` directamente: cuerpo confirma elasticidad **−0.8** (VI, n ≈ 28.000,
excluye estrato 1). El frontmatter tiene `tags: [..., supersedido]`, `confidence: 0.5`, y una
nota en el cuerpo que ya señala "Versión supersedida por [[giea-2025-03]]".

Leído `[[giea-2025-03]]` directamente: cuerpo confirma elasticidad revisada **−0.5** (VI con
controles adicionales, n ≈ 26.800). Relación `supersede: ["[[wp-2024-07]]"]` presente.

**Evaluación del defecto.**
El maker describe correctamente la discrepancia numérica (−0.8 vs −0.5; 37% de diferencia
relativa) y el riesgo de citación cruzada. Sin embargo, el auditor observa un matiz que el
maker no explicita: `[[wp-2024-07]]` **ya contiene** en su cuerpo la siguiente nota:

> "Versión supersedida por [[giea-2025-03]]. `tag: supersedido`, `confidence: 0.5`.
> En QUERY usar [[giea-2025-03]] como referencia principal (ver [[gen-version-paper]])."

Esto mitiga parcialmente el riesgo, pero **no lo elimina**: la nota redirige para QUERY,
pero **no aclara en contexto de la cifra −0.8 que el valor publicado es −0.5**. Un lector
que aterrice en el párrafo de la estimación sin leer el bloque de nota puede extraer −0.8
sin la advertencia. El diff propuesto (añadir nota en el contexto de la cifra) sigue siendo
válido y necesario.

Clase correcta: **contradicción entre páginas wiki** (sev 4). Ambas páginas activas en
`semantic/`, mismo campo empírico, cifras distintas sin anotación en el lugar de la cifra.
Score: sev 4, alcance 2 páginas → **impacto = 42**. Correcto.

---

### C-02 — Vacío estructural: categoría `convenios` sin páginas

**Veredicto: CONFIRMADO** (sin ajuste de score)

**Re-derivación independiente.**
`company.yaml` línea `convenios: []` con comentario "categoría declarada, sin páginas aún
(vacío intencional)". La clave `convenios` aparece también en `taxonomy.semantic`. No existe
`sim/academico/wiki/semantic/convenios/` ni página alguna de tipo `convenio`.
`index.md` lo registra explícitamente en "Vacíos conocidos".

**Evaluación del defecto.**
El maker lo clasifica como vacío (sev 2, alcance 1) → impacto 21. Correcto. La nota "vacío
intencional" en el YAML no exime al candidato: sigue siendo un vacío estructural auditable
cuya resolución (eliminar la categoría del manifiesto, o crear stub) es una decisión pendiente
que debe quedar en propuestas.

Score: sev 2, alcance 1 → **impacto = 21**. Correcto.

---

### C-03 — Link roto: `[[metodologia-iva-2016]]` citada pero inexistente

**Veredicto: CONFIRMADO** (sin ajuste de score)

**Re-derivación independiente.**
`[[preprint-replica-rios-2023]]` leído directamente. Campos `relations.cita` y
`relations.replica` contienen `"[[metodologia-iva-2016]]"`. No existe ningún archivo
`metodologia-iva-2016.md` bajo `sim/academico/wiki/`. La página ya tiene
`tags: [..., cita-pendiente]` y `confidence: 0.4`, consistente con `gen-cita-trazable`.
`index.md` lo lista en "Vacíos conocidos".

**Evaluación del defecto.**
El link roto persiste activo (no es solo advertencia: los campos de relación siguen apuntando
a una página inexistente). El `confidence: 0.4` refleja correctamente la regla de
`gen-cita-trazable`, pero no cierra el link roto — son dos mecanismos distintos.
La doble ocurrencia (en `cita` y en `replica`) agrava el impacto sobre la cadena de
reproducibilidad metodológica.

Score: sev 2, alcance 1 → **impacto = 21**. Correcto.

**Desempate C-02 vs C-03.** Impacto idéntico; misma clase "vacío". Por rúbrica de
desempate (ruta de archivo alfabética): `preprint-replica-rios-2023` < `wiki/index` en
orden lexicográfico de ruta → C-03 tiene menor ruta entre las dos, pero el índice del
vacío C-02 es el manifiesto (`company.yaml`) que tampoco es una wiki-path simple.

Auditor corrige la lógica de desempate del maker: la rúbrica dice "ruta de archivo
alfabética" para las páginas/genes **afectados**. Para C-02 el afectado principal es
`company.yaml` (path `sim/academico/company.yaml`); para C-03 el afectado principal es
`sim/academico/wiki/semantic/papers/preprint-replica-rios-2023.md`. Comparando rutas
completas: `company.yaml` < `wiki/semantic/papers/preprint-*` alfabéticamente →
**C-02 va antes que C-03** en el desempate. El maker invirtió el orden. Corrección:
en el ranking de impacto 21, C-02 tiene precedencia sobre C-03.

Este ajuste **no cambia el top-3** (C-01 y C-05 ya ocupan #1 y #2; el tercer puesto
es C-04 con impacto 22 > 21), pero corrige el orden interno entre C-02 y C-03.

---

### C-04 — Redundancia de datasets: `enph-2022-giea` y `enph-2022-v2-giea`

**Veredicto: PARCIALMENTE REFUTADO — reclasificado, score ajustado**

**Re-derivación independiente.**
Ambas páginas leídas directamente:
- `[[enph-2022-giea]]`: misma fuente raw, descarga 2023-11-08, confidence 0.85, decay low.
  Cuerpo: ~28.000 hogares; nota sobre alta no-respuesta en estrato 1.
- `[[enph-2022-v2-giea]]`: misma fuente raw, misma descarga, confidence 0.85, decay low.
  Frontmatter: `deriva_de: ["[[enph-2022-giea]]"]`. Cuerpo: corrige 214 hogares Chocó,
  excluye estrato 1, ~26.800 hogares. "Usado en la versión final [[giea-2025-03]]."

**Juicio adversarial sobre la cuestión central: ¿`deriva_de` exime de "redundancia"?**

La rúbrica del gen-auto-auditoria define redundancia (near-duplicado) como defecto de
clase detectado por CONSOLIDATE. Sin embargo, el manifiesto `company.yaml` declara
explícitamente `deriva_de` como relación de tipo reconocido:

> `relation_types: [..., deriva_de  # dataset derivado de otro (subconjunto, recodificación)]`

La relación `deriva_de` **es exactamente el mecanismo de documentación de versiones de
dataset** según el esquema del sector. Su presencia indica que el sistema ya reconoce y
gestiona correctamente la genealogía: v2 no es un duplicado accidental sino una versión
derivada intencional con diferencias metodológicas documentadas.

**Veredicto: el candidato debe ser RECLASIFICADO, no eliminado.**

La clasificación como "redundancia (near-duplicado)" (sev 2) es parcialmente incorrecta:
los datasets no son duplicados — son versiones con `deriva_de` declarado. Sin embargo,
**subsiste un defecto real diferente**: ninguna de las dos páginas marca cuál es la
versión canónica para el paper publicado [[giea-2025-03]], y ambas tienen la misma
`confidence: 0.85` pese a que v2 es metodológicamente más cuidadosa. Este defecto real
pertenece a la clase **vacío (campo canónico ausente)**, no a "redundancia".

**Reclasificación:**

| Campo | Valor original (maker) | Valor corregido (auditor) |
|---|---|---|
| Clase | redundancia (near-duplicado) | vacío (campo canónico ausente) |
| Severidad | 2 | 2 |
| Alcance | 2 páginas | 2 páginas |
| Impacto | **22** | **22** |

El impacto numérico no cambia (sev 2, alcance 2 → 22), pero la **clase** cambia: no es
redundancia sino vacío de metadato (falta campo `canonica_para` o `tags: canonica-*` en
v2, y falta nota en v1 que indique a qué paper corresponde cada versión). Esto también
resuelve la fricción F-4 del maker: con `deriva_de` presente, el detector de CONSOLIDATE
**debería exemptuar** este par de redundancia y solo reportar el vacío de marcado
canónico. El diff propuesto por el maker es correcto y se mantiene.

Score: sev 2, alcance 2 → **impacto = 22**. Sin cambio numérico, pero clase corregida.

---

### C-05 — Obsolescencia: WP supersedido sin degradación de tier

**Veredicto: CONFIRMADO con reclasificación de clase y ajuste de score**

**Re-derivación independiente.**
`[[wp-2024-07]]` leído: `tier: semantic`, `tags: [..., supersedido]`, `confidence: 0.5`.
No existe campo `estado` explícito en frontmatter. No hay campo `tier_status`. La página
permanece en `wiki/semantic/papers/`. El gen [[gen-version-paper]] dice: "El WP baja a
`confidence <= 0.5` y recibe `tag: supersedido`; nunca se borra." No especifica
degradación de tier ni campos de estado adicionales.

**Juicio sobre la clase y severidad.**

El maker aplica sev 3 "por analogía con regla obsoleta/deprecable" y lo reconoce
explícitamente como forzado. El auditor evalúa:

1. La clase "regla obsoleta/deprecable" (sev 3) aplica a **genes del genoma**, no a páginas
   wiki, según el texto literal de la rúbrica.
2. Las clases disponibles para páginas wiki son: contradicción (4), vencida-seguridad (5),
   vacío (2), redundancia (2).
3. El defecto real: la página tiene `tag: supersedido` pero no tiene campo de metadato
   que refleje ese estado en el frontmatter (`estado: supersedido` ausente), y el tier no
   fue degradado. Esto es un **vacío de metadato de estado** — mismo tipo de vacío que C-04
   reclasificado.
4. Sin embargo, C-05 tiene un componente adicional: el WP sigue apareciendo en `semantic/`
   indistinguible estructuralmente de páginas vigentes, lo cual es un riesgo de
   **contradicción implícita** con la página publicada (clase sev 4) — ya capturado en C-01.

**Veredicto de reclasificación:** C-05 como defecto independiente de C-01 (atañe al tier y
metadatos, no a la nota textual) se clasifica más apropiadamente como **vacío (metadato de
estado ausente)**, sev 2. El maker aplicó sev 3 por analogía fuera de la rúbrica literal.

Bajo rúbrica estricta:

| Campo | Valor original (maker) | Valor corregido (auditor) |
|---|---|---|
| Clase | obsolescencia de página (sev 3 por analogía) | vacío (metadato de estado ausente) |
| Severidad | 3 | **2** |
| Alcance | 1 página | 1 página |
| Impacto | **31** | **2×10 + 1 = 21** |

**Efecto en ranking:** C-05 baja de impacto 31 → 21, igualando a C-02 y C-03.

Desempate C-02 (21) vs C-03 (21) vs C-05 (21): misma clase (vacío), mismo impacto.
Rutas de afectados principales:
- C-02: `sim/academico/company.yaml`
- C-03: `sim/academico/wiki/semantic/papers/preprint-replica-rios-2023.md`
- C-05: `sim/academico/wiki/semantic/papers/wp-2024-07.md`

Orden alfabético de ruta: `company.yaml` < `wiki/.../preprint-*` < `wiki/.../wp-2024-07`.
Resultado: C-02 > C-03 > C-05 en desempate.

**Ranking final recomputado:**

| Rank | ID | Clase | Sev | Alcance | Impacto |
|---|---|---|---|---|---|
| 1 | C-01 | contradicción entre páginas wiki | 4 | 2 | **42** |
| 2 | C-04 | vacío (campo canónico ausente) | 2 | 2 | **22** |
| 3 | C-02 | vacío (categoría sin cobertura) | 2 | 1 | **21** |
| 4 | C-03 | vacío (link roto) | 2 | 1 | **21** |
| 5 | C-05 | vacío (metadato de estado ausente) | 2 | 1 | **21** |

**Top-3 confirmadas (N = min(3, 4 confirmadas) = 3):** C-01, C-04, C-02.

---

## Tabla comparativa maker vs auditor

| ID | Maker impacto | Auditor impacto | Delta | Veredicto | Motivo del cambio |
|---|---|---|---|---|---|
| C-01 | 42 | **42** | 0 | CONFIRMADO | Sin cambio. Evidencia re-deriva correctamente. |
| C-02 | 21 | **21** | 0 | CONFIRMADO | Sin cambio. |
| C-03 | 21 | **21** | 0 | CONFIRMADO | Sin cambio (desempate interno corregido). |
| C-04 | 22 | **22** | 0 | PARCIALMENTE REFUTADO | Clase corregida (redundancia → vacío canónico). `deriva_de` exime de redundancia. Score idéntico. |
| C-05 | 31 | **21** | **−10** | PARCIALMENTE REFUTADO | Sev 3 analógica fuera de rúbrica → sev 2 literal. Cae de rank 2 a rank 4-5. |

**Confirmados (completos o parciales con score): 4 / 5.**
**Refutados (score eliminado): 0.** (Los dos "parcialmente refutados" mantienen candidatura
con clase/score corregidos.)

---

## Juicio sobre la cuestión específica: `derive_de` como exención de redundancia

**Posición del auditor:**
La relación `deriva_de` declarada en el esquema oficial (`relation_types` del manifiesto)
**DEBE exemptuar** un par de datasets de ser clasificado como "redundancia" por CONSOLIDATE.
La relación documenta explícitamente que v2 es una versión derivada intencional, no un
duplicado accidental. Clasificar ese par como "redundancia" es un falso positivo del detector.

**Consecuencia:** C-04 está **RECLASIFICADO** de redundancia → vacío (campo canónico
ausente). El defecto real subsiste (falta marcar cuál versión es canónica para cada paper),
pero la clase correcta es "vacío", no "redundancia".

**Implicación para el gen:** el detector de near-duplicados debería incorporar la
siguiente regla de exención: *si un par de páginas tiene relación `deriva_de` o `supersede`
declarada en al menos uno de sus frontmatters, no se cuenta como redundancia; se reporta
solo el vacío de metadato de genealogía si existe.* Esta exención debe quedar explícita en
`gen-consolidate` o en `gen-auto-auditoria`.

---

## Juicio sobre la cuestión específica: ¿supersede es "obsolescencia" (sev 3)?

**Posición del auditor:**
La clasificación de C-05 como "obsolescencia de página" con sev 3 aplicada por analogía al
ítem "regla obsoleta/deprecable" es **inapropiada bajo la rúbrica literal**. La rúbrica
reserva sev 3 para genes del genoma. Aplicarla a páginas wiki por analogía introduce
no-determinismo en el detector: dos corridas pueden producir scores distintos para el mismo
defecto según si el analista aplica o no la analogía.

El defecto real (metadatos de estado incompletos en una página supersedida) es un vacío
(sev 2), no una obsolescencia de regla. Si el grupo académico considera que un WP
supersedido sin degradación de tier merece sev > 2, la solución correcta es añadir una
clase nueva en la rúbrica (como sugiere el maker en F-1), no forzar la analogía.

---

## Fricciones del gen

### FG-1. Ausencia de clase "supersede / conocimiento genealógico" en la rúbrica

La rúbrica del gen-auto-auditoria no tiene clase explícita para el caso de un documento
supersedido cuyo tier no fue degradado. La clase más cercana es "regla obsoleta/deprecable"
(sev 3), pensada para genes, y "vacío" (sev 2). Ninguna captura exactamente el fenómeno
de una página con estado de obsolescencia no reflejado en metadatos de tier.

**Propuesta de afinación:** añadir clase en la rúbrica:

| Clase nueva | severidad sugerida |
|---|---|
| conocimiento supersedido sin degradación de tier o campo de estado | 3 |

Esto haría que C-05 recuperara sev 3 de forma legítima (no por analogía), y daría al
gen-version-paper la base para especificar qué campos cambiar al marcar supersedido.
Cambiar la rúbrica = subir `version` del gen = pasa por [[gen-compuerta-mutacion]].

---

### FG-2. Sev 5 "vencido en dominio de seguridad" es demasiado alto para academia no-safety

La rúbrica actual agrupa bajo sev 5 toda "info vencida en dominio de seguridad". En
contexto académico económico (sin consecuencias de seguridad física, salud o cumplimiento
regulatorio con consecuencias legales), aplicar sev 5 a un WP supersedido o retractado
sería una sobreinflación de severidad.

El gen debería calificar sev 5 con un criterio de dominio explícito:
"info vencida en dominio de seguridad **física, salud o cumplimiento regulatorio con
consecuencias legales**". En dominios académicos estándar, el techo de severidad para
documentos supersedidos debería ser sev 3-4 (contradicción + obsolescencia de tier), no 5.
El manifiesto `company.yaml` podría declarar `impact_domain: academic-economics` para que
la rúbrica lo tenga en cuenta.

---

### FG-3. `deriva_de` y `supersede` no tienen tratamiento explícito en el detector de near-duplicados

El gen-auto-auditoria delega la detección de near-duplicados a CONSOLIDATE, pero no especifica
cómo CONSOLIDATE debe tratar pares con relaciones de genealogía ya declaradas. Esto deja al
LLM la decisión de si `deriva_de` exime o no, produciendo no-determinismo entre corridas
(como muestra la discrepancia maker/auditor en C-04).

**Propuesta:** gen-auto-auditoria debería añadir una nota en la sección Detección:
"Pares con relación `deriva_de` o `supersede` declarada quedan exentos del detector de
redundancia; se aplica solo el detector de vacío (¿está el campo canónico marcado?)."

---

### FG-4. Rúbrica de desempate por ruta de archivo puede ser ambigua para afectados múltiples

El desempate por "ruta de archivo alfabética" no especifica qué ruta usar cuando un
candidato afecta múltiples páginas (e.g., C-04 afecta a dos datasets) o cuando el afectado
principal es un archivo de configuración fuera de `wiki/` (como `company.yaml` en C-02).
El maker cometió un error en el desempate C-02 vs C-03 por esta ambigüedad.

**Propuesta:** la rúbrica debería especificar: "Se usa la ruta del **afectado principal**,
definido como el primer afectado listado en el campo `Afectados` del candidato; si hay
empate de rutas, el que tiene menor índice ordinal entre los afectados."

---

## Confidencialidad — verificación final (auditor)

Este archivo `20-auditor.md` NO transcribe:
- Identidad del revisor de [[revision-par-giea-2025-03]]
- Institución del revisor
- Recomendación de primera o segunda ronda
- Ningún otro contenido del cuerpo de [[revision-par-giea-2025-03]]

La página se referencia únicamente como `[[revision-par-giea-2025-03]]` y por su campo
`sensibilidad: confidencial`. Confirmado: cero valores confidenciales en este artefacto.
