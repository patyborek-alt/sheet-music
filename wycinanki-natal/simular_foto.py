"""Simulação da decoração de Natal sobre a FOTO real da fachada da PierogiShop.
Usa somente os desenhos do PDF, aplicados com spray branco pelo método do stencil.
Gera a vista geral e closes em alta resolução (os desenhos são vetoriais, ficam nítidos).
Escala da foto ≈ 2,06 px/cm (porta lateral ≈ 80 cm = 165 px)."""
import sys, io, contextlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import Polygon
from shapely import affinity as af
import gerar

FOTO, OUT = sys.argv[1], sys.argv[2]
with contextlib.redirect_stdout(io.StringIO()):
    G = {k: gerar.build(fn, k) for k, _, fn in gerar.DESENHOS}
foto = Image.open(FOTO).convert("RGB")
PXCM = 2.06
cm = lambda v: v * PXCM

# ---------------- cena: (desenho, cx, ancoragem, valor_y, largura_px | None, altura_px | None)
def fit(k, W=None, H=None):
    b = G[k].bounds; w, h = b[2] - b[0], b[3] - b[1]
    return (W, W * h / w) if W else (H * w / h, H)
CENA = []
def add(k, cx, W=None, H=None, top=None, bottom=None, cy=None):
    w, h = fit(k, W, H)
    y0 = top if top is not None else (bottom - h if bottom is not None else cy - h / 2)
    CENA.append((k, cx - w / 2, y0, w, h))

# vidro grande: porta esquerda x 668–950 · porta direita x 954–1255 · vidro y 932–1430
wW = cm(112); hW = wW * 43 / 273
wS = wW * 168 / 273; hS = wS * 49 / 168
add("wesolych", 809, W=wW, top=957)
add("swiat", 1104, W=wS, top=957 + hW - hS)
add("choinka", 795, H=cm(100), bottom=1372)
add("aniol", 1104, H=cm(88), bottom=1372)
for (x, y, s) in [(700, 1040, 20), (905, 1060, 14), (742, 1112, 11), (1000, 1050, 15), (1222, 1034, 20), (1182, 1120, 11), (880, 1135, 10)]:
    add("sniezynka", x, H=cm(s), cy=y)
for i in range(7):
    add("faixa", 700 + i * 81, W=cm(37), bottom=1424)
for x in (707, 1212):
    add("rozeta", x, W=cm(16), cy=868)
# janela (vidro x 388–548, y 1058–1230)
add("rozeta", 468, W=cm(46), cy=1140)
for x in (405, 531):
    add("sniezynka", x, H=cm(13), cy=1076)
# porta de grade (vidro atrás da grade) e parede sob a janela
add("betlejemska", 214, H=cm(42), cy=1185)
add("ptaszki", 468, W=cm(118), top=1253)

ESCADA = [(160, 1262), (255, 1262), (1052, 1405), (1052, 1548), (140, 1500)]

def render(box, S, nome):
    """Renderiza a região box=(x0,y0,x1,y1) da foto ampliada S vezes."""
    x0, y0, x1, y1 = box
    base = foto.crop(box).resize(((x1 - x0) * S, (y1 - y0) * S), Image.BICUBIC)
    orig = np.asarray(base, float)
    arr = orig.copy()
    for k, gx, gy, w, h in CENA:
        if gx > x1 or gx + w < x0 or gy > y1 or gy + h < y0: continue
        g = G[k]; b = g.bounds
        kk = w / (b[2] - b[0]) * S
        ox, oy = (gx - x0) * S, (gy - y0) * S
        W, H = arr.shape[1], arr.shape[0]
        SSA = 3
        im = Image.new("L", (W * SSA, H * SSA), 0) if False else None
        # rasteriza só a caixa do desenho
        bx0, by0 = int(max(0, ox)), int(max(0, oy))
        bx1, by1 = int(min(W, ox + w * S + 2)), int(min(H, oy + h * S + 2))
        if bx1 <= bx0 or by1 <= by0: continue
        m = Image.new("L", ((bx1 - bx0) * SSA, (by1 - by0) * SSA), 0); d = ImageDraw.Draw(m)
        polys = [g] if isinstance(g, Polygon) else list(g.geoms)
        tr = lambda cs: [(((x - b[0]) * kk + ox - bx0) * SSA, ((y - b[1]) * kk + oy - by0) * SSA) for x, y in cs]
        for p in polys:
            d.polygon(tr(p.exterior.coords), fill=255)
            for i in p.interiors: d.polygon(tr(i.coords), fill=0)
        m = m.resize((bx1 - bx0, by1 - by0), Image.LANCZOS)
        a = (np.asarray(m, float) / 255 * 0.93)[..., None]
        reg = arr[by0:by1, bx0:bx1]
        arr[by0:by1, bx0:bx1] = reg * (1 - a) + np.array([252, 252, 250.0]) * a
    # escada volta para a frente
    band = Image.new("L", base.size, 0)
    ImageDraw.Draw(band).polygon([((px - x0) * S, (py - y0) * S) for px, py in ESCADA], fill=255)
    band = np.asarray(band) > 0
    L = orig.mean(-1); sat = orig.max(-1) - orig.min(-1)
    e = (band & (L > 200) & (sat < 24)).astype(np.uint8) * 255
    e = np.asarray(Image.fromarray(e).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(S / 2)), float)[..., None] / 255
    arr = arr * (1 - e) + orig * e
    Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(f"{OUT}/{nome}.jpg", quality=92)

render((0, 0, 1500, 2000), 2, "fachada-natal")
render((0, 760, 1500, 1460), 2, "fachada-natal-detalhe")
render((660, 925, 960, 1440), 5, "close-porta-esquerda")
render((945, 925, 1265, 1440), 5, "close-porta-direita")
render((120, 990, 650, 1430), 4, "close-janela-porta-parede")
print("ok")
