---
tipo: plan-de-implementacion
fecha: 2026-07-12
spec: docs/specs/2026-07-12-enforcement-mecanico-design.md
---

# Plan de implementación — enforcement mecánico

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (ejecución
> inline en esta sesión). Pasos con checkbox para seguimiento. TDD por tarea: test en
> rojo → implementación mínima → verde → commit.

**Goal:** validadores mecánicos deterministas + tests de reproducibilidad + CI + XRAY +
salud + casos worked/, sin mutar el genoma (propuestas por compuerta).

**Architecture:** paquete `tools/cerebro_core/` (módulos puros, una responsabilidad cada
uno) + CLI única `tools/cerebro.py` + suite `tests/` (unittest) + fixtures como vaults
sandbox. Nada escribe fuera del `--vault` dado; `raw/` jamás.

**Tech stack:** Python ≥3.10 stdlib. GitHub Actions (ubuntu+windows, py3.11). POSIX sh
para el pre-commit.

## Restricciones globales

- Cero dependencias pip (runtime y tests).
- Toda salida determinista: ordenada, LF-normalizada, fechas por parámetro impresas.
- Mensajes de usuario en español; identificadores de código en inglés.
- Ningún comando muta `genome/genes/`, `genome/capsules/` (salvo `onboard apply`, que
  siembra genes NUEVOS del manifiesto — eso es gen-onboard v4, aprobado por manifiesto).
- Exit codes: 0 limpio · 1 hallazgos/violación · 2 error de uso o entrada ilegible.

---

### Tarea 1 — Fundaciones: `miniyaml`, `fm`, `slug`

**Files:** Create `tools/cerebro_core/__init__.py`, `tools/cerebro_core/miniyaml.py`,
`tools/cerebro_core/fm.py`, `tools/cerebro_core/slug.py`; Test `tests/test_miniyaml.py`,
`tests/test_fm.py`, `tests/test_slug.py`.

**Produces:**
- `miniyaml.parse(text: str) -> dict` — subconjunto: maps anidados (indentación 2·n),
  listas block `- item` (ítems escalares o maps), flow `[a, b]` y `{k: v}`, escalares
  (int/float/bool true|false/null vacío/str con o sin comillas), comentarios `#`.
  Rechaza con `MiniYamlError(msg, line)`: tabs de indentación, anclas `&/*`, tags `!!`,
  bloques `|`/`>`, `---` interno, claves duplicadas.
- `fm.split(text: str) -> tuple[dict|None, str, list[str]]` — frontmatter entre `---` en
  línea 1 y su cierre; devuelve (fm, body, errores). Sin frontmatter → (None, text, []).
- `slug.slugify(text: str, fallback_hash: str = "") -> str` — algoritmo exacto de
  gen-identidad-de-pagina v2 (NFD sin diacríticos, `[^a-z0-9]`→`-`, colapso, recorte,
  máx 60, vacío ⇒ `f-<hash8>`).

**Steps:**
- [x] Tests en rojo: manifiesto de ejemplo parsea igual que su semántica esperada
  (company.name, ciclo_de_vida.promocion.confidence_min, seed_genes[0].id…); rechazos
  ruidosos; slug: `"Café con Ñandú"`→`cafe-con-nandu`, colapsos, 60 chars, vacío.
- [x] Implementación mínima → verde.
- [x] Commit `feat(tools): fundaciones miniyaml + frontmatter + slug`.

### Tarea 2 — Espejo del esquema: `schema`, `manifest`

**Files:** Create `tools/cerebro_core/schema.py`, `tools/cerebro_core/manifest.py`;
Test `tests/test_schema.py`, `tests/test_manifest.py`.

**Produces:**
- `schema.REQUIRED_FIELDS`, `schema.OPTIONAL_FIELDS: dict[campo→gen]`, enums
  (`TIERS, DECAY_RATES, SENSIBILIDADES, CLASES, VIGENCIAS, TYPES`),
  `schema.RELATION_CORE`, `schema.GENE_VERBS`,
  `schema.allowed_verbs(manifest) -> set[str]`,
  `schema.validate_page_fm(fm: dict, *, is_meta: bool) -> list[str]` (mensajes por campo),
  `schema.CICLO_DEFAULTS` (números de gen-ciclo-de-vida v5).
