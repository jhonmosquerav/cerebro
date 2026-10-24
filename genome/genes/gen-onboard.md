---
id: gen-onboard
trigger: operación ONBOARD (primera vez o cambio de empresa)
status: active
version: 10
---

ONBOARD adapta el cerebro a una empresa de forma **REPRODUCIBLE**. Fuente de verdad: el
manifiesto `onboard/company.yaml` (esquema en `onboard/company.example.yaml`). Tres modos:
(a) aplicar un `company.yaml` existente; (b) copiar un blueprint de `onboard/blueprints/`;
(c) entrevista que **escribe primero** `company.yaml` y luego aplica.

El aplicado es MECÁNICO: tras tener `onboard/company.yaml` completo (modo a,
b, o el que produce la entrevista del modo c), el agente ejecuta
`python tools/cerebro.py onboard apply --date <hoy>` y reporta su salida.
La herramienta valida todo antes de escribir nada (placeholders sin
rellenar, gen en conflicto o lente sin backend ⇒ aborta sin escritura
parcial), renderiza `company-profile.md`, crea la taxonomía, siembra cada
`seed_gene` con su línea `gene_added` en `events.jsonl` (hash-chain) y
actualiza el bloque Estado de `index.md`. Mismo manifiesto + misma fecha →
mismo hash de estado (probado en CI: `tests/test_onboard.py`, `worked/`).
Siguen siendo del agente: la entrevista que escribe el manifiesto, la
pregunta única de `graph_lens.backend` cuando la lente está activa sin
backend (la herramienta aborta a propósito en ese caso), las
recomendaciones de vistas ([[gen-visualizacion]]) y el commit de la corrida.

**Manifiesto semilla (v9).** Los modos (a) y (b) arrancan con
`python tools/cerebro.py init --profile <minimo|memoria|gobernanza|completo>
[--blueprint <sector>]`: copia `onboard/company.example.yaml` o el blueprint a
`onboard/company.yaml` con `profile:` fijado ([[gen-perfiles]]) y **nada más tocado**; es
idempotente, no pisa un manifiesto distinto sin `--force`, conserva tal cual los
placeholders `<...>` del blueprint (rellenarlos es del operador o de la entrevista del
modo c) y no aplica nada: el aplicado sigue siendo `onboard apply`. El agente propone
`init` antes que copiar archivos a mano. El plugin de marketplace (`plugin/`) es solo un
envoltorio de estos pasos y de los verbos de `CLAUDE.md`: no contiene genes ni reglas, y
cualquier regla que necesite vivir en él pasa primero por esta compuerta.

**Catálogo de blueprints (v10).** Cada blueprint de `onboard/blueprints/` declara su
identidad en el bloque `blueprint: {id, version, min_cerebro}` (id = nombre del archivo,
semver, versión mínima de `tools/`), y `onboard/blueprints/catalog.yaml` los indexa con su
historial de versiones. `init --blueprint` copia el bloque **tal cual** al manifiesto: es
procedencia, no configuración (ONBOARD no lo renderiza y el genoma que produce el
manifiesto no cambia). `init` y `onboard apply` **rechazan sin escribir nada** un
blueprint cuyo `min_cerebro` supere la versión instalada: el remedio es adoptar una release
del template ([[gen-migracion-genoma]]), nunca editar el requisito. `verify` prueba que
catálogo y archivos coinciden (CAT-01…CAT-06); publicar una versión nueva de un blueprint
es subir `version` en el archivo, reflejarlo en el catálogo con su línea de historial y
dejar `python tools/cerebro.py blueprints` en verde. Un manifiesto artesanal (modos a/c)
no lleva el bloque y es legítimo.

La herramienta **AVISA** (no aborta) cuando la `taxonomy` del manifiesto no ofrece destino
para alguno de los tipos de página que el genoma declara —en particular `sintesis`, que el
propio manifiesto se compromete a producir al fijar `sintesis_umbral`—. Es aviso y no error
porque una empresa puede decidir legítimamente no usar un tipo; lo que no puede es
descubrirlo a mitad de un CONSOLIDATE. Cambiar la taxonomía **después** de aplicar rompe la
reproducibilidad desde el manifiesto (mismo manifiesto → mismo genoma), así que el aviso
llega en el único momento en que corregirlo es gratis.

**Replay sobre un vault vivo (v7).** Re-aplicar el manifiesto sobre un vault que ya operó
no aborta por evolución legítima: un seed cuyo gen es idéntico módulo la fecha del pie de
siembra es no-op (se compara contenido, no calendario), y un gen que difiere del seed pero
tiene su mutación registrada como `applied` en `events.jsonl` se respeta sin tocarlo —
ONBOARD jamás pisa un gen y la verdad del gen evolucionado es el ledger, no el seed. Solo
aborta el caso ilegítimo: un gen distinto **sin** mutación registrada (deriva fuera de
compuerta). Probado en `tests/test_onboard.py::TestSeedsEvolucionados`.

**Perfil de instalación (v8).** Si el manifiesto declara `profile:` o `capabilities:`
([[gen-perfiles]]), el aplicado también renderiza `genome/perfil.md` (frontmatter plano con
el perfil y cada `cap_<capacidad>`), añade la línea `- Perfil:` al bloque `## Estado` de
`index.md` y registra `profile_applied` en `events.jsonl` **solo si cambia el conjunto
efectivo** (re-aplicar es no-op; cambiar de perfil deja una línea con `anterior → nuevo`).
Sin declaración no escribe nada: el perfil es `completo` y el hash del vault no cambia. El
archivo aplicado jamás se edita a mano: se cambia el manifiesto (`python tools/cerebro.py
profile set|enable|disable` lo hace sin tocar el resto) y se re-corre `onboard apply`. En
la entrevista, el agente explica qué apaga cada perfil antes de escribir el manifiesto.

No ingiere contenido: ONBOARD solo configura.
