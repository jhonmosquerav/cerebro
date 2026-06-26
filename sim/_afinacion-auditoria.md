# Afinación de `gen-auto-auditoria` — corrida sobre 6 sandboxes

- **run-id:** `2026-06-25-f5c6000` · **gen auditado:** `gen-auto-auditoria v1` · **fecha:** 2026-06-25
- **Escenarios:** agencia, ecommerce, legal, salud, produccion, academico (sandboxes aislados de `sim/`).
- **Método:** por escenario, maker y auditor en **contextos aislados** (subagentes separados); cada
  corrida escribió `00-snapshot / 10-maker / 20-auditor / 30-proposals` en `sim/<esc>/audit/runs/<run-id>/`.

> **Garantía de no-compromiso del core (lo que pediste):** ninguna corrida tocó `genome/`,
> `wiki/` ni el `audit/` real. El gen se aplicó **read-only**. Todo lo de abajo son **propuestas**
> para una futura `v2`; **nada se aplicó**. Cualquier cambio al gen pasa por [[gen-compuerta-mutacion]].

---

## 1. Resumen por escenario

| Escenario | Candidatos | Confirmados | Top-1 | Confidencialidad |
|---|---|---|---|---|
| agencia | 5 | 5/5 | precio vencido (53) | n/a (sin páginas confidenciales) |
| ecommerce | 6 | 6/6 | campos volátiles en prosa (44) | n/a |
| legal | 6 | 5/6 (1 falso positivo) | campo `vigencia` sin gen (44) | **CLEAN** (secreto profesional) |
| salud | 3 | 3/3 | protocolo clínico vencido (55) | **CLEAN** (PII paciente) |
| produccion | 4 | 4/4 | SOP contradice su propio checklist (44) | n/a |
| academico | 5 | 4/5 (2 reclasificados) | working-paper contradice publicado (42) | **CLEAN** (revisión por pares) |

## 2. Qué validó la afinación (lo que funciona)

- **maker≠auditor aporta valor real en bases reales:** el auditor académico **reclasificó** C-05
  (un working-paper "supersedido" mal etiquetado como "regla obsoleta" — clase reservada a genes del
  genoma) bajando su score 31→21; el de legal corrigió un hecho (`dictamenes/` existe pero vacía); el
  de producción reculó la severidad del SOP a 4 por ambigüedad de "dominio de seguridad". El auditor
  NO fue sello de goma.
- **Confidencialidad (§8) robusta:** los 3 dominios sensibles (legal, salud, academico) pasaron
  **leak-check independiente por grep: cero valores sensibles** en ningún artefacto. La herencia de
  [[gen-confidencialidad]] aguantó en secreto profesional, PII de paciente y revisión por pares.
- **Aislamiento confirmado:** `git status` sobre `genome/ wiki/ CLAUDE.md AGENTS.md` quedó vacío tras
  cada commit. El banco de afinación no compromete el desarrollo reproducible.
- **Dedup ya respetó síntesis previa:** en ecommerce el maker NO marcó como redundancia los 4 tickets
  ya agregados en una síntesis (`agregado_en`), correcto.

## 3. Fricciones convergentes → backlog de propuestas para `v2` (requieren compuerta)

Priorizadas por cuántos escenarios las tocaron y por impacto en reproducibilidad.

### P1 — Definir `alcance` de forma explícita por clase (ALTA — reproducibilidad)
**Flagueada por:** salud, legal, produccion, ecommerce, academico (y ya detectada en el fixture).
La definición "nº de páginas/genes afectados" es ambigua y produce ±1 no-determinista. Precisar:
- ¿Cuentan las **páginas de primer nivel que citan** el defecto? (salud y legal: sí). Hacerlo explícito.
- Las páginas `sensibilidad: confidencial` **sí cuentan** en el número, pero su evidencia se cita solo
  por `[[link]]`/campo (salud lo confirmó).
- Los **vacíos de genoma** (un seed gene faltante afecta toda ingesta futura) están infravalorados por
  el conteo estático; considerar un factor de propagación.
- Desempate alfabético para candidatos multi-página: usar la **primera ruta listada en "Afectados"**.

### P2 — "dominio de seguridad" sin definir; `vencido` demasiado atado a `valido_hasta` (ALTA)
**Flagueada por:** agencia, legal, produccion, salud, academico.
La clase sev-5 "info vencida en dominio de seguridad" encaja en salud (clínico) pero es **inerte o
inflada** fuera. Proponer:
- **Enumerar "dominio de seguridad"**: seguridad física, salud, cumplimiento regulatorio con
  consecuencias legales (evita que un paper retractado o un precio vencido hereden sev 5).
