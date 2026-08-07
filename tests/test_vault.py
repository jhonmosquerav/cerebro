"""Tests del modelo de vault y resolución de wikilinks."""
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import vault as vlt

REPO = Path(__file__).resolve().parent.parent

PAGINA = """---
title: {title}
type: {type}
tier: {tier}
tags: [t]
confidence: 0.7
created: 2026-07-01
last_reinforced: 2026-07-10
decay_rate: medium
sources: []
relations: {relations}
---
{body}
"""


def escribir(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def mini_vault(td: str) -> Path:
    root = Path(td)
    escribir(root, "index.md", "---\ntitle: idx\ntype: meta\n---\n# Índice\n[[concepto-a]]\n")
    escribir(root, "wiki/semantic/concepto-a.md", PAGINA.format(
        title="Concepto A", type="concepto", tier="semantic",
        relations='{ usa: "[[Entidad B]]" }', body="Cuerpo con [[entidad-b]]."))
    escribir(root, "wiki/semantic/entidad-b.md", PAGINA.format(
        title="Entidad B", type="entidad", tier="semantic",
        relations="{}", body="Sin enlaces."))
    escribir(root, "wiki/working/nota.md", PAGINA.format(
        title="Nota suelta", type="observacion", tier="working",
        relations="[]", body="Nada."))
    escribir(root, "genome/genes/gen-demo.md",
             "---\nid: gen-demo\ntrigger: demo\nstatus: active\nversion: 1\n---\nRegla.\n")
    return root


class TestCarga(unittest.TestCase):
    def test_carga_y_clasifica(self):
        with tempfile.TemporaryDirectory() as td:
            v = vlt.load_vault(mini_vault(td))
            rels = sorted(p.rel for p in v.wiki_pages)
            self.assertEqual(rels, [
                "wiki/semantic/concepto-a.md",
                "wiki/semantic/entidad-b.md",
                "wiki/working/nota.md",
            ])
            self.assertEqual([g.rel for g in v.genes], ["genome/genes/gen-demo.md"])
            idx = v.page_by_rel("index.md")
            self.assertTrue(idx.is_meta)
            a = v.page_by_rel("wiki/semantic/concepto-a.md")
            self.assertEqual(a.tier_from_path, "semantic")
            self.assertEqual(a.wikilinks, ["entidad-b"])

    def test_resolucion_de_links(self):
        with tempfile.TemporaryDirectory() as td:
            v = vlt.load_vault(mini_vault(td))
            self.assertEqual(v.resolve_link("entidad-b"), "wiki/semantic/entidad-b.md")
            self.assertEqual(v.resolve_link("Entidad B"), "wiki/semantic/entidad-b.md")
            self.assertEqual(v.resolve_link("ENTIDAD-B"), "wiki/semantic/entidad-b.md")
            self.assertEqual(v.resolve_link("gen-demo"), "genome/genes/gen-demo.md")
            self.assertIsNone(v.resolve_link("no-existe"))

    def test_relations_of(self):
        with tempfile.TemporaryDirectory() as td:
            v = vlt.load_vault(mini_vault(td))
            a = v.page_by_rel("wiki/semantic/concepto-a.md")
            self.assertEqual(v.relations_of(a), [("usa", "Entidad B")])

    def test_alias_resuelve(self):
        with tempfile.TemporaryDirectory() as td:
            root = mini_vault(td)
            escribir(root, "wiki/semantic/nueva.md", PAGINA.format(
                title="Nueva", type="concepto", tier="semantic",
                relations="{}", body="x.").replace(
                "relations: {}", "id_alias: [semantic/vieja-clave]\nrelations: {}"))
            v = vlt.load_vault(root)
            self.assertEqual(v.resolve_link("vieja-clave"), "wiki/semantic/nueva.md")


class TestResolucionAcotada(unittest.TestCase):
    """M-05: solo las páginas del vault (wiki/ + genome/ + index.md) resuelven.

    Regresión del piloto: [[ai-act-art72-postmercado]] resolvía a
    corpus/texto/ai-act-art72-postmercado.md —un archivo homónimo fuera de la
    wiki que gana por orden de ruta— y la arista declarada salía "sin evidencia".
    """

    def test_homonimo_fuera_de_la_wiki_no_captura_el_slug(self):
        with tempfile.TemporaryDirectory() as td:
            root = mini_vault(td)
            # `corpus/` ordena antes que `wiki/`: sin la cota, ganaría el slug.
            escribir(root, "corpus/texto/entidad-b.md", "Copia literal de la fuente.")
            v = vlt.load_vault(root)
            self.assertEqual(v.resolve_link("entidad-b"), "wiki/semantic/entidad-b.md")

    def test_archivo_ajeno_no_resuelve_ni_por_nombre_ni_por_title(self):
        with tempfile.TemporaryDirectory() as td:
            root = mini_vault(td)
            escribir(root, "docs/nota-suelta.md",
                     "---\ntitle: Nota Ajena\n---\nNo soy página del vault.\n")
            v = vlt.load_vault(root)
            self.assertIsNone(v.resolve_link("nota-suelta"))
            self.assertIsNone(v.resolve_link("Nota Ajena"))

    def test_wiki_genome_e_index_siguen_resolviendo(self):
        with tempfile.TemporaryDirectory() as td:
            v = vlt.load_vault(mini_vault(td))
            self.assertEqual(v.resolve_link("entidad-b"), "wiki/semantic/entidad-b.md")
            self.assertEqual(v.resolve_link("gen-demo"), "genome/genes/gen-demo.md")
            self.assertEqual(v.resolve_link("index"), "index.md")


class TestCorpusReal(unittest.TestCase):
    def test_repo_carga(self):
        v = vlt.load_vault(REPO)
        self.assertGreaterEqual(len(v.genes), 25)
        self.assertEqual(v.resolve_link("gen-lint"), "genome/genes/gen-lint.md")
        self.assertIsNotNone(v.page_by_rel("index.md"))
        # las carpetas de exclusión no contaminan la resolución
        self.assertIsNone(v.resolve_link("test_vault"))


if __name__ == "__main__":
    unittest.main()
