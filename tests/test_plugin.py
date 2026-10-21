"""El envoltorio plugin/ (Fase 4.2) existe, parsea y solo ENVUELVE el repo.

No prueba Claude Code (no hay harness aquí): prueba que los manifiestos JSON son válidos y
coherentes entre sí, que la skill tiene el frontmatter que el ecosistema exige y que sigue
remitiendo a `init --profile`, `onboard apply` y al CLAUDE.md del vault en vez de replicar
reglas del genoma.
"""
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
PLUGIN_DIR = REPO / "plugin"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
SKILL = PLUGIN_DIR / "skills" / "cerebro" / "SKILL.md"


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md sin frontmatter"
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


class TestPlugin(unittest.TestCase):
    def test_manifiestos_parsean_y_coinciden(self):
        mk = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        pl = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        self.assertEqual(len(mk["plugins"]), 1)
        entrada = mk["plugins"][0]
        self.assertEqual(entrada["name"], pl["name"])
        self.assertEqual(entrada["version"], pl["version"])
        self.assertEqual((REPO / entrada["source"]).resolve(), PLUGIN_DIR.resolve())
        self.assertTrue((REPO / entrada["source"] / ".claude-plugin" / "plugin.json").is_file())

    def test_skill_tiene_frontmatter_y_remite_al_repo(self):
        texto = SKILL.read_text(encoding="utf-8")
        fm = frontmatter(texto)
        self.assertEqual(fm.get("name"), "cerebro")
        self.assertTrue(len(fm.get("description", "")) > 80)
        for frase in ("init --profile", "onboard apply", "CLAUDE.md", "git clone",
                      "events append", "verify"):
            self.assertIn(frase, texto, frase)
        # no sustituye al repo: lo dice y no trae genes propios
        self.assertRegex(texto.lower(), r"no (reemplaza|sustituye)")
        self.assertFalse(list(PLUGIN_DIR.rglob("gen-*.md")), "el plugin no debe traer genes")

    def test_skill_menciona_todos_los_perfiles(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from cerebro_core import schema
        texto = SKILL.read_text(encoding="utf-8")
        for perfil in schema.PROFILE_ORDER:
            self.assertIn(f"`{perfil}`", texto)


if __name__ == "__main__":
    unittest.main()
