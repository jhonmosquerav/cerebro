"""Tests de perfiles de instalación y capacidades activables (gen-perfiles v1)."""
import datetime
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import lint, manifest as mf, onboard, profile, schema, statehash

REPO = Path(__file__).resolve().parent.parent
EJEMPLO = REPO / "onboard" / "company.example.yaml"
AS_OF = datetime.date(2026, 10, 20)

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

MANIFIESTO_MIN = """company:
  name: "Caso"
  sector: "pruebas"
taxonomy:
  semantic: [sintesis]
  procedural: [sops]
"""


def esqueleto(td: str, manifiesto: str | None = None) -> Path:
    root = Path(td)
    (root / "genome" / "genes").mkdir(parents=True)
    (root / "wiki").mkdir()
    (root / "raw").mkdir()
    (root / "onboard").mkdir()
    (root / "index.md").write_text(INDEX_BASE, encoding="utf-8", newline="\n")
    if manifiesto is None:
        shutil.copy(EJEMPLO, root / "onboard" / "company.yaml")
    else:
        (root / "onboard" / "company.yaml").write_text(manifiesto, encoding="utf-8", newline="\n")
    return root


def m_de(texto: str) -> mf.Manifest:
    from cerebro_core import miniyaml
    return mf.Manifest(raw=miniyaml.parse(texto), path="<mem>")


class TestEsquema(unittest.TestCase):
    def test_escalera_estricta(self):
        previo: set = set()
        for nombre in schema.PROFILE_ORDER:
            actual = set(schema.PROFILES[nombre])
            self.assertTrue(previo <= actual, f"{nombre} no contiene al anterior")
            previo = actual
        self.assertEqual(set(schema.PROFILES["completo"]), set(schema.CAPABILITY_ORDER))
        self.assertEqual(schema.PROFILES["minimo"], ())

    def test_todo_gen_del_repo_tiene_sitio(self):
        """Cada gen base está en el núcleo o en EXACTAMENTE una capacidad."""
        genes = sorted(p.stem for p in (REPO / "genome" / "genes").glob("gen-*.md"))
        self.assertGreater(len(genes), 20)
        for g in genes:
            caps = [c for c, d in schema.CAPABILITIES.items() if g in d["genes"]]
            en_nucleo = g in schema.CORE_GENES
            with self.subTest(gen=g):
                self.assertEqual(len(caps) + int(en_nucleo), 1,
                                 f"{g}: núcleo={en_nucleo}, capacidades={caps}")
        # y todo gen declarado por el esquema existe en disco (sin fantasmas)
        declarados = set(schema.CORE_GENES) | {
            g for d in schema.CAPABILITIES.values() for g in d["genes"]}
        self.assertEqual(declarados - set(genes), set())

    def test_capability_of(self):
        self.assertEqual(schema.capability_of("gen-xray"), "auditoria")
        self.assertIsNone(schema.capability_of("gen-ingest"))


class TestEfectivo(unittest.TestCase):
    def test_sin_declaracion_es_completo(self):
        m = m_de(MANIFIESTO_MIN)
        self.assertFalse(profile.declares(m))
        self.assertTrue(all(profile.effective(m).values()))

    def test_preset_y_overrides(self):
        m = m_de(MANIFIESTO_MIN + "profile: memoria\ncapabilities: { auditoria: true }\n")
        caps = profile.effective(m)
        self.assertEqual([c for c in caps if caps[c]], ["memoria", "ciclo_de_vida", "auditoria"])
        self.assertEqual(profile.overrides_of(m), {"auditoria": True})
        m2 = m_de(MANIFIESTO_MIN + "profile: completo\ncapabilities:\n  grafo: false\n")
        self.assertFalse(profile.effective(m2)["grafo"])

    def test_validacion_del_manifiesto(self):
        errs = mf.validate(m_de(MANIFIESTO_MIN + "profile: turbo\ncapabilities: { nube: true, grafo: 1 }\n"))
        texto = "\n".join(errs)
        self.assertIn("profile inválido", texto)
        self.assertIn("capacidad desconocida 'nube'", texto)
        self.assertIn("capabilities.grafo debe ser booleano", texto)
        self.assertEqual(mf.validate(m_de(MANIFIESTO_MIN + "profile: minimo\ncapabilities: {}\n")), [])

    def test_render_y_parse_son_inversos(self):
        m = m_de(MANIFIESTO_MIN + "profile: gobernanza\ncapabilities: { grafo: true }\n")
        texto = profile.render(m, "2026-10-20")
        self.assertEqual(texto, profile.render(m, "2026-10-20"))  # determinista
        nombre, caps = profile.parse_applied(texto)
        self.assertEqual(nombre, "gobernanza")
        self.assertEqual(caps, profile.effective(m))
        self.assertIn("cap_visualizacion: false", texto)
        self.assertIn("cap_grafo: true", texto)
        self.assertIn("type: meta", texto)


