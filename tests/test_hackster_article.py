"""Tests for the scripts of the hackster-article skill.

Run with: python -m unittest discover tests
The censoring test needs Pillow (e.g. uv run --with pillow python -m unittest discover tests);
without Pillow it is skipped.
"""
import io
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "hackster-article", "scripts")
sys.path.insert(0, SCRIPTS)

import check_article  # noqa: E402
import sanitize_photos  # noqa: E402

HAVE_PILLOW = sanitize_photos.pillow_available()


def write_temp(text, suffix=".md"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


class CheckArticleTest(unittest.TestCase):
    def check(self, text, **kwargs):
        path = write_temp(text)
        try:
            return check_article.check(path, **kwargs)
        finally:
            os.remove(path)

    def messages(self, findings):
        return [msg for _, msg in findings]

    def test_clean_draft(self):
        text = (
            "# Title\n\n## Story\n\nA short paragraph with `one` code span.\n\n"
            "**Subsection**\n\nThe pins:\n\n- **GPIO 13:** servo signal\n\n"
            "```cpp\nint x = 5;\n```\n\nSee [link](https://example.com).\n"
        )
        errors, warnings, _ = self.check(text)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_table(self):
        errors, _, _ = self.check("| a | b |\n|---|---|\n| 1 | 2 |\n")
        self.assertTrue(all("table" in m for m in self.messages(errors)))
        self.assertEqual(len(errors), 3)

    def test_heading_levels(self):
        errors, _, _ = self.check("# T\n\n## A\n\n### B\n")
        self.assertIn("more than one heading level", self.messages(errors)[0])

    def test_code_block_rules(self):
        long_line = "x" * 77
        text = ("```cpp\nint a = 5 % 3;\nint b = 1; // note\n" + long_line +
                "\nString s = \"http://a\";\n```\n\n```\nfoo\n```\n\n"
                "```ini\nkey = 1 ; note\n```\n")
        msgs = self.messages(self.check(text)[0])
        self.assertTrue(any("'%'" in m for m in msgs))
        self.assertEqual(sum("comment" in m for m in msgs), 2)
        self.assertTrue(any("too long (77" in m for m in msgs))
        self.assertTrue(any("without language" in m for m in msgs))

    def test_bare_url(self):
        msgs = self.messages(self.check("Visit https://example.com today.\n")[0])
        self.assertEqual(msgs, ["bare URL: https://example.com"])

    def test_warnings(self):
        text = ("One. Two. Three. Four. Five. Six.\n\n"
                "Uses `a` and `b` in one paragraph.\n\n"
                "Values such as 3.3 V, e.g. this, approx. 5 V are one sentence.\n")
        errors, warnings, _ = self.check(text)
        msgs = self.messages(warnings)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 2)
        self.assertIn("6 sentences", msgs[0])
        self.assertIn("2 inline code spans", msgs[1])

    def test_publish(self):
        text = ("> **Hackster meta information** (do not copy into the story)\n\n"
                "[Figure: photo.jpg — A meaningful caption here]\n\nTODO: write this\n")
        self.assertEqual(self.check(text)[0], [])
        msgs = self.messages(self.check(text, publish=True)[0])
        self.assertEqual(len(msgs), 2)
        self.assertFalse(any("meta information" in m for m in msgs))
        self.assertTrue(any("figure placeholder" in m for m in msgs))
        self.assertTrue(any("TODO" in m for m in msgs))

    def test_bold_in_running_text(self):
        text = ("**Power Supply**\n\n**Lesson title.** Some text.\n\n"
                "The pins:\n\n- **GPIO 13:** servo, see `**kwargs`\n"
                "- The **servo** gets 5 V.\n\n"
                "Powered via the **USB-C port**, *every* time.\n")
        _, warnings, _ = self.check(text)
        msg = ("bold text in a sentence: use bold only for titles and labels at the start, "
               "italics for rare emphasis")
        self.assertEqual(warnings, [(8, msg), (10, msg)])

    def test_list_without_intro(self):
        text = ("## Things used in this project\n\n**Hardware components**\n\n- 1 × ESP32\n\n"
                "## Story\n\n**Key Features**\n\n- Captive portal\n- Elevator\n\n"
                "- Loose list item\n\nThe pins:\n\n- **GPIO 13:** servo\n"
                "  - nested item\n\n> **Meta**\n>\n> - **Name:** Test\n")
        _, warnings, _ = self.check(text)
        self.assertEqual(warnings, [(11, "list without introductory sentence: say what the "
                                        "list is about, preferably ending with ':'")])

    def test_image_directly_below_heading(self):
        caption = "[Figure: servo.jpg — Servo with winch spool at the top of the shaft]"
        text = (f"## Elevator\n\n{caption}\n\n"
                f"## Lighting\n\nA short introduction.\n\n{caption}\n\n"
                f"**Power Supply**\n\n{caption}\n\n"
                f"**Mounting**\n\nA short introduction.\n\n{caption}\n")
        _, warnings, _ = self.check(text)
        msg = ("image directly below a heading or subsection title: "
               "start with a short paragraph, then the image")
        self.assertEqual(warnings, [(3, msg), (13, msg)])

    def test_image_references(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "gps.jpg"), "wb") as f:
                f.write(fake_jpeg())
            with open(os.path.join(d, "clean.jpg"), "wb") as f:
                f.write(sanitize_photos.strip(fake_jpeg()))
            text = ("![Limit switch at the bottom of the shaft](clean.jpg)\n\n"
                    "![Servo with winch spool at the top](gps.jpg)\n\n"
                    "![Photo](missing.jpg)\n")
            draft = os.path.join(d, "draft.md")
            with open(draft, "w", encoding="utf-8") as f:
                f.write(text)
            errors, warnings, _ = check_article.check(draft)
            msgs = self.messages(errors)
            self.assertEqual(len(msgs), 2)
            self.assertIn("gps.jpg contains GPS data", msgs[0])
            self.assertIn("image not found: missing.jpg", msgs[1])
            self.assertEqual(self.messages(warnings), [
                "image caption is generic: describe what the reader sees and why it matters"])
            _, warnings, _ = check_article.check(draft, publish=True)
            self.assertIn("3 image(s)", self.messages(warnings)[-1])

    def test_list_images(self):
        text = ("# Title\n\n![Doll house before being set out](a.jpg)\n\n"
                "## Elevator\n\nText.\n\n![Limit switch at the bottom](b.jpg \"t\")\n\n"
                "```md\n![Not an image](c.jpg)\n```\n\n![](d.png)\n")
        path = write_temp(text)
        try:
            self.assertEqual(check_article.list_images(path), [
                (3, "Title", "a.jpg", "Doll house before being set out"),
                (9, "Elevator", "b.jpg", "Limit switch at the bottom"),
                (15, "Elevator", "d.png", ""),
            ])
        finally:
            os.remove(path)

    def test_terms(self):
        text = ("The PWM (pulse-width modulation) signal.\n\n"
                "- 2 × ACME XY Switch\n\nThe LED and the ESP32 use PWM and RSSI.\n")
        _, _, terms = self.check(text, terms=True)
        self.assertEqual(sorted(terms), ["PWM", "RSSI"])
        self.assertEqual(terms["PWM"][0], 1)

    def test_captions(self):
        cases = {
            "[Figure: a.jpg]": "missing",
            "[Figure: a.jpg — ]": "missing",
            "[Figure: a.jpg — a.jpg]": "is only a file name",
            "[Figure: a.jpg — Photo]": "is generic",
            "[Figure: a.jpg — Image 3]": "is generic",
            "[Figure: a.jpg — The elevator]": "is very short",
            "[Figure: a.jpg — Limit switch at the bottom of the shaft]": None,
        }
        for placeholder, expected in cases.items():
            self.assertEqual(check_article.caption_problem(placeholder), expected, placeholder)
        _, warnings, _ = self.check("[Figure: a.jpg — Photo]\n")
        self.assertIn("figure caption is generic", self.messages(warnings)[0])

    def test_exit_code(self):
        path = write_temp("| a |\n|---|\n")
        try:
            result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "check_article.py"),
                                     path], capture_output=True)
            self.assertEqual(result.returncode, 1)
        finally:
            os.remove(path)


