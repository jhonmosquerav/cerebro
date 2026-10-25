"""Tests de ATR-01 — el aprobador siempre tiene dueño (gen-compuerta-mutacion v5).

Cubre la resolución de identidad (clave de firma ↔ ops/allowed_signers → git user.email →
error), el rechazo en escritura, los detectores EVT-09/EVT-10, la corrección por evento
`attribution_corrected` y que ONBOARD resuelva la identidad por la CLI sin tocar los bytes
de los casos trabajados (que llaman a la API sobre un ledger nuevo).
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cerebro_core import events, identity, onboard

from test_onboard import esqueleto

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "tools" / "cerebro.py"

KEY_A = "AAAAC3NzaC1lZDI1NTE5AAAAIClaveDePruebaAnaParaTestsDeAtribucion0001"
KEY_B = "AAAAC3NzaC1lZDI1NTE5AAAAIClaveDePruebaBetoParaTestsDeAtribucion002"
SIGNERS = (
    "# firmantes autorizados (comentario)\n"
    "#   operador@empresa.com namespaces=\"git\" ssh-ed25519 AAAAejemplo\n"
    "\n"
    f"ana@empresa.test namespaces=\"git\" ssh-ed25519 {KEY_A}\n"
    f"beto@empresa.test,b@empresa.test ssh-ed25519 {KEY_B} beto-laptop\n"
)


def ev(approved_by: str, target: str = "gen-x", **extra) -> dict:
    base = {"ts": "2026-10-25", "type": "gene_edited", "target": target,
            "signal": "señal de prueba", "diff": "v1 → v2",
            "approved_by": approved_by, "status": "applied"}
    base.update(extra)
    return base


def linea(e: dict) -> str:
    return json.dumps(e, ensure_ascii=False, separators=(",", ":"))


def sha(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def ledger_con(td: str, lineas: list[str]) -> Path:
    p = Path(td) / "events.jsonl"
    p.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return p


def codigos(p: Path) -> list[str]:
    return [f.code for f in events.verify_file(p)]


def vault_con_signers(td: str) -> Path:
    root = Path(td)
    (root / "ops").mkdir(parents=True, exist_ok=True)
    (root / "ops" / "allowed_signers").write_text(SIGNERS, encoding="utf-8")
    return root


def git_falso(valores: dict):
    return lambda clave: valores.get(clave)


class TestGenericos(unittest.TestCase):
    def test_reconoce_genericos_sin_distinguir_mayusculas(self):
        for v in ("user", "USER", " Operador ", "agente", "claude", "n/a", "-", "?", ""):
            self.assertTrue(identity.is_generic(v), v)

    def test_identidad_real_no_es_generica(self):
        for v in ("ana@empresa.test", "Ana Pérez", "jhonmosquerav"):
            self.assertFalse(identity.is_generic(v), v)


class TestAllowedSigners(unittest.TestCase):
    def test_parsea_principales_y_clave_ignorando_comentarios(self):
        with tempfile.TemporaryDirectory() as td:
            firmantes = identity.signers(vault_con_signers(td))
        self.assertEqual(firmantes, [(["ana@empresa.test"], KEY_A),
                                     (["beto@empresa.test", "b@empresa.test"], KEY_B)])

    def test_sin_archivo_no_hay_firmantes(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(identity.signers(Path(td)), [])

    def test_el_repo_tiene_un_firmante_registrado(self):
        firmantes = identity.signers(REPO)
        self.assertEqual(len(firmantes), 1)
        self.assertIn("@", firmantes[0][0][0])


class TestResolver(unittest.TestCase):
    def test_explicito_generico_se_rechaza(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(identity.IdentityError):
                identity.resolve(Path(td), "user", git=git_falso({}))

    def test_explicito_real_sin_firmantes_no_avisa(self):
        with tempfile.TemporaryDirectory() as td:
            ident = identity.resolve(Path(td), "ana@empresa.test", git=git_falso({}))
        self.assertEqual((ident.value, ident.avisos), ("ana@empresa.test", []))

    def test_explicito_no_registrado_avisa(self):
        with tempfile.TemporaryDirectory() as td:
            ident = identity.resolve(vault_con_signers(td), "carla@otra.test",
                                     git=git_falso({}))
        self.assertEqual(ident.value, "carla@otra.test")
        self.assertTrue(any("allowed_signers" in a for a in ident.avisos))

    def test_clave_de_firma_en_archivo_pub(self):
        with tempfile.TemporaryDirectory() as td:
            root = vault_con_signers(td)
            pub = root / "beto.pub"
            pub.write_text(f"ssh-ed25519 {KEY_B} beto\n", encoding="utf-8")
            ident = identity.resolve(root, git=git_falso({
                "gpg.format": "ssh", "user.signingkey": str(pub),
                "user.email": "otro@correo.test"}))
        self.assertEqual(ident.value, "beto@empresa.test")
        self.assertEqual(ident.avisos, [])
        self.assertIn("allowed_signers", ident.source)

    def test_clave_privada_busca_su_pub(self):
        with tempfile.TemporaryDirectory() as td:
            root = vault_con_signers(td)
            (root / "id_ana").write_text("-----PRIVADA (no se lee)-----\n", encoding="utf-8")
            (root / "id_ana.pub").write_text(f"ssh-ed25519 {KEY_A}\n", encoding="utf-8")
            ident = identity.resolve(root, git=git_falso({
                "gpg.format": "ssh", "user.signingkey": str(root / "id_ana")}))
        self.assertEqual(ident.value, "ana@empresa.test")

    def test_clave_literal_key_prefijo(self):
        with tempfile.TemporaryDirectory() as td:
            ident = identity.resolve(vault_con_signers(td), git=git_falso({
                "gpg.format": "ssh", "user.signingkey": f"key::ssh-ed25519 {KEY_A}"}))
        self.assertEqual(ident.value, "ana@empresa.test")

    def test_clave_que_no_casa_cae_a_git_email_con_aviso(self):
        """El caso del clon: hereda la clave del autor del template y firma con otra."""
        with tempfile.TemporaryDirectory() as td:
            ident = identity.resolve(vault_con_signers(td), git=git_falso({
                "gpg.format": "ssh", "user.signingkey": "key::ssh-ed25519 AAAAotraClave",
                "user.email": "nueva@empresa.test"}))
        self.assertEqual(ident.value, "nueva@empresa.test")
        self.assertTrue(any("allowed_signers" in a for a in ident.avisos))

    def test_sin_formato_ssh_no_usa_la_clave(self):
        with tempfile.TemporaryDirectory() as td:
            ident = identity.resolve(vault_con_signers(td), git=git_falso({
                "user.signingkey": f"key::ssh-ed25519 {KEY_A}",
                "user.email": "ana@empresa.test"}))
        self.assertEqual((ident.value, ident.source), ("ana@empresa.test", "git user.email"))
        self.assertEqual(ident.avisos, [], "registrada por correo: sin aviso")

    def test_sin_identidad_alguna_es_error(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(identity.IdentityError):
                identity.resolve(Path(td), git=git_falso({}))

    def test_email_generico_de_git_no_vale(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(identity.IdentityError):
                identity.resolve(Path(td), git=git_falso({"user.email": "user"}))


class TestDetectores(unittest.TestCase):
    def test_generico_tras_iniciar_la_atribucion_es_evt09(self):
        with tempfile.TemporaryDirectory() as td:
            p = ledger_con(td, [linea(ev("ana@empresa.test")), linea(ev("user"))])
            fnds = events.verify_file(p)
        self.assertTrue(any(f.code == "EVT-09" and f.severity == "error" for f in fnds),
                        [f.render() for f in fnds])

    def test_genericos_previos_a_la_atribucion_son_historia_valida(self):
        with tempfile.TemporaryDirectory() as td:
            p = ledger_con(td, [linea(ev("user")), linea(ev("user")),
                                linea(ev("ana@empresa.test"))])
            self.assertNotIn("EVT-09", codigos(p))

    def test_ledger_solo_generico_no_inicia_la_atribucion(self):
        """Los worked/ regeneran ledgers nuevos con `user`: siguen válidos."""
        with tempfile.TemporaryDirectory() as td:
            p = ledger_con(td, [linea(ev("user")), linea(ev("user"))])
            self.assertEqual(codigos(p), [])

    def test_la_correccion_cura_la_linea(self):
        with tempfile.TemporaryDirectory() as td:
            mala = linea(ev("user"))
            correccion = ev("ana@empresa.test", target="genome/events.jsonl",
                            type="attribution_corrected", corrects=[sha(mala)])
            p = ledger_con(td, [linea(ev("ana@empresa.test")), mala, linea(correccion)])
            cods = codigos(p)
        self.assertNotIn("EVT-09", cods)
        self.assertNotIn("EVT-10", cods)

    def test_correccion_que_apunta_a_linea_inexistente_es_evt10(self):
        with tempfile.TemporaryDirectory() as td:
            correccion = ev("ana@empresa.test", type="attribution_corrected",
                            corrects=["0" * 64])
            p = ledger_con(td, [linea(ev("ana@empresa.test")), linea(correccion)])
            self.assertIn("EVT-10", codigos(p))

    def test_correccion_mal_formada_es_evt10(self):
        for corrects in ([], ["no-es-un-sha"], "9d2e", None):
            with tempfile.TemporaryDirectory() as td:
                correccion = ev("ana@empresa.test", type="attribution_corrected",
                                corrects=corrects)
                p = ledger_con(td, [linea(ev("ana@empresa.test")), linea(correccion)])
                self.assertIn("EVT-10", codigos(p), corrects)

    def test_correccion_con_aprobador_generico_es_evt10(self):
        with tempfile.TemporaryDirectory() as td:
            mala = linea(ev("user"))
            correccion = ev("user", type="attribution_corrected", corrects=[sha(mala)])
            p = ledger_con(td, [linea(ev("ana@empresa.test")), mala, linea(correccion)])
            self.assertIn("EVT-10", codigos(p))


class TestEscritura(unittest.TestCase):
    def test_append_rechaza_generico_con_atribucion_iniciada(self):
        with tempfile.TemporaryDirectory() as td:
            p = ledger_con(td, [linea(ev("ana@empresa.test"))])
            antes = p.read_text(encoding="utf-8")
            with self.assertRaises(events.EventError):
                events.append_line(p, ev("user"))
            self.assertEqual(p.read_text(encoding="utf-8"), antes)

    def test_append_admite_generico_en_ledger_nuevo(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "events.jsonl"
            events.append_line(p, ev("user"))
            events.append_line(p, ev("user", target="gen-y"))
            self.assertEqual(codigos(p), [])

    def test_append_rechaza_aprobador_vacio(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(events.EventError):
                events.append_line(Path(td) / "events.jsonl", ev("  "))

    def test_append_valida_la_correccion(self):
        with tempfile.TemporaryDirectory() as td:
            p = ledger_con(td, [linea(ev("ana@empresa.test"))])
            with self.assertRaises(events.EventError):
                events.append_line(p, ev("ana@empresa.test", type="attribution_corrected",
                                         corrects=["f" * 64]))
            with self.assertRaises(events.EventError):
                events.append_line(p, ev("ana@empresa.test", corrects=[sha(linea(ev("x")))]))

    def test_append_de_correccion_ordena_corrects_tras_status(self):
        with tempfile.TemporaryDirectory() as td:
            mala = linea(ev("user"))
            p = ledger_con(td, [mala, linea(ev("ana@empresa.test"))])
            escrita = events.append_line(p, ev(
                "ana@empresa.test", target="genome/events.jsonl",
                type="attribution_corrected", corrects=[sha(mala)]))
            claves = list(json.loads(escrita))
            self.assertEqual(claves[claves.index("status") + 1], "corrects")
            self.assertEqual(claves[-1], "prev")
            self.assertEqual([f for f in events.verify_file(p) if f.severity == "error"], [])


def entorno_git_aislado(td: str) -> dict:
    """Sin la configuración global ni de sistema de quien corre los tests."""
    vacio = Path(td) / "gitconfig-vacio"
    vacio.write_text("", encoding="utf-8")
    env = dict(os.environ)
    env.update({"GIT_CONFIG_GLOBAL": str(vacio), "GIT_CONFIG_NOSYSTEM": "1"})
    return env


def correr(env: dict, *args):
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True,
                          text=True, encoding="utf-8", cwd=REPO, env=env)


def repo_git(root: Path, env: dict, email: str | None):
    subprocess.run(["git", "init", "-q", str(root)], check=True, env=env)
    if email:
        subprocess.run(["git", "-C", str(root), "config", "user.email", email],
                       check=True, env=env)


class TestCli(unittest.TestCase):
    def _vault_con_ledger(self, td: str, lineas: list[str], email: str | None) -> tuple:
        root = Path(td) / "vault"
        (root / "genome").mkdir(parents=True)
        if lineas:
            (root / "genome" / "events.jsonl").write_text("\n".join(lineas) + "\n",
                                                         encoding="utf-8")
        env = entorno_git_aislado(td)
        repo_git(root, env, email)
        return root, env

    def _append(self, env, root, *extra):
        return correr(env, "--vault", str(root), "events", "append", "--type", "gene_edited",
                      "--target", "gen-x", "--signal", "s", "--diff", "v1 → v2", *extra)

    def test_append_resuelve_la_identidad_de_git(self):
        with tempfile.TemporaryDirectory() as td:
            root, env = self._vault_con_ledger(td, [linea(ev("ana@empresa.test"))],
                                               "ana@empresa.test")
            r = self._append(env, root)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            ultima = (root / "genome" / "events.jsonl").read_text(encoding="utf-8").strip()
            self.assertEqual(json.loads(ultima.split("\n")[-1])["approved_by"],
                             "ana@empresa.test")
            self.assertIn("aprobador", r.stdout)

    def test_append_sin_identidad_sale_2_sin_escribir(self):
        with tempfile.TemporaryDirectory() as td:
            root, env = self._vault_con_ledger(td, [linea(ev("ana@empresa.test"))], None)
            antes = (root / "genome" / "events.jsonl").read_text(encoding="utf-8")
            r = self._append(env, root)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertEqual((root / "genome" / "events.jsonl").read_text(encoding="utf-8"),
                             antes)

    def test_append_con_approved_by_generico_sale_2(self):
        with tempfile.TemporaryDirectory() as td:
            root, env = self._vault_con_ledger(td, [linea(ev("ana@empresa.test"))],
                                               "ana@empresa.test")
            r = self._append(env, root, "--approved-by", "user")
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_append_corrects_escribe_la_correccion(self):
        with tempfile.TemporaryDirectory() as td:
            mala = linea(ev("user"))
            root, env = self._vault_con_ledger(
                td, [mala, linea(ev("ana@empresa.test"))], "ana@empresa.test")
            r = correr(env, "--vault", str(root), "events", "append",
                       "--type", "attribution_corrected", "--target", "genome/events.jsonl",
                       "--signal", "s", "--diff", "user → ana", "--corrects", sha(mala))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            ultima = (root / "genome" / "events.jsonl").read_text(encoding="utf-8")
            self.assertEqual(json.loads(ultima.strip().split("\n")[-1])["corrects"],
                             [sha(mala)])

    def test_onboard_cli_atribuye_las_siembras(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "vault"
            base.mkdir()
            root = esqueleto(str(base))
            env = entorno_git_aislado(td)
            repo_git(root, env, "ana@empresa.test")
            r = correr(env, "--vault", str(root), "onboard", "apply", "--date", "2026-10-25")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            filas = [json.loads(l) for l in (root / "genome" / "events.jsonl")
                     .read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertGreater(len(filas), 0)
            self.assertEqual({f["approved_by"] for f in filas}, {"ana@empresa.test"})


class TestOnboardApi(unittest.TestCase):
    def test_api_con_generico_en_ledger_atribuido_aborta_sin_escribir(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            ledger = root / "genome" / "events.jsonl"
            ledger.write_text(linea(ev("ana@empresa.test")) + "\n", encoding="utf-8")
            antes = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            with self.assertRaises(onboard.OnboardError):
                onboard.apply(root / "onboard" / "company.yaml", root, date="2026-10-25")
            self.assertEqual(sorted(str(p.relative_to(root)) for p in root.rglob("*")), antes)
            self.assertEqual(len(ledger.read_text(encoding="utf-8").splitlines()), 1)

    def test_api_con_identidad_real_la_usa(self):
        with tempfile.TemporaryDirectory() as td:
            root = esqueleto(td)
            onboard.apply(root / "onboard" / "company.yaml", root, date="2026-10-25",
                          approved_by="ana@empresa.test")
            filas = [json.loads(l) for l in (root / "genome" / "events.jsonl")
                     .read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual({f["approved_by"] for f in filas}, {"ana@empresa.test"})


class TestLedgerReal(unittest.TestCase):
    def test_lineas_95_a_97_estan_curadas(self):
        fnds = events.verify_file(REPO / "genome" / "events.jsonl")
        self.assertEqual([f.render() for f in fnds if f.code in ("EVT-09", "EVT-10")], [])


if __name__ == "__main__":
    unittest.main()
