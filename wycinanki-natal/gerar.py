"""Gera stencils estilo wycinanki (recorte folclórico polonês) de Natal.
Preto = papel que fica (máscara). Branco = recortar e descartar (o spray passa).
Cada desenho é validado: uma única peça conectada e pontes >= 2 mm."""
import math, sys
from shapely.geometry import Point, Polygon, box, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity as af

def C(x, y, r): return Point(x, y).buffer(r, 64)
def E(x, y, rx, ry, a=0):
    return af.rotate(af.scale(Point(0, 0).buffer(1, 64), rx, ry).buffer(0), a, origin=(0, 0)).__class__ and \
        af.translate(af.rotate(af.scale(Point(0, 0).buffer(1, 64), rx, ry), a, origin=(0, 0)), x, y)
def leaf(x, y, L, W, a=0):
    """Folha/pétala pontuda (lente) de comprimento L, largura W, eixo vertical, girada a graus."""
    r = (L * L / 4 + W * W / 4) / W
    d = r - W / 2
    g = C(-d, 0, r).intersection(C(d, 0, r))
    return af.translate(af.rotate(g, a, origin=(0, 0)), x, y)
def drop(x, y, L, W, a=0):
    """Gota: ponta para cima (y negativo), parte redonda embaixo."""
    r = W / 2
    tip = (0, -L / 2)
    cy = L / 2 - r
    g = unary_union([C(0, cy, r), Polygon([tip, (-r * 0.98, cy - r * 0.2), (r * 0.98, cy - r * 0.2)]).convex_hull])
    g = unary_union([C(0, cy, r), Polygon([tip, (-r, cy), (r, cy)])]).convex_hull
    return af.translate(af.rotate(g, a, origin=(0, 0)), x, y)
def heart(x, y, s, a=0):
    pts = []
    for i in range(200):
        t = 2 * math.pi * i / 200
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((hx * s / 32, hy * s / 32))
    return af.translate(af.rotate(Polygon(pts), a, origin=(0, 0)), x, y)
def diamond(x, y, w, h): return Polygon([(x, y - h / 2), (x + w / 2, y), (x, y + h / 2), (x - w / 2, y)])
def star(x, y, n, R, r, a=-90):
    pts = []
    for i in range(2 * n):
        rr = R if i % 2 == 0 else r
        t = math.radians(a + 180 * i / n)
        pts.append((x + rr * math.cos(t), y + rr * math.sin(t)))
    return Polygon(pts)
def radial(g, n, ox=0, oy=0, off=0):
    return unary_union([af.rotate(g, off + 360 * i / n, origin=(ox, oy)) for i in range(n)])
def mir(g): return unary_union([g, af.scale(g, -1, 1, origin=(0, 0))])
def U(*gs): return unary_union(list(gs))
def ring(x, y, R, r): return C(x, y, R).difference(C(x, y, r))

# ---------------------------------------------------------------- desenhos
def choinka():
    paper = []
    holes = []
    tiers = [(-95, 30, -55, 48), (-62, 46, -18, 66), (-25, 62, 22, 84), (14, 78, 62, 100)]
    for (yt, hw_top, yb, hw_b) in tiers:
        pass
    # camadas: triângulos com borda inferior em festão
    layers = [(-100, -48, 46), (-70, -10, 64), (-36, 30, 82), (0, 70, 100)]
    for i, (ytop, ybot, hw) in enumerate(layers):
        tri = Polygon([(0, ytop), (hw, ybot), (-hw, ybot)])
        n = 5 + 2 * i
        sc = [C(-hw + (2 * hw) * (k + 0.5) / n, ybot, hw / n) for k in range(n)]
        paper.append(U(tri, *sc))
        # furos: fileira de gotas + losangos
        yy = ybot - 10
        w_at = hw * (yy - ytop) / (ybot - ytop)
        m = 2 + i
        for k in range(-m, m + 1):
            x = k * (w_at - 10) / m if m else 0
            if abs(x) < 4: holes.append(heart(0, yy - 1, 9)); continue
            holes.append(drop(x, yy, 9, 5.5))
        # linha superior: pequenos losangos
        yy2 = ybot - 24 - 2 * i
        if yy2 - ytop > 12:
            w2 = hw * (yy2 - ytop) / (ybot - ytop)
            m2 = 1 + i
            for k in range(-m2, m2 + 1):
                x = k * (w2 - 9) / max(m2, 1)
                holes.append(diamond(x, yy2, 5, 8) if k else C(0, yy2, 3.2))
    # estrela no topo
    paper.append(star(0, -112, 8, 20, 9, a=-90))
    holes.append(star(0, -112, 8, 11, 5))
    # tronco e base
    paper.append(box(-12, 70, 12, 96))
    paper.append(Polygon([(-34, 96), (34, 96), (26, 118), (-26, 118)]))
    holes += [heart(-14, 106, 9), heart(14, 106, 9), diamond(0, 106, 6, 10)]
    holes += [leaf(0, 82, 16, 6)]
    return U(*paper), U(*holes)

