"""Carga y validación del manifiesto de onboard (company.yaml)."""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import miniyaml, schema

_GENE_ID_RE = re.compile(r"^gen-[a-z0-9][a-z0-9-]*$")
_VERB_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_FOLDER_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_PLACEHOLDER_RE = re.compile(r"<[^<>\n]{1,60}>")


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


@dataclass
class Manifest:
    raw: dict = field(default_factory=dict)
    path: str = ""

    @property
    def company(self) -> dict:
        return self.raw.get("company") or {}

    @property
    def company_name(self) -> str:
        return self.company.get("name") or ""

    @property
    def sector(self) -> str:
        return self.company.get("sector") or ""

    @property
    def language(self) -> str:
        return self.company.get("language") or "es"

    @property
    def document_types(self) -> list:
        return self.raw.get("document_types") or []

    @property
    def entities(self) -> dict:
        return self.raw.get("entities") or {}

    @property
    def identity(self) -> dict:
        return self.raw.get("identity") or {}

    @property
    def glossary(self) -> dict:
        return self.raw.get("glossary") or {}

    @property
    def roles(self) -> dict:
        return self.raw.get("roles") or {}

    @property
    def relation_types(self) -> list:
        return self.raw.get("relation_types") or []

    @property
    def source_trust(self) -> dict:
        return self.raw.get("source_trust") or {}

    @property
    def sintesis_umbral(self) -> int:
        v = self.raw.get("sintesis_umbral")
        return v if isinstance(v, int) else 3

    @property
    def hub_umbral(self) -> int:
        v = self.raw.get("hub_umbral")
        return v if isinstance(v, int) else 7

    @property
    def ciclo(self) -> dict:
        declared = self.raw.get("ciclo_de_vida") or {}
        return _deep_merge(schema.CICLO_DEFAULTS, declared)

    @property
    def default_sensibilidad(self) -> str:
        return self.raw.get("default_sensibilidad") or "interno"

    @property
    def campos_extra(self) -> list:
        """Campos de frontmatter que la empresa declara además del núcleo.

        Simétrico a `relation_types` (gen-frontmatter-obligatorio v7). Un blueprint que
        siembra un gen exigiendo un campo propio declara aquí ese campo: así el validador
        lo conoce y no lo marca FM-04.
        """
        return self.raw.get("campos_extra") or []

    @property
    def seed_genes(self) -> list:
        return self.raw.get("seed_genes") or []

    @property
    def taxonomy(self) -> dict:
        return self.raw.get("taxonomy") or {}

    @property
    def graph_lens(self) -> dict:
        return self.raw.get("graph_lens") or {}


def load(path: Path | str) -> Manifest:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    raw = miniyaml.parse(text)
    return Manifest(raw=raw, path=str(p))


def has_placeholders(m: Manifest) -> bool:
    """True si el manifiesto conserva placeholders `<...>` de blueprint sin rellenar."""

    def scan(value) -> bool:
        if isinstance(value, str):
            return bool(_PLACEHOLDER_RE.search(value))
        if isinstance(value, dict):
            return any(scan(k) or scan(v) for k, v in value.items())
        if isinstance(value, list):
            return any(scan(v) for v in value)
        return False

    return scan(m.raw)


