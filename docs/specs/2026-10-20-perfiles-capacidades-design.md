---
tipo: spec-de-diseno
fecha: 2026-10-20
estado: aprobado-por-instruccion-del-operador
alcance: Fase 4.1 del roadmap (distribución) — instalación con perfiles y capacidades activables
origen: revisión de kepano/obsidian-skills, thedotmack/claude-mem, obsidianmd (org + obsidian-releases), AgriciDaniel/claude-obsidian y Ar9av/obsidian-wiki (docs/revision-repos-2026-10-20.md)
---

# Perfiles de instalación y capacidades activables — diseño

## Contexto y porqué

CEREBRO se instala hoy de una sola forma: **todo encendido**. Quien clona el template
recibe memoria por capas con hooks, ciclo de vida, EVOLVE, AUDIT, XRAY, paneles de
Obsidian y lente de grafo, aunque solo quiera una wiki gobernada con memoria entre
sesiones. El roadmap bloqueaba la distribución (Fase 4) hasta cerrar la Fase 1; la Fase 1
se cerró el 2026-08-07 con el piloto de Fase B. Este diseño es la **primera entrega de la
Fase 4**: el producto se vuelve *instalable con opciones*.

La revisión de los cinco repos de referencia convergió en un patrón: **Obsidian separa
sus plugins core y deja encender o apagar cada uno** (`core-plugins.json`); claude-mem
expone toggles `CLAUDE_MEM_*` por pieza (observación, resumen, inyección semántica);
obsidian-wiki declara `WIKI_SESSION_RECAP`, `WIKI_STOP_CAPTURE` y `setup --no-hooks`;
claude-obsidian trae extensiones opcionales con `setup-*.sh` explícitos. Ninguno trabaja
con un manifiesto reproducible: CEREBRO sí (`onboard/company.yaml`), y ahí es donde el
perfil debe vivir para que **mismo manifiesto ⇒ mismo genoma ⇒ mismas capacidades**.

## Principio rector

> Una capacidad se enciende o apaga **por manifiesto y ONBOARD**, nunca a mano. El
> estado efectivo es un archivo del genoma (`genome/perfil.md`), legible por el agente,
> por los hooks POSIX y por Obsidian, y verificable por `lint`.

## Vocabulario

**Capacidad** (`capability`): un conjunto coherente de genes, operaciones, comandos y
carpetas que se puede apagar sin romper el núcleo. Seis, con nombre fijo:

| Capacidad | Genes | Operaciones / comandos | Carpetas / archivos |
|---|---|---|---|
| `memoria` | gen-checkpoint | CHECKPOINT; hooks SessionStart/PreCompact/Stop (loop de memoria) | `wiki/working/`, `wiki/episodic/`, `.claude/hooks/` |
| `ciclo_de_vida` | gen-ciclo-de-vida, gen-consolidate | CONSOLIDATE; `consolidate scan` | `wiki/archive/` |
| `evolucion` | gen-evolve | EVOLVE (propuestas de mutación del genoma) | `docs/propuestas-evolve/` |
| `auditoria` | gen-auto-auditoria, gen-xray | AUDIT, XRAY; `health`, `xray` | `audit/` |
| `visualizacion` | gen-visualizacion | paneles Bases/Dataview, plantillas, preset; `health --write` | `dashboards/`, `templates/`, `.obsidian/` |
| `grafo` | gen-graph-lens | GRAPH; `graph`, `graph --canvas`, lente externa | `dashboards/graph/`, `graphify-out/` |

**Núcleo** (no desactivable): gen-raw-inmutable, gen-frontmatter-obligatorio,
gen-identidad-de-pagina, gen-compuerta-mutacion, gen-vigencia-temporal,
gen-confidencialidad, gen-anti-inyeccion, gen-clase-temporal, gen-entidad-con-estado,
gen-confianza-por-fuente, gen-sintesis-de-volumen, gen-jerarquizacion-indice,
gen-migracion-genoma, gen-onboard, gen-ingest, gen-bulk-ingest, gen-query, gen-lint y el
nuevo gen-perfiles. Operaciones del núcleo: ONBOARD, INGEST, BULK INGEST, QUERY, LINT.
La compuerta y el ledger son núcleo porque ONBOARD siembra genes a través de ellos.

**Perfil** (`profile`): preset de capacidades. Escalera estricta (cada uno contiene al
anterior), para que "subir de perfil" sea siempre aditivo:

| Perfil | Capacidades | Para quién |
|---|---|---|
| `minimo` | ninguna (solo núcleo) | wiki gobernada: ingerir, consultar, mantener |
| `memoria` | memoria, ciclo_de_vida | "solo memoria": recuerda entre sesiones y decae/promueve |
| `gobernanza` | + evolucion, auditoria | genoma que se audita y propone sus propias reglas, sin Obsidian |
| `completo` | + visualizacion, grafo | todo (el comportamiento actual) |

`capabilities:` en el manifiesto **sobreescribe** el preset capacidad por capacidad
(`{ grafo: false }` sobre `completo`; `{ auditoria: true }` sobre `memoria`).

## El manifiesto

