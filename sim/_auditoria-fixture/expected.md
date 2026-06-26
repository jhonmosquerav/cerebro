# expected.md — oráculo del fixture de auto-auditoría

Derivado de la fórmula de `gen-auto-auditoria` (`impacto = severidad*10 + alcance`).
**Desde v2 del gen, el conteo de `alcance` es explícito por clase** (página defectuosa + páginas
citantes de primer nivel; ambos genes del par obsoleto; confidenciales SÍ cuentan), así que el
±1 no-determinista que existía en v1 quedó **cerrado**. Invariante reproducible: mismo estado
(mismo SHA) + misma versión del gen ⇒ **mismo conjunto de candidatos, mismos scores exactos y
mismo top-3**. Lo único que varía entre corridas es la redacción de la prosa de los `diff`.
Los `alcance` de esta tabla coinciden con la regla v2 (D2 vencido = página+citante = 2;
D4 obsolescencia = ambos genes = 2).

## Conjunto de candidatos esperado (8)

| ID | Clase | severidad | alcance | impacto | Páginas/genes |
|----|-------|-----------|---------|---------|---------------|
| D1 | contradicción genes | 5 | 2 | 52 | gen-fix-precio-abierto, gen-fix-precio-vigencia |
| D2 | vencido-seguridad | 5 | 2 | 52 | protocolo-bloqueo-loto, prensa-p1 |
| D3 | violación de invariante (gen-entidad-con-estado) | 4 | 2 | 42 | cliente-acme, caso-acme |
| D4 | regla obsoleta | 3 | 2 | 32 | gen-fix-clasifica-v1, gen-fix-clasifica-v2 |
| D5 | vacío (link roto) | 2 | 1 | 21 | prensa-p1 → [[manual-inexistente]] |
| D6 | vacío (cat. sin cobertura) | 2 | 1 | 21 | taxonomy.semantic: proveedores |
| D7 | redundancia | 2 | 2 | 22 | widget-a, widget-a-detalle |
| D8 | redundancia (confidencial) | 2 | 2 | 22 | expediente-x, expediente-x-copia |

> Nota v3: D3 (cliente-acme activo vs caso-acme baja) aplica a dos clases sev-4 (violación de
> invariante de [[gen-entidad-con-estado]] y contradicción wiki). **Desde v3 la selección de clase
> es determinista**: gana la fila superior de la tabla → "violación de invariante". Así, tanto el
> score (42) como la **clase** son reproducibles. (El auditor v2 ya había derivado esta clase; v3
> la codifica como regla.)

## Top-3 esperado (la salida que AUDIT debe proponer)

1. **D1** — contradicción entre `gen-fix-precio-abierto` y `gen-fix-precio-vigencia` (impacto 52).
2. **D2** — `protocolo-bloqueo-loto` vencido (valido_hasta 2026-01-01) y citado por `prensa-p1` (impacto 52).
3. **D3** — `cliente-acme` (estado activo) contradice a `caso-acme` (dado de baja) (impacto 42).

Desempate aplicado: D1 y D2 empatan en 52 → D1 primero por prioridad de clase (genes > vencido).

## Invariante de confidencialidad (§8 del spec)

D8 toca páginas `sensibilidad: confidencial`. En `10-maker.md` y `20-auditor.md` la evidencia
de D8 DEBE referenciar por `[[expediente-x]]` / `[[expediente-x-copia]]`, **sin** transcribir
el DNI, el titular ni el diagnóstico. Si algún artefacto cita ese contenido, la prueba FALLA.

## Nota de calibración (corrida 2026-06-25-dc198a0)

D4 se corrigió de `alcance 1 / impacto 31` a `alcance 2 / impacto 32` tras la primera corrida.
Motivo: el maker y el auditor —dos agentes con contexto aislado, sin ver este oráculo— derivaron
ambos `alcance=2` para la obsolescencia (los DOS genes del solape están afectados:
`gen-fix-clasifica-v1` subsumido y `gen-fix-clasifica-v2` que lo subsume). El error estaba en
este oráculo (cálculo a mano), no en la implementación; la convergencia independiente de ambos
roles es, de hecho, evidencia de la reproducibilidad. El top-3 nunca cambió (D4=32 sigue 4º, < 42).
Recomendación abierta: hacer explícito en una futura versión del gen el conteo de `alcance` por
clase (p. ej. obsolescencia = ambos genes del solape) para eliminar la ambigüedad de raíz.
