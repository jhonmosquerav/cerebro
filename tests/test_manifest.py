"""Tests de carga y validación del manifiesto onboard/company.yaml."""
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import manifest as mf

REPO = Path(__file__).resolve().parent.parent


class TestCarga(unittest.TestCase):
    def test_manifiesto_de_ejemplo(self):
        m = mf.load(REPO / "onboard" / "company.example.yaml")
        self.assertEqual(m.company_name, "Acme Bots")
        self.assertEqual(m.default_sensibilidad, "interno")
        self.assertEqual(m.hub_umbral, 7)
        self.assertEqual(m.sintesis_umbral, 3)
        self.assertEqual(m.relation_types, ["recibio_propuesta", "proviene_de", "define_precio"])
        self.assertEqual(m.seed_genes[0]["id"], "gen-propuestas")
        self.assertEqual(m.taxonomy["semantic"][0], "clientes")
        self.assertEqual(m.ciclo["decay_ventana_dias"]["high"], 14)
        self.assertEqual(mf.validate(m), [])

    def test_defaults_cuando_faltan_bloques(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "c.yaml"
            p.write_text(
                "company:\n  name: Mini Empresa\n  sector: pruebas\n  language: es\n",
                encoding="utf-8",
            )
            m = mf.load(p)
            self.assertEqual(m.default_sensibilidad, "interno")
            self.assertEqual(m.hub_umbral, 7)
            self.assertEqual(m.ciclo["promocion"]["fuentes_min"], 2)
            self.assertEqual(m.seed_genes, [])
            self.assertEqual(mf.validate(m), [])

    def test_merge_parcial_de_ciclo(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "c.yaml"
            p.write_text(
                "company:\n  name: X\n  sector: s\n  language: es\n"
                "ciclo_de_vida:\n  decaimiento_delta: 0.10\n"
                "  promocion:\n    confidence_min: 0.80\n",
                encoding="utf-8",
            )
            m = mf.load(p)
            self.assertEqual(m.ciclo["decaimiento_delta"], 0.10)
            self.assertEqual(m.ciclo["promocion"]["confidence_min"], 0.80)
            # lo no declarado conserva el default del gen
            self.assertEqual(m.ciclo["promocion"]["fuentes_min"], 2)
            self.assertEqual(m.ciclo["decay_ventana_dias"]["medium"], 60)


class TestValidacion(unittest.TestCase):
    def _con(self, extra_yaml):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "c.yaml"
            p.write_text(
                "company:\n  name: X\n  sector: s\n  language: es\n" + extra_yaml,
                encoding="utf-8",
            )
            m = mf.load(p)
            return mf.validate(m)

    def test_seed_gene_incompleto(self):
        errs = self._con("seed_genes:\n  - id: gen-cosa\n    trigger: algo\n")
        self.assertTrue(any("rule" in e for e in errs))

    def test_seed_gene_id_invalido(self):
        errs = self._con(
            "seed_genes:\n  - id: Cosa Rara\n    trigger: t\n    rule: r\n"
        )
        self.assertTrue(any("id" in e for e in errs))

    def test_source_trust_fuera_de_rango(self):
        errs = self._con("source_trust:\n  oficial: 1.5\n")
        self.assertTrue(any("source_trust" in e for e in errs))

    def test_sensibilidad_invalida(self):
        errs = self._con("default_sensibilidad: secreto\n")
        self.assertTrue(any("default_sensibilidad" in e for e in errs))

    def test_sin_nombre_de_empresa(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "c.yaml"
            p.write_text("company:\n  sector: s\n", encoding="utf-8")
            errs = mf.validate(mf.load(p))
            self.assertTrue(any("name" in e for e in errs))


class TestCorpusBlueprints(unittest.TestCase):
    def test_blueprints_validan_estructuralmente(self):
        for bp in ["agencia", "ecommerce", "legal", "produccion", "salud"]:
            with self.subTest(blueprint=bp):
                m = mf.load(REPO / "onboard" / "blueprints" / f"{bp}.yaml")
                self.assertEqual(mf.validate(m), [])
                self.assertTrue(mf.has_placeholders(m), f"{bp} debería tener placeholders <...>")

    def test_ejemplo_sin_placeholders(self):
        m = mf.load(REPO / "onboard" / "company.example.yaml")
        self.assertFalse(mf.has_placeholders(m))


if __name__ == "__main__":
    unittest.main()
