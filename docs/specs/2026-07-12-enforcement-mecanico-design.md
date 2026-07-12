---
tipo: spec-de-diseno
fecha: 2026-07-12
estado: aprobado-en-conversacion
alcance: Fase C del backlog (validadores diferidos) + Fase 0/2/3 del roadmap de endurecimiento
---

# Enforcement mecánico de CEREBRO — diseño

## Contexto y porqué

La evaluación multidisciplinar `2026-07-01-810f24e` valoró a CEREBRO en **2.8/5 (TRL 4)**
con un patrón repetido por 5 de 6 lentes: *diseño y gobernanza sólidos (3.5–4.5),
enforcement por convención (1.5–2)*. Su brecha #3 textual: **"cero invariantes tienen
protección mecánica: raw/ inmutable, append-only, frontmatter, compuerta — todo descansa
en que el LLM obedezca prosa"**. El backlog (`60-backlog.md`) difería ese enforcement como
**Fase C** con riesgo aceptado documentado.

El operador decidió (conversación 2026-07-10/12, roadmap de endurecimiento) **pagar esa
deuda ahora**: la tesis de CEREBRO es *gobierno del conocimiento con trazabilidad de grado
auditoría*, y un sistema auditable sin verificador mecánico es una contradicción
performativa. Este diseño ejecuta C-01, C-02, C-03, C-05 y C-06 del backlog, más los
criterios de salida de las Fases 0 (Verdad), 2 (XRAY) y 3 (Salud) del roadmap.

## Principio rector

> **El LLM nunca decide lo que un script puede decidir; el script nunca redacta juicio.**

Cada operación se parte en **núcleo mecánico** (Python puro, determinista, testeable) y
**capa de juicio** (LLM, con compuerta y auditoría). La identidad de cada hallazgo la fija
el detector; el LLM juzga relevancia y redacta propuestas — exactamente la doctrina que
[[gen-auto-auditoria]] v4 ya enuncia para AUDIT, ahora con detectores reales.

| Operación | Núcleo mecánico (`tools/`, 0 LLM) | Juicio (LLM + compuerta) |
|---|---|---|
| `LINT` | huérfanas, enlaces rotos, frontmatter inválido, campos/verbos fuera de esquema, vencido duro/blando, id_pagina≠ruta, ledger vs raw/, confidencial anclada | contradicciones semánticas (detector b), redacción de arreglos |
| `ONBOARD` | aplicado del manifiesto: perfil, taxonomía, seed_genes, events, index | la entrevista que *genera* `company.yaml` |
| `CONSOLIDATE` | ventanas de decaimiento, elegibilidad de promoción, candidatos a archivo y a duplicado (léxico) | decisión de fusión, redacción del consolidado |
| `AUDIT` | los detectores de LINT/CONSOLIDATE como insumo del maker | ¿importa?, diff propuesto, score argumentado |
| `XRAY` (nuevo) | deriva declarado vs inferido + score | interpretación de las derivas |
| salud | scorecard determinista | recomendaciones |
| invariantes | espejo AGENTS≡CLAUDE, integridad/append-only/hash-chain de events.jsonl, pre-commit | — |

## Decisiones de arquitectura

1. **Python 3.10+ stdlib puro, cero dependencias.** Coherente con "sin infraestructura":
   un auditor corre los validadores con cualquier Python, sin pip. Costo asumido: parser
   YAML propio de **subconjunto estricto** (`miniyaml`) que falla ruidosamente ante YAML
   exótico — eso es un rasgo, no una limitación: el frontmatter y el manifiesto de CEREBRO
   quedan definidos como ese subconjunto validable. *(Ajuste durante la construcción: el
   subconjunto incluye bloques `|`/`>` de indentación uniforme porque las reglas de los
   blueprints reales los usan; anclas, tags, multidocumento y tabs siguen rechazados.)*
2. **Determinismo verificable.** Salidas ordenadas y estables byte a byte; toda fecha entra
   por parámetro (`--as-of`, `--date`) y queda impresa en el reporte; normalización LF en
   todo hash/comparación (Windows CRLF ≡ Linux LF); sin aleatoriedad ni reloj implícito.
3. **La compuerta se respeta.** Este trabajo NO muta el genoma: los genes que deben
   evolucionar para consumir los núcleos mecánicos quedan como propuestas EVOLVE
   `status: pending` en `docs/propuestas-evolve/` (patrón de `70-propuestas-evolve/`).
   Los validadores son `[infra]` (precedente: A-02 hooks, A-07 staging, A-10 permissions).
