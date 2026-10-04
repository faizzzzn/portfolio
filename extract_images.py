"""Rebuild repo from artifact export: extract+compress data-URI images to assets/, rewrite index.html.
Usage: python3 extract_images.py /path/to/portfolio-v7.html
Run from ~/workspace/portfolio-site so assets/ lands beside index.html."""
import re, base64, hashlib, io, sys, os
from PIL import Image

src = sys.argv[1]
os.makedirs('assets', exist_ok=True)
html = open(src).read()
pat = re.compile(r'data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=]+)')
seen, counter = {}, [0]
def repl(m):
    typ, b64 = m.group(1), m.group(2)
    raw = base64.b64decode(b64)
    sha = hashlib.sha256(raw).hexdigest()
    if sha in seen: return seen[sha]
    counter[0] += 1
    im = Image.open(io.BytesIO(raw))
    w, h = im.size
    if max(w, h) > 1920:
        s = 1920 / max(w, h); im = im.resize((int(w*s), int(h*s)), Image.LANCZOS)
    if typ == 'png':
        if im.mode == 'P': im = im.convert('RGBA')
        fn = f'assets/img-{counter[0]:03d}.png'; im.save(fn, optimize=True)
    else:
        if im.mode in ('RGBA','LA','PA','P'): im = im.convert('RGB')
        fn = f'assets/img-{counter[0]:03d}.jpg'; im.save(fn, quality=82, optimize=True)
    seen[sha] = fn
    return fn
open('index.html','w').write(pat.sub(repl, html))
print(f"unique: {len(seen)}, refs: {counter[0]}")
