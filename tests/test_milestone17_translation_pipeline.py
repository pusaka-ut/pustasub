import os
import unittest
from fastapi.testclient import TestClient
from engine.server import app, on_final_transcript, file_writer, config
from engine.translator import OfflineSentenceTranslator

class TestMilestone17TranslationPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.translator = OfflineSentenceTranslator()

    def test_short_and_long_sentence_translation(self):
        res1 = self.translator.translate_sentence("Welcome to Universitas Terbuka")
        self.assertIn("Universitas Terbuka", res1)
        self.assertIn("Selamat datang", res1)

        res2 = self.translator.translate_sentence("Thank you very much")
        self.assertIn("Terima kasih", res2)

    def test_process_final_transcript_writes_file(self):
        self.translator.process_final_transcript("Good morning ladies and gentlemen")
        self.assertTrue(os.path.exists("output/current_translation.txt"))
        with open("output/current_translation.txt", encoding="utf-8") as f:
            content = f.read().strip()
        self.assertTrue(len(content) > 0)
        self.assertTrue("pagi" in content.lower() or "selamat" in content.lower())

    def test_server_on_final_transcript_bilingual_mode(self):
        config.overlay_style.bilingual_mode = True
        config.overlay_style.translation_enabled = True
        on_final_transcript("Welcome to the international academic webinar")

        with open(file_writer.output_path, encoding="utf-8") as f:
            sub_content = f.read().strip()
        self.assertIn("Welcome", sub_content)
        self.assertIn("\n", sub_content)

        with open("output/current_translation.txt", encoding="utf-8") as f:
            trans_content = f.read().strip()
        self.assertTrue(len(trans_content) > 0)

    def test_offline_lexicon_fallback(self):
        offline_res = self.translator._offline_lexicon_translate("Welcome to Universitas Terbuka")
        self.assertIn("Selamat datang di Universitas Terbuka", offline_res)

    def test_websocket_receives_translation_event(self):
        with self.client.websocket_connect("/ws") as ws:
            init_data = ws.receive_json()
            self.assertEqual(init_data.get("event"), "init_state")

            on_final_transcript("Higher education in Indonesia is transforming")

            ev1 = ws.receive_json()
            self.assertEqual(ev1.get("event"), "final_subtitle")
            ev2 = ws.receive_json()
            self.assertEqual(ev2.get("event"), "translation_sentence")
            self.assertIn("indonesian", ev2)

    def test_switch_translation_control(self):
        res = self.client.post("/api/control/translation", json={"enabled": True, "position": "top-right"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("translation_enabled"))
        self.assertEqual(res.json().get("translation_position"), "top-right")

if __name__ == "__main__":
    unittest.main()
