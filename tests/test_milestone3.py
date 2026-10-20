import os
import sys
import time
import json
import asyncio
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.server import app

def test_overlay_static_files():
    client = TestClient(app)
    
    res_index = client.get("/overlay/index.html")
    assert res_index.status_code == 200
    assert "PUSTASUB Broadcast Overlay" in res_index.text
    assert "id=\"subtitle-card\"" in res_index.text
    assert "id=\"subtitle-text\"" in res_index.text
    
    banned_white = "#" + "f" * 6
    res_css = client.get("/overlay/style.css")
    assert res_css.status_code == 200
    assert ".subtitle-card" in res_css.text
    assert "#FFFDF0" in res_css.text
    assert banned_white not in res_css.text.lower()
    
    res_js = client.get("/overlay/overlay.js")
    assert res_js.status_code == 200
    assert "applyPresetStyle" in res_js.text
    assert "executePanicWipe" in res_js.text
    assert banned_white not in res_js.text.lower()

def test_websocket_broadcast_to_overlay():
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        init_data = websocket.receive_json()
        assert init_data.get("event") == "init_state"
        assert "active_preset" in init_data
        assert "style" in init_data
        
        websocket.send_json({"event": "panic_clear"})
        data_panic = websocket.receive_json()
        assert data_panic.get("event") == "panic_clear"
        assert data_panic.get("action") == "instant_wipe"
        
        websocket.send_json({"event": "freeze_toggle"})
        data_freeze = websocket.receive_json()
        assert data_freeze.get("event") == "freeze_subtitle"
        assert "is_frozen" in data_freeze
        
        websocket.send_json({"event": "apply_preset", "preset_id": "talkshow_honey"})
        data_preset = websocket.receive_json()
        assert data_preset.get("event") == "apply_preset"
        assert data_preset.get("preset_id") == "talkshow_honey"
        assert "style" in data_preset
        assert data_preset.get("preset_id") == "talkshow_honey"
        assert "style" in data_preset

if __name__ == "__main__":
    test_overlay_static_files()
    test_websocket_broadcast_to_overlay()
    print("ALL MILESTONE 3 OVERLAY TESTS PASSED")
