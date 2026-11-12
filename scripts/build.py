import os
import subprocess
import sys

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


def remaining_specimen_rows(font, row_length=24):
    shown_text = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "ÁÉÍÓÚáéíóú"
        "ÄËÏÖÜäëïöü"
        "ÂÊÎÔÛâêîôû"
        "ÃÑÕÇçãñõ"
    )
    shown_codepoints = {ord(char) for char in shown_text}
    seen_codepoints = set()
    remaining = []
    notdef_signature = glyph_signature(font[".notdef"])

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
        remaining.append(char.replace("%", "%%"))

    return [
        "".join(remaining[index : index + row_length])
        for index in range(0, len(remaining), row_length)
    ]


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
    additional_rows = remaining_specimen_rows(font)
    font.close()

    if os.path.exists(WOFF2_OUTPUT):
        os.remove(WOFF2_OUTPUT)
    run(["woff2_compress", TTF_OUTPUT])

    specimen_command = [
            "magick",
            "-size",
            f"1600x{1390 + len(additional_rows) * 86}",
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
            "+96+550",
            "ÁÉÍÓÚ áéíóú",
            "-annotate",
            "+96+660",
            "ÄËÏÖÜ äëïöü",
            "-annotate",
            "+96+770",
            "ÂÊÎÔÛ âêîôû",
            "-annotate",
            "+96+880",
            "ÃÑÕ Çç ãñõ",
            "-annotate",
            "+96+1010",
            "The quick brown fox jumped",
            "-annotate",
            "+96+1120",
            "over the lazy dog",
            "-font",
            SPECIMEN_META_FONT,
            "-pointsize",
            "24",
            "-fill",
            "#000000",
            "-annotate",
            "+96+1240",
            "Additional encoded characters",
            "-font",
            OTF_OUTPUT,
            "-pointsize",
            "44",
        ]

    for index, row in enumerate(additional_rows):
        specimen_command.extend(
            [
                "-annotate",
                f"+96+{1300 + index * 86}",
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
