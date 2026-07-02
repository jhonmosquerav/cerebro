#!/usr/bin/env bash
# ============================================================================
# CEREBRO — ops/backup/backup.sh  (tarea A-09, eval 2026-07-01-810f24e)
#
# Backup íntegro y CIFRADO del repo hacia un destino EXTERNO, y prueba de
# restauración. Runbook (cadencia, passphrase, destinos, programación):
#   ops/backup/runbook-backup.md
#
# Uso:
#   bash ops/backup/backup.sh <dir-destino-externo>
#   bash ops/backup/backup.sh --verify-restore <archivo .tar.gz.enc>
#
# Requiere la variable de entorno CEREBRO_BACKUP_PASSPHRASE (la passphrase
# nunca viaja por argv ni queda en la lista de procesos).
#
# Qué contiene cada backup (dentro del .tar.gz.enc):
#   <nombre>/repo.bundle               historial COMPLETO de git (bundle --all)
#   <nombre>/no-versionados.tar.gz     archivos no versionados y no ignorados
#                                      (excluye .git/, graphify-out/,
#                                       .claude/hooks/.state/)
#   <nombre>/cambios-sin-commit.patch  diff del árbol de trabajo vs HEAD
#   <nombre>/MANIFEST.txt              identidad + parámetros de cifrado
#
# Cifrado: openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt
# Salida:  0 = OK · 1 = FALLO (mensaje claro en stderr)
#
# Nota de diseño: este script es una herramienta de operación MANUAL. A
# diferencia de los hooks de sesión (que degradan en silencio con exit 0),
# aquí un fallo debe VERSE y DETENER: un backup que falla callado es peor
# que no tener backup.
# ============================================================================
set -eu
umask 077

say()  { printf '%s\n' "$*"; }
warn() { printf 'AVISO: %s\n' "$*" >&2; }
fail() { printf 'FALLO: %s\n' "$*" >&2; exit 1; }

usage() {
  say 'uso:'
  say '  bash ops/backup/backup.sh <dir-destino-externo>'
  say '  bash ops/backup/backup.sh --verify-restore <archivo .tar.gz.enc>'
  say ''
  say 'Requiere la variable de entorno CEREBRO_BACKUP_PASSPHRASE.'
  say 'Detalles y cadencia: ops/backup/runbook-backup.md'
}

# --- ubicación del repo (el script vive en <repo>/ops/backup/) ---------------
SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
REPO_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/../.." && pwd)"

command -v git     >/dev/null 2>&1 || fail 'git no está en PATH'
command -v openssl >/dev/null 2>&1 || fail 'openssl no está en PATH (viene con Git Bash)'
command -v tar     >/dev/null 2>&1 || fail 'tar no está en PATH (viene con Git Bash)'

git -C "$REPO_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || fail "no encuentro un repo git en '$REPO_DIR' (¿moviste el script fuera de ops/backup/?)"

need_passphrase() {
  if [ -z "${CEREBRO_BACKUP_PASSPHRASE:-}" ]; then
    fail 'falta la variable de entorno CEREBRO_BACKUP_PASSPHRASE.
  Expórtala sin dejarla en el historial del shell:
    read -r -s CEREBRO_BACKUP_PASSPHRASE && export CEREBRO_BACKUP_PASSPHRASE
  Cómo generarla y dónde guardarla: ops/backup/runbook-backup.md'
  fi
}

make_workdir() {
  WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/cerebro-backup.XXXXXX")" \
    || fail 'no pude crear el directorio temporal'
  # el temporal puede contener material DESCIFRADO: se borra siempre al salir
  trap 'rm -rf "$WORK_DIR"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
}

