"""Tests del LINT mecánico — detectores a, c, d, e de gen-lint v4 y más."""
import datetime
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import lint

REPO = Path(__file__).resolve().parent.parent
SUCIO = REPO / "tests" / "fixtures" / "vault-sucio"
LIMPIO = REPO / "tests" / "fixtures" / "vault-limpio"
AS_OF = datetime.date(2026, 7, 12)


class TestVaultSucio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = lint.run(SUCIO, as_of=AS_OF)
        cls.by_code = {}
        for f in cls.report.findings:
            cls.by_code.setdefault(f.code, []).append(f)

    def _uno(self, code, fragmento_ruta):
        self.assertIn(code, self.by_code, f"no se detectó {code}")
        rutas = [f.path for f in self.by_code[code]]
        self.assertTrue(any(fragmento_ruta in r for r in rutas),
                        f"{code} no señala {fragmento_ruta}: {rutas}")

    def test_fm01_sin_frontmatter(self):
        self._uno("FM-01", "sin-frontmatter.md")

    def test_fm02_requeridos_ausentes(self):
        self._uno("FM-02", "campos-faltantes.md")

    def test_fm03_valores_invalidos_y_tier_carpeta(self):
        self._uno("FM-03", "valores-invalidos.md")
        detalles = " | ".join(f.detail for f in self.by_code["FM-03"])
        self.assertIn("confidence", detalles)
        self.assertIn("decay_rate", detalles)
        self.assertIn("tier", detalles)

    def test_fm04_campo_desconocido(self):
        self._uno("FM-04", "campo-desconocido.md")
        self.assertEqual(self.by_code["FM-04"][0].severity, "aviso")

    def test_rel01_verbo_fuera_de_union(self):
        self._uno("REL-01", "verbo-raro.md")

    def test_lnk01_enlace_roto(self):
        self._uno("LNK-01", "enlace-roto.md")
        self._uno("LNK-01", "index.md")  # [[no-existe-tal-pagina]]

    def test_lnk02_huerfana(self):
        self._uno("LNK-02", "huerfana.md")
        rutas = [f.path for f in self.by_code["LNK-02"]]
        self.assertEqual(len(rutas), 1, f"solo huerfana.md debía ser huérfana: {rutas}")

    def test_vig01_vencida_dura(self):
        self._uno("VIG-01", "pagina-vencida.md")

    def test_vig02_derogada(self):
        self._uno("VIG-02", "derogada.md")

    def test_vig03_vencida_blanda(self):
        self._uno("VIG-03", "decaida.md")
        self.assertEqual(self.by_code["VIG-03"][0].severity, "aviso")

    def test_id01_clave_desalineada(self):
        self._uno("ID-01", "clave-desalineada.md")

    def test_qrn01_cuarentena_es_info(self):
        self._uno("QRN-01", "en-cuarentena.md")
        self.assertEqual(self.by_code["QRN-01"][0].severity, "info")

    def test_sen01_confidencial_anclada(self):
        self._uno("SEN-01", "confidencial-anclada.md")

    def test_led01_raw_muto(self):
        self._uno("LED-01", "raw/fuente.md")

    def test_led02_linea_invalida(self):
        self._uno("LED-02", "ingest-ledger.jsonl")

    def test_salida_determinista(self):
        r2 = lint.run(SUCIO, as_of=AS_OF)
        self.assertEqual(self.report.render_text(), r2.render_text())
        self.assertEqual(self.report.render_json(), r2.render_json())

    def test_exit_code(self):
        self.assertEqual(self.report.exit_code(strict=False), 1)


class TestVaultLimpio(unittest.TestCase):
    def test_cero_hallazgos(self):
        report = lint.run(LIMPIO, as_of=AS_OF)
        self.assertEqual([f.render() for f in report.findings], [])
        self.assertEqual(report.exit_code(strict=True), 0)


class TestRepoReal(unittest.TestCase):
    def test_el_repo_no_tiene_errores(self):
        """El template real debe estar limpio de errores (avisos se toleran)."""
        report = lint.run(REPO, as_of=AS_OF)
        errores = [f.render() for f in report.findings if f.severity == "error"]
        self.assertEqual(errores, [])


if __name__ == "__main__":
    unittest.main()
