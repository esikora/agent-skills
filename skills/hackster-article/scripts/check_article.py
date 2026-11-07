"""Check a Markdown draft of a Hackster.io story for formatting problems.

Errors (exit code 1):
- tables (not supported by the Hackster editor)
- more than one heading level in the story (Hackster offers one heading level)
- code blocks: lines longer than 76 characters, comments, '%' characters, missing language
- bare URLs outside of links and code

- images (![caption](path)): file not found, or JPEG with metadata (GPS, EXIF, XMP)

Additional errors with --publish (run before pasting the story into the Hackster editor):
- figure placeholders ([Figure: ...]) are still present (use real image references)
- "TODO" markers are still present
The meta information block may stay in the draft; it is just not copied into the story.

Warnings (for a manual review, do not change the exit code):
- paragraphs or list items with more than 5 sentences
- paragraphs or list items with more than 1 inline code span (rendered as boxes)
- images and figure placeholders without a meaningful caption (![caption](path) or
  [Figure: file.jpg — caption]): caption missing, shorter than 3 words, only a file name,
  or generic ("photo", "image", ...)
- unused images: image files in a folder the draft takes images from (e.g. photos/web/)
  that the draft does not reference; and, if that folder has a sibling "original" folder
  (photos/original/), originals without a stripped copy. The cover image counts as used
  if the meta block references it: "> - **Cover image:** ![description](path)"
- with --publish: no cover image file referenced in the meta block
- with --publish: reminder to upload the images and set their captions in the editor,
  followed by a list of all images in article order (section, file, caption) to work
  through during the transfer
- with --terms: the first occurrence of each abbreviation (2+ capital letters), so that
  you can check that it is spelled out or explained there

Usage: python check_article.py <draft.md> [--terms] [--publish]
                               [--max-line 76] [--max-sentences 5]
"""
import os
import re
import struct
import sys

MAX_LINE = 76
MAX_SENTENCES = 5
MAX_INLINE_CODE = 1

# Abbreviations that need no explanation for a maker audience
COMMON_TERMS = {
    "LED", "LEDS", "USB", "WIFI", "IOT", "IDE", "PC", "OK", "IP", "HTTP", "HTML", "URL",
    "API", "CPU", "RAM", "PCB", "GND", "DC", "AC", "RGB", "JSON", "TCP", "ID", "UI",
    "GPS", "AI", "GET", "POST", "PDF", "URLS", "GPIOS",
}


GENERIC_CAPTIONS = {
    "photo", "image", "picture", "figure", "screenshot", "img", "pic", "foto", "bild",
    "photo of the project", "the project", "overview", "detail", "result",
}


def caption_problem(placeholder):
    """Return a description of the caption problem of a [Figure: ...] line, or None."""
    m = re.match(r"^\[Figure:\s*(.*?)\]?\s*$", placeholder)
    body = m.group(1) if m else ""
    parts = re.split(r"\s+[—–-]\s+", body, maxsplit=1)
    return caption_text_problem(parts[1] if len(parts) == 2 else "")


def caption_text_problem(caption):
    """Return a description of the problem of a caption text, or None."""
    caption = caption.strip()
    if not caption:
        return "missing"
    plain = caption.rstrip(".").strip().lower()
    if re.fullmatch(r"[\w.\-/]+\.(jpe?g|png|gif|webp|svg|bmp|heic)", plain):
        return "is only a file name"
    if plain in GENERIC_CAPTIONS or re.fullmatch(r"(photo|image|picture|figure|img)\s*\d+", plain):
        return "is generic"
    if len(plain.split()) < 3:
        return "is very short"
    return None


def jpeg_metadata_problem(path):
    """Return a description of the metadata found in a JPEG file, or None.

    Allowed: an EXIF block that only contains the orientation tag (as written by
    sanitize_photos.py). Everything else in APP1 (other EXIF tags, GPS, XMP) is reported.
    """
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] != b"\xff\xd8":
        return "is not a valid JPEG file"
    pos = 2
    while pos + 4 <= len(data) and data[pos] == 0xFF:
        marker = data[pos + 1]
        if marker == 0xDA:
            break
        if marker == 0xD8 or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        payload = data[pos + 4:pos + 2 + length]
        if marker == 0xE1:
            if payload.startswith(b"Exif\x00\x00"):
                tiff = payload[6:]
                endian = "<" if tiff[:2] == b"II" else ">"
                ifd0 = struct.unpack(endian + "I", tiff[4:8])[0]
                count = struct.unpack(endian + "H", tiff[ifd0:ifd0 + 2])[0]
                tags = [struct.unpack(endian + "H", tiff[ifd0 + 2 + 12 * i:ifd0 + 4 + 12 * i])[0]
                        for i in range(count)]
                if 0x8825 in tags:
                    return "contains GPS data"
                if any(tag != 0x0112 for tag in tags):
                    return "contains EXIF metadata"
            else:
                return "contains XMP or other metadata"
        pos += 2 + length
    return None


