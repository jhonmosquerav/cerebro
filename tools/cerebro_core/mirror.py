"""Verificador del espejo AGENTS.md ≡ CLAUDE.md (backlog C-02)."""
from __future__ import annotations

import hashlib
from pathlib import Path


def _norm_bytes(path: Path) -> bytes | None:
    if not path.is_file():
        return None
    return path.read_bytes().replace(b"\r\n", b"\n")


def check(root: Path | str) -> str | None:
    """None si el espejo está en verde; mensaje de error si no."""
    root = Path(root)
    claude = _norm_bytes(root / "CLAUDE.md")
    agents = _norm_bytes(root / "AGENTS.md")
    if claude is None:
        return "CLAUDE.md no existe"
    if agents is None:
        return "AGENTS.md no existe (espejo roto)"
    if claude != agents:
        h1 = hashlib.sha256(claude).hexdigest()[:12]
        h2 = hashlib.sha256(agents).hexdigest()[:12]
        return (
            f"AGENTS.md ≠ CLAUDE.md (sha256 {h2}… vs {h1}…): "
            "re-sincroniza con `python tools/cerebro.py mirror --fix`"
        )
    return None


def fix(root: Path | str) -> None:
    """Copia CLAUDE.md → AGENTS.md (CLAUDE.md es la fuente, regla de la casa)."""
    root = Path(root)
    (root / "AGENTS.md").write_bytes((root / "CLAUDE.md").read_bytes())
