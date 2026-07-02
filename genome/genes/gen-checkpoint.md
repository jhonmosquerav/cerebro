---
id: gen-checkpoint
trigger: operación CHECKPOINT / "checkpoint" — o el agente la propone ante contexto largo o cierre de sesión sin hooks activos
status: active
version: 1
---

CHECKPOINT es la implementación **manual y portable** del loop de memoria: vuelca a disco lo
valioso de la sesión ANTES de que se pierda (compactación de contexto, cierre de sesión,
cambio de agente). El loop de memoria es un **contrato del genoma** con implementaciones
intercambiables que deben cumplir estas mismas postcondiciones: la **automática** son los
hooks de Claude Code (`PreCompact` ≈ paso 1; `Stop` ≈ pasos 2–4 + derivación a EVOLVE; ver
`.claude/hooks/README.md`); la **manual** es esta operación — cualquier agente que lea
`AGENTS.md` la ejecuta sin hooks ni harness específico. Ambas comparten la clave de
idempotencia: si coexisten sobre la misma sesión, actualizan los mismos archivos, no duplican.

## Disparador
El usuario escribe `CHECKPOINT`. Además, el agente lo PROPONE (nunca lo ejecuta sin OK, pero
tampoco lo calla) cuando nota: contexto cercano a compactarse, cierre de sesión sin hooks
activos, o ≥3 hallazgos valiosos aún sin persistir. Ejecutarlo escribe en `wiki/`, `index.md`
y `log.md` — NO muta genoma, así que no pasa por [[gen-compuerta-mutacion]].

## Clave de idempotencia
`session_key = <YYYY-MM-DD>-<slug-del-tema-dominante>` (kebab-case, sin acentos; si el harness
expone un id de sesión estable, se usa ese como slug). Se fija en el primer checkpoint de la
sesión y se reutiliza en los siguientes: **re-ejecutar CHECKPOINT actualiza, no duplica**.
Continuar el mismo tema el mismo día reutiliza la clave (es continuación); temas o días
distintos → claves distintas. **Regla de adopción** (convivencia con la implementación
automática): si ya existe un artefacto del loop para la MISMA sesión con otro nombre (p. ej.
la nota `<fecha>-precompact-<session8>.md` que deja el hook `PreCompact`), CHECKPOINT lo
adopta y lo actualiza en vez de crear un segundo archivo — nunca dos notas de working ni dos
episódicos para la misma sesión.

## Qué es "valioso" (se vuelca) y qué NO
SÍ se vuelca — solo lo que aún no está persistido en `wiki/`:
- **decisiones** tomadas en la sesión, con su porqué;
- **hechos nuevos** sobre entidades/conceptos del negocio que ninguna página recoge;
- **correcciones del usuario** a datos, clasificaciones o supuestos del agente;
- **pendientes y acuerdos** accionables (qué quedó abierto, próximos pasos);
- **fricciones/patrones repetidos** → se anotan como candidatos y se derivan a [[gen-evolve]]
  en modo propuesta (CHECKPOINT jamás muta genoma por sí mismo).
NO se vuelca:
- ruido conversacional (saludos, tanteos, razonamiento intermedio del agente);
- lo ya persistido: si la página existe, no se re-copia — a lo sumo se refuerza
  (`last_reinforced`, [[gen-frontmatter-obligatorio]]) y se enlaza;
- contenido literal de fuentes de `raw/` (eso es INGEST, no CHECKPOINT);
- secretos/credenciales; ante PII real sin anonimizar se DETIENE y pregunta, igual que
  INGEST ([[gen-confidencialidad]]).

## Pasos (deterministas e idempotentes)
1. **Volcado a working/** — crea o actualiza `wiki/working/<session_key>.md` (UNA nota por
   sesión; la separación fina en páginas propias la hará CONSOLIDATE) con frontmatter válido
   ([[gen-frontmatter-obligatorio]]): `type: observacion`, `tier: working`,
   `decay_rate: high`, `sources: ["sesion <session_key>"]`, `sensibilidad` = default del
   manifiesto ([[gen-confidencialidad]]), `confidence` inicial de fuente interna
   ([[gen-confianza-por-fuente]]); cuerpo = lo valioso, con `[[wiki-links]]` a las páginas
   que toca. En `relations` usa SOLO verbos del esquema vigente (núcleo ∪ `relation_types`
   del manifiesto): este gen no introduce verbos nuevos. Si no hubo nada valioso nuevo, este
   paso se omite (no nacen notas vacías).
2. **Episódico** — crea o actualiza `wiki/episodic/<session_key>.md`: resumen de la sesión
   (qué se hizo, operaciones corridas, decisiones, pendientes), con `type: sesion`,
   `tier: episodic`, `clase: evento`, `fecha_evento` = fecha de la sesión, `decay_rate: high`
   ([[gen-clase-temporal]]: hecho fechado, no se refuerza).
3. **Anclas** — solo si nacieron páginas nuevas NO confidenciales, refresca en `index.md` las
   anclas de los tiers `working/` y `episodic/` (apuntan a lo más reciente); no se añade un
   ancla por nota: el índice se mantiene corto.
4. **Bitácora** — UNA línea en `log.md` bajo la fecha de hoy:
   `CHECKPOINT: <session_key> — N nota(s) a working/, episódico actualizado[, M candidato(s) a EVOLVE]`.
   Si ya existe la línea de esa clave, se actualiza en vez de duplicarse.

## Qué NO hace
No procesa `raw/` (eso es INGEST), no promueve de tier ni fusiona (eso es CONSOLIDATE — las
notas quedan en `working/` esperándolo), no clasifica fino a `semantic/`, no muta genoma
(deriva a [[gen-evolve]] + compuerta) y no borra nada. Falla elegante: si un paso no puede
completarse, persiste lo que sí pudo y lo declara en su línea de `log.md` — nunca deja la
sesión sin rastro.

## Criterio de hecho
Al terminar existen (a) 0..1 nota en `working/` y (b) el episódico de la sesión, ambos con
frontmatter válido; (c) anclas al día si hubo página nueva no confidencial; (d) exactamente
una línea en `log.md` para esa `session_key`. Re-ejecutar con la misma clave no crea archivos
ni líneas nuevas: actualiza.
