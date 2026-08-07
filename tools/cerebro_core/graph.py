"""Señales estructurales del grafo de enlaces — deterministas y sin dependencias.

Cubre el subconjunto **estructural** de lo que [[gen-graph-lens]] delega hoy a un
backend externo (graphify): componentes conexas, grado, hubs, huérfanas, puntos de
articulación y camino más corto. Todo es topología pura (BFS + Hopcroft-Tarjan
iterativo), así que corre con Python stdlib y da el MISMO resultado en cada
máquina — a diferencia de las señales semánticas (comunidades por modularidad,
"conexiones sorprendentes"), que siguen siendo territorio de la lente externa
porque dependen de un modelo.

Aporta además el detector de **enlaces sugeridos** (LNK-03): páginas que mencionan
en prosa el título/alias de otra página existente sin enlazarla. Es el complemento
preventivo de LNK-01 (enlace roto) y LNK-02 (huérfana), que solo avisan cuando el
daño ya existe.

Frontera de diseño: aquí NADA se reescribe. Otras herramientas del ecosistema
auto-insertan los wikilinks al escribir; CEREBRO solo PROPONE y el agente aplica
bajo compuerta — un detector que edita páginas por su cuenta violaría el principio
de mutación con compuerta y la regla de no sobrescribir lo que no creaste tú.

Invariantes de seguridad del sugeridor (no negociables):
- nunca sugiere una página `sensibilidad: confidencial` como destino: nombrarla
  expondría su título, que es metadato reidentificador ([[gen-confidencialidad]]);
- nunca toma como origen una página en cuarentena `riesgo_inyeccion: true`: su
  texto es dato no confiable y no debe dirigir la topología ([[gen-anti-inyeccion]]).
"""
from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field

from .vault import Vault

# Ámbitos analizables. `all` = el mismo alcance que el chequeo de enlaces roto
# de LINT (conocimiento + genoma + índice).
SCOPES: dict[str, tuple[str, ...]] = {
    "wiki": ("wiki/",),
    "genome": ("genome/",),
    "all": ("wiki/", "genome/", "index.md"),
}

# Destinos que un [[wikilink]] puede señalar: conocimiento y genoma. Los .md de
# la raíz (CLAUDE, AGENTS, README, log) son infraestructura y se citan por ruta.
DESTINOS_VALIDOS: tuple[str, ...] = ("wiki/", "genome/")

# Un término más corto que esto genera ruido (siglas, palabras comunes).
MIN_TERM_LEN = 5
# Tope de sugerencias por página: el detector propone, no inunda.
MAX_SUGERENCIAS_POR_PAGINA = 5

_URL_RE = re.compile(r"(?:https?://|www\.)\S+")
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_CODE_SPAN_RE = re.compile(r"`[^`\n]*`")
_WIKILINK_RE = re.compile(r"\[\[[^\]]*\]\]")


def in_scope(rel: str, prefixes: tuple[str, ...]) -> bool:
    return any(rel == p or rel.startswith(p) for p in prefixes)


# ── grafo de enlaces ────────────────────────────────────────────────────────

@dataclass
class LinkGraph:
    """Grafo dirigido de páginas; las métricas estructurales usan su vista no dirigida."""

    nodes: list[str] = field(default_factory=list)          # rel, orden determinista
    out: dict[str, set[str]] = field(default_factory=dict)  # aristas dirigidas
    adj: dict[str, set[str]] = field(default_factory=dict)  # vista no dirigida

    @property
    def edges(self) -> int:
        """Aristas no dirigidas distintas."""
        return sum(len(vs) for vs in self.adj.values()) // 2

    def grado(self, rel: str) -> int:
        return len(self.adj.get(rel, ()))

    def grado_salida(self, rel: str) -> int:
        return len(self.out.get(rel, ()))

    def grado_entrada(self, rel: str) -> int:
        return sum(1 for src, dsts in self.out.items() if rel in dsts)


