"""Tests de la CLI — la puerta de entrada que usan CI, pre-commit y el agente."""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "tools" / "cerebro.py"
SUCIO = REPO / "tests" / "fixtures" / "vault-sucio"
LIMPIO = REPO / "tests" / "fixtures" / "vault-limpio"


def correr(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, encoding="utf-8", cwd=REPO,
    )


class TestCli(unittest.TestCase):
    def test_lint_sucio_sale_1(self):
        r = correr("--vault", str(SUCIO), "lint", "--as-of", "2026-07-12")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FM-01", r.stdout)
        self.assertIn("LED-01", r.stdout)

    def test_lint_limpio_sale_0(self):
        r = correr("--vault", str(LIMPIO), "lint", "--as-of", "2026-07-12", "--strict")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_lint_json_es_estable(self):
        r1 = correr("--vault", str(SUCIO), "lint", "--as-of", "2026-07-12", "--json")
        r2 = correr("--vault", str(SUCIO), "lint", "--as-of", "2026-07-12", "--json")
        self.assertEqual(r1.stdout, r2.stdout)

    def test_mirror_repo_en_verde(self):
        r = correr("mirror")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_hash_imprime_sha256(self):
        r = correr("hash", "--scope", "genome")
        self.assertEqual(r.returncode, 0)
        h = r.stdout.strip().split()[-1]
        self.assertEqual(len(h), 64)
        int(h, 16)  # es hexadecimal

    def test_verify_repo_en_verde(self):
        r = correr("verify", "--as-of", "2026-07-12")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("EN VERDE", r.stdout)

    def test_events_verify_repo(self):
        r = correr("events", "verify")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_health_en_fixture(self):
        r = correr("--vault", str(LIMPIO), "health", "--as-of", "2026-07-12")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("score", r.stdout)

    def test_consolidate_scan_en_fixture(self):
        r = correr("--vault", str(SUCIO), "consolidate", "scan", "--as-of", "2026-07-12")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PROPONE", r.stdout)

    def test_xray_en_fixture(self):
        r = correr("--vault", str(LIMPIO), "xray", "--as-of", "2026-07-12", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("drift_score", r.stdout)


if __name__ == "__main__":
    unittest.main()
