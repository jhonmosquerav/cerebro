---
eval_id: 2026-07-01-810f24e
tipo: propuesta-evolve
tarea: A-08
target: gen-raw-inmutable
version_actual: 1
version_propuesta: 2
status: approved
fecha: 2026-07-02
---

# Propuesta EVOLVE — excepción única de purga por incidente en [[gen-raw-inmutable]]

> **Status: `pending` — GATE HUMANO.** Nada de esta propuesta está aplicado: el gen sigue
> en v1. La aplicación exige aprobación explícita + línea en `genome/events.jsonl` +
> commit + re-sincronía de `AGENTS.md` ([[gen-compuerta-mutacion]]); después,
> [[gen-migracion-genoma]] re-valida manifiesto y páginas.

## Qué se propone (una línea)

Añadir a [[gen-raw-inmutable]] (v1 → v2) una **excepción única y auditada**: purgar de
`raw/` —y de la historia de git— una fuente que contenga un secreto, credencial o PII
vertidos por error, solo bajo cuatro condiciones conjuntivas y dejando doble rastro.

## Motivación con evidencia

1. **La regla vigente no tiene salida para incidentes.** `gen-raw-inmutable` v1: *"Nunca
   edites, renombres ni borres una fuente en `raw/`"* — sin excepción alguna
   (`genome/genes/gen-raw-inmutable.md:8-11`).
2. **El panel de seguridad lo marcó como colisión normativa** (eval `2026-07-01-810f24e`):
   debilidad sev-3 — *"si alguien vierte un secreto o credencial en raw/,
   gen-raw-inmutable prohíbe explícitamente borrarlo (…) la regla de integridad colisiona
   con la contención de una fuga"*; y riesgo dedicado (prob. media / imp. medio):
   *"Secreto o credencial vertido en raw/ queda inmutable por regla y versionado para
   siempre"* (`audit/evaluations/2026-07-01-810f24e/10-panel.md`, lente seguridad).
3. **La permanencia en historia está demostrada en este mismo repo:** el fixture con PII
   simulada, borrado en la "limpieza a template público", sigue recuperable con
   `git show 246f8df~1:sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x.md`
   (`30-valoracion.md:66`). Borrar del árbol no borra nada: la única vía real es la purga
   de historia — hoy prohibida si el material vive en `raw/`.
4. **El backlog lo ordena así:** A-08 pide el procedimiento de purga *"como excepción
   documentada y gateada a [[gen-raw-inmutable]] para incidentes"* (`60-backlog.md:58-61`).
5. **La excepción protege la inmutabilidad, no la debilita:** sin salida sancionada, un
   incidente real fuerza a elegir entre violar el gen a escondidas o dejar el secreto
   vivo para siempre. La recomendación P1 del panel lo formuló igual: la excepción
   registrada *"no viola la inmutabilidad — la protege de ser una trampa"*.

## Diff propuesto (v1 → v2)

```diff
 ---
 id: gen-raw-inmutable
 trigger: cualquier acceso a raw/
 status: active
-version: 1
+version: 2
 ---
 
 `raw/` es solo-lectura. Nunca edites, renombres ni borres una fuente en `raw/`: es la
 verdad inmutable del sistema. Todo conocimiento derivado vive en `wiki/` y referencia su
 fuente con `sources: [[raw/...]]`. Si una fuente está desactualizada, no la toques: crea
 una fuente nueva y marca la relación `reemplaza` en la página de wiki correspondiente.
+
+**Excepción única y auditada — purga por incidente.** Si una fuente de `raw/` contiene un
+secreto, credencial o PII vertidos por error, purgarla (del árbol y de la historia de git)
+NO viola este gen solo si se cumplen TODAS estas condiciones: (1) incidente documentado en
+`log.md` (id, fecha, qué se vertió, alcance); (2) aprobación humana explícita ANTES de
+ejecutar la purga; (3) línea en `genome/events.jsonl` (`type: incident_purge`, con
+`incident_ref` al id del incidente) — la purga se registra, jamás se silencia; (4) re-AUDIT
+posterior sobre el estado purgado. La purga es la mínima necesaria (solo la fuente o cadena
+afectada) y las páginas de `wiki/` que la referencien se sanean en el mismo incidente.
+Procedimiento técnico: `ops/runbook-git-seguro.md` §3. Fuera de este caso la regla queda
+intacta: `raw/` jamás se toca.
```

## Por qué estas cuatro condiciones (conjuntivas)

| # | Condición | Qué previene |
|---|---|---|
| 1 | Incidente documentado en `log.md` | purgas "silenciosas" sin contexto reconstruible |
| 2 | Aprobación humana explícita **previa** | que el agente decida solo qué merece borrarse (misma compuerta que toda mutación) |
| 3 | Línea en `genome/events.jsonl` con `incident_ref` | que la excepción escape al ledger append-only que gobierna al propio gen |
| 4 | Re-AUDIT posterior | que el estado post-purga (enlaces, wiki huérfana, sincronía) quede sin revisar |

## Línea draft para `genome/events.jsonl`

Se añade **solo al aplicar** la mutación, con la fecha real de aprobación (mismo esquema
de claves que las 28 líneas existentes: `ts`, `type`, `target`, `signal`, `diff`,
`approved_by`, `status`):

