#!/usr/bin/env python3
"""Extract speaker notes from slides.md into a handout (speaker-notes.md + .html).
Run from anywhere: `python3 scripts/make_handout.py`  (paths are relative to tutorial/)."""
import os, re, html

TUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(TUT, 'slides.md')).read()

body = src.split('---', 2)[2] if src.startswith('---') else src
chunks = re.split(r'\n---\s*\n', body)

def title_of(ch):
    for line in ch.splitlines():
        m = re.match(r'^#{1,3}\s+(.*)', line.strip())
        if m:
            t = re.sub(r'[#*`$\\]', '', m.group(1))
            return re.sub(r'\{[^}]*\}', '', t).strip()
    return None

def notes_of(ch):
    out = []
    for m in re.finditer(r'<!--(.*?)-->', ch, re.DOTALL):
        c = m.group(1).strip()
        if c.startswith('_') or c.startswith('/*') or c.startswith('include:') or 'root' in c[:40] or len(c) < 30:
            continue
        out.append(re.sub(r'\s*\n\s*', ' ', c).strip())
    return out

slides, n = [], 0
for ch in chunks:
    if '<style>' in ch:
        ch = ch.split('</style>', 1)[-1]
    t, nt = title_of(ch), notes_of(ch)
    if t is None and not nt:
        continue
    n += 1
    slides.append((n, t or '(untitled)', nt))

# --- Markdown ---
md = ['# GReinSS Tutorial — Speaker Notes', '',
      '*NCI Spring School on Algorithmic Cancer Biology*', '',
      'One block per slide. → NOTEBOOK slides are the live-demo hand-offs.', '', '---', '']
for num, title, notes in slides:
    md.append(f'### {num}. {title}')
    for para in (notes or ['*(no notes)*']):
        md += ['', para]
    md.append('')
open(os.path.join(TUT, 'speaker-notes.md'), 'w').write('\n'.join(md))

# --- print-ready HTML ---
cards = []
for num, title, notes in slides:
    nh = ''.join(f'<p>{html.escape(p)}</p>' for p in notes) or '<p class="none">— no notes —</p>'
    cards.append(f'<section class="card"><div class="num">{num}</div>'
                 f'<div class="body"><h2>{html.escape(title)}</h2>{nh}</div></section>')
page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<title>GReinSS Tutorial — Speaker Notes</title><style>'
        ':root{--blue:#13294B;--orange:#FF5F05;--muted:#5b6672;}*{box-sizing:border-box;}'
        'body{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;color:#1b1f24;'
        'max-width:820px;margin:0 auto;padding:40px 32px;line-height:1.5;}'
        'header{border-bottom:3px solid var(--orange);margin-bottom:8px;padding-bottom:12px;}'
        'header h1{color:var(--blue);margin:0 0 4px;font-size:28px;}'
        'header p{color:var(--muted);margin:0;font-size:14px;}'
        '.card{display:flex;gap:16px;padding:14px 0;border-bottom:1px solid #e4e9ef;'
        'break-inside:avoid;page-break-inside:avoid;}'
        '.num{flex:0 0 40px;height:40px;border-radius:50%;background:var(--blue);color:#fff;'
        'font-weight:700;display:flex;align-items:center;justify-content:center;}'
        '.body h2{color:var(--blue);font-size:18px;margin:6px 0;}'
        '.body p{margin:6px 0;font-size:14.5px;}.body p.none{color:#9aa4b0;font-style:italic;}'
        '@media print{body{max-width:none;}.num{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}'
        '</style></head><body><header><h1>GReinSS Tutorial — Speaker Notes</h1>'
        '<p>NCI Spring School on Algorithmic Cancer Biology · '
        '→ NOTEBOOK = live-demo hand-off</p></header>' + ''.join(cards) + '</body></html>')
open(os.path.join(TUT, 'speaker-notes.html'), 'w').write(page)
print(f'wrote speaker-notes.md and speaker-notes.html ({len(slides)} slides)')
print('for a PDF: open speaker-notes.html in a browser and Print -> Save as PDF')
