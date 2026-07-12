"""XRAY — deriva entre el grafo declarado y el grafo inferido (Fase 2).

El riesgo estructural de un grafo declarativo es la deriva: lo que el
frontmatter afirma deja de coincidir con lo que el corpus demuestra, y
nadie se entera. XRAY compara mecánicamente ambos mundos y PROPONE:

- **declarado sin evidencia** — arista de `relations` que nada respalda
  (ni wikilink, ni fuente compartida, ni co-mención, ni la lente externa).
- **evidenciado sin declarar** — par co-mencionado ≥ min_co veces sin arista.
- **contradicciones** — `contradice` declarados (se elevan SIEMPRE) y
  `reemplaza` recíprocos.

Jamás escribe en wiki/ ni genome/: su salida va a audit/xray/ y alimenta a
LINT/CONSOLIDATE/EVOLVE por la compuerta. La lente externa (graphify u
otra) es OPCIONAL: un `graph.json` con nodos/aristas suma evidencia, pero
XRAY funciona sin ella. Páginas confidenciales: solo se citan por ruta.
"""
from __future__ import annotations

import datetime
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .vault import Vault, load_vault

RAW_EXTS = {".md", ".txt", ".csv", ".html"}
MIN_TOKEN = 4  # títulos más cortos no sirven como evidencia de co-mención


