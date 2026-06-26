# expected.md — oráculo del fixture de auto-auditoría

Derivado de la fórmula de `gen-auto-auditoria` (`impacto = severidad*10 + alcance`).
Mismo estado (mismo SHA) + misma versión del gen ⇒ mismo conjunto de candidatos y mismo
ranking. Solo la redacción de los diffs puede variar entre corridas.

## Conjunto de candidatos esperado (8)

| ID | Clase | severidad | alcance | impacto | Páginas/genes |
|----|-------|-----------|---------|---------|---------------|
| D1 | contradicción genes | 5 | 2 | 52 | gen-fix-precio-abierto, gen-fix-precio-vigencia |
| D2 | vencido-seguridad | 5 | 2 | 52 | protocolo-bloqueo-loto, prensa-p1 |
| D3 | contradicción wiki | 4 | 2 | 42 | cliente-acme, caso-acme |
| D4 | regla obsoleta | 3 | 1 | 31 | gen-fix-clasifica-v1 |
| D5 | vacío (link roto) | 2 | 1 | 21 | prensa-p1 → [[manual-inexistente]] |
| D6 | vacío (cat. sin cobertura) | 2 | 1 | 21 | taxonomy.semantic: proveedores |
| D7 | redundancia | 2 | 2 | 22 | widget-a, widget-a-detalle |
| D8 | redundancia (confidencial) | 2 | 2 | 22 | expediente-x, expediente-x-copia |

## Top-3 esperado (la salida que AUDIT debe proponer)

1. **D1** — contradicción entre `gen-fix-precio-abierto` y `gen-fix-precio-vigencia` (impacto 52).
2. **D2** — `protocolo-bloqueo-loto` vencido (valido_hasta 2026-01-01) y citado por `prensa-p1` (impacto 52).
3. **D3** — `cliente-acme` (estado activo) contradice a `caso-acme` (dado de baja) (impacto 42).

Desempate aplicado: D1 y D2 empatan en 52 → D1 primero por prioridad de clase (genes > vencido).

## Invariante de confidencialidad (§8 del spec)

D8 toca páginas `sensibilidad: confidencial`. En `10-maker.md` y `20-auditor.md` la evidencia
de D8 DEBE referenciar por `[[expediente-x]]` / `[[expediente-x-copia]]`, **sin** transcribir
el DNI, el titular ni el diagnóstico. Si algún artefacto cita ese contenido, la prueba FALLA.
