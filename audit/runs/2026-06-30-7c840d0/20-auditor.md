---
run_id: 2026-06-30-7c840d0
rol: auditor
fecha: 2026-06-30
gen_version: gen-auto-auditoria v3
fuente: pase adversarial independiente (insumos = 00-snapshot + gen-auto-auditoria + 10-maker)
---

# 20 — Auditor: veredictos por candidato (pase fresco, adversarial)

Barrera maker≠auditor honrada: re-derivé cada evidencia abriendo el archivo citado en el árbol
del SHA `7c840d0` (HEAD verificado; única ruta no rastreada = esta carpeta de la corrida, según
la nota de transparencia del snapshot). Un candidato sobrevive SOLO si re-deriva y aguanta refutación.

Rúbrica aplicada (gen-auto-auditoria v3): `impacto = severidad*10 + alcance`; conteo de `alcance`
por clase; desempate (1) impacto, (2) orden de filas de la tabla de severidad, (3) ruta alfabética.
Cada defecto pertenece a UNA sola clase (la de mayor severidad aplicable).

---

### C1 — Default de `sensibilidad` contradictorio entre dos genes activos → VERDICT: CONFIRMED
- re-derivación: `gen-frontmatter-obligatorio.md:11-12` (v3, active) lista `sensibilidad`
  ([[gen-confidencialidad]], default **`interno`**) — afirma el default plano `interno`.
  `gen-confidencialidad.md:8-10` (v2, active): "default tomado de `default_sensibilidad` del
  manifiesto si lo declara —dominios sensibles como legal/salud suelen fijar `confidencial`—; si
  no existe, `interno`". Ambos son genes ACTIVOS (archivos en `genome/genes/`). Divergen
  realmente cuando el manifiesto fija `default_sensibilidad: confidencial`: un gen dice `interno`,
  el otro dice `confidencial`.
- clase/score recalculado: contradicción entre genes activos · sev 5 · alcance 2 · impacto 52
  (maker decía: sev 5 · imp 52)
- razón: CONFIRMED. Aunque `gen-frontmatter:11` enlaza `[[gen-confidencialidad]]` (no es ignorancia
  mutua), el texto adyacente afirma categóricamente "default `interno`", lo que contradice la regla
  canónica manifiesto-derivada del otro gen. Dos genes activos, mismo campo, default distinto en el
  caso documentado → la clase sev-5 y el alcance 2 (ambos genes en conflicto) se sostienen. Score
  intacto. (Distinto objeto que C3: C1 es el TEXTO de dos genes; C3 son los archivos blueprint.)

### C2 — Vocabulario de `vigencia`: gen base vs seed del blueprint legal → VERDICT: DOWNGRADED (sev 5→2)
- re-derivación: `glob genome/genes/gen-vigencia-normativa.md` → **0 archivos**. Hay exactamente 20
  genes activos; NINGUNO es `gen-vigencia-normativa`. Ese id existe SOLO como `seed_genes` en
  `legal.yaml:55-57`: `vigencia: {vigente|en-revision|derogada}` default `vigente`, y ese mismo
  seed trae su propia regla "QUERY advierte SIEMPRE la vigencia no-vigente". `gen-vigencia-temporal.md:17`
  enumera los estados NO-vigentes `{derogada | no-vigente | en-revision}`. El seed añade `vigente`
  como estado ACTIVO (no listado en el base porque el base solo enumera lo no-vigente) y omite
  `no-vigente` de su set.
- clase/score recalculado: verbo/campo fuera de esquema (en blueprint, no en gen activo) · sev 2 ·
  alcance 1 · impacto 21  (maker decía: sev 5 · imp 52)
- razón: la clase sev-5 "contradicción entre genes ACTIVOS" NO aplica: `gen-vigencia-normativa` no
  es un gen activo, es un seed que ONBOARD instanciaría DESPUÉS pasando por la compuerta — todavía no
  existe como archivo, no puede contradecir a un gen activo. Tampoco hay "norma derogada servida como
  vigente": `vigente` = estado activo correcto (no-vencido); el base no lo lista porque solo enumera
  el set NO-vigente, y el propio seed replica la regla "QUERY advierte siempre lo no-vigente". El
  único residuo real es de schema-consistency: el seed usa `derogada` (✓ coincide con base) pero omite
  `no-vigente`. Defecto menor de campo fuera de esquema en un manifiesto aún no instanciado. El propio
  maker señaló este matiz (confianza media). Re-scoring drástico: imp 52 → 21.

