import os
import time
from datetime import datetime
from typing import Optional

class SessionLogger:
    def __init__(self, sessions_dir: str = "output/sessions"):
        self.sessions_dir = os.path.abspath(sessions_dir)
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.session_id: Optional[str] = None
        self.srt_path: Optional[str] = None
        self.txt_path: Optional[str] = None
        self.entry_index = 1
        self.session_start_time = 0.0

    def start_session(self) -> str:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp_str}"
        self.srt_path = os.path.join(self.sessions_dir, f"{self.session_id}.srt")
        self.txt_path = os.path.join(self.sessions_dir, f"{self.session_id}.txt")
        self.entry_index = 1
        self.session_start_time = time.time()
        with open(self.srt_path, "w", encoding="utf-8") as f:
            pass
        with open(self.txt_path, "w", encoding="utf-8") as f:
            f.write(f"PUSTASUB Session Transcript - {timestamp_str}\n")
            f.write("=" * 60 + "\n\n")
        return self.session_id

    def log_phrase(self, text: str, rel_start_sec: float, rel_end_sec: float) -> None:
        if not self.srt_path or not self.txt_path or not text.strip():
            return

        clean_text = text.strip()
        start_srt = self.format_srt_time(rel_start_sec)
        end_srt = self.format_srt_time(max(rel_end_sec, rel_start_sec + 0.5))

        srt_block = f"{self.entry_index}\n{start_srt} --> {end_srt}\n{clean_text}\n\n"
        with open(self.srt_path, "a", encoding="utf-8") as f:
            f.write(srt_block)

        txt_line = f"[{self.format_txt_time(rel_start_sec)}] {clean_text}\n"
        with open(self.txt_path, "a", encoding="utf-8") as f:
            f.write(txt_line)

        self.entry_index += 1

    @staticmethod
    def format_srt_time(seconds: float) -> str:
        total_millis = int(max(0.0, seconds) * 1000)
        hours = total_millis // 3600000
        remainder = total_millis % 3600000
        minutes = remainder // 60000
        remainder = remainder % 60000
        secs = remainder // 1000
        millis = remainder % 1000
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def format_txt_time(seconds: float) -> str:
        total_seconds = int(max(0.0, seconds))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
