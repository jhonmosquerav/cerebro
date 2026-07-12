"""Extracción de frontmatter YAML y wikilinks de páginas markdown."""
from __future__ import annotations

import re

from . import miniyaml
from .miniyaml import MiniYamlError

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_CODE_SPAN_RE = re.compile(r"`[^`\n]*`")
_WIKILINK_RE = re.compile(r"\[\[([^\][|#]+)(?:[|#][^\]]*)?\]\]")


def split(text: str) -> tuple[dict | None, str, list[str]]:
    """Divide una página en (frontmatter, cuerpo, errores).

    - Sin frontmatter: (None, texto, []).
    - Frontmatter ilegible o sin cierre: (None, cuerpo-o-texto, [error]).
    Tolera BOM y CRLF.
    """
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return None, text, []
    for j in range(1, len(lines)):
        if lines[j].rstrip("\r") == "---":
            fm_text = "\n".join(l.rstrip("\r") for l in lines[1:j])
            body = "\n".join(lines[j + 1 :])
            try:
                meta = miniyaml.parse(fm_text)
            except MiniYamlError as e:
                return None, body, [f"frontmatter ilegible: {e}"]
            if not isinstance(meta, dict):
                return None, body, ["el frontmatter no es un mapa"]
            return meta, body, []
    return None, text, ["frontmatter sin cierre '---'"]


def wikilinks(body: str) -> list[str]:
    """Extrae destinos de [[wikilinks]] del cuerpo, en orden de aparición, sin duplicar.

    Ignora los que viven dentro de código (spans `...` y bloques ```...```).
    `[[Página|alias]]` y `[[Página#sección]]` resuelven a `Página`.
    """
    clean = _FENCE_RE.sub("", body)
    clean = _CODE_SPAN_RE.sub("", clean)
    seen: list[str] = []
    for m in _WIKILINK_RE.finditer(clean):
        target = m.group(1).strip()
        if target and target not in seen:
            seen.append(target)
    return seen
