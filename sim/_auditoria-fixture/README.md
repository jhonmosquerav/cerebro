# sim/_auditoria-fixture — prueba de capacidad (no es un vertical)

Base CEREBRO mínima con **defectos plantados y conocidos** para verificar la operación
`AUDIT` de forma reproducible. El prefijo `_` la marca como prueba de capacidad, no como
industria. Sandbox aislado: NO toca `D:/cerebro/genome` ni `D:/cerebro/wiki`.

## Defectos plantados
- D1 — contradicción entre 2 genes activos (`gen-fix-precio-abierto` vs `gen-fix-precio-vigencia`).
- D2 — info vencida en dominio de seguridad (`protocolo-bloqueo-loto`, citado por `prensa-p1`).
- D3 — contradicción entre 2 páginas wiki (`cliente-acme` vs `caso-acme`).
- D4 — gen obsoleto: `gen-fix-clasifica-v1` subsumido por `gen-fix-clasifica-v2` (trigger solapado).
- D5 — vacío: `prensa-p1` enlaza `[[manual-inexistente]]` (link roto).
- D6 — vacío: la taxonomía declara la categoría `proveedores` sin ninguna página.
- D7 — redundancia: `widget-a` y `widget-a-detalle` casi-duplicadas.
- D8 — redundancia confidencial: `expediente-x` y `expediente-x-copia` (prueba de [[gen-confidencialidad]]).

El top-3 esperado por la fórmula del gen está en `expected.md`.