### C3 — Blueprints salud/legal NO fijan `default_sensibilidad` → VERDICT: CONFIRMED
- re-derivación: `grep default_sensibilidad onboard/blueprints/*` → **0 coincidencias** (verificado).
  `gen-confidencialidad.md:9` afirma que dominios "legal/salud suelen fijar `confidencial`"; el fallback
  documentado (`:10`) es `interno`. `company.example.yaml:44-46` SÍ trae `default_sensibilidad: interno`
  como campo del esquema canónico. Efecto re-derivado: en salud, `historia-clinica` (salud.yaml:17,
  "datos sensibles") y en legal los datos de cliente/`SP` nacerían `interno` → se anclan en index.md,
  se fusionan en CONSOLIDATE y ENTRAN al staging de graphify (que solo excluye `confidencial`).
- clase/score recalculado: violación de invariante impuesta por un gen · sev 4 · alcance 4 · impacto 44
  (maker decía: sev 4 · imp 44)
- razón: CONFIRMED. La ausencia re-deriva por grep; el gen afirma que estos sectores fijan el default y
  el esquema del ejemplo incluye el campo. Alcance 4 = `salud.yaml` + `legal.yaml` + los 2 genes cuyo
  invariante se incumple (`gen-confidencialidad`, `gen-onboard`). Score intacto. Objeto DISTINTO de C1
  (archivos blueprint, no texto de gen) y de C4 (campo `default_sensibilidad`, no bloque `graph_lens`).

### C4 — Los 5 blueprints carecen del bloque `graph_lens` → VERDICT: CONFIRMED (downscope alcance 4→5… ver razón)
- re-derivación: `grep graph_lens onboard/blueprints/*` → **0 coincidencias** (verificado).
  `gen-onboard.md:14-15`: "si el manifiesto activa `graph_lens` sin backend, **pregunta una vez**
  ... lo registra en `graph_lens.backend`". `gen-graph-lens.md:11-13` idem. `company.example.yaml:60-67`
  SÍ trae el bloque `graph_lens` completo. Ninguno de los 5 blueprints tiene nodo YAML donde persistir
  `graph_lens.backend`.
- clase/score recalculado: violación de invariante impuesta por un gen · sev 4 · alcance 4 · impacto 44
  (maker decía: sev 4 · imp 44) — mantengo alcance 4 (5 blueprints + genes; ver razón)
- razón: CONFIRMED. Ausencia re-derivada por grep; el esquema canónico incluye el bloque y dos genes
  activos (gen-onboard v4, gen-graph-lens v2) lo presuponen. Atenuante real (que NO anula el defecto):
  con `enable:false` el flujo de pregunta no se dispara, pero el contrato de campo del esquema queda
  incumplido y la migración/validación falla. Mantengo el alcance del maker (4) por conservadurismo:
  el conteo "violación de invariante" = entidad afectada + páginas implicadas; tomo los 5 blueprints
  como la entidad-categoría afectada más los genes, y no inflo el número. Score 44 intacto. Objeto
  DISTINTO de C3 (campo distinto) y de C10 (C10 mira los 3 no-sensibles bajo clase schema, no invariante).

### C5 — La cápsula `ingesta-de-fuente` omite confidencialidad → VERDICT: CONFIRMED
- re-derivación: `ingesta-de-fuente.md:5` `composes: [gen-raw-inmutable, gen-frontmatter-obligatorio,
  gen-ingest]` — NO incluye `gen-confidencialidad`. `:22` "Registrar: añade ancla en `index.md` si es
  relevante" — sin condicionar a sensibilidad. `gen-confidencialidad.md:10` exige que las páginas
  `confidencial` NO se anclen en index.md; `:13` exige PII-halt (INGEST se detiene ante PII real).
  `gen-ingest.md:8` declara que INGEST sigue ESTA cápsula. El control de confidencialidad falta en el
  workflow canónico real de ingesta.
- clase/score recalculado: violación de invariante impuesta por un gen · sev 4 · alcance 3 · impacto 43
  (maker decía: sev 4 · imp 43)
