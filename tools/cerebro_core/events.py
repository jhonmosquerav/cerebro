"""Integridad del ledger `genome/events.jsonl` (backlog C-03).

Tres garantías mecánicas:
1. **Esquema por línea** — cada evento parsea y trae las claves canónicas.
2. **Hash-chain opcional** — toda línea escrita con `append_line` porta
   `prev` = sha256 de la línea anterior: adulterar el pasado rompe la cadena.
   Las líneas históricas sin `prev` siguen siendo válidas (migración honesta).
3. **Append-only contra git** — cada versión histórica del archivo debe ser
   prefijo de la siguiente; reescrituras del pasado quedan delatadas.
4. **Aprobador con dueño (C-04, ATR-01)** — desde la primera línea con identidad
   real, un `approved_by` genérico es error (EVT-09) salvo que lo cure un evento
   `attribution_corrected` posterior cuyo `corrects` lleve el sha256 de esa línea
   (EVT-10 valida su forma). Las líneas previas a la primera atribución son
   historia válida, igual que las previas a la hash-chain.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from .findings import Finding
from .identity import is_generic
from .schema import is_iso_date

REQUIRED_KEYS = ("ts", "type", "target", "signal", "diff", "approved_by", "status")
VALID_STATUS = {"applied", "proposed", "reverted", "pending"}
CORRECTION_TYPE = "attribution_corrected"
# Orden canónico de claves al escribir (las históricas usan este mismo orden).
KEY_ORDER = ("ts", "type", "target", "signal", "diff", "approved_by", "status",
             "corrects", "incident_ref", "prev")
_SHA_RE = re.compile(r"[0-9a-f]{64}")


class EventError(ValueError):
    pass


def _sha(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def _read_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return [l for l in text.split("\n") if l.strip()]


def _parse(line: str) -> dict | None:
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        return None
    return ev if isinstance(ev, dict) else None


def _attributed(ev: dict | None) -> bool:
    return bool(ev) and "approved_by" in ev and not is_generic(ev["approved_by"])


def attribution_started(path: Path | str) -> bool:
    """True si el ledger ya tiene una línea con aprobador real (desde ahí rige EVT-09)."""
    path = Path(path)
    return path.is_file() and any(_attributed(_parse(l)) for l in _read_lines(path))


def _correction_problem(ev: dict, earlier_shas: set[str]) -> str | None:
    """Motivo por el que un `attribution_corrected` es inválido, o None si está bien."""
    if is_generic(ev.get("approved_by")):
        return "attribution_corrected con approved_by genérico: solo lo firma el aprobador real"
    corrects = ev.get("corrects")
    if not isinstance(corrects, list) or not corrects:
        return "attribution_corrected sin `corrects` (lista no vacía de sha256 de líneas previas)"
    for s in corrects:
        if not isinstance(s, str) or not _SHA_RE.fullmatch(s):
            return f"`corrects` lleva algo que no es un sha256: {str(s)[:20]!r}"
        if s not in earlier_shas:
            return f"`corrects` apunta a una línea que no existe antes de esta: {s[:12]}…"
    return None


def verify_file(path: Path | str) -> list[Finding]:
    path = Path(path)
    rel = path.name if not path.is_absolute() else "genome/events.jsonl"
    if not path.is_file():
        return [Finding("EVT-00", "error", rel, "el ledger no existe")]
    findings: list[Finding] = []
    lines = _read_lines(path)
    shas = [_sha(l) for l in lines]
    # Líneas curadas por un attribution_corrected bien formado (EVT-10 lo valida abajo).
    curadas: set[str] = set()
    for j, line in enumerate(lines):
        ev = _parse(line)
        if ev and ev.get("type") == CORRECTION_TYPE and \
                _correction_problem(ev, set(shas[:j])) is None:
            curadas.update(ev["corrects"])
    prev_ts = None
    chain_started = False
    attribution = False
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
        # atribución (C-04): monótona, como la cadena
        if ev.get("type") == CORRECTION_TYPE:
            problema = _correction_problem(ev, set(shas[: i - 1]))
            if problema:
                findings.append(Finding("EVT-10", "error", loc, problema))
        elif attribution and "approved_by" in ev and is_generic(ev["approved_by"]) \
                and str(ev["approved_by"]).strip() and shas[i - 1] not in curadas:
            findings.append(Finding(
                "EVT-09", "error", loc,
                f"approved_by genérico {ev['approved_by']!r} después de iniciada la "
                "atribución: cúralo con un evento attribution_corrected "
                "(gen-compuerta-mutacion)"))
        if _attributed(ev):
            attribution = True
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
    if not str(evento["approved_by"] or "").strip():
        raise EventError("approved_by vacío")
    lines = _read_lines(path) if path.is_file() else []
    if evento["type"] == CORRECTION_TYPE:
        problema = _correction_problem(evento, {_sha(l) for l in lines})
        if problema:
            raise EventError(problema)
    elif "corrects" in evento:
        raise EventError(f"`corrects` solo vale en eventos {CORRECTION_TYPE}")
    elif is_generic(evento["approved_by"]) and any(_attributed(_parse(l)) for l in lines):
        raise EventError(
            f"approved_by genérico {evento['approved_by']!r} en un ledger con atribución "
            "iniciada: pasa la identidad real del aprobador (gen-compuerta-mutacion, EVT-09)")
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
