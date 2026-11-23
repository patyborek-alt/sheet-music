"""Simulação da decoração de Natal sobre a FOTO real da fachada da PierogiShop.
Usa somente os desenhos do PDF, todos aplicados com spray branco pelo método do stencil. Escala da foto ≈ 2,06 px/cm (porta lateral ≈ 80 cm = 165 px)."""
import sys, io, contextlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity as af
import gerar
from gerar import C, leaf, mir, U, star, heart

FOTO, OUT = sys.argv[1], sys.argv[2]
with contextlib.redirect_stdout(io.StringIO()):
    G = {k: gerar.build(fn, k) for k, _, fn in gerar.DESENHOS}
PXCM = 2.06
SS = 2                                      # trabalha em 2x para ficar nítido
foto = Image.open(FOTO).convert("RGB")
img = foto.resize((foto.width * SS, foto.height * SS), Image.LANCZOS)
rng = np.random.default_rng(3)

def mask(g, W=None, H=None, fill_holes=False):
    """Rasteriza geometria g para caber em largura W (ou altura H) px finais."""
    if fill_holes:
        polys = [g] if isinstance(g, Polygon) else list(g.geoms)
        g = unary_union([Polygon(p.exterior) for p in polys])
    minx, miny, maxx, maxy = g.bounds
    k = (W / (maxx - minx)) if W else (H / (maxy - miny))
    k *= SS
    w, h = int((maxx - minx) * k) + 2, int((maxy - miny) * k) + 2
    S = 3
    im = Image.new("L", (w * S, h * S), 0); d = ImageDraw.Draw(im)
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    tr = lambda cs: [((x - minx) * k * S, (y - miny) * k * S) for x, y in cs]
    for p in polys:
        d.polygon(tr(p.exterior.coords), fill=255)
        for i in p.interiors: d.polygon(tr(i.coords), fill=0)
    return im.resize((w, h), Image.LANCZOS)

def put(m, cx, cy=None, top=None, bottom=None, cor=(250, 252, 255), op=0.9, neve=True, sombra=False):
    """Compõe máscara m na foto. Coordenadas em px da foto original."""
    global img
    w, h = m.size
    x = int(cx * SS - w / 2)
    if top is not None: y = int(top * SS)
    elif bottom is not None: y = int(bottom * SS - h)
    else: y = int(cy * SS - h / 2)
    a = np.asarray(m, float) / 255
    if neve:
        a = np.asarray(m.filter(ImageFilter.GaussianBlur(0.5)), float) / 255
        n = rng.normal(1, 0.12, a.shape).clip(0.65, 1.1)
        a = a * n
    a = (a * op).clip(0, 1)
    base = np.asarray(img, float)
    if sombra:
        sh = np.asarray(m.filter(ImageFilter.GaussianBlur(3 * SS)), float) / 255 * 0.35
        sx, sy = x + 2 * SS, y + 3 * SS
        reg = base[sy:sy + h, sx:sx + w]
        reg *= (1 - sh[:reg.shape[0], :reg.shape[1], None])
    reg = base[y:y + h, x:x + w]
    aa = a[:reg.shape[0], :reg.shape[1], None]
    base[y:y + h, x:x + w] = reg * (1 - aa) + np.array(cor, float) * aa
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8))

VERM, VERDE, VERDE2, BRANCO = (196, 20, 42), (30, 104, 60), (52, 138, 78), (247, 245, 238)

