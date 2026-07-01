---
run_id: 2026-06-30-7c840d0
fecha: 2026-06-30
rol: maker
fuente: 7 auditores especializados (equipo)
---

# 10 — Maker: candidatos (TODOS, sin recorte a 3)

Producido por el equipo de 7 especialistas. Cada candidato lleva clase, severidad, alcance,
impacto (`sev*10 + alcance`), evidencia re-derivable, diff propuesto y confianza. La selección
Top-N (≤3) la hace el auditor independiente (`20-auditor.md`), no este artefacto.

**Dedup aplicado** (`gen-auto-auditoria`: "mismo defecto sobre el mismo objeto" → un candidato):
C3 fusiona A5-F1 + A6-F2 (ambos: `salud.yaml`/`legal.yaml` omiten `default_sensibilidad`).
C6 fusiona A6-F3 + A7-F3 (ambos: mecanismo de staging de `dashboards/graph/00-leeme.md`).
C8 NO se fusiona con C6 pese a tocar el mismo archivo: es un **defecto distinto** (etiqueta
"backend local" obsoleta vs. fragilidad del filtro).

---

## Candidatos (ordenados por impacto)

### C1 — Default de `sensibilidad` contradictorio entre dos genes activos
- clase: **contradicción entre genes activos** · sev **5** · alcance **2** · **impacto 52**
- objeto: `genome/genes/gen-frontmatter-obligatorio.md` ↔ `genome/genes/gen-confidencialidad.md`
- evidencia: `gen-frontmatter-obligatorio.md:11-12` dice default `interno` planamente; `gen-confidencialidad.md:9-10` dice default = `default_sensibilidad` del manifiesto (legal/salud→`confidencial`), si no, `interno`. Diverge cuando el manifiesto fija `confidencial`.
- diff: alinear `gen-frontmatter-obligatorio:11-12` con la regla canónica de `gen-confidencialidad` ("default según `default_sensibilidad`; si no se declara, `interno`"). Genoma → gate + bump version a 4.
- confianza: alta (cita literal en ambos; caso de divergencia documentado por los genes).

### C2 — Vocabulario de `vigencia` incompatible: gen base vs seed del blueprint legal
- clase: **info vencida en dominio de seguridad / contradicción** · sev **5** · alcance **2** · **impacto 52**
- objeto: `genome/genes/gen-vigencia-temporal.md` ↔ seed `gen-vigencia-normativa` en `onboard/blueprints/legal.yaml`
- evidencia: `gen-vigencia-temporal.md:17` enum no-vigente = `{derogada|no-vigente|en-revision}`; `legal.yaml:57` siembra `gen-vigencia-normativa` con `{vigente|en-revision|derogada}` default `vigente`. El blueprint introduce `vigente` (no contemplado) y omite `no-vigente`. `gen-lint.md:11`/`gen-auto-auditoria.md:24` escanean exactamente el set base; un valor fuera evade el chequeo → norma derogada servida como vigente (cumplimiento regulatorio = dominio de seguridad).
- diff: armonizar — el blueprint hereda el enum del base; `gen-vigencia-temporal` documenta `vigente` como estado activo (complemento del set no-vigente).
- confianza: media. **Matiz para el auditor:** `gen-vigencia-normativa` es un `seed_gene` (no instanciado como archivo activo), lo que puede degradar la clase "contradicción entre genes ACTIVOS".

### C3 — Blueprints salud/legal NO fijan `default_sensibilidad` (doble detección: manifiesto + seguridad)
- clase: **violación de invariante impuesta por un gen** · sev **4** · alcance **4** · **impacto 44**
- objeto: `onboard/blueprints/salud.yaml`, `onboard/blueprints/legal.yaml` (+ `gen-confidencialidad`, `gen-onboard`)
- evidencia: `grep default_sensibilidad onboard/blueprints/*` → 0 coincidencias. `gen-confidencialidad.md:9-10` afirma "legal/salud suelen fijar `confidencial`"; fallback `interno`. Efecto: cada historia clínica/minuta nace `interno` → se ancla en index.md, se fusiona en CONSOLIDATE y **entra a la copia staging de graphify** (que solo excluye `confidencial`).
- diff: añadir `default_sensibilidad: confidencial` a `salud.yaml` y `legal.yaml` (idealmente por taxonomía: carpetas `pacientes/`,`clientes/`,`casos/`).
- confianza: alta (ausencia verificada por grep; el gen afirma que estos sectores lo fijan).

### C4 — Los 5 blueprints carecen del bloque `graph_lens` (ONBOARD v4 sin destino de persistencia)
- clase: **violación de invariante impuesta por un gen** · sev **4** · alcance **4** · **impacto 44**
- objeto: los 5 `onboard/blueprints/*.yaml` (+ `gen-onboard` v4, `gen-graph-lens` v2)
- evidencia: `gen-onboard.md:14-15` "si el manifiesto activa `graph_lens` sin backend, pregunta una vez y lo registra en `graph_lens.backend`"; `gen-graph-lens.md:12-14` idem. `company.example.yaml:62-67` tiene el bloque; `grep graph_lens onboard/blueprints/*` → 0. Onboardear desde blueprint no tiene nodo YAML donde persistir el backend.
- diff: anexar a cada blueprint el bloque `graph_lens` del ejemplo con `enable: false` y `backend:` vacío.
- confianza: alta (verificado por grep). Atenuante: con `enable:false` el flujo no se dispara, pero el contrato de campo queda incumplido.

