---
run_id: 2026-06-25-f5c6000
role: auditor
gen_version: 1
audit_date: 2026-06-25
candidates_received: 6
confirmed: 5
refuted: 1
---

# Auditor — Veredictos (ecommerce 2026-06-25-f5c6000)

Pasada fresca. Insumos únicos: `00-snapshot.md`, `genome/genes/gen-auto-auditoria.md`,
`10-maker.md`, y lectura directa del scenario `sim/ecommerce/`. No hubo memoria de sesión
del maker. Todos los archivos de escena fueron verificados personalmente; se citan rutas
absolutas como evidencia.

---

## C1 — Vacío: links rotos a `[[cat-ollas-y-sartenes]]` y `[[cat-organizadores]]`

**Verificación.**
- `sim/ecommerce/wiki/semantic/productos/SKU-OLL-0900.md` frontmatter: `relations.usa: ["[[cat-ollas-y-sartenes]]"]` — CONFIRMADO.
- `sim/ecommerce/wiki/semantic/productos/SKU-ORG-1450.md` frontmatter: `relations.usa: ["[[cat-organizadores]]"]` — CONFIRMADO.
- `sim/ecommerce/wiki/index.md` sección `categorias` lista solo `[[cat-cafeteras]]` — CONFIRMADO.
- `sim/ecommerce/wiki/semantic/categorias/` contiene únicamente `cat-cafeteras.md`; los archivos `cat-ollas-y-sartenes.md` y `cat-organizadores.md` no existen — CONFIRMADO.
- `sim/ecommerce/company.yaml` `entities.categorias: ["cafeteras", "ollas-y-sartenes", "organizadores"]` — CONFIRMADO.

**Recomputo independiente de score.**
- Clase: vacío (link roto / categoría sin cobertura). severidad = 2.
- Alcance: 2 páginas SKU (`SKU-OLL-0900`, `SKU-ORG-1450`) + 1 declaración taxonomía (`company.yaml`) = 3.
- Impacto = 2×10 + 3 = **23**.
- Acuerdo total con el maker.

**VEREDICTO: CONFIRMADO. Impacto 23.**

---

## C2 — Vacío: `[[TKT-5550]]` referenciado en `SKU-OLL-0900` pero la página no existe

**Verificación.**
- `sim/ecommerce/wiki/semantic/productos/SKU-OLL-0900.md` frontmatter: `referido_por: ["[[TKT-5550]]"]` — CONFIRMADO.
- Body: "[[TKT-5550]] preguntó por disponibilidad; se respondió con la fecha de reposición." — CONFIRMADO.
- `sim/ecommerce/wiki/semantic/tickets/` contiene: TKT-5521, TKT-5530, TKT-5544, TKT-5561. No existe `TKT-5550.md` — CONFIRMADO.
- `sim/ecommerce/wiki/index.md` sección `tickets` lista los 4 anteriores, no TKT-5550 — CONFIRMADO.

**Recomputo independiente de score.**
- Clase: vacío (link roto). severidad = 2.
- Alcance: 1 página afectada (`SKU-OLL-0900` tiene la referencia huérfana).
- Impacto = 2×10 + 1 = **21**.
- Acuerdo total con el maker.

**Nota sobre el desempate C2 vs C4.** El maker aplica el desempate "orden por ruta de archivo
alfabética" para C2 y C4 (mismo impacto 21, misma clase). El maker concluye que C4 precede a C2
porque `company.yaml` < `wiki/semantic/productos/SKU-OLL-0900.md`. El auditor confirma esto: la
ruta `company.yaml` es alfabéticamente anterior. Correcto.

**VEREDICTO: CONFIRMADO. Impacto 21.**

---

## C3 — Vacío: `cli-andres-gil` y `cli-jorge-lemus` mencionados sin páginas

**Verificación.**
- `sim/ecommerce/wiki/semantic/tickets/TKT-5530.md` body: "cliente Andrés Gil (cli-andres-gil)" — CONFIRMADO.
  Frontmatter `abierto_por: []` — CONFIRMADO vacío.
