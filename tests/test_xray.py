"""Tests de XRAY — deriva del grafo declarado vs el grafo inferido (Fase 2)."""
import datetime
import json
import unittest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import xray

AS_OF = datetime.date(2026, 7, 12)

PLANTILLA = """---
title: {title}
type: concepto
tier: semantic
tags: [t]
confidence: 0.8
created: 2026-07-01
last_reinforced: 2026-07-10
decay_rate: medium
sources: {sources}
relations: {relations}
---
{body}
"""


def pagina(root: Path, nombre: str, title=None, sources="[]", relations="{}", body="Texto."):
    p = root / "wiki" / "semantic" / f"{nombre}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(PLANTILLA.format(title=title or nombre.replace("-", " ").title(),
                                  sources=sources, relations=relations, body=body),
                 encoding="utf-8")


def vault_deriva(td: str) -> Path:
    root = Path(td)
    # a→b declarada Y evidenciada (wikilink en el cuerpo)
    pagina(root, "concepto-a", relations='{ usa: "[[concepto-b]]" }',
           body="A usa a [[concepto-b]] explícitamente.")
    pagina(root, "concepto-b")
    # c→d declarada SIN evidencia alguna
    pagina(root, "concepto-c", relations='{ depende_de: "[[concepto-d]]" }')
    pagina(root, "concepto-d")
    # e y f co-mencionadas en dos fuentes de raw/ sin arista declarada
    pagina(root, "concepto-e", title="Motor Eléctrico")
    pagina(root, "concepto-f", title="Batería Litio")
    (root / "raw").mkdir()
    (root / "raw" / "doc1.md").write_text(
        "El motor eléctrico depende de la batería litio para operar.", encoding="utf-8")
    (root / "raw" / "doc2.md").write_text(
        "Especificación: batería litio integrada al motor eléctrico.", encoding="utf-8")
    # g contradice h (declarada; las contradicciones SIEMPRE se elevan)
    pagina(root, "concepto-g", relations='{ contradice: "[[concepto-h]]" }')
    pagina(root, "concepto-h")
    return root


class TestBuckets(unittest.TestCase):
    def test_los_tres_buckets(self):
        with tempfile.TemporaryDirectory() as td:
            r = xray.run(vault_deriva(td), as_of=AS_OF)
            evidenciadas = [e for e in r.declaradas if e["evidencia"]]
            sin_evidencia = [e for e in r.declaradas if not e["evidencia"]]
            self.assertTrue(any(e["de"].endswith("concepto-a.md") for e in evidenciadas))
            self.assertTrue(any(e["de"].endswith("concepto-c.md") for e in sin_evidencia))
            pares = [(p["a"], p["b"]) for p in r.sin_declarar]
            self.assertTrue(any("concepto-e" in a + b and "concepto-f" in a + b
                                for a, b in pares),
                            f"co-mención e↔f no detectada: {pares}")
            self.assertTrue(any("concepto-g" in c["de"] for c in r.contradicciones))

    def test_drift_score(self):
        with tempfile.TemporaryDirectory() as td:
            r = xray.run(vault_deriva(td), as_of=AS_OF)
            # 3 declaradas (a→b, c→d, g→h); solo a→b con evidencia
            self.assertEqual(len(r.declaradas), 3)
            self.assertAlmostEqual(r.drift_score, 1 / 3, places=3)

    def test_grafo_inferido_externo_aporta_evidencia(self):
        with tempfile.TemporaryDirectory() as td:
            root = vault_deriva(td)
            inferred = root / "graph.json"
            inferred.write_text(json.dumps({
                "nodes": [{"id": "concepto-c"}, {"id": "concepto-d"}],
                "edges": [{"source": "concepto-c", "target": "concepto-d"}],
            }), encoding="utf-8")
            r = xray.run(root, as_of=AS_OF, inferred_path=inferred)
            c_d = [e for e in r.declaradas if e["de"].endswith("concepto-c.md")][0]
            self.assertIn("lente externa", " ".join(c_d["evidencia"]))
            self.assertAlmostEqual(r.drift_score, 2 / 3, places=3)

    def test_sin_aristas_declaradas_drift_none(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pagina(root, "solitaria")
            r = xray.run(root, as_of=AS_OF)
            self.assertIsNone(r.drift_score)


class TestResolucionAcotadaAlVault(unittest.TestCase):
    """M-05 (regresión del piloto): un archivo homónimo fuera de wiki/ robaba la
    resolución del wikilink y la arista declarada salía "sin evidencia"."""

    def _vault(self, td: str) -> Path:
        root = Path(td)
        pagina(root, "ai-act-art12-registros",
               relations='{ usa: "[[ai-act-art72-postmercado]]" }',
               body="Los registros alimentan a [[ai-act-art72-postmercado]].")
        pagina(root, "ai-act-art72-postmercado")
        # homónimo fuera de la wiki, en carpeta que ordena ANTES que wiki/
        ajeno = root / "corpus" / "texto" / "ai-act-art72-postmercado.md"
        ajeno.parent.mkdir(parents=True)
        ajeno.write_text("Texto literal del artículo 72.", encoding="utf-8")
        return root

    def test_la_evidencia_apunta_a_la_pagina_wiki(self):
        with tempfile.TemporaryDirectory() as td:
            r = xray.run(self._vault(td), as_of=AS_OF)
            arista = [e for e in r.declaradas
                      if e["de"].endswith("ai-act-art12-registros.md")][0]
            self.assertEqual(arista["a"], "wiki/semantic/ai-act-art72-postmercado.md")
            self.assertIn("wikilink en el cuerpo", arista["evidencia"])

    def test_el_archivo_ajeno_no_entra_al_reporte(self):
        with tempfile.TemporaryDirectory() as td:
            r = xray.run(self._vault(td), as_of=AS_OF)
            self.assertNotIn("corpus/", r.render_json())

    def test_el_archivo_ajeno_no_entra_al_grafo(self):
        from cerebro_core import graph
        from cerebro_core.vault import load_vault
        with tempfile.TemporaryDirectory() as td:
            v = load_vault(self._vault(td))
            g = graph.build(v, "wiki")
            self.assertEqual(g.edges, 1)
            self.assertIn("wiki/semantic/ai-act-art72-postmercado.md",
                          g.out["wiki/semantic/ai-act-art12-registros.md"])
            self.assertNotIn("corpus/texto/ai-act-art72-postmercado.md", g.nodes)


class TestReporte(unittest.TestCase):
    def test_determinista_y_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = vault_deriva(td)
            r1, r2 = xray.run(root, as_of=AS_OF), xray.run(root, as_of=AS_OF)
            self.assertEqual(r1.render_md(), r2.render_md())
            self.assertEqual(r1.render_json(), r2.render_json())
            destino = xray.write_report(root, r1)
            self.assertTrue((destino / "reporte.md").is_file())
            data = json.loads((destino / "reporte.json").read_text(encoding="utf-8"))
            self.assertAlmostEqual(data["drift_score"], 1 / 3, places=3)
            # el reporte jamás copia cuerpos de páginas (solo rutas y verbos)
            self.assertNotIn("explícitamente", (destino / "reporte.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
