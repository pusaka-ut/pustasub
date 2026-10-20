import os
import sqlite3
import json
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "pustasub.db"))

class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT UNIQUE NOT NULL,
                category TEXT DEFAULT 'academic',
                phonetic_hint TEXT,
                boost_score REAL DEFAULT 2.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS speaker_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS presets (
                preset_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                config_json TEXT NOT NULL,
                is_default INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL,
                raw_text TEXT NOT NULL,
                formatted_text TEXT NOT NULL,
                glossary_tag TEXT,
                speaker_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vocab_term ON vocabulary(term);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_hist ON session_history(session_id);")
            conn.commit()

    def get_all_vocabulary(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, term, category, phonetic_hint, boost_score FROM vocabulary ORDER BY term ASC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def add_vocabulary(self, term: str, category: str = "academic", phonetic_hint: str = "", boost_score: float = 2.5) -> bool:
        clean_term = term.strip()
        if not clean_term:
            return False
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO vocabulary (term, category, phonetic_hint, boost_score)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(term) DO UPDATE SET
                category=excluded.category,
                phonetic_hint=excluded.phonetic_hint,
                boost_score=excluded.boost_score;
            """, (clean_term, category, phonetic_hint, boost_score))
            conn.commit()
            return True

    def remove_vocabulary(self, identifier: Any) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            id_str = str(identifier).strip()
            if id_str.isdigit():
                cursor.execute("DELETE FROM vocabulary WHERE id = ? OR term = ?;", (int(id_str), id_str))
            else:
                cursor.execute("DELETE FROM vocabulary WHERE term = ?;", (id_str,))
            conn.commit()
            return cursor.rowcount > 0

    def get_term_by_id_or_term(self, identifier: Any) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            id_str = str(identifier).strip()
            if id_str.isdigit():
                cursor.execute("SELECT term FROM vocabulary WHERE id = ? OR term = ?;", (int(id_str), id_str))
            else:
                cursor.execute("SELECT term FROM vocabulary WHERE term = ?;", (id_str,))
            row = cursor.fetchone()
            return row["term"] if row else None

    def delete_vocabulary(self, identifier: Any) -> bool:
        return self.remove_vocabulary(identifier)

    def get_all_presets(self) -> Dict[str, Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT preset_id, name, config_json, is_default, is_active FROM presets;")
            rows = cursor.fetchall()
            result = {}
            for r in rows:
                try:
                    cfg = json.loads(r["config_json"])
                    cfg["name"] = r["name"]
                    result[r["preset_id"]] = cfg
                except Exception:
                    pass
            return result

    def save_preset(self, preset_id: str, name: str, config_dict: Dict[str, Any], is_default: int = 0, is_active: int = 0) -> None:
        cfg_str = json.dumps(config_dict, ensure_ascii=False)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO presets (preset_id, name, config_json, is_default, is_active, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(preset_id) DO UPDATE SET
                name=excluded.name,
                config_json=excluded.config_json,
                is_default=excluded.is_default,
                is_active=excluded.is_active,
                updated_at=CURRENT_TIMESTAMP;
            """, (preset_id, name, cfg_str, is_default, is_active))
            conn.commit()

    def get_active_preset_id(self) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT preset_id FROM presets WHERE is_active = 1 LIMIT 1;")
            row = cursor.fetchone()
            if row:
                return row["preset_id"]
            return "academic_formal"

    def set_active_preset(self, preset_id: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE presets SET is_active = 0;")
            cursor.execute("UPDATE presets SET is_active = 1 WHERE preset_id = ?;", (preset_id,))
            conn.commit()

    def get_active_speaker(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, title, is_active FROM speaker_profiles WHERE is_active = 1 ORDER BY id DESC LIMIT 1;")
            row = cursor.fetchone()
            if row:
                return {"name": row["name"], "title": row["title"], "enabled": bool(row["is_active"])}
            return {"name": "", "title": "", "enabled": False}

    def set_active_speaker(self, name: str, title: str, enabled: bool) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE speaker_profiles SET is_active = 0;")
            cursor.execute("""
            INSERT INTO speaker_profiles (name, title, is_active)
            VALUES (?, ?, ?);
            """, (name.strip(), title.strip(), 1 if enabled else 0))
            conn.commit()

    def log_subtitle(self, session_id: str, start_time: float, end_time: float, raw_text: str, formatted_text: str, glossary_tag: str = "", speaker_name: str = "") -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO session_history (session_id, start_time, end_time, raw_text, formatted_text, glossary_tag, speaker_name)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (session_id, start_time, end_time, raw_text, formatted_text, glossary_tag, speaker_name))
            conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_settings WHERE key = ?;", (key,))
            row = cursor.fetchone()
            if row:
                return row["value"]
            return default

    def set_setting(self, key: str, value: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO system_settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP;
            """, (key, value))
            conn.commit()
