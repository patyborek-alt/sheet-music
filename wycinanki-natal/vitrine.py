"""Arte da vitrine (referência enviada pela cliente) recriada em vetor, no tamanho real das portas.
Unidades: mm, origem no canto superior esquerdo de cada folha de vidro, y para baixo.
Camadas: BRANCO (spray/vinil branco) e VERMELHO (spray/vinil vermelho)."""
import math, random
from shapely.geometry import Point, Polygon, LineString, box, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity as af
from gerar import C, leaf, star, heart, diamond, radial, U
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

FONTES = ["fontes/lobster-latin-400-normal.woff", "fontes/lobster-latin-ext-400-normal.woff"]

# ------------------------------------------------------------------ utilidades
def bez(p0, p1, p2, p3=None, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        if p3 is None:
            pts.append(tuple(u*u*p0[j] + 2*u*t*p1[j] + t*t*p2[j] for j in (0, 1)))
        else:
            pts.append(tuple(u**3*p0[j] + 3*u*u*t*p1[j] + 3*u*t*t*p2[j] + t**3*p3[j] for j in (0, 1)))
    return pts
def stroke(pts, w): return LineString(pts).buffer(w / 2, cap_style=1, join_style=1)
def outline(g, t): return g.difference(g.buffer(-t))
def rot(g, a, o=(0, 0)): return af.rotate(g, a, origin=o)
def mv(g, x, y): return af.translate(g, x, y)
def sc(g, k, o=(0, 0)): return af.scale(g, k, k, origin=o)

def spiral(cx, cy, r0, r1, turns, a0=0, sgn=1, n=80):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0) + sgn * t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

# ------------------------------------------------------------------ motivos de renda (branco, com furos)
def m_folha(x, y, L, W, a):
    """Folha com nervura: branca com dois furos finos."""
    f = leaf(0, 0, L, W)
    furo = U(leaf(-W * 0.2, 0, L * 0.62, W * 0.22), leaf(W * 0.2, 0, L * 0.62, W * 0.22))
    return mv(rot(f.difference(furo), a), x, y)

def m_flor(x, y, r, n=8, a=0):
    """Margarida: pétalas com furo + miolo com anel de furinhos."""
    pet = leaf(0, -r * 0.55, r * 0.9, r * 0.42)
    pf = leaf(0, -r * 0.58, r * 0.5, r * 0.14)
    g = U(radial(pet, n), C(0, 0, r * 0.32))
    h = U(radial(pf, n), radial(C(0, -r * 0.2, r * 0.05), n, off=180 / n), C(0, 0, r * 0.08))
    return mv(rot(g.difference(h), a), x, y)

def m_rosa(x, y, r, a=0):
    """Rosa łowicka: disco com pétalas em espiral vazadas."""
    g = U(C(0, 0, r), radial(C(0, -r, r * 0.28), 10))
    h = [radial(leaf(r * 0.28, -r * 0.55, r * 0.55, r * 0.16, 30), 6),
         radial(C(0, -r, r * 0.12), 10), C(0, 0, r * 0.16),
         radial(C(0, -r * 0.28, r * 0.06), 6, off=30)]
    return mv(rot(g.difference(U(*h)), a), x, y)

def m_tulipa(x, y, s, a=0):
    p = U(leaf(0, -s * 0.5, s, s * 0.45), leaf(-s * 0.28, -s * 0.38, s * 0.8, s * 0.32, -28),
          leaf(s * 0.28, -s * 0.38, s * 0.8, s * 0.32, 28), C(0, -s * 0.05, s * 0.2))
    h = U(leaf(0, -s * 0.5, s * 0.55, s * 0.13), C(0, -s * 0.05, s * 0.07))
    return mv(rot(p.difference(h), a), x, y)

