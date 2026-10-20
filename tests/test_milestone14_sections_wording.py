import os
import unittest
import re

class TestMilestone14SectionsWording(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join("web", "admin", "index.html")
        cls.css_path = os.path.join("web", "admin", "style.css")
        cls.ui_ctrl_path = os.path.join("web", "admin", "js", "ui-controller.js")
        cls.app_path = os.path.join("web", "admin", "js", "app.js")
        cls.vocab_path = os.path.join("web", "admin", "js", "vocab-manager.js")

        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        with open(cls.css_path, "r", encoding="utf-8") as f:
            cls.css_content = f.read()

        with open(cls.ui_ctrl_path, "r", encoding="utf-8") as f:
            cls.ui_ctrl_content = f.read()

        with open(cls.app_path, "r", encoding="utf-8") as f:
            cls.app_content = f.read()

        with open(cls.vocab_path, "r", encoding="utf-8") as f:
            cls.vocab_content = f.read()

    def test_three_independent_cards_in_secondary_zone(self):
        self.assertIn('class="device-card candy-card"', self.html_content)
        self.assertIn('class="vocab-card candy-card"', self.html_content)
        self.assertIn('class="styling-card candy-card"', self.html_content)
        self.assertIn("Sumber Suara", self.html_content)
        self.assertIn("Kamus Istilah Khusus", self.html_content)
        self.assertIn("Gaya &amp; Posisi Subtitle", self.html_content)
        self.assertNotIn('id="settings-drawer"', self.html_content)
        self.assertNotIn('Broadcast Styling & Tuning', self.html_content)

    def test_purged_technical_jargon(self):
        forbidden_jargon = [
            "(SQLite Indexed)",
            "(WASAPI)",
            "Audio Ingestion Mode",
            "Broadcast Styling & Tuning",
            "Live Style Tuning",
            "Master Broadcast Control"
        ]
        for jargon in forbidden_jargon:
            self.assertNotIn(jargon, self.html_content)
            self.assertNotIn(jargon, self.ui_ctrl_content)
            self.assertNotIn(jargon, self.app_content)

    def test_humanized_wording_master_controls(self):
        self.assertIn("Kendali Utama Siaran", self.html_content)
        self.assertIn("Mulai Subtitle", self.html_content)
        self.assertIn("Hapus Layar", self.html_content)
        self.assertIn("Tahan Teks", self.html_content)
        self.assertIn("Indikator Suara Masuk", self.html_content)
        self.assertIn("Suara Komputer (Loopback Default)", self.html_content)
        self.assertIn("Salin Tautan OBS", self.html_content)
        self.assertIn("Salin Jalur vMix", self.html_content)

    def test_humanized_wording_live_monitor_and_translation(self):
        self.assertIn("Monitor Siaran Langsung (16:9)", self.html_content)
        self.assertIn("Buka Jendela Overlay", self.html_content)
        self.assertIn("TERJEMAHAN ID", self.html_content)
        self.assertIn("Terjemahan Bahasa Indonesia", self.html_content)
        self.assertIn("Kalimat Terjemahan Terakhir", self.html_content)
        self.assertIn("Posisi Kotak Terjemahan", self.html_content)
        self.assertIn("Kanan Bawah", self.html_content)
        self.assertIn("Kanan Atas", self.html_content)
        self.assertIn("Bawah Teks", self.html_content)

    def test_humanized_wording_javascript_controllers(self):
        self.assertIn("Hentikan Subtitle", self.ui_ctrl_content)
        self.assertIn("Mulai Subtitle", self.ui_ctrl_content)
        self.assertIn("Lanjutkan Teks", self.ui_ctrl_content)
        self.assertIn("Tahan Teks", self.ui_ctrl_content)
        self.assertIn("Suara Komputer (Loopback Default)", self.ui_ctrl_content)
        self.assertIn("Layar subtitle telah dikosongkan", self.app_content)
        self.assertIn("Siaran subtitle dimulai", self.app_content)
        self.assertIn("Gagal memuat kamus istilah", self.vocab_content)

    def test_css_three_cards_and_spacing_support(self):
        self.assertIn(".device-card,", self.css_content)
        self.assertIn(".vocab-card,", self.css_content)
        self.assertIn(".styling-card", self.css_content)
        self.assertIn(".vocab-count-badge", self.css_content)
        self.assertIn(".card-header-row", self.css_content)

    def test_zero_comments_integrity(self):
        for path, content in [
            (self.html_path, self.html_content),
            (self.css_path, self.css_content),
            (self.ui_ctrl_path, self.ui_ctrl_content),
            (self.app_path, self.app_content),
            (self.vocab_path, self.vocab_content)
        ]:
            if path.endswith(".html"):
                self.assertNotIn("<!--", content)
            elif path.endswith(".css"):
                self.assertNotIn("/*", content)
            elif path.endswith(".js"):
                lines = content.splitlines()
                for idx, line in enumerate(lines, 1):
                    stripped = line.strip()
                    self.assertFalse(stripped.startswith("//"), f"Comment at {path}:{idx}")
                    self.assertFalse(stripped.startswith("/*"), f"Comment at {path}:{idx}")

    def test_zero_pure_white_rule(self):
        for path, content in [
            (self.html_path, self.html_content),
            (self.css_path, self.css_content),
            (self.ui_ctrl_path, self.ui_ctrl_content),
            (self.app_path, self.app_content),
            (self.vocab_path, self.vocab_content)
        ]:
            matches = re.findall(r"#ffffff\b|#fff\b", content, flags=re.IGNORECASE)
            self.assertEqual(len(matches), 0, f"Pure white found in {path}: {matches}")

if __name__ == "__main__":
    unittest.main()