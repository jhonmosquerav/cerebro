"""Render NATIVO del grafo: JSON Canvas 1.0 (`.canvas`), sin backend ni LLM.

Es la tercera salida de la mitad estructural de GRAPH ([[gen-graph-lens]]): el mismo
grafo de enlaces que `graph` reporta en texto, escrito en el formato abierto que
Obsidian abre de serie (spec: github.com/obsidianmd/jsoncanvas). Complementa —no
sustituye— a la lente externa: aquí no hay comunidades ni resúmenes, solo topología.

Invariante duro, idéntico al staging de la lente externa: el `.canvas` SALE del
proceso (se abre, se copia, se comparte), así que aplica la **allowlist fail-closed**
de [[gen-confidencialidad]] y [[gen-anti-inyeccion]]:
- entra una página de `wiki/` solo si declara EXPLÍCITAMENTE `sensibilidad: publico`
  o `interno` y no está en cuarentena (`riesgo_inyeccion: true`);
- sin campo, con typo, con frontmatter ilegible o en cuarentena → NO entra, y tampoco
  entran las aristas que la tocan. Ni su ruta, ni su slug, ni su título aparecen;
- el genoma y `index.md` entran como estructura (son reglas y mapa, no datos).

Salida derivada y regenerable: nunca fuente de verdad, no se versiona.
"""
from __future__ import annotations

import hashlib
import json
import math

from . import graph as graph_mod
from .vault import Page, Vault

# Orden de columnas (grupos) de izquierda a derecha. Lo que no esté aquí va al final.
GRUPOS = ("index", "semantic", "procedural", "working", "episodic", "archive",
          "wiki", "genes", "capsulas", "genoma")
# Colores preset de JSON Canvas: 1 rojo · 2 naranja · 3 amarillo · 4 verde · 5 cian · 6 morado.
COLOR_GRUPO = {
    "index": "3", "semantic": "4", "procedural": "5", "working": "2",
    "episodic": "6", "archive": None, "wiki": None,
    "genes": "#4134E7", "capsulas": "#4134E7", "genoma": "#4134E7",
}
COLOR_VERBO = {"contradice": "1", "reemplaza": "2"}
COLOR_HUB = "3"

NODE_W, NODE_H, GAP = 260, 60, 40
GROUP_PAD, GROUP_LABEL, GROUP_GAP = 60, 40, 200


def permitida(page: Page) -> bool:
    """Allowlist fail-closed (misma regla que el staging de la lente externa)."""
    if page.fm is None:
        return False
    if page.rel == "index.md" or page.rel.startswith("genome/"):
        return True  # estructura: reglas y mapa, no datos
    if not page.rel.startswith("wiki/"):
        return False
    if page.fm.get("sensibilidad") not in ("publico", "interno"):
        return False
    if page.fm.get("riesgo_inyeccion") is True:
        return False
    return True


def grupo_de(rel: str) -> str:
    if rel == "index.md":
        return "index"
    if rel.startswith("genome/genes/"):
        return "genes"
    if rel.startswith("genome/capsules/"):
        return "capsulas"
    if rel.startswith("genome/"):
        return "genoma"  # company-profile y afines
    parts = rel.split("/")
    if parts[0] == "wiki" and len(parts) >= 3:
        return parts[1]  # tier
    if parts[0] == "wiki":
        return "wiki"    # página en la raíz de wiki/ (sin tier)
    return "otros"


def _node_id(rel: str) -> str:
    return "n-" + hashlib.sha1(rel.encode("utf-8")).hexdigest()[:12]