### C5 — La cápsula `ingesta-de-fuente` (workflow canónico de INGEST) omite confidencialidad
- clase: **violación de invariante impuesta por un gen** · sev **4** · alcance **3** · **impacto 43**
- objeto: `genome/capsules/ingesta-de-fuente.md` (+ `gen-ingest`, `gen-confidencialidad`)
- evidencia: `ingesta-de-fuente.md:5` `composes:[gen-raw-inmutable, gen-frontmatter-obligatorio, gen-ingest]` (NO `gen-confidencialidad`); `:22` "añade ancla en index.md si es relevante" sin la exclusión. `gen-confidencialidad.md:10,13` exige no-anclar confidenciales y PII-halt. `gen-ingest.md:8` declara que INGEST sigue esta cápsula → el control falta en el camino real.
- diff: añadir `gen-confidencialidad` a `composes`; insertar paso de clasificación de sensibilidad + PII-halt; condicionar el anclado a `sensibilidad != confidencial`.
- confianza: alta (omisión verificable línea a línea; es el camino por el que entra toda fuente).

### C6 — Filtro de staging de graphify frágil (único gate de la frontera externa)
- clase: **violación de invariante impuesta por un gen** · sev **4** · alcance **1** · **impacto 41**
- objeto: `dashboards/graph/00-leeme.md` (mecanismo de staging) vs invariante "confidencial nunca sale" de `gen-graph-lens`
- evidencia: `:42-43` bash `grep -rL 'sensibilidad: confidencial'` matchea cadena literal → falso negativo con `sensibilidad:  confidencial` (2 espacios), `"confidencial"` entre comillas, etc.; `:49-51` PowerShell aplana rutas (`$_.Name`) → colisión de homónimos. Sin verificación bloqueante de "cero confidenciales en staging" ANTES de invocar `graphify` (el checklist `:72` es post-hoc/manual).
- diff: (a) patrón tolerante a espacios/comillas en ambos shells; (b) preservar jerarquía de rutas en PowerShell; (c) paso de verificación duro bloqueante pre-`graphify`.
- confianza: media (los bugs son ciertos; que un caso real los dispare depende del formato del frontmatter, pero es el único gate de la frontera).

### C7 — index.md desactualizado (sin GRAPH / gen-graph-lens / visualización)
- clase: **conocimiento supersedido sin degradar** · sev **3** · alcance **3** · **impacto 33**
- objeto: `index.md`
- evidencia: `index.md:4` `updated: 2026-06-22` precede a las mutaciones de 06-25/06-30. `:16-21` lista solo `AUDIT`; sin ancla de operación `GRAPH`, `[[gen-graph-lens]]`, ni capa `dashboards/`. (La línea "pendiente ONBOARD" sí sigue vigente.)
- diff: subir `updated` a 2026-06-30; añadir ancla de GRAPH/gen-graph-lens y de visualización opcional. Wiki/index → gate humano (lo escribió el usuario), sin events.jsonl.
- confianza: alta.

### C8 — Runbook de grafo dice "backend local" (contradice gen-graph-lens v2)
- clase: **conocimiento supersedido sin degradar** · sev **3** · alcance **3** · **impacto 33**
- objeto: `dashboards/graph/00-leeme.md` (defecto DISTINTO de C6)
- evidencia: `:54` "**Construye el grafo** (backend local):" pero `gen-graph-lens.md:10-13` (v2) hace el backend elegible `{claude|local|structural}` y registrado en `graph_lens.backend`; el propio principio #2 del runbook (`:21-24`) ya lo dice. La línea 54 es residuo pre-v2.
- diff: cambiar a "(con el backend de `graph_lens.backend`)" y reflejar la elección en el comando.
- confianza: alta.

### C9 — Dashboards instruyen `FROM "sim"`, fuente de datos inexistente
- clase: **vacío (categoría sin cobertura)** · sev **2** · alcance **6** · **impacto 26**
- objeto: `dashboards/00-leeme.md:23-24`, `dashboards/salud-del-conocimiento.md:8`
- evidencia: ambos dicen cambiar `FROM "wiki"` por `FROM "sim"` para "ver los 5 escenarios simulados". `Glob sim/**` → no existe; ningún gen/manifiesto crea `sim/`. Único "happy path" documentado para ver datos → dead-end.
- diff: (a) shippear `sim/` con 5 páginas de ejemplo no-confidenciales con frontmatter completo, o (b) quitar la instrucción `FROM "sim"` y sustituir por guía honesta.
- confianza: alta.