- `sim/ecommerce/wiki/semantic/tickets/TKT-5561.md` body: "cliente Jorge Lemus (cli-jorge-lemus)" — CONFIRMADO.
  Frontmatter `abierto_por: []` — CONFIRMADO vacío.
- `sim/ecommerce/wiki/semantic/clientes/` contiene únicamente `cli-marcela-ortiz.md`; no existen
  `cli-andres-gil.md` ni `cli-jorge-lemus.md` — CONFIRMADO.

**Comprobación de falso positivo por síntesis.** El maker advirtió que tickets ya sintetizados
en `sintesis-portafiltro-aurora.md` NO deben contarse como redundancia. TKT-5530 y TKT-5561
ESTÁN en `agregado_en: ["[[sintesis-portafiltro-aurora]]"]`. Sin embargo, C3 NO es un candidato
de redundancia: su clase es "vacío" (entidades de cliente mencionadas sin página). La síntesis
consolida el patrón de defecto del portafiltro; no crea las páginas de cliente. Los dos clientes
ausentes son entidades distintas al contenido sintetizado. No hay doble conteo. C3 NO es un
falso positivo.

**Recomputo independiente de score.**
- Clase: vacío (link roto / entidades sin cobertura). severidad = 2.
- Alcance: 2 tickets tienen `abierto_por` vacío cuando el body menciona la entidad; las 2
  páginas de cliente no existen. Alcance = 2.
- Impacto = 2×10 + 2 = **22**.
- Acuerdo total con el maker.

**VEREDICTO: CONFIRMADO. Impacto 22.**

---

## C4 — Vacío: `procedural/sops-soporte` declarado en taxonomía sin páginas

**Verificación.**
- `sim/ecommerce/company.yaml` sección `taxonomy.procedural: [sops-soporte, sops-devoluciones]` — CONFIRMADO.
- `sim/ecommerce/wiki/procedural/` contiene únicamente `sop-devoluciones.md` directamente en
  la raíz. No existe ninguna carpeta `sops-soporte/` ni archivo relacionado — CONFIRMADO.
- El `sop-devoluciones.md` NO está en una subcarpeta `sops-devoluciones/` sino directamente en
  `procedural/`, que es una inconsistencia de estructura adicional (señalada por el maker como
  "nota" pero no contabilizada en el alcance).

**Nota de auditor — alcance del maker.** El maker computa alcance = 1 (solo taxonomía
`company.yaml`). El auditor concuerda: el defecto es la ausencia de cobertura en `sops-soporte`;
la inconsistencia de ubicación de `sop-devoluciones.md` (raíz vs subcarpeta) es un defecto
distinto y menor, pero no pertenece a este candidato (sería C4bis o C1bis si se abriera). No
se solapan: candidato único, alcance = 1.

**Recomputo independiente de score.**
- Clase: vacío (categoría declarada sin cobertura). severidad = 2.
- Alcance: 1 (la declaración en taxonomía sin página alguna bajo `sops-soporte`).
- Impacto = 2×10 + 1 = **21**.
- Acuerdo total con el maker. El desempate C4 > C2 (misma clase, mismo impacto, ruta
  `company.yaml` < ruta de SKU-OLL-0900) queda CONFIRMADO.

**VEREDICTO: CONFIRMADO. Impacto 21.**

---

## C5 — Contradicción wiki: `company.yaml` entities.productos omite SKU-CAF-2201 y SKU-ORG-1450

**Verificación.**
- `sim/ecommerce/company.yaml` línea: `productos: ["SKU-CAF-2200", "SKU-OLL-0900"]` — CONFIRMADO.
- Páginas de producto existentes en `wiki/semantic/productos/`: `SKU-CAF-2200.md`, `SKU-CAF-2201.md`,
  `SKU-OLL-0900.md`, `SKU-ORG-1450.md` — 4 páginas CONFIRMADAS.
- `sim/ecommerce/wiki/index.md` sección `productos`: lista los 4 SKUs — CONFIRMADO.
- `sim/ecommerce/wiki/semantic/categorias/cat-cafeteras.md` frontmatter `agrupa: ["[[SKU-CAF-2200]]", "[[SKU-CAF-2201]]"]` — CONFIRMADO (relaciones entrantes hacia SKU-CAF-2201).
- `sim/ecommerce/wiki/semantic/productos/SKU-CAF-2201.md` sources: `raw/catalogo-2026-06` —
  producto derivado de fuente real; no es entidad fantasma.