def duas_camadas(g, W, cx, cy=None, top=None, bottom=None, cor=VERM, fundo=BRANCO, borda=5):
    """Wycinanka de 2 camadas: silhueta de fundo um pouco maior + desenho colorido em cima."""
    minx, miny, maxx, maxy = g.bounds
    esc = (maxx - minx)
    fundo_g = g.buffer(esc * 0.018 * borda / 5)
    Wf = W * (fundo_g.bounds[2] - fundo_g.bounds[0]) / esc
    mf = mask(fundo_g, W=Wf, fill_holes=True)
    m = mask(g, W=W)
    if top is not None: dy = (mf.size[1] - m.size[1]) / 2 / SS; put(mf, cx, top=top - dy, cor=fundo, op=1, neve=False, sombra=True); put(m, cx, top=top, cor=cor, op=1, neve=False)
    elif bottom is not None:
        dy = (mf.size[1] - m.size[1]) / 2 / SS
        put(mf, cx, bottom=bottom + dy, cor=fundo, op=1, neve=False, sombra=True); put(m, cx, bottom=bottom, cor=cor, op=1, neve=False)
    else:
        put(mf, cx, cy=cy, cor=fundo, op=1, neve=False, sombra=True); put(m, cx, cy=cy, cor=cor, op=1, neve=False)

cm = lambda v: v * PXCM

# =================== VIDRO (neve spray) ===================
# porta esquerda x 668–950 · porta direita x 954–1255 · vidro y 932–1430
put(mask(G["wesolych"], W=cm(112)), 809, top=957)
hw = cm(112) * 43 / 273                       # altura de "Wesołych"
hs = cm(112) * 168 / 273 * 49 / 168          # "Świąt" com a mesma escala de letra
put(mask(G["swiat"], W=cm(112) * 168 / 273), 1104, top=957 + hw - hs)
put(mask(G["choinka"], H=cm(100)), 795, bottom=1372)
put(mask(G["aniol"], H=cm(88)), 1104, bottom=1372)
for (x, y, s) in [(700, 1040, 20), (905, 1060, 14), (742, 1112, 11), (1000, 1050, 15), (1222, 1034, 20), (1182, 1120, 11), (880, 1135, 10)]:
    put(mask(G["sniezynka"], H=cm(s)), x, cy=y)
fx = mask(G["faixa"], W=cm(37))
for i in range(7):
    put(fx, 700 + i * 81, bottom=1424)
for x in (707, 1212):                         # bandeira superior, ao lado do letreiro
    put(mask(G["rozeta"], W=cm(16)), x, cy=868, op=0.85)

# janela (vidro x 388–548, y 1058–1230)
put(mask(G["rozeta"], W=cm(46)), 468, cy=1140)
for (x, y) in [(405, 1076), (531, 1076)]:
    put(mask(G["sniezynka"], H=cm(13)), x, cy=y)

# =================== PAREDE, JANELA E PORTA: só os desenhos do PDF ===================
# parede sob a janela: Ptaszki pintado com o mesmo stencil (spray branco na parede)
put(mask(G["ptaszki"], W=cm(118)), 468, top=1253, op=0.95)
# vidro da porta de grade: Estrela de Belém em neve spray
put(mask(G["betlejemska"], H=cm(42)), 214, cy=1185)

# =================== devolve a escada para a frente ===================
orig = np.asarray(foto.resize(img.size, Image.LANCZOS), float)
band = Image.new("L", img.size, 0)
ImageDraw.Draw(band).polygon([(p[0] * SS, p[1] * SS) for p in
    [(160, 1262), (255, 1262), (1052, 1405), (1052, 1548), (140, 1500)]], fill=255)
band = np.asarray(band) > 0
L = orig.mean(-1); sat = orig.max(-1) - orig.min(-1)
escada = band & (L > 178) & (sat < 28)
escada = np.asarray(Image.fromarray((escada * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1)), float)[..., None] / 255
cur = np.asarray(img, float)
img = Image.fromarray((cur * (1 - escada) + orig * escada).astype(np.uint8))

img.resize(foto.size, Image.LANCZOS).save(f"{OUT}/fachada-natal.jpg", quality=92)
img.crop((0, 760 * SS, 1500 * SS, 1460 * SS)).save(f"{OUT}/fachada-natal-detalhe.jpg", quality=90)
print("ok")
