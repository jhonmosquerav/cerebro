"""Parser de un subconjunto YAML estricto.

CEREBRO define su frontmatter y su manifiesto como ESTE subconjunto: mapas
anidados por indentación de espacios, listas block (`- item`), colecciones
flow (`[a, b]`, `{k: v}`), escalares simples, bloques `|`/`>` de indentación
uniforme (los usan las reglas de los blueprints) y comentarios. Todo lo demás
(anclas, tags, multidocumento, tabs) se rechaza con error ruidoso y número de
línea — que el estado sea validable mecánicamente es un rasgo del sistema,
no una limitación del parser.
"""
from __future__ import annotations

import re

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")


class MiniYamlError(ValueError):
    """Error de parseo con número de línea (1-indexado)."""

    def __init__(self, msg: str, line: int):
        super().__init__(f"línea {line}: {msg}")
        self.msg = msg
        self.line = line


class _Tok:
    __slots__ = ("indent", "text", "line", "block_key", "block_value")

    def __init__(self, indent: int, text: str, line: int,
                 block_key: str | None = None, block_value: str | None = None):
        self.indent = indent
        self.text = text
        self.line = line
        # Para bloques `clave: >` / `clave: |`, el valor ya viene plegado.
        self.block_key = block_key
        self.block_value = block_value


def _strip_comment(line: str, lineno: int) -> str:
    """Quita el comentario `#` respetando comillas. `#` pegado a texto no corta."""
    out = []
    in_s = in_d = False
    prev = ""
    for ch in line:
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "#" and not in_s and not in_d and (prev == "" or prev in " \t"):
            break
        out.append(ch)
        prev = ch
    if in_s or in_d:
        raise MiniYamlError("comilla sin cerrar", lineno)
    return "".join(out).rstrip()


_BLOCK_HEADER_RE = re.compile(r"^([|>])([+-]?)$")


def _indent_of(line: str, lineno: int) -> int:
    indent = 0
    for ch in line:
        if ch == " ":
            indent += 1
        elif ch == "\t":
            raise MiniYamlError("indentación con tabs no soportada", lineno)
        else:
            break
    return indent


def _fold_block(block_lines: list[str], style: str, chomp: str, lineno: int) -> str:
    """Pliega un bloque `|`/`>` de indentación uniforme (subconjunto)."""
    while block_lines and block_lines[-1].strip() == "":
        block_lines.pop()
    non_blank = [l for l in block_lines if l.strip()]
    if not non_blank:
        return ""
    common = min(_indent_of(l, lineno) for l in non_blank)
    stripped = [l[common:] if l.strip() else "" for l in block_lines]
    if style == "|":
        text = "\n".join(stripped)
    else:  # ">" plegado: no-blancas consecutivas se unen con espacio; blanca = \n
        parts: list[str] = []
        for l in stripped:
            if not l:
                parts.append("\n")
            elif parts and parts[-1] not in ("", "\n"):
                parts.append(" " + l)
            else:
                parts.append(l)
        text = "".join(parts)
    if chomp == "-":
        return text
    return text + "\n"


def _tokenize(text: str) -> list[_Tok]:
    toks: list[_Tok] = []
    lines = text.split("\n")
    i_raw = 0
    while i_raw < len(lines):
        lineno = i_raw + 1
        line = lines[i_raw].rstrip("\r")
        stripped_full = line.strip()
        if not stripped_full or stripped_full.startswith("#"):
            i_raw += 1
            continue
        if stripped_full == "---" or stripped_full == "...":
            raise MiniYamlError("multidocumento no soportado ('---' interno)", lineno)
        indent = _indent_of(line, lineno)
        content = _strip_comment(line[indent:], lineno)
        if not content:
            i_raw += 1
            continue
        # ¿Encabezado de bloque `clave: >` / `clave: |`? El contenido del bloque
        # se captura CRUDO (un `#` o una comilla suelta ahí es contenido, no sintaxis).
        # No se soporta directamente en ítems de lista (`- clave: >`), sí en sus
        # líneas de continuación — que es como lo usan los blueprints.
        block = None
        if not content.startswith("- "):
            try:
                key, rest = _split_key(content, lineno)
                m = _BLOCK_HEADER_RE.match(rest) if rest else None
                if m:
                    block = (key, m.group(1), m.group(2))
            except MiniYamlError:
                pass
        if block:
            key, style, chomp = block
            j = i_raw + 1
            block_lines: list[str] = []
            while j < len(lines):
                raw2 = lines[j].rstrip("\r")
                if raw2.strip() == "":
                    block_lines.append("")
                    j += 1
                    continue
                if _indent_of(raw2, j + 1) <= indent:
                    break
                block_lines.append(raw2)
                j += 1
            value = _fold_block(block_lines, style, chomp, lineno)
            toks.append(_Tok(indent, content, lineno, block_key=key, block_value=value))
            i_raw = j
            continue
        toks.append(_Tok(indent, content, lineno))
        i_raw += 1
    return toks


def _split_flow(text: str, lineno: int) -> list[str]:
    """Divide por comas de primer nivel respetando comillas y anidación."""
    parts: list[str] = []
    depth = 0
    in_s = in_d = False
    cur = []
    for ch in text:
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif not in_s and not in_d:
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append("".join(cur))
                cur = []
                continue
        cur.append(ch)
    if cur or parts:
        parts.append("".join(cur))
    return parts