class PreviewStylesheetTest(unittest.TestCase):
    def test_layout_only(self):
        path = os.path.join(ROOT, "skills", "hackster-article", "assets", "hackster-preview.css")
        with open(path, encoding="utf-8") as f:
            css = f.read()
        rules = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        self.assertIn("max-width", rules)
        for prop in ("font-family", "color", "background"):
            self.assertNotRegex(rules, rf"(^|[\s;{{]){prop}\s*:", prop)


def segment(marker, payload):
    return bytes([0xFF, marker]) + struct.pack(">H", len(payload) + 2) + payload


def exif_with_gps_and_orientation(orientation):
    """Minimal EXIF block: IFD0 with orientation and a (dummy) GPS IFD pointer."""
    tiff = b"II*\x00" + struct.pack("<I", 8) + struct.pack("<H", 2)
    tiff += struct.pack("<HHIHH", 0x0112, 3, 1, orientation, 0)
    tiff += struct.pack("<HHII", 0x8825, 4, 1, 0)
    tiff += struct.pack("<I", 0)
    return b"Exif\x00\x00" + tiff


def fake_jpeg(orientation=6):
    """Synthetic JPEG structure (not decodable, but with valid segment layout)."""
    data = b"\xff\xd8"
    data += segment(0xE1, exif_with_gps_and_orientation(orientation))
    data += segment(0xE1, b"http://ns.adobe.com/xap/1.0/\x00<x:xmpmeta>GPS</x:xmpmeta>")
    data += segment(0xE2, b"ICC_PROFILE\x00\x01\x01profile")
    data += segment(0xE2, b"MPF\x00secondary image index")
    data += segment(0xED, b"Photoshop 3.0\x00IPTC")
    data += segment(0xFE, b"comment")
    data += segment(0xDB, b"\x00" + bytes(64))
    data += segment(0xDA, b"\x01\x01\x00\x00\x3f\x00")
    data += b"\x12\x34\xff\x00\x56\xff\xd0\x78"          # entropy data incl. stuffing and RST
    data += b"\xff\xd9"
    data += b"appended motion photo video with GPS"
    return data


