import unittest
import os
import re

class TestMilestone12DesktopFrontend(unittest.TestCase):
    def test_soft_lilac_canvas_and_not_blue(self):
        css_path = os.path.join("web", "admin", "style.css")
        self.assertTrue(os.path.exists(css_path))
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("#ECE8F6", content)
        self.assertNotIn("--canvas-bg: #0A1532", content)

    def test_zero_neon_and_glow_in_stylesheet(self):
        css_path = os.path.join("web", "admin", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        neon_box_shadow = re.findall(r"box-shadow:[^;]*\b0\s+0\s+\d+px", content)
        self.assertEqual(len(neon_box_shadow), 0, f"Neon box-shadow found: {neon_box_shadow}")

        neon_text_shadow = re.findall(r"text-shadow:[^;]*\b0\s+0\s+\d+px", content)
        self.assertEqual(len(neon_text_shadow), 0, f"Neon text-shadow found: {neon_text_shadow}")

    def test_zero_pure_white_in_all_admin_files(self):
        root_dir = os.path.join("web", "admin")
        hex_white_pattern = re.compile(r"#fff(?:fff)?\b", re.IGNORECASE)
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith((".html", ".css", ".js")):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    matches = hex_white_pattern.findall(content)
                    self.assertEqual(len(matches), 0, f"Pure white #{matches} found in {filepath}")

    def test_official_logos_exist_and_linked(self):
        logo_png = os.path.join("web", "admin", "assets", "logo.png")
        logo_teks_png = os.path.join("web", "admin", "assets", "logo_teks.png")
        html_path = os.path.join("web", "admin", "index.html")

        self.assertTrue(os.path.exists(logo_png))
        self.assertTrue(os.path.exists(logo_teks_png))

        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("assets/logo.png", html)

    def test_no_version_chip_and_no_tacky_badges(self):
        html_path = os.path.join("web", "admin", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertNotIn("v1.2.0", html)
        self.assertNotIn("version-chip", html)
        self.assertNotIn("engine-status-badge", html)
        self.assertNotIn("engine-lang-badge", html)
        self.assertNotIn("pacing-badge", html)

    def test_professional_svg_icons_used_and_no_crude_unicode(self):
        html_path = os.path.join("web", "admin", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertNotIn("&boxbox;", html)
        self.assertNotIn("&par;", html)
        self.assertNotIn("&sext;", html)
        self.assertNotIn("&blacktriangleright;", html)
        self.assertIn("<svg", html)

    def test_modular_frontend_es_modules_exist(self):
        required_modules = [
            "config.js",
            "icons.js",
            "api.js",
            "websocket.js",
            "ui-controller.js",
            "vocab-manager.js",
            "app.js"
        ]
        for mod in required_modules:
            mod_path = os.path.join("web", "admin", "js", mod)
            self.assertTrue(os.path.exists(mod_path), f"Module {mod} missing at {mod_path}")

        html_path = os.path.join("web", "admin", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('type="module" src="js/app.js"', html)

    def test_font_inherit_reset_declared(self):
        css_path = os.path.join("web", "admin", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("button, input, select, textarea, kbd", content)
        self.assertIn("font-family: inherit;", content)

    def test_zero_comments_in_all_admin_code(self):
        root_dir = os.path.join("web", "admin")
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith((".html", ".css", ".js")):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, start=1):
                        stripped = line.strip()
                        if file.endswith(".js"):
                            if stripped.startswith("//") or "/*" in stripped or "*/" in stripped:
                                self.fail(f"JS comment found in {filepath}:{idx} -> {stripped}")
                        elif file.endswith(".css"):
                            if "/*" in stripped or "*/" in stripped:
                                self.fail(f"CSS comment found in {filepath}:{idx} -> {stripped}")
                        elif file.endswith(".html"):
                            if "<!--" in stripped or "-->" in stripped:
                                self.fail(f"HTML comment found in {filepath}:{idx} -> {stripped}")

if __name__ == "__main__":
    unittest.main()