def build(v: Vault, scope: str = "all") -> LinkGraph:
    """Construye el grafo de enlaces del ámbito pedido.

    Aristas = wikilinks del cuerpo ∪ destinos declarados en `relations`. Se
    conservan solo las que caen dentro del ámbito (un enlace a `docs/` no crea nodo).
    """
    prefixes = SCOPES[scope]
    nodes = sorted(p.rel for p in v.pages if in_scope(p.rel, prefixes))
    node_set = set(nodes)
    g = LinkGraph(nodes=nodes,
                  out={rel: set() for rel in nodes},
                  adj={rel: set() for rel in nodes})
    for rel in nodes:
        page = v.page_by_rel(rel)
        if page is None:
            continue
        targets = list(page.wikilinks) + [t for _, t in v.relations_of(page)]
        for raw in targets:
            dst = v.resolve_link(raw)
            if dst is None or dst == rel or dst not in node_set:
                continue
            g.out[rel].add(dst)
            g.adj[rel].add(dst)
            g.adj[dst].add(rel)
    return g


def componentes(g: LinkGraph) -> list[list[str]]:
    """Componentes conexas por BFS, ordenadas por tamaño desc. y primer nodo."""
    visto: set[str] = set()
    comps: list[list[str]] = []
    for start in g.nodes:
        if start in visto:
            continue
        cola = deque([start])
        visto.add(start)
        comp = [start]
        while cola:
            cur = cola.popleft()
            for nb in sorted(g.adj[cur]):
                if nb not in visto:
                    visto.add(nb)
                    comp.append(nb)
                    cola.append(nb)
        comps.append(sorted(comp))
    comps.sort(key=lambda c: (-len(c), c[0]))
    return comps


def huerfanas(g: LinkGraph) -> list[str]:
    """Nodos de grado 0 — segunda opinión estructural sobre LNK-02."""
    return [rel for rel in g.nodes if g.grado(rel) == 0]


def hubs(g: LinkGraph, umbral: int) -> list[tuple[str, int]]:
    """Nodos con grado ≥ umbral (el `hub_umbral` del manifiesto), por grado desc."""
    out = [(rel, g.grado(rel)) for rel in g.nodes if g.grado(rel) >= umbral]
    out.sort(key=lambda t: (-t[1], t[0]))
    return out


def puntos_de_articulacion(g: LinkGraph) -> list[str]:
    """Nodos cuya eliminación parte su componente (Hopcroft-Tarjan iterativo).

    Son las páginas-puente: si desaparecen, dos zonas del conocimiento quedan
    incomunicadas. Iterativo a propósito — un vault grande desbordaría la
    recursión de Python.
    """
    disc: dict[str, int] = {}
    low: dict[str, int] = {}
    padre: dict[str, str] = {}
    arts: set[str] = set()
    reloj = 0
    for raiz in g.nodes:
        if raiz in disc:
            continue
        disc[raiz] = low[raiz] = reloj
        reloj += 1
        hijos_raiz = 0
        pila: list[tuple[str, object]] = [(raiz, iter(sorted(g.adj[raiz])))]
        while pila:
            nodo, it = pila[-1]
            avanzo = False
            for nb in it:  # type: ignore[union-attr]
                if nb == padre.get(nodo):
                    continue
                if nb not in disc:
                    padre[nb] = nodo
                    disc[nb] = low[nb] = reloj
                    reloj += 1
                    if nodo == raiz:
                        hijos_raiz += 1
                    pila.append((nb, iter(sorted(g.adj[nb]))))
                    avanzo = True
                    break
                low[nodo] = min(low[nodo], disc[nb])
            if not avanzo:
                pila.pop()
                if pila:
                    p = pila[-1][0]
                    low[p] = min(low[p], low[nodo])
                    if p != raiz and low[nodo] >= disc[p]:
                        arts.add(p)
        if hijos_raiz > 1:
            arts.add(raiz)
    return sorted(arts)


