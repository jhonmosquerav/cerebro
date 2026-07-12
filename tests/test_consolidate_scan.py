"""Tests del scanner mecánico de CONSOLIDATE (umbrales de gen-ciclo-de-vida v5)."""
import datetime
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import consolidate_scan as cs

AS_OF = datetime.date(2026, 7, 12)

PLANTILLA = """---
title: {title}
type: {type}
tier: {tier}
tags: [t]
confidence: {confidence}
created: {created}
last_reinforced: {last_reinforced}
decay_rate: {decay_rate}
sources: {sources}
relations: {relations}
{extra}---
{body}
"""


def pagina(root: Path, rel: str, **kw):
    defaults = dict(title=Path(rel).stem, type="concepto", tier=rel.split("/")[1],
                    confidence=0.8, created="2026-07-01",
                    last_reinforced="2026-07-10", decay_rate="medium",
                    sources="[]", relations="{}", extra="", body="Texto.")
    defaults.update(kw)
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(PLANTILLA.format(**defaults), encoding="utf-8")


class TestDecaimiento(unittest.TestCase):
    def test_ventanas_y_delta(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # 2026-05-01 → as-of: 72 días · decay high (14d) → 5 ventanas → -0.25
            pagina(root, "wiki/working/vieja.md", decay_rate="high",
                   last_reinforced="2026-05-01", confidence=0.8)
            r = cs.run(root, as_of=AS_OF)
            d = [x for x in r.decaimientos if "vieja" in x["path"]][0]
            self.assertEqual(d["ventanas"], 5)
            self.assertAlmostEqual(d["confidence_propuesta"], 0.55)

    def test_decay_aplicado_evita_doble_descuento(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/working/tratada.md", decay_rate="high",
                   last_reinforced="2026-05-01", extra="decay_aplicado: 2026-07-01\n")
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual([x for x in r.decaimientos if "tratada" in x["path"]], [])

    def test_evento_no_degrada_confidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/incidente.md", decay_rate="high",
                   last_reinforced="2026-01-01",
                   extra="clase: evento\nfecha_evento: 2026-01-01\n")
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual([x for x in r.decaimientos if "incidente" in x["path"]], [])


class TestPromocion(unittest.TestCase):
    def _elegible(self, root):
        # cumple TODO: estable, conf ≥0.70, 2 fuentes, edad ≥7d, refuerzo posterior
        pagina(root, "wiki/working/lista.md", confidence=0.75,
               created="2026-06-01", last_reinforced="2026-07-10",
               sources="[raw/a.md, raw/b.md]")

    def test_elegible(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._elegible(root)
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual(len(r.promociones), 1)
            self.assertIn("lista", r.promociones[0]["path"])
            self.assertEqual(r.promociones[0]["destino"], "semantic")

    def test_sin_refuerzo_posterior_no_promueve(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/working/cruda.md", confidence=0.75,
                   created="2026-06-01", last_reinforced="2026-06-01",
                   sources="[raw/a.md, raw/b.md]")
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual(r.promociones, [])

    def test_cuarentena_confidencial_y_contradice_bloquean(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/working/cuarentena.md", confidence=0.75,
                   created="2026-06-01", last_reinforced="2026-07-10",
                   sources="[raw/a.md, raw/b.md]", extra="riesgo_inyeccion: true\n")
            pagina(root, "wiki/working/secreta.md", confidence=0.75,
                   created="2026-06-01", last_reinforced="2026-07-10",
                   sources="[raw/a.md, raw/b.md]", extra="sensibilidad: confidencial\n")
            pagina(root, "wiki/working/discutida.md", confidence=0.75,
                   created="2026-06-01", last_reinforced="2026-07-10",
                   sources="[raw/a.md, raw/b.md]",
                   relations='{ contradice: "[[secreta]]" }')
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual(r.promociones, [])

    def test_sop_promueve_a_procedural(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/working/proceso.md", type="sop", confidence=0.75,
                   created="2026-06-01", last_reinforced="2026-07-10",
                   sources="[raw/a.md, raw/b.md]")
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual(r.promociones[0]["destino"], "procedural")


class TestArchivo(unittest.TestCase):
    def test_piso_y_eventos_viejos(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/apagada.md", confidence=0.25)
            pagina(root, "wiki/semantic/evento-viejo.md",
                   extra="clase: evento\nfecha_evento: 2025-12-01\n")
            pagina(root, "wiki/semantic/evento-reciente.md",
                   extra="clase: evento\nfecha_evento: 2026-07-01\n")
            r = cs.run(root, as_of=AS_OF)
            rutas = [x["path"] for x in r.archivos]
            self.assertTrue(any("apagada" in p for p in rutas))
            self.assertTrue(any("evento-viejo" in p for p in rutas))
            self.assertFalse(any("evento-reciente" in p for p in rutas))


class TestDuplicados(unittest.TestCase):
    def test_titulo_igual_normalizado(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/cafe-uno.md", title="Café con Ñandú")
            pagina(root, "wiki/semantic/cafe-dos.md", title="cafe con nandu")
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual(len(r.duplicados), 1)

    def test_exencion_por_relacion_declarada(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/original.md", title="Protocolo X")
            pagina(root, "wiki/semantic/derivada.md", title="Protocolo X",
                   relations='{ deriva_de: "[[original]]" }')
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual(r.duplicados, [],
                             "deriva_de/reemplaza/agregado_en son versionado legítimo")

    def test_cuarentena_excluida_de_fusion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/semantic/a.md", title="Mismo Título")
            pagina(root, "wiki/semantic/b.md", title="Mismo Título",
                   extra="riesgo_inyeccion: true\n")
            r = cs.run(root, as_of=AS_OF)
            self.assertEqual(r.duplicados, [])


class TestDeterminismo(unittest.TestCase):
    def test_salida_estable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "wiki/working/x.md", decay_rate="high",
                   last_reinforced="2026-01-01")
            r1, r2 = cs.run(root, as_of=AS_OF), cs.run(root, as_of=AS_OF)
            self.assertEqual(r1.render_text(), r2.render_text())


if __name__ == "__main__":
    unittest.main()