def m_floco(x, y, r, a=0):
    """Floco de neve fino de 6 braços."""
    arm = U(box(-r * 0.045, -r, r * 0.045, 0),
            *[mv(rot(box(-r * 0.035, -r * L, r * 0.035, 0), s * 45), 0, -r * yy)
              for (yy, L) in [(0.45, 0.32), (0.72, 0.24)] for s in (1, -1)],
            mv(diamond(0, 0, r * 0.22, r * 0.3), 0, -r * 0.9))
    g = U(radial(arm, 6), C(0, 0, r * 0.2))
    h = U(radial(diamond(0, -r * 0.9, r * 0.08, r * 0.12), 6), star(0, 0, 6, r * 0.12, r * 0.05))
    return mv(rot(g.difference(h), a), x, y)

def m_ramo(pts, w, folhas=6, L=60, W=22, lado=1, seed=0):
    """Haste curva com folhinhas alternadas."""
    rnd = random.Random(seed)
    g = [stroke(pts, w)]
    n = len(pts)
    for i in range(1, folhas + 1):
        k = int(i * (n - 1) / (folhas + 1))
        (x0, y0), (x1, y1) = pts[k], pts[min(k + 1, n - 1)]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        s = 1 if i % 2 else -1
        ll = L * (0.75 + 0.4 * rnd.random())
        a = ang + 90 + s * 55
        cx = x0 + math.cos(math.radians(a - 90)) * ll * 0.45
        cy = y0 + math.sin(math.radians(a - 90)) * ll * 0.45
        g.append(leaf(cx, cy, ll, W, a))
    return U(*g)

def m_voluta(x, y, r, a=0, sgn=1, w=None):
    w = w or r * 0.16
    return rot(stroke(spiral(x, y, r * 0.15, r, 1.2, a, sgn), w), 0)

# ------------------------------------------------------------------ preenchimento de faixas de renda
def faixa_vertical(x0, x1, y0, y1, seed=1, lado=1):
    """Renda floral dentro da faixa vertical [x0,x1] x [y0,y1]; lado = lado da borda do vidro (-1 esq, +1 dir)."""
    rnd = random.Random(seed)
    W = x1 - x0; cx = (x0 + x1) / 2
    g = []
    lam = W * 2.2
    pts = [(cx + W * 0.18 * math.sin(2 * math.pi * (y - y0) / lam), y) for y in [y0 + i * 10 for i in range(int((y1 - y0) / 10) + 1)]]
    g.append(stroke(pts, W * 0.045))
    y = y0 + lam * 0.25
    i = 0
    while y < y1 - W * 0.2:
        s = 1 if i % 2 == 0 else -1
        bx = cx + W * 0.18 * math.sin(2 * math.pi * (y - y0) / lam)
        fx = bx + s * W * 0.2
        tipo = i % 4
        r = W * (0.2 + 0.05 * rnd.random())
        if tipo == 0: g.append(m_flor(fx, y, r, 8, rnd.random() * 40))
        elif tipo == 1: g.append(m_rosa(fx, y, r * 0.85))
        elif tipo == 2: g.append(m_floco(fx, y, r * 1.05, rnd.random() * 30))
        else: g.append(m_tulipa(fx, y + r * 0.3, r * 1.6, -s * 70))
        # folhas e ramos para o outro lado
        g.append(m_folha(bx - s * W * 0.22, y + lam * 0.12, W * 0.38, W * 0.15, -s * 60 + rnd.uniform(-15, 15)))
        g.append(m_folha(bx - s * W * 0.16, y - lam * 0.1, W * 0.3, W * 0.12, -s * 120 + rnd.uniform(-15, 15)))
        g.append(m_voluta(bx + s * W * 0.05, y + lam * 0.24, W * 0.12, rnd.uniform(0, 360), s, W * 0.03))
        # pontinhos e floquinhos de preenchimento
        g.append(C(bx - s * W * 0.33, y - lam * 0.02, W * 0.035))
        g.append(m_floco(bx + s * W * 0.33, y + lam * 0.17, W * 0.1, rnd.random() * 60))
        y += lam * 0.36; i += 1
    # borda junto ao caixilho
    ex = x0 if lado < 0 else x1
    g.append(box(min(ex, ex - lado * 14), y0, max(ex, ex - lado * 14), y1))
    return U(*g)

