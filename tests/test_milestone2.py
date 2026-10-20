import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
from fastapi.testclient import TestClient
from engine.server import app, session_logger, file_writer

def main():
    print("=" * 60)
    print("PUSTASUB — MILESTONE 2 DELIVERY & SERVER VERIFICATION")
    print("=" * 60)

    client = TestClient(app)

    print("Testing GET /api/status...")
    resp = client.get("/api/status")
    assert resp.status_code == 200, f"Status check failed: {resp.status_code}"
    status_data = resp.json()
    print("Status response:", status_data["status"], "| Active preset:", status_data["active_preset"])
    assert "presets" in status_data
    assert "academic_formal" in status_data["presets"]

    print("Testing POST /api/control/panic...")
    resp_panic = client.post("/api/control/panic")
    assert resp_panic.status_code == 200
    assert resp_panic.json()["action"] == "panic_cleared"
    with open("output/current_subtitle.txt", "r", encoding="utf-8") as f:
        assert f.read() == "", "Panic clear did not wipe subtitle file!"
    print("Panic clear verified: subtitle file wiped instantly.")

    print("Testing POST /api/control/freeze...")
    resp_freeze = client.post("/api/control/freeze")
    assert resp_freeze.status_code == 200
    assert resp_freeze.json()["is_frozen"] is True
    resp_unfreeze = client.post("/api/control/freeze")
    assert resp_unfreeze.json()["is_frozen"] is False
    print("Freeze / Hold toggle verified.")

    print("Testing POST /api/control/preset...")
    resp_preset = client.post("/api/control/preset", json={"preset_id": "talkshow_honey"})
    assert resp_preset.status_code == 200
    assert resp_preset.json()["active_preset"] == "talkshow_honey"
    print("Preset switch verified: active preset is now talkshow_honey.")

    print("Testing SessionLogger SRT & TXT output...")
    session_id = session_logger.start_session()
    print("Session created:", session_id)
    session_logger.log_phrase("Welcome to Universitas Terbuka academic webinar.", 1.2, 4.5)
    session_logger.log_phrase("Today we discuss streaming subtitle technology.", 5.1, 8.9)

    assert os.path.exists(session_logger.srt_path), "SRT file was not created!"
    assert os.path.exists(session_logger.txt_path), "TXT file was not created!"

    with open(session_logger.srt_path, "r", encoding="utf-8") as f:
        srt_content = f.read()
        print("SRT Content Preview:\n" + srt_content.strip())
        assert "00:00:01,200 --> 00:00:04,500" in srt_content
        assert "Welcome to Universitas Terbuka academic webinar." in srt_content

    with open(session_logger.txt_path, "r", encoding="utf-8") as f:
        txt_content = f.read()
        assert "[00:00:01] Welcome to Universitas Terbuka academic webinar." in txt_content
    print("SessionLogger verified: .srt and .txt archives formatted accurately.")

    client.post("/api/control/preset", json={"preset_id": "academic_formal"})

    print("=" * 60)
    print("MILESTONE 2 DELIVERY & SERVER VERIFICATION: 100% SUCCESS!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    main()
