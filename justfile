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

# Execute GReinSS_demo.ipynb end-to-end and save it in place WITH outputs (figures embedded).
# Uses whatever `jupyter` + kernel are on PATH (like the bare `python3`/`marp` calls above), so
# activate your env first. Needs the code/ submodule and assets/*.{npz,pt} present.
# Do NOT set MPLBACKEND=Agg — the Jupyter inline backend must stay active to embed the matplotlib PNGs.
notebook:
    jupyter nbconvert --to notebook --execute --inplace \
        --ExecutePreprocessor.timeout=1200 \
        GReinSS_demo.ipynb

# Publish a version: build everything, cut a GitHub Release with the artifacts, AND deploy the
# site to gh-pages — one command for both. Push commits first. Usage: just release v1.1
# Needs `gh` authenticated; force-pushes an orphan gh-pages commit (no history bloat).
# One-time Pages setup: repo Settings -> Pages -> Source = "Deploy from a branch", branch = gh-pages / root.
release tag: all
    #!/usr/bin/env bash
    set -euo pipefail
    # Interactive bespoke deck for the live site (not part of `just all`) — references assets/ by relative path.
    {{marp}} {{gen}} {{flags}} -o slides.presenter.html
    # 1) GitHub Release with the pre-built deck + executed notebook.
    gh release create "{{tag}}" \
        --title "GReinSS tutorial {{tag}}" \
        --generate-notes \
        slides.html slides.pdf GReinSS_demo.ipynb
    # 2) Deploy the site to the gh-pages branch (orphan commit each run).
    remote=$(git remote get-url origin)
    site=$(mktemp -d)
    cp pages/index.html      "$site/index.html"
    cp slides.presenter.html "$site/deck.html"
    cp slides.html           "$site/offline.html"
    cp slides.pdf            "$site/slides.pdf"
    cp -R assets             "$site/assets"
    touch "$site/.nojekyll"   # serve paths verbatim; skip Jekyll processing
    git -C "$site" init -q -b gh-pages
    git -C "$site" add -A
    git -C "$site" -c user.name="pages-deploy" -c user.email="pages@local" commit -qm "Deploy slides to GitHub Pages ({{tag}})"
    git -C "$site" push -f "$remote" gh-pages
    rm -rf "$site"
    echo "Released {{tag}} and deployed to gh-pages. If Pages isn't enabled yet: Settings -> Pages -> branch gh-pages / root."

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