### C10 — 3 blueprints no-sensibles sin `default_sensibilidad`/`graph_lens` (inconsistencia de esquema)
- clase: **vacío (inconsistencia estructural)** · sev **2** · alcance **3** · **impacto 23**
- objeto: `onboard/blueprints/agencia.yaml`, `ecommerce.yaml`, `produccion.yaml` (raíz común con C3/C4)
- evidencia: los 5 blueprints son isomorfos entre sí pero divergen del esquema canónico `company.example.yaml`. Efecto benigno (interno correcto; lente off) pero dificulta validación/migración.
- diff: tratar junto con C3/C4 — dejar los 5 blueprints isomorfos al ejemplo.
- confianza: alta.

### C11 — Redundancia: validación de verbos de relación en dos genes
- clase: **redundancia (duplicado)** · sev **2** · alcance **2** · **impacto 22**
- objeto: `gen-lint.md:13-14` ↔ `gen-frontmatter-obligatorio.md:18`
- evidencia: ambos describen la misma comprobación (unión núcleo ∪ `relation_types`). Coherente hoy; riesgo de divergencia futura.
- diff: dejar la definición en `gen-frontmatter-obligatorio` y en `gen-lint` referenciar ("verbos no conformes al esquema de [[gen-frontmatter-obligatorio]]").
- confianza: media (no causa error operativo; registro).

### C12 — Spec de terminación de AUDIT nombra artefactos sin `.md`
- clase: **vacío (imprecisión de invariante)** · sev **2** · alcance **2** · **impacto 22**
- objeto: `gen-auto-auditoria.md:14` ↔ `audit/README.md:8-11`
- evidencia: `:14` "00-snapshot, 10-maker, 20-auditor y 30-proposals" sin extensión; el README y el resto del gen (`:37,40,41`) usan `.md`. Única línea inconsistente en el criterio de parada.
- diff: añadir `.md` en `:14`. Doc, sin bump de versión.
- confianza: alta.

### C13 — audit/README.md no enumera el set de campos de propuesta
- clase: **vacío (categoría sin cobertura)** · sev **2** · alcance **2** · **impacto 22**
- objeto: `audit/README.md:11` ↔ `gen-auto-auditoria.md:16`
- evidencia: el gen exige `id, fecha, motivo, evidencia, diff, score`; el README solo documenta `status:`. Un agente portable que lea solo el README no reconstruye `30-proposals.md` completo.
- diff: completar el contrato de campos en `:11`.
- confianza: alta.

### C14 — QUERY/confidencialidad no filtran metadatos de página confidencial (fuga indirecta)
- clase: **vacío (categoría sin cobertura)** · sev **2** · alcance **1** · **impacto 21**
- objeto: `gen-query.md` ↔ `gen-confidencialidad.md`
- evidencia: prohíben citar contenido textual, pero no el título/nombre de archivo/tags/aristas (`paciente-juan-perez.md`, `tratado_con [[VIH]]`) que reidentifican. graphify YA cierra este vector (`dashboards/graph/00-leeme.md:72` "ni títulos ni relaciones"); QUERY no.
- diff: extender la regla: la referencia indirecta tampoco expone título/archivo/tags/aristas; ID seudonimizado también en el enlace.
- confianza: media (vacío de spec real; impacto depende de cómo se nombren las páginas, que C3/C5 dejan sin gobernar).

### C15 — Typo de instalación `graphifyy` vs comando `graphify`
- clase: **vacío (instrucción rota)** · sev **2** · alcance **2** · **impacto 22**
- objeto: `dashboards/graph/00-leeme.md:30`
- evidencia: `pip install graphifyy` (doble y) pero el comando invocado y el repo enlazado son `graphify`.
- diff: confirmar nombre real en PyPI; corregir a `graphify` o anotar la discrepancia.
- confianza: **baja** (no verificable sin red; inconsistencia interna, no error confirmado).

---

## Verificado LIMPIO (pruebas de cobertura — no re-levantar como falsos positivos)
- **AGENTS.md ≡ CLAUDE.md** byte a byte (mismo sha256, `git diff --no-index` exit 0).
- **Versión de cada gen ↔ events.jsonl**: 20/20 coherentes; sin drift; ningún evento apunta a archivo inexistente.
- **events.jsonl**: JSONL válido 26/26, append-only, 7 claves por línea, todo `approved_by:user / status:applied` (gate honrado).
- **Todos los `[[wiki-link]]` reales resuelven**; frontmatter válido en los 20 genes y todas las páginas/dashboards. Tokens `[[wiki-link]]` sin destino = sintaxis ilustrativa en backticks.
- **Matriz operación↔gen 20/20**, cero huérfanos; **AUDIT obedece su propio protocolo**; **ninguna ruta muta el genoma sin `gen-compuerta-mutacion` + events.jsonl**.
- **graphify "confidencial nunca sale" es gate duro** (no default), cubre los 3 backends; reframe del evento 2026-06-30 verificado.
- **Regresión `gen-query` v1 ("cita siempre") limpia**; CONSOLIDATE honra confidencialidad; redacción de artefactos AUDIT (incl. lado "antes" del diff) airtight.
- **Hooks**: estado stub disclosado consistentemente en settings.json + hooks/README + CLAUDE.md (sin overselling).
- **Dataview**: todos los campos referenciados están en el esquema de frontmatter; `.obsidian` preset coherente (Dataview declarado, binario auto-instalado por el usuario).
