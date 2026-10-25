"""Identidad del aprobador para `approved_by` (C-04, gen-compuerta-mutacion v5, ATR-01).

Orden de resolución cuando no se pasa una identidad explícita:
1. La clave que va a firmar el commit (`user.signingkey` con `gpg.format = ssh`) buscada en
   `ops/allowed_signers`: su principal es la identidad. Así un vault clonado del template,
   que hereda la clave del autor del template, no le atribuye nada a quien no firma.
2. `git config user.email` del vault (con aviso si hay firmantes y no figura).
3. Nada: `IdentityError`. Jamás se cae a un genérico.
"""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

SIGNERS_REL = "ops/allowed_signers"
# Valores sin dueño: no identifican a nadie y C-04 los prohíbe desde la primera atribución.
GENERIC = frozenset({
    "", "user", "usuario", "operador", "operator", "admin", "administrador", "agent",
    "agente", "claude", "llm", "system", "sistema", "unknown", "desconocido", "n/a", "na",
    "-", "?",
})
_KEY_PREFIXES = ("ssh-", "ecdsa-", "sk-")


class IdentityError(ValueError):
    pass


@dataclass
class Identity:
    value: str
    source: str
    avisos: list[str] = field(default_factory=list)


def is_generic(value) -> bool:
    return str(value if value is not None else "").strip().lower() in GENERIC


def _key_of(tokens: list[str]) -> str | None:
    for i, tok in enumerate(tokens[:-1]):
        if tok.startswith(_KEY_PREFIXES):
            return tokens[i + 1]
    return None


def signers(vault: Path | str) -> list[tuple[list[str], str]]:
    """(principales, clave base64) de cada línea de `ops/allowed_signers`."""
    path = Path(vault) / SIGNERS_REL
    if not path.is_file():
        return []
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            tokens = shlex.split(line)
        except ValueError:
            continue
        key = _key_of(tokens)
        principals = [p for p in tokens[0].split(",") if p and "*" not in p]
        if key and principals:
            out.append((principals, key))
    return out


def _git_getter(vault: Path) -> Callable[[str], str | None]:
    def get(clave: str) -> str | None:
        try:
            proc = subprocess.run(["git", "-C", str(vault), "config", "--get", clave],
                                  capture_output=True, text=True, encoding="utf-8")
        except FileNotFoundError:
            return None
        if proc.returncode != 0:
            return None
        return proc.stdout.strip() or None
    return get


def signing_key(vault: Path, git: Callable[[str], str | None]) -> str | None:
    """Clave pública base64 con la que se firmará, o None si no es SSH o no se puede leer."""
    if (git("gpg.format") or "").strip().lower() != "ssh":
        return None
    valor = (git("user.signingkey") or "").strip()
    if not valor:
        return None
    if valor.startswith("key::"):
        return _key_of(valor[5:].split())
    path = Path(valor).expanduser()
    if not path.is_absolute():
        path = vault / path
    if path.suffix != ".pub" and Path(f"{path}.pub").is_file():
        path = Path(f"{path}.pub")
    try:
        return _key_of(path.read_text(encoding="utf-8").split())
    except (OSError, UnicodeDecodeError):
        return None


def _aviso_no_registrado(quien: str) -> str:
    return (f"{quien} no figura en {SIGNERS_REL}: registra tu clave para que la firma de tus "
            "commits sea verificable (ops/runbook-firma-aprobaciones.md)")


def resolve(vault: Path | str, explicit: str | None = None, *,
            git: Callable[[str], str | None] | None = None) -> Identity:
    vault = Path(vault)
    git = git or _git_getter(vault)
    firmantes = signers(vault)
    principales = {p for ps, _ in firmantes for p in ps}

    if explicit is not None:
        valor = explicit.strip()
        if is_generic(valor):
            raise IdentityError(
                f"approved_by genérico o vacío ({explicit!r}): pasa la identidad real del "
                "aprobador (gen-compuerta-mutacion, C-04)")
        avisos = [_aviso_no_registrado(valor)] if firmantes and valor not in principales else []
        return Identity(valor, "--approved-by", avisos)

    clave = signing_key(vault, git)
    if clave:
        for ps, k in firmantes:
            if k == clave:
                return Identity(ps[0], f"{SIGNERS_REL} (clave de user.signingkey)")

    email = (git("user.email") or "").strip()
    if email and not is_generic(email):
        avisos = [_aviso_no_registrado(email)] if firmantes and email not in principales else []
        return Identity(email, "git user.email", avisos)

    raise IdentityError(
        "no hay identidad del aprobador: pasa --approved-by, configura `git config "
        f"user.email` o registra tu clave en {SIGNERS_REL} (ops/runbook-firma-aprobaciones.md)")