- razón: CONFIRMED. Omisión verificada línea a línea. La cápsula es el camino por el que entra toda
  fuente; sin `gen-confidencialidad` en `composes` ni paso de PII-halt/no-anclado, el invariante de
  confidencialidad se puede violar en la ruta operativa. Alcance 3 = la cápsula + los 2 genes implicados
  (`gen-ingest`, `gen-confidencialidad`). Score intacto.

### C6 — Filtro de staging de graphify frágil → VERDICT: CONFIRMED (downgrade alcance, ver razón)
- re-derivación: `dashboards/graph/00-leeme.md:42` bash `grep -rL 'sensibilidad: confidencial'`
  (cadena literal con un espacio) → falso negativo ante `sensibilidad:  confidencial` (2 espacios) o
  `"confidencial"`. `:49-51` PowerShell usa `$_.Name` y `Join-Path 'graphify-out\staging' $_.Name`
  (aplana rutas → colisión de homónimos). NB: el regex PowerShell `'sensibilidad:\s*confidencial'`
  (`:50`) SÍ tolera espacios — la fragilidad por espacios es solo del lado bash, no de ambos shells.
  El checklist `:72` "Cero páginas confidencial en el grafo" es POST-hoc/manual: no hay verificación
  bloqueante pre-`graphify`.
- clase/score recalculado: violación de invariante impuesta por un gen · sev 4 · alcance 1 · impacto 41
  (maker decía: sev 4 · imp 41)
- razón: CONFIRMED, con matiz: la fragilidad por espacios aplica al bash (`:42`), NO al PowerShell
  (`:50` ya usa `\s*`); el aplanado de rutas y la falta de gate duro pre-ejecución SÍ son ciertos en su
  shell. El defecto (frontera externa sin verificación bloqueante + bug de rutas) se sostiene. Alcance 1
  (la página del runbook = el mecanismo afectado). Score 41 intacto. Objeto DISTINTO de C8 (C8 = etiqueta
  textual "backend local" obsoleta en `:54`; C6 = mecánica del filtro en `:42-51` + gate). No es doble
  conteo: distintas líneas, distinto tipo de defecto.

### C7 — index.md desactualizado (sin GRAPH / gen-graph-lens / visualización) → VERDICT: CONFIRMED
- re-derivación: `index.md:4` `updated: 2026-06-22` — anterior a las mutaciones GRAPH (06-25/06-30 según
  log de commits). `:21` lista solo `AUDIT` como operación anclada; no hay ancla de `GRAPH`,
  `[[gen-graph-lens]]`, ni de la capa `dashboards/`. `:13` "pendiente correr ONBOARD" sigue vigente (no es
  defecto). CLAUDE.md y los genes ya documentan GRAPH/gen-graph-lens/visualización, así que index.md quedó
  supersedido sin degradar.
- clase/score recalculado: conocimiento supersedido sin degradar (página) · sev 3 · alcance 3 · impacto 33
  (maker decía: sev 3 · imp 33)
- razón: CONFIRMED. `updated` obsoleto y ausencia de anclas GRAPH/visualización re-derivadas. index.md es
  `type: meta` (exento del LINT de huérfanos/frontmatter, no del contenido). Alcance 3: index.md + las
  referencias operativas de primer nivel ausentes (operación GRAPH, gen-graph-lens, capa dashboards). Score
  intacto.

### C8 — Runbook de grafo dice "backend local" (contradice gen-graph-lens v2) → VERDICT: DOWNGRADED (alcance 3→1)
- re-derivación: `dashboards/graph/00-leeme.md:54` "**Construye el grafo** (backend local):" seguido del
  comando `graphify ... --mode deep`. Pero `gen-graph-lens.md:10-13` (v2) hace el backend ELEGIBLE
  `{claude|local|structural}` registrado en `graph_lens.backend`; el propio principio #2 del runbook
  (`:21-23`) ya dice "Backend a tu elección ... registrado en `graph_lens.backend`". La línea 54 es residuo
  pre-v2 que contradice al mismo documento.
- clase/score recalculado: conocimiento supersedido sin degradar (página) · sev 3 · alcance 1 · impacto 31
  (maker decía: sev 3 · alcance 3 · imp 33)
