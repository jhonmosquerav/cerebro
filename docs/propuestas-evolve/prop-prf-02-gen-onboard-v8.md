---
tipo: propuesta-evolve
tarea: PRF-02
status: approved
fecha: 2026-10-20
genes_afectados: [gen-onboard]
origen: prop-prf-01 (gen-perfiles v1) necesita un aplicador mecánico del perfil
---

# Propuesta EVOLVE PRF-02 — `gen-onboard` v7 → v8: ONBOARD aplica el perfil

## Motivación

Si el perfil vive en el manifiesto, el único camino legítimo para que cambie el estado
efectivo es el mismo que para la taxonomía y los seeds: **ONBOARD**. Así se conserva la
garantía central (mismo manifiesto + misma fecha ⇒ mismo hash) y el archivo aplicado
nunca se edita a mano.

## Diff (v7 → v8)

Párrafo nuevo: cuando el manifiesto declara `profile`/`capabilities`, `onboard apply`
renderiza `genome/perfil.md`, añade la línea `- Perfil:` al bloque `## Estado` de
`index.md` y registra `profile_applied` en `genome/events.jsonl` solo si cambia el
conjunto efectivo (re-aplicar es no-op). Sin declaración no escribe nada (⇒ `completo`).
Sigue siendo del agente explicar al operador qué apaga cada perfil durante la entrevista.

## Infra (mismo cambio, probada)

`onboard.py` (render del perfil, evento, bloque Estado), `manifest.py` (propiedades
`profile`/`capabilities`/`declares_profile` + validación). Tests:
`test_profile.TestOnboardAplicaPerfil` (sin declaración no escribe; declarado escribe
perfil, evento e índice; idempotente; cambio de perfil deja evento; mismo hash) y
`test_onboard` ajustado (el ejemplo ahora declara `completo` ⇒ 2 eventos).

## Compuerta

Aprobada por el operador en sesión Claude Code del 2026-10-20 (misma instrucción que
PRF-01). Registro: `genome/events.jsonl` (`gene_edited`, v7 -> v8), commit firmado.
