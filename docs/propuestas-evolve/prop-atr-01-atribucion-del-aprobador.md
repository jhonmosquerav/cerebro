---
tipo: propuesta-evolve
tarea: ATR-01
status: approved
fecha: 2026-10-25
aprobada: 2026-10-25 — sesión 49318d8a, "Apruebo prop-atr-01 con la opción B"; aplicada en 0112ad4 (infra + L98), 5f4492f (gen-compuerta-mutacion v5, L99), 482d653 (gen-perfiles v2, L100)
genes_afectados: [gen-compuerta-mutacion, gen-perfiles]
origen: revisión de reproducibilidad y datos personales del 2026-10-25 (sesión 49318d8a) — las líneas 95–97 del ledger salieron con `approved_by: "user"` y `verify` no lo vio
---

# Propuesta EVOLVE ATR-01 — `gen-compuerta-mutacion` v4 → v5 y `gen-perfiles` v1 → v2: el aprobador siempre tiene dueño, y lo prueba un script

## Motivación

C-04 (2026-08-07, línea 78 del ledger) fijó la regla: `approved_by` lleva la identidad del
aprobador, *"nunca un genérico sin dueño"*. Desde esa línea hasta la 94 se cumplió. Las tres
últimas la rompen:

| Línea | Fecha | Mutación | `approved_by` | Dónde se aprobó de verdad |
|---|---|---|---|---|
| 95 | 2026-10-20 | gen-onboard v8→v9 (PRF-04) | `user` | sesión `0a682936`: "Apruebo prop-prf-04…" |
| 96 | 2026-10-23 | gen-onboard v9→v10 (CAT-01) | `user` | sesión `85ec123d`: instrucción end-to-end "termina la actualizacion de inicio a fin y actualiza el readme" |
| 97 | 2026-10-23 | gen-migracion-genoma v2→v3 (CAT-01) | `user` | misma instrucción, misma sesión |

Tres causas, todas mecánicas:

1. **`events append` pone `"user"` por defecto** (`tools/cerebro.py:506`). Quien olvida
   `--approved-by` escribe un genérico sin enterarse.
2. **`verify` no lo detecta.** EVT-03 solo revisa que el campo no esté vacío. La regla vive en
   prosa: es exactamente el *enforcement por convención* que la Fase 0 vino a eliminar.
3. **Dos genes se contradicen.** gen-perfiles v1 dice que `profile_applied` lleva
   *"`approved_by: user` como las siembras"*; gen-compuerta-mutacion v4 dice "nunca un
   genérico". ONBOARD (`tools/cerebro_core/onboard.py:270` y `:305`) escribe `"user"` fijo.

La autoría no se perdió: los commits de esas mutaciones están firmados con la clave SSH del
operador. Lo que falla es que el ledger, leído solo, no dice quién aprobó.

Las líneas 1–77 también dicen `user`, pero son **anteriores a la regla** (C-04 es la 78). Se
tratan como las líneas sin `prev` antes de la hash-chain: migración honesta, válidas.

## Diseño

### 1. Resolución de la identidad (`tools/cerebro_core/identity.py`, nuevo)

Cuando no se pasa `--approved-by`, la identidad se resuelve en este orden:

1. **La clave que va a firmar el commit.** Si `gpg.format = ssh`, se lee
   `user.signingkey` (archivo `.pub` o literal `key::…`) y se busca esa clave pública en
   `ops/allowed_signers`. El principal de esa línea es la identidad.
2. **Si no hay coincidencia**, `git config user.email` del vault, con aviso si existe
   `ops/allowed_signers` y esa persona no figura ("registra tu clave: runbook-firma-aprobaciones").
3. **Si no hay nada**, error (exit 2) y no se escribe nada. Jamás se cae a un genérico.

Un `--approved-by` explícito se acepta si no es genérico, con aviso si no figura en
`ops/allowed_signers`.

¿Por qué la clave de firma y no "el único firmante del archivo"? Porque una empresa que
clona el template hereda `ops/allowed_signers` con la clave del autor del template. Con la
regla del "único firmante", su primer ONBOARD quedaría atribuido al autor del template sin
aviso. Con la clave de firma, la identidad es la de quien de verdad firma el commit.