- razón: CONFIRMED como defecto pero DOWNGRADED en alcance. El conteo de "supersedido" = la página
  supersedida + las que la CITAN operativamente (relación tipada de primer nivel). Nada CITA este runbook
  operativamente respecto de la etiqueta "backend local"; el defecto está contenido en la propia página
  (de hecho contradice su propio principio #2). Alcance honesto = 1, no 3. Impacto 33 → 31. Defecto real y
  distinto de C6 (etiqueta textual vs mecánica del filtro).

### C9 — Dashboards instruyen `FROM "sim"`, fuente inexistente → VERDICT: CONFIRMED (downgrade alcance 6→2)
- re-derivación: `dashboards/00-leeme.md:24` "cambia `FROM \"wiki\"` por `FROM \"sim\"` y verás los 5
  escenarios simulados"; `dashboards/salud-del-conocimiento.md:8` idéntica instrucción. `glob sim/**` →
  **0 archivos**; ningún gen/manifiesto crea `sim/`. El único happy-path documentado para ver datos lleva a
  un dead-end.
- clase/score recalculado: vacío (categoría sin cobertura) · sev 2 · alcance 2 · impacto 22
  (maker decía: sev 2 · alcance 6 · imp 26)
- razón: CONFIRMED el defecto, REFUTADO el alcance 6. La regla de conteo para "vacío" es **1** (la
  página/categoría/campo afectado). El maker puso 6 sin base en la rúbrica (parece contar escenarios
  imaginarios + páginas). Aquí hay 2 páginas-dashboard que dan la instrucción rota → como mucho alcance 2
  (las dos páginas afectadas, leyendo "vacío" generosamente como categoría-sin-cobertura sobre 2 archivos).
  Impacto 26 → 22. (Defecto genuino: instrucción que no funciona.)

### C10 — 3 blueprints no-sensibles sin `default_sensibilidad`/`graph_lens` → VERDICT: REFUTED (doble conteo con C3/C4)
- re-derivación: agencia/ecommerce/produccion.yaml efectivamente carecen de `default_sensibilidad` y
  `graph_lens` (mismos greps que C3/C4, que ya dieron 0 en TODOS los blueprints). El efecto es benigno:
  default `interno` es correcto para estos sectores y la lente está off.
- clase/score recalculado: — (REFUTED; no entra al ranking)
- razón: REFUTED como candidato independiente. Es el MISMO defecto-objeto que C3 (falta `default_sensibilidad`)
  y C4 (falta `graph_lens`), solo que sobre los otros 3 archivos. La rúbrica: "cada defecto produce UN solo
  candidato". C4 ya cubre los 5 blueprints sin `graph_lens` (su alcance los incluye). La porción
  `default_sensibilidad` en sectores NO sensibles ni siquiera es defecto (default `interno` es lo correcto
  por gen-confidencialidad). Lo que queda es schema-isomorfismo cosmético sin consecuencia operativa →
  no es un defecto separable; se absorbe en C4 (graph_lens) y no añade impacto propio. Refutado para evitar
  doble conteo y por efecto nulo de la mitad `default_sensibilidad`.

### C11 — Redundancia: validación de verbos de relación en dos genes → VERDICT: CONFIRMED
- re-derivación: `gen-frontmatter-obligatorio.md:18` "LINT valida cada relación contra esa **unión**
  (núcleo ∪ declarados) y marca verbos no declarados". `gen-lint.md:13-14` "(d) relaciones con verbos
  fuera de la unión núcleo ∪ `relation_types` del manifiesto ([[gen-frontmatter-obligatorio]])". Misma
  comprobación descrita en dos genes activos (gen-lint ya enlaza al otro).
- clase/score recalculado: redundancia (duplicado) · sev 2 · alcance 2 · impacto 22
  (maker decía: sev 2 · imp 22)
- razón: CONFIRMED. Dos genes activos describen la misma regla. Coherente hoy (gen-lint ya referencia
  gen-frontmatter), riesgo de divergencia futura. Clase redundancia, alcance 2 (ambos genes). NB: NO están
  exentos por `deriva_de`/`supersede` (no hay relación tipada que los exima). Score intacto.

### C12 — Spec de terminación de AUDIT nombra artefactos sin `.md` → VERDICT: CONFIRMED
- re-derivación: `gen-auto-auditoria.md:14-15` "...con `00-snapshot`, `10-maker`, `20-auditor` y
  `30-proposals`, este último..." — sin extensión. El resto del MISMO gen (`:37` "Escribe `10-maker.md`",
  `:40` "`20-auditor.md`", `:41` "`30-proposals.md`") y `audit/README.md:9-11` usan `.md`. Única línea
  inconsistente en el criterio de parada.