def render(v: Vault, *, scope: str = "all", hub_umbral: int = 7) -> dict:
    """Devuelve el canvas como dict: `nodes`, `edges` y un bloque `cerebro` con
    los conteos (lo consume la CLI; `dumps` no lo escribe al archivo)."""
    g = graph_mod.build(v, scope)
    en_scope = [p for p in (v.page_by_rel(r) for r in g.nodes) if p is not None]
    ok = [p for p in en_scope if permitida(p)]
    ok_set = {p.rel for p in ok}
    excluidas = len(en_scope) - len(ok)
    grado = {r: sum(1 for n in g.adj[r] if n in ok_set) for r in ok_set}

    por_grupo: dict[str, list[str]] = {}
    for p in ok:
        por_grupo.setdefault(grupo_de(p.rel), []).append(p.rel)
    orden = [n for n in GRUPOS if n in por_grupo] + sorted(k for k in por_grupo if k not in GRUPOS)

    nodes: list[dict] = []
    ids: dict[str, str] = {}
    x0 = 0
    for gname in orden:
        rels = sorted(por_grupo[gname], key=lambda r: (-grado[r], r))
        n = len(rels)
        cols = max(1, math.ceil(math.sqrt(n)))
        rows = math.ceil(n / cols)
        gw = GROUP_PAD * 2 + cols * NODE_W + (cols - 1) * GAP
        gh = GROUP_PAD * 2 + GROUP_LABEL + rows * NODE_H + (rows - 1) * GAP
        group = {"id": f"g-{gname}", "type": "group", "label": gname,
                 "x": x0, "y": 0, "width": gw, "height": gh}
        if COLOR_GRUPO.get(gname):
            group["color"] = COLOR_GRUPO[gname]
        nodes.append(group)
        for i, rel in enumerate(rels):
            c, r_ = i % cols, i // cols
            nid = _node_id(rel)
            ids[rel] = nid
            node = {"id": nid, "type": "file", "file": rel,
                    "x": x0 + GROUP_PAD + c * (NODE_W + GAP),
                    "y": GROUP_PAD + GROUP_LABEL + r_ * (NODE_H + GAP),
                    "width": NODE_W, "height": NODE_H}
            if grado[rel] > hub_umbral:
                node["color"] = COLOR_HUB
            nodes.append(node)
        x0 += gw + GROUP_GAP

    edges: list[dict] = []
    for src in sorted(ok_set):
        page = v.page_by_rel(src)
        etiquetas: dict[str, str] = {}
        if page is not None:
            for verb, tgt in v.relations_of(page):
                dst = v.resolve_link(tgt)
                if dst:
                    etiquetas.setdefault(dst, verb)
        for dst in sorted(g.out[src]):
            if dst not in ok_set:
                continue
            e = {"id": f"e-{ids[src][2:]}-{ids[dst][2:]}",
                 "fromNode": ids[src], "toNode": ids[dst]}
            if dst in etiquetas:
                e["label"] = etiquetas[dst]
                if COLOR_VERBO.get(etiquetas[dst]):
                    e["color"] = COLOR_VERBO[etiquetas[dst]]
            edges.append(e)

    leyenda = {
        "id": "t-leyenda", "type": "text", "x": 0, "y": -220, "width": 720, "height": 160,
        "text": (f"**CEREBRO · grafo estructural** (scope `{scope}`)\n\n"
                 f"{len(ok)} nodos · {len(edges)} aristas · "
                 f"{excluidas} página(s) excluida(s) por allowlist fail-closed "
                 f"(confidencial, sin `sensibilidad` explícita o en cuarentena).\n"
                 f"Amarillo = hub (grado > {hub_umbral}). Rojo = `contradice`, "
                 f"naranja = `reemplaza`. Derivado y regenerable: "
                 f"`python tools/cerebro.py graph --canvas <ruta>`. No es fuente de verdad."),
    }
    nodes.insert(0, leyenda)
    return {
        "nodes": nodes,
        "edges": edges,
        "cerebro": {"scope": scope, "hub_umbral": hub_umbral, "nodos": len(ok),
                    "aristas": len(edges), "excluidas_por_allowlist": excluidas},
    }


def dumps(data: dict) -> str:
    """Serializa SOLO lo que la spec JSON Canvas define (nodes, edges), estable."""
    return json.dumps({"nodes": data["nodes"], "edges": data["edges"]},
                      ensure_ascii=False, indent=1, sort_keys=True) + "\n"
