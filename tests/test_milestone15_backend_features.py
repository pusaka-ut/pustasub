import os
import sys
import re
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from engine.server import app, db_manager, translator

class TestMilestone15BackendFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.html_path = os.path.join("web", "admin", "index.html")
        cls.css_path = os.path.join("web", "admin", "style.css")
        cls.vocab_js_path = os.path.join("web", "admin", "js", "vocab-manager.js")
        cls.ws_js_path = os.path.join("web", "admin", "js", "websocket.js")

        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()
        with open(cls.css_path, "r", encoding="utf-8") as f:
            cls.css_content = f.read()
        with open(cls.vocab_js_path, "r", encoding="utf-8") as f:
            cls.vocab_js_content = f.read()
        with open(cls.ws_js_path, "r", encoding="utf-8") as f:
            cls.ws_js_content = f.read()

    def test_engine_control_endpoint(self):
        res = self.client.post("/api/control/engine", json={"running": False})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["is_running"])

    def test_devices_endpoint(self):
        res = self.client.get("/api/devices")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("devices", data)
        self.assertIn("active_device_name", data)

    def test_translation_control_endpoint(self):
        res = self.client.post("/api/control/translation", json={"enabled": True, "position": "top-right"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["translation_enabled"])
        self.assertEqual(data["translation_position"], "top-right")

    def test_vocabulary_crud_alignment(self):
        get_res = self.client.get("/api/vocabulary")
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.json()
        self.assertTrue(get_data["success"])
        self.assertIn("items", get_data)
        self.assertIn("vocabulary", get_data)

        test_term = "Milestone 15 Test Term"
        add_res = self.client.post("/api/vocabulary", json={"term": test_term, "category": "technology", "weight": 2.5})
        self.assertEqual(add_res.status_code, 200)
        add_data = add_res.json()
        self.assertTrue(add_data["success"])

        items = db_manager.get_all_vocabulary()
        created = next((item for item in items if item["term"] == test_term), None)
        self.assertIsNotNone(created)

        del_res = self.client.delete(f"/api/vocabulary/{created['id']}")
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.json()["removed"])

    def test_sentence_translation_execution(self):
        sample_sentence = "Welcome to Universitas Terbuka annual international conference."
        translated = translator.translate_sentence(sample_sentence)
        self.assertIn("Universitas Terbuka", translated)
        self.assertTrue("selamat datang" in translated.lower())

    def test_modal_dialog_markup_and_elements(self):
        self.assertIn('id="open-vocab-modal-btn"', self.html_content)
        self.assertIn('id="vocab-modal-backdrop"', self.html_content)
        self.assertIn('id="vocab-modal"', self.html_content)
        self.assertIn('id="modal-vocab-search"', self.html_content)
        self.assertIn('class="btn-candy-pill btn-modal-filter', self.html_content)
        self.assertIn('id="modal-vocab-list"', self.html_content)
        self.assertIn('id="close-vocab-modal-btn"', self.html_content)

    def test_modal_styling_integrity(self):
        self.assertIn(".candy-modal-backdrop", self.css_content)
        self.assertIn(".candy-modal", self.css_content)
        self.assertIn(".modal-header-row", self.css_content)
        self.assertIn(".modal-search-wrapper", self.css_content)
        self.assertIn(".modal-body-scroll", self.css_content)
        self.assertIn(".modal-item-card", self.css_content)

    def test_javascript_websocket_and_vocab_manager(self):
        self.assertIn("data.event || data.type", self.ws_js_content)
        self.assertIn("openModal()", self.vocab_js_content)
        self.assertIn("closeModal()", self.vocab_js_content)
        self.assertIn("renderModal()", self.vocab_js_content)
        self.assertIn("data.vocabulary || data.items", self.vocab_js_content)

    def test_zero_comments_and_zero_pure_white(self):
        for path, content in [
            (self.html_path, self.html_content),
            (self.css_path, self.css_content),
            (self.vocab_js_path, self.vocab_js_content),
            (self.ws_js_path, self.ws_js_content)
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

            matches = re.findall(r"#ffffff\b|#fff\b", content, flags=re.IGNORECASE)
            self.assertEqual(len(matches), 0, f"Pure white found in {path}")

if __name__ == "__main__":
    unittest.main()