# GReinSS tutorial — slide build recipes
# Requires: marp-cli, pandoc (+ xelatex for the notes PDF), python3
# The --html flag is mandatory: slides.md embeds raw HTML (<div> columns) and
# inline <svg> figures that are escaped to literal text without it.

marp   := "marp"
flags  := "--html --allow-local-files"
pngdir := "_slidepngs"

# List available recipes
default:
    @just --list

# Compile the Marp deck to slides.pdf
pdf:
    {{marp}} slides.md {{flags}} --pdf -o slides.pdf

# Rebuild the self-contained offline viewer slides.html (2x PNGs inlined as data URIs)
html:
    rm -rf {{pngdir}} && mkdir -p {{pngdir}}
    {{marp}} slides.md {{flags}} --images png --image-scale 2 -o {{pngdir}}/s.png
    python3 scripts/make_offline_html.py {{pngdir}}
    rm -rf {{pngdir}}

# Render slides to per-slide PNGs in _chk/ for quick visual inspection (truncation checks)
check:
    rm -rf _chk && mkdir -p _chk
    {{marp}} slides.md {{flags}} --images png --image-scale 1 -o _chk/s.png

# Extract speaker notes to speaker-notes.md/.html and build speaker-notes.pdf
notes:
    python3 scripts/make_handout.py
    sed -e 's/→/$\\rightarrow$/g' -e 's/ℝ/$\\mathbb{R}$/g' speaker-notes.md > .notes.tmp.md
    pandoc .notes.tmp.md -o speaker-notes.pdf --pdf-engine=xelatex -V mainfont="Helvetica Neue"
    rm -f .notes.tmp.md

# Build every deliverable: PDF deck, offline HTML, and speaker-notes handout
all: pdf html notes

# Live preview in the browser, reloading on each save
preview:
    {{marp}} -p slides.md {{flags}}

# Pre-train the graph model (~15 min on CPU) — writes assets/graph_*.{npz,pt}
pretrain epochs="3500":
    EPOCHS={{epochs}} python3 pretrain_graph.py

# Remove build scratch artifacts
clean:
    rm -rf {{pngdir}} _chk .notes.tmp.md
