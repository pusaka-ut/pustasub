import unittest
import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from engine.translator import OfflineSentenceTranslator
from engine.server import app

class TestMilestone10CandyTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.translator = OfflineSentenceTranslator()

    def test_sentence_completion_boundaries(self):
        self.assertIsNotNone(self.translator.process_final_transcript("Welcome to Universitas Terbuka."))
        self.assertIsNotNone(self.translator.process_final_transcript("Are you ready for the conference?"))
        self.assertIsNotNone(self.translator.process_final_transcript("Higher education is accessible for everyone!"))
        self.assertIsNone(self.translator.process_final_transcript(""))
        self.assertIsNone(self.translator.process_final_transcript("   "))

    def test_offline_sentence_translation_ut_academic(self):
        text = "Universitas Terbuka is the pioneer of distance learning in Indonesia."
        translated = self.translator.translate_sentence(text)
        self.assertIn("Universitas Terbuka", translated)
        self.assertTrue("pionir" in translated.lower() or "pelopor" in translated.lower())
        self.assertTrue("pembelajaran jarak jauh" in translated.lower() or "pjj" in translated.lower())

    def test_translation_atomic_file_output(self):
        text = "The Rector delivered the opening speech today."
        translated = self.translator.process_final_transcript(text)
        self.assertIsNotNone(translated)
        self.assertTrue(os.path.exists("output/current_translation.txt"))
        with open("output/current_translation.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()
        self.assertEqual(content, translated)
        self.assertTrue("rektor" in content.lower())

    def test_device_switch_endpoint(self):
        resp = self.client.post("/api/control/device", json={"device_index": -1})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn(data["device_index"], [None, -1])
        self.assertIn("device_name", data)

    def test_translation_style_control_persistence(self):
        resp = self.client.post("/api/control/style", json={
            "translation_enabled": True,
            "translation_position": "top-right"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["style"]["translation_enabled"])
        self.assertEqual(data["style"]["translation_position"], "top-right")

        status_resp = self.client.get("/api/status")
        self.assertEqual(status_resp.status_code, 200)
        status_data = status_resp.json()
        self.assertTrue(status_data["overlay_style"]["translation_enabled"])
        self.assertEqual(status_data["overlay_style"]["translation_position"], "top-right")

    def test_zero_pure_white_rule_in_stylesheets(self):
        files_to_check = [
            os.path.join("web", "admin", "style.css"),
            os.path.join("web", "overlay", "style.css")
        ]
        hex_white_pattern = re.compile(r"#fff(?:fff)?\b", re.IGNORECASE)
        for filepath in files_to_check:
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            matches = hex_white_pattern.findall(content)
            self.assertEqual(len(matches), 0, f"Found pure white #{matches} in {filepath}")

    def test_zero_comments_rule_across_milestone10_files(self):
        files_to_check = [
            os.path.join("engine", "translator.py"),
            os.path.join("web", "admin", "app.js"),
            os.path.join("web", "overlay", "overlay.js"),
            os.path.join("web", "admin", "index.html"),
            os.path.join("web", "overlay", "index.html")
        ]
        for filepath in files_to_check:
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines, start=1):
                stripped = line.strip()
                if filepath.endswith(".py"):
                    if stripped.startswith("#"):
                        self.fail(f"Python comment found in {filepath}:{idx} -> {stripped}")
                elif filepath.endswith(".js"):
                    if stripped.startswith("//") or stripped.startswith("/*") or "*/" in stripped:
                        self.fail(f"JS comment found in {filepath}:{idx} -> {stripped}")
                elif filepath.endswith(".html"):
                    if "<!--" in stripped or "-->" in stripped:
                        self.fail(f"HTML comment found in {filepath}:{idx} -> {stripped}")

if __name__ == "__main__":
    unittest.main()
