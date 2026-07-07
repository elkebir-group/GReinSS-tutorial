#!/usr/bin/env python3
"""Expand `<!-- include: PATH -->` markers in slides.md into slides.gen.md.

Large inline <svg> figures live in separate files under assets/svg/ for
readability; this preprocessor splices them back into a single self-contained
markdown that marp renders (so the SVGs stay truly inline and keep the page's
KaTeX fonts). The justfile runs this before every marp invocation.

Usage:  python3 scripts/build_slides.py
"""
import os
import re
import sys

TUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(TUT, "slides.md")
OUT = os.path.join(TUT, "slides.gen.md")

MARKER = re.compile(r"<!--\s*include:\s*(\S+?)\s*-->")


def expand(text):
    def repl(m):
        rel = m.group(1)
        path = os.path.join(TUT, rel)
        if not os.path.isfile(path):
            sys.exit(f"build_slides: missing include target: {rel}")
        return open(path).read().rstrip("\n")

    return MARKER.sub(repl, text)


def main():
    text = open(SRC).read()
    n = len(MARKER.findall(text))
    open(OUT, "w").write(expand(text))
    print(f"build_slides: expanded {n} include(s) -> {os.path.relpath(OUT, TUT)}")


if __name__ == "__main__":
    main()
