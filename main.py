import os
import sys
import multiprocessing
import uvicorn
from engine.server import app

if __name__ == "__main__":
    multiprocessing.freeze_support()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
