"""Hash de estado determinista del vault.

sha256 sobre líneas `<ruta-posix> <sha256(contenido LF-normalizado)>\n`
ordenadas por ruta. Igual en Windows (CRLF) y Linux (LF): la normalización
de saltos hace al hash portable entre árbol de trabajo y CI.

El hash dice QUÉ contiene el vault, no QUIÉN lo aprobó: del ledger se excluyen
`approved_by` y `prev` (que se deriva de la línea anterior, aprobador incluido).
Así mismo manifiesto + misma fecha ⇒ mismo hash sea quien sea el operador. La
autoría la prueban la hash-chain (EVT-05/07) y la firma del commit, no este hash.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCOPES = {
    "genome": (["genome"], []),
    "knowledge": (["wiki"], ["index.md"]),
    "all": (["genome", "wiki", "onboard"], ["index.md", "CLAUDE.md", "AGENTS.md"]),
}
LEDGER_REL = "genome/events.jsonl"
PROVENANCE_KEYS = ("approved_by", "prev")


def _norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _strip_provenance(data: bytes) -> bytes:
    """Una línea que no es un objeto JSON se conserva tal cual: también cuenta."""
    out = []
    for raw in data.split(b"\n"):
        try:
            ev = json.loads(raw.decode("utf-8"))
        except ValueError:  # JSON inválido o bytes que no son UTF-8
            out.append(raw)
            continue
        if not isinstance(ev, dict):
            out.append(raw)
            continue
        estado = {k: v for k, v in ev.items() if k not in PROVENANCE_KEYS}
        out.append(json.dumps(estado, ensure_ascii=False, separators=(",", ":"))
                   .encode("utf-8", "surrogatepass"))
    return b"\n".join(out)


def file_hash(path: Path, rel: str | None = None) -> str:
    data = _norm(path.read_bytes())
    if rel == LEDGER_REL:
        data = _strip_provenance(data)
    return hashlib.sha256(data).hexdigest()


def _collect(root: Path, scope: str) -> list[Path]:
    if scope not in SCOPES:
        raise ValueError(f"scope desconocido: {scope!r} (∈ {sorted(SCOPES)})")
    dirs, files = SCOPES[scope]
    out: list[Path] = []
    for d in dirs:
        base = root / d
        if base.is_dir():
            out.extend(p for p in base.rglob("*") if p.is_file())
    for f in files:
        p = root / f
        if p.is_file():
            out.append(p)
    return sorted(out, key=lambda p: p.relative_to(root).as_posix())


def tree_hash(root: Path | str, scope: str = "genome") -> str:
    root = Path(root)
    lines = []
    for p in _collect(root, scope):
        rel = p.relative_to(root).as_posix()
        lines.append(f"{rel} {file_hash(p, rel)}\n")
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def manifest_lines(root: Path | str, scope: str = "genome") -> str:
    """El detalle por archivo (para inspección y actas de corrida)."""
    root = Path(root)
    return "".join(
        f"{rel} {file_hash(p, rel)}\n"
        for p in _collect(root, scope)
        for rel in [p.relative_to(root).as_posix()]
    )
