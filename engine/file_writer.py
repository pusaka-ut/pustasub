import os
import tempfile

class AtomicFileWriter:
    def __init__(self, output_path: str = "output/current_subtitle.txt"):
        self.output_path = os.path.abspath(output_path)
        self.dir_name = os.path.dirname(self.output_path)
        os.makedirs(self.dir_name, exist_ok=True)

    def write_subtitle(self, text: str) -> bool:
        try:
            fd, temp_path = tempfile.mkstemp(dir=self.dir_name, prefix="sub_", suffix=".tmp", text=True)
            with open(fd, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(temp_path, self.output_path)
            return True
        except Exception:
            return False

    def clear_subtitle(self) -> bool:
        return self.write_subtitle("")
