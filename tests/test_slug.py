"""Tests del slug determinista (gen-identidad-de-pagina v2)."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from cerebro_core.slug import slugify


class TestSlug(unittest.TestCase):
    def test_diacriticos(self):
        self.assertEqual(slugify("Café con Ñandú"), "cafe-con-nandu")
        self.assertEqual(slugify("PISCC Bucaramanga — Seguridad"), "piscc-bucaramanga-seguridad")

    def test_colapso_y_recorte(self):
        self.assertEqual(slugify("  hola --- mundo!!  "), "hola-mundo")
        self.assertEqual(slugify("¿qué? ***"), "que")

    def test_maximo_60(self):
        s = slugify("a" * 59 + " zz")
        self.assertLessEqual(len(s), 60)
        self.assertFalse(s.endswith("-"))

    def test_vacio_usa_hash(self):
        self.assertEqual(slugify("¡¡¡", fallback_hash="abcdef1234567890"), "f-abcdef12")

    def test_determinista(self):
        self.assertEqual(slugify("Bot WhatsApp 2.0"), slugify("Bot WhatsApp 2.0"))
        self.assertEqual(slugify("Bot WhatsApp 2.0"), "bot-whatsapp-2-0")


if __name__ == "__main__":
    unittest.main()
