---
id: gen-compuerta-mutacion
trigger: cualquier cambio dentro de genome/
status: active
version: 3
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

Verificación mecánica del ledger: `python tools/cerebro.py events verify` (esquema por línea
+ cadena + append-only contra la historia de git). El pre-commit (`.githooks/pre-commit`)
bloquea cualquier commit que reescriba o borre líneas existentes.
