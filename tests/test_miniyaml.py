"""Tests del parser miniyaml — subconjunto YAML estricto de CEREBRO."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import miniyaml
from cerebro_core.miniyaml import MiniYamlError

REPO = Path(__file__).resolve().parent.parent


class TestEscalares(unittest.TestCase):
    def test_tipos_basicos(self):
        d = miniyaml.parse(
            "entero: 7\n"
            "flotante: 0.95\n"
            "verdadero: true\n"
            "falso: false\n"
            "nulo: null\n"
            "vacio:\n"
            "texto: hola mundo\n"
            "fecha: 2026-07-12\n"
        )
        self.assertEqual(d["entero"], 7)
        self.assertEqual(d["flotante"], 0.95)
        self.assertIs(d["verdadero"], True)
        self.assertIs(d["falso"], False)
        self.assertIsNone(d["nulo"])
        self.assertIsNone(d["vacio"])
        self.assertEqual(d["texto"], "hola mundo")
        # Las fechas se conservan como texto; el esquema las valida después.
        self.assertEqual(d["fecha"], "2026-07-12")

    def test_comillas_y_comentarios(self):
        d = miniyaml.parse(
            'a: "con # adentro"   # comentario fuera\n'
            "b: 'simple'\n"
            "# linea completa de comentario\n"
            "c: sin comillas  # otro\n"
        )
        self.assertEqual(d["a"], "con # adentro")
        self.assertEqual(d["b"], "simple")
        self.assertEqual(d["c"], "sin comillas")


class TestColecciones(unittest.TestCase):
    def test_flow_list_y_map(self):
        d = miniyaml.parse(
            "tags: [hub, area-x]\n"
            "vacia: []\n"
            "mapa: { high: 14, medium: 60, low: 180 }\n"
            "mapa_vacio: {}\n"
            'dominios: ["acmebots.com"]\n'
        )
        self.assertEqual(d["tags"], ["hub", "area-x"])
        self.assertEqual(d["vacia"], [])
        self.assertEqual(d["mapa"], {"high": 14, "medium": 60, "low": 180})
        self.assertEqual(d["mapa_vacio"], {})
        self.assertEqual(d["dominios"], ["acmebots.com"])

    def test_block_list_de_escalares(self):
        d = miniyaml.parse("sources:\n  - raw/uno.md\n  - raw/dos.md\n")
        self.assertEqual(d["sources"], ["raw/uno.md", "raw/dos.md"])

    def test_block_list_de_maps(self):
        d = miniyaml.parse(
            "seed_genes:\n"
            "  - id: gen-propuestas\n"
            '    trigger: "la fuente es una propuesta"\n'
            "    target_tier: semantic\n"
            "  - id: gen-otro\n"
            "    trigger: otro disparo\n"
        )
        self.assertEqual(len(d["seed_genes"]), 2)
        self.assertEqual(d["seed_genes"][0]["id"], "gen-propuestas")
        self.assertEqual(d["seed_genes"][0]["trigger"], "la fuente es una propuesta")
        self.assertEqual(d["seed_genes"][1]["trigger"], "otro disparo")

    def test_maps_anidados(self):
        d = miniyaml.parse(
            "ciclo_de_vida:\n"
            "  decaimiento_delta: 0.05\n"
            "  promocion:\n"
            "    confidence_min: 0.70\n"
            "    fuentes_min: 2\n"
        )
        self.assertEqual(d["ciclo_de_vida"]["promocion"]["confidence_min"], 0.70)
        self.assertEqual(d["ciclo_de_vida"]["promocion"]["fuentes_min"], 2)

    def test_clave_con_valor_vacio_y_hermana(self):
        d = miniyaml.parse(
            "graph_lens:\n"
            "  enable: false\n"
            "  backend:\n"
            "  exclude_sensibilidad: [confidencial]\n"
        )
        self.assertIs(d["graph_lens"]["enable"], False)
        self.assertIsNone(d["graph_lens"]["backend"])
        self.assertEqual(d["graph_lens"]["exclude_sensibilidad"], ["confidencial"])


class TestBloques(unittest.TestCase):
    """Bloques `|`/`>` de indentación uniforme — los usan los blueprints."""

    def test_plegado(self):
        d = miniyaml.parse("a: >\n  hola\n  mundo\nb: 1\n")
        self.assertEqual(d["a"], "hola mundo\n")
        self.assertEqual(d["b"], 1)

    def test_literal(self):
        d = miniyaml.parse("a: |\n  uno\n  dos\n")
        self.assertEqual(d["a"], "uno\ndos\n")

    def test_plegado_con_comillas_y_numeral_adentro(self):
        d = miniyaml.parse('a: >\n  dice "hola #mundo" y sigue\n  a la línea dos\n')
        self.assertEqual(d["a"], 'dice "hola #mundo" y sigue a la línea dos\n')

    def test_chomping_strip(self):
        d = miniyaml.parse("a: >-\n  texto\n")
        self.assertEqual(d["a"], "texto")

    def test_en_item_de_lista(self):
        d = miniyaml.parse(
            "genes:\n"
            "  - id: gen-x\n"
            "    rule: >\n"
            "      Primera parte\n"
            "      segunda parte.\n"
            "    target_tier: semantic\n"
        )
        self.assertEqual(d["genes"][0]["rule"], "Primera parte segunda parte.\n")
        self.assertEqual(d["genes"][0]["target_tier"], "semantic")


class TestRechazos(unittest.TestCase):
    def test_rechaza_tabs(self):
        with self.assertRaises(MiniYamlError):
            miniyaml.parse("a:\n\tb: 1\n")

    def test_rechaza_anclas_y_tags(self):
        with self.assertRaises(MiniYamlError):
            miniyaml.parse("a: &ancla 1\n")
        with self.assertRaises(MiniYamlError):
            miniyaml.parse("a: !!str hola\n")

    def test_rechaza_indicador_de_bloque_con_texto_en_linea(self):
        with self.assertRaises(MiniYamlError):
            miniyaml.parse("a: | texto en la misma linea\n")

    def test_rechaza_clave_duplicada(self):
        with self.assertRaises(MiniYamlError):
            miniyaml.parse("a: 1\na: 2\n")

    def test_rechaza_multidocumento(self):
        with self.assertRaises(MiniYamlError):
            miniyaml.parse("a: 1\n---\nb: 2\n")

    def test_error_lleva_numero_de_linea(self):
        try:
            miniyaml.parse("a: 1\nb: &x 2\n")
            self.fail("debió fallar")
        except MiniYamlError as e:
            self.assertEqual(e.line, 2)


class TestCorpusReal(unittest.TestCase):
    """El manifiesto de ejemplo y los 5 blueprints del repo parsean completos."""

    def test_manifiesto_de_ejemplo(self):
        text = (REPO / "onboard" / "company.example.yaml").read_text(encoding="utf-8")
        d = miniyaml.parse(text)
        self.assertEqual(d["company"]["name"], "Acme Bots")
        self.assertEqual(d["company"]["language"], "es")
        self.assertEqual(d["document_types"], ["propuesta", "contrato", "transcripcion-call", "ticket"])
        self.assertEqual(d["entities"]["productos"], ["bot-whatsapp"])
        self.assertEqual(d["identity"]["productos"], "nombre")
        self.assertEqual(d["glossary"]["MRR"], "ingreso recurrente mensual")
        self.assertEqual(d["roles"]["mutation_approver"], "fundador")
        self.assertEqual(d["source_trust"]["oficial"], 0.9)
        self.assertEqual(d["sintesis_umbral"], 3)
        self.assertEqual(d["hub_umbral"], 7)
        self.assertEqual(d["ciclo_de_vida"]["decay_ventana_dias"]["high"], 14)
        self.assertEqual(d["ciclo_de_vida"]["refuerzo_delta"]["oficial"], 0.10)
        self.assertEqual(d["ciclo_de_vida"]["promocion"]["edad_min_dias"], 7)
        self.assertEqual(d["default_sensibilidad"], "interno")
        self.assertEqual(d["seed_genes"][0]["id"], "gen-propuestas")
        self.assertEqual(d["taxonomy"]["semantic"][0], "clientes")
        self.assertIs(d["graph_lens"]["enable"], False)
        self.assertIsNone(d["graph_lens"]["backend"])

    def test_los_cinco_blueprints(self):
        for bp in ["agencia", "ecommerce", "legal", "produccion", "salud"]:
            with self.subTest(blueprint=bp):
                text = (REPO / "onboard" / "blueprints" / f"{bp}.yaml").read_text(encoding="utf-8")
                d = miniyaml.parse(text)
                self.assertIn("company", d)
                self.assertIn("seed_genes", d)
                self.assertTrue(all("id" in g for g in d["seed_genes"]))


if __name__ == "__main__":
    unittest.main()
