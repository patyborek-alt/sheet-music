"""Aplica a arte da vitrine (vitrine.py) na foto real da fachada, com closes em alta resolução,
e exporta SVGs em tamanho real (mm) para a gráfica, uma camada por cor."""
import sys, pickle
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import Polygon
from shapely import affinity as af

PKL, FOTO, OUT = sys.argv[1:4]
D = pickle.load(open(PKL, "rb"))
foto = Image.open(FOTO).convert("RGB")
# posição de cada folha de vidro na foto (px): x0, y0, largura, altura
POS = {"porta-esquerda": (668, 932, 282, 492, 1390, 2400), "porta-direita": (954, 932, 301, 492, 1520, 2400)}
ESCADA = [(160, 1262), (255, 1262), (1052, 1405), (1052, 1548), (140, 1500)]
CORES = {"B": (252, 252, 250), "V": (200, 24, 40)}

def raster(g, size, f):
    S = 3
    m = Image.new("L", (size[0] * S, size[1] * S), 0); d = ImageDraw.Draw(m)
    if not g.is_empty:
        for p in ([g] if isinstance(g, Polygon) else list(g.geoms)):
            d.polygon([f(x, y, S) for x, y in p.exterior.coords], fill=255)
            for i in p.interiors: d.polygon([f(x, y, S) for x, y in i.coords], fill=0)
    return np.asarray(m.resize(size, Image.LANCZOS), float) / 255

def render(box_, S, nome):
    x0, y0, x1, y1 = box_
    base = foto.crop(box_).resize(((x1 - x0) * S, (y1 - y0) * S), Image.BICUBIC)
    orig = np.asarray(base, float); arr = orig.copy()
    for porta, (px, py, pw, ph, W, H) in POS.items():
        B, V = D[porta]
        kx, ky = pw / W, ph / H
        f = lambda x, y, s: (((px + x * kx) - x0) * S * s, ((py + y * ky) - y0) * S * s)
        for g, c, op in [(V, "V", 0.95), (B, "B", 0.93)]:
            a = raster(g, base.size, f)[..., None] * op
            arr = arr * (1 - a) + np.array(CORES[c], float) * a
    band = Image.new("L", base.size, 0)
    ImageDraw.Draw(band).polygon([((qx - x0) * S, (qy - y0) * S) for qx, qy in ESCADA], fill=255)
    band = np.asarray(band) > 0
    L = orig.mean(-1); sat = orig.max(-1) - orig.min(-1)
    e = (band & (L > 200) & (sat < 24)).astype(np.uint8) * 255
    e = np.asarray(Image.fromarray(e).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(S / 2)), float)[..., None] / 255
    arr = arr * (1 - e) + orig * e
    Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(f"{OUT}/{nome}.jpg", quality=92)

def svg(g, W, H, cor, path):
    def ring(cs):
        c = list(cs); return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in c[:-1]) + " Z"
    polys = [] if g.is_empty else ([g] if isinstance(g, Polygon) else list(g.geoms))
    d = " ".join(ring(p.exterior.coords) + " " + " ".join(ring(i.coords) for i in p.interiors) for p in polys)
    open(path, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
                          f'<rect width="{W}" height="{H}" fill="none" stroke="#999" stroke-width="1"/>'
                          f'<path fill="{cor}" fill-rule="evenodd" d="{d}"/></svg>')

def ficha(path):
    """PDF para a gráfica: visão geral colorida + cada camada com medidas."""
    from PIL import ImageFont
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    k = 0.6  # px por mm
    pages = []
    def door_img(B, V, W, H, fundo, modo):
        size = (int(W * k), int(H * k))
        im = Image.new("RGB", size, fundo)
        tf = lambda x, y, s: (x * k * s, y * k * s)
        if modo in ("cor", "V") and not V.is_empty:
            a = raster(V, size, tf)[..., None]
            im = Image.fromarray((np.asarray(im, float) * (1 - a) + np.array((200, 24, 40)) * a).astype(np.uint8))
        if modo in ("cor", "B"):
            a = raster(B, size, tf)[..., None]
            cor = (250, 250, 248) if modo == "cor" else (0, 0, 0)
            im = Image.fromarray((np.asarray(im, float) * (1 - a) + np.array(cor) * a).astype(np.uint8))
        return im
    A4 = (2480, 3508)
    # visão geral
    pg = Image.new("RGB", (3508, 2480), "white"); d = ImageDraw.Draw(pg)
    d.text((120, 80), "Vitrine PierogiShop — arte wycinanki (frente das 2 portas de vidro)", font=fb, fill="black")
    x = 160
    for porta, (*_, W, H) in POS.items():
        B, V = D[porta]
        im = door_img(B, V, W, H, (45, 40, 36), "cor")
        im = im.resize((int(im.width * 1900 / im.height), 1900))
        pg.paste(im, (x, 260))
        d.text((x, 2180), f"{porta.replace('-', ' ')}: {W/10:.0f} × {H/10:.0f} cm", font=f, fill="black")
        x += im.width + 120
    d.text((x + 40, 300), "Camadas:", font=fb, fill="black")
    for i, t in enumerate(["BRANCO: renda, flocos, texto,", "  contornos (spray ou vinil branco)", "VERMELHO: laço, festões, flores,",
                           "  miolo do floco e bolas", "", "Arquivos SVG em mm reais:", "  svg-vitrine/*-BRANCO.svg", "  svg-vitrine/*-VERMELHO.svg",
                           "", "Medidas das portas estimadas", "pela foto — CONFIRMAR na obra", "antes de cortar."]):
        d.text((x + 40, 370 + i * 44), t, font=f, fill="black")
    pages.append(pg)
    for porta, (*_, W, H) in POS.items():
        B, V = D[porta]
        for camada, nome in [("B", "BRANCO"), ("V", "VERMELHO")]:
            if camada == "V" and V.is_empty: continue
            pg = Image.new("RGB", A4, "white"); d = ImageDraw.Draw(pg)
            im = door_img(B, V, W, H, (255, 255, 255), camada)
            im = im.resize((int(im.width * 3000 / im.height), 3000))
            d.text((120, 70), f"{porta.replace('-', ' ').upper()} — camada {nome} — {W/10:.0f} × {H/10:.0f} cm", font=fb, fill="black")
            pg.paste(im, ((A4[0] - im.width) // 2, 220))
            d.rectangle(((A4[0] - im.width) // 2, 220, (A4[0] + im.width) // 2, 220 + im.height), outline=(150, 150, 150), width=3)
            d.text((120, 3300), "Preto = área que recebe a cor (o adesivo é retirado aqui antes do spray, ou é o vinil que fica colado).", font=f, fill="black")
            pages.append(pg)
    pages[0].save(path, save_all=True, append_images=pages[1:], resolution=300)


if __name__ == "__main__":
    render((0, 0, 1500, 2000), 2, "vitrine-fachada")
    render((600, 760, 1320, 1460), 3, "vitrine-detalhe")
    render((660, 925, 960, 1440), 5, "vitrine-close-porta-esquerda")
    render((945, 925, 1265, 1440), 5, "vitrine-close-porta-direita")
    import os
    os.makedirs("svg-vitrine", exist_ok=True)
    for porta, (*_, W, H) in POS.items():
        B, V = D[porta]
        svg(B, W, H, "#000", f"svg-vitrine/{porta}-BRANCO.svg")
        if not V.is_empty: svg(V, W, H, "#c8102e", f"svg-vitrine/{porta}-VERMELHO.svg")
    ficha("vitrine-para-grafica.pdf")
    print("ok")
