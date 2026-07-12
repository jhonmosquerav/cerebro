"""Espejo ejecutable del esquema que declaran los genes del genoma.

Cada constante cita el gen que la origina. Si una mutación de genoma cambia
el esquema (campo nuevo, verbo nuevo, enum nuevo), este módulo debe mutar en
el MISMO cambio — es la contraparte mecánica de la regla, y el test de corpus
(`tests/`) delata la deriva si se olvida.
"""
from __future__ import annotations

import datetime
import re

# ── gen-frontmatter-obligatorio v6 ────────────────────────────────────────────
REQUIRED_FIELDS = [
    "title", "type", "tier", "tags", "confidence",
    "created", "last_reinforced", "decay_rate", "sources", "relations",
]

# campo opcional → gen que lo declara
OPTIONAL_FIELDS = {
    "valido_hasta": "gen-vigencia-temporal",
    "vigencia": "gen-vigencia-temporal",
    "sensibilidad": "gen-confidencialidad",
    "clase": "gen-clase-temporal",
    "fecha_evento": "gen-clase-temporal",
    "volatile_fields": "gen-clase-temporal",
    "estado": "gen-entidad-con-estado",
    "id_pagina": "gen-identidad-de-pagina",
    "id_alias": "gen-identidad-de-pagina",
    "riesgo_inyeccion": "gen-anti-inyeccion",
    "decay_aplicado": "gen-ciclo-de-vida",
    "archivado": "gen-ciclo-de-vida",
}

KNOWN_FIELDS = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)

TIERS = {"working", "episodic", "semantic", "procedural", "archive"}
DECAY_RATES = {"high", "medium", "low"}
SENSIBILIDADES = {"publico", "interno", "confidencial"}          # gen-confidencialidad v3
CLASES = {"estable", "evento"}                                    # gen-clase-temporal v2
VIGENCIAS = {"vigente", "derogada", "no-vigente", "en-revision"}  # gen-vigencia-temporal v2
TYPES = {"concepto", "entidad", "fuente", "sintesis", "sop",
         "observacion", "sesion", "hub", "meta"}

# ── verbos de relación ────────────────────────────────────────────────────────
RELATION_CORE = {"usa", "depende_de", "contradice", "reemplaza"}  # núcleo reservado
GENE_VERBS = {          # declarados por genes activos (gen-frontmatter-obligatorio v6)
    "agrega", "agregado_en",        # gen-sintesis-de-volumen / gen-consolidate
    "sucede_a", "proviene_de",      # gen-entidad-con-estado
    "corrobora",                    # gen-confianza-por-fuente
    "deriva_de",                    # gen-consolidate
}

# ── gen-ciclo-de-vida v5: los números de la memoria por capas ────────────────
CICLO_DEFAULTS = {
    "decay_ventana_dias": {"high": 14, "medium": 60, "low": 180},
    "decaimiento_delta": 0.05,
    "refuerzo_delta": {"oficial": 0.10, "interna": 0.05, "blanda": 0.03},
    "confidence_techo": 0.95,
    "piso_archivo": 0.30,
    "archivo_eventos_dias": 180,
    "promocion": {
        "confidence_min": 0.70,
        "fuentes_min": 2,
        "refs_min": 2,
        "edad_min_dias": 7,
    },
}

# decay_rate por defecto según tier (gen-ciclo-de-vida v5)
TIER_DEFAULT_DECAY = {
    "working": "high", "episodic": "high",
    "semantic": "medium", "procedural": "low", "archive": "low",
}

_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LINK_WRAP_RE = re.compile(r"^\[\[(.+)\]\]$")


def is_iso_date(value) -> bool:
    if not isinstance(value, str) or not _ISO_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def strip_link(target) -> str:
    """`[[Página]]` → `Página`; deja lo demás intacto."""
    if isinstance(target, str):
        m = _LINK_WRAP_RE.match(target.strip())
        if m:
            return m.group(1).strip()
        return target.strip()
    return str(target)


def relation_pairs(relations) -> list[tuple[str, str]]:
    """Aplana `relations` a pares (verbo, destino) ordenados y sin envoltorio [[ ]].

    Acepta dict verbo→(str | lista) y las formas vacías `{}` / `[]`.
    """
    pairs: list[tuple[str, str]] = []
    if not relations:
        return pairs
    if isinstance(relations, dict):
        for verb, targets in relations.items():
            if targets is None:
                continue
            if isinstance(targets, (str, int, float)):
                targets = [targets]
            for t in targets:
                pairs.append((str(verb), strip_link(t)))
    return sorted(pairs)