def rozeta():
    R = 88
    base = C(0, 0, R - 8)
    sc = [C((R - 8) * math.cos(t), (R - 8) * math.sin(t), 8.5) for t in [2 * math.pi * k / 24 for k in range(24)]]
    spikes = radial(Polygon([(-6, -R + 4), (0, -R - 10), (6, -R + 4)]), 24, off=7.5)
    paper = U(base, *sc, spikes)
    holes = []
    holes.append(radial(C(0, -(R - 8), 3.3), 24))                  # furinhos no festão
    holes.append(radial(drop(0, -64, 13, 7), 24, off=7.5))         # gotas
    holes.append(radial(leaf(0, -42, 26, 12), 8))                  # pétalas grandes
    holes.append(radial(leaf(0, -44, 16, 6), 8, off=22.5))         # pétalas finas
    holes.append(radial(heart(0, -24, 8, 180), 8, off=22.5))       # corações
    holes.append(star(0, 0, 8, 15, 7))                             # estrela central
    return paper, U(*holes)

def snieżynka():
    arm = U(box(-4, -92, 4, 0),
            af.rotate(box(-3, -26, 3, 0), 45, origin=(0, 0)).__class__ and
            U(*[af.translate(af.rotate(box(-3, -L, 3, 0), s * 50, origin=(0, 0)), 0, y)
                for (y, L) in [(-40, 26), (-64, 20)] for s in (1, -1)]),
            diamond(0, -84, 18, 26), C(0, -96, 6))
    paper = U(radial(arm, 6), C(0, 0, 26), radial(drop(0, -30, 16, 12, 180), 6, off=30))
    holes = U(star(0, 0, 6, 13, 6, a=-90), radial(C(0, -20, 2.6), 6, off=30),
              radial(diamond(0, -84, 6, 12), 6), radial(C(0, -96, 2.2), 6),
              radial(C(0, -31, 2.6), 6, off=30))
    return paper, holes

def bombka():
    R = 82
    paper = U(C(0, 10, R), box(-20, -R - 6, 20, -R + 16), C(0, -R - 16, 13))
    holes = [C(0, -R - 16, 7)]
    for k in range(-3, 4):
        holes.append(diamond(k * 12, -52, 6, 10))
    for k in range(-5, 6):
        holes.append(heart(k * 11, -36, 8) if k % 2 == 0 else C(k * 11, -36, 2.4))
    holes.append(radial(leaf(0, 10 - 18, 18, 8), 8, ox=0, oy=10))
    holes.append(C(0, 10, 4))
    holes.append(radial(drop(0, 10 - 34, 9, 5, 180), 16, ox=0, oy=10, off=11.25))
    for k in range(-4, 5):
        holes.append(drop(k * 12, 60, 12, 6))
    for k in range(-3, 4):
        holes.append(diamond(k * 12, 78, 5, 7))
    # tampa: frisos
    for k in range(-2, 3):
        holes.append(box(k * 7 - 1.5, -R - 2, k * 7 + 1.5, -R + 12))
    return paper, U(*holes)

def dzwonek():
    pts = []
    for i in range(101):
        t = i / 100
        y = -60 + 130 * t
        hw = 30 + 10 * t + 44 * t ** 5
        pts.append((hw, y))
    bell = U(mir(Polygon([(0, -60)] + pts + [(0, 70)])), C(0, -58, 30), box(-90, 64, 90, 78))
    bell = U(bell, *[C(-90 + 180 * k / 12, 78, 7.5) for k in range(13)])
    clapper = C(0, 94, 11)
    bow = U(mir(Polygon([(0, -96), (40, -120), (46, -86), (0, -90)])), C(0, -93, 9))
    paper = U(bell, clapper, box(-5, 76, 5, 88), bow)
    holes = [leaf(26, -103, 22, 7, 64), leaf(-26, -103, 22, 7, -64), C(0, -93, 3.5), C(0, 94, 4.5)]
    holes += [heart(0, -62, 16), leaf(-17, -44, 20, 8, 35), leaf(17, -44, 20, 8, -35), C(0, -40, 3)]
    for k in range(-2, 3):
        holes.append(diamond(k * 12, -22, 6, 11))
    for k in range(-2, 3):
        holes.append(drop(k * 14, 0, 14, 8) if k else heart(0, 0, 12))
    for k in range(-3, 4):
        holes.append(diamond(k * 12, 22, 6, 10))
    for k in range(-5, 6):
        holes.append(drop(k * 12, 46, 12, 7, 180) if k % 2 else C(k * 12, 46, 3.2))
    for k in range(13):
        holes.append(C(-90 + 180 * k / 12, 78, 2.8))
    return paper, U(*holes)

