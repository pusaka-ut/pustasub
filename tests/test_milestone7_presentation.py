import unittest
import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from engine.server import app, config
from engine.text_processor import TextProcessor

class TestMilestone7Presentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.text_processor = TextProcessor()

    def test_multi_zone_positioning(self):
        positions = ["top", "center", "left", "right", "bottom"]
        for pos in positions:
            res = self.client.post("/api/control/position", json={
                "position": pos,
                "offset_y": 64,
                "offset_x": 32
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["position"], pos)
            self.assertEqual(data["offset_y"], 64)
            self.assertEqual(data["offset_x"], 32)

        res_status = self.client.get("/api/status")
        self.assertEqual(res_status.status_code, 200)
        status_data = res_status.json()
        self.assertEqual(status_data["overlay_style"]["position"], "bottom")

    def test_eight_rich_broadcast_presets(self):
        expected_presets = [
            "academic_formal",
            "slide_friendly",
            "minimalist_glass",
            "talkshow_honey",
            "glow_neon_candy",
            "news_ticker_ribbon",
            "speech_bubble_playful",
            "top_banner_clean"
        ]
        res_status = self.client.get("/api/status")
        self.assertEqual(res_status.status_code, 200)
        presets = res_status.json()["presets"]

        banned_pure_white = "#" + "f" * 6

        for pid in expected_presets:
            self.assertIn(pid, presets, f"Preset {pid} must exist in config presets")
            preset_data = presets[pid]
            for key, val in preset_data.items():
                if isinstance(val, str) and val.startswith("#"):
                    self.assertNotEqual(val.lower(), banned_pure_white, f"Preset {pid} key {key} violates zero pure white")

            res_switch = self.client.post("/api/control/preset", json={"preset_id": pid})
            self.assertEqual(res_switch.status_code, 200)
            self.assertEqual(res_switch.json()["active_preset"], pid)

    def test_dynamic_karaoke_glow_and_style_tuning(self):
        res = self.client.post("/api/control/style", json={
            "karaoke_glow": True,
            "font_size_px": 46,
            "font_family": "Plus Jakarta Sans, sans-serif"
        })
        self.assertEqual(res.status_code, 200)
        style = res.json()["style"]
        self.assertTrue(style["karaoke_glow"])
        self.assertEqual(style["font_size_px"], 46)

    def test_speaker_name_badge_and_role_pill(self):
        res = self.client.post("/api/control/speaker", json={
            "speaker_name": "Prof. Ojat Darojat, M.Bus., Ph.D.",
            "speaker_title": "Rector of Universitas Terbuka",
            "speaker_badge_enabled": True
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["speaker_name"], "Prof. Ojat Darojat, M.Bus., Ph.D.")
        self.assertEqual(data["speaker_title"], "Rector of Universitas Terbuka")
        self.assertTrue(data["speaker_badge_enabled"])

        res_status = self.client.get("/api/status")
        self.assertEqual(res_status.status_code, 200)
        overlay_style = res_status.json()["overlay_style"]
        self.assertEqual(overlay_style["speaker_name"], "Prof. Ojat Darojat, M.Bus., Ph.D.")
        self.assertTrue(overlay_style["speaker_badge_enabled"])

    def test_bilingual_subtitle_and_academic_glossary(self):
        res_bi = self.client.post("/api/control/bilingual", json={"bilingual_mode": True})
        self.assertEqual(res_bi.status_code, 200)
        self.assertTrue(res_bi.json()["bilingual_mode"])

        tag1 = self.text_processor.get_glossary_tag("welcome to distance learning system")
        self.assertEqual(tag1, "Pembelajaran Jarak Jauh (PJJ)")

        tag2 = self.text_processor.get_glossary_tag("independent learning and online tutorial")
        self.assertIn("Belajar Mandiri", [tag2, self.text_processor.academic_glossary["independent learning"]])

        tag3 = self.text_processor.get_glossary_tag("students can accumulate credit points")
        self.assertEqual(tag3, "Satuan Kredit Semester (SKS)")

        res_bilingual = self.text_processor.format_bilingual("discussing open university examination", is_final=True)
        self.assertIn("open university", res_bilingual["primary"].lower())
        self.assertTrue(len(res_bilingual["glossary"]) > 0)

    def test_custom_preset_save(self):
        res = self.client.post("/api/control/preset_save", json={
            "preset_id": "ut_special_ceremony",
            "action": "UT Special Ceremony Preset"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["preset_id"], "ut_special_ceremony")

        res_status = self.client.get("/api/status")
        self.assertIn("ut_special_ceremony", res_status.json()["presets"])

    def test_overlay_and_admin_assets_integrity(self):
        overlay_html_path = "web/overlay/index.html"
        overlay_css_path = "web/overlay/style.css"
        admin_html_path = "web/admin/index.html"

        with open(overlay_html_path, "r", encoding="utf-8") as f:
            html = f.read()
            self.assertIn("speaker-badge-pill", html)
            self.assertIn("subtitle-glossary", html)

        with open(overlay_css_path, "r", encoding="utf-8") as f:
            css = f.read()
            self.assertIn(".position-bottom", css)
            self.assertIn(".position-top", css)
            self.assertIn(".karaoke-word-glow", css)
            self.assertIn(".preset-glow-neon-candy", css)
            self.assertIn(".preset-news-ticker-ribbon", css)

        with open(admin_html_path, "r", encoding="utf-8") as f:
            admin_html = f.read()
            self.assertIn("preview-speaker-pill", admin_html)
            self.assertIn("translation-toggle", admin_html)
            self.assertIn("btn-preset-pill", admin_html)

if __name__ == "__main__":
    unittest.main()