- clase/score recalculado: verbo/campo fuera de esquema (imprecisión de invariante) · sev 2 · alcance 1 ·
  impacto 21  (maker decía: sev 2 · alcance 2 · imp 22)
- razón: CONFIRMED el defecto; alcance ajustado 2→1. Es una sola línea (`:14`) en un solo gen la que omite
  `.md`; la regla de conteo para "vacío/campo fuera de esquema" es 1 (el campo/línea afectado). El otro
  archivo (README) está CORRECTO, no afectado, así que no suma al alcance. Impacto 22 → 21. Doc menor.

### C13 — audit/README.md no enumera el set de campos de propuesta → VERDICT: CONFIRMED
- re-derivación: `gen-auto-auditoria.md:16` exige que cada propuesta lleve `id, fecha, motivo, evidencia,
  diff, score`. `audit/README.md:11` solo documenta "`status: pending|approved|reverted`" para
  `30-proposals.md`; no enumera el contrato de campos. Un agente portable que lea solo el README no
  reconstruye `30-proposals.md` completo.
- clase/score recalculado: vacío (categoría sin cobertura) · sev 2 · alcance 1 · impacto 21
  (maker decía: sev 2 · alcance 2 · imp 22)
- razón: CONFIRMED el defecto; alcance ajustado 2→1. La regla de conteo "vacío" = 1 (la página/categoría
  afectada = el README). El gen está correcto, no afectado. Impacto 22 → 21.

