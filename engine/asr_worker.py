import os
import queue
import threading
import time
from typing import Optional, Callable
import numpy as np
import sherpa_onnx
from engine.config import ASRConfig
from engine.model_loader import download_and_extract_model, is_model_complete, get_model_paths

class ASRWorker:
    def __init__(
        self,
        audio_queue: queue.Queue,
        config: Optional[ASRConfig] = None,
        on_partial: Optional[Callable[[str], None]] = None,
        on_final: Optional[Callable[[str], None]] = None
    ):
        self.audio_queue = audio_queue
        self.config = config or ASRConfig()
        self.on_partial = on_partial
        self.on_final = on_final
        self.recognizer: Optional[sherpa_onnx.OnlineRecognizer] = None
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.last_emitted_text = ""

    def initialize(self) -> bool:
        with self.lock:
            model_dir = self.config.model_path_en
            if not is_model_complete(model_dir):
                try:
                    paths = download_and_extract_model(models_root="models")
                except Exception:
                    return False
            else:
                paths = get_model_paths(model_dir)

            hotwords_path = ""
            if self.config.hotwords_file and os.path.exists(self.config.hotwords_file):
                hotwords_path = self.config.hotwords_file

            try:
                decoding_method = getattr(self.config, "decoding_method", "modified_beam_search")
                max_active_paths = getattr(self.config, "max_active_paths", 4)
                self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                    encoder=paths["encoder"],
                    decoder=paths["decoder"],
                    joiner=paths["joiner"],
                    tokens=paths["tokens"],
                    num_threads=self.config.num_threads,
                    sample_rate=16000,
                    feature_dim=80,
                    enable_endpoint_detection=True,
                    rule1_min_trailing_silence=2.4,
                    rule2_min_trailing_silence=1.2,
                    decoding_method=decoding_method,
                    max_active_paths=max_active_paths,
                    hotwords_file=hotwords_path,
                    hotwords_score=self.config.hotwords_score
                )
                return True
            except Exception:
                return False

    def start(self) -> bool:
        if self.is_running:
            return True
        if self.recognizer is None:
            success = self.initialize()
            if not success:
                return False
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        return True

    def stop(self) -> None:
        self.is_running = False
        if self.worker_thread is not None:
            self.worker_thread.join(timeout=2.0)
            self.worker_thread = None

    def _worker_loop(self) -> None:
        if self.recognizer is None:
            return
        stream = self.recognizer.create_stream()
        while self.is_running:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if not isinstance(chunk, np.ndarray) or len(chunk) == 0:
                continue

            stream.accept_waveform(16000, chunk)

            while self.recognizer.is_ready(stream):
                self.recognizer.decode_stream(stream)

            result_obj = self.recognizer.get_result(stream)
            current_text = result_obj.strip() if isinstance(result_obj, str) else getattr(result_obj, "text", "").strip()
            if current_text and current_text != self.last_emitted_text:
                self.last_emitted_text = current_text
                if self.on_partial is not None:
                    try:
                        self.on_partial(current_text)
                    except Exception:
                        pass

            if self.recognizer.is_endpoint(stream):
                final_text = current_text
                if final_text and self.on_final is not None:
                    try:
                        self.on_final(final_text)
                    except Exception:
                        pass
                self.recognizer.reset(stream)
                self.last_emitted_text = ""

    def switch_language(self, language_code: str) -> bool:
        with self.lock:
            if language_code == self.config.active_language:
                return True
            target_model_dir = self.config.model_path_id if language_code == "id" else self.config.model_path_en
            if not is_model_complete(target_model_dir):
                return False
            paths = get_model_paths(target_model_dir)
            try:
                new_recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                    encoder=paths["encoder"],
                    decoder=paths["decoder"],
                    joiner=paths["joiner"],
                    tokens=paths["tokens"],
                    num_threads=self.config.num_threads,
                    sample_rate=16000,
                    feature_dim=80,
                    enable_endpoint_detection=True
                )
                self.recognizer = new_recognizer
                self.config.active_language = language_code
                self.last_emitted_text = ""
                return True
            except Exception:
                return False
