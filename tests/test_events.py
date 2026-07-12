"""Tests de integridad del ledger genome/events.jsonl (backlog C-03)."""
import json
import subprocess
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import events

REPO = Path(__file__).resolve().parent.parent

# Incluye no-ASCII (∅ → señal cápsula) a propósito: guarda contra la regresión de
# decodificación por locale (Windows/cp1252) en verify_append_only, que lee git show.
LINEA = '{"ts":"2026-07-01","type":"gene_added","target":"gen-x","signal":"señal ∅ inicial","diff":"∅ → cápsula base","approved_by":"user","status":"applied"}'


def escribir_ledger(td: str, lineas: list[str]) -> Path:
    p = Path(td) / "events.jsonl"
    p.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return p


class TestEsquema(unittest.TestCase):
    def test_ledger_valido(self):
        with tempfile.TemporaryDirectory() as td:
            p = escribir_ledger(td, [LINEA])
            self.assertEqual(events.verify_file(p), [])

    def test_json_invalido(self):
        with tempfile.TemporaryDirectory() as td:
            p = escribir_ledger(td, [LINEA, "{esto no es json"])
            codes = [f.code for f in events.verify_file(p)]
            self.assertIn("EVT-01", codes)

    def test_clave_ausente(self):
        with tempfile.TemporaryDirectory() as td:
            linea = json.dumps({"ts": "2026-07-01", "type": "gene_added"})
            p = escribir_ledger(td, [linea])
            codes = [f.code for f in events.verify_file(p)]
            self.assertIn("EVT-02", codes)

    def test_valores_invalidos(self):
        with tempfile.TemporaryDirectory() as td:
            mal = json.loads(LINEA)
            mal["ts"] = "01/07/2026"
            mal["status"] = "quizas"
            p = escribir_ledger(td, [json.dumps(mal)])
            codes = [f.code for f in events.verify_file(p)]
            self.assertIn("EVT-03", codes)

    def test_ts_retrocede_es_aviso(self):
        with tempfile.TemporaryDirectory() as td:
            v2 = json.loads(LINEA)
            v2["ts"] = "2026-06-01"
            p = escribir_ledger(td, [LINEA, json.dumps(v2)])
            fnds = events.verify_file(p)
            self.assertTrue(any(f.code == "EVT-04" and f.severity == "aviso" for f in fnds))

    def test_ledger_real_del_repo(self):
        """Las 63+ líneas históricas del repo validan (sin exigirles hash-chain)."""
        fnds = events.verify_file(REPO / "genome" / "events.jsonl")
        errores = [f for f in fnds if f.severity == "error"]
        self.assertEqual(errores, [], [f.render() for f in errores])


class TestHashChain(unittest.TestCase):
    def test_append_construye_cadena_valida(self):
        with tempfile.TemporaryDirectory() as td:
            p = escribir_ledger(td, [LINEA])
            ev = json.loads(LINEA)
            ev["ts"] = "2026-07-12"
            ev["target"] = "gen-y"
            events.append_line(p, ev)
            ev["target"] = "gen-z"
            events.append_line(p, ev)
            self.assertEqual([f for f in events.verify_file(p) if f.severity == "error"], [])
            lineas = p.read_text(encoding="utf-8").strip().split("\n")
            self.assertIn("prev", json.loads(lineas[1]))
            self.assertIn("prev", json.loads(lineas[2]))

    def test_manipulacion_rompe_la_cadena(self):
        with tempfile.TemporaryDirectory() as td:
            p = escribir_ledger(td, [LINEA])
            ev = json.loads(LINEA)
            ev["ts"] = "2026-07-12"
            events.append_line(p, ev)
            events.append_line(p, ev)
            # adulterar la línea del medio
            lineas = p.read_text(encoding="utf-8").strip().split("\n")
            lineas[1] = lineas[1].replace("2026-07-12", "2026-07-11")
            p.write_text("\n".join(lineas) + "\n", encoding="utf-8")
            codes = [f.code for f in events.verify_file(p)]
            self.assertIn("EVT-05", codes)

    def test_abandonar_la_cadena_es_aviso(self):
        with tempfile.TemporaryDirectory() as td:
            p = escribir_ledger(td, [LINEA])
            ev = json.loads(LINEA)
            ev["ts"] = "2026-07-12"
            events.append_line(p, ev)          # con prev
            with p.open("a", encoding="utf-8") as f:
                f.write(LINEA + "\n")           # a mano, sin prev
            fnds = events.verify_file(p)
            self.assertTrue(any(f.code == "EVT-06" and f.severity == "aviso" for f in fnds))

    def test_append_valida_antes_de_escribir(self):
        with tempfile.TemporaryDirectory() as td:
            p = escribir_ledger(td, [LINEA])
            with self.assertRaises(events.EventError):
                events.append_line(p, {"ts": "hoy", "type": "x"})
            self.assertEqual(len(p.read_text(encoding="utf-8").strip().split("\n")), 1)


def _git(cwd, *args):
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd, capture_output=True, text=True, check=True,
    )


class TestAppendOnlyGit(unittest.TestCase):
    def test_historia_append_only_ok_y_reescritura_detectada(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git(root, "init", "-q")
            (root / "genome").mkdir()
            ledger = root / "genome" / "events.jsonl"
            ledger.write_text(LINEA + "\n", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "v1")
            ledger.write_text(LINEA + "\n" + LINEA + "\n", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "v2 append")
            self.assertEqual(
                [f for f in events.verify_append_only(root, "genome/events.jsonl")
                 if f.severity == "error"], [])
            # reescritura: cambiar la primera línea
            ledger.write_text(LINEA.replace("gen-x", "gen-hackeado") + "\n" + LINEA + "\n",
                              encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "v3 rewrite")
            codes = [f.code for f in events.verify_append_only(root, "genome/events.jsonl")]
            self.assertIn("EVT-07", codes)

    def test_repo_real_append_only(self):
        """C-03 sobre la historia real: 90+ commits sin reescritura del ledger."""
        fnds = events.verify_append_only(REPO, "genome/events.jsonl")
        errores = [f for f in fnds if f.severity == "error"]
        self.assertEqual(errores, [], [f.render() for f in errores])


if __name__ == "__main__":
    unittest.main()