# --- nota de restauración (sin secretos) que acompaña a los backups ----------
write_restore_note() {
  cat > "$1/COMO-RESTAURAR.txt" <<'EOF'
CEREBRO — cómo restaurar un backup (no necesitas el repo vivo ni este script)
Generado por ops/backup/backup.sh. Este archivo NO contiene secretos.

Necesitas: Git Bash (git, openssl, tar) y la passphrase CEREBRO_BACKUP_PASSPHRASE
(guardada en tu gestor de contraseñas — NUNCA junto a estos archivos).

1) (Opcional) verificar integridad del archivo:
     openssl dgst -sha256 -r cerebro-backup-FECHA-SHA.tar.gz.enc
   y compararlo con el .sha256 que lo acompaña.
2) Descifrar (openssl pedirá la passphrase de forma interactiva):
     openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -salt \
       -in cerebro-backup-FECHA-SHA.tar.gz.enc -out backup.tar.gz
3) Extraer:
     tar -xzf backup.tar.gz
4) Recuperar el repo con TODA su historia:
     git clone cerebro-backup-FECHA-SHA/repo.bundle cerebro
5) Recuperar los archivos que no estaban versionados:
     tar -xzf cerebro-backup-FECHA-SHA/no-versionados.tar.gz -C cerebro
6) (Opcional) reaplicar lo que estaba sin commitear al momento del backup:
     cd cerebro && git apply ../cerebro-backup-FECHA-SHA/cambios-sin-commit.patch
7) Revisa MANIFEST.txt (dentro del backup) para confirmar fecha, HEAD y rama.
EOF
}

