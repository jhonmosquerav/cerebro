"""Tests del esquema mecánico — espejo ejecutable del genoma."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import schema


def fm_valido(**extra):
    base = {
        "title": "Página X",
        "type": "concepto",
        "tier": "semantic",
        "tags": ["a"],
        "confidence": 0.7,
        "created": "2026-07-01",
        "last_reinforced": "2026-07-10",
        "decay_rate": "medium",
        "sources": ["raw/x.md"],
        "relations": {},
    }
    base.update(extra)
    return base


class TestValidacion(unittest.TestCase):
    def test_pagina_valida(self):
        self.assertEqual(schema.validate_page_fm(fm_valido(), is_meta=False), [])

    def test_meta_exenta(self):
        self.assertEqual(schema.validate_page_fm({"title": "x", "type": "meta"}, is_meta=True), [])

    def test_requerido_ausente(self):
        fm = fm_valido()
        del fm["confidence"]
        errs = schema.validate_page_fm(fm, is_meta=False)
        self.assertTrue(any("confidence" in e for e in errs))

    def test_valores_invalidos(self):
        errs = schema.validate_page_fm(
            fm_valido(confidence=1.5, tier="cosmico", decay_rate="rapido",
                      created="12/07/2026"),
            is_meta=False,
        )
        joined = " | ".join(errs)
        self.assertIn("confidence", joined)
        self.assertIn("tier", joined)
        self.assertIn("decay_rate", joined)
        self.assertIn("created", joined)

    def test_evento_exige_fecha(self):
        errs = schema.validate_page_fm(fm_valido(clase="evento"), is_meta=False)
        self.assertTrue(any("fecha_evento" in e for e in errs))
        ok = schema.validate_page_fm(
            fm_valido(clase="evento", fecha_evento="2026-07-01"), is_meta=False
        )
        self.assertEqual(ok, [])

    def test_hub_con_reglas_propias(self):
        errs = schema.validate_page_fm(
            fm_valido(type="hub", confidence=0.5), is_meta=False
        )
        self.assertTrue(any("hub" in e for e in errs))
        ok = schema.validate_page_fm(
            fm_valido(type="hub", confidence=1.0, sources=[], relations={}),
            is_meta=False,
        )
        self.assertEqual(ok, [])

    def test_relations_dict_o_vacio(self):
        self.assertEqual(schema.validate_page_fm(fm_valido(relations=[]), is_meta=False), [])
        self.assertEqual(
            schema.validate_page_fm(fm_valido(relations={"usa": "[[otra]]"}), is_meta=False), []
        )
        errs = schema.validate_page_fm(fm_valido(relations="usa otra"), is_meta=False)
        self.assertTrue(any("relations" in e for e in errs))


class TestVerbos(unittest.TestCase):
    def test_union_sin_manifiesto(self):
        verbs = schema.allowed_verbs(None)
        self.assertIn("usa", verbs)
        self.assertIn("reemplaza", verbs)
        self.assertIn("corrobora", verbs)
        self.assertNotIn("producido_en", verbs)

    def test_union_con_relation_types(self):
        verbs = schema.allowed_verbs(["producido_en", "cita"])
        self.assertIn("producido_en", verbs)
        self.assertIn("depende_de", verbs)

    def test_verbos_de_relations(self):
        rels = {"usa": ["[[a]]", "b"], "cita": "[[c]]"}
        pares = schema.relation_pairs(rels)
        self.assertEqual(pares, [("cita", "c"), ("usa", "a"), ("usa", "b")])


class TestCicloDefaults(unittest.TestCase):
    def test_numeros_del_gen(self):
        c = schema.CICLO_DEFAULTS
        self.assertEqual(c["decay_ventana_dias"]["high"], 14)
        self.assertEqual(c["decay_ventana_dias"]["low"], 180)
        self.assertEqual(c["decaimiento_delta"], 0.05)
        self.assertEqual(c["confidence_techo"], 0.95)
        self.assertEqual(c["piso_archivo"], 0.30)
        self.assertEqual(c["archivo_eventos_dias"], 180)
        self.assertEqual(c["promocion"]["confidence_min"], 0.70)
        self.assertEqual(c["promocion"]["edad_min_dias"], 7)


if __name__ == "__main__":
    unittest.main()
