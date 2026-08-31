"""Tests del ONBOARD mecánico — la garantía de reproducibilidad del sistema."""
import json
import unittest
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import events, onboard, statehash

REPO = Path(__file__).resolve().parent.parent
EJEMPLO = REPO / "onboard" / "company.example.yaml"

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


def esqueleto(td: str) -> Path:
    root = Path(td)
    (root / "genome" / "genes").mkdir(parents=True)
    (root / "wiki").mkdir()
    (root / "raw").mkdir()
    (root / "onboard").mkdir()
    (root / "index.md").write_text(INDEX_BASE, encoding="utf-8", newline="\n")
    shutil.copy(EJEMPLO, root / "onboard" / "company.yaml")
    return root


class TestReproducibilidad(unittest.TestCase):
    def test_mismo_manifiesto_mismo_hash(self):
        """LA prueba: dos vaults limpios + mismo manifiesto + misma fecha ⇒ mismo estado."""
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            ra, rb = esqueleto(ta), esqueleto(tb)
            res_a = onboard.apply(ra / "onboard" / "company.yaml", ra, date="2026-07-12")
            res_b = onboard.apply(rb / "onboard" / "company.yaml", rb, date="2026-07-12")
            self.assertEqual(res_a.state_hash, res_b.state_hash)
            self.assertEqual(
                statehash.tree_hash(ra, "all"), statehash.tree_hash(rb, "all"))
            self.assertGreater(len(res_a.actions), 0)

    def test_idempotencia(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            m = root / "onboard" / "company.yaml"
            onboard.apply(m, root, date="2026-07-12")
            h1 = statehash.tree_hash(root, "all")
            eventos_1 = (root / "genome" / "events.jsonl").read_text(encoding="utf-8")
            res2 = onboard.apply(m, root, date="2026-07-12")
            self.assertEqual(res2.actions, [], "re-aplicar no debe producir acciones")
            self.assertEqual(statehash.tree_hash(root, "all"), h1)
            eventos_2 = (root / "genome" / "events.jsonl").read_text(encoding="utf-8")
            self.assertEqual(eventos_1, eventos_2)

    def test_efectos_concretos(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            onboard.apply(root / "onboard" / "company.yaml", root, date="2026-07-12")
            perfil = (root / "genome" / "company-profile.md").read_text(encoding="utf-8")
            self.assertIn("status: configurado", perfil)
            self.assertIn("Acme Bots", perfil)
            gen = root / "genome" / "genes" / "gen-propuestas.md"
            self.assertTrue(gen.is_file())
            self.assertIn("version: 1", gen.read_text(encoding="utf-8"))
            self.assertTrue((root / "wiki" / "semantic" / "clientes" / ".gitkeep").is_file())
            self.assertTrue((root / "wiki" / "procedural" / "sops-ventas" / ".gitkeep").is_file())
            index = (root / "index.md").read_text(encoding="utf-8")
            self.assertIn("**configurado**", index)
            self.assertIn("Acme Bots", index)
            self.assertIn("## Genoma", index)  # el resto del índice queda intacto
            ledger = root / "genome" / "events.jsonl"
            lineas = [json.loads(l) for l in
                      ledger.read_text(encoding="utf-8").strip().split("\n")]
            self.assertEqual(len(lineas), 1)  # 1 seed gene en el ejemplo
            self.assertEqual(lineas[0]["type"], "gene_added")
            self.assertEqual(lineas[0]["target"], "gen-propuestas")
            self.assertEqual(lineas[0]["ts"], "2026-07-12")
            self.assertEqual(
                [f.render() for f in events.verify_file(ledger) if f.severity == "error"], [])

    def test_dry_run_no_escribe(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            h0 = statehash.tree_hash(root, "all")
            res = onboard.apply(root / "onboard" / "company.yaml", root,
                                date="2026-07-12", dry_run=True)
            self.assertGreater(len(res.actions), 0)
            self.assertEqual(statehash.tree_hash(root, "all"), h0)


class TestRechazos(unittest.TestCase):
    def test_placeholders_rechazados_sin_escritura_parcial(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            shutil.copy(REPO / "onboard" / "blueprints" / "legal.yaml",
                        root / "onboard" / "company.yaml")
            h0 = statehash.tree_hash(root, "all")
            with self.assertRaises(onboard.OnboardError) as ctx:
                onboard.apply(root / "onboard" / "company.yaml", root, date="2026-07-12")
            self.assertIn("placeholder", str(ctx.exception).lower())
            self.assertEqual(statehash.tree_hash(root, "all"), h0, "no debe escribir nada")

    def test_graph_lens_sin_backend_es_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            m = root / "onboard" / "company.yaml"
            m.write_text(
                "company:\n  name: X\n  sector: s\n  language: es\n"
                "graph_lens:\n  enable: true\n  backend:\n",
                encoding="utf-8",
            )
            with self.assertRaises(onboard.OnboardError) as ctx:
                onboard.apply(m, root, date="2026-07-12")
            self.assertIn("backend", str(ctx.exception))

    def test_gen_existente_distinto_es_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            (root / "genome" / "genes" / "gen-propuestas.md").write_text(
                "---\nid: gen-propuestas\ntrigger: otro\nstatus: active\nversion: 3\n---\nOtra regla.\n",
                encoding="utf-8",
            )
            h0 = statehash.tree_hash(root, "all")
            with self.assertRaises(onboard.OnboardError) as ctx:
                onboard.apply(root / "onboard" / "company.yaml", root, date="2026-07-12")
            self.assertIn("gen-propuestas", str(ctx.exception))
            self.assertEqual(statehash.tree_hash(root, "all"), h0)

    def test_fecha_invalida(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            with self.assertRaises(onboard.OnboardError):
                onboard.apply(root / "onboard" / "company.yaml", root, date="12/07/2026")


class TestSeedsEvolucionados(unittest.TestCase):
    """gen-onboard v7: el replay no aborta por la fecha del pie ni por genes evolucionados."""

    def test_seed_identico_con_otra_fecha_es_noop(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            m = root / "onboard" / "company.yaml"
            onboard.apply(m, root, date="2026-07-12")
            gen = root / "genome" / "genes" / "gen-propuestas.md"
            antes = gen.read_text(encoding="utf-8")
            res = onboard.apply(m, root, date="2026-07-13")
            self.assertEqual(gen.read_text(encoding="utf-8"), antes,
                             "el gen no debe reescribirse por cambiar la fecha")
            self.assertNotIn("gen sembrado: genome/genes/gen-propuestas.md (v1)",
                             res.actions)

    def test_gen_evolucionado_con_registro_no_aborta(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            m = root / "onboard" / "company.yaml"
            onboard.apply(m, root, date="2026-07-12")
            gen = root / "genome" / "genes" / "gen-propuestas.md"
            evolucionado = ("---\nid: gen-propuestas\ntrigger: \"otro\"\n"
                            "status: active\nversion: 2\n---\n\nRegla evolucionada.\n")
            gen.write_text(evolucionado, encoding="utf-8", newline="\n")
            events.append_line(root / "genome" / "events.jsonl", {
                "ts": "2026-07-13", "type": "gene_edited", "target": "gen-propuestas",
                "signal": "evolución de prueba", "diff": "v1 → v2",
                "approved_by": "user", "status": "applied"})
            res = onboard.apply(m, root, date="2026-07-13")
            self.assertEqual(gen.read_text(encoding="utf-8"), evolucionado,
                             "ONBOARD no debe tocar un gen evolucionado")
            self.assertNotIn("gen sembrado: genome/genes/gen-propuestas.md (v1)",
                             res.actions)

    def test_gen_distinto_sin_registro_sigue_siendo_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            m = root / "onboard" / "company.yaml"
            onboard.apply(m, root, date="2026-07-12")
            gen = root / "genome" / "genes" / "gen-propuestas.md"
            gen.write_text("---\nid: gen-propuestas\ntrigger: \"otro\"\n"
                           "status: active\nversion: 3\n---\n\nSin compuerta.\n",
                           encoding="utf-8", newline="\n")
            # el ledger solo tiene el gene_added de la siembra: sin mutación registrada
            with self.assertRaises(onboard.OnboardError) as ctx:
                onboard.apply(m, root, date="2026-07-14")
            self.assertIn("gen-propuestas", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
