import os
import sys
import time
import threading
import webbrowser
import subprocess
import multiprocessing
import uvicorn
from engine.server import app

def cleanup_port(port=8765):
    try:
        cmd = f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{port} ^| findstr LISTENING\') do taskkill /F /PID %a'
        subprocess.run(cmd, shell=True, capture_output=True)
    except Exception:
        pass

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8765/admin")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(base_dir)
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    cleanup_port(8765)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
