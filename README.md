# GReinSS Tutorial — NCI Spring School on Algorithmic Cancer Biology

A tutorial: **slide deck** + **live Jupyter notebook** for GReinSS
(Generative Reinforcement Learning of Structured States).

📽️ **View the slides online:** <https://elkebir-group.github.io/GReinSS-tutorial/> — hosted on
GitHub Pages (interactive deck, PDF, and offline single-file viewer).

## Contents

| File | What it is |
|---|---|
| `slides.md` | Marp slide deck (source). Speaker notes are in `<!-- HTML comments -->`; SVG figures are pulled in from `assets/svg/` via `<!-- include: -->` markers. |
| `slides.pdf` | Compiled deck (regenerate with the command below). |
| `slides.html` | **Self-contained** offline slide viewer (all images inlined; no network needed). Keys: `←`/`→` navigate, `N` toggle speaker notes, `F` fullscreen. |
| `speaker-notes.html` / `.md` | Speaker-notes handout (one block per slide) as print-ready styled HTML — print to PDF from a browser if you need paper — plus its Markdown source. |
| `GReinSS_demo.ipynb` | The live notebook you run during the talk. |
| `pretrain_setoff.py` | Prepares Demo 1 + Demo 2 set data and pre-trains the `\|U\|=1000` **off-policy** model. |
| `pretrain_graph.py` | Generates the graph sim + ground truth and pre-trains the graph model. |
| `assets/` | Paper figures (PNG) used by the deck + pre-trained graph model & data. `assets/svg/` holds the deck's inline SVG figures (spliced in at build time). |
| `code/` | **Git submodule** → [`elkebir-group/GReinSS`](https://github.com/elkebir-group/GReinSS) (the library the notebook imports). |
| `scripts/` | Helpers that regenerate `slides.html` and the `speaker-notes` handout. |

> **Note.** The generated outputs — `slides.html`, `slides.pdf`, and `speaker-notes.{html,md}` —
> are **not committed** (they're large binaries that churn on every edit; see `.gitignore`).
> Build them locally with `just all`, or download pre-built `slides.html`/`slides.pdf` from the
> [**Releases**](https://github.com/elkebir-group/GReinSS-tutorial/releases) page — the
> `Build & release slides` workflow attaches them to each `v*` tag.

## Setup

This repository uses a git submodule for the GReinSS library, so clone recursively:

```bash
git clone --recursive <this-repo-url>
# or, if already cloned without --recursive:
git submodule update --init
```

Install the Python dependencies (pinned in `requirements.txt`: numpy, scipy,
torch, matplotlib, + JupyterLab to run the notebook):

```bash
# with uv (recommended)
uv venv --python 3.10 && uv pip install -r requirements.txt

# or with pip
pip install -r requirements.txt
```

The notebook imports the library from the `code/` submodule and patches `torch.load`
(newer PyTorch defaults to `weights_only=True`, which cannot load these pickled models).

## Run the notebook

```bash
# from the repo root
jupyter notebook GReinSS_demo.ipynb      # or: jupyter lab
```

Run cells top to bottom. Timings on a laptop CPU:

- **Demo 1 (sets, `|U|=100`, trained live):** ~10 s to train + instant inference.
- **Demo 2 (scaling to `|U|=1000`, off-policy):** a short live on-policy run that
  *deliberately underperforms*, then loads the pre-trained off-policy model (`assets/setoff_model.pt`).
- **Demo 3 (graphs, pre-trained):** inference ~11 s (loads `assets/graph_model.pt`).
- **Intuition (toy):** instant.

### Re-generate the pre-trained models (optional)

```bash
python3 pretrain_setoff.py                # Demo 1 + Demo 2 data & off-policy model
                                          #   writes assets/set100_*.npz + assets/setoff_*.{npz,pt}
                                          #   (EPOCHS=1500 default)
EPOCHS=3500 python3 pretrain_graph.py     # Demo 3 graph model; ~15 min on CPU
                                          #   writes assets/graph_*.{npz,pt}
```

## Compile the slides

Recipes live in the `justfile` (run `just` or `just --list` to see them all):

```bash
just all        # rebuild slides.pdf + offline slides.html + speaker-notes handout
just pdf        # just the PDF deck
just html       # just the offline slides.html viewer
just notes      # just the speaker-notes.{md,html} handout
just preview    # live preview in the browser, reloading on save
just release v1.0  # build everything + publish a GitHub Release (via gh) with the artifacts
just pages       # build the site + publish it to GitHub Pages (gh-pages branch)
```

Equivalent raw commands, if you don't have `just`:

```bash
python3 scripts/build_slides.py                                    # slides.md -> slides.gen.md
marp slides.gen.md --html --pdf --allow-local-files -o slides.pdf  # PDF
marp -p slides.gen.md --html --allow-local-files                   # live preview
```

The `--html` flag is **mandatory**: the deck embeds raw HTML (`<div>` columns) and
inline `<svg>` figures that are escaped to literal text without it.

**Build step.** Large inline `<svg>` figures live as separate files in `assets/svg/`
and are referenced from `slides.md` by `<!-- include: assets/svg/NAME.svg -->` markers.
`scripts/build_slides.py` (run automatically by every `just` recipe) splices them back
into `slides.gen.md`, which is what marp actually renders — so the SVGs stay *inline*
and keep the deck's KaTeX fonts. Edit `slides.md` and the `assets/svg/*.svg` files;
`slides.gen.md` is a generated artifact (git-ignored). Run marp on `slides.md`
directly and the figures render as empty comments.

`just preview` handles this splice live: it runs `build_slides.py --watch` (a stdlib
mtime poller) alongside the marp preview, so saving `slides.md` or any `assets/svg/*.svg`
re-splices `slides.gen.md` and marp reloads automatically — no manual `just build`.

`slides.html` (self-contained offline viewer) and the `speaker-notes.*` handout are
regenerated from `slides.md` with the helper scripts in `scripts/` (wrapped by the
`just html` / `just notes` recipes). Note: a plain `marp --html` export still fetches
KaTeX math fonts from a CDN, so the committed `slides.html` instead embeds pixel-perfect
rendered slide images (fully offline).

## Publish to GitHub Pages

The deck is served at **<https://elkebir-group.github.io/GReinSS-tutorial/>**. Deployment is
done from a laptop via `just` (no CI step) — it builds the site and force-pushes it to the
`gh-pages` branch:

```bash
just pages
```

This runs `just all`, also builds the interactive `slides.presenter.html`, assembles a
`_site` (landing `pages/index.html` → `index.html`, the interactive deck → `deck.html`, the
offline viewer → `offline.html`, `slides.pdf`, and `assets/`), and force-pushes an orphan
commit to `gh-pages` (so that branch stays a single throwaway commit, no history bloat).

**One-time setup:** repo **Settings → Pages → Source = "Deploy from a branch", branch =
`gh-pages` / `root`.** Edit the landing page at `pages/index.html`.
