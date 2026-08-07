"""Tests de las señales estructurales del grafo y del sugeridor de enlaces (LNK-03)."""
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import graph
from cerebro_core import lint
from cerebro_core.vault import load_vault

REPO = Path(__file__).resolve().parent.parent
LIMPIO = REPO / "tests" / "fixtures" / "vault-limpio"

PLANTILLA = """---
title: {title}
type: {type}
tier: {tier}
tags: [t]
confidence: 0.8
created: 2026-07-01
last_reinforced: 2026-07-10
decay_rate: medium
sources: []
relations: {relations}
{extra}---
{body}
"""


def pagina(root: Path, rel: str, **kw):
    defaults = dict(title=Path(rel).stem, type="concepto",
                    tier=rel.split("/")[1] if rel.startswith("wiki/") else "semantic",
                    relations="{}", extra="", body="Texto.")
    defaults.update(kw)
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(PLANTILLA.format(**defaults), encoding="utf-8")


def grafo_de(aristas: list[tuple[str, str]], nodos: list[str] | None = None) -> graph.LinkGraph:
    """Construye un LinkGraph a mano — para probar la topología sin tocar disco."""
    todos = set(nodos or [])
    for a, b in aristas:
        todos.add(a)
        todos.add(b)
    g = graph.LinkGraph(nodes=sorted(todos),
                        out={n: set() for n in todos},
                        adj={n: set() for n in todos})
    for a, b in aristas:
        g.out[a].add(b)
        g.adj[a].add(b)
        g.adj[b].add(a)
    return g


class TestTopologia(unittest.TestCase):
    def test_componentes_y_orden(self):
        g = grafo_de([("a", "b"), ("b", "c"), ("x", "y")], nodos=["solo"])
        comps = graph.componentes(g)
        self.assertEqual([len(c) for c in comps], [3, 2, 1])
        self.assertEqual(comps[0], ["a", "b", "c"])
        self.assertEqual(comps[2], ["solo"])

    def test_huerfanas_es_grado_cero(self):
        g = grafo_de([("a", "b")], nodos=["suelta"])
        self.assertEqual(graph.huerfanas(g), ["suelta"])

    def test_hubs_por_umbral_y_grado_desc(self):
        # h tiene grado 3; m, 1 y 2 tienen grado 2; 3 tiene grado 1.
        g = grafo_de([("h", "1"), ("h", "2"), ("h", "3"), ("m", "1"), ("m", "2")])
        self.assertEqual(graph.hubs(g, 3), [("h", 3)])
        self.assertEqual(graph.hubs(g, 2),
                         [("h", 3), ("1", 2), ("2", 2), ("m", 2)])  # grado desc, luego nombre
        self.assertEqual(graph.hubs(g, 99), [])

    def test_articulacion_en_camino(self):
        # a - b - c : quitar b parte el grafo; quitar a o c no.
        g = grafo_de([("a", "b"), ("b", "c")])
        self.assertEqual(graph.puntos_de_articulacion(g), ["b"])

    def test_articulacion_en_ciclo_no_hay(self):
        g = grafo_de([("a", "b"), ("b", "c"), ("c", "a")])
        self.assertEqual(graph.puntos_de_articulacion(g), [])

    def test_articulacion_dos_triangulos_unidos(self):
        # Dos triángulos que comparten el puente p-q: ambos son articulación.
        g = grafo_de([("a", "b"), ("b", "p"), ("p", "a"),
                      ("p", "q"),
                      ("q", "x"), ("x", "y"), ("y", "q")])
        self.assertEqual(graph.puntos_de_articulacion(g), ["p", "q"])

    def test_articulacion_raiz_con_dos_hijos(self):
        g = grafo_de([("r", "a"), ("r", "b")])
        self.assertEqual(graph.puntos_de_articulacion(g), ["r"])

    def test_camino_mas_corto(self):
        g = grafo_de([("a", "b"), ("b", "c"), ("c", "d"), ("a", "d")])
        self.assertEqual(graph.camino_mas_corto(g, "a", "a"), ["a"])
        camino = graph.camino_mas_corto(g, "a", "c")
        self.assertEqual(len(camino), 3)          # a-b-c o a-d-c, ambos 2 saltos
        self.assertEqual((camino[0], camino[-1]), ("a", "c"))

    def test_camino_inexistente_y_nodo_ausente(self):
        g = grafo_de([("a", "b"), ("x", "y")])
        self.assertIsNone(graph.camino_mas_corto(g, "a", "x"))
        self.assertIsNone(graph.camino_mas_corto(g, "a", "fantasma"))

    def test_grafo_grande_no_desborda_recursion(self):
        """Camino de 3000 nodos: la versión recursiva moriría aquí."""
        aristas = [(f"n{i:04d}", f"n{i + 1:04d}") for i in range(3000)]
        g = grafo_de(aristas)
        arts = graph.puntos_de_articulacion(g)
        self.assertEqual(len(arts), 2999)         # todos menos los dos extremos
        self.assertNotIn("n0000", arts)