Hoy, en este vault, la resolución da `mosquera.abg@gmail.com` (tu `user.signingkey` coincide
con la única línea de `ops/allowed_signers`).

### 2. Escritura: no se puede escribir lo que `verify` marcaría

`events.append_line` rechaza (`EventError`) un `approved_by` genérico **si el ledger ya inició
la atribución** (existe al menos una línea con identidad real). Genéricos reconocidos, sin
distinguir mayúsculas: `user`, `usuario`, `operador`, `operator`, `admin`, `agent`,
`agente`, `claude`, `llm`, `system`, `sistema`, `unknown`, `desconocido`, `n/a`, `-`, `?`.

En un ledger nuevo, sin atribución iniciada (los tres `worked/`, que regeneran byte a byte),
nada cambia.

### 3. Detectores nuevos en `events verify` (y por tanto en `verify` y pre-commit)

- **EVT-09 (error)**: `approved_by` genérico en una línea posterior a la primera línea
  atribuida, salvo que la cure un `attribution_corrected` (ver 4). Misma lógica monótona que
  EVT-06 con `prev`: una vez iniciada, no se vuelve atrás.
- **EVT-10 (error)**: un `attribution_corrected` mal formado: `corrects` vacío, con algo que no
  es un sha256, o que apunta a una línea que no existe *antes* de él.

### 4. Corrección sin reescribir el ledger: evento `attribution_corrected`

El ledger es append-only: las líneas 95–97 no se tocan. Se añade una línea nueva:

```
type:        attribution_corrected
target:      genome/events.jsonl
signal:      ATR-01: las líneas 95–97 salieron con approved_by genérico "user" (default de
             events append). Aprobaciones reales: L95 PRF-04 en la sesión 0a682936
             (2026-10-20, "Apruebo prop-prf-04…"); L96–L97 CAT-01 en la sesión 85ec123d
             (2026-10-23, instrucción end-to-end del operador). Corrección aprobada en la
             sesión 49318d8a (2026-10-25).
diff:        approved_by: user → mosquera.abg@gmail.com (L95, L96, L97)
approved_by: mosquera.abg@gmail.com
corrects:    [9d2efd1a…cee50e (L95), 6965a415…7d74b4 (L96), 80356395…48242f3 (L97)]
```

`corrects` lleva el **sha256 completo** de cada línea corregida, no su número: si alguien
alterara esas líneas, la corrección dejaría de casar y EVT-05/EVT-07 lo delatarían igual. La
semántica es simple: *"estas líneas las aprobó quien firma este evento"*. Por eso solo puede
escribirla el aprobador real, en un commit firmado. CLI: `events append --type
attribution_corrected --corrects <sha> [--corrects <sha> …]`.

### 5. ONBOARD — la decisión que te toca

ONBOARD escribe `"user"` en sus siembras y en `profile_applied`. En el template no pasa nada:
nunca corrió ONBOARD. Pero en un vault clonado (que hereda la historia del template, ya
atribuida desde la línea 78), su primer `onboard apply` escribiría genéricos después de
iniciada la atribución, y con EVT-09 el `verify` saldría en rojo justo después de instalar.
Hay que resolverlo en este mismo cambio. Dos caminos:

- **B (recomendado) — ONBOARD también resuelve la identidad.** `onboard apply` (CLI) usa el
  mismo resolvedor y acepta `--approved-by`. La API de Python conserva `"user"` por defecto, así
  que los tres `worked/` (que la llaman directo, sobre ledger nuevo) **no cambian un byte**.
  Antes de escribir nada, `onboard.apply` aborta si recibe un genérico y el ledger ya inició la
  atribución. gen-perfiles v1 → v2 cambia *"`approved_by: user` como las siembras"* por *"con la
  identidad del aprobador ([[gen-compuerta-mutacion]])"*. **Por qué:** cierra la contradicción
  entre genes y no deja excepciones.
