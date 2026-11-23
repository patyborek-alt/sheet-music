"""Gera stencils estilo wycinanki (recorte folclórico polonês) de Natal.
Cinza/preto = o desenho que fica PINTADO no vidro (peça que se retira antes do spray).
Branco = áreas que continuam cobertas (ficam transparentes).
Validação: o desenho é uma peça só (sai inteira de uma vez) e não tem partes
mais finas que 2 mm. Os textos podem ter acentos como peças separadas."""
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


# ---------------------------------------------------------------- ptaszki, anioły, napis
def _ptak():
    """Passarinho da direita, olhando para a esquerda (centro)."""
    body = E(52, 4, 30, 17, -18)
    head = C(26, -16, 12)
    beak = Polygon([(16, -20), (4, -14), (16, -11)])
    crest = U(leaf(30, -28, 18, 6, 40), leaf(34, -24, 14, 5, 62))
    tail = U(*[af.rotate(leaf(78, -22, 44, 14), a, origin=(76, 6)) for a in (-10, 12, 34, 56, 78)])
    legs = U(box(42, 18, 46, 46), box(54, 16, 58, 46))
    paper = U(body, head, beak, crest, tail, legs)
    holes = [C(23, -18, 2.6), leaf(54, 2, 30, 11, -64), C(36, 8, 2), C(42, 13, 2),
             heart(30, -2, 7, 160)]
    holes += [af.rotate(leaf(78, -18, 26, 4.5), a, origin=(76, 6)) for a in (-10, 12, 34, 56, 78)]
    return paper, U(*holes)

def ptaszki():
    pb, hb = _ptak()
    stem = box(-3.5, -78, 3.5, 46)
    branches = U(*[mir(af.rotate(leaf(14, y, 26, 10), -60, origin=(0, y + 6))) for y in (-52, -26, 0, 24)])
    top = heart(0, -88, 26)
    base = box(-112, 44, 112, 54)
    sc = [C(-112 + 224 * k / 16, 54, 6.5) for k in range(17)]
    paper = U(mir(pb), stem, branches, top, base, *sc)
    holes = [mir(hb), heart(0, -86, 12)]
    holes += [mir(af.rotate(leaf(14, y, 14, 3.5), -60, origin=(0, y + 6))) for y in (-52, -26, 0, 24)]
    holes += [C(-112 + 224 * k / 16, 54, 2.4) for k in range(17)]
    holes += [diamond(x, 49, 6, 5) for x in (-80, -66, 66, 80)]
    return paper, U(*holes)

def _aniol(detalhe=True):
    head = C(0, -72, 14)
    hair = U(C(-12, -66, 7), C(12, -66, 7))
    halo = U(E(0, -96, 18, 6).difference(E(0, -96, 13, 2.6)), box(-2.5, -93, 2.5, -84)) if detalhe else \
        U(E(0, -96, 18, 6), box(-3, -93, 3, -84))
    neck = box(-5, -60, 5, -52)
    dress = Polygon([(-11, -55), (11, -55), (44, 52), (-44, 52)])
    hem = [C(-44 + 88 * k / 8, 52, 6) for k in range(9)]
    feet = U(E(-10, 61, 6, 4), E(10, 61, 6, 4))
    # asa: elipse inclinada com penas em festão na borda de baixo
    wing = U(E(44, -34, 36, 17, -22),
             *[af.rotate(E(44 + dx, -34 + 13, 7, 9), -22, origin=(44, -34)) for dx in (-22, -11, 0, 11, 22)],
             af.rotate(leaf(84, -34, 22, 12, 90), -22, origin=(44, -34)))
    wings = mir(wing)
    paper = U(head, hair, halo, neck, dress, *hem, feet, wings)
    holes = [star(0, -30, 5, 11, 4.6)]
    if detalhe:
        holes += [C(-5, -73, 1.8), C(5, -73, 1.8)]
        holes += [mir(af.rotate(leaf(44 + dx, -36, 20, 6), -22, origin=(44, -34))) for dx in (-16, -2, 12)]
        holes += [mir(af.rotate(C(44 + dx, -22, 2.2), -22, origin=(44, -34))) for dx in (-22, -11, 0, 11, 22)]
        holes += [heart(k * 11, -6, 7) for k in (-1, 0, 1)]
        holes += [drop(k * 11, 12, 9, 5) for k in (-2, -1, 0, 1, 2)]
        holes += [diamond(k * 10, 30, 5, 8) for k in (-3, -2, -1, 0, 1, 2, 3)]
        holes += [C(-44 + 88 * k / 8, 52, 2.2) for k in range(9)]
    else:
        holes += [mir(af.rotate(leaf(44 + dx, -36, 22, 8), -22, origin=(44, -34))) for dx in (-12, 10)]
        holes += [heart(0, 4, 14), diamond(-16, 28, 8, 13), diamond(16, 28, 8, 13), diamond(0, 30, 8, 13)]
    return paper, U(*holes)

