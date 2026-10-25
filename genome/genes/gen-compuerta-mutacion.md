---
id: gen-compuerta-mutacion
trigger: cualquier cambio dentro de genome/
status: active
version: 5
---

Ninguna mutación del genoma (crear, editar o deprecar un gen o cápsula) se aplica sola.
Flujo obligatorio en modo híbrido: (1) PROPÓN el cambio mostrando el diff y la señal que
lo motiva; (2) espera mi aprobación explícita; (3) solo entonces aplica el cambio,
incrementa `version` del gen, añade la línea a `genome/events.jsonl` CON hash-chain usando
`python tools/cerebro.py events append --type <tipo> --target <gen> --signal "<señal>"
--diff "<diff>"` (valida el esquema y encadena `prev`=sha256 de la línea anterior; escribir
la línea a mano deja la cadena con aviso EVT-06 en `verify`) y haz un commit de git;
(4) re-sincroniza `AGENTS.md` con `CLAUDE.md`.
Editar manualmente este gen también requiere registrar el evento.

La cadena es DE ESTE VAULT. Adoptar genoma de otro origen (p. ej. una release del
template) se registra como UNA mutación `genome_adopted` según el camino declarado
en [[gen-migracion-genoma]]; importar, intercalar o re-encadenar líneas de la cadena
de otro vault está prohibido — el append-only protege la historia local, y la del
origen viaja con el origen.

Atribución de la aprobación (C-04): `approved_by` lleva la identidad del aprobador —
la de `ops/allowed_signers` cuando exista; nunca un genérico sin dueño — y el contexto
registrado debe permitir localizar dónde se dio la aprobación (fecha + canal). `events
append` (y `onboard apply`) la resuelven solos: la clave de `user.signingkey` buscada en
`ops/allowed_signers`, si no `git user.email`, y si no hay ninguna abortan sin escribir; un
genérico (`user`, `operador`, `agente`…) se rechaza en cuanto el ledger tiene una línea
atribuida, y `verify` lo delata (EVT-09). Las líneas anteriores a la primera atribución son
historia válida. Una atribución equivocada no se reescribe: se cura con un evento
`attribution_corrected` cuyo `corrects` lista el sha256 de las líneas corregidas, firmado por
el aprobador real, con fecha y canal de la aprobación original en `signal` (EVT-10 valida su
forma). Desde que el operador registra su clave en `ops/allowed_signers`, los commits que
tocan `genome/` se firman (SSH, `git verify-commit`); un commit de mutación sin firma válida
es hallazgo de AUDIT. Runbook: `ops/runbook-firma-aprobaciones.md`.

Verificación mecánica del ledger: `python tools/cerebro.py events verify` (esquema por línea
+ cadena + atribución + append-only contra la historia de git). El pre-commit (`.githooks/pre-commit`)
bloquea cualquier commit que reescriba o borre líneas existentes.
