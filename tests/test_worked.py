"""Los casos de worked/ se regeneran byte a byte — el contrato de Fase 1.

Cualquier tercero puede clonar el repo, correr los comandos de corrida.md
y obtener EXACTAMENTE estos archivos. Si este test falla, o cambió la
herramienta (regenera los esperados y documenta por qué) o alguien editó
un resultado a mano (no se hace).
"""
import shutil
import subprocess
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import onboard, statehash

REPO = Path(__file__).resolve().parent.parent
FECHA = "2026-07-12"  # la fecha es parte de la entrada: cambiarla cambia los bytes

INDEX_BASE = """---
title: CEREBRO — índice
type: meta
updated: 2026-06-22
---

# Mapa

## Estado
- Fase: **scaffolding listo** — pendiente correr `ONBOARD`.
- Empresa: _(sin configurar)_

## Genoma
- Genes activos: carpeta `genome/genes/`.
"""


def regenerar(caso: str, root: Path) -> onboard.ApplyResult:
    (root / "genome" / "genes").mkdir(parents=True)
    (root / "wiki").mkdir()
    (root / "raw").mkdir()
    (root / "onboard").mkdir()
    (root / "index.md").write_text(INDEX_BASE, encoding="utf-8", newline="\n")
    shutil.copy(REPO / "worked" / caso / "company.yaml", root / "onboard" / "company.yaml")
    return onboard.apply(root / "onboard" / "company.yaml", root, date=FECHA)


def norm(p: Path) -> bytes:
    return p.read_bytes().replace(b"\r\n", b"\n")


class TestWorked(unittest.TestCase):
    def _caso(self, caso: str):
        esperado_dir = REPO / "worked" / caso / "resultado-esperado"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            regenerar(caso, root)
            # delta byte a byte: genes sembrados, perfil, ledger de eventos
            for rel in sorted(p.relative_to(esperado_dir).as_posix()
                              for p in esperado_dir.rglob("*.md")):
                with self.subTest(archivo=rel):
                    self.assertEqual(norm(root / rel), norm(esperado_dir / rel),
                                     f"{caso}/{rel} difiere del esperado")
            self.assertEqual(norm(root / "genome" / "events.jsonl"),
                             norm(esperado_dir / "genome" / "events.jsonl"))
            # taxonomía completa
            carpetas = sorted(p.relative_to(root).as_posix()[: -len("/.gitkeep")]
                              for p in root.rglob(".gitkeep"))
            esperadas = norm(esperado_dir / "taxonomia.txt").decode("utf-8").strip().split("\n")
            self.assertEqual(carpetas, esperadas)
            # hash de estado del genoma completo
            hash_esperado = norm(esperado_dir / "state-hash.txt").decode("utf-8").split()[1]
            self.assertEqual(statehash.tree_hash(root, "genome"), hash_esperado)
            # el índice quedó configurado (asserción semántica, no byte a byte)
            index = (root / "index.md").read_text(encoding="utf-8")
            self.assertIn("**configurado**", index)

    def test_agencia_demo(self):
        self._caso("agencia-demo")

    def test_legal_demo(self):
        self._caso("legal-demo")

    def test_piscc_demo(self):
        self._caso("piscc-demo")

    def test_idempotencia_de_los_casos(self):
        for caso in ("agencia-demo", "legal-demo", "piscc-demo"):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                regenerar(caso, root)
                res2 = onboard.apply(root / "onboard" / "company.yaml", root, date=FECHA)
                self.assertEqual(res2.actions, [], f"{caso}: re-aplicar debe ser no-op")

    def test_la_cli_da_el_hash_publicado_con_cualquier_aprobador(self):
        """LA promesa, por el camino real: mismo manifiesto + misma fecha ⇒ mismo hash,
        sea quien sea el aprobador. Los esperados nacen de la API (`user`); un tercero
        corre la CLI con su identidad y debe obtener exactamente el hash publicado."""
        for caso in ("agencia-demo", "legal-demo", "piscc-demo"):
            esperado = norm(REPO / "worked" / caso / "resultado-esperado" / "state-hash.txt"
                            ).decode("utf-8").split()[1]
            for aprobador in ("ana@empresa.test", "beto@otra.test"):
                with self.subTest(caso=caso, aprobador=aprobador), \
                        tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    (root / "genome" / "genes").mkdir(parents=True)
                    (root / "wiki").mkdir()
                    (root / "raw").mkdir()
                    (root / "onboard").mkdir()
                    (root / "index.md").write_text(INDEX_BASE, encoding="utf-8", newline="\n")
                    shutil.copy(REPO / "worked" / caso / "company.yaml",
                                root / "onboard" / "company.yaml")
                    r = subprocess.run(
                        [sys.executable, str(REPO / "tools" / "cerebro.py"), "--vault", str(root),
                         "onboard", "apply", "--date", FECHA, "--approved-by", aprobador],
                        capture_output=True, text=True, encoding="utf-8", cwd=REPO)
                    self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                    self.assertEqual(statehash.tree_hash(root, "genome"), esperado)


if __name__ == "__main__":
    unittest.main()
