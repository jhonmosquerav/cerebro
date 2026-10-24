"""Catálogo de blueprints de sector con versiones y requisito mínimo (Fase 4.3).

Patrón tomado de obsidian-releases: cada blueprint lleva su identidad dentro del archivo
(`blueprint: {id, version, min_cerebro}`, como `manifest.json`), el catálogo
`onboard/blueprints/catalog.yaml` los indexa con historial (`community-plugins.json` +
`versions.json`) y `verify` prueba que coinciden. El bloque es PROCEDENCIA, no
configuración: `init --blueprint` lo copia al manifiesto y `company-profile.md` no lo
renderiza, así que el genoma que produce un manifiesto no cambia (worked/ sigue byte a byte).

Detectores (todos error, deterministas):
  CAT-01 catálogo ilegible o entrada sin los campos/tipos exigidos
  CAT-02 entrada sin archivo, archivo sin entrada, o id ≠ nombre de archivo
  CAT-03 el bloque `blueprint:` del archivo falta o discrepa de la entrada
  CAT-04 `genes` del catálogo ≠ ids de `seed_genes` del archivo (en orden)
  CAT-05 historial `versions` vacío, no creciente o que no termina en la versión actual
  CAT-06 `min_cerebro` mayor que la versión instalada, o `cerebro_version` ≠ __version__
"""
from __future__ import annotations

import re
from pathlib import Path

from . import __version__, miniyaml
from .findings import Finding, sort_findings

CATALOG_REL = "onboard/blueprints/catalog.yaml"
BLUEPRINTS_REL = "onboard/blueprints"
MANIFEST_REL = "onboard/company.yaml"
CAMPOS_ENTRADA = ("id", "name", "file", "version", "min_cerebro", "origen", "genes", "versions")
ORIGENES = ("simulacion", "normativo", "piloto")

_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def parse_semver(value) -> tuple[int, int, int]:
    """`X.Y.Z` estricto → tupla comparable. Cualquier otra cosa es ValueError."""
    if not isinstance(value, str):
        raise ValueError(f"semver inválido: {value!r} (se espera 'X.Y.Z' como cadena)")
    m = _SEMVER_RE.match(value.strip())
    if not m:
        raise ValueError(f"semver inválido: {value!r} (se espera 'X.Y.Z')")
    return tuple(int(x) for x in m.groups())  # type: ignore[return-value]


def installed_version() -> str:
    return __version__


def has_catalog(root: Path | str) -> bool:
    return (Path(root) / CATALOG_REL).is_file()


