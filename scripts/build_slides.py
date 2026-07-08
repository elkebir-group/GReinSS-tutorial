#!/usr/bin/env python3
"""Expand `<!-- include: PATH -->` markers in slides.md into slides.gen.md.

Large inline <svg> figures live in separate files under assets/svg/ for
readability; this preprocessor splices them back into a single self-contained
markdown that marp renders (so the SVGs stay truly inline and keep the page's
KaTeX fonts). The justfile runs this before every marp invocation.

Usage:  python3 scripts/build_slides.py            # splice once
        python3 scripts/build_slides.py --watch    # re-splice on every save (for live preview)
"""
import glob
import os
import re
import sys
import time

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


def build():
    text = open(SRC).read()
    n = len(MARKER.findall(text))
    open(OUT, "w").write(expand(text))
    print(f"build_slides: expanded {n} include(s) -> {os.path.relpath(OUT, TUT)}", flush=True)


def sources():
    """Files whose edits should trigger a re-splice: slides.md + every SVG fragment."""
    return [SRC] + sorted(glob.glob(os.path.join(TUT, "assets", "svg", "*.svg")))


def watch():
    """Poll slides.md + assets/svg/*.svg and re-splice on any change (stdlib only)."""
    build()
    print("build_slides: watching slides.md + assets/svg/ for changes (Ctrl-C to stop)", flush=True)
    stamps = {f: os.path.getmtime(f) for f in sources()}
    while True:
        time.sleep(0.4)
        now = {f: os.path.getmtime(f) for f in sources() if os.path.exists(f)}
        if now != stamps:
            stamps = now
            try:
                build()  # marp -p is watching slides.gen.md, so it reloads once we rewrite it
            except SystemExit as e:
                print(e)  # e.g. a missing include mid-edit — report but keep watching


if __name__ == "__main__":
    watch() if "--watch" in sys.argv[1:] else build()
