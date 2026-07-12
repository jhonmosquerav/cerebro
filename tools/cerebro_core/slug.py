"""Slug determinista — algoritmo exacto de gen-identidad-de-pagina v2."""
from __future__ import annotations

import unicodedata

_ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789")


def slugify(text: str, fallback_hash: str = "") -> str:
    """minúsculas → sin diacríticos → [^a-z0-9]→'-' → colapsar → recortar →
    máx 60 (recorte de '-' final) → vacío ⇒ `f-<hash8>`."""
    s = unicodedata.normalize("NFD", text.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = "".join(c if c in _ALLOWED else "-" for c in s)
    while "--" in s:
        s = s.replace("--", "-")
    s = s.strip("-")
    if len(s) > 60:
        s = s[:60].rstrip("-")
    if not s:
        return f"f-{fallback_hash[:8]}" if fallback_hash else "f-"
    return s
