"""Tests del LINT mecánico — detectores a, c, d, e de gen-lint v4 y más."""
import datetime
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core import lint
from cerebro_core import manifest
from cerebro_core import schema

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


class TestCamposExtensibles(unittest.TestCase):
    """gen-frontmatter-obligatorio v7: los campos se extienden como los verbos.

    Regresión de H-08 del piloto: `gen-comparacion-declarada`, sembrado por ONBOARD y
    aprobado por compuerta, exigía el campo `dimension` y LINT lo rechazaba diciendo
    «ningún gen lo declara».
    """

    PAGINA = """---
title: comparacion
type: concepto
tier: semantic
tags: [t]
confidence: 0.8
created: 2026-07-01
last_reinforced: 2026-07-10
decay_rate: medium
sources: []
relations: {}
dimension: determinismo
---
Cuerpo con [[otra]].
"""

    def _correr(self, td: str, campos_extra: list[str] | None):
        root = Path(td)
        (root / "wiki" / "semantic").mkdir(parents=True)
        (root / "wiki" / "semantic" / "comparacion.md").write_text(
            self.PAGINA, encoding="utf-8", newline="\n")
        m = None
        if campos_extra is not None:
            m = manifest.Manifest(raw={"campos_extra": campos_extra}, path=root / "m.yaml")
        return lint.run(root, as_of=AS_OF, manifest=m)

    def test_sin_declarar_sigue_avisando(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            fm04 = [f for f in self._correr(td, None).findings if f.code == "FM-04"]
            self.assertEqual(len(fm04), 1)
            self.assertIn("dimension", fm04[0].detail)

    def test_declarado_en_el_manifiesto_no_avisa(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            fm04 = [f for f in self._correr(td, ["dimension"]).findings if f.code == "FM-04"]
            self.assertEqual(fm04, [], "un campo declarado no puede ser 'fuera de esquema'")

    def test_declarar_un_campo_del_nucleo_es_error_de_manifiesto(self):
        m = manifest.Manifest(raw={"company": {"name": "x"}, "campos_extra": ["title"]},
                              path=Path("m.yaml"))
        errs = manifest.validate(m)
        self.assertTrue(any("ya está en el núcleo" in e for e in errs), errs)

    def test_union_simetrica_a_los_verbos(self):
        self.assertTrue(schema.KNOWN_FIELDS <= schema.allowed_fields(None))
        self.assertIn("dimension", schema.allowed_fields(["dimension"]))


class TestDescartesLnk03(unittest.TestCase):
    """LNK-03: descartes persistentes en `lint-descartes.jsonl` (raíz del vault).

    Una sugerencia evaluada y rechazada bajo criterio no debe reaparecer en cada
    corrida. El archivo es opcional, append-only, una línea JSON por descarte
    con claves {ts, pagina, termino, motivo}; línea malformada → aviso, no crash.
    """

    PAGINA = """---
title: {title}
type: concepto
tier: semantic
tags: [t]
confidence: 0.8
created: 2026-07-01
last_reinforced: 2026-07-10
decay_rate: medium
sources: []
relations: {{}}
---
{body}
"""

    DESCARTE = ('{"ts": "2026-07-12", "pagina": "wiki/semantic/origen.md", '
                '"termino": "fuente-clave", "motivo": "falso positivo evaluado"}\n')

    def _correr(self, td: str, descartes: str | None):
        root = Path(td)
        (root / "wiki" / "semantic").mkdir(parents=True)
        (root / "wiki" / "semantic" / "origen.md").write_text(
            self.PAGINA.format(title="origen", body="Hablo de fuente-clave y de [[destino-b]]."),
            encoding="utf-8", newline="\n")
        (root / "wiki" / "semantic" / "fuente-clave.md").write_text(
            self.PAGINA.format(title="fuente-clave", body="Cuerpo con [[origen]]."),
            encoding="utf-8", newline="\n")
        (root / "wiki" / "semantic" / "destino-b.md").write_text(
            self.PAGINA.format(title="destino-b", body="Cuerpo con [[origen]]."),
            encoding="utf-8", newline="\n")
        if descartes is not None:
            (root / "lint-descartes.jsonl").write_text(
                descartes, encoding="utf-8", newline="\n")
        return lint.run(root, as_of=AS_OF)

    def test_sin_archivo_la_sugerencia_aparece(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            rep = self._correr(td, None)
            lnk03 = [f for f in rep.findings if f.code == "LNK-03"]
            self.assertEqual(len(lnk03), 1)
            self.assertEqual(rep.omitidas_por_descarte, 0)
            self.assertNotIn("omitida", rep.render_text())

    def test_descarte_omite_y_el_reporte_lo_cuenta_en_una_linea(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            rep = self._correr(td, self.DESCARTE)
            self.assertEqual([f for f in rep.findings if f.code == "LNK-03"], [])
            self.assertEqual(rep.omitidas_por_descarte, 1)
            texto = rep.render_text()
            lineas = [l for l in texto.split("\n") if "omitida" in l]
            self.assertEqual(len(lineas), 1, texto)
            self.assertIn("1 sugerencia(s) LNK-03 omitida(s)", lineas[0])
            self.assertIn('"omitidas_por_descarte": 1', rep.render_json())

    def test_descarte_de_otro_par_no_omite(self):
        import tempfile
        otro = self.DESCARTE.replace("wiki/semantic/origen.md", "wiki/semantic/otra.md")
        with tempfile.TemporaryDirectory() as td:
            rep = self._correr(td, otro)
            self.assertEqual(len([f for f in rep.findings if f.code == "LNK-03"]), 1)
            self.assertEqual(rep.omitidas_por_descarte, 0)

    def test_linea_malformada_avisa_sin_crash_y_las_validas_aplican(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            rep = self._correr(td, "esto no es json\n" + self.DESCARTE)
            dsc = [f for f in rep.findings if f.code == "DSC-01"]
            self.assertEqual(len(dsc), 1)
            self.assertEqual(dsc[0].severity, "aviso")
            self.assertIn("lint-descartes.jsonl:1", dsc[0].path)
            # la línea válida sigue aplicando
            self.assertEqual([f for f in rep.findings if f.code == "LNK-03"], [])
            self.assertEqual(rep.omitidas_por_descarte, 1)

    def test_claves_ausentes_avisa_y_no_descarta(self):
        import tempfile
        sin_motivo = ('{"ts": "2026-07-12", "pagina": "wiki/semantic/origen.md", '
                      '"termino": "fuente-clave"}\n')
        with tempfile.TemporaryDirectory() as td:
            rep = self._correr(td, sin_motivo)
            dsc = [f for f in rep.findings if f.code == "DSC-01"]
            self.assertEqual(len(dsc), 1)
            self.assertIn("motivo", dsc[0].detail)
            self.assertEqual(len([f for f in rep.findings if f.code == "LNK-03"]), 1)


class TestVocabularioDelLedger(unittest.TestCase):
    """gen-identidad-de-pagina v3: `resultado` es vocabulario cerrado.

    Regresión del hallazgo H-09 del piloto: `resultado: "ok"` pasaba el lint y la
    cobertura de health lo contaba como 0 — métrica falsa, en silencio.
    """

    LINEA = ('{{"ts":"2026-07-01","op":"INGEST","fuente":"raw/fuente.md",'
             '"hash":"{h}","resultado":"{r}"}}\n')

    def _vault(self, td: str, resultado: str):
        root = Path(td)
        (root / "raw").mkdir(parents=True)
        (root / "wiki").mkdir()
        datos = b"contenido\n"
        (root / "raw" / "fuente.md").write_bytes(datos)
        h = lint.git_blob_sha1(datos)
        (root / "ingest-ledger.jsonl").write_text(
            self.LINEA.format(h=h, r=resultado), encoding="utf-8", newline="\n")
        return lint.run(root, as_of=AS_OF)

    def test_valores_validos_no_producen_hallazgo(self):
        import tempfile
        for r in sorted(schema.LEDGER_RESULTADOS):
            with tempfile.TemporaryDirectory() as td, self.subTest(resultado=r):
                led = [f for f in self._vault(td, r).findings if f.code.startswith("LED")]
                self.assertEqual(led, [], f"{r} debería ser válido: {[f.render() for f in led]}")

    def test_valor_libre_es_error(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            report = self._vault(td, "ok")
            led02 = [f for f in report.findings if f.code == "LED-02"]
            self.assertEqual(len(led02), 1)
            self.assertEqual(led02[0].severity, "error")
            self.assertIn("fuera de vocabulario", led02[0].detail)

    def test_health_y_lint_comparten_el_vocabulario(self):
        """La tupla incrustada en health._cobertura era la causa raíz de H-09."""
        self.assertTrue(schema.LEDGER_RESULTADOS_PROCESADA <= schema.LEDGER_RESULTADOS)

    def test_detenida_es_valida_pero_no_cuenta_como_procesada(self):
        """La regla de salto del gen manda reintentar lo `detenida`: no está hecha."""
        self.assertIn("detenida", schema.LEDGER_RESULTADOS)
        self.assertNotIn("detenida", schema.LEDGER_RESULTADOS_PROCESADA)


class TestExclusionDeCodigos(unittest.TestCase):
    """`--exclude` separa lo que causa el commit de lo que causa el calendario."""

    def test_temporales_desaparecen_del_reporte(self):
        r = lint.run(SUCIO, as_of=AS_OF, exclude=lint.CODIGOS_TEMPORALES)
        codigos = {f.code for f in r.findings}
        self.assertFalse(codigos & lint.CODIGOS_TEMPORALES, f"quedaron temporales: {codigos}")
        self.assertEqual(r.excluded, ["VIG-01", "VIG-02", "VIG-03"])

    def test_los_estructurales_siguen_fallando(self):
        """Excluir vencimientos NO debe volver verde un vault con enlaces rotos."""
        r = lint.run(SUCIO, as_of=AS_OF, exclude=lint.CODIGOS_TEMPORALES)
        self.assertIn("LNK-01", {f.code for f in r.findings})
        self.assertEqual(r.exit_code(strict=False), 1)

    def test_excluir_solo_lo_pedido(self):
        r = lint.run(SUCIO, as_of=AS_OF, exclude={"LNK-01"})
        codigos = {f.code for f in r.findings}
        self.assertNotIn("LNK-01", codigos)
        self.assertIn("VIG-01", codigos)

    def test_sin_exclude_no_cambia_nada(self):
        base = lint.run(SUCIO, as_of=AS_OF)
        igual = lint.run(SUCIO, as_of=AS_OF, exclude=set())
        self.assertEqual(base.render_text(), igual.render_text())
        self.assertEqual(base.excluded, [])

    def test_el_json_declara_lo_excluido(self):
        r = lint.run(SUCIO, as_of=AS_OF, exclude=lint.CODIGOS_TEMPORALES)
        self.assertIn('"excluded"', r.render_json())
        self.assertIn("VIG-01", r.render_json())   # visible aunque no haya hallazgos


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