def allowed_verbs(relation_types) -> set[str]:
    """Unión: núcleo ∪ verbos de genes activos ∪ relation_types del manifiesto."""
    verbs = set(RELATION_CORE) | set(GENE_VERBS)
    if relation_types:
        verbs |= {str(v) for v in relation_types}
    return verbs


def validate_page_fm(fm: dict, *, is_meta: bool) -> list[str]:
    """Valida el frontmatter de una página de wiki/ contra el esquema.

    Devuelve mensajes de error (sin ruta; el llamador la antepone).
    Las páginas `type: meta` quedan exentas (gen-frontmatter-obligatorio v6).
    """
    if is_meta or fm.get("type") == "meta":
        return []
    errs: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in fm or fm[field] is None:
            errs.append(f"campo requerido ausente: {field}")
    if "title" in fm and not (isinstance(fm["title"], str) and fm["title"].strip()):
        errs.append("title debe ser texto no vacío")
    if "type" in fm and fm["type"] not in TYPES:
        errs.append(f"type inválido: {fm['type']!r} (∈ {sorted(TYPES)})")
    if "tier" in fm and fm["tier"] not in TIERS:
        errs.append(f"tier inválido: {fm['tier']!r} (∈ {sorted(TIERS)})")
    if "tags" in fm and not isinstance(fm["tags"], list):
        errs.append("tags debe ser lista")
    if "confidence" in fm:
        c = fm["confidence"]
        if not isinstance(c, (int, float)) or isinstance(c, bool) or not (0.0 <= float(c) <= 1.0):
            errs.append(f"confidence fuera de rango [0,1]: {c!r}")
    for date_field in ("created", "last_reinforced", "valido_hasta",
                       "fecha_evento", "decay_aplicado", "archivado"):
        if date_field in fm and fm[date_field] is not None and not is_iso_date(fm[date_field]):
            errs.append(f"{date_field} no es fecha ISO (YYYY-MM-DD): {fm[date_field]!r}")
    if "decay_rate" in fm and fm["decay_rate"] not in DECAY_RATES:
        errs.append(f"decay_rate inválido: {fm['decay_rate']!r} (∈ {sorted(DECAY_RATES)})")
    if "sources" in fm and not isinstance(fm["sources"], list):
        errs.append("sources debe ser lista")
    if "relations" in fm:
        r = fm["relations"]
        if not (isinstance(r, dict) or r == [] or r is None):
            errs.append("relations debe ser mapa verbo→destino(s) o vacío")
    if "sensibilidad" in fm and fm["sensibilidad"] not in SENSIBILIDADES:
        errs.append(f"sensibilidad inválida: {fm['sensibilidad']!r} (∈ {sorted(SENSIBILIDADES)})")
    if "clase" in fm:
        if fm["clase"] not in CLASES:
            errs.append(f"clase inválida: {fm['clase']!r} (∈ {sorted(CLASES)})")
        elif fm["clase"] == "evento" and not fm.get("fecha_evento"):
            errs.append("clase: evento exige fecha_evento (gen-clase-temporal)")
    if "vigencia" in fm and fm["vigencia"] not in VIGENCIAS:
        errs.append(f"vigencia inválida: {fm['vigencia']!r} (∈ {sorted(VIGENCIAS)})")
    if "riesgo_inyeccion" in fm and not isinstance(fm["riesgo_inyeccion"], bool):
        errs.append("riesgo_inyeccion debe ser booleano")
    if "id_alias" in fm and not isinstance(fm["id_alias"], list):
        errs.append("id_alias debe ser lista")
    # gen-jerarquizacion-indice v2: reglas propias del hub
    if fm.get("type") == "hub":
        if fm.get("confidence") not in (1, 1.0):
            errs.append("página hub exige confidence: 1.0 (gen-jerarquizacion-indice)")
        if fm.get("sources"):
            errs.append("página hub exige sources: [] (gen-jerarquizacion-indice)")
        if fm.get("relations"):
            errs.append("página hub exige relations vacías (gen-jerarquizacion-indice)")
    return errs
