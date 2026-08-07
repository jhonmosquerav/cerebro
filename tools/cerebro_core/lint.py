"""LINT mecánico — los detectores deterministas de gen-lint v4 (a, c, d, e)
más los invariantes de identidad, ledger, cuarentena y confidencialidad.

La identidad de cada hallazgo la fija ESTE detector; el juicio (¿importa?,
qué proponer) sigue siendo de la operación LINT del agente, bajo compuerta.
El detector (b) — contradicciones semánticas entre páginas — NO se mecaniza:
requiere leer significado, no estructura.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import graph as graph_mod
from . import manifest as mf
from . import schema
from .findings import Finding, sort_findings
from .vault import Vault, is_linkable, load_vault


@dataclass
class Report:
    as_of: datetime.date
    findings: list[Finding] = field(default_factory=list)
    pages_total: int = 0
    excluded: list[str] = field(default_factory=list)  # códigos silenciados a propósito
    omitidas_por_descarte: int = 0  # sugerencias LNK-03 calladas por lint-descartes.jsonl

    def counts(self) -> dict:
        c = {"error": 0, "aviso": 0, "info": 0}
        for f in self.findings:
            c[f.severity] += 1
        return c

    def exit_code(self, strict: bool = False) -> int:
        c = self.counts()
        if c["error"]:
            return 1
        if strict and (c["aviso"] or c["info"]):
            return 1
        return 0

    def render_text(self) -> str:
        c = self.counts()
        out = [
            f"LINT mecánico · as-of {self.as_of.isoformat()} · "
            f"{self.pages_total} páginas wiki · "
            f"{c['error']} errores · {c['aviso']} avisos · {c['info']} info",
        ]
        if self.excluded:
            out.append(f"  (excluidos a propósito: {', '.join(self.excluded)})")
        if self.omitidas_por_descarte:
            out.append(f"  ({self.omitidas_por_descarte} sugerencia(s) LNK-03 "
                       "omitida(s) por descartes en lint-descartes.jsonl)")
        if not self.findings:
            out.append("Sin hallazgos: el vault está estructuralmente sano.")
        for f in self.findings:
            out.append(f.render())
        return "\n".join(out) + "\n"

    def render_json(self) -> str:
        return json.dumps(
            {
                "as_of": self.as_of.isoformat(),
                "pages_total": self.pages_total,
                "counts": self.counts(),
                "excluded": self.excluded,
                "omitidas_por_descarte": self.omitidas_por_descarte,
                "findings": [
                    {"code": f.code, "severity": f.severity, "path": f.path, "detail": f.detail}
                    for f in self.findings
                ],
            },
            ensure_ascii=False, indent=2, sort_keys=True,
        ) + "\n"


def git_blob_sha1(data: bytes) -> str:
    """`git hash-object` sin git: sha1('blob <len>\\0' + bytes)."""
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _load_manifest(root: Path) -> mf.Manifest | None:
    p = root / "onboard" / "company.yaml"
    if p.is_file():
        try:
            return mf.load(p)
        except Exception:
            return None
    return None


def _in_link_scope(rel: str) -> bool:
    """Ámbito del chequeo de enlaces rotos: conocimiento, genoma e índice —el
    mismo conjunto que resuelve wikilinks (vault.is_linkable). Quedan fuera
    docs/ y audit/, que citan genes hipotéticos en propuestas, y CLAUDE.md,
    que usa [[wiki-link]] como notación de ejemplo."""
    return is_linkable(rel)


def _check_wiki_pages(v: Vault, allowed: set[str], campos_ok: set[str],
                      as_of: datetime.date,
                      ciclo: dict, findings: list[Finding]) -> None:
    for p in v.wiki_pages:
        if p.fm is None:
            detail = p.fm_errors[0] if p.fm_errors else "página sin frontmatter"
            findings.append(Finding("FM-01", "error", p.rel, detail))
            continue
        if p.is_meta:
            continue
        for msg in schema.validate_page_fm(p.fm, is_meta=False):
            code = "FM-02" if msg.startswith("campo requerido ausente") else "FM-03"
            findings.append(Finding(code, "error", p.rel, msg))
        # tier declarado vs carpeta real
        tier_path = p.tier_from_path
        if tier_path and p.fm.get("tier") in schema.TIERS and p.fm["tier"] != tier_path:
            findings.append(Finding(
                "FM-03", "error", p.rel,
                f"tier declarado '{p.fm['tier']}' ≠ carpeta 'wiki/{tier_path}/'"))
        # campos que ningún gen declara (detector e)
        for campo in sorted(set(p.fm) - campos_ok):
            findings.append(Finding(
                "FM-04", "aviso", p.rel,
                f"campo fuera de esquema: '{campo}' (ningún gen lo declara; "
                "decláralo vía EVOLVE o retíralo)"))
        # verbos fuera de la unión (detector d)
        for verbo, _ in v.relations_of(p):
            if verbo not in allowed:
                findings.append(Finding(
                    "REL-01", "error", p.rel,
                    f"verbo de relación fuera de la unión: '{verbo}' "
                    "(núcleo ∪ verbos de genes ∪ relation_types del manifiesto)"))
        # vigencia dura por fecha y por evento (detector c duro)
        vh = p.fm.get("valido_hasta")
        if isinstance(vh, str) and schema.is_iso_date(vh) and datetime.date.fromisoformat(vh) < as_of:
            findings.append(Finding(
                "VIG-01", "error", p.rel,
                f"vencida dura: valido_hasta {vh} < {as_of.isoformat()} "
                "(prioritario si el dominio es de seguridad; QUERY debe advertirla siempre)"))
        vig = p.fm.get("vigencia")
        if vig in ("derogada", "no-vigente", "en-revision"):
            findings.append(Finding(
                "VIG-02", "error", p.rel,
                f"vencida por evento: vigencia '{vig}' (gen-vigencia-temporal)"))
        # vencido blando por ventanas de decaimiento (detector c blando)
        _check_soft_decay(p, as_of, ciclo, findings)
        # identidad de página
        idp = p.fm.get("id_pagina")
        if isinstance(idp, str) and p.rel.startswith("wiki/"):
            esperado = p.rel[len("wiki/"):-len(".md")]
            if idp != esperado:
                findings.append(Finding(
                    "ID-01", "error", p.rel,
                    f"id_pagina '{idp}' ≠ ruta '{esperado}' "
                    "(las claves históricas van en id_alias)"))
        if p.fm.get("riesgo_inyeccion") is True:
            findings.append(Finding(
                "QRN-01", "info", p.rel,
                "en cuarentena riesgo_inyeccion: no promover ni fusionar; "
                "solo el humano la retira tras revisión"))


def _check_soft_decay(p, as_of: datetime.date, ciclo: dict, findings: list[Finding]) -> None:
    if p.fm.get("clase") == "evento" or p.fm.get("type") in ("hub", "meta"):
        return
    if p.tier_from_path == "archive":
        return
    lr = p.fm.get("last_reinforced")
    rate = p.fm.get("decay_rate")
    if not (isinstance(lr, str) and schema.is_iso_date(lr)) or rate not in schema.DECAY_RATES:
        return
    base = datetime.date.fromisoformat(lr)
    da = p.fm.get("decay_aplicado")
    if isinstance(da, str) and schema.is_iso_date(da):
        base = max(base, datetime.date.fromisoformat(da))
    ventana = ciclo["decay_ventana_dias"][rate]
    ventanas = (as_of - base).days // ventana
    if ventanas >= 1:
        findings.append(Finding(
            "VIG-03", "aviso", p.rel,
            f"vencida blanda: {ventanas} ventana(s) de {ventana}d sin refuerzo "
            f"desde {base.isoformat()} (CONSOLIDATE restará "
            f"{ciclo['decaimiento_delta']} por ventana)"))


def _check_links(v: Vault, findings: list[Finding]) -> None:
    linked_in: set[str] = set()
    for p in v.pages:
        targets = list(p.wikilinks)
        if p.fm:
            targets += [t for _, t in v.relations_of(p)]
        for t in targets:
            resolved = v.resolve_link(t)
            if resolved:
                linked_in.add(resolved)
            elif _in_link_scope(p.rel):
                findings.append(Finding(
                    "LNK-01", "error", p.rel, f"enlace roto: [[{t}]] no resuelve"))
    # huérfanas (detector a): sin entrantes ni salientes; exentas las meta
    for p in v.wiki_pages:
        if p.fm is None or p.is_meta:
            continue
        tiene_salientes = bool(p.wikilinks) or bool(v.relations_of(p))
        tiene_entrantes = p.rel in linked_in
        if not tiene_salientes and not tiene_entrantes:
            findings.append(Finding(
                "LNK-02", "aviso", p.rel,
                "huérfana: sin relaciones entrantes ni salientes ni ancla"))


def _cargar_descartes(root: Path, findings: list[Finding]) -> set[tuple[str, str]]:
    """Descartes persistentes de LNK-03: `lint-descartes.jsonl` en la raíz.

    Archivo OPCIONAL y append-only; una línea JSON por descarte con claves
    {ts, pagina, termino, motivo}. El par (pagina, termino) descartado deja de
    sugerirse en corridas futuras — así una sugerencia evaluada y rechazada bajo
    criterio no vuelve a aparecer en cada lint. Validación tolerante: una línea
    malformada produce aviso (DSC-01), no crash, y no invalida a las demás.
    """
    descartes: set[tuple[str, str]] = set()
    path = root / "lint-descartes.jsonl"
    if not path.is_file():
        return descartes
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    for i, line in enumerate([l for l in text.split("\n") if l.strip()], start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            findings.append(Finding(
                "DSC-01", "aviso", f"lint-descartes.jsonl:{i}",
                f"línea inválida: {e.msg} (se ignora; el resto sigue aplicando)"))
            continue
        if not isinstance(entry, dict):
            findings.append(Finding(
                "DSC-01", "aviso", f"lint-descartes.jsonl:{i}",
                "el descarte debe ser un objeto JSON {ts, pagina, termino, motivo}"))
            continue
        faltan = [k for k in ("ts", "pagina", "termino", "motivo")
                  if not (isinstance(entry.get(k), str) and entry[k].strip())]
        if faltan:
            findings.append(Finding(
                "DSC-01", "aviso", f"lint-descartes.jsonl:{i}",
                f"claves ausentes o vacías: {', '.join(faltan)} "
                "(esquema: ts, pagina, termino, motivo)"))
            continue
        descartes.add((entry["pagina"], entry["termino"]))
    return descartes


def _check_link_suggestions(v: Vault, findings: list[Finding],
                            descartes: set[tuple[str, str]]) -> int:
    """LNK-03 — mención en prosa de una página existente que no está enlazada.

    Complemento PREVENTIVO de LNK-01/LNK-02: ataca la causa de las huérfanas en
    vez de esperar a que aparezcan. Severidad `info` porque no es un defecto:
    es una propuesta que el agente evalúa y aplica bajo criterio (nunca
    auto-inserta; ver `graph.py`). Devuelve cuántas sugerencias calló el
    archivo de descartes (el reporte lo muestra en una sola línea).
    """
    omitidas = 0
    for src, dst, term in graph_mod.sugerencias(v, "wiki"):
        if (src, term) in descartes:
            omitidas += 1
            continue
        findings.append(Finding(
            "LNK-03", "info", src,
            f"menciona «{term}» sin enlazar → [[{Path(dst).stem}]] ({dst})"))
    return omitidas


def _check_confidencial_anclada(v: Vault, findings: list[Finding]) -> None:
    anclas: set[str] = set()
    for p in v.pages:
        es_indice = p.rel == "index.md"
        es_hub = bool(p.fm) and p.fm.get("type") == "hub"
        if not (es_indice or es_hub):
            continue
        for t in p.wikilinks:
            resolved = v.resolve_link(t)
            if resolved:
                anclas.add((resolved, p.rel))
    for rel, donde in sorted(anclas):
        page = v.page_by_rel(rel)
        if page and page.fm and page.fm.get("sensibilidad") == "confidencial":
            findings.append(Finding(
                "SEN-01", "error", rel,
                f"página confidencial anclada en {donde} "
                "(gen-confidencialidad: lo confidencial no se ancla)"))


def _check_ledger(root: Path, findings: list[Finding]) -> None:
    ledger = root / "ingest-ledger.jsonl"
    if not ledger.is_file():
        return  # sin ledger = nada ingerido aún (estado legítimo del template)
    ultimo_por_fuente: dict[str, dict] = {}
    text = ledger.read_text(encoding="utf-8").replace("\r\n", "\n")
    for i, line in enumerate([l for l in text.split("\n") if l.strip()], start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            findings.append(Finding(
                "LED-02", "error", f"ingest-ledger.jsonl:{i}", f"línea inválida: {e.msg}"))
            continue
        faltan = [k for k in ("ts", "op", "fuente", "hash", "resultado") if k not in entry]
        if faltan:
            findings.append(Finding(
                "LED-02", "error", f"ingest-ledger.jsonl:{i}",
                f"claves ausentes: {', '.join(faltan)}"))
            continue
        # `resultado` es vocabulario cerrado (gen-identidad-de-pagina v3): la cobertura de
        # health se calcula sobre este campo, así que un valor libre la falsea sin avisar.
        if entry["resultado"] not in schema.LEDGER_RESULTADOS:
            findings.append(Finding(
                "LED-02", "error", f"ingest-ledger.jsonl:{i}",
                f"resultado fuera de vocabulario: {entry['resultado']!r} "
                f"(∈ {sorted(schema.LEDGER_RESULTADOS)}); la cobertura de health "
                "se calcula sobre este campo"))
            continue
        ultimo_por_fuente[entry["fuente"]] = entry
    for fuente, entry in sorted(ultimo_por_fuente.items()):
        f_path = root / fuente
        if not f_path.is_file():
            findings.append(Finding(
                "LED-01", "error", fuente,
                "fuente registrada en el ledger que ya no existe en raw/ "
                "(gen-raw-inmutable violado: nada se borra de raw/)"))
            continue
        data = f_path.read_bytes()
        h_raw = git_blob_sha1(data)
        h_lf = git_blob_sha1(data.replace(b"\r\n", b"\n"))
        if entry["hash"] not in (h_raw, h_lf):
            findings.append(Finding(
                "LED-01", "error", fuente,
                f"raw/ mutó: hash actual {h_raw[:12]}… ≠ ledger {str(entry['hash'])[:12]}… "
                "(gen-raw-inmutable violado; no procesar, reportar)"))


def _check_genome(v: Vault, findings: list[Finding]) -> None:
    for p in v.genes + v.capsules:
        if p.fm is None:
            findings.append(Finding(
                "GEN-01", "error", p.rel,
                p.fm_errors[0] if p.fm_errors else "gen sin frontmatter"))
            continue
        gid = p.fm.get("id")
        base = p.basename
        if not gid:
            findings.append(Finding("GEN-01", "error", p.rel, "gen sin campo id"))
        elif gid not in (base, f"cap-{base}"):
            findings.append(Finding(
                "GEN-01", "error", p.rel, f"id '{gid}' no coincide con el archivo '{base}.md'"))
        if p.fm.get("status") not in ("active", "deprecated"):
            findings.append(Finding(
                "GEN-01", "error", p.rel, f"status inválido: {p.fm.get('status')!r}"))
        version = p.fm.get("version")
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            findings.append(Finding(
                "GEN-01", "error", p.rel, f"version inválida: {version!r}"))
        if p.rel.startswith("genome/genes/") and not p.fm.get("trigger"):
            findings.append(Finding("GEN-01", "error", p.rel, "gen sin trigger"))
        if p.rel.startswith("genome/capsules/") and not isinstance(p.fm.get("composes"), list):
            findings.append(Finding("GEN-01", "error", p.rel, "cápsula sin composes"))


# Códigos que dependen del CALENDARIO, no del contenido del commit: una página
# vence sola, sin que nadie la toque. Excluirlos es lo que permite correr el lint
# completo en el pre-commit sin que un vencimiento bloquee commits ajenos (el
# vencimiento lo atiende la operación LINT, bajo compuerta, no un hook).
CODIGOS_TEMPORALES = frozenset({"VIG-01", "VIG-02", "VIG-03"})


def run(root: Path | str, *, as_of: datetime.date,
        manifest: mf.Manifest | None = None,
        exclude: set[str] | frozenset[str] | None = None) -> Report:
    root = Path(root)
    v = load_vault(root)
    m = manifest if manifest is not None else _load_manifest(root)
    allowed = schema.allowed_verbs(m.relation_types if m else None)
    campos_ok = schema.allowed_fields(m.campos_extra if m else None)
    ciclo = m.ciclo if m else schema.CICLO_DEFAULTS
    findings: list[Finding] = []
    _check_wiki_pages(v, allowed, campos_ok, as_of, ciclo, findings)
    _check_links(v, findings)
    descartes = _cargar_descartes(root, findings)
    omitidas = _check_link_suggestions(v, findings, descartes)
    _check_confidencial_anclada(v, findings)
    _check_ledger(root, findings)
    _check_genome(v, findings)
    if exclude:
        findings = [f for f in findings if f.code not in exclude]
    return Report(as_of=as_of, findings=sort_findings(findings),
                  pages_total=len(v.wiki_pages), excluded=sorted(exclude or ()),
                  omitidas_por_descarte=omitidas)