def faixa_horizontal(x0, x1, y0, y1, seed=2):
    rnd = random.Random(seed)
    H = y1 - y0; cy = (y0 + y1) / 2
    g = [box(x0, y0, x1, y0 + 14)]
    lam = H * 2.4
    pts = [(x, cy + H * 0.15 * math.sin(2 * math.pi * (x - x0) / lam)) for x in [x0 + i * 10 for i in range(int((x1 - x0) / 10) + 1)]]
    g.append(stroke(pts, H * 0.045))
    x = x0 + lam * 0.2; i = 0
    while x < x1 - H * 0.2:
        s = 1 if i % 2 == 0 else -1
        by = cy + H * 0.15 * math.sin(2 * math.pi * (x - x0) / lam)
        r = H * 0.22
        if i % 3 == 0: g.append(m_flor(x, by + s * H * 0.12, r, 8, rnd.random() * 40))
        elif i % 3 == 1: g.append(m_rosa(x, by + s * H * 0.12, r * 0.85))
        else: g.append(m_tulipa(x, by + s * H * 0.12, r * 1.5, 180 if s > 0 else 0))
        g.append(m_folha(x + lam * 0.13, by - s * H * 0.18, H * 0.36, H * 0.14, s * 35 + 90))
        g.append(m_folha(x - lam * 0.12, by - s * H * 0.2, H * 0.3, H * 0.12, -s * 35 + 90))
        g.append(C(x + lam * 0.2, by + s * H * 0.25, H * 0.035))
        x += lam * 0.34; i += 1
    return U(*g)

def canto(cx, cy, R, a0, a1, seed=3, w_borda=14):
    """Leque de renda em canto: centro (cx,cy) no canto do vidro, raio R, de a0 a a1 graus."""
    rnd = random.Random(seed)
    g = []
    am = (a0 + a1) / 2
    for k, f in enumerate([0.25, 0.5, 0.75]):
        a = math.radians(a0 + (a1 - a0) * f)
        pts = bez((cx, cy), (cx + R * 0.45 * math.cos(a + 0.25), cy + R * 0.45 * math.sin(a + 0.25)),
                  (cx + R * 0.85 * math.cos(a), cy + R * 0.85 * math.sin(a)))
        g.append(m_ramo(pts, R * 0.025, 5, R * 0.16, R * 0.06, seed=seed + k))
    # flores principais em arco
    for k in range(5):
        a = math.radians(a0 + (a1 - a0) * (k + 0.5) / 5)
        rr = R * (0.55 + 0.12 * (k % 2))
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        r = R * (0.12 + 0.03 * rnd.random())
        g.append([m_rosa, m_flor, m_floco][k % 3](x, y, r) if k % 3 != 1 else m_flor(x, y, r, 8, rnd.random() * 45))
    for k in range(4):
        a = math.radians(a0 + (a1 - a0) * (k + 1) / 5)
        rr = R * 0.33
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        g.append(m_folha(x, y, R * 0.2, R * 0.08, math.degrees(a) + 90 + (35 if k % 2 else -35)))
        g.append(m_voluta(cx + R * 0.82 * math.cos(a), cy + R * 0.82 * math.sin(a), R * 0.08, rnd.uniform(0, 360), 1 if k % 2 else -1, R * 0.018))
    g.append(m_flor(cx + R * 0.16 * math.cos(math.radians(am)), cy + R * 0.16 * math.sin(math.radians(am)), R * 0.13, 6))
    return U(*g)