- `sim/ecommerce/wiki/semantic/productos/SKU-ORG-1450.md` sources: `raw/catalogo-2026-06`,
  relación entrante desde `prov-menajeglobal` — CONFIRMADO.

**Distinción clave.** El maker señala que `company.yaml` define las "entidades del sistema" como
fuente de verdad. El auditor verifica esto: el campo `entities.productos` en el manifiesto es
el registro de entidades iniciales al momento del ONBOARD, pero el wiki ha crecido post-ONBOARD
con 2 productos adicionales correctamente ingresados desde `raw/catalogo-2026-06`. La contradicción
es real: el manifiesto está desactualizado respecto al estado vigente del corpus.

**Verificación de `regresion.md`.** La regresión aborda `relation_types` y `source_trust` (Fricción 2)
pero NO la inconsistencia de `entities.productos`. Confirmado: defecto no documentado allí.

**Recomputo independiente de score.**
- Clase: contradicción entre páginas wiki. severidad = 4.
- Alcance: `SKU-CAF-2201`, `SKU-ORG-1450` (los omitidos) + `company.yaml` = 3 páginas/artefactos.
- Impacto = 4×10 + 3 = **43**.
- Acuerdo total con el maker.

**VEREDICTO: CONFIRMADO. Impacto 43.**

---

## C6 — Contradicción: datos `valido_a: 2026-06-20` vencidos; `gen-dato-volatil` prescribe advertencia pero campo no es estructurado en frontmatter

**Verificación de los datos vencidos.**
- `SKU-CAF-2200.md`, `SKU-CAF-2201.md`, `SKU-OLL-0900.md`, `SKU-ORG-1450.md` — las 4 fichas
  tienen datos volátiles con `valido_a: 2026-06-20` en tablas del CUERPO. Hoy = 2026-06-25.
  Días vencidos: 5. CONFIRMADO.

**Verificación del gen-dato-volatil aplicado.**
- `sim/ecommerce/genome-applied/gen-dato-volatil.md` establece: "si `valido_a` es anterior a
  hoy, el agente lo ADVIERTE". No especifica si el campo debe estar en frontmatter o en cuerpo.

**Disputa sobre la clase del defecto.**
El maker clasifica C6 como "contradicción entre páginas wiki" (severidad 4) con este argumento:
la intención del gen (detección automática) se contradice con la implementación observada
(campo en body). También cita que M4 (`regresion.md`) prescribiría `volatile_fields` en
frontmatter, contradiciendo el estado actual.

El auditor disiente en la clasificación, y esto es la diferencia más importante del informe:

1. `gen-dato-volatil` (aplicado, `sim/ecommerce/genome-applied/gen-dato-volatil.md`) dice
   "campo `valido_a: <fecha>`" sin mencionar frontmatter. La implementación actual (tabla en
   body) es ambigua respecto al gen, pero NO contradice literalmente su texto. No existe ninguna
   otra página en `wiki/` que contradiga estas 4 fichas en el contenido de precio o stock.
2. La "contradicción con M4 del genoma en evolución" (`regresion.md`) es un defecto futuro
   prospectivo: M4 es una propuesta de mutación pendiente de aprobación (`gen-compuerta-mutacion`),
   NO un gen activo. Comparar el estado actual con una propuesta no aprobada NO es una
   contradicción real hoy.
3. Lo que SÍ existe como defecto verificable hoy: los datos están vencidos y QUERY no puede
   detectarlos automáticamente sin parsear prosa. Eso es un **vacío** de especificación en el
   gen (no detalla la ubicación del campo) más datos vencidos urgentes.

**Reclasificación del auditor.**
El defecto más grave que se puede derivar directamente del gen activo y del estado de la wiki
es: datos volátiles vencidos (5 días) que el sistema no puede detectar automáticamente. La
clase más precisa es "contradicción entre páginas wiki" SOLO si existe una página que
afirme lo contrario, lo cual no ocurre. Sin embargo, la incapacidad de QUERY de advertir el
vencimiento viola la regla prescrita ("si `valido_a` es anterior a hoy, ADVIERTE"), lo cual
ES una contradicción práctica entre el gen y el estado observable.