4. **CLI única**: `python tools/cerebro.py <comando>`. Comandos: `lint`, `mirror`,
   `events verify|append`, `hash`, `onboard apply`, `consolidate scan`, `health`, `xray`,
   `verify`. Todos aceptan `--vault DIR` (default: raíz del repo) — los tests y `worked/`
   operan sobre vaults sandbox.
5. **Tests stdlib `unittest`** (sin pytest: cero deps también para probar). CI en GitHub
   Actions, matriz ubuntu + windows — el determinismo cross-OS es parte de la afirmación.
6. **`raw/` inmutable, también aquí:** ningún comando escribe en `raw/`; el pre-commit
   bloquea modificaciones/borrados staged bajo `raw/` (añadir fuentes nuevas es legítimo).

## Esquema mecánico (espejo del genoma)

Derivado de los genes v-actuales; `tools/cerebro_core/schema.py` es su espejo ejecutable y
se actualiza con las mutaciones del genoma (documentado en `tools/README.md`):

- **Requeridos** (gen-frontmatter-obligatorio v6): `title, type, tier, tags, confidence,
  created, last_reinforced, decay_rate, sources, relations`.
- **Opcionales → gen que los declara**: `valido_hasta`,`vigencia`→vigencia-temporal;
  `sensibilidad`→confidencialidad; `clase`,`fecha_evento`,`volatile_fields`→clase-temporal;
  `estado`→entidad-con-estado; `id_pagina`,`id_alias`→identidad-de-pagina;
  `riesgo_inyeccion`→anti-inyeccion; `decay_aplicado`,`archivado`→ciclo-de-vida.
- **Enums**: `tier ∈ {working,episodic,semantic,procedural,archive}`;
  `decay_rate ∈ {high,medium,low}`; `sensibilidad ∈ {publico,interno,confidencial}`;
  `clase ∈ {estable,evento}`; `vigencia ∈ {vigente,derogada,no-vigente,en-revision}`;
  `type ∈ {concepto,entidad,fuente,sintesis,sop,observacion,sesion,hub,meta}`.
- **Verbos de relación**: núcleo `{usa,depende_de,contradice,reemplaza}` ∪ verbos de genes
  `{agrega,agregado_en,sucede_a,proviene_de,corrobora,deriva_de}` ∪ `relation_types` del
  manifiesto. `relations` acepta dict verbo→(target|lista) o vacío (`{}`/`[]`).
- **Exenciones**: `type: meta` exenta de frontmatter completo y de huérfanos (gen v6);
  `type: hub` con reglas propias (confidence 1.0, sources [], nunca lista confidenciales).
- **events.jsonl**: claves `{ts,type,target,signal,diff,approved_by,status}`; extensión
  opcional `prev` (sha256 de la línea anterior, hash-chain C-03) que solo escribe
  `events append`; las 63 líneas históricas sin `prev` siguen siendo válidas (la cadena se
  verifica desde la primera línea que la porta).
- **Slug** (gen-identidad-de-pagina v2): minúsculas → sin diacríticos → `[^a-z0-9]`→`-` →
  colapsar `-` → recortar extremos → máx 60 (recorte de `-` final) → vacío ⇒ `f-<hash8>`.

## ONBOARD mecánico (la prueba de reproducibilidad)

`onboard apply --manifest M --vault V --date D` — **valida-todo-luego-escribe** (nada
parcial). Efectos deterministas: (1) `genome/company-profile.md` se **re-renderiza
completo** desde el manifiesto (plantilla canónica versionada con la herramienta,
`status: configurado`, `updated: D`); (2) carpetas de taxonomía + categorías de `entities`
con `.gitkeep`; (3) cada `seed_genes` → `genome/genes/<id>.md` (frontmatter estándar,
`version: 1`); gen ya existente idéntico ⇒ no-op, distinto ⇒ **error** (jamás pisa);
(4) 1 línea por gen NUEVO en `genome/events.jsonl` (`type: gene_added`,
`approved_by: "user"` — el manifiesto ES la aprobación del operador, gen-onboard v4);
(5) bloque `## Estado` de `index.md` re-escrito (Fase configurado + empresa).
`graph_lens.enable` sin `backend` ⇒ **error ruidoso** (la elección es del humano/entrevista,
nunca del script). **Garantía probada en CI**: mismo manifiesto + misma fecha sobre dos
vaults limpios ⇒ mismo hash de estado; re-aplicar ⇒ cero cambios (idempotencia).

