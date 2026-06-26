---
run_id: 2026-06-25-f5c6000
role: auditor
scenario: legal
date: 2026-06-25
gen_auditoria_version: 1
inputs_used:
  - sim/legal/audit/runs/2026-06-25-f5c6000/00-snapshot.md
  - genome/genes/gen-auto-auditoria.md
  - sim/legal/audit/runs/2026-06-25-f5c6000/10-maker.md
  - sim/legal/ (scenario source — read-only)
---

# 20-auditor — Veredictos independientes (sandbox legal)

Pasada fresca, adversarial. Los insumos se leen directamente desde disco; no se
hereda memoria de sesión del maker. Todas las referencias a páginas
`secreto_profesional: true` se expresan ÚNICAMENTE por `[[link]]`/id + nombre de
campo — ningún valor sensible transcrito.

---

## Metodología

1. Re-derivación independiente de cada candidato desde las fuentes del escenario
   (`sim/legal/wiki/`, `sim/legal/genome-applied/`, `sim/legal/company.yaml`).
2. Verificación de la autodetección del falso positivo (C6).
3. Recomputo de scores con la rúbrica canónica `impacto = severidad×10 + alcance`.
4. Leak-check: búsqueda de tokens sensibles en `sim/legal/audit/`.
5. Sección "Fricciones del gen" con perspectiva propia.

---

## Veredictos por candidato

### C1 — Campo `vigencia:` huérfano (sin gen que lo defina ni valide)

**Re-derivación propia:**

Lectura directa de los cuatro archivos wiki citados:

- `art-1154-codigo-civil.md`: frontmatter contiene `vigencia: vigente`. Campo
  presente.
- `art-1124-codigo-civil.md`: frontmatter NO contiene campo `vigencia`. Campo
  ausente — asimetría confirmada.
- `reforma-cc-2026.md`: frontmatter contiene `vigencia: no-vigente`. Campo
  presente.
- `jurisprudencia-moderacion-clausula-penal.md`: frontmatter contiene
  `vigencia: en-revision`. Campo presente.

Verificación del genoma: los tres genes de `genome-applied/` son
`gen-secreto-profesional`, `gen-version-contrato` y `gen-conflicto-interes`.
Ninguno define el campo `vigencia` ni sus valores válidos. El archivo
`regresion.md` confirma explícitamente: "El campo `vigencia:` que aparece en
las páginas wiki actuales es residuo del run anterior (estilo seed), no está
respaldado por ningún gen del genoma de 16: LINT no lo conoce ni lo valida."

**Clase:** El defecto es una inconsistencia de esquema entre páginas del mismo
tier (unas tienen el campo, `art-1124-cc` no lo tiene) y la ausencia total de
gen respaldo. Esto impide que LINT valide o detecte páginas con `vigencia:
derogada` no detectada. La clase más alta aplicable es "contradicción entre
páginas wiki" (severidad 4), no meramente "vacío" (severidad 2), por la
inconsistencia de esquema entre pares.

**Alcance:** El maker cuenta 4 páginas afectadas. Auditor lo confirma: las
cuatro páginas citadas están directamente involucradas. Correcto.

**Score maker:** 4×10 + 4 = 44. **Score auditor: 44. Coincide.**

**VEREDICTO: CONFIRMADO.**

---

### C2 — `contrato-distribucion-v2` cita como `sources` la fuente raw de v3

**Re-derivación propia:**

Lectura de `contrato-distribucion-v2.md`:
```
sources:
  - "[[raw/2026-05-20-contrato-distribucion-v3]]"
```
Lectura de `contrato-distribucion-v3.md`:
```
sources:
  - "[[raw/2026-05-20-contrato-distribucion-v3]]"
```

Ambas páginas citan exactamente la misma fuente raw (`2026-05-20-contrato-
distribucion-v3`). La página v2 es la versión histórica anterior: su `sources`
debería apuntar al documento raw que representó en su momento (el contrato v2
original), o estar vacío si ese documento no existe en `raw/`. Al apuntar al
raw de v3, la página histórica declara su evidencia en un documento que no la
representa — contradicción factual directa.

**Verificación del gen:** `gen-version-contrato` dice que la versión anterior
"cita su fuente en `raw/`". No especifica que el `sources` deba ser diferente
de la versión nueva, pero la consecuencia lógica es que cada página cite su
propia fuente: la función de `sources` es la trazabilidad de procedencia. Una
página histórica apuntando al raw de su sucesor rompe esa trazabilidad.