class TestEdicionDelManifiesto(unittest.TestCase):
    def test_set_sobre_manifiesto_sin_bloque(self):
        out = profile.edit_manifest_text(MANIFIESTO_MIN, profile="memoria")
        self.assertTrue(out.startswith(MANIFIESTO_MIN.rstrip("\n")))
        self.assertIn("\nprofile: memoria\n", out)
        self.assertIn("\ncapabilities: {}\n", out)
        self.assertEqual(profile.profile_name(m_de(out)), "memoria")

    def test_enable_disable_minimizan_overrides(self):
        base = MANIFIESTO_MIN + "profile: memoria   # preset\ncapabilities: {}   # overrides\n"
        out = profile.edit_manifest_text(base, enable="grafo")
        self.assertIn("profile: memoria   # preset", out)
        self.assertIn("capabilities:   # overrides\n  grafo: true\n", out)
        out2 = profile.edit_manifest_text(out, disable="grafo")   # vuelve al preset ⇒ sin override
        self.assertIn("capabilities: {}   # overrides\n", out2)
        out3 = profile.edit_manifest_text(out, profile="completo")  # grafo ya está en completo
        self.assertIn("profile: completo   # preset", out3)
        self.assertIn("capabilities: {}", out3)
        self.assertNotIn("grafo: true", out3)

    def test_edicion_conserva_el_resto(self):
        texto = EJEMPLO.read_text(encoding="utf-8")
        out = profile.edit_manifest_text(texto, disable="auditoria")
        m = m_de(out)
        self.assertEqual(m.company_name, "Acme Bots")
        self.assertEqual(m.seed_genes[0]["id"], "gen-propuestas")
        self.assertFalse(profile.effective(m)["auditoria"])
        # solo cambian las líneas de profile/capabilities
        antes = [l for l in texto.splitlines() if not l.startswith(("profile:", "capabilities:", "  "))]
        despues = [l for l in out.splitlines() if not l.startswith(("profile:", "capabilities:", "  "))]
        self.assertEqual(antes, despues)

    def test_rechaza_desconocidos(self):
        with self.assertRaises(profile.ProfileError):
            profile.edit_manifest_text(MANIFIESTO_MIN, profile="turbo")
        with self.assertRaises(profile.ProfileError):
            profile.edit_manifest_text(MANIFIESTO_MIN, enable="nube")