IMAGE_RE = re.compile(r"^!\[(.*?)\]\((\S+?)(?:\s+\"[^\"]*\")?\)$")
# Cover image in the meta block: "> - **Cover image:** ![description](path) ..."
COVER_RE = re.compile(r"^>\s*(?:-\s*)?\*\*Cover image:?\*\*:?.*?!\[(.*?)\]\((\S+?)\)")


def image_file_problems(base, ref):
    """Return problems of a local image file (missing, JPEG with metadata)."""
    file = os.path.join(base, ref.replace("%20", " "))
    if not os.path.isfile(file):
        return [f"image not found: {ref}"]
    if re.search(r"\.jpe?g$", ref, re.I):
        meta = jpeg_metadata_problem(file)
        if meta:
            return [f"image {ref} {meta}: strip it before publishing (sanitize_photos.py)"]
    return []


def list_images(path):
    """Return the images of a draft in article order as (line, section, path, caption).

    The section is the text of the last heading before the image. Images inside code
    blocks are ignored.
    """
    images, section, in_code = [], "", False
    with open(path, encoding="utf-8") as f:
        for no, line in enumerate(f.read().split("\n"), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            heading = re.match(r"^#{1,6}\s+(.*?)\s*#*$", stripped)
            if heading:
                section = heading.group(1)
                continue
            cover = COVER_RE.match(stripped)
            if cover:
                images.append((no, "Cover image (meta block)", cover.group(2),
                               "(none; upload it as the cover image)"))
                continue
            image = IMAGE_RE.match(stripped)
            if image:
                images.append((no, section, image.group(2), image.group(1).strip()))
    return images


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".heic")


def unused_image_problems(base, refs, placeholders):
    """Return warnings about image files that the draft does not use.

    refs: local image paths referenced by the draft (relative to base).
    placeholders: file names mentioned in [Figure: ...] placeholders (count as used).

    Checks every folder that contains at least one referenced image:
    - image files in that folder that are not referenced (unused photos);
    - if the folder has a sibling "original" folder (convention photos/original and
      photos/web): originals without a copy in the referenced folder (not stripped yet).
    """
    problems = []
    used = {}
    for ref in refs:
        file = os.path.normcase(os.path.abspath(os.path.join(base, ref.replace("%20", " "))))
        used.setdefault(os.path.dirname(file), set()).add(os.path.basename(file))
    placeholder_names = {os.path.normcase(os.path.basename(p)) for p in placeholders}

    def images_in(folder):
        return sorted(f for f in os.listdir(folder)
                      if f.lower().endswith(IMAGE_EXTENSIONS)
                      and os.path.isfile(os.path.join(folder, f)))

    for folder in sorted(used):
        if not os.path.isdir(folder):
            continue
        rel = os.path.relpath(folder, base).replace(os.sep, "/") + "/"
        present = images_in(folder)
        unused = [f for f in present if os.path.normcase(f) not in used[folder]
                  and os.path.normcase(f) not in placeholder_names]
        if unused:
            problems.append(f"{len(unused)} unused image(s) in {rel}: {', '.join(unused)} "
                            "(use them in the article or delete them)")
        original = os.path.join(os.path.dirname(folder), "original")
        if os.path.normcase(original) != folder and os.path.isdir(original):
            copies = {os.path.normcase(f) for f in present}
            missing = [f for f in images_in(original) if os.path.normcase(f) not in copies]
            if missing:
                rel_orig = os.path.relpath(original, base).replace(os.sep, "/") + "/"
                problems.append(f"{len(missing)} image(s) in {rel_orig} without a stripped "
                                f"copy in {rel}: {', '.join(missing)} (strip them with "
                                "sanitize_photos.py if you want to use them)")
    return problems


def count_sentences(text):
    text = re.sub(r"`[^`]*`", "x", text)                 # inline code
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links
    text = re.sub(r"\b(e\.g|i\.e|approx|etc|vs|ca|no)\.", "x", text, flags=re.I)
    text = re.sub(r"\d\.\d", "x", text)                   # decimal numbers
    return len(re.findall(r"[.!?](\s|$)", text))


