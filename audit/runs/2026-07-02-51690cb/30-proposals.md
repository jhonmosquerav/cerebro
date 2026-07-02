---
run_id: 2026-07-02-51690cb
fecha: 2026-07-02
rol: orquestador
gen_version: gen-auto-auditoria v3
tipo: proposals
---

# 30 — Propuestas (≤3, rankeadas) · GATE HUMANO

Ensambladas por el orquestador a partir de `20-auditor.md`. `N = min(3, confirmadas) = 3`.
El humano aprueba/rechaza **una por una**. Nada se aplica sin tu OK.

- Maker: equipo de 4 especialistas (ver `10-maker.md`; el especialista de reproducibilidad
  reportó cero candidatos con todo su dominio en verde).
- Auditor independiente: 13 confirmadas · 3 ajustadas (C8 sev4→2, C9 y C10 alcance→1) · **0 refutadas**.
- Desempate aplicado: (1) impacto; (2) prioridad de clase por orden de filas; (3) ruta alfabética.
- Patrón de la corrida: los 4 sev-5 son **costuras entre propuestas EVOLVE redactadas en
  paralelo** (tanda 810f24e) — cada gen es coherente por dentro; las enumeraciones cerradas
  de uno no conocen las marcas/flujos del otro.

---

## P1 — Reconciliar los verbos de relación del genoma base con el esquema de `relations`
- id: `AUDIT-2026-07-02-P1` (candidato C1)
- fecha: 2026-07-02
- clase: **contradicción entre genes activos** · sev 5 · alcance 7 · **impacto 57** · status: **applied** (2026-07-02, variante del auditor; 4 commits: gen-frontmatter-obligatorio v6, gen-lint v4, gen-consolidate v5, gen-auto-auditoria v4)
- motivo: El núcleo de `relations` es `{usa, depende_de, contradice, reemplaza}` y LINT (d) valida contra "núcleo ∪ `relation_types` del manifiesto". Pero 5 genes base activos mandan/presuponen verbos fuera de esa unión: `agrega` (gen-sintesis-de-volumen), `corrobora` (gen-confianza-por-fuente), `sucede_a`/`proviene_de` (gen-entidad-con-estado), `deriva_de`/`supersede`/`agregado_en` (exención de gen-consolidate y gen-auto-auditoria). Ejecutar el genoma base out-of-the-box produce relaciones que su propio LINT marca inválidas, y la exención de fusión jamás podría activarse legítimamente.
- evidencia: `gen-frontmatter-obligatorio.md:17-18` (núcleo) · `gen-lint.md:12-13` (chequeo d) · `gen-sintesis-de-volumen.md:10` (`agrega`) · `gen-confianza-por-fuente.md:11` (`corrobora`) · `gen-entidad-con-estado.md:12` (`sucede_a`/`proviene_de`) · `gen-consolidate.md:13-14` + `gen-auto-auditoria.md:25-26` (trío de exención) · `company.example.yaml:39` (no los declara).
- diff (variante recomendada por el auditor — declarar la unión con cláusula de gen, unificando `supersede` con `reemplaza`):
  ```diff
  --- genome/genes/gen-frontmatter-obligatorio.md (v5 -> v6)
  -LINT valida cada relación contra esa **unión** (núcleo ∪ declarados) y marca verbos no declarados.
  +LINT valida cada relación contra esa **unión** (núcleo ∪ verbos declarados por genes activos
  +—`agrega`/`agregado_en` ([[gen-sintesis-de-volumen]], [[gen-consolidate]]), `sucede_a`/`proviene_de`
  +([[gen-entidad-con-estado]]), `corrobora` ([[gen-confianza-por-fuente]]), `deriva_de`
  +([[gen-consolidate]]); `supersede` se unifica con el núcleo `reemplaza`— ∪ `relation_types`
  +del manifiesto) y marca verbos no declarados.
  ```
  + edición espejo del chequeo (d) de [[gen-lint]] (mismo evento o evento hermano) y de la
  mención `supersede` en gen-consolidate/gen-auto-auditoria (`supersede`→`reemplaza`).
- objeción del auditor al diff del maker (variante E3): meter `supersede` al núcleo consagra la duplicación con `reemplaza` y omite `proviene_de` — por eso se recomienda la variante de unión declarada.
- ruta de aplicación: **genoma → [[gen-compuerta-mutacion]]** (eventos + versiones + commit + re-sync `AGENTS.md`); luego [[gen-migracion-genoma]].

## P2 — La cuarentena `riesgo_inyeccion` entra a los criterios de promoción/fusión
- id: `AUDIT-2026-07-02-P2` (candidato C2)
- fecha: 2026-07-02
- clase: **contradicción entre genes activos** · sev 5 · alcance 3 · **impacto 53** · status: **applied** (2026-07-02; gen-ciclo-de-vida v2, gen-consolidate v6)
- motivo: gen-anti-inyeccion ordena que una página en cuarentena no se promueve ni se fusiona; gen-ciclo-de-vida define la promoción como lista cerrada de aplicación directa que omite la cuarentena (aunque sí incorpora el bloqueo de confidencialidad — pretende ser el set completo), y la regla de fusión de gen-consolidate tampoco la excluye. Página en cuarentena que cumpla la lista = dos órdenes incompatibles. Costura A-01 vs A-05.
- evidencia: `gen-anti-inyeccion.md:48-49` · `gen-ciclo-de-vida.md:40-45` · `gen-consolidate.md:9-10,13-14`.
- diff:
  ```diff
  # gen-ciclo-de-vida.md (criterio de promoción; v1 -> v2)
  - sesión") · sin `contradice` abierta · `sensibilidad ≠ confidencial`
  + sesión") · sin `contradice` abierta · sin `riesgo_inyeccion: true` ([[gen-anti-inyeccion]]:
  + la cuarentena bloquea promoción y fusión hasta revisión humana) · `sensibilidad ≠ confidencial`
  # gen-consolidate.md (regla de fusión; v4 -> v5)
  - fusiona duplicados conservando la página con más relaciones —**exención**: pares con relación
  + fusiona duplicados conservando la página con más relaciones —nunca páginas en cuarentena
  + `riesgo_inyeccion: true` ([[gen-anti-inyeccion]])—; **exención**: pares con relación
  ```