### C14 — QUERY/confidencialidad no filtran metadatos de página confidencial → VERDICT: CONFIRMED
- re-derivación: `gen-query.md:10-13` y `gen-confidencialidad.md:10-12` prohíben citar CONTENIDO textual
  de páginas `confidencial` (responder con "referencia indirecta o ID seudonimizado") pero NO prohíben
  explícitamente exponer título/nombre-de-archivo/tags/aristas, que pueden reidentificar. `dashboards/
  graph/00-leeme.md:72` SÍ cierra el vector en graphify ("Cero páginas confidencial ... ni títulos ni
  relaciones"); QUERY no tiene esa cláusula.
- clase/score recalculado: vacío (categoría sin cobertura) · sev 2 · alcance 1 · impacto 21
  (maker decía: sev 2 · imp 21)
- razón: CONFIRMED. Vacío de especificación real: la asimetría con el runbook de grafo (que sí lo cierra)
  confirma que es una omisión, no una decisión. Clase vacío, alcance 1. Score intacto. (Impacto modesto;
  depende de cómo se nombren las páginas, gobernado por C3/C5.)

### C15 — Typo de instalación `graphifyy` vs comando `graphify` → VERDICT: CONFIRMED (downgrade)
- re-derivación: `dashboards/graph/00-leeme.md:30` `pip install graphifyy` (doble y) `(o pipx install
  graphifyy)`. El comando invocado `:57` es `graphify` (una y) y el repo enlazado `:9` es
  `github.com/safishamsi/graphify` (una y). Inconsistencia interna confirmada.
- clase/score recalculado: verbo/campo fuera de esquema → trato como vacío (instrucción rota) · sev 2 ·
  alcance 1 · impacto 21  (maker decía: sev 2 · alcance 2 · imp 22)
- razón: CONFIRMED como inconsistencia INTERNA (no requiere red: el comando y el repo del propio documento
  usan `graphify`, el install dice `graphifyy`). Alcance ajustado 2→1 (una sola línea/instrucción afectada).
  Impacto 22 → 21. Confianza baja del maker se refiere a "cuál es el nombre real en PyPI"; pero como defecto
  de consistencia interna es seguro. Menor.

---

## Resumen de re-scoring

| Cand | Veredicto | clase | sev | alcance | impacto (auditor) | impacto (maker) |
|---|---|---|---|---|---|---|
| C1 | CONFIRMED | contradicción genes activos | 5 | 2 | **52** | 52 |
| C2 | DOWNGRADED | campo fuera de esquema (seed, no gen activo) | 2 | 1 | 21 | 52 |
| C3 | CONFIRMED | violación de invariante | 4 | 4 | **44** | 44 |
| C4 | CONFIRMED | violación de invariante | 4 | 4 | **44** | 44 |
| C5 | CONFIRMED | violación de invariante | 4 | 3 | 43 | 43 |
| C6 | CONFIRMED | violación de invariante | 4 | 1 | 41 | 41 |
| C7 | CONFIRMED | supersedido sin degradar | 3 | 3 | 33 | 33 |
| C8 | DOWNGRADED | supersedido sin degradar | 3 | 1 | 31 | 33 |
| C9 | CONFIRMED | vacío | 2 | 2 | 22 | 26 |
| C10 | REFUTED | (doble conteo con C3/C4) | — | — | — | 23 |
| C11 | CONFIRMED | redundancia | 2 | 2 | 22 | 22 |
| C12 | CONFIRMED | campo fuera de esquema | 2 | 1 | 21 | 22 |
| C13 | CONFIRMED | vacío | 2 | 1 | 21 | 22 |
| C14 | CONFIRMED | vacío | 2 | 1 | 21 | 21 |
| C15 | CONFIRMED | vacío (instrucción rota) | 2 | 1 | 21 | 22 |

**Confirmadas por el auditor: 13** (C1, C3, C4, C5, C6, C7, C8, C9, C11, C12, C13, C14, C15).
**Refutadas: 1** (C10 — doble conteo). **Re-scoring sustantivo: 1 downgrade drástico (C2: 52→21) + ajustes de alcance en C8, C9, C12, C13, C15.**

---

## Top-N confirmadas (rankeadas)

N = min(3, confirmadas por auditor) = min(3, 13) = **3**.

Desempate aplicado: (1) mayor impacto; (2) orden de filas de la tabla de severidad; (3) ruta alfabética.

1. **C1 — Default de `sensibilidad` contradictorio entre dos genes activos** · contradicción entre genes
   activos · sev 5 · alcance 2 · **impacto 52**.
   Único sev-5 que sobrevive: `gen-frontmatter-obligatorio:11-12` fija default `interno` plano vs
   `gen-confidencialidad:8-10` default manifiesto-derivado (legal/salud→`confidencial`). Toca genoma → gate
   + bump version. El mayor impacto de la corrida.

2. **C3 — Blueprints salud/legal NO fijan `default_sensibilidad`** · violación de invariante · sev 4 ·
   alcance 4 · **impacto 44**.
   Empata en impacto con C4; **gana el desempate** porque su clase (violación de invariante, fila superior)
   es idéntica a la de C4 → pasa a la ruta alfabética: `onboard/blueprints/legal.yaml` y `salud.yaml` vs el
   conjunto de C4. Decisivo: la PRIMERA ruta alfabética implicada por C3 es `onboard/blueprints/legal.yaml`;
   por C4 es `onboard/blueprints/agencia.yaml`. Por alfabético estricto `agencia` < `legal`, lo que pondría
   C4 antes. **Corrijo el orden abajo.**

3. **C4 — Los 5 blueprints carecen del bloque `graph_lens`** · violación de invariante · sev 4 · alcance 4
   · **impacto 44**.

### Ranking final corregido (desempate alfabético estricto entre C3 y C4)

C3 y C4 empatan en impacto (44) y clase (violación de invariante). El tercer criterio es ruta de archivo
alfabética: la primera ruta afectada por **C4** es `onboard/blueprints/agencia.yaml`; por **C3** es
`onboard/blueprints/legal.yaml`. `agencia` < `legal` alfabéticamente ⇒ **C4 precede a C3**.

1. **C1** — impacto **52** — contradicción sev-5 entre genes activos (default `sensibilidad`). Toca genoma → gate + bump.
2. **C4** — impacto **44** — los 5 blueprints sin bloque `graph_lens` (contrato de ONBOARD v4 / gen-graph-lens v2 incumplido). Desempata sobre C3 por ruta alfabética (`agencia.yaml` < `legal.yaml`).
3. **C3** — impacto **44** — salud/legal sin `default_sensibilidad` (datos clínicos/legales nacen `interno` y entran a index/CONSOLIDATE/graphify).

> Nota de desempate: C5 (imp 43) y C6 (imp 41) quedan JUSTO fuera del Top-3 pese a ser defectos sólidos de
> confidencialidad. Si el gate humano rechaza C3 o C4, C5 es el siguiente en línea.
