"""Hash de estado determinista del vault.

sha256 sobre líneas `<ruta-posix> <sha256(contenido LF-normalizado)>\n`
ordenadas por ruta. Igual en Windows (CRLF) y Linux (LF): la normalización
de saltos hace al hash portable entre árbol de trabajo y CI.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

SCOPES = {
    "genome": (["genome"], []),
    "knowledge": (["wiki"], ["index.md"]),
    "all": (["genome", "wiki", "onboard"], ["index.md", "CLAUDE.md", "AGENTS.md"]),
}


def _norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def file_hash(path: Path) -> str:
    return hashlib.sha256(_norm(path.read_bytes())).hexdigest()


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
        lines.append(f"{rel} {file_hash(p)}\n")
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def manifest_lines(root: Path | str, scope: str = "genome") -> str:
    """El detalle por archivo (para inspección y actas de corrida)."""
    root = Path(root)
    return "".join(
        f"{p.relative_to(root).as_posix()} {file_hash(p)}\n" for p in _collect(root, scope)
    )