def _parse_scalar(text: str, lineno: int):
    text = text.strip()
    if text == "":
        return None
    first = text[0]
    if first in "&*":
        raise MiniYamlError("anclas/alias YAML no soportados", lineno)
    if text.startswith("!!") or first == "!":
        raise MiniYamlError("tags YAML no soportados", lineno)
    if first in "|>":
        raise MiniYamlError(
            "indicador de bloque con texto en la misma línea (usa `clave: >` y el texto indentado debajo)",
            lineno,
        )
    if first == '"':
        if len(text) < 2 or not text.endswith('"') or text.endswith('\\"'):
            raise MiniYamlError("comilla doble sin cerrar", lineno)
        return text[1:-1]
    if first == "'":
        if len(text) < 2 or not text.endswith("'"):
            raise MiniYamlError("comilla simple sin cerrar", lineno)
        return text[1:-1]
    if first == "[":
        if not text.endswith("]"):
            raise MiniYamlError("lista flow sin cerrar", lineno)
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(p, lineno) for p in _split_flow(inner, lineno)]
    if first == "{":
        if not text.endswith("}"):
            raise MiniYamlError("mapa flow sin cerrar", lineno)
        inner = text[1:-1].strip()
        result: dict = {}
        if not inner:
            return result
        for pair in _split_flow(inner, lineno):
            key, val = _split_key(pair.strip(), lineno)
            if key in result:
                raise MiniYamlError(f"clave duplicada '{key}'", lineno)
            result[key] = _parse_scalar(val, lineno) if val else None
        return result
    if text == "null" or text == "~":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if _INT_RE.match(text):
        return int(text)
    if _FLOAT_RE.match(text):
        return float(text)
    return text


def _split_key(text: str, lineno: int) -> tuple[str, str]:
    """Divide `clave: valor` en la primera `:` fuera de comillas.

    Devuelve (clave, resto); resto puede ser "".
    """
    in_s = in_d = False
    for i, ch in enumerate(text):
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == ":" and not in_s and not in_d:
            after = text[i + 1 :]
            if after == "" or after.startswith(" "):
                key = text[:i].strip()
                if (key.startswith('"') and key.endswith('"')) or (
                    key.startswith("'") and key.endswith("'")
                ):
                    key = key[1:-1]
                if not key:
                    raise MiniYamlError("clave vacía", lineno)
                return key, after.strip()
    raise MiniYamlError(f"se esperaba 'clave: valor' y se encontró: {text!r}", lineno)


def _parse_map(toks: list[_Tok], i: int, indent: int) -> tuple[dict, int]:
    result: dict = {}
    while i < len(toks) and toks[i].indent == indent:
        tok = toks[i]
        if tok.text.startswith("- ") or tok.text == "-":
            break
        if tok.block_key is not None:
            if tok.block_key in result:
                raise MiniYamlError(f"clave duplicada '{tok.block_key}'", tok.line)
            result[tok.block_key] = tok.block_value
            i += 1
            continue
        key, rest = _split_key(tok.text, tok.line)
        if key in result:
            raise MiniYamlError(f"clave duplicada '{key}'", tok.line)
        if rest:
            result[key] = _parse_scalar(rest, tok.line)
            i += 1
        else:
            i += 1
            if i < len(toks) and toks[i].indent > indent:
                value, i = _parse_block(toks, i, toks[i].indent)
                result[key] = value
            elif i < len(toks) and toks[i].indent == indent and (
                toks[i].text.startswith("- ") or toks[i].text == "-"
            ):
                value, i = _parse_list(toks, i, indent)
                result[key] = value
            else:
                result[key] = None
    if i < len(toks) and toks[i].indent > indent:
        raise MiniYamlError("indentación inconsistente", toks[i].line)
    return result, i


def _parse_list(toks: list[_Tok], i: int, indent: int) -> tuple[list, int]:
    result: list = []
    while i < len(toks) and toks[i].indent == indent and (
        toks[i].text.startswith("- ") or toks[i].text == "-"
    ):
        tok = toks[i]
        rest = tok.text[2:].strip() if tok.text.startswith("- ") else ""
        item_indent = indent + 2
        if not rest:
            i += 1
            if i < len(toks) and toks[i].indent > indent:
                value, i = _parse_block(toks, i, toks[i].indent)
                result.append(value)
            else:
                result.append(None)
            continue
        # ¿El ítem es un `clave: valor` (mapa) o un escalar?
        try:
            key, val = _split_key(rest, tok.line)
            is_map = True
        except MiniYamlError:
            is_map = False
        if is_map and not rest.startswith(("[", "{", '"', "'")):
            sub = [_Tok(item_indent, rest, tok.line)]
            i += 1
            while i < len(toks) and toks[i].indent >= item_indent and not (
                toks[i].indent == indent and (toks[i].text.startswith("- ") or toks[i].text == "-")
            ):
                if toks[i].indent < item_indent:
                    raise MiniYamlError("indentación inconsistente en ítem de lista", toks[i].line)
                sub.append(toks[i])
                i += 1
            value, j = _parse_map(sub, 0, item_indent)
            if j != len(sub):
                raise MiniYamlError("estructura inesperada en ítem de lista", sub[j].line)
            result.append(value)
        else:
            result.append(_parse_scalar(rest, tok.line))
            i += 1
    return result, i


def _parse_block(toks: list[_Tok], i: int, indent: int):
    if toks[i].text.startswith("- ") or toks[i].text == "-":
        return _parse_list(toks, i, indent)
    return _parse_map(toks, i, indent)


def parse(text: str) -> dict:
    """Parsea el subconjunto y devuelve un dict (vacío si no hay contenido)."""
    toks = _tokenize(text)
    if not toks:
        return {}
    base = toks[0].indent
    if toks[0].text.startswith("- ") or toks[0].text == "-":
        raise MiniYamlError("el nivel superior debe ser un mapa", toks[0].line)
    result, i = _parse_map(toks, 0, base)
    if i != len(toks):
        raise MiniYamlError("indentación inconsistente", toks[i].line)
    return result