@dataclass
class XrayReport:
    as_of: datetime.date
    declaradas: list[dict] = field(default_factory=list)
    sin_declarar: list[dict] = field(default_factory=list)
    contradicciones: list[dict] = field(default_factory=list)
    drift_score: float | None = None
    lente_externa: str | None = None

    def render_md(self) -> str:
        ev = [e for e in self.declaradas if e["evidencia"]]
        no_ev = [e for e in self.declaradas if not e["evidencia"]]
        drift = "N/A (sin aristas declaradas)" if self.drift_score is None \
            else f"{self.drift_score:.3f} ({len(ev)}/{len(self.declaradas)} aristas con evidencia)"
        out = [
            "---",
            "title: XRAY — deriva declarado vs inferido",
            "type: meta",
            f"updated: {self.as_of.isoformat()}",
            "---",
            "",
            f"# XRAY · as-of {self.as_of.isoformat()}",
            "",
            f"- **Score de deriva**: {drift}",
            f"- Lente externa: {self.lente_externa or 'no usada (evidencia léxica local)'}",
            "- Este reporte **PROPONE**: nada se aplica sin compuerta.",
            "",
            f"## Declarado sin evidencia ({len(no_ev)}) — candidatos a decaimiento o revisión",
        ]
        for e in no_ev:
            out.append(f"- `{e['de']}` —{e['verbo']}→ `{e['a']}`")
        out.append("")
        out.append(f"## Evidenciado sin declarar ({len(self.sin_declarar)}) — candidatos a ingesta de relación")
        for p in self.sin_declarar:
            out.append(f"- `{p['a']}` ↔ `{p['b']}` ({p['evidencia']})")
        out.append("")
        out.append(f"## Contradicciones ({len(self.contradicciones)}) — escalamiento")
        for c in self.contradicciones:
            out.append(f"- `{c['de']}` —{c['verbo']}→ `{c['a']}` ({c['nota']})")
        out.append("")
        out.append(f"## Declarado con evidencia ({len(ev)})")
        for e in ev:
            out.append(f"- `{e['de']}` —{e['verbo']}→ `{e['a']}` · {'; '.join(e['evidencia'])}")
        return "\n".join(out) + "\n"

    def render_json(self) -> str:
        return json.dumps({
            "as_of": self.as_of.isoformat(),
            "drift_score": self.drift_score,
            "lente_externa": self.lente_externa,
            "declaradas": self.declaradas,
            "sin_declarar": self.sin_declarar,
            "contradicciones": self.contradicciones,
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _tokens(page) -> list[str]:
    toks = [page.basename.lower()]
    title = (page.fm or {}).get("title")
    if isinstance(title, str) and len(title.strip()) >= MIN_TOKEN:
        toks.append(title.strip().lower())
    return [t for t in toks if len(t) >= MIN_TOKEN]


def _leer_raw(root: Path) -> dict[str, str]:
    docs: dict[str, str] = {}
    raw = root / "raw"
    if not raw.is_dir():
        return docs
    for p in sorted(raw.rglob("*")):
        if p.is_file() and p.suffix.lower() in RAW_EXTS:
            try:
                docs[p.relative_to(root).as_posix()] = \
                    p.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
    return docs


def _cargar_inferido(inferred_path: Path, v: Vault) -> set[frozenset]:
    """Aristas de un graph.json externo, mapeadas a rutas del vault."""
    data = json.loads(Path(inferred_path).read_text(encoding="utf-8"))
    pares: set[frozenset] = set()
    for edge in data.get("edges", []):
        a = edge.get("source") or edge.get("from") or ""
        b = edge.get("target") or edge.get("to") or ""
        ra, rb = v.resolve_link(str(a)), v.resolve_link(str(b))
        if ra and rb and ra != rb:
            pares.add(frozenset((ra, rb)))
    return pares


def run(root: Path | str, *, as_of: datetime.date,
        inferred_path: Path | str | None = None, min_co: int = 2) -> XrayReport:
    root = Path(root)
    v = load_vault(root)
    paginas = [p for p in v.wiki_pages
               if p.fm and not p.is_meta and p.fm.get("type") != "hub"]
    por_rel = {p.rel: p for p in paginas}
    raw_docs = _leer_raw(root)
    inferido: set[frozenset] = set()
    lente = None
    if inferred_path:
        inferido = _cargar_inferido(Path(inferred_path), v)
        lente = Path(inferred_path).name

    # ── evidencia por co-mención (raw + terceras páginas) ───────────────────
    co_menciones: dict[frozenset, list[str]] = {}
    toks = {p.rel: _tokens(p) for p in paginas}
    rels = sorted(por_rel)
    for doc_rel, texto in raw_docs.items():
        presentes = [r for r in rels if any(t in texto for t in toks[r])]
        for i, a in enumerate(presentes):
            for b in presentes[i + 1:]:
                co_menciones.setdefault(frozenset((a, b)), []).append(doc_rel)
    for p in v.pages:
        destinos = {v.resolve_link(t) for t in p.wikilinks}
        destinos = sorted(d for d in destinos if d and d in por_rel and d != p.rel)
        for i, a in enumerate(destinos):
            for b in destinos[i + 1:]:
                co_menciones.setdefault(frozenset((a, b)), []).append(f"co-enlace en {p.rel}")

    # ── aristas declaradas y su evidencia ────────────────────────────────────
    declaradas: list[dict] = []
    contradicciones: list[dict] = []
    declared_pairs: set[frozenset] = set()
    reemplaza_dirigido: set[tuple[str, str]] = set()
    for p in paginas:
        sources_p = {str(s) for s in (p.fm.get("sources") or [])}
        for verbo, target in v.relations_of(p):
            destino = v.resolve_link(target)
            entrada = {"de": p.rel, "verbo": verbo, "a": destino or f"[[{target}]] (no resuelve)",
                       "evidencia": []}
            if destino and destino in por_rel:
                declared_pairs.add(frozenset((p.rel, destino)))
                q = por_rel[destino]
                if destino in {v.resolve_link(t) for t in p.wikilinks} or \
                        p.rel in {v.resolve_link(t) for t in q.wikilinks}:
                    entrada["evidencia"].append("wikilink en el cuerpo")
                if sources_p & {str(s) for s in (q.fm.get("sources") or [])}:
                    entrada["evidencia"].append("fuente compartida en sources")
                docs = co_menciones.get(frozenset((p.rel, destino)), [])
                if docs:
                    entrada["evidencia"].append(f"co-mención en {len(docs)} documento(s)")
                if frozenset((p.rel, destino)) in inferido:
                    entrada["evidencia"].append("arista en la lente externa")
                if verbo == "reemplaza":
                    reemplaza_dirigido.add((p.rel, destino))
            if verbo == "contradice":
                contradicciones.append({
                    "de": p.rel, "verbo": verbo, "a": entrada["a"],
                    "nota": "contradicción declarada abierta (bloquea promoción)"})
            declaradas.append(entrada)
    for a, b in sorted(reemplaza_dirigido):
        if (b, a) in reemplaza_dirigido and a < b:
            contradicciones.append({
                "de": a, "verbo": "reemplaza", "a": b,
                "nota": "reemplaza RECÍPROCO: ambos dicen reemplazar al otro"})

    # ── evidenciado sin declarar ─────────────────────────────────────────────
    sin_declarar: list[dict] = []
    for par, docs in sorted(co_menciones.items(), key=lambda kv: sorted(kv[0])):
        if len(docs) >= min_co and par not in declared_pairs:
            a, b = sorted(par)
            sin_declarar.append({
                "a": a, "b": b,
                "evidencia": f"co-mención en {len(docs)} lugares: {', '.join(sorted(set(docs))[:3])}"})
    for par in sorted(inferido, key=sorted):
        if par not in declared_pairs and len(par) == 2:
            a, b = sorted(par)
            if not any(s["a"] == a and s["b"] == b for s in sin_declarar):
                sin_declarar.append({"a": a, "b": b,
                                     "evidencia": "arista de la lente externa sin declarar"})

    con_evidencia = sum(1 for e in declaradas if e["evidencia"])
    drift = (con_evidencia / len(declaradas)) if declaradas else None
    return XrayReport(as_of=as_of, declaradas=declaradas, sin_declarar=sin_declarar,
                      contradicciones=contradicciones, drift_score=drift,
                      lente_externa=lente)


def _short_sha(root: Path) -> str:
    try:
        proc = subprocess.run(["git", "-C", str(root), "rev-parse", "--short=8", "HEAD"],
                              capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "worktree"


def write_report(root: Path | str, report: XrayReport) -> Path:
    """Persiste la corrida en audit/xray/<as-of>-<sha8>/ (reproducible por SHA)."""
    root = Path(root)
    destino = root / "audit" / "xray" / f"{report.as_of.isoformat()}-{_short_sha(root)}"
    destino.mkdir(parents=True, exist_ok=True)
    with (destino / "reporte.md").open("w", encoding="utf-8", newline="\n") as f:
        f.write(report.render_md())
    with (destino / "reporte.json").open("w", encoding="utf-8", newline="\n") as f:
        f.write(report.render_json())
    return destino
