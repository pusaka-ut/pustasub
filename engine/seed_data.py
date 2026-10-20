from typing import List, Tuple, Dict, Any
from engine.db import DatabaseManager
from engine.config import get_default_presets

UT_VOCABULARY_CORPUS: List[Tuple[str, str, str, float]] = [
    ("Prof. Dr. Ojat Darojat, M.Bus., Ph.D.", "leadership", "profesor ojat darojat", 3.0),
    ("Prof. Dr. Paken Pandiangan, S.Si., M.Si.", "leadership", "profesor paken pandiangan", 3.0),
    ("Dr. Mohamad Yunus, S.S., M.A.", "leadership", "doktor mohamad yunus", 3.0),
    ("Prof. Dr. Ali Muktiyanto, S.E., M.Si.", "leadership", "profesor ali muktiyanto", 3.0),
    ("Rahmat Budiman, M.Hum., Ph.D.", "leadership", "rahmat budiman", 3.0),
    ("Rector of Universitas Terbuka", "leadership", "rektor universitas terbuka", 2.8),
    ("Vice Rector", "leadership", "wakil rektor", 2.8),
    ("Dean of Faculty", "leadership", "dekan fakultas", 2.8),
    ("Vice Dean", "leadership", "wakil dekan", 2.5),
    ("Head of Study Program", "leadership", "ketua program studi", 2.5),
    ("Chief Librarian", "leadership", "kepala perpustakaan", 2.5),
    ("Academic Senate", "leadership", "senat akademik", 2.8),
    ("University Council", "leadership", "dewan universitas", 2.5),
    ("Faculty of Economics and Business", "faculties", "fakultas ekonomi dan bisnis", 2.8),
    ("Faculty of Law, Social, and Political Sciences", "faculties", "fakultas hukum ilmu sosial dan ilmu politik", 2.8),
    ("Faculty of Science and Technology", "faculties", "fakultas sains dan teknologi", 2.8),
    ("Faculty of Teacher Training and Education", "faculties", "fakultas keguruan dan ilmu pendidikan", 2.8),
    ("Postgraduate School", "faculties", "sekolah pascasarjana", 2.8),
    ("Universitas Terbuka", "academic", "unipersiti terbuka", 3.0),
    ("Open University", "academic", "universitas terbuka", 3.0),
    ("Distance Learning", "academic", "pembelajaran jarak jauh", 3.0),
    ("Higher Education", "academic", "pendidikan tinggi", 2.8),
    ("Online Tutorial", "academic", "tutorial online tuton", 2.8),
    ("Independent Learning", "academic", "belajar mandiri", 2.8),
    ("Learning Materials", "academic", "bahan ajar modul", 2.8),
    ("Course Modules", "academic", "modul perkuliahan", 2.8),
    ("Credit Points", "academic", "satuan kredit semester sks", 2.8),
    ("Semester Credit System", "academic", "sistem kredit semester sks", 2.8),
    ("Final Examination", "academic", "ujian akhir semester uas", 2.8),
    ("Take-Home Exam", "academic", "ujian take home exam the", 2.8),
    ("Online Proctoring", "academic", "pengawasan ujian online", 2.8),
    ("Digital Library", "academic", "perpustakaan digital pustaloka", 2.8),
    ("Academic Transcript", "academic", "transkrip nilai akademik", 2.8),
    ("Study Program", "academic", "program studi prodi", 2.8),
    ("Academic Year", "academic", "tahun akademik", 2.5),
    ("Student Registration", "academic", "registrasi mahasiswa", 2.5),
    ("Matriculation", "academic", "matrikulasi", 2.5),
    ("Convocation", "academic", "upacara penyerahan ijazah upbjj", 2.8),
    ("Graduation Ceremony", "academic", "upacara wisuda kelulusan", 2.8),
    ("Valedictorian", "academic", "lulusan terbaik", 2.5),
    ("Honorary Doctorate", "academic", "doktor kehormatan honoris causa", 2.5),
    ("National Accreditation", "academic", "akreditasi nasional ban pt", 2.8),
    ("International Accreditation", "academic", "akreditasi internasional", 2.8),
    ("International Webinar", "conference", "webinar seminar internasional", 2.8),
    ("Keynote Speaker", "conference", "pembicara utama", 2.8),
    ("Plenary Session", "conference", "sesi pleno", 2.5),
    ("Colloquium", "conference", "kolokium akademik", 2.5),
    ("Symposium", "conference", "simposium ilmiah", 2.5),
    ("Call for Papers", "conference", "panggilan artikel ilmiah", 2.5),
    ("Peer-Reviewed Journal", "academic", "jurnal ilmiah terindeks", 2.5),
    ("Lifelong Learning", "academic", "pendidikan sepanjang hayat", 2.8),
    ("Learning Management System", "technology", "lms elearning moodle", 2.8),
    ("Blended Learning", "technology", "pembelajaran campuran", 2.8),
    ("Instructional Design", "pedagogy", "desain instruksional", 2.5),
    ("Virtual Classroom", "technology", "kelas virtual teleconference", 2.5),
    ("Broadcast Subtitle", "technology", "teks subtitle siaran", 2.5),
    ("OBS Studio", "technology", "obs studio browser source", 2.8),
    ("vMix", "technology", "vmix live video switcher", 2.8),
    ("Audio Loopback", "technology", "wasapi loopback audio", 2.8)
]

def seed_database(db: DatabaseManager) -> None:
    current_vocab = db.get_all_vocabulary()
    if len(current_vocab) < 10:
        for term, cat, hint, score in UT_VOCABULARY_CORPUS:
            db.add_vocabulary(term, category=cat, phonetic_hint=hint, boost_score=score)

    existing_presets = db.get_all_presets()
    if not existing_presets:
        defaults = get_default_presets()
        for pid, cfg in defaults.items():
            name = cfg.get("name", pid)
            is_def = 1 if pid == "academic_formal" else 0
            is_act = 1 if pid == "academic_formal" else 0
            db.save_preset(pid, name, cfg, is_default=is_def, is_active=is_act)

    spk = db.get_active_speaker()
    if not spk.get("name"):
        db.set_active_speaker(
            name="Prof. Dr. Ojat Darojat, M.Bus., Ph.D.",
            title="Rector of Universitas Terbuka",
            enabled=False
        )

if __name__ == "__main__":
    db_mgr = DatabaseManager()
    seed_database(db_mgr)
    print("DATABASE SEEDED SUCCESSFULLY. VOCAB COUNT:", len(db_mgr.get_all_vocabulary()))