class TestOnboardAplicaPerfil(unittest.TestCase):
    def test_sin_declaracion_no_escribe_archivo(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td, MANIFIESTO_MIN)
            onboard.apply(root / "onboard" / "company.yaml", root, date="2026-10-20")
            self.assertFalse((root / profile.PERFIL_REL).is_file())
            self.assertTrue(profile.is_on(root, "grafo"))

    def test_declarado_escribe_perfil_evento_e_indice(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td, MANIFIESTO_MIN + "profile: memoria\n")
            res = onboard.apply(root / "onboard" / "company.yaml", root, date="2026-10-20")
            self.assertIn("perfil: genome/perfil.md renderizado (memoria)", res.actions)
            self.assertIn("evento: profile_applied perfil", res.actions)
            self.assertTrue(profile.is_on(root, "memoria"))
            self.assertFalse(profile.is_on(root, "grafo"))
            index = (root / "index.md").read_text(encoding="utf-8")
            self.assertIn("- Perfil: **memoria** — apagadas: evolucion, auditoria, visualizacion, grafo", index)
            ledger = root / "genome" / "events.jsonl"
            ev = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual([e["type"] for e in ev], ["profile_applied"])
            self.assertEqual(ev[0]["diff"], "∅ → memoria")
            # idempotente: re-aplicar no produce acciones ni eventos
            res2 = onboard.apply(root / "onboard" / "company.yaml", root, date="2026-10-20")
            self.assertEqual(res2.actions, [])
            self.assertEqual(len(ledger.read_text(encoding="utf-8").splitlines()), 1)

    def test_cambio_de_perfil_deja_evento_y_lint_detecta_deriva(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td, MANIFIESTO_MIN + "profile: memoria\n")
            man = root / "onboard" / "company.yaml"
            onboard.apply(man, root, date="2026-10-20")
            # editar el manifiesto sin aplicar ⇒ PRF-01
            man.write_text(profile.edit_manifest_text(man.read_text(encoding="utf-8"),
                                                      profile="completo"),
                           encoding="utf-8", newline="\n")
            rep = lint.run(root, as_of=AS_OF)
            self.assertTrue(any(f.code == "PRF-01" and f.severity == "error" for f in rep.findings),
                            rep.render_text())
            # aplicar ⇒ evento nuevo y lint limpio de PRF
            res = onboard.apply(man, root, date="2026-10-21")
            self.assertIn("evento: profile_applied perfil", res.actions)
            ev = [json.loads(l) for l in (root / "genome" / "events.jsonl")
                  .read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(ev[-1]["diff"], "memoria → completo")
            rep2 = lint.run(root, as_of=AS_OF)
            self.assertEqual([f.code for f in rep2.findings if f.code.startswith("PRF")], [])

    def test_perfil_sin_declaracion_es_aviso_y_corrupto_es_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td, MANIFIESTO_MIN)
            (root / "genome" / "perfil.md").write_text(
                profile.render(m_de(MANIFIESTO_MIN + "profile: minimo\n"), "2026-10-20"),
                encoding="utf-8", newline="\n")
            rep = lint.run(root, as_of=AS_OF)
            self.assertEqual([f.code for f in rep.findings if f.code.startswith("PRF")], ["PRF-02"])
            (root / "genome" / "perfil.md").write_text("---\ntitle: x\n---\n", encoding="utf-8")
            rep = lint.run(root, as_of=AS_OF)
            self.assertEqual([f.code for f in rep.findings if f.code.startswith("PRF")], ["PRF-01"])
            self.assertTrue(profile.is_on(root, "grafo"))  # corrupto ⇒ todo activo (fail-open)

    def test_mismo_manifiesto_mismo_hash_con_perfil(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            ra = esqueleto(ta, MANIFIESTO_MIN + "profile: gobernanza\n")
            rb = esqueleto(tb, MANIFIESTO_MIN + "profile: gobernanza\n")
            onboard.apply(ra / "onboard" / "company.yaml", ra, date="2026-10-20")
            onboard.apply(rb / "onboard" / "company.yaml", rb, date="2026-10-20")
            self.assertEqual(statehash.tree_hash(ra, "all"), statehash.tree_hash(rb, "all"))


if __name__ == "__main__":
    unittest.main()


class TestCliPerfil(unittest.TestCase):
    """Punta a punta por la CLI: declarar → aplicar → gating → deriva."""

    def _correr(self, vault, *args):
        import subprocess
        return subprocess.run(
            [sys.executable, str(REPO / "tools" / "cerebro.py"), "--vault", str(vault), *args],
            capture_output=True, text=True, encoding="utf-8", cwd=REPO)

    def test_flujo_completo(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td, MANIFIESTO_MIN)
            (root / "wiki" / "semantic").mkdir(parents=True)
            r = self._correr(root, "profile", "set", "memoria")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("perfil declarado: memoria", r.stdout)
            r = self._correr(root, "profile", "enable", "auditoria")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = self._correr(root, "profile")
            self.assertIn("PENDIENTE de `onboard apply`", r.stdout)
            r = self._correr(root, "onboard", "apply", "--date", "2026-10-20")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("profile_applied", r.stdout)
            r = self._correr(root, "profile")
            self.assertIn("coincide con el manifiesto", r.stdout)
            self.assertIn("overrides: auditoria=true", r.stdout)
            # grafo apagada ⇒ exit 2; forzada ⇒ corre
            r = self._correr(root, "graph", "--scope", "wiki")
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("APAGADA", r.stdout)
            r = self._correr(root, "graph", "--scope", "wiki", "--ignore-profile")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # auditoria encendida por override ⇒ health corre
            r = self._correr(root, "health", "--as-of", "2026-10-20")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # consolidate (ciclo_de_vida en memoria) corre
            r = self._correr(root, "consolidate", "scan", "--as-of", "2026-10-20")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # deriva: editar sin aplicar ⇒ lint sale 1 con PRF-01 y `profile` lo dice
            r = self._correr(root, "profile", "disable", "memoria")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = self._correr(root, "lint", "--as-of", "2026-10-20")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("PRF-01", r.stdout)
            r = self._correr(root, "profile")
            self.assertIn("DERIVA", r.stdout)
            r = self._correr(root, "profile", "set", "turbo")
            self.assertEqual(r.returncode, 2)