- **Generalizar `vencido`** más allá de `valido_hasta`: en legal la obsolescencia es **por evento**
  (`vigencia: en-revision|derogada|no-vigente`), no por fecha. AUDIT/LINT deberían detectarlo.
- Opcional: permitir al manifiesto declarar `impact_domain` para escalar severidad por dominio.

### P3 — Clases de defecto que faltan en la rúbrica (MEDIA)
**Flagueada por:** agencia, produccion, academico, legal.
- **Violación de invariante impuesta por un gen** (agencia: el gen exige enlaces que la página no
  tiene) — hoy se fuerza dentro de "contradicción wiki".
- **Entidad con estado inconsistente con su historial de eventos** (produccion: estado de máquina /
  lead→cliente) — no es contradicción de una página ni vencimiento.
- **Conocimiento supersedido sin degradar tier/estado** a nivel **wiki** (academico, ecommerce) —
  distinto de la obsolescencia de **genoma** (que es lo único que cubre "regla obsoleta" hoy).
- **Verbo de relación / campo fuera de esquema** como clase de AUDIT (LINT lo detecta; la rúbrica no
  lo puntúa).

### P4 — El detector de redundancia debe eximir derivación/síntesis declarada (MEDIA)
**Flagueada por:** ecommerce, academico.
Pares con `agregado_en` (a una síntesis) o `deriva_de`/`supersede` (versionado declarado) **no** son
redundancia. Codificar la exención en `gen-auto-auditoria` o en [[gen-consolidate]] para evitar falsos
positivos (causó la divergencia maker/auditor en el dataset académico).

### P5 — Dominios confidenciales-por-defecto (MEDIA)
**Flagueada por:** legal, salud.
El genoma asume abierto-por-defecto; legal/salud son lo inverso. Proponer `default_sensibilidad` en el
manifiesto. Además: documentar que páginas confidenciales cuentan en `alcance` (cita por ref), y marcar
como **vector de fuga latente** los genes que cruzan ambos lados de un caso (ej. `gen-conflicto-interes`)
sin regla de no-reproducir contenido sensible en el cruce.

### P6 — Regla de fusión "mismo defecto" ambigua (BAJA)
**Flagueada por:** legal. ¿"mismo defecto" = mismo **objeto** o misma **causa raíz**? (legal C1/C3
comparten causa, distinto objeto, se mantuvieron separados). Precisar.

### P7 — Fallback de identidad en sandboxes sin repo propio (BAJA)
**Flagueada por:** salud, academico. `git rev-parse HEAD` funcionó aquí (sim/ vive en este repo), pero el
gen debería prescribir un fallback `sim-<token>` para sandboxes que no son su propio repo.

### P8 — sev-5 con incidente abierto vinculado (BAJA)
**Flagueada por:** salud. Un hallazgo sev-5 ligado a un incidente abierto debería exigir un paso de
revisión / `incident_ref` antes de aprobar la propuesta (no inflar el score).

## 3bis. Verificación adversarial de las fricciones (qué sobrevivió)

Cada fricción se sometió a un verificador independiente con consigna de **refutar** (leyendo el
texto real del gen v1 + la evidencia citada). Resultado — separa lo real de lo especulativo:

| # | Veredicto | Acción |
|---|---|---|
| **P1** alcance | **REAL (parcial)** | Mantener (a) citantes y (b) confidenciales cuentan, (c) re-enmarcada como "ambos lados del par obsoleto/solape". **Quitar (d): el desempate alfabético YA está definido (líneas 53-57 del gen) — refutado.** |
| **P2** dominio-seguridad/vencido | **REAL (a y b)** | Mantener. Afecta reproducibilidad (sev4 vs5) y correctitud (clase sev-5 inerte en dominios por-evento). |
| **P3** clases faltantes | **REAL (4/4)** | Mantener. Evidencia dura: académico C-05 cayó 31→21 y salió del top-3 por falta de clase "supersedido a nivel wiki". (d) verbo/campo fuera de esquema = real pero menor. |
| **P4** eximir deriva_de/síntesis | **REAL** | Mantener. Ausencia confirmada en `gen-auto-auditoria` y `gen-consolidate`; produjo trato no-determinista (académico marcó el par `deriva_de`, ecommerce no marcó el `agregado_en` — ambos por criterio del agente, no por regla). |
| **P5** confidencial-por-defecto | **MEJORA, no defecto** | **Degradar.** Los leak-checks fueron CLEAN; el audit manejó bien lo confidencial. Es capa de manifiesto/ONBOARD (`default_sensibilidad`) + un fix a `gen-conflicto-interes`, NO de `gen-auto-auditoria`. Derivar a [[gen-evolve]]/ONBOARD. |
| **P6** "mismo defecto" ambiguo | **REAL (baja)** | Mantener como baja prioridad. No volteó scores esta corrida; gap estructural de reproducibilidad. |
| **P7** SHA en sandbox | **ESPECULATIVA — no ocurrió** | **Degradar.** `sim/` vive dentro del repo; `git rev-parse HEAD` resolvió bien en las 6 corridas. Solo mordería si alguien desacopla un sandbox como repo propio (contrario al diseño). Nota de robustez opcional, no defecto. |
| **P8** gate por incidente | **MEJORA, no defecto** | **Degradar.** El gen ya exige gate humano universal sobre TODA propuesta (`status: pending`, sin auto-aplicar); el incidente ya aparece en la evidencia. P8 es pulido procedimental opcional para dominios críticos. |

