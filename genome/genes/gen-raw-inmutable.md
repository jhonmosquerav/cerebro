---
id: gen-raw-inmutable
trigger: cualquier acceso a raw/
status: active
version: 2
---

`raw/` es solo-lectura. Nunca edites, renombres ni borres una fuente en `raw/`: es la
verdad inmutable del sistema. Todo conocimiento derivado vive en `wiki/` y referencia su
fuente con `sources: [[raw/...]]`. Si una fuente está desactualizada, no la toques: crea
una fuente nueva y marca la relación `reemplaza` en la página de wiki correspondiente.

**Excepción única y auditada — purga por incidente.** Si una fuente de `raw/` contiene un
secreto, credencial o PII vertidos por error, purgarla (del árbol y de la historia de git)
NO viola este gen solo si se cumplen TODAS estas condiciones: (1) incidente documentado en
`log.md` (id, fecha, qué se vertió, alcance); (2) aprobación humana explícita ANTES de
ejecutar la purga; (3) línea en `genome/events.jsonl` (`type: incident_purge`, con
`incident_ref` al id del incidente) — la purga se registra, jamás se silencia; (4) re-AUDIT
posterior sobre el estado purgado. La purga es la mínima necesaria (solo la fuente o cadena
afectada) y las páginas de `wiki/` que la referencien se sanean en el mismo incidente.
Procedimiento técnico: `ops/runbook-git-seguro.md` §3. Fuera de este caso la regla queda
intacta: `raw/` jamás se toca.
