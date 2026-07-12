"""Integridad del ledger `genome/events.jsonl` (backlog C-03).

Tres garantías mecánicas:
1. **Esquema por línea** — cada evento parsea y trae las claves canónicas.
2. **Hash-chain opcional** — toda línea escrita con `append_line` porta
   `prev` = sha256 de la línea anterior: adulterar el pasado rompe la cadena.
   Las líneas históricas sin `prev` siguen siendo válidas (migración honesta).
3. **Append-only contra git** — cada versión histórica del archivo debe ser
   prefijo de la siguiente; reescrituras del pasado quedan delatadas.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .findings import Finding
from .schema import is_iso_date

REQUIRED_KEYS = ("ts", "type", "target", "signal", "diff", "approved_by", "status")
VALID_STATUS = {"applied", "proposed", "reverted", "pending"}
# Orden canónico de claves al escribir (las históricas usan este mismo orden).
KEY_ORDER = ("ts", "type", "target", "signal", "diff", "approved_by", "status",
             "incident_ref", "prev")


class EventError(ValueError):
    pass


def _sha(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def _read_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return [l for l in text.split("\n") if l.strip()]


def verify_file(path: Path | str) -> list[Finding]:
    path = Path(path)
    rel = path.name if not path.is_absolute() else "genome/events.jsonl"
    if not path.is_file():
        return [Finding("EVT-00", "error", rel, "el ledger no existe")]
    findings: list[Finding] = []
    lines = _read_lines(path)
    prev_ts = None
    chain_started = False
    for i, line in enumerate(lines, start=1):
        loc = f"{rel}:{i}"
        try:
            ev = json.loads(line)
        except json.JSONDecodeError as e:
            findings.append(Finding("EVT-01", "error", loc, f"JSON inválido: {e.msg}"))
            continue
        if not isinstance(ev, dict):
            findings.append(Finding("EVT-01", "error", loc, "la línea no es un objeto JSON"))
            continue
        missing = [k for k in REQUIRED_KEYS if k not in ev]
        if missing:
            findings.append(Finding("EVT-02", "error", loc,
                                    f"claves requeridas ausentes: {', '.join(missing)}"))
        if "ts" in ev and not is_iso_date(ev["ts"]):
            findings.append(Finding("EVT-03", "error", loc,
                                    f"ts no es fecha ISO: {ev['ts']!r}"))
        if "status" in ev and ev["status"] not in VALID_STATUS:
            findings.append(Finding("EVT-03", "error", loc,
                                    f"status inválido: {ev['status']!r} (∈ {sorted(VALID_STATUS)})"))
        if "approved_by" in ev and not str(ev.get("approved_by") or "").strip():
            findings.append(Finding("EVT-03", "error", loc, "approved_by vacío"))
        if "ts" in ev and is_iso_date(ev["ts"]):
            if prev_ts and ev["ts"] < prev_ts:
                findings.append(Finding("EVT-04", "aviso", loc,
                                        f"ts retrocede: {ev['ts']} < {prev_ts}"))
            prev_ts = ev["ts"]
        # hash-chain
        if "prev" in ev:
            if i == 1:
                findings.append(Finding("EVT-05", "error", loc,
                                        "la primera línea no puede portar prev"))
            else:
                expected = _sha(lines[i - 2])
                if ev["prev"] != expected:
                    findings.append(Finding(
                        "EVT-05", "error", loc,
                        f"hash-chain rota: prev={str(ev['prev'])[:12]}… "
                        f"≠ sha256(línea {i-1})={expected[:12]}…"))
            chain_started = True
        elif chain_started:
            findings.append(Finding("EVT-06", "aviso", loc,
                                    "línea sin prev después de iniciada la cadena "
                                    "(usa `events append` para escribir)"))
    return findings


def verify_append_only(git_root: Path | str, rel: str) -> list[Finding]:
    """Cada versión histórica del ledger debe ser prefijo de la siguiente."""
    git_root = Path(git_root)
    try:
        proc = subprocess.run(
            ["git", "-C", str(git_root), "rev-list", "--reverse", "HEAD", "--", rel],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return [Finding("EVT-08", "info", rel,
                        f"historia no verificable (git no disponible o sin commits): {e}")]
    shas = [s for s in proc.stdout.split() if s]
    versions: list[list[str]] = []
    for sha in shas:
        # Salida en BYTES + decode UTF-8 explícito: no delegar al locale, que en
        # Windows es cp1252 y corrompería '∅'/'→'/acentos → falso EVT-07.
        show = subprocess.run(
            ["git", "-C", str(git_root), "show", f"{sha}:{rel}"],
            capture_output=True,
        )
        if show.returncode != 0:
            continue  # el archivo no existía en ese commit (borrado/renombrado)
        content = show.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
        versions.append([l for l in content.split("\n") if l.strip()])
    current = _read_lines(git_root / rel) if (git_root / rel).is_file() else []
    versions.append(current)
    findings: list[Finding] = []
    for a, b in zip(versions, versions[1:]):
        if b[: len(a)] != a:
            # localizar la primera divergencia para el reporte
            idx = next((j for j, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
            findings.append(Finding(
                "EVT-07", "error", rel,
                f"historia NO append-only: la línea {idx + 1} fue reescrita o eliminada "
                f"entre versiones ({len(a)} → {len(b)} líneas)"))
            break
    return findings


def append_line(path: Path | str, evento: dict) -> str:
    """Valida y añade un evento con hash-chain. Devuelve la línea escrita."""
    path = Path(path)
    missing = [k for k in REQUIRED_KEYS if k not in evento]
    if missing:
        raise EventError(f"evento incompleto, faltan: {', '.join(missing)}")
    if not is_iso_date(evento["ts"]):
        raise EventError(f"ts no es fecha ISO: {evento['ts']!r}")
    if evento["status"] not in VALID_STATUS:
        raise EventError(f"status inválido: {evento['status']!r}")
    lines = _read_lines(path) if path.is_file() else []
    ev = dict(evento)
    if lines:
        ev["prev"] = _sha(lines[-1])
    ordered = {k: ev[k] for k in KEY_ORDER if k in ev}
    for k in sorted(ev):
        if k not in ordered:
            ordered[k] = ev[k]
    line = json.dumps(ordered, ensure_ascii=False, separators=(",", ":"))
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    return line
