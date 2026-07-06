#!/usr/bin/env python3
"""Build a fully self-contained slides.html: render slides.md to PNGs with Marp,
then inline them (data URIs) into a keyboard-navigable viewer with a speaker-notes panel.

Usage (from tutorial/):
    marp slides.md --images png --image-scale 2 --allow-local-files -o /tmp/s/s.png
    python3 scripts/make_offline_html.py /tmp/s
The argument is the directory holding the rendered s.NNN.png files.
"""
import base64, os, re, json, glob, sys

TUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TUT, '_slidepngs')

imgs = ['data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
        for p in sorted(glob.glob(os.path.join(SL, 's.*.png')))]
if not imgs:
    sys.exit(f'no s.*.png found in {SL} — render with marp first (see module docstring)')

# --- speaker notes (same parse as make_handout) ---
src = open(os.path.join(TUT, 'slides.md')).read()
body = src.split('---', 2)[2] if src.startswith('---') else src
chunks = re.split(r'\n---\s*\n', body)
def title_of(ch):
    for line in ch.splitlines():
        m = re.match(r'^#{1,3}\s+(.*)', line.strip())
        if m:
            return re.sub(r'\{[^}]*\}', '', re.sub(r'[#*`$\\]', '', m.group(1))).strip()
    return ''
def notes_of(ch):
    o = []
    for m in re.finditer(r'<!--(.*?)-->', ch, re.DOTALL):
        c = m.group(1).strip()
        if c.startswith('_') or c.startswith('/*') or 'root' in c[:40] or len(c) < 30:
            continue
        o.append(re.sub(r'\s*\n\s*', ' ', c).strip())
    return ' '.join(o)
notes = []
for ch in chunks:
    if '<style>' in ch:
        ch = ch.split('</style>', 1)[-1]
    t, nt = title_of(ch), notes_of(ch)
    if not t and not nt:
        continue
    notes.append({'title': t, 'note': nt})
while len(notes) < len(imgs): notes.append({'title': '', 'note': ''})
notes = notes[:len(imgs)]

DATA = json.dumps({'imgs': imgs, 'notes': notes})
page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GReinSS Tutorial — Slides</title><style>
html,body{margin:0;height:100%;background:#0c1420;overflow:hidden;font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;}
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;}
#slide{max-width:100vw;max-height:100vh;box-shadow:0 8px 40px rgba(0,0,0,.6);}
#bar{position:fixed;left:0;right:0;bottom:0;height:4px;background:#1c2a3a;}
#prog{height:100%;width:0;background:#FF5F05;transition:width .15s;}
#counter{position:fixed;bottom:12px;right:16px;color:#9fb0c3;font-size:13px;background:rgba(12,20,32,.6);padding:3px 10px;border-radius:12px;user-select:none;}
#hint{position:fixed;bottom:12px;left:16px;color:#6b7c90;font-size:12px;user-select:none;}
.zone{position:fixed;top:0;bottom:0;width:22%;cursor:pointer;}#zL{left:0;}#zR{right:0;}
#notes{position:fixed;left:0;right:0;bottom:0;max-height:42vh;overflow:auto;background:rgba(10,17,28,.97);color:#e8eef5;border-top:3px solid #FF5F05;padding:18px 26px;transform:translateY(100%);transition:transform .2s;box-sizing:border-box;}
#notes.show{transform:translateY(0);}#notes h3{margin:0 0 8px;color:#ffb38a;font-size:16px;}
#notes p{margin:0;font-size:15px;line-height:1.55;color:#dbe4ef;}#notes .meta{color:#7d8da0;font-size:12px;margin-top:10px;}
</style></head><body>
<div id="stage"><img id="slide" alt="slide"></div>
<div id="zL" class="zone" onclick="go(-1)"></div><div id="zR" class="zone" onclick="go(1)"></div>
<div id="bar"><div id="prog"></div></div><div id="counter"></div>
<div id="hint">&larr; &rarr; navigate &middot; N notes &middot; F fullscreen</div>
<div id="notes"><h3 id="nTitle"></h3><p id="nBody"></p><div class="meta">Press N to hide</div></div>
<script>
const D=''' + DATA + ''';let i=0;
const img=document.getElementById('slide'),prog=document.getElementById('prog'),counter=document.getElementById('counter'),
notes=document.getElementById('notes'),nTitle=document.getElementById('nTitle'),nBody=document.getElementById('nBody');
function render(){img.src=D.imgs[i];counter.textContent=(i+1)+' / '+D.imgs.length;prog.style.width=((i+1)/D.imgs.length*100)+'%';
const n=D.notes[i]||{};nTitle.textContent=(i+1)+'. '+(n.title||'');nBody.textContent=n.note||'— no notes for this slide —';}
function go(d){i=Math.min(D.imgs.length-1,Math.max(0,i+d));render();}
document.addEventListener('keydown',e=>{
if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){go(1);e.preventDefault();}
else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){go(-1);e.preventDefault();}
else if(e.key==='Home'){i=0;render();}else if(e.key==='End'){i=D.imgs.length-1;render();}
else if(e.key==='n'||e.key==='N'){notes.classList.toggle('show');}
else if(e.key==='f'||e.key==='F'){if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen();}});
render();</script></body></html>'''
out = os.path.join(TUT, 'slides.html')
open(out, 'w').write(page)
print(f'wrote {out}  ({round(len(page)/1e6,2)} MB, {len(imgs)} slides)')
