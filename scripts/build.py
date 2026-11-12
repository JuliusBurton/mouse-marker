import os
import subprocess
import sys
import unicodedata

import fontforge


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE_PATH = os.path.join(ROOT, "source", "Mouse-Marker-source.sfd")
OTF_OUTPUT = os.path.join(ROOT, "fonts", "Mouse-Marker-Regular.otf")
TTF_OUTPUT = os.path.join(ROOT, "fonts", "Mouse-Marker-Regular.ttf")
WOFF2_OUTPUT = os.path.join(ROOT, "fonts", "Mouse-Marker-Regular.woff2")
SPECIMEN_OUTPUT = os.path.join(ROOT, "images", "specimen.png")
SPECIMEN_META_FONT = "/System/Library/Fonts/Supplemental/Verdana.ttf"


def run(command):
    subprocess.run(command, check=True)


def glyph_signature(glyph):
    return tuple(
        tuple((round(point.x, 6), round(point.y, 6), point.on_curve) for point in contour)
        for contour in glyph.foreground
    )


def remaining_specimen_groups(font):
    shown_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    shown_codepoints = {ord(char) for char in shown_text}
    seen_codepoints = set()
    accented = []
    other = []
    notdef_signature = glyph_signature(font[".notdef"])
    accent_keywords = (
        "ACCENT",
        "ACUTE",
        "BREVE",
        "CARON",
        "CEDILLA",
        "CIRCUMFLEX",
        "COMMA BELOW",
        "DIAERESIS",
        "DOUBLE ACUTE",
        "GRAVE",
        "MACRON",
        "OGONEK",
        "TILDE",
    )

    for glyph in font.glyphs():
        codepoint = glyph.unicode
        if (
            codepoint < 0x21
            or codepoint in shown_codepoints
            or codepoint in seen_codepoints
            or glyph_signature(glyph) == notdef_signature
        ):
            continue
        char = chr(codepoint)
        if not char.isprintable() or char.isspace():
            continue
        seen_codepoints.add(codepoint)
        display_char = char.replace("%", "%%")
        unicode_name = unicodedata.name(char, "")
        item = (display_char, glyph.width, codepoint, unicode_name, char)
        if "LATIN" in unicode_name or any(
            keyword in unicode_name for keyword in accent_keywords
        ):
            accented.append(item)
        else:
            other.append(item)

    accent_order = (
        "RING ABOVE",
        "ACUTE",
        "DIAERESIS",
        "GRAVE",
        "CIRCUMFLEX",
        "TILDE",
        "MACRON",
        "BREVE",
        "CARON",
        "CEDILLA",
        "COMMA BELOW",
        "DOUBLE ACUTE",
        "OGONEK",
    )

    def accent_key(item):
        _, _, codepoint, unicode_name, char = item
        normalized = unicodedata.normalize("NFKD", char)
        base = "".join(
            part for part in normalized if part.isalpha() and not unicodedata.combining(part)
        ).casefold()
        if "LETTER AE" in unicode_name:
            base = "a"
        elif "LETTER OE" in unicode_name:
            base = "o"
        elif "SHARP S" in unicode_name:
            base = "s"
        elif "DOTLESS I" in unicode_name:
            base = "i"
        elif "F WITH HOOK" in unicode_name:
            base = "f"
        accent_rank = next(
            (index for index, marker in enumerate(accent_order) if marker in unicode_name),
            len(accent_order),
        )
        return (
            base or "{",
            0 if char.islower() else 1,
            accent_rank,
            codepoint,
        )

    accented.sort(key=accent_key)

    def rows(items, max_width=20500):
        result = []
        current = []
        current_width = 0
        for item in items:
            display_char, width, _, _, _ = item
            if current and current_width + width > max_width:
                result.append("".join(current))
                current = []
                current_width = 0
            current.append(display_char)
            current_width += width
        if current:
            result.append("".join(current))
        return result

    return rows(accented), rows(other)


def main():
    os.makedirs(os.path.join(ROOT, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "source"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "images"), exist_ok=True)

    font = fontforge.open(SOURCE_PATH)
    font.familyname = "Mouse Marker"
    font.fullname = "Mouse Marker Regular"
    font.fontname = "MouseMarker-Regular"
    font.version = "1.1.0"
    font.copyright = "Copyright (C) 2026 Julius Burton. Dedicated to the public domain under CC0 1.0 Universal."
    font.appendSFNTName("English (US)", "Preferred Family", "Mouse Marker")
    font.appendSFNTName("English (US)", "Preferred Styles", "Regular")
    font.appendSFNTName("English (US)", "UniqueID", "Julius Burton: Mouse Marker Regular: 2026")
    font.appendSFNTName("English (US)", "License", "CC0 1.0 Universal")
    font.appendSFNTName("English (US)", "License URL", "https://creativecommons.org/publicdomain/zero/1.0/")

    font.save(SOURCE_PATH)
    font.generate(OTF_OUTPUT)
    font.generate(TTF_OUTPUT)
    accented_rows, other_rows = remaining_specimen_groups(font)
    font.close()

    if os.path.exists(WOFF2_OUTPUT):
        os.remove(WOFF2_OUTPUT)
    run(["woff2_compress", TTF_OUTPUT])

    pangram_start = 550
    accent_start = 800
    accent_step = 92
    other_start = accent_start + len(accented_rows) * accent_step + 100
    image_height = other_start + len(other_rows) * accent_step + 100

    specimen_command = [
            "magick",
            "-size",
            f"1600x{image_height}",
            "xc:#ffffff",
            "-fill",
            "#000000",
            "-font",
            OTF_OUTPUT,
            "-pointsize",
            "64",
            "-gravity",
            "northwest",
            "-annotate",
            "+96+220",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "-annotate",
            "+96+330",
            "abcdefghijklmnopqrstuvwxyz",
            "-annotate",
            "+96+440",
            "0123456789",
            "-annotate",
            f"+96+{pangram_start}",
            "The quick brown fox jumped",
            "-annotate",
            f"+96+{pangram_start + 110}",
            "over the lazy dog",
            "-pointsize",
            "64",
        ]

    for index, row in enumerate(accented_rows):
        specimen_command.extend(
            [
                "-annotate",
                f"+96+{accent_start + index * accent_step}",
                row,
            ]
        )

    for index, row in enumerate(other_rows):
        specimen_command.extend(
            [
                "-annotate",
                f"+96+{other_start + index * accent_step}",
                row,
            ]
        )

    specimen_command.extend(
        [
            "-font",
            SPECIMEN_META_FONT,
            "-pointsize",
            "42",
            "-fill",
            "#000000",
            "-annotate",
            "+96+70",
            "Mouse Marker",
            "-pointsize",
            "20",
            "-fill",
            "#000000",
            "-annotate",
            "+96+120",
            "Release v1.1.0   Designed by Julius Burton   CC0 1.0 Universal",
            SPECIMEN_OUTPUT,
        ]
    )
    run(specimen_command)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
