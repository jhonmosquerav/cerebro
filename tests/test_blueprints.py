"""Tests del catálogo de blueprints (Fase 4.3).

Contrato: cada blueprint lleva su identidad (`blueprint: {id, version, min_cerebro}`),
`onboard/blueprints/catalog.yaml` la indexa con historial, y `verify` prueba que
coinciden (CAT-01…CAT-06). `init --blueprint` y `onboard apply` rechazan, sin escribir
nada, un blueprint que exija un CEREBRO más nuevo que el instalado. El bloque es
procedencia, no configuración: `worked/` sigue byte a byte (lo prueba test_worked.py).
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import cerebro_core
from cerebro_core import blueprints as bp
from cerebro_core import init_manifest as im
from cerebro_core import manifest as mf
from cerebro_core import miniyaml, onboard

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "tools" / "cerebro.py"
BLUEPRINTS = REPO / "onboard" / "blueprints"
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


def correr(*args):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=REPO)


def esqueleto(td: str) -> Path:
    """Clon mínimo con onboard/ (ejemplo + blueprints + catálogo), sin company.yaml."""
    root = Path(td)
    (root / "genome" / "genes").mkdir(parents=True)
    (root / "wiki").mkdir()
    (root / "raw").mkdir()
    (root / "onboard").mkdir()
    shutil.copy(EJEMPLO, root / "onboard" / "company.example.yaml")
    shutil.copytree(BLUEPRINTS, root / "onboard" / "blueprints")
    (root / "index.md").write_text(INDEX_BASE, encoding="utf-8", newline="\n")
    return root


def codigos(findings) -> list[str]:
    return sorted({f.code for f in findings})


def reemplazar(path: Path, viejo: str, nuevo: str) -> None:
    texto = path.read_text(encoding="utf-8")
    assert viejo in texto, f"{viejo!r} no está en {path}"
    path.write_text(texto.replace(viejo, nuevo, 1), encoding="utf-8", newline="")


class TestSemver(unittest.TestCase):
    def test_parsea_y_compara(self):
        self.assertEqual(bp.parse_semver("0.1.0"), (0, 1, 0))
        self.assertLess(bp.parse_semver("0.9.9"), bp.parse_semver("1.0.0"))
        self.assertLess(bp.parse_semver("1.2.3"), bp.parse_semver("1.10.0"))

    def test_rechaza_lo_que_no_es_semver(self):
        for malo in ("1.0", "v1.0.0", "1.0.0-beta", "", "a.b.c", 1):
            with self.subTest(valor=malo):
                with self.assertRaises(ValueError):
                    bp.parse_semver(malo)


class TestCatalogoDelRepo(unittest.TestCase):
    def test_catalogo_en_verde(self):
        self.assertEqual(bp.check(REPO), [], [f.render() for f in bp.check(REPO)])

    def test_seis_blueprints_catalogados(self):
        cat = bp.load_catalog(REPO)
        ids = [e["id"] for e in cat["blueprints"]]
        self.assertEqual(ids, sorted(p.stem for p in BLUEPRINTS.glob("*.yaml")
                              if p.name != "catalog.yaml"))
        self.assertEqual(cat["cerebro_version"], cerebro_core.__version__)

    def test_cada_blueprint_lleva_su_bloque(self):
        for p in sorted(BLUEPRINTS.glob("*.yaml")):
            if p.name == "catalog.yaml":
                continue
            with self.subTest(blueprint=p.name):
                raw = miniyaml.parse(p.read_text(encoding="utf-8"))
                self.assertEqual(raw["blueprint"]["id"], p.stem)
                bp.parse_semver(raw["blueprint"]["version"])
                bp.parse_semver(raw["blueprint"]["min_cerebro"])

    def test_los_worked_no_divergen_de_su_blueprint(self):
        for caso in ("agencia-demo", "legal-demo", "piscc-demo"):
            with self.subTest(caso=caso):
                raw = miniyaml.parse((REPO / "worked" / caso / "company.yaml")
                                     .read_text(encoding="utf-8"))
                bloque = raw["blueprint"]
                origen = miniyaml.parse((BLUEPRINTS / f"{bloque['id']}.yaml")
                                        .read_text(encoding="utf-8"))["blueprint"]
                self.assertEqual(bloque, origen)


class TestDetectores(unittest.TestCase):
    """Cada detector se dispara sobre una copia temporal del catálogo real."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = esqueleto(self._td.name)
        self.cat = self.root / "onboard" / "blueprints" / "catalog.yaml"

    def tearDown(self):
        self._td.cleanup()

    def test_cat01_catalogo_ilegible(self):
        self.cat.write_text("blueprints: [\n", encoding="utf-8")
        self.assertEqual(codigos(bp.check(self.root)), ["CAT-01"])

    def test_cat01_entrada_sin_campos(self):
        reemplazar(self.cat, '    min_cerebro: "0.1.0"\n', "", )
        self.assertIn("CAT-01", codigos(bp.check(self.root)))

    def test_cat02_archivo_sin_entrada(self):
        shutil.copy(self.root / "onboard" / "blueprints" / "legal.yaml",
                    self.root / "onboard" / "blueprints" / "notarias.yaml")
        fs = [f for f in bp.check(self.root) if f.code == "CAT-02"]
        self.assertTrue(fs and any("notarias.yaml" in f.detail for f in fs), fs)

    def test_cat02_entrada_sin_archivo(self):
        (self.root / "onboard" / "blueprints" / "salud.yaml").unlink()
        fs = [f for f in bp.check(self.root) if f.code == "CAT-02"]
        self.assertTrue(fs and any("salud" in f.detail for f in fs), fs)

    def test_cat03_bloque_del_archivo_discrepa(self):
        reemplazar(self.root / "onboard" / "blueprints" / "legal.yaml",
                   'version: "1.0.0"', 'version: "1.1.0"')
        self.assertIn("CAT-03", codigos(bp.check(self.root)))

    def test_cat03_blueprint_sin_bloque(self):
        p = self.root / "onboard" / "blueprints" / "legal.yaml"
        raw = miniyaml.parse(p.read_text(encoding="utf-8"))
        texto = p.read_text(encoding="utf-8")
        ini = texto.index("blueprint:")
        fin = texto.index("\n\n", ini)
        p.write_text(texto[:ini] + texto[fin + 2:], encoding="utf-8", newline="")
        self.assertNotIn("blueprint", miniyaml.parse(p.read_text(encoding="utf-8")))
        self.assertIn("CAT-03", codigos(bp.check(self.root)))
        del raw

    def test_cat04_genes_discrepan(self):
        reemplazar(self.cat, "gen-triada-clinica", "gen-triada-clinica, gen-otro")
        self.assertIn("CAT-04", codigos(bp.check(self.root)))

    def test_cat05_historial_no_termina_en_la_version_actual(self):
        texto = self.cat.read_text(encoding="utf-8")
        # la primera entrada del catálogo: su versión actual pasa a 1.1.0 (archivo también)
        cat = miniyaml.parse(texto)
        primera = cat["blueprints"][0]
        reemplazar(self.cat, f'    version: "{primera["version"]}"', '    version: "1.1.0"')
        reemplazar(self.root / "onboard" / "blueprints" / primera["file"],
                   f'version: "{primera["version"]}"', 'version: "1.1.0"')
        self.assertIn("CAT-05", codigos(bp.check(self.root)))

    def test_cat06_min_cerebro_futuro(self):
        texto = self.cat.read_text(encoding="utf-8").replace('min_cerebro: "0.1.0"',
                                                              'min_cerebro: "9.0.0"')
        self.cat.write_text(texto, encoding="utf-8", newline="")
        for p in (self.root / "onboard" / "blueprints").glob("*.yaml"):
            if p.name != "catalog.yaml":
                reemplazar(p, 'min_cerebro: "0.1.0"', 'min_cerebro: "9.0.0"')
        self.assertIn("CAT-06", codigos(bp.check(self.root)))

    def test_cat06_cerebro_version_del_catalogo_discrepa(self):
        reemplazar(self.cat, f'cerebro_version: "{cerebro_core.__version__}"',
                   'cerebro_version: "0.0.1"')
        self.assertIn("CAT-06", codigos(bp.check(self.root)))

    def test_init_rechaza_catalog_como_blueprint(self):
        with self.assertRaises(im.InitError):
            im.run(self.root, profile="memoria", blueprint="catalog", date="2026-10-23")
        self.assertNotIn("catalog", im.list_blueprints(self.root))

    def test_sin_catalogo_no_hay_hallazgos(self):
        """Un vault sin onboard/blueprints/ (clon operativo que los borró) no falla."""
        shutil.rmtree(self.root / "onboard" / "blueprints")
        self.assertEqual(bp.check(self.root), [])
        self.assertFalse(bp.has_catalog(self.root))


