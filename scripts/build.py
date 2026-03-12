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


def main():
    os.makedirs(os.path.join(ROOT, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "source"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "images"), exist_ok=True)

    font = fontforge.open(SOURCE_PATH)
    font.familyname = "Mouse Marker"
    font.fullname = "Mouse Marker Regular"
    font.fontname = "MouseMarker-Regular"
    font.version = "1.0.0"
    font.copyright = "Copyright (C) 2026 Julius Burton. Dedicated to the public domain under CC0 1.0 Universal."
    font.appendSFNTName("English (US)", "Preferred Family", "Mouse Marker")
    font.appendSFNTName("English (US)", "Preferred Styles", "Regular")
    font.appendSFNTName("English (US)", "UniqueID", "Julius Burton: Mouse Marker Regular: 2026")
    font.appendSFNTName("English (US)", "License", "CC0 1.0 Universal")
    font.appendSFNTName("English (US)", "License URL", "https://creativecommons.org/publicdomain/zero/1.0/")

    font.save(SOURCE_PATH)
    font.generate(OTF_OUTPUT)
    font.generate(TTF_OUTPUT)
    font.close()

    if os.path.exists(WOFF2_OUTPUT):
        os.remove(WOFF2_OUTPUT)
    run(["woff2_compress", TTF_OUTPUT])

    run(
        [
            "magick",
            "-size",
            "1600x900",
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
            "+96+340",
            "abcdefghijklmnopqrstuvwxyz",
            "-annotate",
            "+96+460",
            "0123456789",
            "-annotate",
            "+96+620",
            "The quick brown fox jumped",
            "-annotate",
            "+96+730",
            "over the lazy dog",
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
            "Release v1.0.0   Designed by Julius Burton   CC0 1.0 Universal",
            SPECIMEN_OUTPUT,
        ]
    )


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
