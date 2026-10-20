import os
import sys
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist", "PUSTASUB")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")

def test_distribution_directory_structure():
    assert os.path.exists(DIST_DIR), "Distribution directory dist/PUSTASUB does not exist!"
    
    required_dirs = [
        os.path.join(DIST_DIR, "engine"),
        os.path.join(DIST_DIR, "web", "admin"),
        os.path.join(DIST_DIR, "web", "overlay"),
        os.path.join(DIST_DIR, "models"),
        os.path.join(DIST_DIR, "output", "sessions")
    ]
    for d in required_dirs:
        assert os.path.exists(d), f"Required directory missing in distribution: {d}"

def test_distribution_critical_files():
    required_files = [
        os.path.join(DIST_DIR, "run.bat"),
        os.path.join(DIST_DIR, "PUSTASUB.vbs"),
        os.path.join(DIST_DIR, "config.json"),
        os.path.join(DIST_DIR, "requirements.txt"),
        os.path.join(DIST_DIR, "output", "current_subtitle.txt"),
        os.path.join(DIST_DIR, "engine", "server.py"),
        os.path.join(DIST_DIR, "engine", "asr_worker.py"),
        os.path.join(DIST_DIR, "engine", "audio_capture.py"),
        os.path.join(DIST_DIR, "engine", "config.py"),
        os.path.join(DIST_DIR, "engine", "file_writer.py"),
        os.path.join(DIST_DIR, "engine", "model_loader.py"),
        os.path.join(DIST_DIR, "engine", "session_logger.py"),
        os.path.join(DIST_DIR, "engine", "text_processor.py"),
        os.path.join(DIST_DIR, "web", "admin", "index.html"),
        os.path.join(DIST_DIR, "web", "admin", "style.css"),
        os.path.join(DIST_DIR, "web", "admin", "app.js"),
        os.path.join(DIST_DIR, "web", "overlay", "index.html"),
        os.path.join(DIST_DIR, "web", "overlay", "style.css"),
        os.path.join(DIST_DIR, "web", "overlay", "overlay.js")
    ]
    for f in required_files:
        assert os.path.exists(f), f"Required file missing in distribution: {f}"
        assert os.path.getsize(f) >= 0, f"File is invalid: {f}"

def test_models_bundling():
    model_dir = os.path.join(DIST_DIR, "models", "sherpa-onnx-streaming-zipformer-en-20M-2023-02-17")
    assert os.path.exists(model_dir), "Pre-trained ASR model directory missing in distribution!"
    
    model_files = [
        os.path.join(model_dir, "tokens.txt"),
        os.path.join(model_dir, "encoder-epoch-99-avg-1.onnx"),
        os.path.join(model_dir, "decoder-epoch-99-avg-1.onnx"),
        os.path.join(model_dir, "joiner-epoch-99-avg-1.onnx")
    ]
    for mf in model_files:
        assert os.path.exists(mf), f"Model binary missing: {mf}"
        assert os.path.getsize(mf) > 1000, f"Model binary too small: {mf}"

def test_inno_setup_script():
    iss_path = os.path.join(BUILD_DIR, "setup_script.iss")
    assert os.path.exists(iss_path), "Inno Setup script missing!"
    
    with open(iss_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "AppName=PUSTASUB" in content
    assert "AppVersion=1.1.0" in content
    assert "AppPublisher=Universitas Terbuka" in content
    assert "OutputBaseFilename=PUSTASUB-v1.1.0-Setup" in content
    assert "PUSTASUB.vbs" in content
    assert "run.bat" in content

def test_zero_comments_across_distribution():
    python_files = []
    for root, _, files in os.walk(DIST_DIR):
        for file in files:
            if file.endswith((".py", ".js", ".html", ".css", ".bat", ".vbs")):
                python_files.append(os.path.join(root, file))
                
    for fpath in python_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, 1):
                s = line.strip()
                if s.startswith("#") or s.startswith("//") or s.startswith("/*") or s.startswith("REM ") or s.startswith("::"):
                    assert False, f"Comment found in distribution file {fpath}:{idx} -> {line}"

if __name__ == "__main__":
    test_distribution_directory_structure()
    test_distribution_critical_files()
    test_models_bundling()
    test_inno_setup_script()
    test_zero_comments_across_distribution()
    print("ALL MILESTONE 5 PACKAGING & DISTRIBUTION TESTS PASSED")