- `manifest.load(path) -> Manifest` (dataclass con defaults; `Manifest.ciclo` fusiona
  bloque del yaml sobre `CICLO_DEFAULTS`), `manifest.validate(m) -> list[str]`
  (estructura, tipos, `graph_lens.enable` sin backend NO es error aquí — lo es en
  onboard), y parsea los 5 blueprints reales sin errores (test de corpus).

**Steps:** [x] rojo → [x] verde → [x] commit `feat(tools): esquema espejo del genoma + manifiesto`.

### Tarea 3 — Modelo del vault: `vault`

**Files:** Create `tools/cerebro_core/vault.py`; Test `tests/test_vault.py`.

**Produces:** `Page` (dataclass: `path, rel, fm, body, fm_errors, wikilinks: list[str],
is_meta, tier_from_path`), `load_vault(root: Path) -> Vault` con `Vault.pages`
(wiki/**.md), `Vault.genes`, `Vault.capsules`, `Vault.all_md_basenames: dict[nombre→rel]`
(resolución de `[[link]]` case-insensitive sobre todo .md del repo salvo dot-dirs,
`tests/`, `worked/`), `Vault.relations_of(page) -> list[tuple[verbo, target]]`
(dict verbo→str|list; `[]`/`{}` vacíos válidos), `resolve_link(name) -> rel|None`
(basename, `title` y `id_alias`).

**Steps:** [x] rojo (fixture mínimo en tmp) → [x] verde → [x] commit `feat(tools): modelo de vault y resolución de enlaces`.

### Tarea 4 — Integridad base: `statehash`, `mirror`

**Files:** Create `tools/cerebro_core/statehash.py`, `tools/cerebro_core/mirror.py`;
Test `tests/test_statehash.py`, `tests/test_mirror.py`.

**Produces:**
- `statehash.tree_hash(root, scope) -> str` — sha256 sobre líneas `"<rel_posix> <sha256(contenido LF-normalizado)>\n"`
  ordenadas; scopes: `genome` (genome/**), `knowledge` (wiki/** + index.md),
  `all` (ambos + CLAUDE.md, AGENTS.md, onboard/**). CRLF≡LF probado.
- `mirror.check(root) -> str|None` (None=OK, msg=difieren tras normalizar LF),
  `mirror.fix(root)` copia CLAUDE.md→AGENTS.md.

**Steps:** [x] rojo → [x] verde → [x] commit `feat(tools): hash de estado determinista + espejo AGENTS≡CLAUDE`.

### Tarea 5 — Ledger de mutaciones: `events`

**Files:** Create `tools/cerebro_core/events.py`; Test `tests/test_events.py`.

**Produces:**
- `events.verify_file(path, *, git_root=None) -> list[Finding]` — por línea: JSON válido,
  claves requeridas `{ts,type,target,signal,diff,approved_by,status}`, `ts` fecha ISO
  no-decreciente (retroceso ⇒ aviso), `status ∈ {applied, proposed, reverted}`;
  hash-chain: toda línea con `prev` debe cumplir `prev == sha256(línea_anterior_normalizada)`
  y, desde la primera portadora, TODAS las siguientes deben portarlo (aviso si no).
- `events.verify_append_only(git_root, rel) -> list[Finding]` — recorre
  `git rev-list --reverse` del archivo; cada versión debe ser prefijo (por líneas) de la
  siguiente.
- `events.append_line(path, evento: dict) -> str` — valida esquema, calcula `prev`,
  añade; devuelve la línea escrita.
- `Finding` común (en `findings.py` si hace falta): `(code, severity, path, detail)`.

**Steps:** [x] rojo (ledger válido; línea corrupta; cadena rota; prefijo violado en repo
git tmp) → [x] verde → [x] commit `feat(tools): integridad + hash-chain + append-only de events.jsonl`.

### Tarea 6 — El validador: `lint`

**Files:** Create `tools/cerebro_core/lint.py`, fixtures
`tests/fixtures/vault-limpio/**`, `tests/fixtures/vault-sucio/**`;
Test `tests/test_lint.py`.

**Produces:** `lint.run(root, *, as_of: date, manifest: Manifest|None, strict=False)
-> Report` con `Report.findings: list[Finding]` ordenados (rel, code) y
`Report.render_text() / render_json()` estables. Códigos:
`FM-01` sin/ilegible frontmatter [error] · `FM-02` requerido ausente [error] ·
`FM-03` valor inválido (enums, rangos, fechas, tier≠carpeta, evento sin fecha_evento,
hub inválido) [error] · `FM-04` campo fuera de esquema [aviso] ·
`REL-01` verbo fuera de unión [error] · `LNK-01` wikilink roto [error] ·
`LNK-02` huérfana [aviso] · `VIG-01` valido_hasta < as-of [error] ·
`VIG-02` vigencia no-vigente [error] · `VIG-03` vencido blando (ventanas de
ciclo_de_vida) [aviso] · `ID-01` id_pagina≠ruta [error] · `QRN-01` cuarentena activa
[info] · `LED-01` hash de raw/ ≠ último del ledger [error] · `LED-02` línea de ledger
inválida [error] · `SEN-01` confidencial anclada en index/hub [error].
Exit: 1 si errores (con `--strict`, también avisos).

**Steps:** [x] fixtures con las violaciones etiquetadas 1:1 → [x] rojo → [x] verde
(vault-sucio produce exactamente los códigos esperados; vault-limpio y el REPO REAL
producen 0 errores) → [x] commit `feat(tools): lint mecánico determinista (detectores a,c,d,e y más)`.

### Tarea 7 — Reproducibilidad: `onboard`

**Files:** Create `tools/cerebro_core/onboard.py`; Test `tests/test_onboard.py`.

**Produces:** `onboard.apply(manifest_path, vault_root, *, date: str, dry_run=False)
-> ApplyResult` (acciones ordenadas, state_hash final). Semántica del spec:
valida-todo-luego-escribe; perfil re-renderizado completo; taxonomía+entities con
`.gitkeep`; seed_genes nuevos (idéntico=no-op, distinto=error); 1 línea
`gene_added`/gen nuevo vía `events.append_line`; bloque `## Estado` de index.md;
`graph_lens.enable` sin backend ⇒ `OnboardError`.

**Steps:** [x] rojo: (a) **reproducibilidad** dos sandbox → mismo `tree_hash`;
(b) **idempotencia** re-apply → 0 acciones, hash intacto, 0 eventos nuevos;
(c) rechazo ruidoso sin escritura parcial; (d) gen distinto existente ⇒ error →
[x] verde → [x] commit `feat(tools): onboard apply mecánico — reproducible e idempotente`.

### Tarea 8 — Puerta de entrada: CLI `verify` + pre-commit + CI

**Files:** Create `tools/cerebro.py` (CLI argparse completa), `.githooks/pre-commit`,
`.github/workflows/ci.yml`, `.gitattributes`; Test `tests/test_cli.py`.

**Produces:** `verify` = mirror + events(verify+append-only) + lint(errores) + genes/
manifiesto parsean; `--quick` = mirror+events. Pre-commit POSIX: bloquea M/D staged bajo
`raw/`, no-append staged de events.jsonl, CLAUDE.md staged sin AGENTS.md igual; corre
`verify --quick` si hay python. CI: unittest + `verify` en ubuntu+windows, badge.
Instalación hook: `git config core.hooksPath .githooks` (en tools/README).

**Steps:** [x] rojo CLI → [x] verde → [x] probar pre-commit a mano (caso bloqueo raw/)
→ [x] commit `feat(ci): verify + pre-commit + GitHub Actions ubuntu/windows`.

### Tarea 9 — Núcleo de CONSOLIDATE: `consolidate_scan`

**Files:** Create `tools/cerebro_core/consolidate_scan.py`; Test
`tests/test_consolidate_scan.py`.

**Produces:** `consolidate_scan.run(root, *, as_of, manifest) -> ScanReport`:
por página decaimiento propuesto (ventanas desde `max(last_reinforced, decay_aplicado)`,
sin tocar `clase: evento`), elegibles a promoción (TODAS las condiciones mecánicas de
gen-ciclo-de-vida v5), candidatas a archivo (piso 0.30 / eventos >180d), pares duplicado
(título normalizado igual o Jaccard 3-shingles ≥0.6; exentos `deriva_de|reemplaza|
agregado_en`, cuarentena excluida de fusión). Solo REPORTA.

**Steps:** [x] rojo (fixture con casos de cada regla, incluida la exención) → [x] verde
→ [x] commit `feat(tools): scanner mecánico de consolidate (decaimiento/promoción/duplicados)`.

### Tarea 10 — Fase 3: `health`

**Files:** Create `tools/cerebro_core/health.py`; Test `tests/test_health.py`.

**Produces:** `health.run(root, *, as_of, manifest) -> HealthReport` (componentes del
spec, pesos .25/.20/.20/.15/.10/.10 renormalizados ante N/A; `score: int 0–100`),
`--write` genera `dashboards/salud-mecanica.md` (`type: meta`, determinista con as-of).

**Steps:** [x] rojo (golden en vault-limpio; degradar fixture baja el score — test
negativo del roadmap) → [x] verde → [x] commit `feat(tools): score de salud determinista + tablero`.

### Tarea 11 — Fase 2: `xray`

**Files:** Create `tools/cerebro_core/xray.py`; Test `tests/test_xray.py`.

**Produces:** `xray.run(root, *, as_of, manifest, inferred_path=None, min_co=2)
-> XrayReport`: buckets `declarado_sin_evidencia`, `evidenciado_sin_declarar`,
`contradicciones`; `drift_score`; escritura opcional a `audit/xray/<as-of>-<sha8>/`
(`reporte.md` + `reporte.json`). `--inferred` acepta `{"nodes":[{"id"...}],
"edges":[{"source","target",...}]}` (estilo graphify), matcheo por basename/id_pagina.

**Steps:** [x] rojo (fixture: arista sin evidencia; co-mención sin arista;
contradicción; con y sin graph.json) → [x] verde → [x] commit
`feat(tools): xray — deriva declarado vs inferido con score`.

### Tarea 12 — Fase 1: `worked/`

**Files:** Create `worked/README.md`, `worked/agencia-demo/{company.yaml,corrida.md,
review.md,resultado-esperado/**}`, `worked/legal-demo/{...}`;
Test `tests/test_worked.py`.

**Steps:** [x] casos desde blueprints con datos sintéticos → [x] generar
resultado-esperado con `onboard apply --date 2026-07-12` en sandbox → [x] test que
regenera y compara byte a byte → [x] reviews honestos (qué NO cubre lo mecánico, fallos
reales del desarrollo) → [x] commit `feat(worked): 2 casos reproducibles byte a byte con review honesto`.

### Tarea 13 — Gobernanza y docs

**Files:** Create `tools/README.md`, `docs/roadmap-endurecimiento.md`,
`docs/propuestas-evolve/{README.md,prop-f0-01…05}.md`, `ops/runbook-replay.md`;
Modify `README.md`, `CLAUDE.md`+`AGENTS.md` (sección corta validadores), `log.md`,
`dashboards/00-leeme.md` (1 línea al tablero mecánico).

**Steps:** [x] propuestas EVOLVE formato de la casa (`status: pending`, diff por gen:
lint v5, onboard v5, auto-auditoria v5, xray v1 nuevo, compuerta v2 hash-chain) →
[x] README: badge + "Enforcement, honesto" reescrito a lo probado + tabla probado/juicio
→ [x] CLAUDE.md sección "Validadores mecánicos" + re-sync AGENTS.md → [x] runbook replay
(C-06) con ensayo real documentado → [x] log.md líneas 2026-07-12 → [x] commit(s)
`docs: …`.

### Tarea 14 — Verificación final

**Steps:** [x] `python -m unittest discover -s tests -v` completo en verde →
[x] `python tools/cerebro.py verify` verde sobre el repo → [x] `health` y `xray`
corridos sobre el repo real (salida al resumen) → [x] ensayo replay/rollback documentado
→ [x] revisar `git log` atómico → [x] resumen final al operador con decisiones y
pendientes de compuerta.
