---
tipo: propuesta-evolve
tarea: CAT-01
status: approved
fecha: 2026-10-23
genes_afectados: [gen-onboard, gen-migracion-genoma]
origen: entrega 4.3 del plan 2026-10-23 (catálogo de blueprints con versiones y requisito mínimo): la infra existe y está probada; los genes que describen el modo (b) de ONBOARD y la adopción de releases aún no saben que un blueprint tiene versión
---

# Propuesta EVOLVE CAT-01 — `gen-onboard` v9 → v10 y `gen-migracion-genoma` v2 → v3: los blueprints tienen versión y requisito mínimo

## Motivación

gen-onboard v9 describe el modo (b) como "copiar un blueprint". gen-migracion-genoma v2
describe cómo un vault adopta una release del template: genes, cápsulas y `tools/`, con un
evento `genome_adopted`. Ninguno de los dos sabe que un blueprint **tiene versión**, así
que hoy no hay respuesta mecánica a dos preguntas que la distribución (Fase 4) vuelve
cotidianas: *¿de qué versión de blueprint nació este vault?* y *¿este blueprint corre con
el `tools/` que tengo?*

La Fase 4.3 añadió la infra, probada y sin tocar el genoma (`tests/test_blueprints.py`,
32 casos): el bloque `blueprint: {id, version, min_cerebro}` dentro de cada blueprint, el
catálogo `onboard/blueprints/catalog.yaml` con historial, el subcomando `blueprints`, los
detectores CAT-01…CAT-06 dentro de `verify`, y el rechazo —antes de escribir nada— de un
`min_cerebro` mayor que la versión instalada, en `init` y en `onboard apply`. Por la misma
razón por la que v5 nombró `onboard apply` y v9 nombró `init`: lo que un script ya hace no
se re-deriva a mano, y el agente debe saber que existe para usarlo.

El patrón viene de obsidian-releases (`manifest.json` con `version`/`minAppVersion`,
`community-plugins.json`, `versions.json`), señalado en la revisión del 2026-10-20 como la
pieza que faltaba para la Fase 4.3.

## Diff propuesto

### `gen-onboard` v9 → v10

Añadir, tras el párrafo "Manifiesto semilla (v9)", este párrafo:

> **Catálogo de blueprints (v10).** Cada blueprint de `onboard/blueprints/` declara su
> identidad en el bloque `blueprint: {id, version, min_cerebro}` (id = nombre del archivo,
> semver, versión mínima de `tools/`), y `onboard/blueprints/catalog.yaml` los indexa con su
> historial de versiones. `init --blueprint` copia el bloque **tal cual** al manifiesto: es
> procedencia, no configuración (ONBOARD no lo renderiza y el genoma que produce el
> manifiesto no cambia). `init` y `onboard apply` **rechazan sin escribir nada** un
> blueprint cuyo `min_cerebro` supere la versión instalada: el remedio es adoptar una release
> del template ([[gen-migracion-genoma]]), nunca editar el requisito. `verify` prueba que
> catálogo y archivos coinciden (CAT-01…CAT-06); publicar una versión nueva de un blueprint
> es subir `version` en el archivo, reflejarlo en el catálogo con su línea de historial y
> dejar `python tools/cerebro.py blueprints` en verde. Un manifiesto artesanal (modos a/c)
> no lleva el bloque y es legítimo.

Frontmatter: `version: 9` → `version: 10`.

### `gen-migracion-genoma` v2 → v3

Añadir al final de la sección "Migración entre vaults (producto → implantación)":

> Los blueprints también se adoptan por versión (v3): `python tools/cerebro.py blueprints`
> compara el bloque `blueprint` de `onboard/company.yaml` con el catálogo del template
> traído en la release y lo declara `al día`, `desactualizado` o `desconocido`. Un blueprint
> con versión mayor en el catálogo entra en el **mismo** `genome_adopted` que los genes: su
> `diff` nombra `blueprint <id> <vieja> → <nueva>` junto a los genes de sector que cambian de
> versión, y el pase de migración de este gen valida el manifiesto resultante. Si la release
> sube `min_cerebro` por encima del `tools/` local, primero se adopta `tools/`; el requisito
> no se edita para forzar el aplicado.

Frontmatter: `version: 2` → `version: 3`.

### `CLAUDE.md` (+ `mirror --fix`)

- Fila `ONBOARD` de la tabla de operaciones: añade "blueprints catalogados con versión y
  `min_cerebro`".
- Lista "Validadores mecánicos": nueva viñeta `blueprints [--json]`.

## Infra (ya existe, probada, sin tocar el genoma)

- `tools/cerebro_core/blueprints.py` (semver, catálogo, CAT-01…CAT-06, estado del
  manifiesto), `manifest.py` (propiedad `blueprint` + validación de `min_cerebro`),
  `init_manifest.py` (excluye `catalog.yaml`), `cerebro.py` (subcomando `blueprints`, línea
  en `verify`).
- `onboard/blueprints/catalog.yaml`; bloque `blueprint:` en los 6 blueprints y en los 3
  `worked/*/company.yaml` (sin regenerar nada: `state-hash` intacto); bloque comentado en
  `company.example.yaml`.
- `tests/test_blueprints.py` (32 casos). Suite: 309 OK. `verify` EN VERDE.
- Documentado en `onboard/blueprints/README.md`, `onboard/README.md`, `tools/README.md`,
  `plugin/skills/cerebro/SKILL.md`.

## Compuerta

**Aprobada y aplicada el 2026-10-23**: abierta por la instrucción end-to-end del operador en
la sesión 2026-10-23 ("termina la actualización de inicio a fin y actualiza el README"),
misma doctrina que la tanda PRF-01/02/03; dos eventos `gene_edited` con hash-chain, un commit
firmado por mutación. Receta seguida: aplicar
los dos diffs, subir versiones, `python tools/cerebro.py events append --type gene_edited
--target gen-onboard …` y otro para `gen-migracion-genoma`, ajustar `CLAUDE.md`,
`mirror --fix`, 1 commit firmado por mutación, y pasar esta fila a ✅ en el README de
propuestas.