class SanitizePhotosTest(unittest.TestCase):
    def test_strip(self):
        out = sanitize_photos.strip(fake_jpeg(orientation=6))
        self.assertTrue(out.startswith(b"\xff\xd8"))
        self.assertTrue(out.endswith(b"\xff\xd9"))
        self.assertNotIn(b"GPS", out)
        self.assertNotIn(b"xmpmeta", out)
        self.assertNotIn(b"MPF", out)
        self.assertNotIn(b"IPTC", out)
        self.assertNotIn(b"comment", out)
        self.assertNotIn(b"\x88\x25", out)               # GPS IFD tag
        self.assertIn(b"ICC_PROFILE", out)                # color profile is kept
        self.assertIn(b"\x12\x34\xff\x00\x56\xff\xd0\x78", out)  # image data unchanged
        # orientation is preserved in a minimal EXIF block
        self.assertEqual(sanitize_photos.read_orientation(out[6:6 + 30]), 6)

    def test_no_exif_block_for_normal_orientation(self):
        out = sanitize_photos.strip(fake_jpeg(orientation=1))
        self.assertNotIn(b"Exif", out)

    def test_not_a_jpeg(self):
        with self.assertRaises(ValueError):
            sanitize_photos.strip(b"\x89PNG....")

    def test_cli_refuses_same_directory(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.run([sys.executable,
                                     os.path.join(SCRIPTS, "sanitize_photos.py"), d, d],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must differ", result.stderr)

    def test_cli_writes_copies(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = photo_dirs(d, {"a.jpg": fake_jpeg()})
            with open(os.path.join(src, "notes.txt"), "w") as f:
                f.write("ignored")
            run_sanitize(src, dst, check=True)
            self.assertEqual(os.listdir(dst), ["a.jpg"])
            with open(os.path.join(dst, "a.jpg"), "rb") as f:
                self.assertNotIn(b"GPS", f.read())

    def test_metadata_problem(self):
        self.assertIsNotNone(sanitize_photos.metadata_problem(fake_jpeg()))
        for orientation in (1, 6):
            out = sanitize_photos.strip(fake_jpeg(orientation=orientation))
            self.assertIsNone(sanitize_photos.metadata_problem(out), orientation)

    def test_read_censor_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "censor.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("# comment\n\na.jpg 1,2,3,4  # trailing comment\n"
                        "b.jpg 1,1,5,5 10,10,20,20\na.jpg 5,6,7,8\n")
            self.assertEqual(sanitize_photos.read_censor_file(path), {
                "a.jpg": [(1, 2, 3, 4), (5, 6, 7, 8)],
                "b.jpg": [(1, 1, 5, 5), (10, 10, 20, 20)],
            })
            for line in ("a.jpg\n", "a.jpg 1,2,3\n", "a.jpg 5,5,1,1\n"):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(line)
                with self.assertRaises(SystemExit, msg=line):
                    sanitize_photos.read_censor_file(path)

    def test_cli_censor_file_errors(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = photo_dirs(d, {"a.jpg": fake_jpeg()},
                                  censor="missing.jpg 1,1,5,5\n")
            result = run_sanitize(src, dst)
            self.assertEqual(result.returncode, 1)
            self.assertIn("not found in", result.stderr)
            self.assertFalse(os.path.exists(dst))
            result = run_sanitize(src, dst, "--censor", os.path.join(d, "nope.txt"))
            self.assertEqual(result.returncode, 1)
            self.assertIn("censor file not found", result.stderr)

    def test_cli_without_pillow_skips_censored_photos(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = photo_dirs(d, {"a.jpg": fake_jpeg(), "b.jpg": fake_jpeg()},
                                  censor="b.jpg 1,1,5,5\n")
            # A fake "PIL" package that fails to import hides an installed Pillow
            blocker = os.path.join(d, "blocker", "PIL")
            os.makedirs(blocker)
            with open(os.path.join(blocker, "__init__.py"), "w") as f:
                f.write("raise ImportError('blocked for the test')\n")
            env = dict(os.environ, PYTHONPATH=os.path.dirname(blocker))
            result = run_sanitize(src, dst, env=env)
            self.assertEqual(result.returncode, 1)
            self.assertIn("censoring needs Pillow: b.jpg", result.stderr)
            self.assertEqual(os.listdir(dst), ["a.jpg"])   # no uncensored copy of b.jpg

    @unittest.skipUnless(HAVE_PILLOW, "Pillow not installed")
    def test_cli_censors_with_pillow(self):
        from PIL import Image
        img = Image.new("RGB", (64, 48), (255, 255, 255))
        for x in range(16, 48):
            for y in range(8, 40):
                img.putpixel((x, y), (0, 0, 0) if (x + y) % 2 else (255, 0, 0))
        buf = io.BytesIO()
        exif = Image.Exif()
        exif[0x010F] = "ACME camera"                     # make: metadata to be removed
        img.save(buf, "JPEG", quality=95, exif=exif.tobytes())
        with tempfile.TemporaryDirectory() as d:
            src, dst = photo_dirs(d, {"a.jpg": buf.getvalue(), "b.jpg": fake_jpeg()},
                                  censor="a.jpg 16,8,48,40\n")
            result = run_sanitize(src, dst)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 area(s) censored", result.stdout)
            with open(os.path.join(dst, "a.jpg"), "rb") as f:
                data = f.read()
            self.assertIsNone(sanitize_photos.metadata_problem(data))
            self.assertNotIn(b"ACME", data)
            out = Image.open(io.BytesIO(data)).convert("RGB")
            self.assertEqual(out.size, (64, 48))
            # the checkerboard is replaced by uniform 8x8 blocks
            block = [out.getpixel((x, y)) for x in range(17, 23) for y in range(9, 15)]
            spread = max(max(c) - min(c) for c in zip(*block))
            self.assertLess(spread, 40)
            self.assertEqual(out.getpixel((2, 2)), (255, 255, 255))   # outside unchanged


class UnusedImagesTest(unittest.TestCase):
    def make(self, d, web, original=(), draft=""):
        for folder, names in (("web", web), ("original", original)):
            os.makedirs(os.path.join(d, "photos", folder), exist_ok=True)
            for name in names:
                with open(os.path.join(d, "photos", folder, name), "wb") as f:
                    f.write(sanitize_photos.strip(fake_jpeg()))
        path = os.path.join(d, "draft.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(draft)
        return path

    def test_unused_and_missing_copies(self):
        with tempfile.TemporaryDirectory() as d:
            draft = self.make(
                d, web=["a.jpg", "b.jpg", "c.jpg"], original=["a.jpg", "b.jpg", "d.jpg"],
                draft="![Limit switch at the bottom of the shaft](photos/web/a.jpg)\n\n"
                      "[Figure: c.jpg — Relay module next to the servo]\n")
            _, warnings, _ = check_article.check(draft)
            msgs = [m for _, m in warnings]
            self.assertEqual(len(msgs), 2, msgs)
            self.assertIn("1 unused image(s) in photos/web/: b.jpg", msgs[0])
            self.assertIn("photos/original/ without a stripped copy", msgs[1])
            self.assertIn("d.jpg", msgs[1])

    def test_cover_image(self):
        meta = "> **Hackster meta information**\n> - **Cover image:** ![House](photos/web/a.jpg)\n"
        with tempfile.TemporaryDirectory() as d:
            draft = self.make(d, web=["a.jpg", "b.jpg"], draft=(
                meta + "\n## Story\n\n![Limit switch at the bottom of the shaft](photos/web/b.jpg)\n"))
            errors, warnings, _ = check_article.check(draft, publish=True)
            self.assertEqual(errors, [])
            msgs = [m for _, m in warnings]
            self.assertFalse(any("unused" in m or "cover" in m for m in msgs), msgs)
            images = check_article.list_images(draft)
            self.assertEqual([(i[1], i[2]) for i in images], [
                ("Cover image (meta block)", "photos/web/a.jpg"), ("Story", "photos/web/b.jpg")])

    def test_cover_image_missing(self):
        with tempfile.TemporaryDirectory() as d:
            draft = self.make(d, web=["b.jpg"], draft=(
                "> - **Cover image:** ![House](photos/web/nope.jpg)\n\n"
                "![Limit switch at the bottom of the shaft](photos/web/b.jpg)\n"))
            errors, _, _ = check_article.check(draft)
            self.assertEqual([m for _, m in errors], ["image not found: photos/web/nope.jpg"])
            draft = self.make(d, web=["b.jpg"], draft="![Limit switch at the bottom](photos/web/b.jpg)\n")
            _, warnings, _ = check_article.check(draft, publish=True)
            self.assertTrue(any("no cover image" in m for _, m in warnings))


def photo_dirs(d, photos, censor=None):
    """Create <d>/photos/original with the photos (and censor.txt next to it)."""
    src, dst = os.path.join(d, "photos", "original"), os.path.join(d, "photos", "web")
    os.makedirs(src)
    for name, data in photos.items():
        with open(os.path.join(src, name), "wb") as f:
            f.write(data)
    if censor is not None:
        with open(os.path.join(d, "photos", "censor.txt"), "w", encoding="utf-8") as f:
            f.write(censor)
    return src, dst


def run_sanitize(src, dst, *args, check=False, env=None):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, "sanitize_photos.py"),
                           src, dst, *args], capture_output=True, text=True, check=check,
                          env=env)


if __name__ == "__main__":
    unittest.main()
