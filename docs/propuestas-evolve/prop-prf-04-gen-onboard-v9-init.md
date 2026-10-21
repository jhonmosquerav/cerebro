---
tipo: propuesta-evolve
tarea: PRF-04
status: pending
fecha: 2026-10-20
genes_afectados: [gen-onboard]
origen: entrega 4.2 del plan 2026-10-20 (empaquetado instalable): `init --profile` y el plugin mínimo ya existen como infra; el gen que describe los modos de ONBOARD aún no sabe que el manifiesto semilla puede nacer mecánicamente
---

# Propuesta EVOLVE PRF-04 — `gen-onboard` v8 → v9: `init` como camino mecánico del manifiesto semilla

## Motivación

gen-onboard v8 describe tres modos: (a) aplicar un `company.yaml` existente, (b) copiar un
blueprint, (c) entrevista que escribe el manifiesto. Los modos (a) y (b) empezaban con un
`cp` a mano y, desde gen-perfiles v1, con un `profile set` aparte. La Fase 4.2 añadió
`python tools/cerebro.py init --profile <p> [--blueprint <s>]`, que hace ese arranque
**mecánico, idempotente y sin pisar** lo existente, con el perfil de instalación fijado
desde el primer byte. El gen debería nombrar ese camino, por la misma razón por la que v5
nombró `onboard apply`: lo que un script ya hace no se re-deriva a mano, y el agente debe
saber que existe para proponerlo en vez de copiar archivos.

También conviene que el gen fije el límite del **plugin de marketplace** (`plugin/`): es un
envoltorio que enseña a clonar, `init` y `onboard apply`, y remite al `CLAUDE.md` del vault;
nunca contiene genes ni reglas. Si no se dice en el genoma, un mantenedor futuro podría
"mejorar" la skill copiando reglas dentro, y nacería un segundo genoma sin compuerta.

## Diff propuesto (v8 → v9)

Añadir, tras el párrafo "El aplicado es MECÁNICO…", este párrafo:

> **Manifiesto semilla (v9).** Los modos (a) y (b) arrancan con
> `python tools/cerebro.py init --profile <minimo|memoria|gobernanza|completo>
> [--blueprint <sector>]`: copia `onboard/company.example.yaml` o el blueprint a
> `onboard/company.yaml` con `profile:` fijado ([[gen-perfiles]]) y **nada más tocado**; es
> idempotente, no pisa un manifiesto distinto sin `--force`, conserva tal cual los
> placeholders `<...>` del blueprint (rellenarlos es del operador o de la entrevista del
> modo c) y no aplica nada: el aplicado sigue siendo `onboard apply`. El agente propone
> `init` antes que copiar archivos a mano. El plugin de marketplace (`plugin/`) es solo un
> envoltorio de estos pasos y de los verbos de `CLAUDE.md`: no contiene genes ni reglas, y
> cualquier regla que necesite vivir en él pasa primero por esta compuerta.

Frontmatter: `version: 8` → `version: 9`. Sin cambios en el resto del gen ni en otros genes.
`CLAUDE.md`: fila `ONBOARD` de la tabla de operaciones añade "(`init --profile` deja el
manifiesto semilla)"; luego `mirror --fix`.

## Infra (ya existe, probada, sin tocar el genoma)

- `tools/cerebro_core/init_manifest.py` + subcomando `init` en `tools/cerebro.py`
  (reutiliza `profile.edit_manifest_text`; exit 2 si pisaría o si el perfil/blueprint no existe).
- `tests/test_init.py` (17 casos: idempotencia, no pisa, `--force`, los 4 perfiles, los 6
  blueprints con placeholders intactos, `init` → `onboard apply` deja `genome/perfil.md`) y
  `tests/test_plugin.py` (manifiestos JSON coherentes, skill con frontmatter que remite al repo).
- `.claude-plugin/marketplace.json` → `plugin/` (`plugin.json`, `skills/cerebro/SKILL.md`, README).
- Documentado en `README.md` (Inicio rápido), `tools/README.md`, `onboard/README.md`,
  `onboard/blueprints/README.md`.

## Compuerta

**Pendiente.** No se ha tocado `genome/genes/gen-onboard.md` ni `genome/events.jsonl`. Al
aprobar: aplicar el diff, `version: 9`, `python tools/cerebro.py events append --type
gene_edited --target gen-onboard --signal "PRF-04: init como manifiesto semilla" --diff
"v8 -> v9"`, ajustar la fila ONBOARD de `CLAUDE.md`, `mirror --fix`, 1 commit firmado,
y pasar esta fila a ✅ en `docs/propuestas-evolve/README.md`.