def camino_mas_corto(g: LinkGraph, origen: str, destino: str) -> list[str] | None:
    """Camino mínimo en la vista no dirigida, o None si no hay ruta."""
    if origen not in g.adj or destino not in g.adj:
        return None
    if origen == destino:
        return [origen]
    prev: dict[str, str] = {origen: origen}
    cola = deque([origen])
    while cola:
        cur = cola.popleft()
        for nb in sorted(g.adj[cur]):
            if nb in prev:
                continue
            prev[nb] = cur
            if nb == destino:
                camino = [destino]
                while camino[-1] != origen:
                    camino.append(prev[camino[-1]])
                return list(reversed(camino))
            cola.append(nb)
    return None


# ── enlaces sugeridos (LNK-03) ──────────────────────────────────────────────

def texto_buscable(body: str) -> str:
    """Cuerpo sin código, URLs ni wikilinks ya puestos.

    Los cuatro se excluyen por la misma razón que en otras implementaciones de
    auto-enlazado: sugerir dentro de un bloque de código o de un `[[enlace]]`
    existente corrompe el contenido en vez de conectarlo.
    """
    clean = _FENCE_RE.sub(" ", body)
    clean = _CODE_SPAN_RE.sub(" ", clean)
    clean = _WIKILINK_RE.sub(" ", clean)
    clean = _URL_RE.sub(" ", clean)
    return clean


def _terminos_de(page) -> list[str]:
    """Términos por los que una página puede ser mencionada: basename, title, alias."""
    terms = {page.basename}
    if page.fm:
        title = page.fm.get("title")
        if isinstance(title, str):
            terms.add(title.strip())
        alias = page.fm.get("id_alias")
        if isinstance(alias, list):
            for a in alias:
                a = str(a).strip()
                if a:
                    terms.add(a)
                    terms.add(a.rsplit("/", 1)[-1])
    return sorted({t for t in terms if len(t) >= MIN_TERM_LEN})


def _menciona(texto_bajo: str, term: str) -> bool:
    """Coincidencia por palabra completa, sin cortar tokens con guion.

    `(?![\\w-])` evita que «gen-lint» dispare dentro de «gen-lint-v5».
    `(?!\\.[a-z0-9]{1,6}(?![\\w-]))` evita disparar sobre nombres de archivo
    aunque no vayan entre backticks: «events.jsonl» no es una mención de la
    página `events` (el punto de fin de oración —«… events. Y»— sí dispara,
    porque no le sigue una extensión pegada).
    """
    pat = re.compile(r"(?<![\w-])" + re.escape(term.lower())
                     + r"(?![\w-])(?!\.[a-z0-9]{1,6}(?![\w-]))")
    return bool(pat.search(texto_bajo))


def sugerencias(v: Vault, scope: str = "wiki",
                max_por_pagina: int = MAX_SUGERENCIAS_POR_PAGINA,
                ) -> list[tuple[str, str, str]]:
    """Devuelve (origen, destino, término) para menciones sin enlazar.

    Ámbito de ORIGEN = `scope` (por defecto `wiki/`, el mismo que LNK-02: las
    huérfanas son un problema del conocimiento, no del genoma). El destino puede
    ser cualquier página resoluble, porque enlazar una página de conocimiento a
    su gen es exactamente lo que se quiere.
    """
    prefixes = SCOPES[scope]
    destinos: list[tuple[str, list[str]]] = []
    for p in v.pages:
        # Destino legítimo = página de conocimiento o gen. Los .md de raíz
        # (CLAUDE/AGENTS/README/log) y las páginas `meta` como el índice son
        # infraestructura: se citan por ruta, no con [[wikilink]].
        if not in_scope(p.rel, DESTINOS_VALIDOS) or p.is_meta:
            continue
        if p.fm and p.fm.get("sensibilidad") == "confidencial":
            continue  # invariante: no nombrar lo confidencial
        terms = _terminos_de(p)
        if terms:
            destinos.append((p.rel, terms))

    out: list[tuple[str, str, str]] = []
    for src in v.pages:
        if not in_scope(src.rel, prefixes) or src.fm is None or src.is_meta:
            continue
        if src.fm.get("riesgo_inyeccion") is True:
            continue  # invariante: la cuarentena no dirige la topología
        ya_enlaza = set()
        for raw in list(src.wikilinks) + [t for _, t in v.relations_of(src)]:
            dst = v.resolve_link(raw)
            if dst:
                ya_enlaza.add(dst)
        texto = texto_buscable(src.body).lower()
        halladas: list[tuple[str, str]] = []
        for dst_rel, terms in destinos:
            if dst_rel == src.rel or dst_rel in ya_enlaza:
                continue
            hit = next((t for t in sorted(terms, key=lambda s: (-len(s), s))
                        if _menciona(texto, t)), None)
            if hit:
                halladas.append((dst_rel, hit))
        halladas.sort(key=lambda t: (-len(t[1]), t[0]))
        for dst_rel, term in halladas[:max_por_pagina]:
            out.append((src.rel, dst_rel, term))
    out.sort()
    return out


