import unittest
import os
import re

class TestMilestone11CandyClayUI(unittest.TestCase):
    def test_zero_neon_in_all_stylesheets(self):
        css_files = [
            os.path.join("web", "admin", "style.css"),
            os.path.join("web", "overlay", "style.css")
        ]
        for css_path in css_files:
            self.assertTrue(os.path.exists(css_path))
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()

            neon_box_shadow = re.findall(r"box-shadow:[^;]*\b0\s+0\s+\d+px", content)
            self.assertEqual(len(neon_box_shadow), 0, f"Neon box-shadow detected in {css_path}: {neon_box_shadow}")

            neon_text_shadow = re.findall(r"text-shadow:[^;]*\b0\s+0\s+\d+px", content)
            self.assertEqual(len(neon_text_shadow), 0, f"Neon text-shadow detected in {css_path}: {neon_text_shadow}")

    def test_zero_pure_white_in_all_ui_files(self):
        paths = [
            os.path.join("web", "admin", "style.css"),
            os.path.join("web", "admin", "index.html"),
            os.path.join("web", "overlay", "style.css"),
            os.path.join("web", "overlay", "index.html")
        ]
        hex_white_pattern = re.compile(r"#fff(?:fff)?\b", re.IGNORECASE)
        for filepath in paths:
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            matches = hex_white_pattern.findall(content)
            self.assertEqual(len(matches), 0, f"Pure white #{matches} found in {filepath}")

    def test_dynamic_font_outfit_embedded_and_styled(self):
        pairs = [
            (os.path.join("web", "admin", "index.html"), os.path.join("web", "admin", "style.css")),
            (os.path.join("web", "overlay", "index.html"), os.path.join("web", "overlay", "style.css"))
        ]
        for html_path, css_path in pairs:
            self.assertTrue(os.path.exists(html_path))
            self.assertTrue(os.path.exists(css_path))
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            self.assertIn("Outfit", html_content)
            self.assertIn("Plus+Jakarta+Sans", html_content)

            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            self.assertIn("Outfit", css_content)
            self.assertIn("Plus Jakarta Sans", css_content)

    def test_candyclay_three_shadow_physics_applied(self):
        css_files = [
            os.path.join("web", "admin", "style.css"),
            os.path.join("web", "overlay", "style.css")
        ]
        for css_path in css_files:
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("inset", content)

    def test_zero_comments_in_all_ui_files(self):
        files_to_check = [
            os.path.join("web", "admin", "style.css"),
            os.path.join("web", "admin", "index.html"),
            os.path.join("web", "overlay", "style.css"),
            os.path.join("web", "overlay", "index.html")
        ]
        for filepath in files_to_check:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines, start=1):
                stripped = line.strip()
                if filepath.endswith(".css"):
                    if "/*" in stripped or "*/" in stripped:
                        self.fail(f"CSS comment found in {filepath}:{idx} -> {stripped}")
                elif filepath.endswith(".html"):
                    if "<!--" in stripped or "-->" in stripped:
                        self.fail(f"HTML comment found in {filepath}:{idx} -> {stripped}")

if __name__ == "__main__":
    unittest.main()