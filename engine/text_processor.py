import os
import re
from typing import Dict, List, Optional
from engine.phonetic_normalizer import PhoneticNormalizer
from engine.grammar_repair import BrokenEnglishGrammarRepair
from engine.context_memory import ContextMemory

class TextProcessor:
    def __init__(
        self,
        hotwords_file: Optional[str] = "config/hotwords.txt",
        max_chars_per_line: int = 37,
        max_lines: int = 2
    ):
        self.hotwords_map: Dict[str, str] = {}
        self.max_chars_per_line = max_chars_per_line
        self.max_lines = max_lines
        self.smart_repair_enabled = True
        self.question_words = {"what", "why", "how", "where", "when", "who", "which", "is", "are", "can", "could", "would", "do", "does", "did"}

        if hotwords_file and os.path.exists(hotwords_file):
            self.load_hotwords(hotwords_file)

        self.phonetic_normalizer = PhoneticNormalizer(hotwords=list(self.hotwords_map.values()))
        self.grammar_repair = BrokenEnglishGrammarRepair()
        self.context_memory = ContextMemory()
        self.academic_glossary = {
            "distance learning": "Pembelajaran Jarak Jauh (PJJ)",
            "independent learning": "Belajar Mandiri",
            "online tutorial": "Tutorial Online (Tuton)",
            "open university": "Universitas Terbuka (UT)",
            "academic record": "Transkrip Nilai Akademik",
            "study program": "Program Studi (Prodi)",
            "credit points": "Satuan Kredit Semester (SKS)",
            "examination": "Ujian Akhir Semester (UAS)",
            "learning materials": "Bahan Ajar / Modul UT",
            "course material": "Materi Perkuliahan",
            "curriculum": "Kurikulum Akademik",
            "registration": "Registrasi Mata Kuliah",
            "semester": "Semester Perkuliahan",
            "student": "Mahasiswa",
            "students": "Mahasiswa",
            "professor": "Profesor / Guru Besar",
            "lecture": "Perkuliahan",
            "lecturer": "Dosen Pengampu",
            "faculty": "Fakultas",
            "rector": "Rektor",
            "vice rector": "Wakil Rektor",
            "webinar": "Seminar Daring",
            "research": "Penelitian Ilmiah",
            "higher education": "Pendidikan Tinggi",
            "digital library": "Perpustakaan Digital",
            "admission": "Penerimaan Mahasiswa Baru",
            "graduation": "Wisuda Kelulusan",
            "diploma": "Ijazah",
            "academic year": "Tahun Akademik"
        }

    def load_hotwords(self, hotwords_file: str) -> None:
        if not os.path.isfile(hotwords_file):
            return
        with open(hotwords_file, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    self.hotwords_map[word.lower()] = word

    def add_hotword(self, word: str) -> None:
        trimmed = word.strip()
        if trimmed:
            self.hotwords_map[trimmed.lower()] = trimmed
            if hasattr(self, "phonetic_normalizer"):
                self.phonetic_normalizer.hotwords = list(self.hotwords_map.values())

    def remove_hotword(self, word: str) -> None:
        key = word.strip().lower()
        if key in self.hotwords_map:
            del self.hotwords_map[key]
            if hasattr(self, "phonetic_normalizer"):
                self.phonetic_normalizer.hotwords = list(self.hotwords_map.values())

    def set_smart_repair(self, enabled: bool) -> None:
        self.smart_repair_enabled = enabled

    def format_text(self, raw_text: str, is_final: bool = False) -> str:
        if not raw_text:
            return ""
        cleaned = re.sub(r"\s+", " ", raw_text).strip()
        if not cleaned:
            return ""

        result = cleaned
        if self.smart_repair_enabled:
            result = self.phonetic_normalizer.normalize(result)
            result = self.context_memory.resolve_homophones(result)
            result = self.grammar_repair.process(result, enabled=True)
            if is_final:
                self.context_memory.add_phrase(result)

        sorted_hotwords = sorted(self.hotwords_map.values(), key=len, reverse=True)
        for hw in sorted_hotwords:
            pattern = re.compile(rf"\b{re.escape(hw)}\b", re.IGNORECASE)
            result = pattern.sub(hw, result)

        if result:
            result = result[0].upper() + result[1:]

        if is_final:
            first_word_lower = cleaned.split(" ")[0].lower()
            if not result.endswith((".", "?", "!")):
                if first_word_lower in self.question_words:
                    result += "?"
                else:
                    result += "."

        return result

    def wrap_lines(self, text: str) -> str:
        if not text:
            return ""
        words = text.split(" ")
        lines: List[str] = []
        current_line: List[str] = []
        current_len = 0

        for word in words:
            word_len = len(word)
            addition = word_len if current_len == 0 else word_len + 1
            if current_len + addition <= self.max_chars_per_line:
                current_line.append(word)
                current_len += addition
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_len = word_len

        if current_line:
            lines.append(" ".join(current_line))

        if len(lines) > self.max_lines:
            lines = lines[-self.max_lines:]

        return "\n".join(lines)

    def apply_pacing(self, text: str, mode: str = "paced_chunk", is_final: bool = False) -> str:
        formatted = self.format_text(text, is_final=is_final)
        if not formatted:
            return ""
        return self.wrap_lines(formatted)

    def get_glossary_tag(self, text: str) -> str:
        if not text:
            return ""
        lowered = text.lower()
        sorted_terms = sorted(self.academic_glossary.keys(), key=len, reverse=True)
        for term in sorted_terms:
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            if pattern.search(lowered):
                return self.academic_glossary[term]
        return ""

    def format_bilingual(self, text: str, is_final: bool = False) -> Dict[str, str]:
        formatted = self.format_text(text, is_final=is_final)
        tag = self.get_glossary_tag(formatted)
        return {
            "primary": self.wrap_lines(formatted),
            "glossary": tag
        }
