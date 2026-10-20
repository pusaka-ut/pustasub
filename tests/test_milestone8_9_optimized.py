import unittest
import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from engine.db import DatabaseManager, DEFAULT_DB_PATH as DB_PATH
from engine.config import AppConfig
from engine.server import app, db_manager

class TestMilestone8And9Optimized(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_sqlite_database_tables_and_wal(self):
        self.assertTrue(os.path.exists(DB_PATH))
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode;")
            row = cursor.fetchone()
            self.assertEqual(row[0].lower(), "wal")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cursor.fetchall()]
            required = ["vocabulary", "speaker_profiles", "presets", "session_history", "system_settings"]
            for req in required:
                self.assertIn(req, tables)

    def test_preseeded_universitas_terbuka_terms(self):
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vocabulary;")
            total = cursor.fetchone()[0]
            self.assertGreaterEqual(total, 59)
            cursor.execute("SELECT term FROM vocabulary WHERE category='leadership';")
            leadership = [r[0] for r in cursor.fetchall()]
            self.assertTrue(any("Ojat" in term for term in leadership))
            cursor.execute("SELECT term FROM vocabulary WHERE category='academic';")
            academic = [r[0] for r in cursor.fetchall()]
            self.assertTrue(any("PJJ" in term or "Distance" in term for term in academic))

    def test_vocabulary_crud_database(self):
        test_term = "Testing Term Unik 123"
        db_manager.add_vocabulary(test_term, category="technology", boost_score=3.0)
        vocab = db_manager.get_all_vocabulary()
        matching = [v for v in vocab if v["term"] == test_term]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["category"], "technology")
        self.assertEqual(matching[0]["boost_score"], 3.0)
        deleted = db_manager.delete_vocabulary(test_term)
        self.assertTrue(deleted)
        vocab_after = db_manager.get_all_vocabulary()
        self.assertFalse(any(v["term"] == test_term for v in vocab_after))

    def test_language_switch_purged_and_dedicated_en(self):
        resp = self.client.post("/api/control/language", json={"language": "id"})
        self.assertEqual(resp.status_code, 404)
        cfg = AppConfig()
        self.assertEqual(cfg.asr.active_language, "en")
        self.assertFalse(hasattr(cfg.asr, "model_path_id"))

    def test_api_vocabulary_endpoints(self):
        get_res = self.client.get("/api/vocabulary")
        self.assertEqual(get_res.status_code, 200)
        data = get_res.json()
        self.assertTrue(data.get("success"))
        terms = data.get("items", [])
        self.assertIsInstance(terms, list)
        self.assertGreaterEqual(len(terms), 59)
        new_term = "End-to-End Test Term 999"
        post_res = self.client.post("/api/vocabulary", json={"hotword": new_term, "category": "academic", "boost_score": 2.5})
        self.assertEqual(post_res.status_code, 200)
        pdata = post_res.json()
        self.assertTrue(pdata.get("success"))
        del_res = self.client.delete(f"/api/vocabulary/{new_term}")
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.json().get("success"))

    def test_zero_comments_in_codebase(self):
        files_to_check = [
            os.path.join("engine", "db.py"),
            os.path.join("engine", "seed_data.py"),
            os.path.join("engine", "config.py"),
            os.path.join("engine", "server.py"),
            os.path.join("web", "admin", "app.js"),
            os.path.join("web", "admin", "style.css"),
            os.path.join("web", "admin", "index.html"),
        ]
        for fpath in files_to_check:
            self.assertTrue(os.path.exists(fpath), f"File {fpath} does not exist")
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                stripped = line.strip()
                if fpath.endswith(".py"):
                    if stripped.startswith("#"):
                        self.fail(f"Comment found in {fpath}:{idx}: {line}")
                elif fpath.endswith(".html"):
                    if "<!--" in stripped or "-->" in stripped:
                        self.fail(f"HTML comment found in {fpath}:{idx}: {line}")
                else:
                    if "/*" in stripped or "*/" in stripped:
                        self.fail(f"Comment block found in {fpath}:{idx}: {line}")
                    if re.search(r"(?<!:)//", stripped):
                        self.fail(f"Single-line comment found in {fpath}:{idx}: {line}")

    def test_zero_pure_white_in_admin_ui(self):
        files_to_check = [
            os.path.join("web", "admin", "style.css"),
            os.path.join("web", "admin", "js", "app.js"),
        ]
        forbidden = [
            re.compile(r"#ffffff\b", re.IGNORECASE),
            re.compile(r"#fff\b", re.IGNORECASE),
            re.compile(r"rgb\s*\(\s*255\s*,\s*255\s*,\s*255\s*\)", re.IGNORECASE),
            re.compile(r"rgba\s*\(\s*255\s*,\s*255\s*,\s*255\s*,", re.IGNORECASE),
        ]
        for fpath in files_to_check:
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                for pattern in forbidden:
                    if pattern.search(line):
                        self.fail(f"Pure white detected in {fpath}:{idx}: {line}")

    def test_dark_clay_neumorphism_tokens(self):
        css_path = os.path.join("web", "admin", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("--canvas-bg:", content)
        self.assertIn("--surface-clay:", content)
        self.assertIn("box-shadow", content)
        self.assertIn("inset", content)

if __name__ == "__main__":
    unittest.main()
