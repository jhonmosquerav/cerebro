# Runbook — firma y atribución de aprobaciones del gate (C-04)

**Qué protege:** el hash-chain de `genome/events.jsonl` (C-03) prueba que la historia no
se reescribió (*tamper-evidence*); esta capa añade **autoría fuerte**: que la aprobación
de cada mutación la dio quien dice el ledger, verificable por un tercero con git puro.

**Diseño elegido (2026-08-07):** firma **SSH** de los commits de mutación con
`allowed_signers` — sin keyring GPG; la mayoría de operadores ya tiene clave SSH y
`git verify-commit` hace la verificación. Referencia de la alternativa descartada en
`docs/roadmap-endurecimiento.md` (§ "Mapa a C-04").

## Doctrina (gen-compuerta-mutacion v5)

1. **Atribución obligatoria**: toda línea nueva del ledger lleva `approved_by` con la
   identidad del aprobador (la de `ops/allowed_signers` cuando exista; mientras tanto la
   identidad git del vault) — nunca un genérico sin dueño — y el `signal`/contexto debe
   permitir localizar DÓNDE se dio la aprobación (fecha + canal, p. ej. "instrucción de
   la sesión YYYY-MM-DD"). Desde ATR-01 (2026-10-25) **no hace falta pasarla a mano**:
   `events append` y `onboard apply` la resuelven en este orden y la imprimen
   (`aprobador: … (fuente)`):
   1. el principal de `ops/allowed_signers` cuya clave es la de `user.signingkey`
      (con `gpg.format ssh`);
   2. si no casa, `git config user.email`, con aviso si no figuras en `ops/allowed_signers`;
   3. si no hay ninguno, exit 2 sin escribir.
   Un `--approved-by` explícito genérico (`user`, `operador`, `agente`…) se rechaza, y
   `verify` marca EVT-09 en cualquier genérico posterior a la primera línea atribuida.
2. **Firma de commits de mutación**: desde que el operador registra su clave en
   `ops/allowed_signers`, los commits que tocan `genome/` **se firman**; un commit de
   mutación sin firma válida es hallazgo de AUDIT.
3. **Corregir una atribución sin reescribir el ledger**: si una línea salió con un
   genérico o con otra identidad, no se edita (el append-only lo prohíbe). La firma el
   aprobador real con un evento nuevo:

   ```bash
   python tools/cerebro.py events append --type attribution_corrected \
     --target genome/events.jsonl \
     --signal "<qué líneas, por qué, dónde se aprobó cada una (fecha + canal)>" \
     --diff "approved_by: user → <identidad> (L<n>, …)" \
     --corrects <sha256 de la línea> [--corrects <sha256> …]
   ```

   El sha256 se calcula sobre la línea exacta (sin el salto final). `corrects` lo valida
   EVT-10: tiene que apuntar a líneas que existen antes del evento. Primer caso real: L98 de
   este vault, que cura las L95–L97 (ATR-01).
4. **Al clonar el template**: `ops/allowed_signers` trae la clave del autor del template.
   Añade la tuya (commit propio) y no la borres: verifica la historia firmada que heredas.
   Mientras tu clave no figure, la identidad resuelta será tu `git user.email` y se avisará.

## Activación (acto del operador, ~5 minutos, una sola vez)

```bash
git config gpg.format ssh
git config user.signingkey ~/.ssh/id_ed25519.pub
git config gpg.ssh.allowedSignersFile ops/allowed_signers
git config commit.gpgsign true   # o firmar solo mutaciones con -S
```

Y añade tu clave pública a `ops/allowed_signers` (formato:
`<email> namespaces="git" <tipo-clave> <clave-publica>`), commiteando ese cambio —
la incorporación de un firmante es a su vez un evento auditable.

## Verificación (cualquier tercero)

```bash
git -c gpg.ssh.allowedSignersFile=ops/allowed_signers log --show-signature -- genome/
```

`Good "git" signature` + identidad del allowed_signers = la aprobación registrada en la
línea del ledger de ese commit está firmada por su autor.

## Estado honesto

- Doctrina y andamiaje: **aplicados 2026-08-07** (gen v4 + este runbook + plantilla
  `ops/allowed_signers`).
- Firma criptográfica: **inactiva hasta que el operador registre su clave** — la clave
  privada es del humano; un agente no la genera ni la usa por él. Hasta entonces la
  atribución descansa en identidad git + hash-chain + este registro, y así se declara.
