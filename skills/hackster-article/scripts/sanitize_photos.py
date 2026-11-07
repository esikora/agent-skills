# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Strip metadata (GPS location, time, camera, ...) from JPEG files and hide areas.

Removes all APP1 segments (EXIF incl. GPS, XMP), APP2 segments except the ICC color
profile (e.g. MPF, FlashPix), APP3 to APP15 (e.g. IPTC), comments, and any data appended
after the primary image (e.g. motion photo videos, HDR gain maps). The image data itself
is copied unchanged (no re-encoding). The EXIF orientation is preserved by writing a
minimal EXIF block that only contains the orientation tag.

Censoring (optional): areas listed in a censor file are pixelated, e.g. spoilers, names
or license plates. Only these photos are re-encoded, and only after their metadata has
been stripped; the result is stripped again. The censor file is a text file, one photo
per line, areas as x0,y0,x1,y1 in pixels of the upright image (as an image viewer shows
it); '#' starts a comment:

    workbench.jpg 1200,800,1400,950
    car.jpg 100,200,300,260 900,950,1000,1010

By default, censor.txt next to <src_dir> is used (e.g. doc/photos/censor.txt for
doc/photos/original). Keep it in version control so that every run applies the
censoring; a photo listed there but missing in <src_dir> is an error.

Every written file is checked afterwards; the script fails if any metadata is left.

Only JPEG files (*.jpg, *.jpeg) are processed. Use other tools for PNG, HEIC or videos
(e.g. ExifTool, or `ffmpeg -i in.mp4 -map_metadata -1 -c copy out.mp4`).

Usage: python sanitize_photos.py <src_dir> <dst_dir> [--censor <file>]
Writes stripped (and censored) copies of all JPEGs in <src_dir> to <dst_dir> (existing
files are overwritten; <dst_dir> must differ from <src_dir>). Check censored photos
visually: the hidden content must not be recognizable.
Requires Python 3 (standard library only); censoring needs Pillow in addition
(`uv run sanitize_photos.py ...` installs it automatically). Without Pillow, photos that
need censoring are skipped (not written, so no uncensored copy is created), all others
are stripped, and the script exits with an error.
"""
import io
import os
import struct
import sys


def read_orientation(exif: bytes):
    """Return the orientation from an APP1 EXIF payload, or None."""
    if not exif.startswith(b"Exif\x00\x00"):
        return None
    tiff = exif[6:]
    if len(tiff) < 8:
        return None
    endian = "<" if tiff[:2] == b"II" else ">"
    ifd0 = struct.unpack(endian + "I", tiff[4:8])[0]
    count = struct.unpack(endian + "H", tiff[ifd0:ifd0 + 2])[0]
    for i in range(count):
        entry = tiff[ifd0 + 2 + 12 * i: ifd0 + 14 + 12 * i]
        tag, typ = struct.unpack(endian + "HH", entry[:4])
        if tag == 0x0112 and typ == 3:
            return struct.unpack(endian + "H", entry[8:10])[0]
    return None


def minimal_exif(orientation: int) -> bytes:
    tiff = b"II*\x00" + struct.pack("<I", 8)
    tiff += struct.pack("<H", 1)
    tiff += struct.pack("<HHIHH", 0x0112, 3, 1, orientation, 0)
    tiff += struct.pack("<I", 0)
    payload = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + struct.pack(">H", len(payload) + 2) + payload


def segments(data: bytes):
    """Yield (marker, segment bytes) up to and including the scan data (SOS to EOI)."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    pos = 2
    while pos < len(data):
        if data[pos] != 0xFF:
            raise ValueError(f"bad marker at {pos}")
        marker = data[pos + 1]
        if marker == 0xD8 or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker == 0xDA:  # start of scan: entropy data up to EOI
            eoi = pos + 2 + length
            while True:
                eoi = data.index(b"\xff", eoi)
                nxt = data[eoi + 1]
                if nxt == 0xD9:
                    break
                eoi += 2 if (nxt == 0x00 or 0xD0 <= nxt <= 0xD7) else 1
            yield marker, data[pos:eoi + 2]
            return
        yield marker, data[pos:pos + 2 + length]
        pos += 2 + length


def is_metadata(marker: int, payload: bytes) -> bool:
    """True for segments that may contain metadata (everything except ICC and JFIF)."""
    if marker in (0xE1, 0xED, 0xFE):  # EXIF / XMP, IPTC, comment
        return True
    if marker == 0xE2:
        return not payload.startswith(b"ICC_PROFILE\x00")
    return 0xE3 <= marker <= 0xEF  # other vendor APP segments


def strip(data: bytes) -> bytes:
    kept = []
    orientation = None
    for marker, segment in segments(data):
        payload = segment[4:]
        if marker == 0xE1 and payload.startswith(b"Exif\x00\x00") and orientation is None:
            orientation = read_orientation(payload)
        if not is_metadata(marker, payload):
            kept.append(segment)
    out = b"\xff\xd8"
    if orientation and orientation != 1:
        out += minimal_exif(orientation)
    return out + b"".join(kept)


