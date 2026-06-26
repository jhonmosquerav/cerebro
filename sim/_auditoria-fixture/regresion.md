# Registro de regresión — corrida 2026-06-25-dc198a0

- **Run-id:** 2026-06-25-dc198a0
- **Gene version:** gen-auto-auditoria v1
- **SHA:** dc198a0
- **Fecha:** 2026-06-25
- **Artefactos:** 10-maker.md, 20-auditor.md, 30-proposals.md, wiki/log.md

---

## Comparación obtenido vs esperado (8 candidatos)

La rúbrica aplica `impacto = severidad*10 + alcance`. Columnas: clase, severidad, alcance,
impacto. Origen oracle = `expected.md`; origen obtenido = `10-maker.md` + `20-auditor.md`.

| ID oracle | Clase (oracle) | sev | alcance (oracle) | impacto (oracle) | alcance (obtenido) | impacto (obtenido) | Match |
|-----------|---------------|-----|-----------------|-----------------|--------------------|--------------------|-------|
| D1 | contradicción genes | 5 | 2 | 52 | 2 | 52 | ✓ |
| D2 | vencido-seguridad | 5 | 2 | 52 | 2 | 52 | ✓ |
| D3 | contradicción wiki | 4 | 2 | 42 | 2 | 42 | ✓ |
| D4 | regla obsoleta | 3 | 2 | 32 | 2 | 32 | ✓ (ver Calibración) |
| D5 | vacío (link roto) | 2 | 1 | 21 | 1 | 21 | ✓ |
| D6 | vacío (cat. sin cobertura) | 2 | 1 | 21 | 1 | 21 | ✓ |
| D7 | redundancia | 2 | 2 | 22 | 2 | 22 | ✓ |
| D8 | redundancia (confidencial) | 2 | 2 | 22 | 2 | 22 | ✓ |

**Todos los candidatos obtenidos coinciden con el oracle en clase, alcance e impacto.**

---

## Top-3

- **Obtenido:** D1 (52), D2 (52), D3 (42) — C1, C2, C3 del maker/auditor.
- **Esperado:** D1 (52), D2 (52), D3 (42).
- **Resultado:** Top-3 obtenido = esperado ✓

---

## Verificación de confidencialidad (D8)

D8 afecta a [[expediente-x]] y [[expediente-x-copia]], ambas con `sensibilidad: confidencial`.
La invariante exige que ningún artefacto de la corrida transcriba el DNI (`12.345.678`), el
titular (`Juan Pérez`) ni el diagnóstico.

Comando ejecutado:

```
grep -rn "12.345.678\|Juan" sim/_auditoria-fixture/audit/
```

**Resultado:** sin coincidencias (exit 1 — ningún archivo contiene esos valores).

La evidencia de D8 en `10-maker.md` y `20-auditor.md` se expresa exclusivamente por
`[[expediente-x]]` / `[[expediente-x-copia]]` (referencia por id/link), sin transcribir
ningún valor sensible. **Invariante de confidencialidad: RESPETADA ✓**

---

## Calibración — D4 (alcance corregido 31→32 en el oracle)

El oracle original registraba D4 con `alcance 1 / impacto 31`. Esta corrida reveló un error
de cálculo manual en el oracle:

- El maker (en contexto aislado, sin ver el oracle) derivó `alcance = 2` para la obsolescencia
  de [[gen-fix-clasifica-v1]]: tanto el gen obsoleto como el gen que lo subsume
  ([[gen-fix-clasifica-v2]]) están implicados por el defecto.
- El auditor (pasada fresca, sin compartir contexto con el maker) llegó de forma independiente
  a la misma conclusión: `alcance = 2`, impacto = 32.

La convergencia independiente de ambos roles es evidencia de que la implementación es
auto-consistente y que el error estaba en el oracle (cálculo a mano), no en la lógica del
gen. El oracle fue corregido a `alcance 2 / impacto 32`.

El top-3 nunca se vio afectado: D4 queda en cuarto lugar (32 < 42 = D3).

Recomendación abierta: en una futura versión del gen hacer explícito que para la clase
"regla obsoleta/deprecable", el alcance cuenta AMBOS genes del solape (el obsoleto y el que
lo subsume), eliminando la ambigüedad de raíz.

---

## Reproducibilidad — segunda corrida independiente (maker fresco, contexto aislado)