class TestGrafoDelVault(unittest.TestCase):
    def test_aristas_desde_cuerpo_y_relations(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/a.md", body="Menciono a [[b]].")
            pagina(root, "wiki/semantic/b.md", relations='{ usa: "[[c]]" }')
            pagina(root, "wiki/semantic/c.md")
            g = graph.build(load_vault(root), "wiki")
            self.assertEqual(g.edges, 2)
            self.assertEqual(g.grado("wiki/semantic/b.md"), 2)   # entrante + saliente
            self.assertEqual(g.grado_salida("wiki/semantic/b.md"), 1)
            self.assertEqual(g.grado_entrada("wiki/semantic/b.md"), 1)

    def test_enlace_fuera_del_ambito_no_crea_arista(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/a.md", body="Cito [[gen-x]].")
            (root / "genome" / "genes").mkdir(parents=True)
            (root / "genome" / "genes" / "gen-x.md").write_text(
                "---\nid: gen-x\nstatus: active\nversion: 1\n---\nRegla.\n",
                encoding="utf-8")
            v = load_vault(root)
            self.assertEqual(graph.build(v, "wiki").edges, 0)
            self.assertEqual(graph.build(v, "all").edges, 1)

    def test_reporte_determinista(self):
        v = load_vault(LIMPIO)
        r1 = graph.reporte(v, scope="all", hub_umbral=7)
        r2 = graph.reporte(load_vault(LIMPIO), scope="all", hub_umbral=7)
        self.assertEqual(r1, r2)
        self.assertEqual(graph.render_text(r1), graph.render_text(r2))

    def test_reporte_vault_sin_paginas(self):
        with tempfile.TemporaryDirectory() as td:
            rep = graph.reporte(load_vault(Path(td)), scope="wiki")
            self.assertEqual(rep["nodos"], 0)
            self.assertIn("nada que analizar", graph.render_text(rep))


class TestSugerencias(unittest.TestCase):
    def _sug(self, root: Path):
        return graph.sugerencias(load_vault(root), "wiki")

    def test_mencion_sin_enlazar_se_sugiere(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Hablo de fuente-clave aquí.")
            pagina(root, "wiki/semantic/fuente-clave.md")
            self.assertEqual(
                self._sug(root),
                [("wiki/semantic/origen.md", "wiki/semantic/fuente-clave.md",
                  "fuente-clave")])

    def test_ya_enlazada_por_cuerpo_no_se_sugiere(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md",
                   body="Hablo de [[fuente-clave]] y de fuente-clave otra vez.")
            pagina(root, "wiki/semantic/fuente-clave.md")
            self.assertEqual(self._sug(root), [])

    def test_ya_enlazada_por_relations_no_se_sugiere(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Hablo de fuente-clave.",
                   relations='{ usa: "[[fuente-clave]]" }')
            pagina(root, "wiki/semantic/fuente-clave.md")
            self.assertEqual(self._sug(root), [])

    def test_codigo_urls_y_wikilinks_se_excluyen(self):
        cuerpo = (
            "```\nfuente-clave en bloque\n```\n"
            "Inline `fuente-clave` y URL https://x.dev/fuente-clave y [[otra-cosa|fuente-clave]].\n"
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body=cuerpo)
            pagina(root, "wiki/semantic/fuente-clave.md")
            pagina(root, "wiki/semantic/otra-cosa.md")
            self.assertEqual(self._sug(root), [])

    def test_destino_confidencial_nunca_se_nombra(self):
        """gen-confidencialidad: el título es metadato reidentificador."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Hablo de nomina-secreta.")
            pagina(root, "wiki/semantic/nomina-secreta.md",
                   extra="sensibilidad: confidencial\n")
            self.assertEqual(self._sug(root), [])

    def test_origen_en_cuarentena_no_dirige_la_topologia(self):
        """gen-anti-inyeccion: su texto es dato no confiable."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Hablo de fuente-clave.",
                   extra="riesgo_inyeccion: true\n")
            pagina(root, "wiki/semantic/fuente-clave.md")
            self.assertEqual(self._sug(root), [])

    def test_termino_corto_no_dispara(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Menciono abc por ahí.")
            pagina(root, "wiki/semantic/abc.md")
            self.assertEqual(self._sug(root), [])

    def test_no_corta_tokens_con_guion(self):
        """«gen-lint» no debe disparar dentro de «gen-lint-v5»."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Aplico gen-lint-v5 hoy.")
            pagina(root, "wiki/semantic/gen-lint.md")
            self.assertEqual(self._sug(root), [])

    def test_nombre_de_archivo_no_dispara(self):
        """«events.jsonl» o «ai-act.md» sin backticks no son menciones de página."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md",
                   body="Todo queda en events.jsonl y el acta vive en ai-act.md, sin backticks.")
            pagina(root, "wiki/semantic/events.md")
            pagina(root, "wiki/semantic/ai-act.md")
            self.assertEqual(self._sug(root), [])

    def test_punto_de_fin_de_oracion_si_dispara(self):
        """El veto es solo para `termino.ext`: el punto de fin de oración no lo activa."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Hablo de fuente-clave. Y sigo.")
            pagina(root, "wiki/semantic/fuente-clave.md")
            self.assertEqual([s[2] for s in self._sug(root)], ["fuente-clave"])

    def test_extension_de_mas_de_seis_chars_no_es_archivo(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md",
                   body="El paquete events.jsonlines corre solo.")
            pagina(root, "wiki/semantic/events.md")
            self.assertEqual([s[2] for s in self._sug(root)], ["events"])

    def test_no_se_sugiere_a_si_misma(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/fuente-clave.md",
                   body="Yo soy fuente-clave.")
            self.assertEqual(self._sug(root), [])

    def test_alias_dispara_la_sugerencia(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Hablo del Banco Central.")
            pagina(root, "wiki/semantic/banrep.md",
                   extra='id_alias: ["Banco Central"]\n')
            sug = self._sug(root)
            self.assertEqual([s[2] for s in sug], ["Banco Central"])

    def test_pagina_meta_no_es_origen_ni_destino(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/panel.md", type="meta",
                   body="Hablo de fuente-clave.")
            pagina(root, "wiki/semantic/fuente-clave.md", body="Vengo del panel.")
            self.assertEqual(self._sug(root), [])

    def test_tope_por_pagina(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cuerpo = " ".join(f"destino-{i:02d}" for i in range(9))
            pagina(root, "wiki/semantic/origen.md", body=cuerpo)
            for i in range(9):
                pagina(root, f"wiki/semantic/destino-{i:02d}.md")
            self.assertEqual(len(self._sug(root)), graph.MAX_SUGERENCIAS_POR_PAGINA)

    def test_orden_determinista(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="beta-larga y alfa-corta.")
            pagina(root, "wiki/semantic/alfa-corta.md")
            pagina(root, "wiki/semantic/beta-larga.md")
            self.assertEqual(self._sug(root), self._sug(root))
            self.assertEqual(sorted(self._sug(root)), self._sug(root))


class TestIntegracionLint(unittest.TestCase):
    def test_lnk03_aparece_como_info(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/origen.md", body="Hablo de fuente-clave.")
            pagina(root, "wiki/semantic/fuente-clave.md", body="Nadie me enlaza.")
            import datetime
            rep = lint.run(root, as_of=datetime.date(2026, 7, 12))
            lnk03 = [f for f in rep.findings if f.code == "LNK-03"]
            self.assertEqual(len(lnk03), 1)
            self.assertEqual(lnk03[0].severity, "info")
            self.assertIn("fuente-clave", lnk03[0].detail)
            self.assertEqual(rep.exit_code(strict=False), 0,
                             "una sugerencia no puede hacer fallar el lint")

    def test_vault_limpio_sigue_sin_hallazgos(self):
        """El fixture canónico no debe ganar ruido por el detector nuevo."""
        import datetime
        rep = lint.run(LIMPIO, as_of=datetime.date(2026, 7, 12))
        self.assertEqual([f.render() for f in rep.findings], [])


if __name__ == "__main__":
    unittest.main()
