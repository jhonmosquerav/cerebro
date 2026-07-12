"""Tests del score de salud determinista (Fase 3 del roadmap)."""
import datetime
import shutil
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import health

REPO = Path(__file__).resolve().parent.parent
LIMPIO = REPO / "tests" / "fixtures" / "vault-limpio"
SUCIO = REPO / "tests" / "fixtures" / "vault-sucio"
AS_OF = datetime.date(2026, 7, 12)


class TestScore(unittest.TestCase):
    def test_vault_limpio_alto_y_estable(self):
        r1 = health.run(LIMPIO, as_of=AS_OF)
        r2 = health.run(LIMPIO, as_of=AS_OF)
        self.assertEqual(r1.score, r2.score)
        self.assertEqual(r1.render_text(), r2.render_text())
        self.assertGreaterEqual(r1.score, 90, r1.render_text())
        self.assertEqual(r1.componentes["higiene"], 100)
        self.assertEqual(r1.componentes["conectividad"], 100)
        self.assertEqual(r1.componentes["vigencia"], 100)

    def test_vault_sucio_puntua_bajo(self):
        limpio = health.run(LIMPIO, as_of=AS_OF).score
        sucio = health.run(SUCIO, as_of=AS_OF).score
        self.assertLess(sucio, limpio)
        self.assertLess(sucio, 70, "un vault plagado de violaciones no puede aprobar")

    def test_degradar_baja_el_score(self):
        """El test negativo del roadmap: romper el vault DEBE bajar el número."""
        with tempfile.TemporaryDirectory() as td:
            copia = Path(td) / "v"
            shutil.copytree(LIMPIO, copia)
            base = health.run(copia, as_of=AS_OF).score
            (copia / "wiki" / "semantic" / "rota.md").write_text(
                "---\ntitle: Rota\n---\nSin campos requeridos y [[enlace-roto-x]].\n",
                encoding="utf-8")
            degradado = health.run(copia, as_of=AS_OF).score
            self.assertLess(degradado, base)

    def test_cobertura_na_sin_raw(self):
        with tempfile.TemporaryDirectory() as td:
            copia = Path(td) / "v"
            shutil.copytree(LIMPIO, copia)
            shutil.rmtree(copia / "raw")
            r = health.run(copia, as_of=AS_OF)
            self.assertIsNone(r.componentes["cobertura"])
            self.assertGreater(r.score, 0)  # renormaliza sin la componente

    def test_write_genera_tablero(self):
        with tempfile.TemporaryDirectory() as td:
            copia = Path(td) / "v"
            shutil.copytree(LIMPIO, copia)
            r = health.run(copia, as_of=AS_OF)
            path = health.write_dashboard(copia, r)
            texto = path.read_text(encoding="utf-8")
            self.assertIn("type: meta", texto)
            self.assertIn(str(r.score), texto)
            self.assertIn("2026-07-12", texto)


if __name__ == "__main__":
    unittest.main()