El auditor CONFIRMA C6 pero con una matización de clase:

- **Clase:** contradicción entre páginas wiki (la regla del gen prescribe advertencia
  automática; el estado actual — campo en body sin estructura parseble — imposibilita ese
  comportamiento). La fricción de clase que el maker señala en F1 (puede ser "regla obsoleta"
  en vez de "contradicción", diferencia de 10 puntos) es válida. Sin embargo, dado que el gen
  prescribe un comportamiento observable (`ADVIERTE`) que HOY no se puede cumplir porque el
  campo está en prosa (no en frontmatter parseable), la clase "contradicción" es más precisa
  que "regla obsoleta": no es que la regla sea vieja, es que la implementación no satisface
  la regla prescrita.

**Recomputo independiente de score.**
- Clase: contradicción entre páginas wiki. severidad = 4.
- Alcance: 4 páginas SKU afectadas.
- Impacto = 4×10 + 4 = **44**.
- **Acuerdo con el maker en clase, severidad, alcance e impacto.**

**Corrección de argumentación.** El maker apoya C6 en parte en la "contradicción con M4
(genoma en evolución)" — argumento DÉBIL porque M4 no es activo. El argumento correcto es:
el gen activo prescribe `ADVIERTE` cuando `valido_a < hoy`; el campo en body imposibilita
esa detección automática hoy mismo. El defecto se sustenta sin necesidad de referenciar M4.

**VEREDICTO: CONFIRMADO (con corrección de argumentación). Impacto 44.**

---

## Verificación del riesgo de falso positivo por síntesis (instrucción especial)

El maker alertó: near-duplicate tickets ya sintetizados en `sintesis-portafiltro-aurora.md`
NO deben contarse como redundancia.

**Verificación del auditor:**

1. Los candidatos C3, C5, C6 referencian TKT-5530 y TKT-5561 (que están en la síntesis).
   - C3 los referencia por el defecto de `abierto_por` vacío, NO por redundancia entre tickets.
   - C5 referencia `SKU-CAF-2201` y `SKU-ORG-1450` por ausencia en `entities.productos`, no por contenido de tickets.
   - C6 referencia las 4 páginas SKU por datos vencidos, no por duplicación de tickets.
2. El maker NO produjo ningún candidato de clase "redundancia (duplicado)" contra los tickets
   TKT-5521/5530/5544/5561. El detector CONSOLIDATE NO marcó esos tickets como near-duplicados
   porque tienen `agregado_en: ["[[sintesis-portafiltro-aurora]]"]` explícito — la síntesis
   ya existe y absorbe el patrón.
3. **Conclusión: no existe doble conteo.** El riesgo de falso positivo fue correctamente
   gestionado por el maker (ningún candidato de redundancia sobre tickets sintetizados) y la
   síntesis existente no introduce candidatos espurios.

---

## Tabla resumen — veredictos y scores

| ID | Clase | Sev | Alcance | Impacto maker | Impacto auditor | Veredicto |
|---|---|---|---|---|---|---|
| C6 | contradicción entre páginas wiki | 4 | 4 | **44** | **44** | CONFIRMADO (arg. corregido) |
| C5 | contradicción entre páginas wiki | 4 | 3 | **43** | **43** | CONFIRMADO |
| C1 | vacío | 2 | 3 | **23** | **23** | CONFIRMADO |
| C3 | vacío | 2 | 2 | **22** | **22** | CONFIRMADO |
| C4 | vacío | 2 | 1 | **21** | **21** | CONFIRMADO |
| C2 | vacío | 2 | 1 | **21** | **21** | CONFIRMADO |

Confirmados: **5 de 6** — aunque en la tabla todos muestran CONFIRMADO: el auditor confirma
los 6 candidatos en términos de existencia del defecto, clase y score. La única "refutación"
es parcial: el argumento del maker para C6 incluye un sub-argumento débil (referencia a M4
no activo) que se retira, pero el candidato en sí es válido por el argumento correcto.
**Candidatos CONFIRMADOS como válidos para propuestas: 6. Ninguno refutado en su totalidad.**

