import re
from typing import List, Tuple

class BrokenEnglishGrammarRepair:
    def __init__(self):
        self.disfluency_pattern = re.compile(
            r"\b(uh+|um+|ah+|er+|you know|like like|i mean|anu|apa namanya|gitu ya|gitu)\b",
            re.IGNORECASE
        )
        self.duplicate_words_pattern = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)
        self.syntax_rules: List[Tuple[re.Pattern, str]] = self._compile_syntax_rules()

    def _compile_syntax_rules(self) -> List[Tuple[re.Pattern, str]]:
        raw_rules = [
            (r"\bwe are discuss\b", "we are discussing"),
            (r"\bwe are talk\b", "we are talking"),
            (r"\bwe must to\s+([a-zA-Z]+)\b", r"we must \1"),
            (r"\bis have\b", "has"),
            (r"\bare have\b", "have"),
            (r"\byesterday we discuss\b", "yesterday we discussed"),
            (r"\blast week I go\b", "last week I went"),
            (r"\bthank you for attend\b", "thank you for attending"),
            (r"\bwelcome to the our\b", "welcome to our"),
            (r"\bmore better\b", "better"),
            (r"\bmore easier\b", "easier"),
            (r"\bvery much people\b", "many people"),
            (r"\ba lots of\b", "a lot of"),
            (r"\bdepend of\b", "depend on"),
            (r"\bcongratulation for\b", "congratulations on"),
            (r"\bdiscuss about\b", "discuss")
        ]
        compiled = []
        for pat, repl in raw_rules:
            compiled.append((re.compile(pat, re.IGNORECASE), repl))
        return compiled

    def clean_disfluencies(self, text: str) -> str:
        if not text:
            return ""
        cleaned = self.disfluency_pattern.sub("", text)
        cleaned = self.duplicate_words_pattern.sub(r"\1", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def repair_syntax(self, text: str) -> str:
        if not text:
            return ""
        result = text
        for pattern, replacement in self.syntax_rules:
            result = pattern.sub(replacement, result)
        result = re.sub(r"\s+", " ", result).strip()
        return result

    def process(self, text: str, enabled: bool = True) -> str:
        if not text or not enabled:
            return text or ""
        without_disfluencies = self.clean_disfluencies(text)
        repaired = self.repair_syntax(without_disfluencies)
        return repaired