class Renda:
    """Renda organizada: vinhas (hastes) com flores alternadas e folhas, sem nada sobreposto."""
    def __init__(self, excl=None, gap=14):
        self.g = []; self.ocup = excl if excl is not None else Polygon(); self.gap = gap
    def tenta(self, m, forcar=False):
        if forcar or not m.intersects(self.ocup):
            self.g.append(m); self.ocup = self.ocup.union(m.buffer(self.gap)); return True
        return False
    def vinha(self, pts, r, w, seed=0, tipos=("flor", "rosa", "floco", "tulipa")):
        rnd = random.Random(seed)
        L = LineString(pts)
        haste = stroke(pts, w)
        passo = r * 2.25
        n = int(L.length / passo)
        motivos, folhas = [], []
        for i in range(n):
            d = (i + 0.5) * passo
            p = L.interpolate(d); q = L.interpolate(min(d + 5, L.length))
            ang = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
            s = 1 if i % 2 == 0 else -1
            nx, ny = -math.sin(math.radians(ang)) * s, math.cos(math.radians(ang)) * s
            cx, cy = p.x + nx * r * 0.3, p.y + ny * r * 0.3
            t = tipos[i % len(tipos)]
            a = rnd.choice([0, 15, 30])
            if t == "flor": m = m_flor(cx, cy, r, 8, a)
            elif t == "rosa": m = m_rosa(cx, cy, r * 0.82, a)
            elif t == "floco": m = m_floco(cx, cy, r, a)
            else: m = mv(rot(m_tulipa(0, r * 0.35, r * 1.8), ang + (90 if s > 0 else -90) + 180), cx, cy)
            motivos.append(m)
            # folhas no lado oposto, entre as flores
            for k, dd in enumerate((d + passo * 0.5,)):
                if dd >= L.length: continue
                p2 = L.interpolate(dd); q2 = L.interpolate(min(dd + 5, L.length))
                a2 = math.degrees(math.atan2(q2.y - p2.y, q2.x - p2.x))
                for s2 in (1, -1):
                    th = a2 + s2 * 65
                    folhas.append(mv(rot(m_folha(0, -r * 0.58, r * 1.05, r * 0.42, 0), th + 90), p2.x, p2.y))
        for m in motivos: self.tenta(m)
        self.g.append(haste)
        for f in folhas: self.tenta(f)
    def pontos(self, regiao, r, seed=0):
        """Preenche espaços livres que sobraram com floquinhos e bolinhas."""
        rnd = random.Random(seed)
        minx, miny, maxx, maxy = regiao.bounds
        for _ in range(400):
            x, y = rnd.uniform(minx, maxx), rnd.uniform(miny, maxy)
            if not regiao.contains(Point(x, y)): continue
            m = m_floco(x, y, r, rnd.choice([0, 30])) if rnd.random() < 0.5 else C(x, y, r * 0.22)
            self.tenta(m)
    def geom(self): return U(*self.g)

def onda_pts(x0, y0, x1, y1, amp, lam, vertical=True, passo=8):
    if vertical:
        cx = (x0 + x1) / 2
        return [(cx + amp * math.sin(2 * math.pi * (y - y0) / lam), y) for y in [y0 + i * passo for i in range(int((y1 - y0) / passo) + 1)]]
    cy = (y0 + y1) / 2
    return [(x, cy + amp * math.sin(2 * math.pi * (x - x0) / lam)) for x in [x0 + i * passo for i in range(int((x1 - x0) / passo) + 1)]]

def arco_pts(cx, cy, R, a0, a1, n=60):
    return [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def onda(x0, y0, x1, y1, amp, lam, lado):
    """Polígono de faixa com borda interna ondulada. lado: 'L','R','T','B' = lado colado no caixilho."""
    pts = []
    if lado in "LR":
        n = int((y1 - y0) / 10)
        edge = [((x1 if lado == "L" else x0) + amp * math.sin(2 * math.pi * i * 10 / lam), y0 + i * 10) for i in range(n + 1)]
        if lado == "L": return Polygon([(x0, y0)] + edge + [(x0, y1)])
        return Polygon([(x1, y0)] + edge + [(x1, y1)])
    n = int((x1 - x0) / 10)
    edge = [(x0 + i * 10, (y1 if lado == "T" else y0) + amp * math.sin(2 * math.pi * i * 10 / lam)) for i in range(n + 1)]
    if lado == "T": return Polygon([(x0, y0)] + edge + [(x1, y0)])
    return Polygon([(x0, y1)] + edge + [(x1, y1)])

def leque(cx, cy, R, a0, a1):
    pts = [(cx, cy)] + [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / 40)) * (1 + 0.06 * math.sin(i * 1.3)),
                         cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / 40)) * (1 + 0.06 * math.sin(i * 1.3))) for i in range(41)]
    return Polygon(pts)