def validate(m: Manifest) -> list[str]:
    """Validación estructural estricta. Placeholders NO son error aquí
    (los blueprints son plantillas válidas); onboard sí los rechaza."""
    errs: list[str] = []
    if not isinstance(m.raw, dict) or not m.raw:
        return ["manifiesto vacío o ilegible"]
    if not m.company:
        errs.append("bloque company ausente")
    if not m.company_name.strip():
        errs.append("company.name es obligatorio")
    if m.raw.get("document_types") is not None and not isinstance(m.raw["document_types"], list):
        errs.append("document_types debe ser lista")
    if not isinstance(m.entities, dict):
        errs.append("entities debe ser mapa categoría→lista")
    else:
        for cat, items in m.entities.items():
            if items is not None and not isinstance(items, list):
                errs.append(f"entities.{cat} debe ser lista")
    for verb in m.relation_types:
        if not isinstance(verb, str) or not _VERB_RE.match(verb):
            errs.append(f"relation_types: verbo inválido {verb!r} (minúsculas/guion_bajo)")
    for campo in m.campos_extra:
        if not isinstance(campo, str) or not _VERB_RE.match(campo):
            errs.append(f"campos_extra: campo inválido {campo!r} (minúsculas/guion_bajo)")
        elif campo in schema.KNOWN_FIELDS:
            errs.append(f"campos_extra: {campo!r} ya está en el núcleo — retíralo del manifiesto")
    for tipo, valor in m.source_trust.items():
        if not isinstance(valor, (int, float)) or isinstance(valor, bool) or not 0.0 <= float(valor) <= 1.0:
            errs.append(f"source_trust.{tipo} fuera de rango [0,1]: {valor!r}")
    for campo in ("sintesis_umbral", "hub_umbral"):
        v = m.raw.get(campo)
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 1):
            errs.append(f"{campo} debe ser entero ≥ 1")
    if m.raw.get("default_sensibilidad") is not None and \
            m.raw["default_sensibilidad"] not in schema.SENSIBILIDADES:
        errs.append(
            f"default_sensibilidad inválida: {m.raw['default_sensibilidad']!r} "
            f"(∈ {sorted(schema.SENSIBILIDADES)})"
        )
    ciclo = m.ciclo
    for rate, dias in ciclo["decay_ventana_dias"].items():
        if not isinstance(dias, int) or isinstance(dias, bool) or dias < 1:
            errs.append(f"ciclo_de_vida.decay_ventana_dias.{rate} debe ser entero ≥ 1")
    for campo in ("decaimiento_delta", "confidence_techo", "piso_archivo"):
        v = ciclo[campo]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0.0 <= float(v) <= 1.0:
            errs.append(f"ciclo_de_vida.{campo} fuera de rango [0,1]")
    seen_ids: set[str] = set()
    for i, g in enumerate(m.seed_genes):
        if not isinstance(g, dict):
            errs.append(f"seed_genes[{i}] debe ser mapa")
            continue
        gid = g.get("id") or ""
        if not isinstance(gid, str) or not _GENE_ID_RE.match(gid):
            errs.append(f"seed_genes[{i}].id inválido: {gid!r} (patrón gen-<slug>)")
        elif gid in seen_ids:
            errs.append(f"seed_genes: id duplicado {gid!r}")
        else:
            seen_ids.add(gid)
        for req in ("trigger", "rule"):
            if not (isinstance(g.get(req), str) and g[req].strip()):
                errs.append(f"seed_genes[{i}] ({gid or 'sin id'}): falta {req}")
        tt = g.get("target_tier")
        if tt is not None and tt not in schema.TIERS:
            errs.append(f"seed_genes[{i}].target_tier inválido: {tt!r}")
    if not isinstance(m.taxonomy, dict):
        errs.append("taxonomy debe ser mapa tier→[carpetas]")
    else:
        for tier, folders in m.taxonomy.items():
            if tier not in schema.TIERS:
                errs.append(f"taxonomy: tier desconocido {tier!r}")
            if not isinstance(folders, list):
                errs.append(f"taxonomy.{tier} debe ser lista")
                continue
            for f_ in folders:
                if not isinstance(f_, str) or not _FOLDER_RE.match(f_):
                    errs.append(f"taxonomy.{tier}: carpeta inválida {f_!r} (slug en minúsculas)")
    gl = m.graph_lens
    if gl:
        if gl.get("enable") not in (True, False, None):
            errs.append("graph_lens.enable debe ser booleano")
        backend = gl.get("backend")
        if backend is not None and backend not in ("claude", "local", "structural"):
            errs.append(f"graph_lens.backend inválido: {backend!r} (claude|local|structural)")
    return errs
