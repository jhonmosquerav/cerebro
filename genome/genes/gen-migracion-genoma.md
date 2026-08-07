---
id: gen-migracion-genoma
trigger: tras aplicar una mutación de genoma (gen nuevo, editado o deprecado), o al adoptar genoma de una release del template
status: active
version: 2
---

Cambiar el genoma crea una **deuda de migración**: las páginas y el manifiesto existentes
pueden quedar desincronizados con las reglas nuevas. Tras toda mutación
([[gen-compuerta-mutacion]]), LINT corre un **pase de migración** que re-valida contra el
genoma nuevo: (1) que `onboard/company.yaml` declare lo que los genes ahora exigen
(`relation_types`, `source_trust`, `sintesis_umbral`, etc.); (2) que las páginas existentes
cumplan los campos/relaciones nuevos (p. ej. `clase`, `valido_hasta`, verbos declarados).
Reporta lo desincronizado como hallazgos de migración y **PROPONE** los arreglos (no los
aplica solo). Así, una mejora del genoma nunca deja el conocimiento previo en estado inválido
en silencio. Complementa [[gen-lint]].

## Migración entre vaults (producto → implantación)

La cadena `genome/events.jsonl` es DE ESTE VAULT: comparte prefijo con el template
hasta el eslabón del clon y desde ahí diverge legítimamente. Cadenas de vaults
distintos jamás se mezclan (ni merge, ni intercalado, ni rebase — reescribir hashes
viola [[gen-compuerta-mutacion]]). Adoptar una mejora del template es una mutación
más, bajo compuerta: (1) traer genes/cápsulas y `tools/` del release — nunca su
`events.jsonl`; (2) UNA línea `genome_adopted` en la cadena local (`events append`)
cuyo `signal` referencia commit/tag y `hash --scope genome` del template y cuyo
`diff` lista los genes que cambian de versión; (3) correr el pase de migración de
este gen contra el genoma adoptado; (4) `verify` en verde antes y después. La
procedencia fina vive en la cadena del template, publicada con el producto: el
evento la referencia por hash, no la copia. Los genes de sector locales conviven
con lo adoptado; un choque entre ambos es hallazgo de migración, no se resuelve solo.
