---
tipo: propuesta-evolve
tarea: PRF-03
status: approved
fecha: 2026-10-20
genes_afectados: [gen-lint]
origen: prop-prf-01 (gen-perfiles v1): el estado aplicado necesita un detector de deriva
---

# Propuesta EVOLVE PRF-03 — `gen-lint` v7 → v8: detectores PRF-01 / PRF-02

## Motivación

Un archivo de estado que leen hooks y comandos sin verificación es una invitación a la
deriva silenciosa: alguien cambia `profile:` en el manifiesto, olvida re-correr ONBOARD y
el vault sigue corriendo con el perfil viejo; o alguien "arregla" `genome/perfil.md` a
mano. Como con el ledger y el espejo, la respuesta es un detector mecánico que entre en
`verify` y, por tanto, en el pre-commit y el CI.

## Diff (v7 → v8)

Detector (g) **perfil**: `PRF-01` (error) cuando el manifiesto declara perfil y
`genome/perfil.md` falta, está corrupto o difiere en nombre o en alguna capacidad;
`PRF-02` (aviso) cuando existe el archivo sin declaración en el manifiesto. Error y no
aviso porque un hook o un comando leerían un estado que el manifiesto ya no respalda. La
corrección es siempre la misma: re-correr `onboard apply` (nunca editar el archivo).

## Infra (mismo cambio, probada)

`lint.py` (`_check_profile`, códigos PRF-01/PRF-02, se ejecuta en `run` y por tanto en
`verify`). Tests: `test_profile` (deriva tras editar el manifiesto, archivo sin
declaración ⇒ aviso, archivo corrupto ⇒ error y fail-open de los comandos).

## Compuerta

Aprobada por el operador en sesión Claude Code del 2026-10-20 (misma instrucción que
PRF-01). Registro: `genome/events.jsonl` (`gene_edited`, v7 -> v8), commit firmado.
