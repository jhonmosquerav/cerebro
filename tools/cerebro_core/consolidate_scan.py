"""Scanner mecánico de CONSOLIDATE — calcula, jamás aplica.

Mecaniza los umbrales numéricos de gen-ciclo-de-vida v5 y la detección de
candidatos de gen-consolidate v6. La decisión de fusionar, promover o
archivar sigue siendo del agente bajo las reglas del genoma; este scanner
le entrega la lista determinista de candidatos con los números ya hechos.
"""
from __future__ import annotations

import datetime
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from . import manifest as mf
from . import schema
from .vault import Vault, load_vault

# pares con relación declarada que NO son duplicados (gen-consolidate v6)
EXEMPT_VERBS = {"deriva_de", "reemplaza", "agregado_en", "agrega", "sucede_a", "proviene_de"}
JACCARD_UMBRAL = 0.6


@dataclass
class ScanReport:
    as_of: datetime.date
    decaimientos: list[dict] = field(default_factory=list)
    promociones: list[dict] = field(default_factory=list)
    archivos: list[dict] = field(default_factory=list)
    duplicados: list[dict] = field(default_factory=list)

    def render_text(self) -> str:
        out = [f"CONSOLIDATE scan · as-of {self.as_of.isoformat()} — solo PROPONE, nada se aplica"]
        out.append(f"\n## Decaimientos pendientes ({len(self.decaimientos)})")
        for d in self.decaimientos:
            out.append(
                f"  - {d['path']}: {d['ventanas']} ventana(s) de {d['ventana_dias']}d → "
                f"confidence {d['confidence_actual']} → {d['confidence_propuesta']} "
                f"(anotar decay_aplicado: {self.as_of.isoformat()})")
        out.append(f"\n## Elegibles a promoción ({len(self.promociones)})")
        for p in self.promociones:
            out.append(f"  - {p['path']} → wiki/{p['destino']}/ (cumple TODAS las condiciones)")
        out.append(f"\n## Candidatas a archivo ({len(self.archivos)}) — requieren OK humano")
        for a in self.archivos:
            out.append(f"  - {a['path']}: {a['motivo']}")
        out.append(f"\n## Pares candidatos a duplicado ({len(self.duplicados)}) — la fusión es juicio")
        for dup in self.duplicados:
            out.append(f"  - {dup['a']} ↔ {dup['b']} ({dup['motivo']})")
        return "\n".join(out) + "\n"

    def render_json(self) -> str:
        return json.dumps({
            "as_of": self.as_of.isoformat(),
            "decaimientos": self.decaimientos,
            "promociones": self.promociones,
            "archivos": self.archivos,
            "duplicados": self.duplicados,
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _norm_title(title: str) -> str:
    s = unicodedata.normalize("NFD", str(title).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def _shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    words = re.sub(r"[^\wáéíóúñü ]", " ", text.lower()).split()
    return {tuple(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def _fecha(fm: dict, campo: str) -> datetime.date | None:
    v = fm.get(campo)
    if isinstance(v, str) and schema.is_iso_date(v):
        return datetime.date.fromisoformat(v)
    return None


def _scan_decaimientos(v: Vault, as_of: datetime.date, ciclo: dict) -> list[dict]:
    out = []
    for p in v.wiki_pages:
        if not p.fm or p.is_meta or p.fm.get("type") == "hub":
            continue
        if p.fm.get("clase") == "evento" or p.tier_from_path == "archive":
            continue
        rate = p.fm.get("decay_rate")
        lr = _fecha(p.fm, "last_reinforced")
        conf = p.fm.get("confidence")
        if rate not in schema.DECAY_RATES or lr is None or not isinstance(conf, (int, float)):
            continue
        base = lr
        da = _fecha(p.fm, "decay_aplicado")
        if da:
            base = max(base, da)
        ventana = ciclo["decay_ventana_dias"][rate]
        ventanas = (as_of - base).days // ventana
        if ventanas >= 1:
            delta = round(ventanas * ciclo["decaimiento_delta"], 4)
            out.append({
                "path": p.rel,
                "ventanas": ventanas,
                "ventana_dias": ventana,
                "confidence_actual": conf,
                "confidence_propuesta": max(0.0, round(float(conf) - delta, 4)),
            })
    return sorted(out, key=lambda d: d["path"])


def _tiene_contradice(v: Vault, page, entrantes: dict[str, set[str]]) -> bool:
    if any(verbo == "contradice" for verbo, _ in v.relations_of(page)):
        return True
    return "contradice" in entrantes.get(page.rel, set())


def _scan_promociones(v: Vault, as_of: datetime.date, ciclo: dict) -> list[dict]:
    # mapa de relaciones entrantes: rel_destino → {verbos}, y conteo de refs
    entrantes: dict[str, set[str]] = {}
    refs: dict[str, set[str]] = {}
    for p in v.pages:
        objetivos = [(verbo, v.resolve_link(t)) for verbo, t in v.relations_of(p)] if p.fm else []
        objetivos += [(None, v.resolve_link(t)) for t in p.wikilinks]
        for verbo, destino in objetivos:
            if not destino:
                continue
            if verbo:
                entrantes.setdefault(destino, set()).add(verbo)
            refs.setdefault(destino, set()).add(p.rel)
    pro = ciclo["promocion"]
    out = []
    for p in v.wiki_pages:
        if not p.fm or p.is_meta or p.tier_from_path != "working":
            continue
        fm = p.fm
        if fm.get("clase", "estable") != "estable":
            continue
        conf = fm.get("confidence")
        if not isinstance(conf, (int, float)) or conf < pro["confidence_min"]:
            continue
        fuentes = fm.get("sources") if isinstance(fm.get("sources"), list) else []
        n_refs = len(refs.get(p.rel, set()) - {p.rel})
        if len(fuentes) < pro["fuentes_min"] and n_refs < pro["refs_min"]:
            continue
        created = _fecha(fm, "created")
        lr = _fecha(fm, "last_reinforced")
        if not created or not lr:
            continue
        if (as_of - created).days < pro["edad_min_dias"] or not lr > created:
            continue
        if fm.get("riesgo_inyeccion") is True:
            continue
        if fm.get("sensibilidad") == "confidencial":
            continue
        if _tiene_contradice(v, p, entrantes):
            continue
        destino = "procedural" if fm.get("type") == "sop" else "semantic"
        out.append({"path": p.rel, "destino": destino})
    return sorted(out, key=lambda d: d["path"])


def _scan_archivos(v: Vault, as_of: datetime.date, ciclo: dict) -> list[dict]:
    out = []
    for p in v.wiki_pages:
        if not p.fm or p.is_meta or p.fm.get("type") == "hub":
            continue
        if p.tier_from_path == "archive":
            continue
        fm = p.fm
        if fm.get("estado"):
            continue  # jamás se archiva una entidad con estado operativo abierto
        conf = fm.get("confidence")
        if fm.get("clase", "estable") == "estable" and isinstance(conf, (int, float)) \
                and conf <= ciclo["piso_archivo"]:
            out.append({"path": p.rel,
                        "motivo": f"confidence {conf} ≤ piso_archivo {ciclo['piso_archivo']}"})
            continue
        if fm.get("clase") == "evento":
            fe = _fecha(fm, "fecha_evento")
            if fe and (as_of - fe).days > ciclo["archivo_eventos_dias"]:
                agregada = any(verbo == "agregado_en" for verbo, _ in v.relations_of(p))
                nota = " (bajo riesgo: ya agregada en síntesis)" if agregada else ""
                out.append({"path": p.rel,
                            "motivo": f"evento de hace {(as_of - fe).days}d "
                                      f"> {ciclo['archivo_eventos_dias']}d{nota}"})
    return sorted(out, key=lambda d: d["path"])


def _exentos(v: Vault, a, b) -> bool:
    for x, y in ((a, b), (b, a)):
        for verbo, target in v.relations_of(x):
            if verbo in EXEMPT_VERBS and v.resolve_link(target) == y.rel:
                return True
    return False


def _scan_duplicados(v: Vault, ciclo: dict) -> list[dict]:
    candidatas = [p for p in v.wiki_pages
                  if p.fm and not p.is_meta and p.fm.get("type") != "hub"
                  and p.fm.get("riesgo_inyeccion") is not True
                  and p.tier_from_path != "archive"]
    out = []
    for i, a in enumerate(candidatas):
        for b in candidatas[i + 1:]:
            if _exentos(v, a, b):
                continue
            motivo = None
            ta, tb = _norm_title(a.fm.get("title", "")), _norm_title(b.fm.get("title", ""))
            if ta and ta == tb:
                motivo = "mismo título normalizado"
            else:
                sa, sb = _shingles(a.body), _shingles(b.body)
                if sa and sb:
                    j = len(sa & sb) / len(sa | sb)
                    if j >= JACCARD_UMBRAL:
                        motivo = f"similitud léxica Jaccard {j:.2f} ≥ {JACCARD_UMBRAL}"
            if motivo:
                out.append({"a": a.rel, "b": b.rel, "motivo": motivo})
    return sorted(out, key=lambda d: (d["a"], d["b"]))


def run(root: Path | str, *, as_of: datetime.date,
        manifest: mf.Manifest | None = None) -> ScanReport:
    root = Path(root)
    v = load_vault(root)
    if manifest is None:
        p = root / "onboard" / "company.yaml"
        if p.is_file():
            try:
                manifest = mf.load(p)
            except Exception:
                manifest = None
    ciclo = manifest.ciclo if manifest else schema.CICLO_DEFAULTS
    return ScanReport(
        as_of=as_of,
        decaimientos=_scan_decaimientos(v, as_of, ciclo),
        promociones=_scan_promociones(v, as_of, ciclo),
        archivos=_scan_archivos(v, as_of, ciclo),
        duplicados=_scan_duplicados(v, ciclo),
    )
