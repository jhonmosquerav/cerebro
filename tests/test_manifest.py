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

    def test_tipos_extra_validos_pasan(self):
        errs = self._con("tipos_extra: [spec, norma]\n")
        self.assertEqual(errs, [])

    def test_tipos_extra_malformado(self):
        errs = self._con('tipos_extra: ["Spec Legal"]\n')
        self.assertTrue(any("tipos_extra" in e for e in errs))

    def test_tipos_extra_no_duplica_el_nucleo(self):
        errs = self._con("tipos_extra: [concepto]\n")
        self.assertTrue(any("ya está en el núcleo" in e for e in errs))

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


class TestAvisosDeTaxonomia(unittest.TestCase):
    """gen-onboard v6: avisar si la taxonomía no cubre los tipos que el genoma declara.

    Regresión de H-07 del piloto: se aplicó un manifiesto sin destino para `sintesis`
    teniendo `sintesis_umbral: 3`, y nada lo dijo.
    """

    def _m(self, taxonomy: dict, **extra):
        return mf.Manifest(raw={"company": {"name": "x"}, "taxonomy": taxonomy, **extra},
                                 path=Path("m.yaml"))

    def test_sin_carpeta_para_sintesis_avisa(self):
        avisos = mf.avisos(self._m({"semantic": ["clientes"], "procedural": ["sops"]}))
        self.assertTrue(any("síntesis" in a for a in avisos), avisos)

    def test_con_carpeta_para_sintesis_no_avisa_de_eso(self):
        avisos = mf.avisos(self._m({"semantic": ["clientes", "sintesis"],
                                          "procedural": ["sops"]}))
        self.assertFalse(any("síntesis" in a for a in avisos), avisos)

    def test_tier_vacio_avisa_por_cada_tipo(self):
        avisos = mf.avisos(self._m({"semantic": ["conceptos", "sintesis"],
                                          "procedural": []}))
        self.assertTrue(any("'sop'" in a for a in avisos), avisos)

    def test_los_avisos_no_son_errores(self):
        """Un aviso no puede abortar `onboard apply`."""
        m = self._m({"semantic": ["clientes"], "procedural": ["sops"]})
        self.assertTrue(mf.avisos(m))
        self.assertEqual([e for e in mf.validate(m) if "taxonom" in e], [])


if __name__ == "__main__":
    unittest.main()