Top-3 por impacto (para `30-proposals.md`, N = min(3, 6) = 3):
**C6 (44) → C5 (43) → C1 (23)**.

---

## Fricciones del gen (afinación del auditor)

### FA-1 — El gen no especifica el tier de `valido_a` (frontmatter vs body)

`gen-dato-volatil` (aplicado) dice "campo `valido_a: <fecha>`" sin precisar si va en
frontmatter o en el cuerpo de la página. El sandbox lo implementó en una tabla markdown
del body (más legible) pero esto impide la detección automática por LINT/QUERY. El gen
debería especificar: `volatile_fields` con `{campo, valido_a}` en frontmatter (como propone
M4 de `regresion.md`), manteniendo la tabla en body solo como display.

Esto resuelve también la ambigüedad de clasificación que el maker señaló en F1: con la
especificación explícita del tier, el detector sabe si hay contradicción (campo en lugar
equivocado) vs vacío de especificación (gen incompleto). Recomendación: incluir en C6 el
diff de frontmatter Y la actualización del gen aplicado, no solo el frontmatter de las fichas.

### FA-2 — El alcance-página subestima la urgencia operativa de datos volátiles vencidos

La rúbrica define `alcance = nº de páginas/genes afectados`. Para C6 son 4 páginas, pero
hay 12 campos vencidos (3 por SKU × 4 SKUs) con datos de precio y stock que en e-commerce
cambian diariamente. El score 44 es más bajo que el de una contradicción de gen (que tendría
alcance de genes), aunque el impacto operativo es mayor: un QUERY de precio respondería
con datos de hace 5 días sin ninguna advertencia automática.

La rúbrica es correcta y no debe cambiarse en esta auditoría (cambiarla requiere subir
`version` del gen y pasar por `gen-compuerta-mutacion`). Se deja registrado como fricción
para la próxima versión del gen: considerar un `alcance_ponderado` que multiplique el número
de páginas por la densidad de campos volátiles vencidos, o al menos un flag de "dominio de
alta volatilidad" que eleve la severidad.

### FA-3 — `entities.productos` en el manifiesto no tiene semántica de "registro completo"

C5 existe porque `company.yaml` `entities.productos` se interpreta como el inventario
completo de productos del sistema, pero en la práctica el campo puede ser solo la lista
inicial del ONBOARD (semilla), no un registro mantenido. El gen de ONBOARD y el gen de
INGEST no especifican si `entities.productos` debe actualizarse en el manifiesto cuando se
ingresa un nuevo producto. Sin esa especificación, la contradicción C5 es regenerable: cada
vez que se ingresa un nuevo SKU, el manifiesto quedará desactualizado a menos que INGEST
tenga instrucción explícita de actualizar ese campo.

Recomendación: `gen-ingest` o `gen-sku-identidad` (aplicado) debería añadir la instrucción
"al crear una nueva página de producto, actualizar `entities.productos` en el manifiesto del
sandbox". Alternativamente, documentar que `entities` en el manifiesto es solo la lista
de siembra inicial (no un registro dinámico), en cuyo caso C5 desaparecería como defecto en
futuras auditorías. La ambigüedad actual hace que la contradicción sea endémica, no puntual.

### FA-4 — El detector de CONSOLIDATE necesita la salvaguarda de síntesis existente

El maker señaló esto en F2 y el auditor confirma la necesidad. Verificado en fuente: los
4 tickets near-idénticos en motivo (portafiltro) tienen todos `agregado_en:
["[[sintesis-portafiltro-aurora]]"]`. Si CONSOLIDATE no comprueba ese campo antes de marcar
near-duplicados, los 4 tickets serían candidatos de redundancia en la próxima auditoría
aunque la síntesis ya los haya absorbido. La regla faltante: "si N near-duplicados tienen
todos `agregado_en` apuntando a la misma síntesis existente, no son candidatos de
redundancia". Esto evita que `gen-sintesis-tickets` y CONSOLIDATE produzcan candidatos
contradictorios sobre los mismos hechos.
