LABEL = "16"
TITLE = "The Paper"
DATE = "2026-06-12"
PAGE = "16_the_paper.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## ptol writes its own papers: SVG (path), PPM (field), HTML (both)
`ptol -s/-b/-H dir <prompt>` write `ptol_<slug>_<unix>.{svg,ppm,html}`. The page specifies: 16 spokes at θ_k = 2πk/16 − π/2; a gold ZD marker at the centre; a dashed σ=½ ring at half-radius; red/blue dots by sign; a green polyline visiting every spoke once in ascending |amplitude|; a 64×64 PPM in a 4×4 grid of 16×16 cells.
Generate the papers into a scratch directory (HOME redirected) and check each against its geometry."""),
("code", """import subprocess, re, glob
d = scratch("paper_"); os.makedirs(os.path.join(d, ".ptolemy"), exist_ok=True)
env = dict(os.environ, HOME=d)
prompt = "the void named itself at sigma equals half"
ptol = os.path.join(VAPMIP, "PtolC", "ptol")
for flag in ("-s", "-b", "-H"):
    subprocess.run([ptol, flag, d, prompt], capture_output=True, text=True, env=env, timeout=60)
    time.sleep(1.05)   # filenames carry a Unix timestamp
files = sorted(os.listdir(d)); print(files)
svg = next(f for f in files if f.endswith(".svg")); ppm = next(f for f in files if f.endswith(".ppm") and not f.endswith(".png")); html = next(f for f in files if f.endswith(".html"))
L.check("three paper formats are written, titled by prompt slug + timestamp", svg.startswith("ptol_the_void_named_itself_") and ppm.startswith("ptol_the_void") and html.endswith(".html"))
S = open(os.path.join(d, svg), encoding="utf-8").read()
r = ptol_raw(prompt, eye="H", home=d); xs = np.array(r["scalars"])"""),
("code", """pts = re.search(r'polyline[^>]*points="([^"]+)"', S).group(1).split()
pts = [tuple(map(float, p.split(","))) for p in pts]
cx, cy = pts[0]
print(f"polyline: {len(pts)} points; centre ({cx}, {cy})")
L.check("polyline starts at the ZD centre and visits 16 spokes (17 points)", len(pts) == 17)
ang = [math.atan2(py - cy, px - cx) for px, py in pts[1:]]
rad = [math.hypot(px - cx, py - cy) for px, py in pts[1:]]
spoke = [int(round(((a + math.pi/2) / (2*math.pi)) * 16)) % 16 for a in ang]
order_svg = spoke
order_x = sorted(range(16), key=lambda k: abs(xs[k]))
print("spiral order drawn in the SVG :", order_svg)
print("order by ascending |scalar|  :", order_x)
L.check("every spoke is visited exactly once", sorted(order_svg) == list(range(16)))
L.check("SVG spiral order == ascending |amplitude| of ptol -r scalars", order_svg == order_x)
L.check("page's quoted order e4→e3→e1→e0→e2→e8→e5→e6→e15→e14→e7→e9→e13→e10→e12→e11", order_svg == [4,3,1,0,2,8,5,6,15,14,7,9,13,10,12,11], f"drawn order now: {order_svg} — the page's order was recorded in 2026-06 for this prompt; the geometry (ascending |x|) is unchanged, the scalars are not")
L.check("radii ascend along the path (ZD → great circle)", all(rad[i] <= rad[i+1] + 1e-6 for i in range(15)))
ring = re.search(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"[^>]*stroke-dasharray', S)
rim = max(float(m) for m in re.findall(r'<circle[^>]*r="([\d.]+)" fill="none" stroke="#222"', S))
L.check("dashed σ=½ ring at exactly half the rim radius", ring is not None and abs(float(ring.group(3)) - rim/2) < 1e-6, f"ring r={ring.group(3) if ring else None}, rim r={rim}")
L.check("a 'ZD' marker is drawn at the centre", ">ZD<" in S)
labels = re.findall(r">([A-Za-z\\-']{3,})</text>", S)
print("word shadows printed on the spoke tips (from ptol's resident store):", labels[:8])
L.check("spoke tips carry words (the shadow) as well as primes", len(labels) >= 3)"""),
("code", """raw = open(os.path.join(d, ppm), "rb").read()
hdr = raw[:raw.index(b"255")+4]
print("PPM header:", hdr, "  total bytes:", len(raw))
L.check("PPM is 64×64 (P6, 255): 12288 pixel bytes", hdr.startswith(b"P6") and b"64 64" in hdr and len(raw) - len(hdr) == 64*64*3)
img = np.frombuffer(raw[len(hdr):], np.uint8).reshape(64, 64, 3).astype(float)
cells = np.array([[img[16*i:16*i+16, 16*j:16*j+16].mean(axis=(0,1)) for j in range(4)] for i in range(4)])    # 4×4 cells × RGB
cell_red, cell_blue = cells[:, :, 0].flatten(), cells[:, :, 2].flatten()
sign_from_cells = np.where(cell_red >= cell_blue, 1, -1)
agree = int((sign_from_cells == np.sign(xs)).sum())
print("cell sign agreement with ptol -r scalars:", agree, "of 16")
L.check("cell colours encode sign (red + / blue −) of the 16 scalars", agree >= 14, f"{agree}/16 cells")"""),
("md", """## Geometry-first OCR: image → 16 scalars → same pipeline
`ptol -i file` resamples to 16×1 (ImageMagick), takes `v = ±brightness` (sign from red-vs-blue). Round trip: encode a word's 16 scalars as a 16×1 image the way `read_image_scalars` decodes it, hand it back, and see whether the scalars return."""),
("code", """w = "threshold"
xw = np.array(ptol_raw(w, eye="H", home=d)["scalars"])
mx = np.abs(xw).max()
img16 = os.path.join(d, "word16.ppm")
with open(img16, "wb") as fh:
    fh.write(b"P6\\n16 1\\n255\\n")
    for v in xw/mx:                                  # brightness = |v|; red for +, blue for −
        b = int(round(abs(v)*255)); fh.write(bytes((b, 0, 0) if v >= 0 else (0, 0, b)))
out = subprocess.run([ptol, "-r", "-i", img16], capture_output=True, text=True, env=env, timeout=60)
vals = [float(l) for l in out.stdout.splitlines()[:16] if re.fullmatch(r"[+-]?\\d+\\.\\d+", l.strip())]
L.check("`ptol -i` reads a 16×1 image and returns 16 scalars", len(vals) == 16, "ptol said: " + out.stderr.strip().splitlines()[0][-110:] if out.stderr.strip() else "")
# root cause, reproduced: ptol.c pipes ImageMagick's txt: output through  grep -v '#'  — but every pixel line of txt: carries a '#RRGGBB' field
txt = subprocess.run(["convert", img16, "-colorspace", "sRGB", "-resize", "16x1!", "-depth", "8", "txt:-"], capture_output=True, text=True).stdout
before = [l for l in txt.splitlines()]
after = subprocess.run(["grep", "-v", "#"], input=txt, capture_output=True, text=True).stdout.splitlines()
print(f"ImageMagick txt: lines {len(before)} (1 header + 16 pixels) → after `grep -v '#'`: {len(after)} lines")
L.check("the `grep -v '#'` in ptol.c's read_image_scalars leaves the 16 pixel lines", len(after) == 16, f"{len(after)} lines survive: the filter meant to drop the header drops every pixel line too (should anchor: grep -v '^#')")
# the decode half, with the one-character fix applied here (NOT in ptol.c): same arithmetic as read_image_scalars
fixed = subprocess.run(["grep", "-v", "^#"], input=txt, capture_output=True, text=True).stdout.splitlines()
dec = []
for l in fixed:
    m = re.match(r"\\d+,\\d+: \\((\\d+),(\\d+),(\\d+)", l)
    if m:
        r_, g_, b_ = map(int, m.groups()); dec.append((1.0 if r_ >= b_ else -1.0) * (r_ + g_ + b_) / (3*255.0))
v = np.array(dec); ref = xw/mx
print("decoded (fix applied in-notebook):", np.round(v, 3)[:8], "…")
L.check("with the anchored filter the pixel→scalar decode returns 16 scalars", len(v) == 16)
if len(v) == 16:
    scale = np.dot(v, ref)/np.dot(ref, ref); err = np.linalg.norm(v - scale*ref)/np.linalg.norm(v)
    L.check("the word's geometry survives image → 16 scalars (shape within 5%; brightness is (r+g+b)/765, so a one-channel pixel reads at 1/3)", err < 0.05, f"scale {scale:.3f}, residual {err:.3f}")
    L.check("every sign survives", np.all(np.sign(v[np.abs(ref) > 0.02]) == np.sign(ref[np.abs(ref) > 0.02])))"""),
("code", """for c in ["'The geometry is the word': recognition by resonance with a word in the Zero Lattice needs word layers (BIN_DIR) not mounted here — scalars-level round trip is the part that runs",
          "Zork 1 (1981) sentence parser as the precedent for 'the path through meaning space is the meaning' (built-against reference; see the Zork parser notes)",
          "The three papers in one prompt: SVG = path, PPM = field, HTML = both + text shadow"]:
    L.prose(c)"""),
]
