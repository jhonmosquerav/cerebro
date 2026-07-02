---
eval_id: 2026-07-01-810f24e
tipo: propuesta-evolve
tarea: A-11
audit_ref: 2026-06-30-7c840d0 (hallazgo C14)
genes_afectados: [gen-query, gen-confidencialidad]
version_actual: 2 (ambos)
version_propuesta: 3 (ambos)
status: approved
fecha: 2026-07-02
---

# Propuesta EVOLVE — cerrar la fuga indirecta por metadatos en páginas `confidencial` (C14)

> **Status: `pending` — GATE HUMANO.** Nada de esta propuesta está aplicado: ambos genes
> siguen en v2. La aplicación exige aprobación explícita + línea en `genome/events.jsonl`
> por gen + commit + re-sincronía de `AGENTS.md` ([[gen-compuerta-mutacion]]); después,
> [[gen-migracion-genoma]] re-valida manifiesto y páginas.

## Qué se propone (una línea)

Extender [[gen-query]] (v2 → v3) y [[gen-confidencialidad]] (v2 → v3) para que la
"referencia indirecta" a una página `confidencial` tampoco exponga sus **metadatos
reidentificadores** —título, nombre de archivo, tags, relaciones (`relations`)— y el ID
seudonimizado cubra también el enlace o mención.

## Motivación con evidencia