def aniol():
    return _aniol(True)

def anioly():
    p, h = _aniol(False)
    ps, hs = [], []
    for x in (-165, 0, 165):
        ps.append(af.translate(p, x, 0)); hs.append(af.translate(h, x, 0))
    W = 250
    base = box(-W, 60, W, 70)
    sc = [C(-W + 2 * W * k / 28, 70, 8) for k in range(29)]
    hs += [C(-W + 2 * W * k / 28, 71, 2.6) for k in range(29)]
    hs += [heart(x, 65, 7) for x in (-82, 82)]
    return U(*ps, base, *sc), U(*hs)

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
def texto(s, size=100.0, track=4.0):
    from fontTools.ttLib import TTFont
    from fontTools.pens.basePen import BasePen
    f = TTFont(FONTE); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f["head"].unitsPerEm
    k = size / upm
    class P(BasePen):
        def __init__(s_, gs_): super().__init__(gs_); s_.rings = []; s_.cur = []
        def _moveTo(s_, p): s_.cur = [p]
        def _lineTo(s_, p): s_.cur.append(p)
        def _curveToOne(s_, a, b, c):
            p0 = s_.cur[-1]
            for i in range(1, 13):
                t = i / 12; u = 1 - t
                s_.cur.append(tuple(u**3*p0[j] + 3*u*u*t*a[j] + 3*u*t*t*b[j] + t**3*c[j] for j in (0, 1)))
        def _qCurveToOne(s_, a, b):
            p0 = s_.cur[-1]
            for i in range(1, 10):
                t = i / 9; u = 1 - t
                s_.cur.append(tuple(u*u*p0[j] + 2*u*t*a[j] + t*t*b[j] for j in (0, 1)))
        def _closePath(s_):
            if len(s_.cur) > 2: s_.rings.append(s_.cur)
            s_.cur = []
        _endPath = _closePath
    x = 0; letters = []
    for ch in s:
        gn = cmap[ord(ch)]; pen = P(gs); gs[gn].draw(pen)
        g = Polygon()
        for r in pen.rings:
            g = g.symmetric_difference(Polygon([(x + px, -py) for px, py in r]).buffer(0))
        letters.append(af.scale(g, k, k, origin=(0, 0)))
        x += gs[gn].width + track * upm / size
    return letters

