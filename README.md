# GReinSS Tutorial — NCI Spring School on Algorithmic Cancer Biology

A tutorial: **slide deck** + **live Jupyter notebook** for GReinSS
(Generative Reinforcement Learning of Structured States).

## Contents

| File | What it is |
|---|---|
| `slides.md` | Marp slide deck (source). Speaker notes are in `<!-- HTML comments -->`; SVG figures are pulled in from `assets/svg/` via `<!-- include: -->` markers. |
| `slides.pdf` | Compiled deck (regenerate with the command below). |
| `slides.html` | **Self-contained** offline slide viewer (all images inlined; no network needed). Keys: `←`/`→` navigate, `N` toggle speaker notes, `F` fullscreen. |
| `speaker-notes.pdf` | Printable speaker-notes handout (one block per slide). |
| `speaker-notes.html` / `.md` | Same handout as styled HTML (print to PDF from a browser) and Markdown source. |
| `GReinSS_demo.ipynb` | The live notebook you run during the talk. |
| `GReinSS_demo_executed.ipynb` | Pre-run copy with outputs — **fallback** if live execution fails. |
| `pretrain_graph.py` | Generates the graph sim + ground truth and pre-trains the graph model. |
| `assets/` | Paper figures (PNG) used by the deck + pre-trained graph model & data. `assets/svg/` holds the deck's inline SVG figures (spliced in at build time). |
| `code/` | **Git submodule** → [`elkebir-group/GReinSS`](https://github.com/elkebir-group/GReinSS) (the library the notebook imports). |
| `scripts/` | Helpers that regenerate `slides.html` and the `speaker-notes` handout. |

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

- **Demo 1 (sets, trained live):** ~9 s to train + instant inference.
- **Intuition (toy):** instant.
- **Demo 2 (graphs, pre-trained):** inference ~11 s (loads `assets/graph_model.pt`).

### Re-generate the pre-trained graph model (optional)

```bash
EPOCHS=3500 python3 pretrain_graph.py    # ~15 min on CPU; writes assets/graph_*.{npz,pt}
```

## Compile the slides

Recipes live in the `justfile` (run `just` or `just --list` to see them all):

```bash
just all        # rebuild slides.pdf + offline slides.html + speaker-notes handout
just pdf        # just the PDF deck
just html       # just the offline slides.html viewer
just notes      # just the speaker-notes.{md,html,pdf} handout
just preview    # live preview in the browser, reloading on save
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

`slides.html` (self-contained offline viewer) and the `speaker-notes.*` handout are
regenerated from `slides.md` with the helper scripts in `scripts/` (wrapped by the
`just html` / `just notes` recipes). Note: a plain `marp --html` export still fetches
KaTeX math fonts from a CDN, so the committed `slides.html` instead embeds pixel-perfect
rendered slide images (fully offline).

## Suggested flow

| Time | Slides | Notes |
|---|---|---|
| 0–4 min | Motivation → two problems | Frame with cancer states: phylogenies, CNVs, isoforms. |
| 4–9 min | Why usual tools fail → the idea → **the one equation** | The theorem is the crux; keep to intuition. |
| 9–12 min | Toy intuition slide | Denominator = "reward shrinks as it succeeds." |
| 12–18 min | **Notebook Demo 1** (sets, live) | Train live; show likelihood curve + denoising vs thresholding. |
| 18–21 min | Simulation results | GReinSS wins where observations are information-poor / large. |
| 21–25 min | **Notebook Demo 2** (graphs) + toy cell | Show F1 0.96 reconstruction; run the toy PG-vs-GReinSS cell. |
| 25–29 min | RNA isoforms vs RSEM → CloMu/CNRein → recipe | The real-data payoff for this audience. |
| 29–30 min | Recap / Q&A | The 4-line recipe. |

## Live-demo tips

- **Do a dry run** on the exact machine + kernel you'll present with.
- Keep `GReinSS_demo_executed.ipynb` open in a second tab as a fallback.
- Demo 1 uses a *self-generated* set simulation with known ground truth (universe 20,
  σ = 0.5, module structure), so you can show real F1 gains over naive thresholding
  (~0.91 vs ~0.80) — the same API as the README's set example.
- If inference in Demo 2 feels slow, it's the 100k-trajectory sampler in `simpleInference`;
  that's expected (~11 s) and worth narrating as "sampling states to solve the inference problem."
