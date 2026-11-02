"""Tests del hash de estado determinista."""
import hashlib
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


L1 = '{"ts":"2026-07-12","type":"gene_added","target":"gen-a","signal":"señal ∅","approved_by":"%s"}'
L2 = '{"ts":"2026-07-12","type":"gene_added","target":"gen-b","approved_by":"%s","prev":"%s"}'


def ledger(aprobador: str, prev: str = "aaa") -> bytes:
    return ("\n".join([L1 % aprobador, L2 % (aprobador, prev)]) + "\n").encode("utf-8")


class TestProcedenciaDelLedger(unittest.TestCase):
    """El hash dice QUÉ contiene el genoma; QUIÉN lo aprobó lo prueban la cadena y la firma."""

    def _hash(self, rel: str, data: bytes) -> str:
        with tempfile.TemporaryDirectory() as td:
            escribir(Path(td), rel, data)
            return statehash.tree_hash(Path(td), "all")

    def test_ignora_aprobador_y_prev(self):
        self.assertEqual(self._hash("genome/events.jsonl", ledger("ana@empresa.test", "aaa")),
                         self._hash("genome/events.jsonl", ledger("beto@empresa.test", "bbb")))

    def test_sigue_sensible_al_contenido_del_ledger(self):
        base = ledger("ana@empresa.test").decode("utf-8")
        lineas = base.strip().split("\n")
        variantes = {
            "signal": base.replace("señal ∅", "señal X"),
            "target": base.replace("gen-b", "gen-z"),
            "línea borrada": lineas[0] + "\n",
            "orden": lineas[1] + "\n" + lineas[0] + "\n",
        }
        h = self._hash("genome/events.jsonl", base.encode("utf-8"))
        for nombre, texto in variantes.items():
            with self.subTest(nombre):
                self.assertNotEqual(h, self._hash("genome/events.jsonl", texto.encode("utf-8")))

    def test_linea_invalida_sigue_contando(self):
        self.assertNotEqual(self._hash("genome/events.jsonl", b'{"ts":"x"}\n{roto uno\n'),
                            self._hash("genome/events.jsonl", b'{"ts":"x"}\n{roto dos\n'))

    def test_bytes_no_utf8_no_rompen_y_cuentan(self):
        self.assertNotEqual(self._hash("genome/events.jsonl", b'\xff\xfe uno\n'),
                            self._hash("genome/events.jsonl", b'\xff\xfe dos\n'))

    def test_solo_el_ledger_del_genoma_se_normaliza(self):
        for rel in ("genome/otro.jsonl", "wiki/events.jsonl", "genome/sub/events.jsonl"):
            with self.subTest(rel):
                self.assertNotEqual(self._hash(rel, ledger("ana@empresa.test", "aaa")),
                                    self._hash(rel, ledger("beto@empresa.test", "bbb")))

    def test_crlf_equivale_a_lf_en_el_ledger(self):
        lf = ledger("ana@empresa.test")
        self.assertEqual(self._hash("genome/events.jsonl", lf),
                         self._hash("genome/events.jsonl", lf.replace(b"\n", b"\r\n")))

    def test_golden_del_ledger(self):
        """Fija la normalización con un cálculo independiente: quita solo esas dos claves."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            escribir(root, "genome/events.jsonl",
                     b'{"ts":"2026-07-12","approved_by":"ana","status":"applied","prev":"abc"}\n')
            contenido = hashlib.sha256(
                b'{"ts":"2026-07-12","status":"applied"}\n').hexdigest()
            esperado = hashlib.sha256(
                f"genome/events.jsonl {contenido}\n".encode("utf-8")).hexdigest()
            self.assertEqual(statehash.tree_hash(root, "genome"), esperado)

    def test_detalle_y_arbol_usan_la_misma_normalizacion(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            escribir(Path(a), "genome/events.jsonl", ledger("ana@empresa.test", "aaa"))
            escribir(Path(b), "genome/events.jsonl", ledger("beto@empresa.test", "bbb"))
            self.assertEqual(statehash.manifest_lines(Path(a), "genome"),
                             statehash.manifest_lines(Path(b), "genome"))


if __name__ == "__main__":
    unittest.main()