def _napis(palavra):
    letters = texto(palavra)
    g = unary_union(letters)
    minx, miny, maxx, maxy = g.bounds
    letters = [af.translate(l, -(minx + maxx) / 2, 0) for l in letters]
    g = unary_union(letters); minx, miny, maxx, maxy = g.bounds
    # base: barra na linha de base (y=0) com festão
    W = maxx - minx + 40
    base = box(-W / 2, -1.5, W / 2, 9)
    n = int(W // 13)
    sc = [C(-W / 2 + W * i / n, 9, 5.5) for i in range(n + 1)]
    ends = [heart(s * (W / 2 + 6), 3, 22, s * 90) for s in (-1, 1)]
    paper = U(*letters, base, *sc, *ends)
    # pontes para acentos soltos (ex.: o acento do Ś)
    parts = [paper] if isinstance(paper, Polygon) else sorted(paper.geoms, key=lambda p: -p.area)
    bridges = []
    for p in parts[1:]:
        cx = p.centroid.x; by = p.bounds[3]
        pass
    paper = U(paper, *bridges)
    zona = unary_union(letters).buffer(2.5)
    holes = [C(-W / 2 + W * i / n, 9, 2) for i in range(n + 1) if not C(-W / 2 + W * i / n, 9, 2).intersects(zona)]
    holes += [heart(s * (W / 2 + 6), 3, 9, s * 90) for s in (-1, 1)]
    return paper, U(*holes)

def wesolych(): return _napis("Wesołych")
def swiat(): return _napis("Świąt")

DESENHOS = [
    ("choinka", "Choinka — Árvore de Natal", choinka),
    ("rozeta", "Gwiazda — Roseta de estrela", rozeta),
    ("sniezynka", "Śnieżynka — Floco de neve", snieżynka),
    ("bombka", "Bombka — Bola de Natal", bombka),
    ("dzwonek", "Dzwonek — Sino", dzwonek),
    ("betlejemska", "Gwiazda Betlejemska — Estrela de Belém", betlejemska),
    ("faixa", "Girlanda — Faixa de rodapé (2×)", faixa),
    ("ptaszki", "Ptaszki — Passarinhos e árvore da vida", ptaszki),
    ("aniol", "Anioł — Anjo", aniol),
    ("anioly", "Anioły — Faixa de anjinhos", anioly),
    ("wesolych", "„Wesołych” — 1ª palavra de Wesołych Świąt", wesolych),
    ("swiat", "„Świąt” — 2ª palavra de Wesołych Świąt", swiat),
]
PAISAGEM = {"anioly", "wesolych", "swiat"}

MAXW, MAXH = 186, 246   # área útil no A4 (com legenda)

def build(fn, key):
    paper, holes = fn()
    minx, miny, maxx, maxy = paper.bounds
    mw, mh = (273, 160) if key in PAISAGEM else (MAXW, 120 if key == "faixa" else MAXH)
    f = min(1.6, mw / (maxx - minx), mh / (maxy - miny))
    if key == "swiat":  # mesma altura de letra que "Wesołych" para as duas linhas combinarem
        pw, _ = wesolych()
        b = pw.bounds
        f = min(1.6, mw / (b[2] - b[0]), mh / (b[3] - b[1]))
    paper = af.scale(paper, f, f, origin=(0, 0)); holes = af.scale(holes, f, f, origin=(0, 0))
    # abertura morfológica: elimina lascas de papel mais finas que ~2,4 mm
    paper = paper.buffer(-1.2, 32).buffer(1.2, 32)
    inner = paper.buffer(-2.5)
    hs = [holes] if isinstance(holes, Polygon) else list(holes.geoms)
    kept = [h for h in hs if inner.contains(h)]
    if len(kept) < len(hs): print(f"  ({key}: {len(hs)-len(kept)} furos perto da borda descartados)")
    holes = unary_union(kept)
    g = paper.difference(holes).buffer(0)
    minx, miny, maxx, maxy = g.bounds
    return af.translate(g, -(minx + maxx) / 2, -(miny + maxy) / 2)

def check(name, g):
    ok = True
    if not isinstance(g, Polygon):
        n = len(g.geoms)
        if name.startswith(("wesolych", "swiat")):
            print(f"  ({name}: {n} peças — letras/acentos separados, ok com papel adesivo)")
        else:
            print(f"  !! {name}: {n} peças soltas", [round(p.area) for p in g.geoms]); ok = False
    e = g.buffer(-1.0)  # largura mínima de 2 mm
    if not name.startswith(("wesolych", "swiat")) and not isinstance(e, Polygon) and sum(p.area > 1 for p in e.geoms) > (1 if isinstance(g, Polygon) else len(g.geoms)):
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
        out[key] = dict(land=key in PAISAGEM, title=title, d=path_d(g), bounds=list(g.bounds))
        if key in ("wesolych", "swiat"):   # versão espelhada para aplicar por dentro da vitrine
            m = af.scale(g, -1, 1, origin=(0, 0))
            out[key + "_esp"] = dict(land=True, title=title + " (ESPELHADO — aplicar por dentro)",
                                     d=path_d(m), bounds=list(m.bounds))
    import os
    os.makedirs("svg", exist_ok=True)   # vetores em mm reais, para gráfica/plotter de recorte
    for k, v in out.items():
        b = v["bounds"]; w, h = b[2] - b[0], b[3] - b[1]
        open(f"svg/{k}.svg", "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}mm" height="{h:.1f}mm" '
            f'viewBox="{b[0]:.2f} {b[1]:.2f} {w:.2f} {h:.2f}"><path fill="#000" fill-rule="evenodd" d="{v["d"]}"/></svg>')
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "paths.json", "w"))
    print("TUDO OK" if allok else "HÁ PROBLEMAS")