def check(path, max_line=MAX_LINE, max_sentences=MAX_SENTENCES, terms=False, publish=False):
    errors, warnings, first_terms = [], [], {}
    in_code = False
    lang = ""
    heading_levels = set()
    images = 0
    local_refs, placeholder_files = [], []
    cover_found = False
    base = os.path.dirname(os.path.abspath(path))
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    for no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                lang = stripped[3:].strip()
                if not lang:
                    errors.append((no, "code block without language"))
            else:
                in_code = False
            continue

        if in_code:
            if len(line) > max_line:
                errors.append((no, f"code line too long ({len(line)} > {max_line})"))
            code_wo_strings = re.sub(r'"(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\'', '""', line)
            if re.search(r"(^|[^:])//|/\*", code_wo_strings) or \
                    (lang in ("ini", "toml", "cfg") and re.search(r"(^|\s);", line)) or \
                    (lang in ("python", "py", "sh", "bash", "yaml", "ini") and
                     re.search(r"(^|\s)#", code_wo_strings)):
                errors.append((no, "comment in code block"))
            if "%" in code_wo_strings:
                errors.append((no, "'%' in code block (breaks highlighting)"))
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            errors.append((no, "table (use a bulleted list)"))
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            heading_levels.add(len(m.group(1)))
        for url in re.finditer(r"https?://\S+", line):
            start = url.start()
            if not (line[max(0, start - 2):start] == "](" or line[max(0, start - 1):start] in "<`"):
                errors.append((no, f"bare URL: {url.group(0)}"))

        cover = COVER_RE.match(stripped)
        if cover:
            cover_found = True
            if not re.match(r"^https?://", cover.group(2)):
                local_refs.append(cover.group(2))
                errors.extend((no, msg) for msg in image_file_problems(base, cover.group(2)))
        if publish and re.search(r"\bTODO\b", line):
            errors.append((no, "TODO marker"))
        image = IMAGE_RE.match(stripped)
        if image:
            images += 1
            caption, ref = image.group(1), image.group(2)
            problem = caption_text_problem(caption)
            if problem:
                warnings.append((no, f"image caption {problem}: describe what the reader "
                                     "sees and why it matters"))
            if not re.match(r"^https?://", ref):
                local_refs.append(ref)
                errors.extend((no, msg) for msg in image_file_problems(base, ref))
        elif stripped.startswith("[Figure:"):
            name = re.match(r"^\[Figure:\s*(\S+)", stripped)
            if name:
                placeholder_files.append(name.group(1))
            problem = caption_problem(stripped)
            if problem:
                warnings.append((no, f"figure caption {problem}: describe what the reader "
                                     "sees and why it matters"))
            if publish:
                errors.append((no, "figure placeholder: replace it with a real image "
                                   "reference (![caption](path))"))
        elif stripped and not stripped.startswith(("#", ">")):
            n = count_sentences(stripped)
            if n > max_sentences:
                warnings.append((no, f"long paragraph ({n} sentences > {max_sentences}): "
                                     f"consider splitting or shortening"))
            spans = len(re.findall(r"`[^`]+`", stripped))
            if spans > MAX_INLINE_CODE:
                warnings.append((no, f"{spans} inline code spans (> {MAX_INLINE_CODE}): "
                                     "use plain text where possible"))
        # part lists ("- 2 × ...") contain brand and model names, not abbreviations
        if terms and not stripped.startswith(">") and not re.match(r"^- \d+ ×", stripped):
            plain = re.sub(r"`[^`]*`|\([^)]*\)\]?\([^)]*\)", "", line)
            for t in re.findall(r"\b[A-Z][A-Z0-9]{1,}[a-z]?\b", plain):
                key = t.upper()
                if key not in COMMON_TERMS and key not in first_terms and \
                        not any(c.isdigit() for c in t):
                    first_terms[key] = (no, t, line.strip())

    story_levels = sorted(l for l in heading_levels if l > 1)
    if len(story_levels) > 1:
        errors.append((0, "more than one heading level in the story "
                          f"({', '.join('#' * l for l in story_levels)}); "
                          "use bold paragraph titles for subsections"))
    for problem in unused_image_problems(base, local_refs, placeholder_files):
        warnings.append((0, problem))
    if publish and not cover_found:
        warnings.append((0, "no cover image file referenced in the meta block "
                            "(> - **Cover image:** ![description](path))"))
    if publish and images:
        warnings.append((0, f"{images} image(s): pasting from the preview may not transfer "
                            "images; upload each image in the editor and set its caption "
                            "(see the image list below)"))
    return errors, warnings, first_terms


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    max_line = int(args[args.index("--max-line") + 1]) if "--max-line" in args else MAX_LINE
    max_sent = int(args[args.index("--max-sentences") + 1]) if "--max-sentences" in args \
        else MAX_SENTENCES
    path = args[0]
    errors, warnings, terms = check(path, max_line, max_sent, "--terms" in args,
                                    "--publish" in args)
    for no, msg in errors:
        print(f"{path}:{no}: error: {msg}" if no else f"{path}: error: {msg}")
    for no, msg in warnings:
        print(f"{path}:{no}: warning: {msg}" if no else f"{path}: warning: {msg}")
    if "--publish" in args:
        images = list_images(path)
        if images:
            print("\nImages to upload (in article order; paste the caption into the "
                  "image's caption field):")
            for i, (no, section, ref, caption) in enumerate(images, start=1):
                where = f"{section}, " if section else ""
                print(f"  {i}. {where}line {no}: {ref}")
                print(f"     Caption: {caption or '(missing)'}")
    if terms:
        print("\nFirst occurrence of abbreviations (check that each is spelled out or explained):")
        for key, (no, t, text) in sorted(terms.items(), key=lambda kv: kv[1][0]):
            print(f"  {path}:{no}: {t}: {text[:90]}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