class TestManifiesto(unittest.TestCase):
    def _manifest(self, bloque: str) -> mf.Manifest:
        texto = EJEMPLO.read_text(encoding="utf-8") + "\n" + bloque
        return mf.Manifest(raw=miniyaml.parse(texto), path="x")

    def test_sin_bloque_es_legitimo(self):
        m = mf.load(EJEMPLO)
        self.assertEqual(m.blueprint, {})
        self.assertEqual(mf.validate(m), [])

    def test_bloque_valido(self):
        m = self._manifest('blueprint:\n  id: legal\n  version: "1.0.0"\n  min_cerebro: "0.1.0"\n')
        self.assertEqual(mf.validate(m), [])
        self.assertEqual(m.blueprint["id"], "legal")

    def test_rechaza_min_cerebro_futuro(self):
        m = self._manifest('blueprint:\n  id: legal\n  version: "1.0.0"\n  min_cerebro: "9.0.0"\n')
        errs = mf.validate(m)
        self.assertTrue(any("9.0.0" in e and cerebro_core.__version__ in e for e in errs), errs)

    def test_rechaza_bloque_malformado(self):
        m = self._manifest('blueprint:\n  id: Legal Demo\n  version: "1.0"\n  min_cerebro: 1\n')
        errs = mf.validate(m)
        self.assertGreaterEqual(len(errs), 3, errs)


