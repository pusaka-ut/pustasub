import re
from typing import Dict, List, Tuple

class PhoneticNormalizer:
    def __init__(self, hotwords: List[str] = None):
        self.exact_map: Dict[str, str] = {
            "unipersiti terbuka": "Universitas Terbuka",
            "unipersitas terbuka": "Universitas Terbuka",
            "university terbuka": "Universitas Terbuka",
            "universitas terbuka": "Universitas Terbuka",
            "unipersiti": "University",
            "unipersitas": "Universitas",
            "aktip": "active",
            "efektip": "effective",
            "inopasi": "innovation",
            "inopatif": "innovative",
            "propesor": "Professor",
            "profesor": "Professor",
            "rektour": "Rector",
            "rek tor": "Rector",
            "tank you": "thank you",
            "tengkiu": "thank you",
            "tingk": "think",
            "tingking": "thinking",
            "dis is": "this is",
            "dat is": "that is",
            "fakulti": "Faculty",
            "fakultas": "Faculty",
            "pedagogi": "pedagogy",
            "pedagogik": "pedagogical",
            "kurikulum": "curriculum",
            "silabus": "syllabus",
            "jarak jauh": "distance learning",
            "pjj": "distance learning",
            "ojat darojat": "Ojat Darojat",
            "elearning": "e-learning",
            "diskas": "discuss",
            "debelop": "develop",
            "partisipan": "participants",
            "sertifikat": "certificate",
            "metodolodi": "methodology"
        }
        self.hotwords: List[str] = hotwords or []
        self._compiled_patterns: List[Tuple[re.Pattern, str]] = self._compile_rules()

    def _compile_rules(self) -> List[Tuple[re.Pattern, str]]:
        patterns = []
        sorted_keys = sorted(self.exact_map.keys(), key=len, reverse=True)
        for key in sorted_keys:
            replacement = self.exact_map[key]
            pattern = re.compile(rf"\b{re.escape(key)}\b", re.IGNORECASE)
            patterns.append((pattern, replacement))
        return patterns

    def add_custom_mapping(self, source: str, target: str) -> None:
        clean_src = source.strip().lower()
        clean_tgt = target.strip()
        if clean_src and clean_tgt:
            self.exact_map[clean_src] = clean_tgt
            self._compiled_patterns = self._compile_rules()

    def normalize(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        result = text
        for pattern, replacement in self._compiled_patterns:
            result = pattern.sub(replacement, result)

        for hotword in self.hotwords:
            if not hotword.strip():
                continue
            hw_clean = hotword.strip()
            hw_pattern = re.compile(rf"\b{re.escape(hw_clean)}\b", re.IGNORECASE)
            result = hw_pattern.sub(hw_clean, result)

        return result