- **A (mínimo) — eximir a ONBOARD.** El detector ignora las líneas cuyo `signal` empieza por
  `ONBOARD:`. Menos código, gen-perfiles intacto. **Contra:** cualquiera que escriba
  `--signal "ONBOARD: …"` en `events append` se salta EVT-09. Es un agujero en la regla que el
  propio cambio pretende cerrar.

## Diffs de los genes

**gen-compuerta-mutacion v4 → v5** — el párrafo "Atribución de la aprobación (C-04)" queda así:

> Atribución de la aprobación (C-04): `approved_by` lleva la identidad del aprobador —
> la de `ops/allowed_signers` cuando exista; nunca un genérico sin dueño — y el contexto
> registrado debe permitir localizar dónde se dio la aprobación (fecha + canal). **`events
> append` (y `onboard apply`) la resuelven solos: la clave de `user.signingkey` buscada en
> `ops/allowed_signers`, si no `git user.email`, y si no hay ninguna abortan sin escribir; un
> genérico (`user`, `operador`, `agente`…) se rechaza en cuanto el ledger tiene una línea
> atribuida, y `verify` lo delata (EVT-09). Las líneas anteriores a la primera atribución son
> historia válida. Una atribución equivocada no se reescribe: se cura con un evento
> `attribution_corrected` cuyo `corrects` lista el sha256 de las líneas corregidas, firmado por
> el aprobador real, con fecha y canal de la aprobación original en `signal` (EVT-10 valida su
> forma).** Desde que el operador registra su clave en `ops/allowed_signers`, los commits que
> tocan `genome/` se firman (SSH, `git verify-commit`); un commit de mutación sin firma válida
> es hallazgo de AUDIT. Runbook: `ops/runbook-firma-aprobaciones.md`.

**gen-perfiles v1 → v2** (solo con B) — en el párrafo del estado efectivo:

> ~~(hash-chain, `approved_by: user` como las siembras)~~ → (hash-chain, con la identidad del
> aprobador como toda línea del ledger — [[gen-compuerta-mutacion]])

## Lo que NO hace

- No reescribe ni borra ninguna línea del ledger. Pasa de 97 a 100 líneas con B (a 99 con A).
- No toca las líneas 1–77: son anteriores a la regla.
- No regenera `worked/` ni cambia su state-hash.
- No cambia tu principal de `ops/allowed_signers`. Las líneas nuevas seguirán llevando tu
  gmail, como las 17 de C-04. Si prefieres la dirección noreply de GitHub (la que usan tus
  commits desde el 2026-10-20), es otro commit auditable de registro de firmante: aparte.
- No hace push.

## Fuera del genoma, en el mismo lote

- `worked/piscc-demo/review.md:41`: el nombre corto 8.3 de la carpeta de usuario sale de la
  prosa y queda descrito ("la ruta corta 8.3 de la carpeta de usuario").
  Es prosa, no forma parte de lo que se regenera byte a byte.
- Documentación: `ops/runbook-firma-aprobaciones.md` (orden de resolución + cómo corregir),
  `tools/README.md` (EVT-09/EVT-10), tabla de `docs/propuestas-evolve/README.md`, bitácora y
  episódico de la sesión.

## Plan de aplicación (tras el OK, una tanda, commits firmados)

1. **feat(events)** — TDD: `identity.py`, rechazo en escritura, `--corrects`, EVT-09/EVT-10,
   `onboard apply` resolviendo la identidad (B) + **línea 98 `attribution_corrected`**. El
   detector nace con su cura en el mismo commit, para que el pre-commit no bloquee.
2. **evolve(gen-compuerta-mutacion v4→v5)** + línea 99, ya con identidad resuelta.
3. **evolve(gen-perfiles v1→v2)** + línea 100 (solo con B).
4. **docs** — runbook, tools/README, propuesta `approved`, tabla, review del piscc-demo,
   bitácora, episódico.

Criterio de cierre: suite completa en verde (gateada con el exit code real, sin pipes),
`verify` en verde, `events verify` sin EVT-09, las tres líneas nuevas con identidad real y
`git verify-commit` válido en los cuatro commits.