# ── reporte ─────────────────────────────────────────────────────────────────

def reporte(v: Vault, *, scope: str = "all", hub_umbral: int = 7) -> dict:
    """Señales estructurales en dict serializable (mismo orden en cada corrida)."""
    g = build(v, scope)
    comps = componentes(g)
    islas = [c for c in comps[1:]] if len(comps) > 1 else []
    return {
        "scope": scope,
        "hub_umbral": hub_umbral,
        "nodos": len(g.nodes),
        "aristas": g.edges,
        "componentes": [{"tamano": len(c), "paginas": c} for c in comps],
        "componente_mayor": len(comps[0]) if comps else 0,
        "islas": [p for c in islas for p in c],
        "huerfanas": huerfanas(g),
        "hubs": [{"pagina": r, "grado": d} for r, d in hubs(g, hub_umbral)],
        "puentes": puntos_de_articulacion(g),
        "sugerencias": [
            {"origen": s, "destino": d, "termino": t}
            for s, d, t in sugerencias(v, "wiki" if scope == "all" else scope)
        ],
    }


def render_text(rep: dict) -> str:
    out = [
        f"GRAFO ESTRUCTURAL · scope {rep['scope']} · "
        f"{rep['nodos']} nodos · {rep['aristas']} aristas · "
        f"{len(rep['componentes'])} componente(s)",
    ]
    if rep["nodos"] == 0:
        out.append("  (sin páginas en el ámbito: nada que analizar)")
        return "\n".join(out) + "\n"
    out.append(f"  componente mayor : {rep['componente_mayor']}/{rep['nodos']} páginas")
    out.append(f"  islas            : {len(rep['islas'])}"
               + (f" — {', '.join(rep['islas'][:8])}" if rep["islas"] else ""))
    out.append(f"  huérfanas        : {len(rep['huerfanas'])}"
               + (f" — {', '.join(rep['huerfanas'][:8])}" if rep["huerfanas"] else ""))
    if rep["hubs"]:
        out.append(f"  hubs (grado ≥ {rep['hub_umbral']}):")
        for h in rep["hubs"][:10]:
            out.append(f"    - {h['pagina']} (grado {h['grado']})")
    else:
        out.append(f"  hubs (grado ≥ {rep['hub_umbral']}): ninguno")
    if rep["puentes"]:
        out.append(f"  puentes (quitarlos parte el grafo): {len(rep['puentes'])}")
        for p in rep["puentes"][:10]:
            out.append(f"    - {p}")
    if rep["sugerencias"]:
        out.append(f"  enlaces sugeridos (LNK-03): {len(rep['sugerencias'])}")
        for s in rep["sugerencias"][:10]:
            out.append(f"    - {s['origen']} → {s['destino']} (menciona «{s['termino']}»)")
    out.append("  Señales para PROPONER, no para aplicar: hubs → CONSOLIDATE / "
               "hub_umbral · islas y huérfanas → LINT · puentes → riesgo de "
               "fragmentación · comunidades y semántica siguen en la lente externa.")
    return "\n".join(out) + "\n"