# ------------------------------------------------------------------ peças centrais
def floco_grande(x, y, R, a=0):
    """Floco ornamental (os dois do topo): 6 braços de pétalas vazadas."""
    arm = U(outline(leaf(0, -R * 0.55, R * 0.9, R * 0.36), R * 0.045),
            leaf(0, -R * 0.52, R * 0.42, R * 0.13),
            leaf(0, -R * 0.93, R * 0.2, R * 0.1),
            rot(leaf(0, -R * 0.92, R * 0.18, R * 0.07), 28, (0, -R * 0.82)),
            rot(leaf(0, -R * 0.92, R * 0.18, R * 0.07), -28, (0, -R * 0.82)),
            C(0, -R * 0.08, R * 0.06))
    mid = U(leaf(0, -R * 0.5, R * 0.42, R * 0.16), C(0, -R * 0.75, R * 0.045))
    g = U(radial(arm, 6), radial(mid, 6, off=30), outline(C(0, 0, R * 0.24), R * 0.04),
          star(0, 0, 6, R * 0.17, R * 0.08))
    g = g.difference(radial(leaf(0, -R * 0.5, R * 0.2, R * 0.06), 6, off=30))
    return mv(rot(g, a), x, y)

def floco_central(x, y, R):
    """Floco central de 12 losangos: contorno branco e miolo vermelho."""
    branco, verm = [], []
    for k in range(12):
        L = R if k % 2 == 0 else R * 0.78
        d = Polygon([(0, -R * 0.2), (R * 0.12, -(R * 0.2 + L) / 2 - R * 0.06), (0, -L), (-R * 0.12, -(R * 0.2 + L) / 2 - R * 0.06)])
        d = rot(d, 30 * k)
        branco.append(outline(d, R * 0.035))
        inner = d.buffer(-R * 0.035)
        dots = U(*[rot(C(0, -R * f, R * 0.016), 30 * k) for f in (0.38, 0.52, 0.66)][: 3 if k % 2 == 0 else 2])
        branco.append(dots)
        verm.append(inner.difference(dots.buffer(R * 0.01)))
        branco.append(rot(C(0, -L - R * 0.04, R * 0.03), 30 * k))
    branco.append(outline(C(0, 0, R * 0.2), R * 0.03))
    verm.append(star(0, 0, 8, R * 0.16, R * 0.07))
    branco.append(star(0, 0, 8, R * 0.06, R * 0.03))
    # coroa/gancho no topo
    branco.append(U(m_tulipa(0, -R * 1.15, R * 0.22), box(-R * 0.012, -R * 1.08, R * 0.012, -R * 1.0)))
    return mv(U(*branco), x, y), mv(U(*verm).difference(U(*branco)), x, y)

def bola(x, y, r):
    """Bola vermelha pendurada com floco branco."""
    verm = C(x, y, r)
    br = U(outline(C(x, y, r), r * 0.05), m_floco(x, y, r * 0.72),
           box(x - r * 0.18, y - r * 1.12, x + r * 0.18, y - r * 0.94),
           radial(C(0, -r * 0.86, r * 0.035), 16).__class__ and mv(radial(C(0, -r * 0.86, r * 0.035), 16), x, y))
    return br, verm.difference(br.buffer(r * 0.02))

def brilho(x, y, s): return star(x, y, 4, s, s * 0.22, a=-90)

def texto(s, x, y, altura, fontes=FONTES):
    fs = [TTFont(f) for f in fontes]
    upm = fs[0]["head"].unitsPerEm
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
    pen_x = 0; out = Polygon()
    for ch in s:
        for f in fs:
            cm_ = f.getBestCmap()
            if ord(ch) in cm_:
                gs = f.getGlyphSet(); gn = cm_[ord(ch)]; break
        p = P(gs); gs[gn].draw(p)
        g = Polygon()
        for r in p.rings:
            g = g.symmetric_difference(Polygon([(pen_x + px, -py) for px, py in r]).buffer(0))
        out = out.union(g)
        pen_x += gs[gn].width
    capH = 700  # altura de referência de Lobster (unidades)
    k = altura / capH
    out = sc(out, k)
    b = out.bounds
    return mv(out, x - (b[0] + b[2]) / 2, y)

