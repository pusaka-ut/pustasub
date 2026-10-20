import os
import re
import json
import tempfile
import time
import threading
import urllib.request
import urllib.parse
from typing import Optional, Callable, Dict, List
from engine.db import DatabaseManager

class OfflineSentenceTranslator:
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        output_file: str = "output/current_translation.txt",
        on_translation: Optional[Callable[[str, str], None]] = None
    ):
        self.db_manager = db_manager
        self.output_file = os.path.abspath(output_file)
        self.on_translation = on_translation
        self.current_english_sentence = ""
        self.current_indonesian_sentence = ""
        self.cache: Dict[str, str] = {}
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        self._init_lexicon()
        self._load_db_vocabulary()

    def _load_db_vocabulary(self):
        if not self.db_manager:
            return
        try:
            vocab = self.db_manager.get_all_vocabulary()
            for v in vocab:
                term = v.get("term", "").strip()
                if term:
                    self.add_vocabulary_term(term, v.get("category", "academic"))
        except Exception:
            pass

    def add_vocabulary_term(self, term: str, category: str = "academic") -> None:
        clean = term.strip().lower()
        if not clean:
            return
        if " " in clean:
            self.phrase_dict[clean] = term.strip()
        else:
            self.word_dict[clean] = term.strip()

    def remove_vocabulary_term(self, term: str) -> None:
        clean = term.strip().lower()
        if clean in self.phrase_dict:
            del self.phrase_dict[clean]
        if clean in self.word_dict:
            del self.word_dict[clean]

    def _init_lexicon(self):
        self.phrase_dict = {
            "welcome to universitas terbuka": "selamat datang di universitas terbuka",
            "welcome to the international academic webinar": "selamat datang di webinar akademik internasional",
            "welcome to the webinar": "selamat datang di webinar",
            "good morning ladies and gentlemen": "selamat pagi bapak dan ibu sekalian",
            "good afternoon ladies and gentlemen": "selamat siang bapak dan ibu sekalian",
            "thank you very much for joining us": "terima kasih banyak telah bergabung bersama kami",
            "thank you very much": "terima kasih banyak",
            "thank you": "terima kasih",
            "rector of universitas terbuka": "rektor universitas terbuka",
            "distance higher education": "pendidikan tinggi jarak jauh",
            "distance learning system": "sistem pembelajaran jarak jauh",
            "distance learning": "pembelajaran jarak jauh",
            "open and distance learning": "pembelajaran terbuka dan jarak jauh",
            "independent learning curriculum": "kurikulum belajar mandiri",
            "independent learning": "belajar mandiri",
            "higher education in indonesia": "pendidikan tinggi di indonesia",
            "higher education institution": "institusi pendidikan tinggi",
            "higher education": "pendidikan tinggi",
            "academic senate of universitas terbuka": "senat akademik universitas terbuka",
            "academic senate": "senat akademik",
            "faculty of economics and business": "fakultas ekonomi dan bisnis",
            "faculty of law social and political sciences": "fakultas hukum ilmu sosial dan ilmu politik",
            "faculty of science and technology": "fakultas sains dan teknologi",
            "faculty of teacher training and education": "fakultas keguruan dan ilmu pendidikan",
            "digital library system": "sistem perpustakaan digital",
            "digital library": "perpustakaan digital",
            "online tutorial system": "sistem tutorial daring",
            "online tutorial": "tutorial online (tuton)",
            "final semester examination": "ujian akhir semester",
            "final examination": "ujian akhir semester",
            "graduation ceremony": "upacara wisuda",
            "course modules": "modul perkuliahan",
            "credit points": "satuan kredit semester",
            "study program": "program studi",
            "international conference": "konferensi internasional",
            "keynote speaker": "pembicara utama",
            "guest lecture": "kuliah umum",
            "honorary doctorate": "doktor kehormatan",
            "quality assurance system": "sistem penjaminan mutu",
            "quality assurance": "penjaminan mutu",
            "in this presentation": "dalam presentasi ini",
            "in this session": "pada sesi ini",
            "we are discussing": "kita sedang mendiskusikan",
            "as we know": "sebagaimana kita ketahui",
            "first of all": "pertama-tama",
            "furthermore": "selain itu",
            "on the other hand": "di sisi lain",
            "for example": "sebagai contoh",
            "in conclusion": "kesimpulannya",
            "to summarize": "untuk menyimpulkan",
            "have a nice day": "semoga hari anda menyenangkan"
        }

        self.word_dict = {
            "welcome": "selamat datang",
            "today": "hari ini",
            "we": "kita",
            "our": "kami",
            "will": "akan",
            "discuss": "mendiskusikan",
            "discussing": "membahas",
            "present": "mempresentasikan",
            "presentation": "presentasi",
            "webinar": "webinar",
            "seminar": "seminar",
            "conference": "konferensi",
            "university": "universitas",
            "academic": "akademik",
            "education": "pendidikan",
            "learning": "pembelajaran",
            "students": "mahasiswa",
            "student": "mahasiswa",
            "lecturer": "dosen",
            "lecturers": "para dosen",
            "professor": "profesor",
            "rector": "rektor",
            "dean": "dekan",
            "faculty": "fakultas",
            "program": "program",
            "course": "mata kuliah",
            "courses": "mata kuliah",
            "module": "modul",
            "modules": "modul-modul",
            "system": "sistem",
            "technology": "teknologi",
            "digital": "digital",
            "online": "daring",
            "offline": "luring",
            "library": "perpustakaan",
            "research": "penelitian",
            "development": "pengembangan",
            "service": "layanan",
            "quality": "mutu",
            "international": "internasional",
            "national": "nasional",
            "indonesia": "indonesia",
            "open": "terbuka",
            "distance": "jarak jauh",
            "innovation": "inovasi",
            "future": "masa depan",
            "transformation": "transformasi",
            "strategy": "strategi",
            "evaluation": "evaluasi",
            "assessment": "penilaian",
            "examination": "ujian",
            "certificate": "sertifikat",
            "degree": "gelar",
            "thank": "terima kasih",
            "thanks": "terima kasih",
            "good": "baik",
            "morning": "pagi",
            "afternoon": "siang",
            "evening": "sore",
            "night": "malam",
            "very": "sangat",
            "much": "banyak",
            "important": "penting",
            "challenge": "tantangan",
            "opportunity": "peluang",
            "growth": "pertumbuhan",
            "community": "komunitas",
            "society": "masyarakat",
            "leadership": "kepemimpinan",
            "management": "manajemen",
            "collaboration": "kolaborasi",
            "partnership": "kemitraan",
            "network": "jaringan",
            "pioneer": "pionir",
            "opening": "pembukaan",
            "delivered": "menyampaikan",
            "platform": "platform",
            "virtual": "virtual",
            "hybrid": "hibrida",
            "session": "sesi",
            "chapter": "bab",
            "topic": "topik",
            "issue": "isu",
            "problem": "masalah",
            "solution": "solusi",
            "result": "hasil",
            "results": "hasil-hasil",
            "achievement": "capaian",
            "success": "keberhasilan",
            "process": "proses",
            "activity": "kegiatan",
            "activities": "kegiatan-kegiatan",
            "participant": "peserta",
            "participants": "para peserta",
            "audience": "hadirin",
            "speech": "pidato",
            "address": "sambutan",
            "meeting": "pertemuan",
            "discussion": "diskusi",
            "perspective": "perspektif",
            "pedagogy": "pedagogi",
            "curriculum": "kurikulum",
            "material": "materi",
            "materials": "materi-materi",
            "resource": "sumber daya",
            "resources": "sumber daya",
            "access": "akses",
            "opportunity": "kesempatan",
            "equity": "keadilan",
            "inclusion": "inklusi",
            "implementation": "implementasi",
            "governance": "tata kelola",
            "accreditation": "akreditasi",
            "standard": "standar",
            "standards": "standar-standar"
        }

    def _neural_translate(self, sentence: str) -> Optional[str]:
        try:
            encoded = urllib.parse.quote(sentence.strip())
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=id&dt=t&q={encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    translated = "".join([part[0] for part in data[0] if part and len(part) > 0 and part[0]])
                    return translated.strip()
        except Exception:
            return None
        return None

    def _offline_lexicon_translate(self, clean: str) -> str:
        punctuation = ""
        if clean[-1] in ".?!":
            punctuation = clean[-1]
            clean = clean[:-1].strip()

        lower = clean.lower()

        for phrase, translation in sorted(self.phrase_dict.items(), key=lambda x: len(x[0]), reverse=True):
            if phrase in lower:
                lower = re.sub(r"\b" + re.escape(phrase) + r"\b", translation, lower)

        words = lower.split()
        translated_words = []
        skip_next = False

        for i in range(len(words)):
            if skip_next:
                skip_next = False
                continue

            w = words[i]
            clean_w = re.sub(r"[^\w\-]", "", w)

            if i + 1 < len(words):
                next_w = re.sub(r"[^\w\-]", "", words[i + 1])
                pair = clean_w + " " + next_w
                if pair in self.phrase_dict:
                    translated_words.append(self.phrase_dict[pair])
                    skip_next = True
                    continue

            if clean_w in self.word_dict:
                tw = self.word_dict[clean_w]
                translated_words.append(tw)
            else:
                translated_words.append(w)

        res = " ".join(translated_words)
        res = self._post_process_indonesian(res)
        if punctuation:
            res += punctuation

        return res

    def translate_sentence(self, sentence: str) -> str:
        clean = sentence.strip()
        if not clean:
            return ""

        lower_key = clean.lower()
        if lower_key in self.cache:
            return self.cache[lower_key]

        neural_result = self._neural_translate(clean)
        if neural_result:
            result = self._post_process_indonesian(neural_result)
            self.cache[lower_key] = result
            return result

        result = self._offline_lexicon_translate(clean)
        self.cache[lower_key] = result
        return result

    def _post_process_indonesian(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return ""

        text = text[0].upper() + text[1:]
        text = re.sub(r"\bUniversitas terbuka\b", "Universitas Terbuka", text, flags=re.IGNORECASE)
        text = re.sub(r"\bIndonesia\b", "Indonesia", text, flags=re.IGNORECASE)
        text = re.sub(r"\bTuton\b", "Tuton", text, flags=re.IGNORECASE)
        text = re.sub(r"\bUas\b", "UAS", text, flags=re.IGNORECASE)
        text = re.sub(r"\bSks\b", "SKS", text, flags=re.IGNORECASE)
        text = re.sub(r"\bLms\b", "LMS", text, flags=re.IGNORECASE)
        text = re.sub(r"\bPjj\b", "PJJ", text, flags=re.IGNORECASE)
        return text

    def process_final_transcript(self, raw_text: str) -> Optional[str]:
        cleaned = raw_text.strip()
        if not cleaned:
            return None

        translated = self.translate_sentence(cleaned)
        if not translated:
            return None

        self.current_english_sentence = cleaned
        self.current_indonesian_sentence = translated
        self._atomic_write_translation(translated)

        if self.on_translation:
            try:
                self.on_translation(cleaned, translated)
            except Exception:
                pass

        return translated

    def _atomic_write_translation(self, text: str) -> None:
        try:
            target_dir = os.path.dirname(self.output_file)
            with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
                tf.write(text.strip())
                temp_name = tf.name
            os.replace(temp_name, self.output_file)
        except Exception:
            try:
                with open(self.output_file, "w", encoding="utf-8") as f:
                    f.write(text.strip())
            except Exception:
                pass

    def clear_translation(self) -> None:
        self.current_english_sentence = ""
        self.current_indonesian_sentence = ""
        self._atomic_write_translation("")
