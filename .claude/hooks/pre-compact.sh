#!/bin/sh
# CEREBRO — hook PreCompact
# Antes de compactar el contexto, vuelca un snapshot MECÁNICO de la sesión a
# wiki/working/<YYYY-MM-DD>-precompact-<session8>.md (frontmatter válido según
# gen-frontmatter-obligatorio; tier working, decay_rate high) y deja un marcador
# en .claude/hooks/.state/pending-dump-<session8> para que SessionStart recuerde
# destilar. El stdout de PreCompact NO llega al modelo: el valor es lo escrito a disco.
# Idempotente: si la página del día/sesión ya existe, añade una sección con la hora.
# Tolerante a fallos: JAMÁS debe romper la sesión → siempre exit 0.
# POSIX puro (Git Bash en Windows); python opcional con fallback POSIX; sin jq.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$PROJECT_DIR/.claude/hooks/.state"
WORKING_DIR="$PROJECT_DIR/wiki/working"

# --- stdin: JSON del hook ---
RAW=""
if [ ! -t 0 ]; then
  RAW=$(cat 2>/dev/null || true)
fi

# Extrae "clave":"valor" (primera aparición) con sed POSIX.
json_str() {
  printf '%s' "$RAW" | sed -n 's/.*"'"$1"'"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1
}

SESSION_ID=$(json_str session_id)
TRIGGER=$(json_str trigger)
TRANSCRIPT=$(json_str transcript_path)
# des-escapar JSON en la ruta: \\ -> \ y \/ -> /
TRANSCRIPT=$(printf '%s' "$TRANSCRIPT" | sed 's/\\\\/\\/g; s/\\\//\//g')

SESSION8=$(printf '%s' "$SESSION_ID" | cut -c1-8 | tr -cd 'A-Za-z0-9-')
[ -n "$SESSION8" ] || SESSION8="sin-id"
[ -n "$TRIGGER" ] || TRIGGER="desconocido"

DATE=$(date +%Y-%m-%d 2>/dev/null) || DATE="sin-fecha"
TIME=$(date +%H:%M:%S 2>/dev/null) || TIME="sin-hora"

PAGE_REL="wiki/working/$DATE-precompact-$SESSION8.md"
PAGE="$PROJECT_DIR/$PAGE_REL"

if ! mkdir -p "$WORKING_DIR" 2>/dev/null; then
  echo "[CEREBRO] PreCompact: no se pudo crear wiki/working/; se omite el volcado."
  exit 0
fi
mkdir -p "$STATE_DIR" 2>/dev/null || true

# --- python disponible y funcional (en Windows el alias de la Store no ejecuta) ---
PYBIN=""
if [ -z "${CEREBRO_HOOKS_NO_PYTHON:-}" ]; then
  for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'print(0)' >/dev/null 2>&1; then
      PYBIN="$cand"
      break
    fi
  done
fi

# --- extracción mecánica: últimos ~15 turnos de texto user/assistant del transcript ---
TURNS=""
if [ -n "$PYBIN" ] && [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
  TURNS=$(
    PYTHONIOENCODING=utf-8 "$PYBIN" - "$TRANSCRIPT" 2>/dev/null <<'PYEOF'
import io
import json
import sys

MAX_TURNS = 15
MAX_CHARS = 500

def texto(contenido):
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = []
        for item in contenido:
            if isinstance(item, dict) and item.get("type") == "text":
                partes.append(item.get("text") or "")
        return "\n".join(partes)
    return ""

turnos = []
try:
    with io.open(sys.argv[1], "r", encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea:
                continue
            try:
                obj = json.loads(linea)
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            rol = obj.get("type")
            if rol not in ("user", "assistant"):
                continue
            if obj.get("isMeta") or obj.get("isSidechain"):
                continue
            msg = obj.get("message")
            if not isinstance(msg, dict):
                continue
            t = " ".join(texto(msg.get("content")).split())
            if not t:
                continue
            if len(t) > MAX_CHARS:
                t = t[:MAX_CHARS] + " [...]"
            turnos.append("- **%s**: %s" % (rol, t))
except Exception:
    pass

for t in turnos[-MAX_TURNS:]:
    print(t)
PYEOF
  ) || TURNS=""
fi

# --- página nueva: nace con frontmatter válido (gen-frontmatter-obligatorio) ---
# sensibilidad se omite a propósito: aplica el default del manifiesto
# (gen-frontmatter-obligatorio, versión vigente en genome/genes/).
if [ ! -f "$PAGE" ]; then
  {
    printf '%s\n' "---"
    printf '%s\n' "title: Volcado pre-compactación $DATE — sesión $SESSION8"
    printf '%s\n' "type: observacion"
    printf '%s\n' "tier: working"
    printf '%s\n' "tags: [precompact, sesion, memoria]"
    printf '%s\n' "confidence: 0.3"
    printf '%s\n' "created: $DATE"
    printf '%s\n' "last_reinforced: $DATE"
    printf '%s\n' "decay_rate: high"
    printf '%s\n' "sources: ['transcript de la sesión $SESSION8 (Claude Code; ruta en el cuerpo)']"
    printf '%s\n' "relations: []"
    printf '%s\n' "---"
    printf '\n'
    printf '%s\n' "# Volcado pre-compactación — sesión $SESSION8"
    printf '\n'
    printf '%s\n' "Página creada automáticamente por el hook \`PreCompact\` antes de compactar el"
    printf '%s\n' "contexto. Contenido mecánico, sin juicio: destilar lo valioso a \`semantic/\` o"
    printf '%s\n' "\`procedural/\` y dejar que el resto decaiga. Regla: [[gen-frontmatter-obligatorio]]."
  } > "$PAGE" 2>/dev/null || exit 0
fi

# --- sección de este volcado (append; una por ejecución, marcada con la hora) ---
{
  printf '\n'
  printf '%s\n' "## Volcado $DATE $TIME (trigger: $TRIGGER)"
  printf '\n'
  printf '%s\n' "- session_id: \`${SESSION_ID:-desconocido}\`"
  printf '%s\n' "- transcript: \`${TRANSCRIPT:-desconocido}\`"
  printf '\n'
  if [ -n "$TURNS" ]; then
    printf '%s\n' "Últimos turnos user/assistant (extracción mecánica, ~500 caracteres por turno, sin tool calls):"
    printf '\n'
    printf '%s\n' "$TURNS"
  else
    printf '%s\n' "_Sin extracción automática (python no disponible o transcript ilegible)._"
    printf '%s\n' "_Revisar a mano el transcript en la ruta de arriba y volcar aquí lo valioso._"
  fi
} >> "$PAGE" 2>/dev/null || exit 0

# --- marcador para el recordatorio de SessionStart y la limpieza en el cierre ---
printf '%s\n' "$PAGE_REL" > "$STATE_DIR/pending-dump-$SESSION8" 2>/dev/null || true

echo "[CEREBRO] PreCompact: volcado en $PAGE_REL (marcador pending-dump-$SESSION8)"
exit 0