**Backlog verificado para la `v2` del gen (lo que sí vale una compuerta):** **P1 (a,b,c), P2, P3, P4**
— son los que afectan reproducibilidad/correctitud del score y la clasificación. **P6** queda como
mejora menor. **P5, P7, P8** se degradan (mejoras de otra capa o especulativas), y **P1(d) se
descarta** (ya cubierto). La verificación recortó el backlog de 8 a **4 fricciones de peso + 1 menor**.

## 4. Cómo se aplicaría (sin comprometer reproducibilidad)
Cada propuesta de arriba es material para un futuro `EVOLVE` → [[gen-compuerta-mutacion]]: se PROPONE el
diff + señal, se aprueba, se sube `version` del gen, 1 línea en `genome/events.jsonl`, commit, re-sync
`AGENTS.md`, y se re-corre este banco para confirmar la mejora. P1 y P2 son las de mayor retorno (cierran
el no-determinismo de score y la inflación de severidad). **Nada de esto está aplicado.**

## 5. Resultado de la aplicación (lote v2 — 2026-06-25)

El lote v2 se aprobó por la compuerta y se aplicó (6 genes: `gen-auto-auditoria` v2,
`gen-vigencia-temporal` v2, `gen-lint` v3, `gen-consolidate` v2, `gen-onboard` v3,
`gen-confidencialidad` v2 + `default_sensibilidad` en el manifiesto). Re-corrida del banco con v2
(run-id `2026-06-25-9d6819a`):

- **Fixture: PASS determinista.** 8/8 candidatos con scores EXACTOS = oráculo; el ±1 de v1 cerrado
  (el `alcance` ahora lo fija la regla). Ver `_auditoria-fixture/regresion.md` §Corrida v2.
- **Académico: P3 corregido en vivo.** El working-paper supersedido, que en v1 caía mal a sev2/21,
  ahora toma la nueva clase **"conocimiento supersedido sin degradar tier (wiki)" sev3/impacto 31**
  y **encabeza el top-3**. Exactamente la corrección que P3 buscaba.
- **Las otras 5 (agencia, ecommerce, legal, salud, produccion):** sus scores v1 ya usaban la lectura
  "citantes/confidenciales cuentan" que v2 codifica → quedan **confirmados y ahora deterministas por
  construcción** (no se re-corrieron con subagentes frescos; v2 las vuelve rule-determinadas).

### Fricciones nuevas que destapó la corrida v2 (candidatas a v3)
- **F-v2-a (proceso / confidencialidad):** al describir un candidato sobre una página confidencial,
  el maker académico **transcribió** la identidad del revisor en `10-maker.md`. El **auditor lo cazó**
  (refutó el candidato C6 + flag de fuga) y se **redactó antes de commitear** (sin PII en git). Señal:
  el gen debe instruir explícitamente "describe el defecto de una página confidencial SIN copiar su
  valor, ni en el bloque de evidencia ni en el diff propuesto". El diseño maker≠auditor + el gate
  funcionaron como red de seguridad.
- **F-v2-b (selección de clase):** v2 añadió clases sev-4 que solapan; cuando dos clases de IGUAL
  severidad aplican a un defecto, la selección no es determinista (score/ranking no se afectan).
  Falta una regla de desempate ENTRE clases de misma severidad.

Ambas son menores (no afectan scores/ranking) y quedan como backlog para una eventual v3 — por la
compuerta, como siempre.