# ============================================================================
# MODO 1 — crear backup:  backup.sh <dir-destino-externo>
# ============================================================================
do_backup() {
  DEST="$1"
  if [ ! -d "$DEST" ]; then
    fail "el destino '$DEST' no existe.
  Crea el directorio en un medio EXTERNO (disco USB, carpeta sincronizada a nube)
  y vuelve a correr. No hay destino por defecto a propósito: un backup dentro
  del mismo disco no protege contra pérdida del disco."
  fi
  DEST_ABS="$(CDPATH='' cd -- "$DEST" && pwd)"
  case "$DEST_ABS/" in
    "$REPO_DIR"/*) fail "el destino '$DEST_ABS' está DENTRO del repo ($REPO_DIR). Usa un medio externo." ;;
  esac

  git -C "$REPO_DIR" rev-parse --verify HEAD >/dev/null 2>&1 \
    || fail 'el repo no tiene commits todavía; no hay historial que respaldar'

  make_workdir
  SHORT_SHA="$(git -C "$REPO_DIR" rev-parse --short=7 HEAD)"
  STAMP="$(date +%Y%m%d-%H%M%S)"
  NAME="cerebro-backup-$STAMP-$SHORT_SHA"
  STAGE="$WORK_DIR/$NAME"
  mkdir -p "$STAGE"

  say "[1/5] git bundle (historial completo, todas las refs)…"
  git -C "$REPO_DIR" bundle create "$STAGE/repo.bundle" --all
  git -C "$REPO_DIR" bundle verify "$STAGE/repo.bundle" >/dev/null \
    || fail 'el bundle recién creado no verifica; no continúo'

  say "[2/5] archivos no versionados (excluye ignorados, graphify-out/, .claude/hooks/.state/)…"
  UNSTAGE="$WORK_DIR/no-versionados"
  mkdir -p "$UNSTAGE"
  N=0
  git -C "$REPO_DIR" -c core.quotepath=false ls-files --others --exclude-standard \
    > "$WORK_DIR/no-versionados.lst"
  while IFS= read -r f; do
    if [ -z "$f" ]; then continue; fi
    case "$f" in
      .git/*|graphify-out/*|.claude/hooks/.state/*) continue ;;
    esac
    if [ -f "$REPO_DIR/$f" ]; then
      d="$(dirname -- "$f")"
      mkdir -p "$UNSTAGE/$d"
      cp -p -- "$REPO_DIR/$f" "$UNSTAGE/$f"
      N=$((N + 1))
    fi
  done < "$WORK_DIR/no-versionados.lst"
  tar -czf "$STAGE/no-versionados.tar.gz" -C "$UNSTAGE" .
  say "      $N archivo(s) no versionados incluidos"

  say "[3/5] cambios sin commitear (patch de respaldo)…"
  # -c core.safecrlf=false: solo acalla el aviso LF/CRLF de Windows en esta lectura
  git -C "$REPO_DIR" -c core.safecrlf=false diff --binary HEAD > "$STAGE/cambios-sin-commit.patch"
  if [ -s "$STAGE/cambios-sin-commit.patch" ]; then
    warn 'hay cambios sin commitear: van en cambios-sin-commit.patch, pero el bundle solo lleva lo commiteado — commitea pronto'
  fi

  say "[4/5] manifiesto…"
  {
    printf 'backup: %s\n'  "$NAME"
    printf 'fecha: %s\n'   "$(date +%Y-%m-%dT%H:%M:%S)"
    printf 'repo: %s\n'    "$REPO_DIR"
    printf 'head: %s\n'    "$(git -C "$REPO_DIR" rev-parse HEAD)"
    printf 'rama: %s\n'    "$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"
    printf 'no_versionados: %s archivo(s)\n' "$N"
    printf 'cifrado: openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -pass env:CEREBRO_BACKUP_PASSPHRASE\n'
    printf 'git: %s\n'     "$(git --version)"
    printf 'openssl: %s\n' "$(openssl version)"
    printf 'estado_arbol_al_respaldar (git status --porcelain):\n'
    git -C "$REPO_DIR" status --porcelain | sed 's/^/  /'
  } > "$STAGE/MANIFEST.txt"

  say "[5/5] empaquetado y cifrado…"
  tar -czf "$WORK_DIR/$NAME.tar.gz" -C "$WORK_DIR" "$NAME"
  OUT="$DEST_ABS/$NAME.tar.gz.enc"
  openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt \
    -pass env:CEREBRO_BACKUP_PASSPHRASE \
    -in "$WORK_DIR/$NAME.tar.gz" -out "$OUT" \
    || fail 'openssl no pudo cifrar el paquete'

  SHA256="$(openssl dgst -sha256 -r "$OUT" | cut -d' ' -f1)"
  printf '%s\n' "$SHA256" > "$OUT.sha256"
  write_restore_note "$DEST_ABS"
  BYTES="$(wc -c < "$OUT" | tr -d '[:space:]')"

  say ''
  say 'OK: backup creado y cifrado'
  say "  archivo : $OUT"
  say "  sha256  : $SHA256"
  say "  bytes   : $BYTES"
  say "  head    : $SHORT_SHA ($(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD))"
  say ''
  say 'Siguiente paso recomendado (prueba de restauración):'
  say "  bash ops/backup/backup.sh --verify-restore '$OUT'"
}

# ============================================================================
# MODO 2 — prueba de restauración:  backup.sh --verify-restore <archivo>
# Descifra a un temporal, clona el bundle, corre git fsck y compara HEAD
# con el repo vivo. No escribe nada dentro del repo ni del destino.
# ============================================================================
do_verify() {
  ENC="$1"
  if [ ! -f "$ENC" ]; then fail "no existe el archivo '$ENC'"; fi
  make_workdir
  VDIR="$WORK_DIR/verify"
  mkdir -p "$VDIR"

  say "[1/7] checksum del archivo cifrado…"
  if [ -f "$ENC.sha256" ]; then
    WANT="$(cat "$ENC.sha256")"
    GOT="$(openssl dgst -sha256 -r "$ENC" | cut -d' ' -f1)"
    if [ "$WANT" = "$GOT" ]; then
      say '      sha256 coincide con el .sha256 registrado'
    else
      fail "el sha256 NO coincide con $ENC.sha256 — archivo alterado o truncado"
    fi
  else
    say '      (sin archivo .sha256 al lado; se omite este chequeo)'
  fi

  say "[2/7] descifrando…"
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -salt \
    -pass env:CEREBRO_BACKUP_PASSPHRASE \
    -in "$ENC" -out "$VDIR/backup.tar.gz" 2>/dev/null \
    || fail 'no se pudo descifrar (¿CEREBRO_BACKUP_PASSPHRASE incorrecta o archivo corrupto?)'

  say "[3/7] extrayendo…"
  tar -xzf "$VDIR/backup.tar.gz" -C "$VDIR" \
    || fail 'el tar interno no extrae (archivo corrupto)'
  INNER=''
  for d in "$VDIR"/cerebro-backup-*; do
    if [ -d "$d" ]; then INNER="$d"; break; fi
  done
  if [ -z "$INNER" ]; then fail 'estructura inesperada: no hay directorio cerebro-backup-* dentro del paquete'; fi
  if [ -f "$INNER/MANIFEST.txt" ]; then
    say '      manifiesto del backup:'
    sed -n '1,5p' "$INNER/MANIFEST.txt" | sed 's/^/        /'
  fi

  say "[4/7] integridad del tar de no versionados…"
  if [ ! -f "$INNER/no-versionados.tar.gz" ]; then fail 'falta no-versionados.tar.gz en el backup'; fi
  gzip -t "$INNER/no-versionados.tar.gz" || fail 'no-versionados.tar.gz está corrupto'

  say "[5/7] git bundle verify + clone…"
  if [ ! -f "$INNER/repo.bundle" ]; then fail 'falta repo.bundle en el backup'; fi
  git -C "$REPO_DIR" bundle verify "$INNER/repo.bundle" >/dev/null \
    || fail 'git bundle verify falló'
  git clone --quiet "$INNER/repo.bundle" "$VDIR/restaurado" \
    || fail 'git clone desde el bundle falló'

  say "[6/7] git fsck sobre el clon restaurado…"
  git -C "$VDIR/restaurado" fsck --no-progress >/dev/null \
    || fail 'git fsck reportó corrupción en el clon restaurado'

  say "[7/7] comparando HEAD con el repo vivo…"
  HEAD_VIVO="$(git -C "$REPO_DIR" rev-parse HEAD)"
  HEAD_BK="$(git -C "$VDIR/restaurado" rev-parse HEAD)"
  say ''
  if [ "$HEAD_VIVO" = "$HEAD_BK" ]; then
    say 'OK: restauración verificada — el HEAD del backup es idéntico al del repo vivo'
    say "  head: $HEAD_BK"
  elif git -C "$REPO_DIR" merge-base --is-ancestor "$HEAD_BK" "$HEAD_VIVO" 2>/dev/null; then
    say 'OK: restauración verificada — backup íntegro pero ANTERIOR al estado actual'
    say "  head del backup   : $HEAD_BK"
    say "  head del repo vivo: $HEAD_VIVO"
    warn 'el repo avanzó desde este backup; genera uno nuevo para cubrir los últimos commits'
  else
    fail "el HEAD del backup ($HEAD_BK) no es ancestro del repo vivo ($HEAD_VIVO): historias divergentes.
  ¿Hubo una purga/reescritura de historia después de este backup? Si fue así, este
  backup contiene la historia VIEJA (incluido lo purgado): destrúyelo y genera uno
  nuevo. Ver ops/runbook-git-seguro.md (§ purga) y ops/backup/runbook-backup.md."
  fi
}

# ============================================================================
# Dispatch
# ============================================================================
MODE="${1:-}"
case "$MODE" in
  '')
    usage >&2
    fail 'falta el argumento: directorio destino EXTERNO, o --verify-restore <archivo>'
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  --verify-restore)
    if [ -z "${2:-}" ]; then
      fail '--verify-restore requiere la ruta del archivo .tar.gz.enc'
    fi
    need_passphrase
    do_verify "$2"
    ;;
  *)
    if [ -n "${2:-}" ]; then
      fail "sobra el argumento '$2' (¿el destino lleva espacios sin comillas?)"
    fi
    need_passphrase
    do_backup "$MODE"
    ;;
esac
