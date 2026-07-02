#!/bin/sh
# CEREBRO — hook SessionStart
# Inyecta al contexto de la sesión (stdout → contexto): cabecera + head de index.md
# + head de log.md + genes activos. Presupuesto de contexto: ~120 líneas máximo.
# Tolerante a fallos: este hook JAMÁS debe romper la sesión → siempre exit 0.
# POSIX puro (corre en Git Bash en Windows); sin jq, sin flags GNU-only.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$PROJECT_DIR/.claude/hooks/.state"

# --- stdin: JSON del hook (si no hay pipe, p. ej. prueba manual, no bloquear) ---
RAW=""
if [ ! -t 0 ]; then
  RAW=$(cat 2>/dev/null || true)
fi
SOURCE=$(printf '%s' "$RAW" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)

echo "=== CEREBRO: contexto de arranque (hook SessionStart, source: ${SOURCE:-desconocido}) ==="
echo "Regla de la casa: navega desde index.md por relaciones; nunca cargues la wiki entera."

# --- index.md: primeras 50 líneas ---
if [ -f "$PROJECT_DIR/index.md" ]; then
  echo ""
  echo "--- index.md (primeras 50 líneas) ---"
  head -n 50 "$PROJECT_DIR/index.md" 2>/dev/null || true
else
  echo "[aviso] index.md no encontrado en $PROJECT_DIR"
fi

# --- log.md: primeras 35 líneas (lo más reciente va arriba) ---
if [ -f "$PROJECT_DIR/log.md" ]; then
  echo ""
  echo "--- log.md (primeras 35 líneas, lo más reciente arriba) ---"
  head -n 35 "$PROJECT_DIR/log.md" 2>/dev/null || true
else
  echo "[aviso] log.md no encontrado en $PROJECT_DIR"
fi

# --- genes activos: una sola línea con los nombres de archivo ---
GENES=""
for g in "$PROJECT_DIR/genome/genes/"*.md; do
  [ -e "$g" ] || continue
  base=$(basename "$g" .md)
  if [ -n "$GENES" ]; then GENES="$GENES, $base"; else GENES="$base"; fi
done
echo ""
if [ -n "$GENES" ]; then
  echo "--- genes activos (genome/genes/) ---"
  printf '%s\n' "$GENES"
else
  echo "[aviso] no se encontraron genes en genome/genes/"
fi

# --- recordatorio: volcados pre-compactación pendientes de destilar ---
PENDING=""
for m in "$STATE_DIR"/pending-dump-*; do
  [ -e "$m" ] || continue
  base=$(basename "$m")
  if [ -n "$PENDING" ]; then PENDING="$PENDING, $base"; else PENDING="$base"; fi
done
if [ "$SOURCE" = "compact" ] || [ -n "$PENDING" ]; then
  echo ""
  echo "[RECORDATORIO] Hay volcados pre-compactación por revisar: mira wiki/working/,"
  echo "destila lo valioso (a semantic/, procedural/ o log.md) y borra el marcador"
  printf '%s\n' "correspondiente en .claude/hooks/.state/. Marcadores: ${PENDING:-ninguno (arranque tras compactación)}"
fi

exit 0