- ruta de aplicación: **genoma → compuerta** (2 eventos, 2 commits, re-sync `AGENTS.md`); luego migración.

## P3 — Reconciliar el paso de anclas de CHECKPOINT con el anclado determinista del índice
- id: `AUDIT-2026-07-02-P3` (candidato C3)
- fecha: 2026-07-02
- clase: **contradicción entre genes activos** · sev 5 · alcance 2 · **impacto 52** · status: **applied** (2026-07-02, variante "excepción declarada"; gen-jerarquizacion-indice v2)
- motivo: gen-jerarquizacion-indice prohíbe sin zona gris anclar `working/`/`episodic/` en `index.md` ("llega al índice solo cuando CONSOLIDATE lo promueve") y no lista a CHECKPOINT entre sus consumidores; gen-checkpoint (paso 3 + criterio de hecho c) ordena refrescar en `index.md` anclas de esos dos tiers. Dos genes nuevos de la misma tanda con órdenes incompatibles sobre el mismo flujo. Costura A-03 vs A-06.
- evidencia: `gen-jerarquizacion-indice.md:18-19,22` · `gen-checkpoint.md:64-65` · `index.md:30-31`.
- diff (reconciliación mínima propuesta por el maker — legalizar el puntero rotatorio como excepción declarada; la alternativa es eliminar el paso 3 de gen-checkpoint: **decidir en el gate**):
  ```diff
  # gen-jerarquizacion-indice.md (condición 2; v1 -> v2)
   2. tier `semantic/` o `procedural/` (lo de `working/` y `episodic/` no se ancla: llega al
  -   índice solo cuando CONSOLIDATE lo promueve);
  +   índice solo cuando CONSOLIDATE lo promueve; excepción declarada: el puntero rotatorio
  +   "lo más reciente" por tier que mantiene CHECKPOINT ([[gen-checkpoint]], paso 3) es
  +   navegación meta, no ancla de conocimiento, y no cuenta para `hub_umbral`);
  ```
- ruta de aplicación: **genoma → compuerta**; luego migración.

---

## Fuera del corte (siguiente en fila si rechazas alguna)
- **C4** (impacto 52) — `id_pagina` inmutable/atada a ruta vs promoción/archivo que mueven el archivo de tier (contradicción gen-identidad-de-pagina ↔ gen-ciclo-de-vida). Cuarto sev-5; quedó fuera solo por el desempate alfabético con C3. → **applied** (2026-07-02, corte ampliado a 4 por decisión del operador en el gate; gen-identidad-de-pagina v2, gen-ciclo-de-vida v3).
- **C5** (43) — gen-checkpoint atribuye al hook `Stop` postcondiciones que stop.sh/README no cumplen.
- **C6** (43) — el staging de GRAPH no excluye páginas en cuarentena y gen-graph-lens aún frasea denylist (pendiente A-07).
- **C7** (42) — el formato del log del fallback léxico de QUERY expone el nombre de archivo de páginas confidenciales.

## Confirmadas de menor impacto (registro; no entran al Top-3)
C14 y C15 (README de hooks: sobredeclara permissions; "(gen v4)" muerto), C11 (fila LINT de CLAUDE.md incompleta), C10 (README sin CHECKPOINT ni archive/), C16 (retiro de ancla al archivar no contempla hubs), C12 (`refuerzo_delta` sin regla para tipos custom como `doctrina`), C8 (advertencias de QUERY sin la cuarentena — ajustada a vacío sev-2), C13 (onboard/README con "aplicado" incompleto), C9 (entities sin carpeta en taxonomy en example/agencia/legal). Todos impacto 21.

---

> **Nota del orquestador:** los 4 sev-5 + C5–C8 son todos re-aperturas de costura de la tanda
> `810f24e`. Si apruebas P1–P3, C4 debería entrar a la siguiente tanda EVOLVE junto con los
> "fuera del corte" — o aprobarse aquí mismo como cuarta si decides ampliar el corte (la regla
> del gen fija N=3; ampliar N es decisión tuya en el gate, no del orquestador).

> **Resolución del gate (2026-07-02):** el operador aprobó P1 (variante del auditor), P2, P3
> (variante "excepción declarada") y **amplió el corte a C4**. Total aplicado: 9 mutaciones,
> 9 eventos, 9 commits, `AGENTS.md` re-sincronizado.

> **Resolución del gate, segunda tanda (2026-07-02, misma fecha):** el operador aprobó la
> tanda C5–C16 completa. **Applied**: C5 (gen-checkpoint v2 + stop.sh/README coherentes),
> C6 (gen-graph-lens v3 allowlist+cuarentena + filtro del runbook en bash/PowerShell +
> checklist — cierra el pendiente A-07), C7 (gen-query v5), C8 (gen-query v6), C12
> (gen-ciclo-de-vida v4), C16 (gen-ciclo-de-vida v5) — 6 mutaciones = 6 eventos + 6 commits —
> y los fixes directos C9/C13 (onboard), C10 (README), C11 (fila LINT de CLAUDE.md +
> re-sync), C14/C15 (hooks) en 4 commits de config. **Los 16 hallazgos de la corrida quedan
> cerrados: 16/16 applied.**
