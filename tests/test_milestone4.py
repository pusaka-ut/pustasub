import os
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.server import app

def test_admin_dashboard_static_assets():
    client = TestClient(app)
    
    res_html = client.get("/admin/index.html")
    assert res_html.status_code == 200
    assert "PUSTASUB" in res_html.text
    assert "gummy-vu-track" in res_html.text
    assert "preset-pill-grid" in res_html.text
    assert "hotwords-chip-container" in res_html.text
    
    banned_white = "#" + "f" * 6
    res_css = client.get("/admin/style.css")
    assert res_css.status_code == 200
    assert "--primary-blue: #034694;" in res_css.text
    assert "--vibrant-yellow: #FFDE00;" in res_css.text
    assert banned_white not in res_css.text.lower()
    
    res_js = client.get("/admin/app.js")
    assert res_js.status_code == 200
    assert "connectWebSocket" in res_js.text
    assert "updateVuMeter" in res_js.text
    assert "handlePanicClear" in res_js.text
    assert banned_white not in res_js.text.lower()

def test_dashboard_operator_controls():
    client = TestClient(app)
    
    res_lang = client.post("/api/control/language", json={"language": "id"})
    assert res_lang.status_code == 200
    assert res_lang.json()["active_language"] == "id"
    
    res_pacing = client.post("/api/control/pacing", json={"pacing_mode": "word_flow"})
    assert res_pacing.status_code == 200
    assert res_pacing.json()["pacing_mode"] == "word_flow"
    
    res_preset = client.post("/api/control/preset", json={"preset_id": "slide_friendly"})
    assert res_preset.status_code == 200
    assert res_preset.json()["active_preset"] == "slide_friendly"
    
    client.post("/api/control/language", json={"language": "en"})
    client.post("/api/control/pacing", json={"pacing_mode": "paced_chunk"})
    client.post("/api/control/preset", json={"preset_id": "academic_formal"})

def test_dashboard_websocket_interaction():
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as ws:
        init_msg = ws.receive_json()
        assert init_msg.get("event") == "init_state"
        
        ws.send_json({"event": "panic_clear"})
        panic_msg = ws.receive_json()
        assert panic_msg.get("event") == "panic_clear"
        
        ws.send_json({"event": "freeze_toggle"})
        freeze_msg = ws.receive_json()
        assert freeze_msg.get("event") == "freeze_subtitle"
        
        ws.send_json({"event": "apply_preset", "preset_id": "talkshow_honey"})
        preset_msg = ws.receive_json()
        assert preset_msg.get("event") == "apply_preset"
        assert preset_msg.get("preset_id") == "talkshow_honey"

if __name__ == "__main__":
    test_admin_dashboard_static_assets()
    test_dashboard_operator_controls()
    test_dashboard_websocket_interaction()
    print("ALL MILESTONE 4 OPERATOR DASHBOARD TESTS PASSED")
