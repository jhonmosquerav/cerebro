#!/bin/sh
# CEREBRO — hook Stop
# Política del resumen episódico: bloquea el cierre SOLO si la sesión tocó el
# cerebro (cambios en wiki/, genome/, log.md o index.md según git status) y aún
# no existe wiki/episodic/<YYYY-MM-DD>-<session8>.md. En ese caso imprime
# {"decision":"block","reason":"..."} para instruir al agente. En cualquier otro
# caso permite el cierre. Anti-bucle OBLIGATORIO: si stop_hook_active es true,
# permite siempre. Degradación elegante: sin git, sin session_id o sin fecha →
# permitir (nunca bloquear a ciegas). Siempre exit 0.
# POSIX puro (Git Bash en Windows); sin jq, sin flags GNU-only.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

# --- stdin: JSON del hook ---
RAW=""
if [ ! -t 0 ]; then
  RAW=$(cat 2>/dev/null || true)
fi

# --- anti-bucle: si ya venimos de un block de este hook, permitir SIEMPRE ---
if printf '%s' "$RAW" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

SESSION_ID=$(printf '%s' "$RAW" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
SESSION8=$(printf '%s' "$SESSION_ID" | cut -c1-8 | tr -cd 'A-Za-z0-9-')
# sin session_id no podemos exigir un archivo concreto → permitir (degradación)
[ -n "$SESSION8" ] || exit 0

# sin git no hay forma fiable de saber si la sesión tocó el cerebro → permitir
command -v git >/dev/null 2>&1 || exit 0

# ¿la sesión tocó el cerebro? (solo lectura; incluye archivos nuevos sin trackear)
CHANGES=$(git -C "$PROJECT_DIR" status --porcelain -- wiki genome log.md index.md 2>/dev/null || true)
[ -n "$CHANGES" ] || exit 0

DATE=$(date +%Y-%m-%d 2>/dev/null) || exit 0
EPISODIC_REL="wiki/episodic/$DATE-$SESSION8.md"
if [ -f "$PROJECT_DIR/$EPISODIC_REL" ]; then
  exit 0
fi

# --- falta el resumen episódico: bloquear con instrucción precisa ---
# El reason no debe contener comillas dobles ni backslashes (JSON construido a mano).
MARKER_REL=".claude/hooks/.state/pending-dump-$SESSION8"
REASON="La sesión tocó el cerebro (hay cambios en wiki/, genome/, log.md o index.md) y falta el resumen episódico. Crea exactamente el archivo $EPISODIC_REL con frontmatter YAML válido según gen-frontmatter-obligatorio (title, type, tier: episodic, tags, confidence, created, last_reinforced, decay_rate, sources, relations) y un resumen breve de la sesión: qué se hizo, qué páginas se tocaron y qué quedó pendiente. Si existe el marcador $MARKER_REL, bórralo. Después intenta terminar de nuevo."
printf '{"decision":"block","reason":"%s"}\n' "$REASON"
exit 0