## XRAY (Fase 2 — deriva declarado vs inferido)

Grafo **declarado** = `relations` del frontmatter. **Evidencia mecánica** de una arista
A→B (cualquiera): wikilink en el cuerpo (A↔B), `sources` compartidas, co-mención de ambos
en un archivo de `raw/` o en el cuerpo de una tercera página, o arista presente en un
`graph.json` externo (`--inferred`, formato nodos/aristas estilo graphify — adaptador
opcional, CEREBRO funciona sin él). Salidas: **declarado-sin-evidencia**,
**evidenciado-sin-declarar** (co-mención ≥ umbral sin arista), **contradicciones**
(`contradice` declarados + `reemplaza` recíproco). **Score de deriva** = aristas con
evidencia / aristas declaradas. Reporte a `audit/xray/<as-of>-<sha8>/` (md + json);
**propone, jamás aplica**; páginas confidenciales se citan por ruta/id, nunca contenido
(doctrina de gen-auto-auditoria). El gen y la operación se PROPONEN por compuerta
(`prop-f0-04`); la herramienta es infra utilizable desde ya.

## Salud (Fase 3 — scorecard determinista)

`health` → componentes 0–100: **higiene** (páginas sin errores FM/REL), **conectividad**
(sin huérfanas ni enlaces rotos), **vigencia** (sin vencidos duros/blandos), **cobertura**
(fuentes de `raw/` con línea terminal en el ledger; N/A si `raw/` vacío), **deriva** (score
XRAY si existe reporte; N/A si no), **genoma** (espejo + events + genes parsean). Score
único ponderado (pesos en `health.py`, renormalizados ante N/A: higiene .25, conectividad
.20, vigencia .20, cobertura .15, deriva .10, genoma .10). `--write` genera
`dashboards/salud-mecanica.md` (`type: meta`). **Test negativo obligatorio**: degradar un
vault fixture baja el score de forma predecible.

## Casos trabajados (Fase 1 — inicio honesto)

`worked/` con contrato (`README.md`) + 2 casos sintéticos re-corribles (`agencia-demo`,
`legal-demo`): `company.yaml`, `corrida.md` (comandos exactos), `resultado-esperado/`
(bytes exactos del delta: genes sembrados, perfil, events, index) y `review.md` **honesto**
(qué cubre el aplicado mecánico, qué queda en juicio, qué falló al construirlo). Un test de
CI regenera cada caso en sandbox y compara byte a byte. *Limitación declarada:* son casos
de estructura (ONBOARD), no de contenido con corpus real — el piloto B-01…B-06 sigue
pendiente y NO se marca cumplido con esto.

## Qué NO hace este trabajo

- **No muta genes** (propuestas pendientes de compuerta en `docs/propuestas-evolve/`).
- **No toca `raw/`** ni reescribe `events.jsonl` (solo append vía herramienta).
- **No ejecuta el piloto con datos reales** (Fase B del backlog) ni C-04 (firma de
  aprobaciones, requiere decisión de diseño del operador).
- **No empaqueta distribución** (Fase 4 del roadmap): distribuir antes de verificar
  amplifica el problema.
- **No reemplaza el juicio**: contradicciones semánticas, fusiones y redacción siguen
  siendo del LLM bajo compuerta.

## Criterios de salida (verificables)

- [ ] CI verde (ubuntu + windows) con badge en README.
- [ ] `onboard apply` demostrablemente reproducible e idempotente (tests).
- [ ] `lint`, `mirror`, `events verify`, `hash`, `health`, `xray` corren sin LLM y su
      salida es determinista (tests de fixtures con violaciones sembradas).
- [ ] El propio repo pasa `verify` en verde.
- [ ] Hash-chain disponible para líneas nuevas de events.jsonl + append-only verificado
      contra la historia git (C-03) y ensayo de replay documentado (C-06).
- [ ] Pre-commit local instalable que bloquea `raw/` y no-append de events (C-05).
- [ ] README ya no afirma nada que el CI no pruebe (tabla probado vs juicio).
- [ ] 2 casos `worked/` regenerables byte a byte en CI con review honesto.
