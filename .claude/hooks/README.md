# Hooks de CEREBRO — el loop de memoria, real

Los 3 hooks de `../settings.json` ya **no son stubs**: apuntan a los scripts de esta
carpeta, que cierran el loop de memoria infinita de forma mecánica y verificable.
Diseño común: **POSIX puro** (corren en Git Bash también en Windows), sin `jq`, sin
flags GNU-only, y **tolerantes a fallo** — un hook jamás rompe la sesión; todos
terminan con `exit 0` y degradan con elegancia (archivo ausente → aviso, sin python →
nota manual, sin git → permitir el cierre).

| Hook | Script | Timeout | Qué hace |
|---|---|---|---|
| `SessionStart` | `session-start.sh` | 15 s | Inyecta contexto de arranque (su stdout entra al contexto) |
| `PreCompact` | `pre-compact.sh` | 30 s | Vuelca un snapshot mecánico de la sesión a `wiki/working/` |
| `Stop` | `stop.sh` | 15 s | Exige el resumen episódico si la sesión tocó el cerebro |

## session-start.sh
- Imprime (~120 líneas máximo, presupuesto de contexto): cabecera + primeras 50 líneas
  de `index.md` + primeras 35 de `log.md` (lo reciente arriba) + genes activos en una línea.
- Si `source == "compact"` o existen marcadores `pending-dump-*` en `.state/`, añade un
  **recordatorio**: revisar `wiki/working/`, destilar lo valioso y borrar el marcador.
- Contrato de Claude Code: lo que un hook `SessionStart` imprime por stdout se inyecta
  como contexto de la sesión.

## pre-compact.sh
- Crea `wiki/working/<YYYY-MM-DD>-precompact-<session8>.md` (`session8` = primeros 8
  caracteres del `session_id`) con frontmatter válido según [[gen-frontmatter-obligatorio]]:
  `tier: working`, `decay_rate: high`, `confidence: 0.3`. `sensibilidad` se omite a
  propósito para que aplique el default del manifiesto (gen v4).
- Cuerpo: metadatos de la sesión (fecha, `session_id`, trigger, ruta del transcript) y,
  si hay `python3`/`python` funcional, los últimos ~15 turnos de texto user/assistant del
  transcript JSONL (texto plano, sin tool calls, ~500 caracteres por turno). Sin python:
  una nota con la ruta del transcript para revisión manual.
- Deja el marcador `.claude/hooks/.state/pending-dump-<session8>` (contiene la ruta de la
  página). `.state/` está en `.gitignore`: es estado runtime, no conocimiento.
- **Idempotente**: si la página de esa fecha/sesión ya existe, añade una sección
  `## Volcado <fecha> <hora>` en lugar de duplicar el archivo.
- El stdout de `PreCompact` **no** llega al modelo; el valor del hook es lo que escribe a disco.

## stop.sh — política del resumen episódico
Bloquea el cierre **solo** si se cumplen las dos condiciones a la vez:
1. `git status --porcelain` (desde `$CLAUDE_PROJECT_DIR`) muestra cambios en `wiki/`,
   `genome/`, `log.md` o `index.md` — la sesión tocó el cerebro; y
2. no existe `wiki/episodic/<YYYY-MM-DD>-<session8>.md`.

En ese caso imprime `{"decision":"block","reason":"…"}` con la instrucción exacta: crear
ese archivo con frontmatter válido (`tier: episodic`) y un resumen de la sesión (qué se
hizo, qué páginas se tocaron, pendientes), y borrar el marcador `pending-dump` de la
sesión si existe. En **todos** los demás casos permite el cierre:
- `stop_hook_active: true` en el stdin → permite SIEMPRE (obligatorio: evita bucles infinitos);
- árbol limpio en esas rutas → permite;
- sin `git`, sin `session_id` o sin fecha → permite (degradación: nunca bloquear a ciegas).

## Límites honestos (v1)
- La extracción de `pre-compact.sh` es **mecánica**: recorta texto plano del transcript,
  no resume ni juzga. El volcado *inteligente* lo hace el agente cuando `SessionStart` le
  muestra el recordatorio y revisa `wiki/working/`.
- El resumen episódico lo escribe el **agente**; el hook Stop solo lo exige y verifica su
  existencia (no su calidad).
- El `EVOLVE` en modo propuesta al cierre sigue siendo responsabilidad del agente; este
  hook no lo dispara.

## Probarlos a mano (Git Bash, desde la raíz del repo)
Los scripts usan `${CLAUDE_PROJECT_DIR:-$PWD}`, así que basta ejecutarlos desde la raíz:

```sh
# SessionStart (arranque normal; con source=compact añade el recordatorio)
echo '{"session_id":"abc12345-0000","source":"startup"}' | bash .claude/hooks/session-start.sh

# PreCompact — OJO: escribe de verdad en wiki/working/ y .claude/hooks/.state/;
# si es solo una prueba, borra después la página y el marcador que genere.
echo '{"session_id":"test0000-1111","trigger":"manual","transcript_path":"C:\\ruta\\al\\transcript.jsonl"}' | bash .claude/hooks/pre-compact.sh

# Stop — anti-bucle (debe permitir sin imprimir nada):
echo '{"session_id":"test0000-1111","stop_hook_active":true}' | bash .claude/hooks/stop.sh
# Stop — caso real (bloquea solo si hay cambios en wiki/genome/log.md/index.md
# y no existe wiki/episodic/<hoy>-test0000.md):
echo '{"session_id":"test0000-1111","stop_hook_active":false}' | bash .claude/hooks/stop.sh
```

- `CEREBRO_HOOKS_NO_PYTHON=1` fuerza el fallback POSIX de `pre-compact.sh` (para probar
  la ruta sin python).
- Sintaxis sin ejecutar: `bash -n .claude/hooks/<script>.sh`.

## Notas operativas
- `settings.json` se relee **al iniciar sesión**: los cambios en hooks o permisos aplican
  al reiniciar Claude Code, no en caliente.
- Además del loop, `settings.json` endurece permisos: `deny` de `Write`/`Edit` sobre
  `raw/**` ([[gen-raw-inmutable]] hecho mecánico) y `ask` sobre `genome/**` (la compuerta
  de [[gen-compuerta-mutacion]] materializada: toda escritura al genoma pide confirmación
  humana).
- Gotcha aprendido a la mala: los `command` de los hooks corren en **bash**
  (`/usr/bin/bash`), también en Windows — no en PowerShell. Entrecomilla siempre
  (paréntesis sin comillas rompieron los stubs originales).
- Los scripts se invocan con `bash "$CLAUDE_PROJECT_DIR/..."`, así que no dependen del
  bit de ejecución.
- Estos scripts se versionan en git: son parte del genoma operativo.