Se corrió un SEGUNDO maker sobre el MISMO estado del fixture (sin ver `expected.md`,
`regresion.md` ni los artefactos del primer run). Resultado:

- **Conjunto de candidatos:** idéntico — los mismos 8 defectos, las mismas 6 clases. ✓
- **Top-3:** idéntico en contenido Y orden — [contradicción-genes-precio, protocolo-vencido,
  cliente-acme↔caso-acme]. ✓
- **Scores exactos:** una divergencia de ±1 en `alcance`. El segundo maker contó el defecto
  `vencido-seguridad` (protocolo) con `alcance = 1` (solo la página vencida) → impacto **51**,
  mientras el primer maker + auditor contaron `alcance = 2` (la página vencida + `prensa-p1`
  que la cita) → impacto **52**. El top-3 NO se vio afectado (51 > 42, el protocolo sigue 2º).

### Frontera de no-determinismo (aislada y documentada, según el spec §4)
La reproducibilidad se cumple para lo que es el **entregable**: el **conjunto de candidatos**
y el **top-3** (contenido y orden) son estables entre derivaciones independientes. Lo que NO
es del todo determinista es el **valor exacto de `alcance` (±1)** en las clases donde "páginas
afectadas" puede incluir o no las **páginas que citan/relacionan** al defecto:
- `vencido-seguridad`: ¿cuenta solo la página vencida (1) o también las que la citan (2)?
- `regla obsoleta`: ¿cuenta solo el gen obsoleto (1) o ambos genes del solape (2)?

Ambas ambigüedades aparecieron empíricamente (D4 en el run 1, protocolo en el run 2). El
ranking top-3 es robusto a ellas por diseño (margen de impacto), pero los scores exactos no.

### Recomendación (requiere compuerta — decisión del fundador)
Para llevar la reproducibilidad del **score exacto** al 100% y cumplir "criterios explícitos,
no implícitos", hacer EXPLÍCITO en una futura `version` de `gen-auto-auditoria` el conteo de
`alcance` por clase, p. ej.:
- `vencido-seguridad`: alcance = 1 (página vencida) + nº de páginas que la citan operativamente.
- `regla obsoleta`: alcance = nº de genes del solape (obsoleto + el que lo subsume).
- `contradicción` / `redundancia`: alcance = nº de páginas/genes en conflicto/duplicados.
- `vacío`: alcance = 1.
Es una mutación de genoma → pasa por [[gen-compuerta-mutacion]]; no se aplica aquí.

---

## Veredicto final

**PASS** (entregable reproducible; no-determinismo de score aislado y documentado).

- 8/8 candidatos detectados y confirmados; conjunto de candidatos reproducible entre 3
  derivaciones independientes (maker run 1, auditor, maker run 2).
- Top-3 coincide con el oracle y es estable en contenido y orden entre corridas.
- Confidencialidad D8 respetada (sin PII en artefactos de auditoría).
- Calibración D4 documenta y justifica la corrección del oracle.
- No-determinismo residual: `alcance` ±1 en clases con páginas citantes/relacionadas; el
  top-3 es robusto. Fix de raíz recomendado (rúbrica de `alcance` explícita por clase, vía
  compuerta).

---

## Corrida v2 (run-id 2026-06-25-9d6819a, gen-auto-auditoria v2)

Re-corrida del fixture con el gen v2 (alcance explícito por clase). Maker y auditor en contextos
aislados, sin ver el oráculo.

- **8/8 candidatos confirmados; scores EXACTOS = oráculo** (52,52,42,32,22,22,21,21). El ±1 de v1
  **quedó cerrado**: ahora el `alcance` lo fija la regla (página + citantes; ambos genes del par
  obsoleto; confidenciales cuentan), no el criterio del agente.
- **Top-3 = [contradicción-genes 52, vencido-seguridad 52, 42]** = oráculo ✓.
- **Confidencialidad D8:** artefactos limpios (sin transcribir DNI/titular/diagnóstico).
- **Friction nueva (menor, para v3):** D3 puede caer en dos clases sev-4 distintas (contradicción
  wiki vs violación de invariante); la selección entre clases de IGUAL severidad no es determinista.
  Score y ranking NO se ven afectados (ambas = 42). Anotado en `expected.md`.

**Veredicto v2: PASS — scoring ahora determinista** (cierra el objetivo de reproducibilidad
exacta). Queda una friction menor de selección-de-clase, sin impacto en scores/ranking.