class TestInitYApplyRechazan(unittest.TestCase):
    def test_init_aborta_sin_escribir_si_el_blueprint_exige_mas_cerebro(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            reemplazar(root / "onboard" / "blueprints" / "legal.yaml",
                       'min_cerebro: "0.1.0"', 'min_cerebro: "9.0.0"')
            with self.assertRaises(im.InitError) as cm:
                im.run(root, profile="memoria", blueprint="legal", date="2026-10-23")
            self.assertIn("9.0.0", str(cm.exception))
            self.assertFalse((root / "onboard" / "company.yaml").exists())

    def test_init_copia_el_bloque_tal_cual(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            im.run(root, profile="memoria", blueprint="salud", date="2026-10-23")
            raw = miniyaml.parse((root / "onboard" / "company.yaml").read_text(encoding="utf-8"))
            origen = miniyaml.parse((BLUEPRINTS / "salud.yaml").read_text(encoding="utf-8"))
            self.assertEqual(raw["blueprint"], origen["blueprint"])
            estado = bp.estado_manifiesto(root)
            self.assertEqual(estado["estado"], "al-dia")

    def test_onboard_apply_aborta_sin_escribir(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            destino = root / "onboard" / "company.yaml"
            shutil.copy(REPO / "worked" / "agencia-demo" / "company.yaml", destino)
            reemplazar(destino, 'min_cerebro: "0.1.0"', 'min_cerebro: "9.0.0"')
            with self.assertRaises(onboard.OnboardError):
                onboard.apply(destino, root, date="2026-10-23")
            self.assertFalse((root / "genome" / "company-profile.md").exists())
            self.assertFalse((root / "genome" / "events.jsonl").exists())


class TestEstadoDelManifiesto(unittest.TestCase):
    def test_sin_manifiesto(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            self.assertEqual(bp.estado_manifiesto(root)["estado"], "sin-manifiesto")

    def test_artesanal(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            shutil.copy(EJEMPLO, root / "onboard" / "company.yaml")
            self.assertEqual(bp.estado_manifiesto(root)["estado"], "sin-bloque")

    def test_desactualizado_y_desconocido(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            destino = root / "onboard" / "company.yaml"
            shutil.copy(REPO / "worked" / "legal-demo" / "company.yaml", destino)
            reemplazar(destino, 'version: "1.0.0"', 'version: "0.9.0"')
            e = bp.estado_manifiesto(root)
            self.assertEqual(e["estado"], "desactualizado")
            self.assertEqual((e["version_local"], e["version_catalogo"]), ("0.9.0", "1.0.0"))
            reemplazar(destino, "id: legal", "id: notarias")
            self.assertEqual(bp.estado_manifiesto(root)["estado"], "desconocido")


class TestCli(unittest.TestCase):
    def test_blueprints_sale_0_y_lista_los_seis(self):
        r = correr("blueprints")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for sector in ("agencia", "ecommerce", "legal", "produccion", "salud",
                       "seguridad-territorial"):
            self.assertIn(sector, r.stdout)
        self.assertIn("sin onboard/company.yaml", r.stdout)  # el template no tiene manifiesto

    def test_blueprints_json_estable(self):
        r1 = correr("blueprints", "--json")
        r2 = correr("blueprints", "--json")
        self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
        self.assertEqual(r1.stdout, r2.stdout)
        data = json.loads(r1.stdout)
        self.assertEqual(len(data["blueprints"]), 6)
        self.assertEqual(data["hallazgos"], [])

    def test_blueprints_sale_1_con_deriva(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            reemplazar(root / "onboard" / "blueprints" / "catalog.yaml",
                       "gen-triada-clinica", "gen-triada-clinica, gen-otro")
            r = correr("--vault", str(root), "blueprints")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("CAT-04", r.stdout)

    def test_verify_incluye_el_catalogo(self):
        r = correr("verify", "--as-of", "2026-10-23")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("catálogo de blueprints (6)", r.stdout)


if __name__ == "__main__":
    unittest.main()