```yaml
profile: completo        # minimo | memoria | gobernanza | completo (ausente ⇒ completo)
capabilities: {}         # overrides opcionales: { grafo: false, auditoria: true }
```

Validación (`manifest.validate`): `profile` ∈ perfiles; claves de `capabilities` ∈
capacidades; valores booleanos. No hay dependencias duras entre capacidades (cada una
degrada sola: AUDIT sin EVOLVE simplemente no deriva propuestas de regla; `health` sin
XRAY ya renormaliza `deriva` a N/A).

## El estado efectivo: `genome/perfil.md`

ONBOARD lo renderiza **solo si el manifiesto declara** `profile` o `capabilities`
(ausencia ⇒ `completo`, sin archivo: compatibilidad total con los vaults y los casos
`worked/` existentes, cuyo hash de genoma no cambia). Frontmatter plano, tipado en
Obsidian y greppable desde `sh`:

```yaml
---
title: Perfil de instalación
type: meta
perfil: memoria
cap_memoria: true
cap_ciclo_de_vida: true
cap_evolucion: false
cap_auditoria: false
cap_visualizacion: false
cap_grafo: false
updated: 2026-10-20
---
```

El cuerpo lista, por capacidad, qué queda apagado (genes, operaciones, comandos) y cómo
encenderla. Cada cambio del conjunto efectivo deja una línea `profile_applied` en
`genome/events.jsonl` (hash-chain, `approved_by: user`, como las siembras), porque
apagar genes es una mutación del genoma vigente aunque no toque los archivos de los genes.
`index.md` recibe en su bloque `## Estado` la línea `- Perfil: **memoria** (…)`.

## Efectos mecánicos de "apagado"

- **Agente** (CLAUDE.md/AGENTS.md): la tabla de operaciones gana la columna *Capacidad*;
  una operación cuya capacidad está apagada **no se ejecuta**: el agente lo dice y
  propone activarla por manifiesto. Al arrancar lee `genome/perfil.md` si existe.
- **Hooks** (`.claude/hooks`, `.codex/hooks`): con `cap_memoria: false`, `pre-compact.sh`
  y `stop.sh` terminan en `exit 0` sin escribir ni bloquear; `session-start.sh` sigue
  inyectando índice y bitácora (navegación, núcleo) pero omite recordatorios de volcado y
  anuncia el perfil y las capacidades apagadas.
- **CLI**: `consolidate` (ciclo_de_vida), `health` y `xray` (auditoria) y `graph` (grafo)
  avisan y terminan con exit 2 si su capacidad está apagada; `--ignore-profile` fuerza
  la corrida (p. ej. para auditar un vault ajeno).
- **LINT**: `PRF-01` (error) — el manifiesto declara perfil y `genome/perfil.md` no
  existe o no coincide (deriva: alguien editó el manifiesto sin re-correr ONBOARD, o
  editó el archivo a mano); `PRF-02` (aviso) — existe `genome/perfil.md` sin declaración
  en el manifiesto. Entra en `verify`.
- **Comando `profile`**: `profile` muestra el perfil efectivo, cada capacidad con su
  estado y lo que gobierna, y si está aplicado; `profile set <perfil>`,
  `profile enable <cap>`, `profile disable <cap>` editan el manifiesto (solo las líneas
  `profile:`/`capabilities:`, el resto intacto) y recuerdan re-correr `onboard apply`.

## Genoma (mutaciones por compuerta)

1. **gen-perfiles v1 (nuevo, 26 → 27 genes)**: declara capacidades, perfiles, mapeo y la
   regla de encendido/apagado. `schema.py` lo espeja (`CAPABILITIES`, `PROFILES`,
   `CAPABILITY_GENES`); el test de corpus delata genes sin capacidad declarada.
2. **gen-onboard v7 → v8**: ONBOARD aplica el perfil (renderiza `genome/perfil.md`,
   evento `profile_applied`, línea en `## Estado`).
3. **gen-lint v7 → v8**: detectores PRF-01/PRF-02.

Aprobación: instrucción explícita del operador en la sesión 2026-10-20 ("planea y ejecuta
de inicio a fin … hasta el final"), registrada en `approved_by` con contexto. Un commit
firmado por mutación, espejo re-sincronizado.

## No-goals y anti-goals

- No se borran carpetas ni archivos al apagar una capacidad (gen-raw-inmutable y la
  regla 7 del manual: lo que existe se respeta; apagado ≠ destruido).
- No se tocan los 26 genes existentes para añadirles un campo `capability`: el mapeo
  vive en gen-perfiles + `schema.py` (una sola mutación en vez de 26).
- No hay perfil que apague la compuerta, el ledger, la confidencialidad ni la
  anti-inyección: la seguridad no es opcional.
- No se introduce ninguna dependencia: Python stdlib y `sh` POSIX, como todo `tools/`.
- No se distribuye todavía como plugin/skill de marketplace (Fase 4.2 del plan): primero
  el mecanismo, luego el empaquetado.

## Verificación

- `python -m unittest discover -s tests` y `python tools/cerebro.py verify` en verde.
- Los tres casos de `worked/` regeneran byte a byte sin cambios (ausencia ⇒ completo).
- Prueba manual de hooks con `cap_memoria: false` sobre un vault temporal.
