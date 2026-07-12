"""Tests del espejo AGENTS.md ≡ CLAUDE.md."""
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import mirror

REPO = Path(__file__).resolve().parent.parent


class TestMirror(unittest.TestCase):
    def test_identicos_ok(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "CLAUDE.md").write_text("manual\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("manual\n", encoding="utf-8")
            self.assertIsNone(mirror.check(root))

    def test_crlf_no_rompe_el_espejo(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "CLAUDE.md").write_bytes(b"manual\r\nlinea\r\n")
            (root / "AGENTS.md").write_bytes(b"manual\nlinea\n")
            self.assertIsNone(mirror.check(root))

    def test_desincronizado_falla_y_fix_repara(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "CLAUDE.md").write_text("manual v2\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("manual v1\n", encoding="utf-8")
            self.assertIsNotNone(mirror.check(root))
            mirror.fix(root)
            self.assertIsNone(mirror.check(root))
            self.assertIn("v2", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_ausente_falla(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "CLAUDE.md").write_text("manual\n", encoding="utf-8")
            self.assertIsNotNone(mirror.check(root))

    def test_repo_real_en_verde(self):
        """C-02: el repo mantiene su invariante de espejo."""
        self.assertIsNone(mirror.check(REPO))


if __name__ == "__main__":
    unittest.main()