**Nota adicional del auditor:** el maker describe como defecto secundario la
ausencia de campo `reemplazada_por` en v2. Auditor coincide en que eso es
menor (el gen no lo exige — v3 declara `reemplaza: [v2]` y eso es suficiente
según la letra del gen). El defecto real y no ambiguo es el `sources` incorrecto.

**Alcance:** 2 páginas. Confirmado.

**Score maker:** 4×10 + 2 = 42. **Score auditor: 42. Coincide.**

**VEREDICTO: CONFIRMADO** (defecto principal = sources incorrecto en v2;
back-link es mejora opcional, no defecto exigido por el gen).

---

### C3 — `contradice` asimétrico: `reforma-cc-2026` declara la relación; las páginas afectadas no la declaran de vuelta

**Re-derivación propia:**

Lectura de `reforma-cc-2026.md`:
```
relations:
  contradice:
    - "[[art-1154-codigo-civil]]"
    - "[[jurisprudencia-moderacion-clausula-penal]]"
```

Lectura de `jurisprudencia-moderacion-clausula-penal.md`:
```
relations:
  contradice: []
```

Lectura de `art-1154-codigo-civil.md`:
```
relations:
  contradice: []
```

La asimetría es real. `reforma-cc-2026` advierte que contradice a los otros
dos, pero esos dos no declaran que son contradichos. Un agente navegando desde
`jurisprudencia-moderacion-clausula-penal` o desde `art-1154-codigo-civil` no
descubre la amenaza de la reforma en su grafo de relaciones salientes — solo
existe una nota en el body text de `art-1154-cc.md` ("Amenazada por
[[reforma-cc-2026]]"), pero ese aviso en prose no es navegable por LINT ni
por QUERY semántico.

**Observación crítica del auditor:** El gen base [[gen-lint]] (referenciado en
`gen-auto-auditoria`) no especifica explícitamente que `contradice` deba ser
simétrico. Sin embargo, el propósito de las relaciones en CEREBRO es la
navegabilidad del grafo. Una relación bidireccional declarada solo en un
extremo produce descubrimiento incompleto, lo cual en un dominio legal (donde
no conocer una amenaza normativa tiene consecuencias prácticas) equivale a
información incorrecta por omisión. El maker razona correctamente que la
asimetría es un defecto.

**Alcance:** El maker cuenta 3 páginas. Auditor confirma: `reforma-cc-2026`,
`jurisprudencia-moderacion-clausula-penal`, `art-1154-codigo-civil`. Correcto.

**Score maker:** 4×10 + 3 = 43. **Score auditor: 43. Coincide.**

**VEREDICTO: CONFIRMADO.**

---

### C4 — Carpeta `semantic/dictamenes` declarada en taxonomy pero vacía

**Re-derivación propia — DIVERGENCIA FACTUAL:**

El maker afirma: "carpeta no existe en `sim/legal/wiki/semantic/`."

Auditor verificó directamente el sistema de archivos:
- `sim/legal/wiki/semantic/dictamenes/` **SÍ EXISTE** como directorio, pero
  está vacío (cero archivos).

Esto modifica la naturaleza del defecto pero no lo elimina:
- El defecto no es "carpeta ausente" sino "carpeta existente pero sin ninguna
  página ni stub".
- La taxonomy declara la carpeta y el tipo de documento `dictamen` (en
  `document_types`). Ninguna página del corpus tiene `type: dictamen`.
- El defecto persiste como "categoría declarada sin cobertura de contenido",
  que sigue siendo clase "vacío" (severidad 2).

**Corrección del diff:** el maker propone "crear un `.gitkeep`" — pero la
carpeta ya existe. El diff correcto sería: crear un stub de página
`dictamenes/00-leeme.md` o `dictamenes/placeholder.md` para que la categoría
sea navegable, o bien eliminar `dictamenes` de `taxonomy.semantic` y de
`document_types` en `company.yaml` si no se planean dictámenes en este
sandbox.

**Alcance:** La severidad (2) y la clase (vacío) no cambian. El alcance sigue
siendo 1 (la categoría entera). El score no cambia.

**Score maker:** 2×10 + 1 = 21. **Score auditor: 21. Coincide** (pese a la
corrección factual del estado de la carpeta).

**VEREDICTO: CONFIRMADO CON CORRECCIÓN FACTUAL.** La carpeta existe pero
vacía; el diff del maker es parcialmente incorrecto (`.gitkeep` innecesario).

---

### C5 — Abogados y juzgado en carpeta `casos/` (tipo vs. carpeta mal alineados)

**Re-derivación propia:**

Lectura de `company.yaml`:
```yaml
entities:
  clientes: [...]
  casos: [...]
  contrapartes: [...]
  juzgados: ["Juzgado de lo Mercantil nº 3 de Madrid"]
  abogados: ["Lucía Vega", "Mateo Alcántara"]

taxonomy:
  semantic: [clientes, casos, contrapartes, contratos, jurisprudencia, normativa, dictamenes]
```

Las categorías `juzgados` y `abogados` aparecen en `entities` pero no en
`taxonomy.semantic`. Las páginas [[lucia-vega]], [[mateo-alcantara]] y
[[juzgado-mercantil-3-madrid]] residen bajo `wiki/semantic/casos/`.

Confirmado: hay tres entidades con tipo (`abogado`, `entidad` de tipo juzgado)
que no corresponden a la carpeta `casos/`, y la taxonomy no declara carpetas
para esos tipos. El principio de navegación limpia por relaciones se viola
porque no hay ruta de carpeta que distinga el tipo de entidad.

**Matiz del auditor:** el defecto existe, pero en la práctica el frontmatter
de cada página declara su `type` correctamente y las relaciones son
navegables. El impacto es de convención estructural, no de defecto que rompa
una operación del genoma. Se confirma como vacío de categoría.

**Alcance:** 3 páginas. Confirmado.

**Score maker:** 2×10 + 3 = 23. **Score auditor: 23. Coincide.**

**VEREDICTO: CONFIRMADO.**

---

### C6 — Falso positivo autodeclarado: enlace de [[minuta-2026-05-12-andina]] desde [[caso-exp-2026-0142]]

**Juicio independiente del auditor:**

El gen `gen-secreto-profesional` dice:
> "NO se enlaza como conocimiento abierto desde `index.md`; se restringe a la
> carpeta del cliente o caso (`wiki/semantic/clientes/` o
> `wiki/semantic/casos/`)."

Lectura independiente de `wiki/index.md`: no contiene enlace directo a
[[minuta-2026-05-12-andina]] ni a [[distribuidora-andina]]. El índice menciona
[[caso-exp-2026-0142]] (caso como punto de entrada) con la nota "contiene
páginas confidenciales no listadas: minuta de estrategia" — pero sin enlazar
la minuta directamente. Esto respeta la regla del gen.

Lectura de [[caso-exp-2026-0142]] (campo: body text / campo: `relations`):
la página menciona [[minuta-2026-05-12-andina]] en su cuerpo ("Detalle
sensible en [[minuta-2026-05-12-andina]]") pero no en `relations` formales.
Ambas páginas tienen `secreto_profesional: true`. El gen restringe los enlaces
desde `index.md`; no prohíbe que dos páginas confidenciales se enlacen entre
sí dentro de las carpetas permitidas.

**Veredicto auditor: C6 es efectivamente un falso positivo.** El enlace
case→minuta es legítimo bajo el gen porque: (1) el index no enlaza la minuta
directamente; (2) la minuta está en `wiki/semantic/casos/`, que es la carpeta
permitida; (3) ambos extremos del enlace son `secreto_profesional: true`. La
cadena de acceso es correcta por diseño (se llega a la minuta navegando desde
el caso, no desde el índice abierto).

**VEREDICTO: FALSO POSITIVO CONFIRMADO.** El maker lo identificó
correctamente. No es un defecto real.

---

## Tabla consolidada (recomputed)

| id | Descripción | Clase | Sev | Alcance | Impacto | Score maker | Score auditor | Veredicto |
|---|---|---|---|---|---|---|---|---|
| C1 | Campo `vigencia:` huérfano | contradicción wikis | 4 | 4 | **44** | 44 | **44** | CONFIRMADO |
| C3 | `contradice` asimétrico (reforma↔jurisprud+art-1154) | contradicción wikis | 4 | 3 | **43** | 43 | **43** | CONFIRMADO |
| C2 | `sources` de v2 apunta a raw de v3 | contradicción wikis | 4 | 2 | **42** | 42 | **42** | CONFIRMADO |
| C5 | Abogados/juzgado en carpeta `casos/` | vacío (taxonomy) | 2 | 3 | **23** | 23 | **23** | CONFIRMADO |
| C4 | `dictamenes` declarado pero sin contenido | vacío | 2 | 1 | **21** | 21 | **21** | CONFIRMADO* |
| C6 | Enlace case→minuta (secreto_profesional) | — | 0 | — | 0 | 0 | 0 | FALSO POSITIVO |

`*` C4: corrección factual — la carpeta existe (vacía), el maker la declaró
ausente. Score no cambia; el diff propuesto necesita ajuste.

**Resumen: 5 confirmados / 6 candidatos totales (incluyendo C6 falso positivo).**
**Sin discrepancias de score. Una corrección factual en C4 (estado de carpeta).**

Top-3 para propuestas: **C1 (44) → C3 (43) → C2 (42).**

---

## Leak-check de artefactos del maker

Se buscaron en `sim/legal/audit/` los siguientes tokens sensibles identificados
en las fuentes `secreto_profesional: true` del escenario:

| Token / patrón buscado | Resultado |
|---|---|
| Cifra de margen de negociación (valor numérico sensible de [[minuta-2026-05-12-andina]], campo: body/fuente raw) | NO encontrado |
| Nombre del representante legal del cliente (campo: fuente raw, no reproducida) | NO encontrado |
| Texto de estrategia procesal (debilidad del cliente) de [[caso-exp-2026-0142]], campo: body | NO encontrado |
| Texto "evitar prensa" | NO encontrado |
| Referencia a pagos tardíos del propio cliente (texto literal de raw) | NO encontrado |

**Resultado del leak-check: LIMPIO.** El artefacto `10-maker.md` referencia
las tres páginas confidenciales exclusivamente por `[[link]]` y nombre de
campo frontmatter. Ningún valor sensible fue transcrito.

Nota: La mención de "EXP-2026-0142" en `10-maker.md` (línea 90, campo
`Evidencia` de C5) no es un leak: el identificador del expediente aparece
en `wiki/index.md` como conocimiento abierto y no está protegido por
`gen-secreto-profesional`.

---

## Fricciones del gen (`gen-auto-auditoria` v1 en dominio legal)

El maker identificó seis fricciones relevantes. El auditor las evalúa y añade
perspectiva propia.

### F1 — Vigencia por evento, no por fecha (maker: correcto; auditor: confirma y amplía)

La rúbrica define "info vencida en dominio de seguridad" (severidad 5) usando
`valido_hasta < hoy`. En legal, la caducidad más crítica es la normativa: no
se vence por fecha de calendario sino por evento externo (sentencia del
Tribunal Supremo, promulgación de ley). El campo `valido_hasta` de
`gen-vigencia-temporal` no captura esto.

Consecuencia concreta: `jurisprudencia-moderacion-clausula-penal` tiene
`vigencia: en-revision` por una amenaza normativa real, pero LINT no elevaría
este hecho porque no hay `valido_hasta` vencido. La clase de severidad 5
queda inerte en este sandbox. Confirmado.

**Adición del auditor:** este vacío es precisamente el núcleo de C1 y C3 de
este run. La propuesta de afinación del maker (añadir detección por
`vigencia: en-revision|derogada|no-vigente`) es correcta, pero requeriría
que `gen-lint` conozca el campo — lo cual, a su vez, requiere que el campo
esté formalizado en un gen (lo que C1 propone crear). La cadena de
dependencias es: C1 → gen-vigencia-normativa → gen-lint actualizado → clase
severidad 5 operativa. Este run está bien secuenciado: C1 es la pieza base.

### F2 — Dominio de mayoría confidencial (maker: correcto; auditor: matiza)

El gen hereda `gen-confidencialidad` que asume que el dominio es
mayoritariamente abierto y la confidencialidad es la excepción. En legal, la
inversión es real: minutas, estrategia, margen de negociación y datos del
cliente representan la mayor parte del conocimiento operativo.

**Matiz del auditor:** el impacto práctico de esta inversión en el contexto de
AUDIT es que los defectos más relevantes (los que afectan directamente la
estrategia) podrían residir en páginas confidenciales, pero el diff de
propuesta no puede transcribir el contenido ni el valor afectado. El canal de
revisión restringida que el maker menciona como necesario (con control de
acceso real) es correcto pero está fuera del alcance de CEREBRO/markdown. La
fricción es real e inherente al modelo de seguridad del sistema.

**Adición del auditor — default de sensibilidad:** para el sector legal sería
correcto invertir el default de INGEST: `sensibilidad: confidencial` a menos
que se declare explícitamente `sensibilidad: publico`. Esto requeriría un
parámetro de manifiesto (`default_sensibilidad: confidencial`) que hoy no
existe en `gen-auto-auditoria` ni en `gen-confidencialidad`. Es una propuesta
de afinación de alcance mayor — apropiada para una propuesta [[gen-evolve]].

### F3 — Encadenamiento de confidencialidad (maker: identifica el problema; auditor: confirma como riesgo latente)

El gen modela confidencialidad por página individual, no por subgrafo. Un
agente que navega el grafo puede llegar a información de estrategia del caso
(campo `body` de [[caso-exp-2026-0142]]) simplemente siguiendo la ruta
index → caso. El gen dice que `index.md` no debe enlazar directamente las
páginas confidenciales — y no lo hace — pero sí enlaza al caso en sí, que
ES confidencial.

**Posición del auditor:** el enlace de index a [[caso-exp-2026-0142]] es
inevitable en un sistema de conocimiento: el caso es la entidad central.
La protección real debe ser a nivel de acceso (quién puede abrir el archivo),
no de grafo. El gen establece la restricción de enlace como proxy de acceso,
que es una aproximación razonable dentro de las limitaciones de un sistema
markdown. No es un defecto del gen sino un límite declarado del modelo.

### F4 — gen-conflicto-interes como vector de fuga (maker: identifica; auditor: confirma y acota)

`gen-conflicto-interes` accede a las páginas de ambos lados (cliente y
contraparte) para hacer el cruce. Si alguna de esas páginas es confidencial,
el cruce en sí no genera fuga (no reproduce contenido), pero la regla del gen
("marca `relations.contradice`") crea un enlace entre las dos páginas. Ese
enlace podría ser navegable por alguien que solo tiene acceso a la contraparte.

**Posición del auditor:** en el sandbox actual no hay conflicto real
(Distribuidora Andina es cliente, Logística del Norte es contraparte —
entidades distintas sin solapamiento). El riesgo es latente, no
materializado. La afinación correcta sería que `gen-conflicto-interes`
especifique que la alerta se emite en un canal restringido (solo al
`mutation_approver`) sin crear el enlace cruzado en el grafo público.

### F5 — Rúbrica no distingue alcance estático vs. dinámico (maker: identifica; auditor: confirma con calificación)

La rúbrica cuenta `alcance` como número de páginas/genes afectados
actualmente. Un gen faltante (como el de `vigencia-normativa` que falta en
`genome-applied/`) tiene `alcance = 1` en el cómputo actual, pero un impacto
dinámico sobre todas las páginas de normativa/jurisprudencia que se ingieran
en el futuro.

**Posición del auditor:** el maker tiene razón en que la rúbrica es ciega al
alcance dinámico. Sin embargo, cambiar la rúbrica requiere subir `version`
del gen y pasar por [[gen-compuerta-mutacion]]. Para este run, la rúbrica
vigente (v1) es la que aplica — las propuestas se puntúan con ella. La
observación es apropiada para una propuesta futura de EVOLVE.

### F6 — Regla de fusión de candidatos: "mismo defecto" mal especificada (maker: identifica; auditor: confirma)

El gen dice que si LINT y el detector de auditoría marcan el mismo defecto, se
fusionan en un candidato. Pero "mismo defecto" no está definido: ¿mismo objeto
(página/gen) o misma causa raíz? C1 (campo `vigencia` huérfano) y C3
(`contradice` asimétrico) tienen causa raíz parcialmente relacionada (ambos
emergen de la ausencia de un gen de vigencia normativa), pero tienen objetos
distintos y páginas distintas. El maker los mantiene separados — decisión
correcta bajo la definición más restrictiva ("mismo objeto"). El gen debería
aclarar qué "mismo" significa.

---

## Confirmación de confidencialidad (este artefacto)

Las tres páginas `secreto_profesional: true` del sandbox (`[[caso-exp-2026-0142]]`,
`[[minuta-2026-05-12-andina]]`, `[[distribuidora-andina]]`) se referencian en
este documento exclusivamente por su `[[link]]` y por el nombre del campo
frontmatter inspeccionado. **Ningún valor sensible** (cifra de negociación,
nombre de representante legal, detalle estratégico, debilidad procesal,
preferencia del cliente) ha sido transcrito en este artefacto.
