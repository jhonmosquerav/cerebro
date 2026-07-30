"""Score de salud determinista del cerebro (Fase 3 del roadmap).

Seis componentes 0–100 calculadas sin LLM; las no medibles se declaran N/A
y los pesos se renormalizan (no se inventa un número donde no hay dato).
El render estático es la vista 1 de gen-visualizacion; Dataview y la lente
de grafo siguen siendo las vistas vivas e interactivas.
"""
from __future__ import annotations

import datetime
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import events as events_mod
from . import lint as lint_mod
from . import manifest as mf
from . import mirror as mirror_mod
from . import schema

PESOS = {
    "higiene": 0.25,
    "conectividad": 0.20,
    "vigencia": 0.20,
    "cobertura": 0.15,
    "deriva": 0.10,
    "genoma": 0.10,
}

_HIGIENE_CODES = {"FM-01", "FM-02", "FM-03", "FM-04", "REL-01", "ID-01"}
_CONECT_CODES = {"LNK-01", "LNK-02"}
_VIGENCIA_CODES = {"VIG-01", "VIG-02", "VIG-03"}


@dataclass
class HealthReport:
    as_of: datetime.date
    componentes: dict = field(default_factory=dict)   # nombre → int 0–100 | None
    score: int = 0
    detalle: dict = field(default_factory=dict)

    def render_text(self) -> str:
        out = [f"SALUD DEL CEREBRO · as-of {self.as_of.isoformat()} · score {self.score}/100"]
        for nombre in PESOS:
            valor = self.componentes.get(nombre)
            render = "N/A (sin dato; peso renormalizado)" if valor is None else f"{valor}/100"
            nota = self.detalle.get(nombre, "")
            out.append(f"  - {nombre:<13} {render}" + (f" — {nota}" if nota else ""))
        return "\n".join(out) + "\n"

    def render_json(self) -> str:
        return json.dumps({
            "as_of": self.as_of.isoformat(),
            "score": self.score,
            "componentes": self.componentes,
            "detalle": self.detalle,
            "pesos": PESOS,
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _pct(malas: int, total: int) -> int:
    if total <= 0:
        return 100
    return max(0, round(100 * (1 - malas / total)))


def _paginas_con(report, codes) -> int:
    return len({f.path for f in report.findings if f.code in codes})


def _cobertura(root: Path) -> tuple[int | None, str]:
    raw_dir = root / "raw"
    fuentes = [p for p in raw_dir.rglob("*") if p.is_file() and p.name != ".gitkeep"] \
        if raw_dir.is_dir() else []
    if not fuentes:
        return None, "raw/ vacío: nada que ingerir aún"
    ledger = root / "ingest-ledger.jsonl"
    procesadas: set[str] = set()
    if ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n"):
            if not line.strip():
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("resultado") in schema.LEDGER_RESULTADOS_PROCESADA:
                procesadas.add(e.get("fuente", ""))
        n = sum(1 for f in fuentes if f.relative_to(root).as_posix() in procesadas)
    else:
        n = 0
    return round(100 * n / len(fuentes)), f"{n}/{len(fuentes)} fuentes de raw/ ingeridas"


def _deriva(root: Path) -> tuple[int | None, str]:
    base = root / "audit" / "xray"
    if not base.is_dir():
        return None, "sin corrida XRAY (corre `cerebro xray --write`)"
    corridas = sorted(base.glob("*/reporte.json"))
    if not corridas:
        return None, "sin corrida XRAY (corre `cerebro xray --write`)"
    ultima = corridas[-1]
    try:
        data = json.loads(ultima.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, f"reporte XRAY ilegible: {ultima.name}"
    drift = data.get("drift_score")
    if drift is None:
        return None, "XRAY sin aristas declaradas que evaluar"
    return round(100 * float(drift)), f"corrida {ultima.parent.name}"


def _genoma(root: Path, report) -> tuple[int, str]:
    fallos = 0
    notas = []
    if mirror_mod.check(root) is not None:
        fallos += 1
        notas.append("espejo roto")
    ledger = root / "genome" / "events.jsonl"
    if ledger.is_file():
        if any(f.severity == "error" for f in events_mod.verify_file(ledger)):
            fallos += 1
            notas.append("events.jsonl con errores")
    gen_err = {f.path for f in report.findings if f.code == "GEN-01"}
    if gen_err:
        fallos += 1
        notas.append(f"{len(gen_err)} gen(es) inválido(s)")
    return max(0, 100 - 34 * fallos), "; ".join(notas) or "espejo + ledger + genes en verde"


def run(root: Path | str, *, as_of: datetime.date,
        manifest: mf.Manifest | None = None) -> HealthReport:
    root = Path(root)
    report = lint_mod.run(root, as_of=as_of, manifest=manifest)
    paginas = max(report.pages_total, 0)
    comp: dict = {}
    detalle: dict = {}

    comp["higiene"] = _pct(_paginas_con(report, _HIGIENE_CODES), paginas)
    detalle["higiene"] = f"{_paginas_con(report, _HIGIENE_CODES)} de {paginas} páginas con defectos de esquema"
    comp["conectividad"] = _pct(_paginas_con(report, _CONECT_CODES), paginas)
    detalle["conectividad"] = f"{_paginas_con(report, _CONECT_CODES)} de {paginas} páginas huérfanas o con enlaces rotos"
    comp["vigencia"] = _pct(_paginas_con(report, _VIGENCIA_CODES), paginas)
    detalle["vigencia"] = f"{_paginas_con(report, _VIGENCIA_CODES)} de {paginas} páginas vencidas (duro o blando)"
    comp["cobertura"], detalle["cobertura"] = _cobertura(root)
    comp["deriva"], detalle["deriva"] = _deriva(root)
    comp["genoma"], detalle["genoma"] = _genoma(root, report)

    disponibles = {k: v for k, v in comp.items() if v is not None}
    peso_total = sum(PESOS[k] for k in disponibles)
    score = round(sum(v * PESOS[k] for k, v in disponibles.items()) / peso_total) \
        if peso_total else 0
    return HealthReport(as_of=as_of, componentes=comp, score=score, detalle=detalle)


def write_dashboard(root: Path | str, report: HealthReport) -> Path:
    """Escribe el render estático dashboards/salud-mecanica.md (type: meta)."""
    root = Path(root)
    filas = []
    for nombre in PESOS:
        v = report.componentes.get(nombre)
        filas.append(f"| {nombre} | {'N/A' if v is None else v} | "
                     f"{PESOS[nombre]} | {report.detalle.get(nombre, '')} |")
    contenido = (
        "---\n"
        "title: Salud mecánica del cerebro\n"
        "type: meta\n"
        f"updated: {report.as_of.isoformat()}\n"
        "---\n"
        "\n"
        f"# Salud mecánica — {report.score}/100\n"
        "\n"
        f"> Generado por `python tools/cerebro.py health --write` (as-of "
        f"{report.as_of.isoformat()}). Determinista: mismo vault + misma fecha "
        "⇒ mismo número. Las componentes N/A no inventan dato: renormalizan.\n"
        "\n"
        "| Componente | Valor | Peso | Detalle |\n"
        "|---|---|---|---|\n"
        + "\n".join(filas) + "\n"
        "\n"
        "Vistas vivas: [[salud-del-genoma]] y [[salud-del-conocimiento]] (Dataview).\n"
    )
    path = root / "dashboards" / "salud-mecanica.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(contenido)
    return path
