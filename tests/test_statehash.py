"""Tests del hash de estado determinista."""
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import statehash


def escribir(root: Path, rel: str, data: bytes):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


class TestTreeHash(unittest.TestCase):
    def test_estable_y_sensible_al_contenido(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            escribir(root, "genome/genes/g.md", b"---\nid: g\n---\nregla\n")
            escribir(root, "genome/events.jsonl", b'{"ts":"2026-07-12"}\n')
            h1 = statehash.tree_hash(root, "genome")
            h2 = statehash.tree_hash(root, "genome")
            self.assertEqual(h1, h2)
            escribir(root, "genome/genes/g.md", b"---\nid: g\n---\nregla mutada\n")
            self.assertNotEqual(h1, statehash.tree_hash(root, "genome"))

    def test_crlf_equivale_a_lf(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            escribir(Path(a), "genome/g.md", b"linea uno\nlinea dos\n")
            escribir(Path(b), "genome/g.md", b"linea uno\r\nlinea dos\r\n")
            self.assertEqual(
                statehash.tree_hash(Path(a), "genome"),
                statehash.tree_hash(Path(b), "genome"),
            )

    def test_independiente_del_orden_de_creacion(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            escribir(Path(a), "genome/1.md", b"uno")
            escribir(Path(a), "genome/2.md", b"dos")
            escribir(Path(b), "genome/2.md", b"dos")
            escribir(Path(b), "genome/1.md", b"uno")
            self.assertEqual(
                statehash.tree_hash(Path(a), "genome"),
                statehash.tree_hash(Path(b), "genome"),
            )

    def test_scopes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            escribir(root, "genome/g.md", b"g")
            escribir(root, "wiki/semantic/p.md", b"p")
            escribir(root, "index.md", b"i")
            escribir(root, "CLAUDE.md", b"c")
            escribir(root, "AGENTS.md", b"c")
            escribir(root, "onboard/company.yaml", b"y")
            hg = statehash.tree_hash(root, "genome")
            hk = statehash.tree_hash(root, "knowledge")
            ha = statehash.tree_hash(root, "all")
            self.assertNotEqual(hg, hk)
            self.assertNotEqual(hk, ha)
            # knowledge no cambia si muta el genoma
            escribir(root, "genome/g.md", b"g2")
            self.assertEqual(hk, statehash.tree_hash(root, "knowledge"))

    def test_golden_fijo(self):
        """Hash de referencia: si esto cambia, cambió el algoritmo (no lo hagas)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            escribir(root, "genome/a.md", b"hola\n")
            self.assertEqual(
                statehash.tree_hash(root, "genome"),
                "3e1f0011d9600d6c9fd9249beb1cd7a93362fedf1b8d20ec1ea155e736fc270a",
            )


if __name__ == "__main__":
    unittest.main()
