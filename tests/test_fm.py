"""Tests de extracción de frontmatter."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import fm

REPO = Path(__file__).resolve().parent.parent


class TestSplit(unittest.TestCase):
    def test_pagina_normal(self):
        meta, body, errs = fm.split("---\ntitle: Hola\ntags: [a]\n---\n\n# Cuerpo\n")
        self.assertEqual(errs, [])
        self.assertEqual(meta["title"], "Hola")
        self.assertEqual(body, "\n# Cuerpo\n")

    def test_sin_frontmatter(self):
        meta, body, errs = fm.split("# Solo cuerpo\n")
        self.assertIsNone(meta)
        self.assertEqual(body, "# Solo cuerpo\n")
        self.assertEqual(errs, [])

    def test_frontmatter_sin_cierre(self):
        meta, body, errs = fm.split("---\ntitle: X\n")
        self.assertIsNone(meta)
        self.assertTrue(errs)

    def test_frontmatter_ilegible(self):
        meta, body, errs = fm.split("---\na: &x 1\n---\ncuerpo\n")
        self.assertIsNone(meta)
        self.assertTrue(any("línea" in e or "line" in e or ":" in e for e in errs))

    def test_bom_y_crlf(self):
        meta, body, errs = fm.split("﻿---\r\ntitle: X\r\n---\r\ncuerpo\r\n")
        self.assertEqual(errs, [])
        self.assertEqual(meta["title"], "X")

    def test_corpus_real_genes(self):
        """Todos los genes y cápsulas del repo tienen frontmatter legible."""
        for p in sorted((REPO / "genome").rglob("*.md")):
            with self.subTest(gen=p.name):
                meta, _, errs = fm.split(p.read_text(encoding="utf-8"))
                self.assertEqual(errs, [], f"{p.name}: {errs}")
                if p.parent.name in ("genes", "capsules"):
                    self.assertIsNotNone(meta, p.name)
                    self.assertIn("id", meta)
                    self.assertIn("version", meta)

    def test_corpus_real_wiki(self):
        """Las páginas existentes de wiki/ tienen frontmatter legible."""
        for p in sorted((REPO / "wiki").rglob("*.md")):
            with self.subTest(pagina=str(p.relative_to(REPO))):
                meta, _, errs = fm.split(p.read_text(encoding="utf-8"))
                self.assertEqual(errs, [])
                self.assertIsNotNone(meta)


class TestWikilinks(unittest.TestCase):
    def test_extraccion(self):
        links = fm.wikilinks("Ver [[gen-lint]] y [[Página X|alias]] pero no `[[en-codigo]]`.")
        self.assertIn("gen-lint", links)
        self.assertIn("Página X", links)
        self.assertNotIn("en-codigo", links)

    def test_sin_duplicados_y_ordenado_por_aparicion(self):
        links = fm.wikilinks("[[b]] [[a]] [[b]]")
        self.assertEqual(links, ["b", "a"])


if __name__ == "__main__":
    unittest.main()
