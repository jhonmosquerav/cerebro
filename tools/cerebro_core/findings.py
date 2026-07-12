"""Hallazgo mecánico común a todos los validadores."""
from __future__ import annotations

from dataclasses import dataclass

SEVERITIES = ("error", "aviso", "info")


@dataclass(frozen=True)
class Finding:
    code: str        # p. ej. FM-02, EVT-05
    severity: str    # error | aviso | info
    path: str        # ruta relativa del objeto afectado
    detail: str      # qué se encontró, con el dato exacto

    def render(self) -> str:
        return f"[{self.severity.upper():5}] {self.code} {self.path} — {self.detail}"


def sort_findings(findings: list[Finding]) -> list[Finding]:
    """Orden determinista: ruta, código, detalle."""
    return sorted(findings, key=lambda f: (f.path, f.code, f.detail))


def has_errors(findings: list[Finding]) -> bool:
    return any(f.severity == "error" for f in findings)
