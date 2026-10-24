"""`init`: deja `onboard/company.yaml` listo con el perfil de instalación fijado (Fase 4.2).

Es el primer paso mecánico de una instalación: parte del ejemplo (`company.example.yaml`)
o de un blueprint de sector (`onboard/blueprints/<sector>.yaml`), fija `profile:` con la
misma edición textual de gen-perfiles (`profile.edit_manifest_text`) y NO toca nada más.
Los placeholders `<...>` de un blueprint se conservan tal cual: rellenarlos es del
operador (o de la entrevista de ONBOARD), y `onboard apply` los rechaza si siguen ahí.

Garantías: idempotente (re-correr sobre su propio resultado no cambia bytes ni falla);
no pisa un manifiesto distinto sin `force`; no escribe nada si algo falla.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path

from . import manifest as mf
from . import miniyaml
from . import profile as profile_mod
from . import schema

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent.parent
EJEMPLO_REL = "onboard/company.example.yaml"
BLUEPRINTS_REL = "onboard/blueprints"
DESTINO_REL = "onboard/company.yaml"


class InitError(ValueError):
    pass


@dataclass
class InitResult:
    manifest_path: Path
    source: Path
    profile: str
    blueprint: str | None
    written: bool            # False ⇒ ya existía idéntico (idempotencia)
    placeholders: bool       # el resultado conserva `<...>` por rellenar
    next_steps: list[str] = field(default_factory=list)


# ── fuentes ──────────────────────────────────────────────────────────────────

def _first_existing(*candidates: Path) -> Path | None:
    for c in candidates:
        if c.is_file():
            return c
    return None


def list_blueprints(root: Path | str) -> list[str]:
    """Sectores disponibles: los del vault y, si no tiene, los del template."""
    for base in (Path(root) / BLUEPRINTS_REL, TEMPLATE_ROOT / BLUEPRINTS_REL):
        if base.is_dir():
            nombres = sorted(p.stem for p in base.glob("*.yaml") if p.name != "catalog.yaml")
            if nombres:
                return nombres
    return []


def source_for(root: Path | str, blueprint: str | None) -> Path:
    """Ruta de la fuente: blueprint del sector o el ejemplo. Vault primero, template después."""
    root = Path(root)
    if blueprint is None:
        src = _first_existing(root / EJEMPLO_REL, TEMPLATE_ROOT / EJEMPLO_REL)
        if src is None:
            raise InitError(f"no encuentro {EJEMPLO_REL} ni en el vault ni en el template")
        return src
    nombre = blueprint[:-5] if blueprint.endswith(".yaml") else blueprint
    if nombre == "catalog":
        raise InitError("catalog.yaml es el índice de blueprints, no un blueprint: elige un sector "
                        f"({', '.join(list_blueprints(root)) or 'ninguno'})")
    src = _first_existing(root / BLUEPRINTS_REL / f"{nombre}.yaml",
                          TEMPLATE_ROOT / BLUEPRINTS_REL / f"{nombre}.yaml")
    if src is None:
        disponibles = ", ".join(list_blueprints(root)) or "(ninguno)"
        raise InitError(f"blueprint desconocido: {blueprint!r}. Disponibles: {disponibles}")
    return src


# ── render ───────────────────────────────────────────────────────────────────

def render(source_text: str, profile: str) -> str:
    """Texto final del manifiesto: la fuente con `profile:` fijado y nada más tocado."""
    if profile not in schema.PROFILES:
        raise InitError(f"perfil desconocido: {profile!r} (∈ {list(schema.PROFILE_ORDER)})")
    raw = miniyaml.parse(source_text) or {}
    if raw.get("profile") == profile:
        return source_text          # ya lo declara: ni un byte distinto (idempotencia)
    try:
        return profile_mod.edit_manifest_text(source_text, profile=profile)
    except profile_mod.ProfileError as e:
        raise InitError(str(e)) from e


def _next_steps(root: Path, profile: str, placeholders: bool, date: str) -> list[str]:
    caps = schema.PROFILES[profile]
    apagadas = [c for c in schema.CAPABILITY_ORDER if c not in caps]
    pasos: list[str] = []
    if placeholders:
        pasos.append(f"Edita {DESTINO_REL}: reemplaza cada placeholder `<...>` por tus datos "
                     "(onboard apply los rechaza si siguen ahí).")
    else:
        pasos.append(f"Revisa {DESTINO_REL}: nombre, sector, entidades, glosario y seed_genes "
                     "son los del ejemplo; ajústalos a tu empresa.")
    if apagadas:
        pasos.append(f"Perfil `{profile}` deja apagadas: {', '.join(apagadas)}. Para encender "
                     "una aparte: python tools/cerebro.py profile enable <capacidad>.")
    pasos.append(f"Aplica el manifiesto (mecánico, reproducible): "
                 f"python tools/cerebro.py onboard apply --date {date}")
    pasos.append("Comprueba: python tools/cerebro.py profile  ·  python tools/cerebro.py verify")
    pasos.append("Abre la carpeta con tu agente (Claude Code lee CLAUDE.md; Codex/Cursor, "
                 "AGENTS.md) y opera: ONBOARD ya aplicado → suelta fuentes en raw/ → BULK INGEST → QUERY.")
    return pasos


# ── operación ────────────────────────────────────────────────────────────────

def run(root: Path | str, *, profile: str, blueprint: str | None = None,
        force: bool = False, date: str | None = None) -> InitResult:
    root = Path(root)
    if profile not in schema.PROFILES:
        raise InitError(f"perfil desconocido: {profile!r} (∈ {list(schema.PROFILE_ORDER)})")
    date = date or datetime.date.today().isoformat()
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise InitError(f"fecha inválida (YYYY-MM-DD): {date!r}")
    src = source_for(root, blueprint)
    texto = render(src.read_text(encoding="utf-8"), profile)
    m = mf.Manifest(raw=miniyaml.parse(texto) or {}, path=str(src))
    errs = mf.validate(m)
    if errs:
        raise InitError(f"la fuente {src} no produce un manifiesto válido:\n  - "
                        + "\n  - ".join(errs))
    placeholders = mf.has_placeholders(m)
    destino = root / DESTINO_REL
    written = True
    if destino.is_file():
        actual = destino.read_text(encoding="utf-8")
        if actual == texto:
            written = False
        elif not force:
            raise InitError(
                f"ya existe {destino} y difiere de lo que init escribiría. No lo piso: "
                "revísalo (python tools/cerebro.py profile) o re-corre init con --force "
                "para reemplazarlo.")
    if written:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8", newline="")
    nombre_bp = (blueprint[:-5] if blueprint and blueprint.endswith(".yaml") else blueprint)
    return InitResult(manifest_path=destino, source=src, profile=profile,
                      blueprint=nombre_bp, written=written, placeholders=placeholders,
                      next_steps=_next_steps(root, profile, placeholders, date))