```json
{"ts":"AAAA-MM-DD","type":"gene_edited","target":"gen-raw-inmutable","signal":"eval 2026-07-01-810f24e / backlog A-08: un secreto o PII vertido en raw/ quedaba imborrable por regla (fixture recuperable via git show demostrado en el propio repo); la inmutabilidad colisionaba con la contencion de incidentes","diff":"v1 -> v2 (+ excepcion unica y auditada de purga por incidente: documentado en log.md + aprobacion explicita previa + linea incident_purge en events.jsonl + re-AUDIT posterior; purga minima; procedimiento en ops/runbook-git-seguro.md)","approved_by":"user","status":"applied"}
```

Plantilla para cada purga futura que ejerza la excepción (mismas claves; la exige la
condición 3 del gen v2):

```json
{"ts":"AAAA-MM-DD","type":"incident_purge","target":"raw/<fuente-purgada>","signal":"incidente <id en log.md>: <secreto|credencial|PII> vertido por error; contencion y rotacion ejecutadas antes de purgar","diff":"historia reescrita con git-filter-repo: HEAD <SHA-viejo> -> <SHA-nuevo>; commit-map archivado en ops/purgas/<id>/","approved_by":"user","status":"applied"}
```

**Nota de semántica del ledger:** `log.md` define hoy `events.jsonl` como registro de
"solo mutaciones del genoma". Esta propuesta amplía deliberadamente esa semántica a
"mutaciones + ejercicio de excepciones gateadas", para que la purga quede en el **mismo**
registro append-only que la regla que excepciona (el vocabulario `incident_ref` ya existe
en el genoma: gen-auto-auditoria v2). Si el aprobador prefiere no ampliar el ledger, la
alternativa mínima es registrar la purga solo en `log.md` — desaconsejado aquí: dejaría
la excepción fuera de la traza del genoma.

## Criterios de aceptación

1. `gen-raw-inmutable` v2 publicado con la excepción y las 4 condiciones textuales, vía
   compuerta: línea `gene_edited` en `events.jsonl` + commit.
2. `AGENTS.md` re-sincronizado byte a byte con `CLAUDE.md` tras la aplicación (si el
   índice de genes de `CLAUDE.md` no cambia, la verificación de sincronía se corre igual;
   ajustar el resumen de una línea del índice es decisión del aplicador en el gate —
   editar `CLAUDE.md`/`AGENTS.md` queda fuera de esta propuesta).
3. `ops/runbook-git-seguro.md` §3.4 actualizado de "propuesta pendiente" a "excepción
   vigente (v2)" — edición documental posterior a la aplicación.
4. [[gen-migracion-genoma]] corrido tras la mutación: sin páginas ni manifiesto que
   re-validar en pre-ONBOARD, deja constancia de ello.
5. (Recomendado) simulacro documentado en un clon desechable: purga de un archivo de
   prueba siguiendo §3 del runbook, con `commit-map` archivado — verifica el
   procedimiento sin tocar el repo vivo.
6. La primera purga real cumple las 4 condiciones y su re-AUDIT referencia el
   `incident_ref`.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| La excepción se usa como puerta trasera para "limpiar" fuentes incómodas | 4 condiciones conjuntivas, aprobación humana previa, doble rastro (`log.md` + `events.jsonl`), purga mínima, re-AUDIT |
| Ampliar `events.jsonl` confunde el replay del genoma | tipo dedicado `incident_purge` (el replay de mutaciones filtra por `gene_*`/`capsule_*`); nota de semántica explícita en esta propuesta |
| La purga reescribe SHAs e invalida run-id/eval-id anclados a SHA | consecuencia documentada en `ops/runbook-git-seguro.md` §3.3: carpetas no se renombran, `commit-map` archivado, línea `PURGA` en `log.md` con el mapeo |
| Purgar da falsa sensación de seguridad sin rotar el secreto | el runbook (§4.2) ordena rotar/revocar SIEMPRE; la plantilla de `incident_purge` lo declara ejecutado antes de purgar |
| Backups previos retienen lo purgado | rotación obligatoria al cierre del incidente (`ops/backup/runbook-backup.md`); `--verify-restore` detecta la divergencia de historias |
| Páginas de `wiki/` quedan citando una fuente purgada (`sources: [[raw/...]]` colgante) | saneo en el mismo incidente (texto del gen v2); [[gen-lint]] detecta huérfanos residuales |
| Deriva normativa: la excepción se percibe como permiso general | el texto v2 cierra reafirmando la regla: fuera del caso, `raw/` jamás se toca |

## Relación con otros artefactos

- Procedimiento técnico de purga y checklist pre-push: `ops/runbook-git-seguro.md` (A-08).
- Respaldo previo obligatorio y rotación post-purga: `ops/backup/runbook-backup.md` +
  `ops/backup/backup.sh` (A-09).
- [[gen-confidencialidad]] — el PII-halt de INGEST reduce la probabilidad de llegar a
  necesitar esta excepción; no la elimina (el vertido accidental directo a `raw/` no pasa
  por INGEST).
- [[gen-auto-auditoria]] — ejecuta el re-AUDIT de la condición 4; su vocabulario ya
  incluye `incident_ref`.
