"""Tests de `init`: deja onboard/company.yaml listo con el perfil fijado (Fase 4.2).

Contrato: parte del ejemplo o de un blueprint, fija `profile:` reutilizando la edición
textual de gen-perfiles, no pisa un manifiesto existente salvo --force, es idempotente
(re-correr sobre su propio resultado no cambia bytes ni falla) y conserva TAL CUAL los
placeholders `<...>` del blueprint: rellenarlos es del operador, no de la herramienta.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import init_manifest as im
from cerebro_core import manifest as mf
from cerebro_core import onboard, profile, schema

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "tools" / "cerebro.py"
EJEMPLO = REPO / "onboard" / "company.example.yaml"
BLUEPRINTS = REPO / "onboard" / "blueprints"
FECHA = "2026-10-20"

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
    """Clon mínimo: onboard/ con ejemplo y blueprints, sin company.yaml."""
    root = Path(td)
    (root / "genome" / "genes").mkdir(parents=True)
    (root / "wiki").mkdir()
    (root / "raw").mkdir()
    (root / "onboard").mkdir()
    shutil.copy(EJEMPLO, root / "onboard" / "company.example.yaml")
    shutil.copytree(BLUEPRINTS, root / "onboard" / "blueprints")
    (root / "index.md").write_text(INDEX_BASE, encoding="utf-8", newline="\n")
    return root


def correr(*args):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=REPO)


class TestInitDesdeEjemplo(unittest.TestCase):
    def test_fija_perfil_y_conserva_el_resto(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            res = im.run(root, profile="memoria", date=FECHA)
            self.assertTrue(res.written)
            self.assertIsNone(res.blueprint)
            self.assertFalse(res.placeholders)
            destino = root / "onboard" / "company.yaml"
            self.assertTrue(destino.is_file())
            m = mf.load(destino)
            self.assertEqual(mf.validate(m), [])
            self.assertEqual(m.profile, "memoria")
            self.assertTrue(m.declares_profile)
            # el resto del ejemplo viaja intacto: misma empresa, mismos seeds
            self.assertEqual(m.company_name, mf.load(EJEMPLO).company_name)
            self.assertEqual(m.raw.get("seed_genes"), mf.load(EJEMPLO).raw.get("seed_genes"))
            # y el texto solo difiere en la línea profile:
            esperado = profile.edit_manifest_text(
                EJEMPLO.read_text(encoding="utf-8"), profile="memoria")
            self.assertEqual(destino.read_text(encoding="utf-8"), esperado)

    def test_perfil_completo_sobre_el_ejemplo_no_cambia_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            im.run(root, profile="completo", date=FECHA)
            self.assertEqual((root / "onboard" / "company.yaml").read_bytes(),
                             EJEMPLO.read_bytes().replace(b"\r\n", b"\n"))

    def test_todos_los_perfiles_producen_manifiesto_valido(self):
        for perfil in schema.PROFILE_ORDER:
            with self.subTest(perfil=perfil), tempfile.TemporaryDirectory() as td:
                root = esqueleto(td)
                im.run(root, profile=perfil, date=FECHA)
                m = mf.load(root / "onboard" / "company.yaml")
                self.assertEqual(mf.validate(m), [])
                self.assertEqual(m.profile, perfil)
                self.assertEqual(profile.effective(m),
                                 {c: c in schema.PROFILES[perfil] for c in schema.CAPABILITY_ORDER})

    def test_pasos_siguientes_apuntan_a_onboard_apply(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            res = im.run(root, profile="gobernanza", date=FECHA)
            texto = "\n".join(res.next_steps)
            self.assertIn(f"onboard apply --date {FECHA}", texto)
            self.assertNotIn("placeholder", texto.lower())


class TestIdempotenciaYNoPisar(unittest.TestCase):
    def test_idempotente_sobre_su_propio_resultado(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            r1 = im.run(root, profile="memoria", date=FECHA)
            bytes1 = (root / "onboard" / "company.yaml").read_bytes()
            r2 = im.run(root, profile="memoria", date=FECHA)   # sin --force: no falla
            self.assertTrue(r1.written)
            self.assertFalse(r2.written)
            self.assertEqual((root / "onboard" / "company.yaml").read_bytes(), bytes1)

    def test_no_pisa_un_manifiesto_distinto_sin_force(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            destino = root / "onboard" / "company.yaml"
            propio = "company:\n  name: \"Mi empresa\"\n  sector: \"propio\"\n"
            destino.write_text(propio, encoding="utf-8", newline="\n")
            with self.assertRaises(im.InitError) as cm:
                im.run(root, profile="memoria", date=FECHA)
            self.assertIn("--force", str(cm.exception))
            self.assertEqual(destino.read_text(encoding="utf-8"), propio)

    def test_force_sobrescribe(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            destino = root / "onboard" / "company.yaml"
            destino.write_text("company:\n  name: \"Vieja\"\n", encoding="utf-8", newline="\n")
            res = im.run(root, profile="minimo", date=FECHA, force=True)
            self.assertTrue(res.written)
            self.assertEqual(mf.load(destino).profile, "minimo")
            self.assertEqual(mf.load(destino).company_name, mf.load(EJEMPLO).company_name)

    def test_cambiar_de_perfil_exige_force(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            im.run(root, profile="memoria", date=FECHA)
            with self.assertRaises(im.InitError):
                im.run(root, profile="completo", date=FECHA)
            self.assertEqual(mf.load(root / "onboard" / "company.yaml").profile, "memoria")


class TestInitDesdeBlueprint(unittest.TestCase):
    def test_blueprint_conserva_placeholders_tal_cual(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            res = im.run(root, profile="memoria", blueprint="legal", date=FECHA)
            self.assertEqual(res.blueprint, "legal")
            self.assertTrue(res.placeholders)
            destino = root / "onboard" / "company.yaml"
            texto = destino.read_text(encoding="utf-8")
            original = (BLUEPRINTS / "legal.yaml").read_text(encoding="utf-8")
            # cada placeholder del blueprint sigue ahí, sin tocar
            for ph in ("<tu bufete>", "<tudominio>.legal"):
                self.assertIn(ph, texto)
            # el blueprint entero es prefijo del resultado: solo se AÑADE el bloque de perfil
            self.assertTrue(texto.startswith(original.rstrip("\n")),
                            "init alteró el cuerpo del blueprint")
            m = mf.load(destino)
            self.assertEqual(mf.validate(m), [])        # placeholders no son error estructural
            self.assertTrue(mf.has_placeholders(m))
            self.assertEqual(m.profile, "memoria")
            self.assertEqual(m.raw.get("default_sensibilidad"), "confidencial")
            # y los pasos siguientes avisan que hay que rellenarlos antes de aplicar
            self.assertIn("placeholder", "\n".join(res.next_steps).lower())

    def test_todos_los_blueprints_del_repo_inician(self):
        for bp in im.list_blueprints(REPO):
            with self.subTest(blueprint=bp), tempfile.TemporaryDirectory() as td:
                root = esqueleto(td)
                res = im.run(root, profile="gobernanza", blueprint=bp, date=FECHA)
                m = mf.load(root / "onboard" / "company.yaml")
                self.assertEqual(mf.validate(m), [], bp)
                self.assertEqual(m.profile, "gobernanza")
                self.assertEqual(res.placeholders, mf.has_placeholders(m))

    def test_blueprint_desconocido_lista_los_disponibles(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            with self.assertRaises(im.InitError) as cm:
                im.run(root, profile="memoria", blueprint="astrologia", date=FECHA)
            self.assertIn("legal", str(cm.exception))
            self.assertFalse((root / "onboard" / "company.yaml").exists())

    def test_perfil_desconocido_es_error_sin_escritura(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            with self.assertRaises(im.InitError):
                im.run(root, profile="maximo", date=FECHA)
            self.assertFalse((root / "onboard" / "company.yaml").exists())


class TestInitLuegoOnboard(unittest.TestCase):
    def test_el_manifiesto_iniciado_se_aplica_y_deja_el_perfil(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            im.run(root, profile="memoria", date=FECHA)
            onboard.apply(root / "onboard" / "company.yaml", root, date=FECHA)
            aplicado = profile.read_applied(root)
            self.assertIsNotNone(aplicado)
            self.assertEqual(aplicado[0], "memoria")
            self.assertTrue(aplicado[1]["memoria"])
            self.assertFalse(aplicado[1]["grafo"])


class TestInitCli(unittest.TestCase):
    def test_init_cli_feliz_e_idempotente(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            r = correr("--vault", str(root), "init", "--profile", "memoria", "--date", FECHA)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(f"onboard apply --date {FECHA}", r.stdout)
            self.assertIn("memoria", r.stdout)
            r2 = correr("--vault", str(root), "init", "--profile", "memoria", "--date", FECHA)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertIn("sin cambios", r2.stdout)

    def test_init_cli_no_pisa_sale_2(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            correr("--vault", str(root), "init", "--profile", "memoria", "--date", FECHA)
            r = correr("--vault", str(root), "init", "--profile", "completo", "--date", FECHA)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("--force", r.stdout)
            r3 = correr("--vault", str(root), "init", "--profile", "completo",
                        "--date", FECHA, "--force")
            self.assertEqual(r3.returncode, 0, r3.stdout + r3.stderr)
            self.assertEqual(mf.load(root / "onboard" / "company.yaml").profile, "completo")

    def test_init_cli_blueprint_avisa_placeholders(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            r = correr("--vault", str(root), "init", "--profile", "minimo",
                       "--blueprint", "salud", "--date", FECHA)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("placeholder", r.stdout.lower())

    def test_init_cli_perfil_fuera_de_la_escalera_sale_2(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            r = correr("--vault", str(root), "init", "--profile", "turbo")
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
