"""El checklist pre-push de ops/runbook-git-seguro.md no debe dar falsos positivos.

Dos aparecieron en los pushes del 2026-10-23: el paso 5 preguntaba a `git check-ignore` por una
carpeta que aún no existe (un patrón de directorio no casa contra una ruta inexistente ⇒ falso
ALTO en todo clon fresco), y el barrido de secretos buscaba la raíz `secret`, que casa con
"secretaría", "secretarios" y "secretos" — vocabulario normal del sector público. Estos tests
leen el patrón y las sondas DESDE el runbook, así que si alguien los edita, el test lo revisa.
"""
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNBOOK = REPO / "ops" / "runbook-git-seguro.md"


def _texto() -> str:
    return RUNBOOK.read_text(encoding="utf-8")


def _patron_secretos() -> str:
    """El valor de SEC='…' tal como lo define el runbook (debe ser uno solo, repetido igual)."""
    valores = set(re.findall(r"^\s*SEC='([^']+)'", _texto(), re.M))
    assert len(valores) == 1, f"el runbook define SEC de {len(valores)} formas distintas: {valores}"
    return valores.pop()


def _sondas() -> list[str]:
    return re.findall(r"git check-ignore -q (\S+)", _texto())


class TestBarridoDeSecretos(unittest.TestCase):
    def setUp(self):
        # misma semántica que `grep -iE`: ERE con \b, sin distinguir mayúsculas
        self.rx = re.compile(_patron_secretos(), re.I)

    def test_no_casa_con_vocabulario_del_sector_publico(self):
        for frase in ("la secretaría de gobierno", "116 secretarios de gobierno",
                      "no hay secretos en el diff", "el secreto profesional",
                      "coste en tokens de contexto", "una contraseñanueva pegada"):
            with self.subTest(frase=frase):
                self.assertIsNone(self.rx.search(frase), frase)

    def test_casa_con_secretos_reales(self):
        for frase in ("SECRET=abc123", "api_key: sk-live-1", "API-KEY=…", "token: ghp_x",
                      "password=hunter2", "passwd: x", "contraseña: 1234", "contrasena=1234",
                      "-----BEGIN OPENSSH PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----"):
            with self.subTest(frase=frase):
                self.assertIsNotNone(self.rx.search(frase), frase)

    def test_el_paso_4b_y_el_incidente_usan_el_mismo_patron(self):
        # _patron_secretos ya falla si hay más de una definición; aquí se exige que haya dos usos
        self.assertGreaterEqual(_texto().count("SEC='"), 2)


class TestPaso5Sondas(unittest.TestCase):
    def test_las_sondas_son_rutas_dentro_de_las_carpetas_no_las_carpetas(self):
        sondas = _sondas()
        self.assertGreaterEqual(len(sondas), 3, sondas)
        for s in sondas:
            with self.subTest(sonda=s):
                self.assertIn("/", s)
                self.assertFalse(s.endswith("/"), "la sonda debe ser un archivo, no una carpeta")

    def test_git_ignora_cada_sonda_aunque_la_carpeta_no_exista(self):
        for s in _sondas():
            with self.subTest(sonda=s):
                carpeta = REPO / Path(s).parent
                # el caso que daba el falso ALTO: la carpeta derivada no existe en un clon fresco
                if s.startswith("graphify-out") or ".state" in s:
                    self.assertFalse(carpeta.exists(), f"{carpeta} no debería existir en el template")
                r = subprocess.run(["git", "check-ignore", "-q", s], cwd=REPO)
                self.assertEqual(r.returncode, 0, f"{s} no está ignorado por .gitignore")

    def test_una_ruta_normal_no_esta_ignorada(self):
        r = subprocess.run(["git", "check-ignore", "-q", "wiki/sonda.md"], cwd=REPO)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