def load_catalog(root: Path | str) -> dict:
    p = Path(root) / CATALOG_REL
    raw = miniyaml.parse(p.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _bloque_de(path: Path) -> dict | None:
    raw = miniyaml.parse(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    b = raw.get("blueprint")
    return b if isinstance(b, dict) else None


def _seed_ids(path: Path) -> list[str]:
    raw = miniyaml.parse(path.read_text(encoding="utf-8"))
    seeds = raw.get("seed_genes") if isinstance(raw, dict) else None
    return [g.get("id") for g in (seeds or []) if isinstance(g, dict)]


# ── validación ────────────────────────────────────────────────────────────────

def check(root: Path | str) -> list[Finding]:
    """Todos los detectores CAT-xx sobre el catálogo del vault. Sin catálogo ⇒ []."""
    root = Path(root)
    if not has_catalog(root):
        return []
    out: list[Finding] = []
    rel = CATALOG_REL

    def err(code: str, detail: str, path: str = rel) -> None:
        out.append(Finding(code, "error", path, detail))

    try:
        cat = load_catalog(root)
    except Exception as e:  # miniyaml.MiniYamlError u otro
        err("CAT-01", f"catálogo ilegible: {e}")
        return out
    if not isinstance(cat.get("catalog_version"), int) or isinstance(cat.get("catalog_version"), bool):
        err("CAT-01", "catalog_version debe ser entero")
    entradas = cat.get("blueprints")
    if not isinstance(entradas, list) or not entradas:
        err("CAT-01", "blueprints debe ser una lista no vacía")
        return sort_findings(out)

    # CAT-06 (catálogo): la versión con la que se validó es la instalada
    if cat.get("cerebro_version") != installed_version():
        err("CAT-06", f"cerebro_version del catálogo es {cat.get('cerebro_version')!r} y "
                      f"tools/ es {installed_version()}: re-valida el catálogo al subir versión")

    carpeta = root / BLUEPRINTS_REL
    archivos = sorted(p.name for p in carpeta.glob("*.yaml") if p.name != "catalog.yaml")
    vistos: dict[str, dict] = {}
    for i, e in enumerate(entradas):
        if not isinstance(e, dict):
            err("CAT-01", f"blueprints[{i}] debe ser mapa")
            continue
        faltan = [c for c in CAMPOS_ENTRADA if c not in e]
        if faltan:
            err("CAT-01", f"blueprints[{i}] ({e.get('id', 'sin id')}): faltan {', '.join(faltan)}")
            continue
        eid = e["id"]
        if not isinstance(eid, str) or not _SLUG_RE.match(eid):
            err("CAT-01", f"blueprints[{i}].id inválido: {eid!r} (slug en minúsculas)")
            continue
        if eid in vistos:
            err("CAT-02", f"id duplicado en el catálogo: {eid!r}")
            continue
        vistos[eid] = e
        tipos_ok = True
        for campo in ("version", "min_cerebro"):
            try:
                parse_semver(e[campo])
            except ValueError as ex:
                err("CAT-01", f"{eid}: {campo} — {ex}")
                tipos_ok = False
        if not isinstance(e["genes"], list):
            err("CAT-01", f"{eid}: genes debe ser lista")
            tipos_ok = False
        if not isinstance(e["versions"], list):
            err("CAT-01", f"{eid}: versions debe ser lista")
            tipos_ok = False
        if e["origen"] not in ORIGENES:
            err("CAT-01", f"{eid}: origen inválido {e['origen']!r} (∈ {list(ORIGENES)})")
        if not tipos_ok:
            continue
        # CAT-02: archivo
        if e["file"] != f"{eid}.yaml":
            err("CAT-02", f"{eid}: file debe ser '{eid}.yaml' (id = nombre del archivo), es {e['file']!r}")
        archivo = carpeta / str(e["file"])
        if not archivo.is_file():
            err("CAT-02", f"{eid}: el archivo {e['file']} no existe en {BLUEPRINTS_REL}/")
            continue
        rel_arch = f"{BLUEPRINTS_REL}/{e['file']}"
        # CAT-03: bloque del archivo
        try:
            bloque = _bloque_de(archivo)
        except Exception as ex:
            err("CAT-03", f"{eid}: blueprint ilegible — {ex}", rel_arch)
            continue
        if bloque is None:
            err("CAT-03", f"{eid}: el blueprint no declara el bloque `blueprint:` "
                          f"(id, version, min_cerebro)", rel_arch)
        else:
            for campo in ("id", "version", "min_cerebro"):
                if bloque.get(campo) != e[campo]:
                    err("CAT-03", f"{eid}: blueprint.{campo} del archivo es {bloque.get(campo)!r} "
                                  f"y el catálogo dice {e[campo]!r}", rel_arch)
        # CAT-04: genes
        try:
            seeds = _seed_ids(archivo)
        except Exception as ex:
            err("CAT-04", f"{eid}: seed_genes ilegibles — {ex}", rel_arch)
            seeds = None
        if seeds is not None and list(e["genes"]) != seeds:
            err("CAT-04", f"{eid}: genes del catálogo {list(e['genes'])} ≠ seed_genes del "
                          f"archivo {seeds}")
        # CAT-05: historial
        hist = e["versions"]
        if not hist:
            err("CAT-05", f"{eid}: versions está vacío")
        else:
            prev = None
            ok_hist = True
            for j, h in enumerate(hist):
                if not isinstance(h, dict) or "version" not in h or "min_cerebro" not in h \
                        or "fecha" not in h or "cambios" not in h:
                    err("CAT-05", f"{eid}: versions[{j}] debe traer version, min_cerebro, fecha, cambios")
                    ok_hist = False
                    break
                try:
                    v = parse_semver(h["version"])
                    parse_semver(h["min_cerebro"])
                except ValueError as ex:
                    err("CAT-05", f"{eid}: versions[{j}] — {ex}")
                    ok_hist = False
                    break
                if prev is not None and v <= prev:
                    err("CAT-05", f"{eid}: versions no es estrictamente creciente en {h['version']}")
                    ok_hist = False
                    break
                prev = v
            if ok_hist:
                ultima = hist[-1]
                if ultima["version"] != e["version"]:
                    err("CAT-05", f"{eid}: la última versión del historial es {ultima['version']} "
                                  f"y la entrada declara {e['version']}")
                elif ultima["min_cerebro"] != e["min_cerebro"]:
                    err("CAT-05", f"{eid}: min_cerebro del historial ({ultima['min_cerebro']}) ≠ "
                                  f"el de la entrada ({e['min_cerebro']})")
        # CAT-06: el template no distribuye lo que no puede correr
        if parse_semver(e["min_cerebro"]) > parse_semver(installed_version()):
            err("CAT-06", f"{eid}: exige CEREBRO ≥ {e['min_cerebro']} y tools/ es "
                          f"{installed_version()}")
    # CAT-02: archivos sin entrada
    for nombre in archivos:
        if nombre[:-5] not in vistos:
            err("CAT-02", f"{nombre} está en {BLUEPRINTS_REL}/ y no en el catálogo",
                f"{BLUEPRINTS_REL}/{nombre}")
    return sort_findings(out)


# ── estado del manifiesto del vault frente al catálogo ───────────────────────

def estado_manifiesto(root: Path | str) -> dict:
    """De qué blueprint nació `onboard/company.yaml` y si está al día con el catálogo.

    estado ∈ sin-manifiesto · sin-bloque (manifiesto artesanal, legítimo) · desconocido
    (id que el catálogo no lista) · desactualizado · adelantado · al-dia.
    """
    root = Path(root)
    p = root / MANIFEST_REL
    base = {"estado": "sin-manifiesto", "id": None, "version_local": None, "version_catalogo": None}
    if not p.is_file():
        return base
    try:
        bloque = _bloque_de(p)
    except Exception:
        return {**base, "estado": "sin-bloque"}
    if not bloque:
        return {**base, "estado": "sin-bloque"}
    bid = bloque.get("id")
    vloc = bloque.get("version")
    out = {**base, "id": bid, "version_local": vloc}
    if not has_catalog(root):
        return {**out, "estado": "desconocido"}
    try:
        cat = load_catalog(root)
        entrada = next((e for e in cat.get("blueprints") or []
                        if isinstance(e, dict) and e.get("id") == bid), None)
    except Exception:
        entrada = None
    if entrada is None:
        return {**out, "estado": "desconocido"}
    vcat = entrada.get("version")
    out["version_catalogo"] = vcat
    try:
        a, b = parse_semver(vloc), parse_semver(vcat)
    except ValueError:
        return {**out, "estado": "desconocido"}
    if a < b:
        return {**out, "estado": "desactualizado"}
    if a > b:
        return {**out, "estado": "adelantado"}
    return {**out, "estado": "al-dia"}


def resumen(root: Path | str) -> dict:
    """Vista JSON estable: entradas del catálogo + hallazgos + estado del manifiesto."""
    root = Path(root)
    entradas: list[dict] = []
    if has_catalog(root):
        try:
            for e in load_catalog(root).get("blueprints") or []:
                if isinstance(e, dict):
                    entradas.append({k: e.get(k) for k in CAMPOS_ENTRADA if k != "versions"}
                                    | {"versiones": len(e.get("versions") or [])})
        except Exception:
            pass
    return {
        "cerebro_version": installed_version(),
        "catalogo": CATALOG_REL if has_catalog(root) else None,
        "blueprints": entradas,
        "hallazgos": [{"code": f.code, "severity": f.severity, "path": f.path, "detail": f.detail}
                      for f in check(root)],
        "manifiesto": estado_manifiesto(root),
    }