# ------------------------------------------------------------------ portas
def porta_esquerda(W=1390, H=2400):
    branco, verm = [], []
    # renda das bordas (densa, borda interna ondulada)
    # medalhões grandes nas laterais (altura do floco central)
    branco.append(m_flor(W * 0.08, H * 0.56, W * 0.13, 12))
    branco.append(m_flor(W * 0.9, H * 0.56, W * 0.12, 12, 15))
    # flocos do topo
    branco.append(floco_grande(W * 0.28, H * 0.135, W * 0.135, 0))
    branco.append(floco_grande(W * 0.73, H * 0.135, W * 0.135, 30))
    # laço e festões vermelhos com bordinha branca
    for s in (-1, 1):
        p = bez((W * 0.5 + s * W * 0.02, H * 0.14), (W * 0.5 + s * W * 0.05, H * 0.215), (W * 0.5 + s * W * 0.17, H * 0.245), (W * 0.5 + s * W * 0.235, H * 0.248))
        verm.append(stroke(p, W * 0.034))
        # bordinha recortada (festão) abaixo da fita
        ln = LineString(p).parallel_offset(W * 0.024, 'left' if s < 0 else 'right')
        pts = list(ln.coords) if ln.geom_type == "LineString" else []
        if pts:
            branco.append(stroke(pts, W * 0.008))
            L = LineString(pts)
            for i in range(1, 22):
                q = L.interpolate(i / 22, normalized=True)
                branco.append(outline(C(q.x, q.y, W * 0.011), W * 0.004))
        # flor vermelha (bico-de-papagaio) na ponta e fita caindo
        fx, fy = W * 0.5 + s * W * 0.25, H * 0.25
        pet = leaf(0, -W * 0.05, W * 0.075, W * 0.032)
        flor = mv(U(radial(pet, 7), C(0, 0, W * 0.02)), fx, fy)
        verm.append(flor)
        branco.append(mv(U(radial(leaf(0, -W * 0.05, W * 0.04, W * 0.007), 7), radial(C(0, -W * 0.012, W * 0.006), 5)), fx, fy))
        tail = bez((fx + s * W * 0.02, fy + W * 0.03), (fx + s * W * 0.08, fy + H * 0.05), (fx + s * W * 0.01, fy + H * 0.08), (fx + s * W * 0.05, fy + H * 0.115))
        verm.append(stroke(tail, W * 0.012))
    # laço
    lc = U(outline(leaf(-W * 0.045, H * 0.122, W * 0.085, W * 0.045, -70), W * 0.01),
           outline(leaf(W * 0.045, H * 0.122, W * 0.085, W * 0.045, 70), W * 0.01), C(0, H * 0.128, W * 0.014))
    verm.append(mv(lc, W * 0.5, 0))
    # texto
    branco.append(texto("Wesołych", W * 0.5, H * 0.365, W * 0.075))
    branco.append(texto("Świąt", W * 0.53, H * 0.437, W * 0.075))
    # brilhos
    for (u, v, s) in [(0.27, 0.32, 24), (0.25, 0.395, 30), (0.56, 0.275, 18), (0.6, 0.297, 22), (0.4, 0.28, 18), (0.72, 0.405, 14), (0.78, 0.43, 22), (0.33, 0.335, 12)]:
        branco.append(brilho(W * u, H * v, s))
    # volutas acima do floco central
    for s in (-1, 1):
        cx = W * 0.5 + s * W * 0.16
        pts = bez((W * 0.5 + s * W * 0.05, H * 0.455), (cx, H * 0.43), (cx + s * W * 0.1, H * 0.445), (cx + s * W * 0.07, H * 0.475))
        branco.append(stroke(pts, W * 0.008))
        branco.append(stroke(spiral(cx + s * W * 0.05, H * 0.47, 6, W * 0.025, 1.0, 180 if s < 0 else 0, s), W * 0.007))
        branco.append(leaf(cx - s * W * 0.02, H * 0.437, W * 0.035, W * 0.012, s * 60))
    # floco central
    fb, fv = floco_central(W * 0.495, H * 0.565, W * 0.19)
    branco.append(fb); verm.append(fv)
    # bolas penduradas
    for (u, v, r) in [(0.37, 0.705, 0.067), (0.62, 0.7, 0.048)]:
        br, vr = bola(W * u, H * v, W * r)
        branco.append(br); verm.append(vr)
        branco.append(box(W * u - 2.5, H * 0.62, W * u + 2.5, H * v - W * r * 1.1))
    centro = U(*branco, *verm)
    R = Renda(excl=centro.buffer(W * 0.012), gap=W * 0.007)
    r = W * 0.06; w = W * 0.011
    R.vinha(onda_pts(W * 0.03, H * 0.02, W * 0.17, H * 0.99, W * 0.025, W * 0.5), r, w, seed=1)
    R.vinha(onda_pts(W * 0.83, H * 0.02, W * 0.97, H * 0.96, W * 0.025, W * 0.5), r, w, seed=2, tipos=("rosa", "flor", "tulipa", "floco"))
    R.vinha(onda_pts(W * 0.15, H * 0.005, W * 0.85, H * 0.06, H * 0.008, W * 0.45, vertical=False), r * 0.8, w, seed=3, tipos=("floco", "flor", "rosa", "tulipa"))
    R.vinha(arco_pts(0, H, W * 0.3, -88, -2), r * 0.9, w, seed=4, tipos=("tulipa", "flor", "rosa"))
    R.vinha(arco_pts(0, 0, W * 0.2, 5, 85), r * 0.8, w, seed=6, tipos=("rosa", "flor"))
    R.vinha(arco_pts(W, 0, W * 0.2, 95, 175), r * 0.8, w, seed=7, tipos=("flor", "rosa"))
    R.pontos(U(box(0, 0, W * 0.2, H), box(W * 0.8, 0, W, H * 0.96), box(0, 0, W, H * 0.08)), W * 0.025, seed=5)
    branco.append(R.geom())
    branco.append(U(box(0, 0, W, 16), box(0, 0, 16, H), box(W - 16, 0, W, H * 0.96)))
    B = U(*branco).intersection(box(0, 0, W, H))
    V = U(*verm).intersection(box(0, 0, W, H)).difference(B)
    return B, V