1. **Hallazgo confirmado por el auditor independiente** (corrida
   `audit/runs/2026-06-30-7c840d0/`, C14, verdict CONFIRMED): ambos genes prohíben citar
   el *contenido* textual de páginas `confidencial` ("responde con referencia indirecta o
   ID seudonimizado") pero **no prohíben exponer título/nombre-de-archivo/tags/aristas**,
   que pueden reidentificar (`20-auditor.md:202-208`).
2. **El vector es real con la convención de nombres actual:** una página
   `paciente-juan-perez.md` con relación `tratado_con [[VIH]]` reidentifica a la persona
   aunque QUERY jamás cite su contenido (`10-maker.md:115-120`). Nada gobierna hoy el
   nombre de archivo de una página confidencial.
3. **La lente de grafo YA cierra este mismo vector; QUERY no.** El staging de graphify es
   allowlist fail-closed: una página `confidencial` no entra a la copia — ni su título ni
   sus relaciones (`dashboards/graph/00-leeme.md`, principio 1). La misma garantía no
   existe en la operación de consulta, que es la vía de exposición más frecuente.
4. **El backlog lo ordena:** A-11 incluye "cerrar … C14 (fuga por metadatos)"
   (`audit/evaluations/2026-07-01-810f24e/60-backlog.md`). Al ser mutación de genoma, la
   vía es esta propuesta bajo compuerta — no una edición directa.

## Diff propuesto — [[gen-query]] (v2 → v3)

```diff
 ---
 id: gen-query
 trigger: operación QUERY sobre un tema
 status: active
-version: 2
+version: 3
 ---
 
 QUERY responde navegando el grafo, no leyendo todo. Empieza en `index.md`, sigue las
 relaciones `[[...]]` relevantes y abre solo las páginas necesarias (presupuesto de contexto).
 Cita las páginas-fuente consultadas y su `confidence`, **excepto las `sensibilidad: confidencial`**
 ([[gen-confidencialidad]]): de esas no revela contenido sensible ni las cita textualmente —
-responde con referencia indirecta o ID seudonimizado. Advierte **siempre** lo vencido por
+responde con referencia indirecta o ID seudonimizado. La referencia indirecta tampoco
+expone metadatos reidentificadores: ni el título, ni el nombre de archivo, ni los tags,
+ni sus relaciones; el ID seudonimizado aplica también al enlace o mención con que se
+responde. Advierte **siempre** lo vencido por
 `valido_hasta` ([[gen-vigencia-temporal]]), lo contradictorio (`relations.contradice`) y la baja
 `confidence`, en vez de afirmar con falsa seguridad. Si no hay información, dilo: no inventes.
```

## Diff propuesto — [[gen-confidencialidad]] (v2 → v3)

```diff
 ---
 id: gen-confidencialidad
 trigger: ingesta o consulta de información sensible (PII, secreto profesional, datos de cliente/paciente)
 status: active
-version: 2
+version: 3
 ---
 
 Eje de sensibilidad sobre toda página: `sensibilidad: publico | interno | confidencial`
 (default tomado de `default_sensibilidad` del manifiesto si lo declara —dominios sensibles como
 legal/salud suelen fijar `confidencial`—; si no existe, `interno`). Las páginas `confidencial`: (1) no se anclan en `index.md`; (2) no se
 promueven de tier ni se fusionan por CONSOLIDATE; (3) QUERY no las cita textualmente ni
 revela su contenido sensible sin autorización explícita — responde con referencia indirecta
-o ID seudonimizado. Además, INGEST **se detiene y pregunta** si detecta PII real sin
+o ID seudonimizado, sin exponer tampoco sus metadatos reidentificadores (título, nombre de
+archivo, tags, relaciones): el seudónimo cubre también el enlace o mención. Regla práctica
+de nombrado: una página `confidencial` no lleva el nombre de la persona en el título ni en
+el nombre de archivo — usa el ID seudonimizado. Además, INGEST **se detiene y pregunta** si detecta PII real sin
 anonimizar (nombre + identificador de una persona física). Regla práctica: el conocimiento
 clínico/legal/comercial estable es `publico` o `interno`; los datos de la persona concreta
 son `confidencial`. Complementa [[gen-frontmatter-obligatorio]] y la privacidad de toda empresa.
```

Racional del reparto: [[gen-confidencialidad]] es la **fuente de verdad del eje** (mismo
criterio que la P1 aplicada de la corrida `2026-06-30-7c840d0`), así que la regla completa
—incluido el nombrado— vive ahí; [[gen-query]] repite la cláusula operativa porque es el
gen que se dispara en cada consulta y hoy ya la enuncia (mantener ambos coherentes evita
reabrir la clase "contradicción entre genes activos").

## Líneas draft para `genome/events.jsonl`

Se añaden **solo al aplicar**, con la fecha real de aprobación (mismo esquema de claves
que las líneas existentes: `ts`, `type`, `target`, `signal`, `diff`, `approved_by`,
`status`; una línea por gen):

```json
{"ts":"AAAA-MM-DD","type":"gene_edited","target":"gen-confidencialidad","signal":"AUDIT 2026-06-30-7c840d0 C14 / backlog A-11: la clausula (3) prohibia citar contenido de paginas confidenciales pero no exponer titulo, nombre de archivo, tags ni aristas, que reidentifican (graphify ya cerraba ese vector; QUERY no)","diff":"v2 -> v3 (la referencia indirecta no expone metadatos reidentificadores: titulo, nombre de archivo, tags, relaciones; el seudonimo cubre tambien el enlace o mencion; + regla de nombrado seudonimo para paginas confidencial)","approved_by":"user","status":"applied"}
```

```json
{"ts":"AAAA-MM-DD","type":"gene_edited","target":"gen-query","signal":"AUDIT 2026-06-30-7c840d0 C14 / backlog A-11: la referencia indirecta de QUERY a paginas confidenciales podia exponer titulo, nombre de archivo, tags y relaciones que reidentifican","diff":"v2 -> v3 (la referencia indirecta tampoco expone titulo/nombre de archivo/tags/relaciones; el ID seudonimizado aplica tambien al enlace o mencion)","approved_by":"user","status":"applied"}
```

## Criterios de aceptación

1. Ambos genes publicados en v3 con el texto de los diffs, vía compuerta: **2 líneas**
   `gene_edited` en `events.jsonl` + commit.
2. `AGENTS.md` re-sincronizado byte a byte con `CLAUDE.md` tras la aplicación (el resumen
   de una línea de [[gen-confidencialidad]] en el índice de genes dice "no se cita
   textual"; ampliarlo a "ni sus metadatos" es decisión del aplicador en el gate — editar
   `CLAUDE.md`/`AGENTS.md` queda fuera de esta propuesta).
3. En la corrida `2026-06-30-7c840d0`, C14 pasa de "anotada, sin aplicar" a cerrada
   (anotación del aplicador en `30-proposals.md` o en `log.md`, según la casa decida).
4. [[gen-migracion-genoma]] corrido tras la mutación: pre-ONBOARD no hay páginas que
   re-validar; deja constancia de ello.
5. Prueba de humo posterior: una QUERY simulada sobre una página `confidencial` de prueba
   responde con seudónimo sin exponer título/archivo/tags/relaciones.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Respuestas de QUERY menos útiles (todo seudonimizado) | la regla aplica SOLO a `sensibilidad: confidencial`; `publico`/`interno` se citan igual que hoy |
| El seudónimo rompe la navegabilidad del grafo para quien SÍ está autorizado | la excepción de autorización explícita ya existe en ambos genes y no cambia |
| Páginas confidenciales ya nombradas con PII quedan fuera de la regla de nombrado | la regla es para páginas nuevas; renombrar las existentes es un paso de LINT/CONSOLIDATE bajo su propio flujo (y pre-ONBOARD no existe ninguna) |
| Dos genes enuncian la misma cláusula y podrían divergir en futuras ediciones | mismo patrón ya aceptado en P1: la fuente de verdad es [[gen-confidencialidad]]; [[gen-lint]] y AUDIT detectan divergencias entre genes activos |

## Relación con otros artefactos

- Vector equivalente ya cerrado en la lente de grafo: `dashboards/graph/00-leeme.md`
  (staging allowlist fail-closed — lo `confidencial` no entra, ni títulos ni relaciones).
- [[gen-frontmatter-obligatorio]] — el eje `sensibilidad` que activa la cláusula.
- Corrida de origen del hallazgo: `audit/runs/2026-06-30-7c840d0/` (C14 en `10-maker.md`,
  `20-auditor.md` y registro en `30-proposals.md`).
