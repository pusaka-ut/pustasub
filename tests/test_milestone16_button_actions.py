import unittest
from fastapi.testclient import TestClient
from engine.server import app

class TestMilestone16ButtonActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_engine_toggle_buttons(self):
        res_start = self.client.post("/api/control/engine", json={"running": True})
        self.assertEqual(res_start.status_code, 200)
        data_start = res_start.json()
        self.assertTrue(data_start.get("success"))
        self.assertEqual(data_start.get("status"), "LIVE")

        res_stop = self.client.post("/api/control/engine", json={"running": False})
        self.assertEqual(res_stop.status_code, 200)
        data_stop = res_stop.json()
        self.assertTrue(data_stop.get("success"))
        self.assertEqual(data_stop.get("status"), "STANDBY")

    def test_panic_clear_button(self):
        res = self.client.post("/api/control/panic", json={})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("action"), "panic_cleared")

    def test_freeze_toggle_button(self):
        res1 = self.client.post("/api/control/freeze", json={"frozen": True})
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json().get("frozen"))

        res2 = self.client.post("/api/control/freeze", json={"frozen": False})
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json().get("frozen"))

    def test_all_preset_pills_both_keys(self):
        presets = [
            "academic_formal",
            "slide_friendly",
            "minimalist_glass",
            "talkshow_honey",
            "news_ticker_ribbon",
            "speech_bubble_playful",
            "top_banner_clean"
        ]
        for p in presets:
            res_client_format = self.client.post("/api/control/preset", json={"preset": p, "preset_id": p})
            self.assertEqual(res_client_format.status_code, 200)
            self.assertEqual(res_client_format.json().get("active_preset"), p)

            res_only_preset = self.client.post("/api/control/preset", json={"preset": p})
            self.assertEqual(res_only_preset.status_code, 200)
            self.assertEqual(res_only_preset.json().get("active_preset"), p)

    def test_position_pills(self):
        positions = ["bottom", "top", "center", "left", "right"]
        for pos in positions:
            res = self.client.post("/api/control/position", json={"position": pos})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json().get("position"), pos)

    def test_translation_switch_and_positions(self):
        res_enable = self.client.post("/api/control/translation", json={"enabled": True})
        self.assertEqual(res_enable.status_code, 200)
        self.assertTrue(res_enable.json().get("translation_enabled"))

        res_disable = self.client.post("/api/control/translation", json={"enabled": False})
        self.assertEqual(res_disable.status_code, 200)
        self.assertFalse(res_disable.json().get("translation_enabled"))

        for pos in ["bottom-right", "top-right", "below-en"]:
            res_pos = self.client.post("/api/control/translation", json={"position": pos})
            self.assertEqual(res_pos.status_code, 200)
            self.assertEqual(res_pos.json().get("translation_position"), pos)

    def test_audio_device_switch(self):
        res = self.client.post("/api/control/device", json={"device_index": -1})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("success"))

    def test_vocabulary_buttons_add_and_delete(self):
        res_add = self.client.post("/api/vocabulary", json={
            "term": "Universitas Terbuka Cyber Campus",
            "category": "technology",
            "weight": 2.5,
            "boost_score": 2.5
        })
        self.assertEqual(res_add.status_code, 200)
        self.assertTrue(res_add.json().get("success"))

        res_del = self.client.delete("/api/vocabulary/Universitas Terbuka Cyber Campus")
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.json().get("success"))

    def test_slider_visual_adjustments(self):
        res = self.client.post("/api/control/style", json={
            "font_size": 44,
            "bg_opacity": 0.8,
            "border_radius": 36,
            "stroke_width": 3.0
        })
        self.assertEqual(res.status_code, 200)
        style = res.json().get("style", {})
        self.assertEqual(style.get("font_size_px"), 44)
        self.assertEqual(style.get("background_opacity"), 0.8)
        self.assertEqual(style.get("border_radius_px"), 36)
        self.assertEqual(style.get("stroke_width_px"), 3.0)

    def test_get_status_and_devices_and_vocabulary(self):
        s = self.client.get("/api/status")
        self.assertEqual(s.status_code, 200)
        self.assertIn("status", s.json())

        d = self.client.get("/api/devices")
        self.assertEqual(d.status_code, 200)
        self.assertIn("devices", d.json())

        v = self.client.get("/api/vocabulary")
        self.assertEqual(v.status_code, 200)
        self.assertIn("items", v.json())

if __name__ == "__main__":
    unittest.main()
