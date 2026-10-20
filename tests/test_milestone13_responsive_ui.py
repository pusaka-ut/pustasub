import unittest
import os
import re

class TestMilestone13ResponsiveUI(unittest.TestCase):
    def test_dynamic_center_maximal_width_declared(self):
        css_path = os.path.join("web", "admin", "style.css")
        self.assertTrue(os.path.exists(css_path))
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("max-width: min(1580px, 95vw);", content)
        self.assertIn("margin: 0 auto;", content)

    def test_responsive_grid_and_breakpoints_present(self):
        css_path = os.path.join("web", "admin", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("@media (max-width: 1060px)", content)
        self.assertIn("@media (max-width: 720px)", content)
        self.assertIn("grid-template-columns: minmax(0, 1.48fr) minmax(360px, 1fr);", content)

    def test_precision_spacing_and_clamp_scales(self):
        css_path = os.path.join("web", "admin", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        clamp_count = len(re.findall(r"clamp\(", content))
        self.assertGreaterEqual(clamp_count, 6, f"Expected at least 6 clamp rules for dynamic spacing, found {clamp_count}")

    def test_action_button_flexibility_and_no_squash(self):
        css_path = os.path.join("web", "admin", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("flex-wrap: wrap;", content)
        self.assertIn("flex: 1.4 1 200px;", content)

    def test_zero_neon_and_zero_glow(self):
        css_path = os.path.join("web", "admin", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        neon_box_shadow = re.findall(r"box-shadow:[^;]*\b0\s+0\s+\d+px", content)
        self.assertEqual(len(neon_box_shadow), 0, f"Neon box-shadow found: {neon_box_shadow}")

        neon_text_shadow = re.findall(r"text-shadow:[^;]*\b0\s+0\s+\d+px", content)
        self.assertEqual(len(neon_text_shadow), 0, f"Neon text-shadow found: {neon_text_shadow}")

    def test_zero_pure_white_in_admin_ui(self):
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