def metadata_problem(data: bytes):
    """Return a description of metadata left in a JPEG, or None.

    Allowed: JFIF, ICC profile and the minimal EXIF block written by minimal_exif().
    """
    for marker, segment in segments(data):
        payload = segment[4:]
        if marker == 0xE1 and payload.startswith(b"Exif\x00\x00") and \
                segment == minimal_exif(read_orientation(payload) or 1):
            continue
        if is_metadata(marker, payload):
            return f"metadata segment 0x{marker:02X} left"
    return None


def read_censor_file(path):
    """Return {file name: [(x0, y0, x1, y1), ...]} from a censor file."""
    areas = {}
    with open(path, encoding="utf-8") as f:
        for no, line in enumerate(f, start=1):
            parts = line.split("#", 1)[0].split()
            if not parts:
                continue
            if len(parts) < 2:
                sys.exit(f"{path}:{no}: expected '<file> x0,y0,x1,y1 [...]'")
            boxes = []
            for text in parts[1:]:
                try:
                    x0, y0, x1, y1 = (int(v) for v in text.split(","))
                except ValueError:
                    sys.exit(f"{path}:{no}: invalid area '{text}', expected x0,y0,x1,y1")
                if x1 <= x0 or y1 <= y0:
                    sys.exit(f"{path}:{no}: invalid area '{text}': x1/y1 must be greater")
                boxes.append((x0, y0, x1, y1))
            areas.setdefault(parts[0], []).extend(boxes)
    return areas


def pillow_available() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def censor(stripped: bytes, boxes) -> bytes:
    """Pixelate the boxes of an already stripped JPEG; return the re-encoded JPEG."""
    from PIL import Image, ImageOps
    img = Image.open(io.BytesIO(stripped))
    icc = img.info.get("icc_profile")
    img = ImageOps.exif_transpose(img).convert("RGB")
    for box in boxes:
        x0, y0 = max(0, box[0]), max(0, box[1])
        x1, y1 = min(img.width, box[2]), min(img.height, box[3])
        if x1 <= x0 or y1 <= y0:
            sys.exit(f"area {box} is outside the image ({img.width}x{img.height})")
        region = img.crop((x0, y0, x1, y1))
        w, h = region.size
        block = max(4, min(w, h) // 4)
        small = region.resize((max(1, w // block), max(1, h // block)), Image.BILINEAR)
        img.paste(small.resize((w, h), Image.NEAREST), (x0, y0))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=92, optimize=True, **({"icc_profile": icc} if icc else {}))
    return strip(out.getvalue())


def main():
    args = sys.argv[1:]
    censor_path = None
    if "--censor" in args:
        i = args.index("--censor")
        if i + 1 >= len(args):
            sys.exit(__doc__)
        censor_path = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    src, dst = args
    if os.path.abspath(src) == os.path.abspath(dst):
        sys.exit("Error: <dst_dir> must differ from <src_dir> (originals are kept).")
    if censor_path is not None and not os.path.isfile(censor_path):
        sys.exit(f"Error: censor file not found: {censor_path}")
    if censor_path is None:
        default =os.path.join(os.path.dirname(os.path.abspath(src)), "censor.txt")
        censor_path = default if os.path.isfile(default) else None
    areas = read_censor_file(censor_path) if censor_path else {}
    if censor_path:
        print(f"Censor areas from {censor_path}: {len(areas)} photo(s)")

    names = sorted(n for n in os.listdir(src) if n.lower().endswith((".jpg", ".jpeg")))
    missing = sorted(set(areas) - set(names))
    if missing:
        sys.exit(f"Error: censor file lists photo(s) not found in {src}: {', '.join(missing)}")

    can_censor = not areas or pillow_available()
    if not can_censor:
        print("Pillow is not installed: photos that need censoring are skipped "
              "(not written), all others are stripped.")

    os.makedirs(dst, exist_ok=True)
    failed, skipped = [], []
    for name in names:
        if name in areas and not can_censor:
            skipped.append(name)
            print(f"{name}: skipped (needs censoring)")
            continue
        with open(os.path.join(src, name), "rb") as f:
            data = f.read()
        out = strip(data)
        note = ""
        if name in areas:
            out = censor(out, areas[name])
            note = f", {len(areas[name])} area(s) censored (re-encoded)"
        problem = metadata_problem(out)
        if problem:
            failed.append(f"{name}: {problem}")
            continue
        with open(os.path.join(dst, name), "wb") as f:
            f.write(out)
        print(f"{name}: {len(data)} -> {len(out)} bytes{note}")
    errors = []
    if failed:
        errors.append("not written, metadata left:\n  " + "\n  ".join(failed))
    if skipped:
        errors.append(f"not written, censoring needs Pillow: {', '.join(skipped)}\n"
                      "  Run 'uv run sanitize_photos.py ...' or 'pip install pillow' "
                      "and run the script again.")
    if errors:
        sys.exit("Error: " + "\nError: ".join(errors))


if __name__ == "__main__":
    main()
