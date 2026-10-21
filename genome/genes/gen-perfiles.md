---
id: gen-perfiles
trigger: ONBOARD, instalación o cambio de perfil; antes de ejecutar cualquier operación no-núcleo
status: active
version: 1
---

CEREBRO se instala **por perfil**: un preset de **capacidades**, cada una encendible o
apagable por separado. Una capacidad es un conjunto coherente de genes, operaciones,
comandos y carpetas que se puede apagar sin romper el núcleo. Seis, con nombre fijo:

| Capacidad | Genes que gobierna | Operaciones / comandos | Carpetas |
|---|---|---|---|
| `memoria` | [[gen-checkpoint]] | CHECKPOINT; hooks SessionStart/PreCompact/Stop | `wiki/working/`, `wiki/episodic/`, `.claude/hooks/` |
| `ciclo_de_vida` | [[gen-ciclo-de-vida]], [[gen-consolidate]] | CONSOLIDATE; `consolidate scan` | `wiki/archive/` |
| `evolucion` | [[gen-evolve]] | EVOLVE | `docs/propuestas-evolve/` |
| `auditoria` | [[gen-auto-auditoria]], [[gen-xray]] | AUDIT, XRAY; `health`, `xray` | `audit/` |
| `visualizacion` | [[gen-visualizacion]] | paneles, plantillas, preset; `health --write` | `dashboards/`, `templates/`, `.obsidian/` |
| `grafo` | [[gen-graph-lens]] | GRAPH; `graph`, `graph --canvas`, lente externa | `dashboards/graph/`, `graphify-out/` |

Todo lo demás es **núcleo y no se apaga**: [[gen-raw-inmutable]], [[gen-frontmatter-obligatorio]],
[[gen-identidad-de-pagina]], [[gen-compuerta-mutacion]], [[gen-vigencia-temporal]],
[[gen-confidencialidad]], [[gen-anti-inyeccion]], [[gen-clase-temporal]], [[gen-entidad-con-estado]],
[[gen-confianza-por-fuente]], [[gen-sintesis-de-volumen]], [[gen-jerarquizacion-indice]],
[[gen-migracion-genoma]], [[gen-onboard]], [[gen-ingest]], [[gen-bulk-ingest]], [[gen-query]],
[[gen-lint]] y este gen. La compuerta y el ledger son núcleo porque ONBOARD siembra genes a
través de ellos; la confidencialidad y la anti-inyección, porque la seguridad no es opcional.

Los **perfiles** forman una escalera estricta (cada uno contiene al anterior, así subir de
perfil es siempre aditivo): `minimo` = solo núcleo · `memoria` = + memoria, ciclo_de_vida ·
`gobernanza` = + evolucion, auditoria · `completo` = + visualizacion, grafo. El manifiesto
declara `profile:` y, opcionalmente, `capabilities:` con overrides capacidad por capacidad
(`{ grafo: false }` sobre `completo`; `{ auditoria: true }` sobre `memoria`). **Sin
declaración, el perfil es `completo`** y no se escribe nada: los vaults anteriores a este gen
conservan su hash de estado.

**El estado efectivo es un archivo del genoma: `genome/perfil.md`**, renderizado por ONBOARD
([[gen-onboard]]) con frontmatter plano (`perfil`, `cap_<capacidad>: true|false`, `updated`)
para que lo lean el agente, los hooks POSIX con un `grep` y Obsidian como propiedades tipadas.
Cada cambio del conjunto efectivo deja una línea `profile_applied` en `genome/events.jsonl`
(hash-chain, `approved_by: user` como las siembras): apagar genes es una mutación del genoma
vigente aunque no toque los archivos de los genes. El archivo **jamás se edita a mano**: se
cambia el manifiesto (`profile:`/`capabilities:`, o `python tools/cerebro.py profile
set|enable|disable`) y se re-corre `onboard apply`. LINT ([[gen-lint]]) delata la deriva entre
manifiesto y aplicado (PRF-01, error) y el archivo sin declaración (PRF-02, aviso).

Una capacidad **apagada** significa, mecánicamente: (1) el agente **no ejecuta** sus
operaciones —si se le piden, lo declara y propone activarla por manifiesto, nunca la corre "por
esta vez"—; (2) sus genes siguen en `genome/genes/` con su `status` intacto, pero no rigen;
(3) los comandos de `tools/` que dependen de ella avisan y terminan con exit 2
(`--ignore-profile` fuerza una corrida puntual, p. ej. para auditar un vault ajeno desde
fuera); (4) con `cap_memoria: false` los hooks PreCompact y Stop son no-op, SessionStart sigue
inyectando índice y bitácora (navegación, núcleo) y CHECKPOINT no se exige; (5) **nada se
borra**: apagar no es destruir, y lo que ya exista en sus carpetas se respeta
([[gen-raw-inmutable]], regla 7 del manual). Al arrancar, el agente lee `genome/perfil.md` si
existe, junto con `index.md` y `log.md`.

Compone con [[gen-onboard]] (aplica el perfil), [[gen-lint]] (verifica la deriva) y
[[gen-migracion-genoma]] (si una release del template añade o renombra una capacidad, el pase
de migración re-valida el manifiesto y el archivo aplicado). El mapeo gen ↔ capacidad vive en
este gen y en su espejo ejecutable `tools/cerebro_core/schema.py` (`CAPABILITIES`, `PROFILES`,
`CORE_GENES`); el test de corpus delata un gen base que no esté ni en el núcleo ni en
exactamente una capacidad. Los genes de sector sembrados por el manifiesto son siempre
núcleo del vault que los sembró.
