# GReinSS tutorial — slide build recipes
# Requires: marp-cli, python3, gh (for `just release`)
# The --html flag is mandatory: slides.md embeds raw HTML (<div> columns) and
# inline <svg> figures that are escaped to literal text without it.

marp   := "marp"
flags  := "--html --allow-local-files --theme-set themes/greinss.css"
pngdir := "_slidepngs"
gen    := "slides.gen.md"

# List available recipes
default:
    @just --list

# Splice assets/svg/*.svg fragments into slides.gen.md (the marp input)
build:
    python3 scripts/build_slides.py

# Compile the Marp deck to slides.pdf
pdf: build
    {{marp}} {{gen}} {{flags}} --pdf -o slides.pdf

# Rebuild the self-contained offline viewer slides.html (2x PNGs inlined as data URIs)
html: build
    rm -rf {{pngdir}} && mkdir -p {{pngdir}}
    {{marp}} {{gen}} {{flags}} --images png --image-scale 2 -o {{pngdir}}/s.png
    python3 scripts/make_offline_html.py {{pngdir}}
    rm -rf {{pngdir}}

# Render slides to per-slide PNGs in _chk/ for quick visual inspection (truncation checks)
check: build
    rm -rf _chk && mkdir -p _chk
    {{marp}} {{gen}} {{flags}} --images png --image-scale 1 -o _chk/s.png

# Extract speaker notes into the speaker-notes.md + print-ready speaker-notes.html handout
notes:
    python3 scripts/make_handout.py

# Build every deliverable: PDF deck, offline HTML, and speaker-notes handout
all: pdf html notes

# Creates tag {{tag}} at the default-branch HEAD and attaches slides.html + slides.pdf.
# Push commits first. Usage: just release v1.0
# Build all deliverables, then publish them as a GitHub Release (needs `gh`, authenticated).
release tag: all
    #!/usr/bin/env bash
    set -euo pipefail
    gh release create "{{tag}}" \
        --title "GReinSS tutorial {{tag}}" \
        --generate-notes \
        slides.html slides.pdf

# Re-splices assets/svg into slides.gen.md on every save of slides.md or an SVG.
# Live preview in the browser that reloads automatically as you edit slides.md.
preview: build
    #!/usr/bin/env bash
    python3 scripts/build_slides.py --watch &
    splicer=$!
    trap 'kill $splicer 2>/dev/null' EXIT
    {{marp}} -p {{gen}} {{flags}}

# Pre-train the graph model (~15 min on CPU) — writes assets/graph_*.{npz,pt}
pretrain epochs="3500":
    EPOCHS={{epochs}} python3 pretrain_graph.py

# Remove build scratch artifacts
clean:
    rm -rf {{pngdir}} _chk {{gen}}
