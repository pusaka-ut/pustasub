import os
import sys
import shutil
import zipfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_ROOT = os.path.join(PROJECT_ROOT, "dist", "PUSTASUB")
COMPILED_DIR = os.path.join(PROJECT_ROOT, "dist", "pustasub-engine")
ZIP_OUT = os.path.join(PROJECT_ROOT, "dist", "PUSTASUB-v1.1.0-Portable.zip")

def create_directory_structure():
    if os.path.exists(DIST_ROOT):
        shutil.rmtree(DIST_ROOT)
    os.makedirs(DIST_ROOT, exist_ok=True)
    os.makedirs(os.path.join(DIST_ROOT, "web", "admin"), exist_ok=True)
    os.makedirs(os.path.join(DIST_ROOT, "web", "overlay"), exist_ok=True)
    os.makedirs(os.path.join(DIST_ROOT, "models"), exist_ok=True)
    os.makedirs(os.path.join(DIST_ROOT, "data"), exist_ok=True)
    os.makedirs(os.path.join(DIST_ROOT, "config"), exist_ok=True)
    os.makedirs(os.path.join(DIST_ROOT, "output", "sessions"), exist_ok=True)

def copy_application_files():
    if os.path.exists(COMPILED_DIR):
        exe_src = os.path.join(COMPILED_DIR, "pustasub-engine.exe")
        if os.path.exists(exe_src):
            shutil.copy2(exe_src, os.path.join(DIST_ROOT, "pustasub-engine.exe"))
            shutil.copy2(exe_src, os.path.join(DIST_ROOT, "PUSTASUB.exe"))
        internal_src = os.path.join(COMPILED_DIR, "_internal")
        if os.path.exists(internal_src):
            shutil.copytree(internal_src, os.path.join(DIST_ROOT, "_internal"), dirs_exist_ok=True)

    web_admin_src = os.path.join(PROJECT_ROOT, "web", "admin")
    for f in os.listdir(web_admin_src):
        src_item = os.path.join(web_admin_src, f)
        dst_item = os.path.join(DIST_ROOT, "web", "admin", f)
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
        else:
            shutil.copy2(src_item, dst_item)

    web_overlay_src = os.path.join(PROJECT_ROOT, "web", "overlay")
    for f in os.listdir(web_overlay_src):
        src_item = os.path.join(web_overlay_src, f)
        dst_item = os.path.join(DIST_ROOT, "web", "overlay", f)
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
        else:
            shutil.copy2(src_item, dst_item)

    config_src = os.path.join(PROJECT_ROOT, "config.json")
    if os.path.exists(config_src):
        shutil.copy2(config_src, os.path.join(DIST_ROOT, "config.json"))

    hotwords_src = os.path.join(PROJECT_ROOT, "config", "hotwords.txt")
    if os.path.exists(hotwords_src):
        shutil.copy2(hotwords_src, os.path.join(DIST_ROOT, "config", "hotwords.txt"))

    db_src = os.path.join(PROJECT_ROOT, "data", "pustasub.db")
    if os.path.exists(db_src):
        shutil.copy2(db_src, os.path.join(DIST_ROOT, "data", "pustasub.db"))

    update_src = os.path.join(PROJECT_ROOT, "update.bat")
    if os.path.exists(update_src):
        shutil.copy2(update_src, os.path.join(DIST_ROOT, "update.bat"))

    models_src = os.path.join(PROJECT_ROOT, "models")
    if os.path.exists(models_src):
        for item in os.listdir(models_src):
            s = os.path.join(models_src, item)
            d = os.path.join(DIST_ROOT, "models", item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    empty_sub = os.path.join(DIST_ROOT, "output", "current_subtitle.txt")
    with open(empty_sub, "w", encoding="utf-8") as f:
        f.write("")

    empty_trans = os.path.join(DIST_ROOT, "output", "current_translation.txt")
    with open(empty_trans, "w", encoding="utf-8") as f:
        f.write("")

def write_launchers():
    bat_content = (
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n\r\n"
        "for /f \"tokens=5\" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (\r\n"
        "    taskkill /F /PID %%a >nul 2>&1\r\n"
        ")\r\n\r\n"
        "start \"\" cmd /c \"timeout /t 2 /nobreak >nul && start http://127.0.0.1:8765/admin\"\r\n\r\n"
        "if exist pustasub-engine.exe (\r\n"
        "    pustasub-engine.exe\r\n"
        ") else if exist python\\python.exe (\r\n"
        "    python\\python.exe -m uvicorn engine.server:app --host 127.0.0.1 --port 8765 --log-level info\r\n"
        ") else (\r\n"
        "    python -m uvicorn engine.server:app --host 127.0.0.1 --port 8765 --log-level info\r\n"
        ")\r\n"
        "pause\r\n"
    )
    with open(os.path.join(DIST_ROOT, "run.bat"), "w", encoding="utf-8") as f:
        f.write(bat_content)

    vbs_content = "Set WshShell = CreateObject(\"WScript.Shell\")\r\nWshShell.Run \"run.bat\", 0, False\r\nSet WshShell = Nothing\r\n"
    with open(os.path.join(DIST_ROOT, "PUSTASUB.vbs"), "w", encoding="utf-8") as f:
        f.write(vbs_content)

def make_portable_zip():
    if os.path.exists(ZIP_OUT):
        os.remove(ZIP_OUT)
    with zipfile.ZipFile(ZIP_OUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DIST_ROOT):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.dirname(DIST_ROOT))
                zipf.write(abs_path, rel_path)

def build_portable_distribution():
    create_directory_structure()
    copy_application_files()
    write_launchers()
    make_portable_zip()
    return os.path.exists(DIST_ROOT) and os.path.exists(ZIP_OUT)

if __name__ == "__main__":
    success = build_portable_distribution()
    if success:
        print("PORTABLE DISTRIBUTION BUNDLED SUCCESSFULLY AT:", DIST_ROOT)
        print("PORTABLE ZIP ARCHIVE CREATED AT:", ZIP_OUT)
    else:
        print("DISTRIBUTION BUNDLE FAILED")
        sys.exit(1)
