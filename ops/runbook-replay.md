# Runbook — replay y rollback del genoma (backlog C-06)

> Ensayado de verdad el 2026-07-12 en un clon de práctica (salidas reales
> abajo). La regla de la casa: **el ledger jamás pierde líneas** — revertir
> es revertir el CONTENIDO y añadir un evento `reverted` nuevo, no borrar
> historia.

## 1 · Replay — reconstruir cómo llegó el genoma a su estado

Cada mutación = 1 commit + 1 línea en `genome/events.jsonl`. Reconstruir un
estado pasado es, por diseño, una operación de git:

```bash
git log --oneline -- genome/          # la historia de mutaciones
git checkout <sha>                    # el genoma exacto en ese momento
python tools/cerebro.py hash --scope genome   # huella verificable del estado
git checkout <rama>                   # volver al presente
```

Para auditar que NINGUNA línea del pasado fue tocada entre dos versiones
cualesquiera (la garantía append-only completa):

```bash
python tools/cerebro.py events verify
```

## 2 · Rollback INCORRECTO (y cómo el sistema lo atrapa)

`git revert` de un commit de mutación completo revierte también la línea
del ledger — eso REESCRIBE la historia del conocimiento. Ensayo real:

```text
$ git revert --no-commit c25297c     # gen-ciclo-de-vida v4→v5
$ python tools/cerebro.py events verify
[ERROR] EVT-07 genome/events.jsonl — historia NO append-only: la línea 63
        fue reescrita o eliminada entre versiones (63 → 62 líneas)
```

El pre-commit (`.githooks/pre-commit`) bloquea ese commit; si alguien lo
salta con `--no-verify`, `verify` en CI lo pesca igual. Abortar con
`git revert --abort` (o `git reset --hard` si ya estaba staged).

## 3 · Rollback CORRECTO — contenido atrás, historia adelante

```bash
# 1. revertir SOLO el contenido del gen (al estado previo a la mutación)
git checkout <sha-mutación>~1 -- genome/genes/<gen>.md
#    (bajar `version` no es necesario: la versión vieja del archivo ya la trae)

# 2. registrar el evento de reversión — CON hash-chain
python tools/cerebro.py events append \
  --type gene_reverted --target <gen> \
  --signal "por qué se revierte (señal observable)" \
  --diff "vN → vN-1 (revert de contenido; el ledger conserva la historia)" \
  --status reverted

# 3. si la propuesta vino de AUDIT: marcar status: reverted en su 30-proposals.md
# 4. verificar y commitear (1 revert = 1 commit) + re-sync del espejo si aplica
python tools/cerebro.py verify --exclude temporales
git add genome/ && git commit -m "revert(genome): <gen> vN → vN-1 (<motivo>)"
```

Salida real del ensayo (paso 2):

```text
evento añadido con hash-chain: {"ts":"2026-07-12","type":"gene_reverted",
 "target":"gen-ciclo-de-vida", …, "status":"reverted","prev":"2d4fea45…"}
$ python tools/cerebro.py events verify
ledger en verde: esquema válido, historia append-only
```

## 4 · Límites honestos

- El replay reconstruye **estados commiteados**; lo no commiteado no existe
  para la auditoría (norma: 1 mutación = 1 commit, sin excepciones).
- Los commits ANTERIORES a 2026-07-12 no llevan hash-chain en sus líneas
  (`prev`): su integridad la garantiza el chequeo append-only contra git,
  no la cadena. Toda línea nueva debe nacer con `events append`
  (propuesta `prop-f0-05` pendiente de compuerta para hacerlo regla del gen).
- Purga por incidente (PII vertida): es la ÚNICA excepción a "la historia no
  se toca" y tiene su propio procedimiento gateado —
  `ops/runbook-git-seguro.md` §3 + [[gen-raw-inmutable]] v2.
