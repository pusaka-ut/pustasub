import os
import sys
import queue
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.phonetic_normalizer import PhoneticNormalizer
from engine.grammar_repair import BrokenEnglishGrammarRepair
from engine.context_memory import ContextMemory
from engine.text_processor import TextProcessor
from engine.asr_worker import ASRWorker
from engine.config import ASRConfig

def test_phonetic_normalizer():
    pn = PhoneticNormalizer(hotwords=["Universitas Terbuka", "Ojat Darojat"])
    
    assert pn.normalize("unipersiti terbuka") == "Universitas Terbuka"
    assert pn.normalize("propesor ojat darojat") == "Professor Ojat Darojat"
    assert pn.normalize("rek tor") == "Rector"
    assert pn.normalize("inopasi aktip") == "innovation active"
    assert pn.normalize("jarak jauh") == "distance learning"
    assert pn.normalize("tank you propesor") == "thank you Professor"

def test_broken_english_grammar_repair():
    gr = BrokenEnglishGrammarRepair()
    
    raw = "um uh you know we are discuss about the curriculum and anu we must to debelop"
    cleaned = gr.clean_disfluencies(raw)
    words = cleaned.split()
    assert "um" not in words
    assert "uh" not in words
    assert "you know" not in cleaned
    assert "anu" not in words
    
    repaired = gr.process(raw, enabled=True)
    assert "we are discussing" in repaired
    assert "we must debelop" in repaired

def test_contextual_memory():
    cm = ContextMemory()
    cm.add_phrase("Welcome to Universitas Terbuka academic webinar.")
    cm.add_phrase("Today we present the new curriculum.")
    
    assert cm.is_academic_context() is True
    assert cm.resolve_homophones("this coarse is great") == "this course is great"
    assert cm.resolve_homophones("past the exam") == "passed the exam"

def test_integrated_pipeline():
    tp = TextProcessor()
    
    raw = "um uh unipersiti terbuka is have many student and we must to debelop inopasi"
    result = tp.apply_pacing(raw, mode="paced_chunk", is_final=True)
    
    assert "Universitas Terbuka" in result
    assert "has many student" in result
    assert "we must develop" in result
    assert "innovation." in result
    res_words = result.lower().split()
    assert "um" not in res_words
    assert "uh" not in res_words

def test_asr_worker_beam_search():
    audio_q = queue.Queue()
    cfg = ASRConfig(decoding_method="modified_beam_search", max_active_paths=4)
    worker = ASRWorker(audio_queue=audio_q, config=cfg)
    
    init_ok = worker.initialize()
    assert init_ok is True
    assert worker.recognizer is not None
    
    silent_chunk = np.zeros(1600, dtype=np.float32)
    audio_q.put(silent_chunk)
    
    started = worker.start()
    assert started is True
    
    worker.stop()
    assert worker.is_running is False

if __name__ == "__main__":
    test_phonetic_normalizer()
    test_broken_english_grammar_repair()
    test_contextual_memory()
    test_integrated_pipeline()
    test_asr_worker_beam_search()
    print("ALL MILESTONE 6 SMART ASR & BROKEN ENGLISH TESTS PASSED")
