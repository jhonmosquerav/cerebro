"""Perfiles de instalación y capacidades activables (gen-perfiles v1).

Una capacidad es un conjunto coherente de genes, operaciones, comandos y carpetas que
se puede apagar sin romper el núcleo. Un perfil es un preset de capacidades. Ambos se
declaran en el manifiesto (`profile:` / `capabilities:`), ONBOARD los aplica y el estado
efectivo queda en `genome/perfil.md`: frontmatter PLANO (`cap_<nombre>: true|false`)
para que lo lean el agente, los hooks POSIX (`grep`) y Obsidian (propiedades tipadas).

Ausencia de declaración ⇒ `completo` (todo activo) y NO se escribe archivo: los vaults
y los casos `worked/` anteriores a este gen conservan su hash.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import fm as fm_mod
from . import schema

PERFIL_REL = "genome/perfil.md"
EVENT_TYPE = "profile_applied"

_PROFILE_LINE_RE = re.compile(r"^profile:(.*)$")
_CAPS_LINE_RE = re.compile(r"^capabilities:(.*)$")
_COMMENT_RE = re.compile(r"\s(#.*)$")


class ProfileError(ValueError):
    pass


# ── estado efectivo ──────────────────────────────────────────────────────────

def declares(m) -> bool:
    """True si el manifiesto declara `profile` o `capabilities` (aunque sea vacío)."""
    raw = m.raw if hasattr(m, "raw") else (m or {})
    return "profile" in raw or "capabilities" in raw


def effective(m) -> dict[str, bool]:
    """Capacidades efectivas: preset del perfil + overrides, en orden canónico."""
    raw = m.raw if hasattr(m, "raw") else (m or {})
    perfil = raw.get("profile") or schema.DEFAULT_PROFILE
    if perfil not in schema.PROFILES:
        raise ProfileError(f"perfil desconocido: {perfil!r} (∈ {list(schema.PROFILE_ORDER)})")
    preset = set(schema.PROFILES[perfil])
    overrides = raw.get("capabilities") or {}
    if not isinstance(overrides, dict):
        raise ProfileError("capabilities debe ser mapa capacidad→booleano")
    out: dict[str, bool] = {}
    for cap in schema.CAPABILITY_ORDER:
        valor = overrides.get(cap)
        out[cap] = bool(valor) if isinstance(valor, bool) else (cap in preset)
    return out


def profile_name(m) -> str:
    raw = m.raw if hasattr(m, "raw") else (m or {})
    return raw.get("profile") or schema.DEFAULT_PROFILE


def overrides_of(m) -> dict[str, bool]:
    """Solo los overrides que difieren del preset (los redundantes no cuentan)."""
    raw = m.raw if hasattr(m, "raw") else (m or {})
    preset = set(schema.PROFILES.get(profile_name(m), ()))
    decl = raw.get("capabilities") or {}
    out = {}
    if isinstance(decl, dict):
        for cap in schema.CAPABILITY_ORDER:
            v = decl.get(cap)
            if isinstance(v, bool) and v != (cap in preset):
                out[cap] = v
    return out


# ── render de genome/perfil.md ───────────────────────────────────────────────

def render(m, date: str) -> str:
    caps = effective(m)
    perfil = profile_name(m)
    activas = [c for c in schema.CAPABILITY_ORDER if caps[c]]
    apagadas = [c for c in schema.CAPABILITY_ORDER if not caps[c]]
    fm_lines = ["---", "title: Perfil de instalación", "type: meta", f"perfil: {perfil}"]
    for cap in schema.CAPABILITY_ORDER:
        fm_lines.append(f"cap_{cap}: {'true' if caps[cap] else 'false'}")
    fm_lines += [f"updated: {date}", "---"]
    filas = []
    for cap in schema.CAPABILITY_ORDER:
        d = schema.CAPABILITIES[cap]
        estado = "**activa**" if caps[cap] else "apagada"
        ops = ", ".join(d["operaciones"] + [f"`{c}`" for c in d["comandos"]]) or "—"
        filas.append(
            f"| `{cap}` | {estado} | {', '.join(d['genes'])} | {ops} | "
            f"{', '.join(f'`{p}`' for p in d['carpetas'])} |")
    cuerpo = "\n".join([
        "",
        "# Perfil de instalación",
        "",
        f"> Generado mecánicamente por ONBOARD desde `onboard/company.yaml` el {date}.",
        "> Mismo manifiesto → mismo perfil. No editar a mano: cambia `profile:` /",
        "> `capabilities:` en el manifiesto (o usa `python tools/cerebro.py profile set|enable|disable`)",
        "> y re-corre `onboard apply`. Regla: gen-perfiles (`genome/genes/gen-perfiles.md`).",
        "",
        f"Perfil **{perfil}** · activas: {', '.join(activas) or '—'} · "
        f"apagadas: {', '.join(apagadas) or '—'}.",
        "",
        "## Capacidades",
        "",
        "| Capacidad | Estado | Genes | Operaciones / comandos | Carpetas |",
        "|---|---|---|---|---|",
        *filas,
        "",
        "## Qué significa \"apagada\"",
        "",
        "- La operación **no se ejecuta**: el agente lo declara y propone activarla por manifiesto.",
        "- Sus genes siguen en `genome/genes/` con su `status` intacto, pero no rigen; los comandos",
        "  de `tools/` que dependen de ella avisan y terminan con exit 2 (`--ignore-profile` fuerza).",
        "- Con `cap_memoria: false` los hooks PreCompact/Stop son no-op y CHECKPOINT no se exige.",
        "- **Nada se borra**: apagar no es destruir. El núcleo (compuerta, ledger, confidencialidad,",
        "  anti-inyección, INGEST, QUERY, LINT, ONBOARD) no se puede apagar.",
        "",
    ])
    return "\n".join(fm_lines) + "\n" + cuerpo


# ── lectura del estado aplicado ──────────────────────────────────────────────

def parse_applied(text: str) -> tuple[str | None, dict[str, bool]]:
    """(perfil, capacidades) desde el frontmatter de genome/perfil.md.

    Lanza ProfileError si el archivo no parsea o le faltan capacidades.
    """
    meta, _body, errors = fm_mod.split(text)
    if meta is None:
        raise ProfileError(errors[0] if errors else "sin frontmatter")
    caps: dict[str, bool] = {}
    for cap in schema.CAPABILITY_ORDER:
        v = meta.get(f"cap_{cap}")
        if not isinstance(v, bool):
            raise ProfileError(f"cap_{cap} ausente o no booleano en {PERFIL_REL}")
        caps[cap] = v
    perfil = meta.get("perfil")
    return (perfil if isinstance(perfil, str) else None), caps


def read_applied(root: Path | str) -> tuple[str | None, dict[str, bool]] | None:
    """None si no existe genome/perfil.md (⇒ completo). ProfileError si está corrupto."""
    p = Path(root) / PERFIL_REL
    if not p.is_file():
        return None
    return parse_applied(p.read_text(encoding="utf-8"))


def is_on(root: Path | str, cap: str) -> bool:
    """¿Está activa la capacidad en el vault? Sin archivo ⇒ sí (completo).

    Un archivo corrupto cuenta como "todo activo": apagar por accidente una operación
    sería peor que dejarla correr; LINT (PRF-01) es quien delata la corrupción.
    """
    if cap not in schema.CAPABILITIES:
        raise ProfileError(f"capacidad desconocida: {cap!r} (∈ {list(schema.CAPABILITY_ORDER)})")
    try:
        applied = read_applied(root)
    except ProfileError:
        return True
    if applied is None:
        return True
    return applied[1][cap]


# ── edición textual del manifiesto (solo profile:/capabilities:) ─────────────

def _render_caps_block(overrides: dict[str, bool], comentario: str = "") -> list[str]:
    sufijo = f"   {comentario}" if comentario else ""
    if not overrides:
        return [f"capabilities: {{}}{sufijo}"]
    lines = [f"capabilities:{sufijo}"]
    for cap in schema.CAPABILITY_ORDER:
        if cap in overrides:
            lines.append(f"  {cap}: {'true' if overrides[cap] else 'false'}")
    return lines


def _block_end(lines: list[str], start: int) -> int:
    """Fin (exclusivo) del bloque YAML que empieza en `start`: hijos indentados."""
    i = start + 1
    while i < len(lines):
        l = lines[i]
        if l.strip() == "" or l.startswith((" ", "\t")):
            # una línea en blanco solo pertenece al bloque si después sigue un hijo
            if l.strip() == "":
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines) and lines[j].startswith((" ", "\t")):
                    i = j
                    continue
                break
            i += 1
            continue
        break
    return i


def edit_manifest_text(text: str, *, profile: str | None = None,
                       enable: str | None = None, disable: str | None = None) -> str:
    """Devuelve el manifiesto con `profile:`/`capabilities:` actualizados y el resto intacto.

    Los overrides redundantes (iguales al preset del perfil resultante) se eliminan: el
    manifiesto queda mínimo y legible. Comentarios al final de las líneas `profile:` y
    `capabilities:` se conservan.
    """
    from . import miniyaml
    if profile is not None and profile not in schema.PROFILES:
        raise ProfileError(f"perfil desconocido: {profile!r} (∈ {list(schema.PROFILE_ORDER)})")
    for cap in (enable, disable):
        if cap is not None and cap not in schema.CAPABILITIES:
            raise ProfileError(
                f"capacidad desconocida: {cap!r} (∈ {list(schema.CAPABILITY_ORDER)})")
    raw = miniyaml.parse(text) or {}
    perfil_actual = raw.get("profile") or schema.DEFAULT_PROFILE
    if perfil_actual not in schema.PROFILES:
        raise ProfileError(f"el manifiesto declara un perfil desconocido: {perfil_actual!r}")
    nuevo_perfil = profile or perfil_actual
    decl = raw.get("capabilities") or {}
    overrides = {c: v for c, v in decl.items() if isinstance(v, bool)} if isinstance(decl, dict) else {}
    if enable:
        overrides[enable] = True
    if disable:
        overrides[disable] = False
    preset = set(schema.PROFILES[nuevo_perfil])
    overrides = {c: v for c, v in overrides.items()
                 if c in schema.CAPABILITIES and v != (c in preset)}

    crlf = "\r\n" in text
    lines = text.replace("\r\n", "\n").split("\n")
    # localizar líneas existentes (nivel raíz, sin indentación)
    i_prof = next((i for i, l in enumerate(lines) if _PROFILE_LINE_RE.match(l)), None)
    i_caps = next((i for i, l in enumerate(lines) if _CAPS_LINE_RE.match(l)), None)
    com_prof = com_caps = ""
    if i_prof is not None:
        m = _COMMENT_RE.search(lines[i_prof])
        com_prof = m.group(1) if m else ""
    if i_caps is not None:
        m = _COMMENT_RE.search(lines[i_caps])
        com_caps = m.group(1) if m else ""
    linea_prof = f"profile: {nuevo_perfil}" + (f"   {com_prof}" if com_prof else "")
    bloque_caps = _render_caps_block(overrides, com_caps)

    # 1) capabilities (se edita primero para no desplazar i_prof si está antes)
    if i_caps is not None:
        fin = _block_end(lines, i_caps)
        lines[i_caps:fin] = bloque_caps
        if i_prof is not None and i_prof > i_caps:
            i_prof += len(bloque_caps) - (fin - i_caps)
    # 2) profile
    if i_prof is not None:
        lines[i_prof] = linea_prof
    else:
        if i_caps is not None:
            lines[i_caps:i_caps] = [linea_prof]
            i_caps += 1
        else:
            while lines and lines[-1].strip() == "":
                lines.pop()
            lines += ["", "# Perfil de instalación (gen-perfiles): preset de capacidades + overrides.",
                      linea_prof]
    if i_caps is None:
        # insertar justo después de la línea profile (ya garantizada)
        i_prof = next(i for i, l in enumerate(lines) if _PROFILE_LINE_RE.match(l))
        lines[i_prof + 1:i_prof + 1] = bloque_caps
    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    return out.replace("\n", "\r\n") if crlf else out
