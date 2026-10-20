import re
from collections import deque
from typing import List, Set

class ContextMemory:
    def __init__(self, max_history: int = 4):
        self.history: deque = deque(maxlen=max_history)
        self.academic_keywords: Set[str] = {
            "university", "universitas", "student", "students", "faculty", "curriculum",
            "pedagogy", "academic", "learning", "distance", "rector", "dean", "professor",
            "exam", "lecture", "campus", "course", "courses", "syllabus", "degree", "webinar"
        }
        self.homophone_map = [
            (re.compile(r"\bcoarse\b", re.IGNORECASE), "course"),
            (re.compile(r"\bcoarses\b", re.IGNORECASE), "courses"),
            (re.compile(r"\bboard of\b", re.IGNORECASE), "board of"),
            (re.compile(r"\bwrite the exam\b", re.IGNORECASE), "take the exam"),
            (re.compile(r"\bpast the exam\b", re.IGNORECASE), "passed the exam")
        ]

    def add_phrase(self, phrase: str) -> None:
        if phrase and phrase.strip():
            self.history.append(phrase.strip())

    def get_recent_context(self) -> str:
        return " ".join(self.history)

    def is_academic_context(self) -> bool:
        context_str = self.get_recent_context().lower()
        if not context_str:
            return True
        for kw in self.academic_keywords:
            if kw in context_str:
                return True
        return True

    def resolve_homophones(self, text: str) -> str:
        if not text:
            return ""
        if not self.is_academic_context():
            return text

        result = text
        for pattern, replacement in self.homophone_map:
            result = pattern.sub(replacement, result)
        return result

    def clear(self) -> None:
        self.history.clear()