def betlejemska():
    rays = []
    for k in range(8):
        L = 100 if k % 2 == 0 else 52
        if k == 4: L = 118
        rays.append(af.rotate(Polygon([(-15 if k % 2 == 0 else -11, 0), (0, -L), (15 if k % 2 == 0 else 11, 0)]), 45 * k, origin=(0, 0)))
    paper = U(*rays, C(0, 0, 30), radial(C(0, -30, 7), 16))
    holes = []
    for k in range(8):
        L = 100 if k % 2 == 0 else 52
        if k == 4: L = 118
        a = 45 * k
        if k % 2 == 0:
            holes.append(af.rotate(leaf(0, -(34 + (L - 32) * 0.36), (L - 32) * 0.45, 6), a, origin=(0, 0)))
    holes.append(radial(C(0, -30, 2.6), 16))
    holes.append(radial(leaf(0, -15, 14, 6), 8, off=22.5))
    holes.append(star(0, 0, 8, 6, 3))
    return af.translate(paper, 0, -10), af.translate(U(*holes), 0, -10)

def faixa():
    """Faixa/guirlanda para a parte de baixo da vitrine (2 por página)."""
    W = 190
    paper = [box(-W / 2, 16, W / 2, 26)]
    paper += [C(-W / 2 + W * k / 19, 26, 5.0) for k in range(20)]
    holes = [C(-W / 2 + W * k / 19, 26, 2) for k in range(20)]
    for k in range(-3, 4):
        x = k * 27
        if k % 2 == 0:  # arvorezinha
            t = U(Polygon([(x, -28), (x + 13, -6), (x - 13, -6)]), Polygon([(x, -14), (x + 15, 12), (x - 15, 12)]),
                  box(x - 3, 10, x + 3, 17), star(x, -29, 5, 7, 3))
            paper.append(t)
            holes += [diamond(x, -10, 4, 7), drop(x - 6, 6, 7, 4), drop(x + 6, 6, 7, 4), C(x, 6, 1.8)]
        else:           # coração com furinhos
            paper.append(U(heart(x, -2, 30), box(x - 3, 10, x + 3, 17)))
            holes += [heart(x, 3, 10), C(x - 7, -6, 1.8), C(x + 7, -6, 1.8)]
    return U(*paper), U(*holes)

DESENHOS = [
    ("choinka", "Choinka — Árvore de Natal", choinka),
    ("rozeta", "Gwiazda — Roseta de estrela", rozeta),
    ("sniezynka", "Śnieżynka — Floco de neve", snieżynka),
    ("bombka", "Bombka — Bola de Natal", bombka),
    ("dzwonek", "Dzwonek — Sino", dzwonek),
    ("betlejemska", "Gwiazda Betlejemska — Estrela de Belém", betlejemska),
    ("faixa", "Girlanda — Faixa de rodapé (2×)", faixa),
]

MAXW, MAXH = 186, 246   # área útil no A4 (com legenda)

def build(fn, key):
    paper, holes = fn()
    inner = paper.buffer(-2.5)
    hs = [holes] if isinstance(holes, Polygon) else list(holes.geoms)
    kept = [h for h in hs if inner.contains(h)]
    if len(kept) < len(hs): print(f"  ({key}: {len(hs)-len(kept)} furos perto da borda descartados)")
    holes = unary_union(kept)
    g = paper.difference(holes).buffer(0)
    minx, miny, maxx, maxy = g.bounds
    lim_h = 120 if key == "faixa" else MAXH
    f = min(1.0, MAXW / (maxx - minx), lim_h / (maxy - miny))
    g = af.scale(g, f, f, origin=(0, 0))
    minx, miny, maxx, maxy = g.bounds
    return af.translate(g, -(minx + maxx) / 2, -(miny + maxy) / 2)

def check(name, g):
    ok = True
    if not isinstance(g, Polygon):
        print(f"  !! {name}: {len(g.geoms)} peças soltas", [round(p.area) for p in g.geoms]); ok = False
    e = g.buffer(-1.0)  # ponte mínima de 2 mm
    if not isinstance(e, Polygon):
        print(f"  !! {name}: ponte fina (<2mm) separa partes", [round(p.area) for p in e.geoms]); ok = False
    # furos que viraram parte da borda (tocaram fora) ainda são ok, só informa
    b = g.bounds
    print(f"  {name}: {b[2]-b[0]:.0f}×{b[3]-b[1]:.0f} mm, furos={len(g.interiors) if isinstance(g, Polygon) else '?'} {'OK' if ok else ''}")
    return ok

def path_d(g):
    def ring_d(coords):
        c = list(coords)
        return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in c[:-1]) + " Z"
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    return " ".join(ring_d(p.exterior.coords) + " " + " ".join(ring_d(i.coords) for i in p.interiors) for p in polys)

if __name__ == "__main__":
    import json
    out = {}
    allok = True
    for key, title, fn in DESENHOS:
        g = build(fn, key)
        allok &= check(key, g)
        minx, miny, maxx, maxy = g.bounds
        out[key] = dict(title=title, d=path_d(g), bounds=[minx, miny, maxx, maxy])
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "paths.json", "w"))
    print("TUDO OK" if allok else "HÁ PROBLEMAS")