def porta_direita(W=1520, H=2400):
    R = Renda(gap=W * 0.007)
    r = W * 0.055; w = W * 0.01
    for k, (rr, tp) in enumerate([(0.2, ("flor",)), (0.4, ("rosa", "flor", "floco")), (0.6, ("tulipa", "flor", "rosa", "floco"))]):
        R.vinha(arco_pts(0, 0, W * rr, 4, 86), r, w, seed=10 + k, tipos=tp)
        R.vinha(arco_pts(0, H, W * rr * 1.1, -86, -4), r, w, seed=20 + k, tipos=tp)
    R.pontos(U(Point(0, 0).buffer(W * 0.66), Point(0, H).buffer(W * 0.72)), W * 0.023, seed=7)
    B = U(R.geom(), box(0, 0, W * 0.62, 16), box(0, 0, 16, W * 0.62), box(0, H - 16, W * 0.68, H), box(0, H - W * 0.68, 16, H))
    return B.intersection(box(0, 0, W, H)), Polygon()

def limpa(g, r=1.0):
    """Abertura morfológica: elimina partes mais finas que 2r mm."""
    return g.buffer(-r, 16).buffer(r, 16).buffer(0)

if __name__ == "__main__":
    import sys, json, os, pickle
    out = {}
    for nome, fn in [("porta-esquerda", porta_esquerda), ("porta-direita", porta_direita)]:
        B, V = fn()
        B = limpa(B); V = limpa(V) if not V.is_empty else V
        out[nome] = (B, V)
        print(nome, "branco área m²:", round(B.area / 1e6, 3), "vermelho:", round(V.area / 1e6, 3))
    pickle.dump(out, open(sys.argv[1], "wb"))
