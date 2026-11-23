"""Simulação dos stencils pintados (neve spray) no vidro da janela de atendimento da fachada."""
import sys, io, contextlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.geometry import Polygon
from shapely import affinity as af
import gerar

OUT = sys.argv[1]
FACHADA = sys.argv[2]
with contextlib.redirect_stdout(io.StringIO()):
    G = {k: gerar.build(fn, k) for k, _, fn in gerar.DESENHOS}

def mask(g, pxmm, flip=False):
    if flip: g = af.scale(g, -1, 1, origin=(0, 0))
    minx, miny, maxx, maxy = g.bounds
    W, H = int((maxx - minx) * pxmm) + 4, int((maxy - miny) * pxmm) + 4
    S = 3  # supersampling
    im = Image.new("L", (W * S, H * S), 0); d = ImageDraw.Draw(im)
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    tr = lambda cs: [((x - minx) * pxmm * S + 2 * S, (y - miny) * pxmm * S + 2 * S) for x, y in cs]
    for p in polys:
        d.polygon(tr(p.exterior.coords), fill=255)
        for i in p.interiors: d.polygon(tr(i.coords), fill=0)
    return im.resize((W, H), Image.LANCZOS)

rng = np.random.default_rng(7)
def spray(base, m, x, y, cor=(250, 252, 255), op=0.92):
    """Aplica 'neve spray' com a máscara m em (x,y) (canto sup. esq.) sobre base RGB."""
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(0.6)), dtype=float) / 255
    noise = rng.normal(1, 0.10, a.shape).clip(0.7, 1.1)
    noise = np.asarray(Image.fromarray((noise * 120).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), float) / 120
    a = (a * noise * op).clip(0, 1)[..., None]
    h, w = a.shape[:2]
    reg = np.asarray(base.crop((x, y, x + w, y + h)), float)
    h2, w2 = reg.shape[:2]; a = a[:h2, :w2]
    out = reg * (1 - a) + np.array(cor, float) * a
    base.paste(Image.fromarray(out.astype(np.uint8)), (x, y))

# ------------- layout no vidro (cm) — vidro estimado 90 x 92 cm
VW, VH = 90.0, 92.0
# (desenho, escala de impressão, centro x cm, topo y cm, espelhar)
LAYOUT = [
    ("wesolych", 1.414, 45, 4.0, False),     # A3
    ("swiat",    1.414, 45, 11.5, False),    # A3
    ("choinka",  1.414, 45, 24, False),      # A3  26 x 32 cm
    ("aniol",    1.0,   15.5, 33, False),    # A4
    ("aniol",    1.0,   74.5, 33, False),    # A4
    ("sniezynka", 0.6,  9, 4, False),        # A4 a 60 %
    ("sniezynka", 0.6,  81, 4, False),
    ("ptaszki",  1.0,   45, 62, False),      # A4
    ("faixa",    1.0,   15.5, 82, False),    # A4, 4 cópias no rodapé
    ("faixa",    1.0,   35, 82, False),
    ("faixa",    1.0,   55, 82, False),
    ("faixa",    1.0,   74.5, 82, False),
]

def vidro(pxcm, fundo):
    """Desenha o vidro com interior escuro + composição. Retorna imagem RGB (VW x VH cm)."""
    W, H = int(VW * pxcm), int(VH * pxcm)
    base = fundo.resize((W, H)) if fundo is not None else None
    if base is None:
        yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
        g = 38 + 30 * yy + 10 * np.sin(xx * 3)       # interior iluminado ao fundo
        arr = np.stack([g * 1.05, g * 0.95, g * 0.85], -1)
        base = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    for k, esc, cx, top, esp in LAYOUT:
        m = mask(G[k], pxcm / 10 * esc, esp)
        spray(base, m, int(cx * pxcm - m.width / 2), int(top * pxcm))
    # reflexo diagonal do vidro
    arr = np.asarray(base, float)
    yy, xx = np.mgrid[0:H, 0:W]
    band = np.exp(-((xx - yy * 0.55 - W * 0.25) / (W * 0.09)) ** 2) * 0.10 + \
           np.exp(-((xx - yy * 0.55 - W * 0.55) / (W * 0.03)) ** 2) * 0.06
    arr = arr + (255 - arr) * band[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))

def fonte(sz, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), sz)

# ---------- 1) vista frontal em escala, com cotas
px = 9
v = vidro(px, None)
M = 70
canvas = Image.new("RGB", (v.width + 2 * M + 480, v.height + 2 * M), (245, 243, 238))
d = ImageDraw.Draw(canvas)
d.rectangle((M - 14, M - 14, M + v.width + 14, M + v.height + 14), fill=(70, 70, 72))  # caixilho
canvas.paste(v, (M, M))
d.rectangle((M - 14, M + v.height + 14, M + v.width + 14, M + v.height + 34), fill=(15, 15, 15))  # balcão
f, fb = fonte(18), fonte(22, True)
d.line((M, M - 40, M + v.width, M - 40), fill=(0, 0, 0), width=2)
d.text((M + v.width / 2, M - 52), "≈ 90 cm", font=fb, fill=(0, 0, 0), anchor="ms")
d.line((M + v.width + 40, M, M + v.width + 40, M + v.height), fill=(0, 0, 0), width=2)
d.text((M + v.width + 50, M + v.height / 2), "≈ 92 cm", font=fb, fill=(0, 0, 0), anchor="lm")
leg = ["O QUE IMPRIMIR", "",
       "Wesołych — A3", "Świąt — A3", "Choinka — A3",
       "Anioł — A4 (2×)", "Ptaszki — A4", "Śnieżynka — A4 a 60 % (2×)", "Girlanda — A4 (2 folhas,",
       "  4 faixas)", "", "Medidas do vidro estimadas", "pela imagem 3D da fachada.", "Confirme na obra."]
for i, t in enumerate(leg):
    d.text((M + v.width + 130, M + 120 + i * 28), t, font=fb if i == 0 else f, fill=(30, 30, 30))
canvas.save(f"{OUT}/simulacao-vidro-frontal.png")

# ---------- 2) na fachada (imagem 3D do projeto)
fac = Image.open(FACHADA).convert("RGB")
S = 3
big = fac.resize((fac.width * S, fac.height * S), Image.LANCZOS)
x0, y0, x1, y1 = 372, 346, 484, 461          # vão da janela de atendimento (px da imagem original)
gw, gh = (x1 - x0) * S, (y1 - y0) * S
pxcm = gw / VW
v2 = vidro(pxcm, None).resize((gw, gh), Image.LANCZOS)
big.paste(v2, (x0 * S, y0 * S))
crop = big.crop((250 * S, 250 * S, 640 * S, 610 * S))
crop.save(f"{OUT}/simulacao-fachada-zoom.png")
big.resize((fac.width * 2, fac.height * 2), Image.LANCZOS).save(f"{OUT}/simulacao-fachada.png")
print("ok")
