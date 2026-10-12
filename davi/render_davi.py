"""Reel 'O gigante foi a parte fácil' — Davi em partículas P&B. Gera frames, trilha, mixa narração e exporta MP4."""
import json, os, sys, wave, subprocess
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.signal import fftconvolve, resample_poly
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
OUTFILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "reel_davi_50s.mp4")
ONLY = [float(x) for x in sys.argv[2:]]  # tempos para prévia
W, H, FPS, SS, N = 1080, 1920, 30, 2, 2600
CX, CY = W / 2, 860
FR = os.path.join(HERE, "frames"); os.makedirs(FR, exist_ok=True)
rng = np.random.default_rng(11)

F = "/usr/share/fonts/opentype/inter/"
def font(n, s): return ImageFont.truetype(F + n, s)
f_cap, f_ui, f_lbl = font("Inter-SemiBold.otf", 50), font("Inter-Medium.otf", 26), font("Inter-Bold.otf", 34)

# ---------- linha do tempo a partir da narração ----------
NARR = json.load(open(os.path.join(HERE, "narr", "timing.json")))
LEAD, TAIL = 0.25, 0.35
S, D, acc = [], [], 0.0
for i, x in enumerate(NARR):
    d = LEAD + x["dur"] + TAIL + (1.6 if i == len(NARR) - 1 else 0)
    S.append(acc); D.append(d); acc += d
TOTAL = acc
NF = int(TOTAL * FPS)
def at(i, frac):  # instante em que a fala i chega a 'frac' do texto
    return S[i] + LEAD + NARR[i]["dur"] * frac

# ---------- formas ----------
def from_mask(draw_fn, grid=13, n=N, var=True):
    img = Image.new("L", (W, H), 0); draw_fn(ImageDraw.Draw(img), img)
    return sample(np.array(img), grid, n, var)

def sample(a, grid, n=N, var=True):
    ys, xs = np.mgrid[0:H:grid, 0:W:grid]
    m = a[ys, xs] > 100
    pts = np.stack([xs[m], ys[m]], 1).astype(float)
    idx = rng.choice(len(pts), n, replace=len(pts) < n)
    s = rng.uniform(0.75, 1.1, n) if var else np.ones(n)
    if var == "shade": s = 0.45 + 0.6 * (a[ys, xs][m][idx] / 255)
    return pts[idx] + rng.normal(0, 1.3, (n, 2)), s

def giant_draw(d, img=None):
    d.ellipse([485, 505, 595, 615], fill=255)                       # cabeça
    d.polygon([(480, 520), (540, 455), (600, 520)], fill=255)      # elmo
    d.rectangle([520, 600, 560, 640], fill=255)                     # pescoço
    d.polygon([(430, 640), (650, 640), (615, 900), (465, 900)], fill=255)  # tronco
    d.polygon([(430, 640), (470, 655), (420, 900), (385, 890)], fill=255)  # braço esq
    d.polygon([(650, 640), (610, 655), (665, 900), (700, 890)], fill=255)  # braço dir
    d.ellipse([320, 720, 450, 930], fill=255)                       # escudo
    d.line([(700, 430), (690, 1250)], fill=255, width=16)           # lança
    d.polygon([(700, 380), (715, 440), (685, 440)], fill=255)
    d.polygon([(465, 900), (535, 900), (530, 1240), (480, 1240)], fill=255)  # pernas
    d.polygon([(545, 900), (615, 900), (600, 1240), (550, 1240)], fill=255)

def giant_fallen():
    img = Image.new("L", (W, H), 0); giant_draw(ImageDraw.Draw(img))
    img = img.rotate(-84, center=(540, 840), translate=(0, 330), resample=Image.BILINEAR)
    return sample(np.array(img), 13)

def lion_draw(d, img=None, cx=540, cy=820):
    lr = np.random.default_rng(5)
    for r0, r1, n, w, off, fill in [(150, 330, 22, 0.17, 0.0, 185), (130, 265, 22, 0.15, np.pi / 22, 215)]:
        for kk in range(n):
            a = 2 * np.pi * kk / n + off + lr.uniform(-.05, .05); rr1 = r1 * lr.uniform(.85, 1.12)
            sw = lr.uniform(.18, .38); L, R = [], []
            for t in np.linspace(0, 1, 14):
                r = r0 + (rr1 - r0) * t; half = w * (1 - t) ** 0.8 + 0.01
                for side, lst in ((-1, L), (1, R)):
                    aa = a + sw * t ** 1.5 + side * half
                    lst.append((cx + r * np.cos(aa), cy + r * 1.08 * np.sin(aa) + 30))
            d.polygon(L + R[::-1], fill=fill)
    d.ellipse([cx - 245, cy - 225, cx + 245, cy + 285], fill=225)
    face = [(-135, -150), (-60, -185), (0, -190), (60, -185), (135, -150), (165, -60), (150, 40), (110, 130),
            (60, 190), (0, 210), (-60, 190), (-110, 130), (-150, 40), (-165, -60)]
    d.polygon([(cx + x * 1.17, cy + y * 1.14 + 12) for x, y in face], fill=0)
    d.polygon([(cx + x, cy + y) for x, y in face], fill=255)
    for sd in (-1, 1):
        d.ellipse([cx + sd * 150 - 44, cy - 212, cx + sd * 150 + 44, cy - 124], fill=0)
        d.ellipse([cx + sd * 150 - 26, cy - 193, cx + sd * 150 + 26, cy - 142], fill=255)
        ex = cx + sd * 68
        d.polygon([(ex - sd * 46, cy - 38), (ex, cy - 64), (ex + sd * 44, cy - 44), (ex, cy - 18)], fill=0)
        d.line([(ex - sd * 45, cy - 78), (ex + sd * 40, cy - 92)], fill=0, width=15)
        d.line([(cx + sd * 22, cy - 50), (cx + sd * 30, cy + 40)], fill=0, width=13)
    d.polygon([(cx - 58, cy + 40), (cx + 58, cy + 40), (cx + 26, cy + 90), (cx - 26, cy + 90)], fill=0)
    d.line([(cx, cy + 85), (cx, cy + 115)], fill=0, width=14)
    d.arc([cx - 75, cy + 70, cx + 2, cy + 140], 20, 140, fill=0, width=14)
    d.arc([cx - 2, cy + 70, cx + 75, cy + 140], 40, 160, fill=0, width=14)

def king_draw(d, img=None):
    d.ellipse([480, 520, 600, 640], fill=255)                                        # cabeça
    d.polygon([(470, 530), (470, 450), (505, 490), (540, 430), (575, 490), (610, 450), (610, 530)], fill=255)  # coroa
    d.rectangle([470, 515, 610, 532], fill=0)
    d.rectangle([520, 630, 560, 670], fill=255)
    d.polygon([(450, 670), (630, 670), (720, 1240), (360, 1240)], fill=255)          # manto
    d.line([(540, 690), (540, 1240)], fill=0, width=14)
    d.polygon([(450, 670), (400, 700), (370, 900), (410, 905)], fill=255)            # braços
    d.polygon([(630, 670), (680, 700), (710, 900), (670, 905)], fill=255)

def harp_draw(d, img=None):
    d.line([(370, 1200), (370, 560)], fill=255, width=34)
    xs = np.linspace(370, 740, 40); ys = 600 - 70 * np.sin((xs - 370) / 370 * np.pi) + (xs - 370) * 0.12
    d.line(list(zip(xs, ys)), fill=255, width=30)
    d.line([(740, 645), (400, 1190)], fill=255, width=38)
    for x in np.arange(420, 720, 34):
        ytop = np.interp(x, xs, ys); ybot = 645 + (740 - x) / 340 * 545
        d.line([(x, ytop), (x, ybot)], fill=255, width=9)

def crown_draw(d, img=None):
    d.polygon([(290, 1080), (290, 690), (415, 880), (540, 620), (665, 880), (790, 690), (790, 1080)], fill=255)
    d.rectangle([290, 990, 790, 1010], fill=0)
    for x, y in [(290, 690), (540, 620), (790, 690)]:
        d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=255)
    for x in (400, 540, 680):
        d.ellipse([x - 26, 925, x + 26, 977], fill=0)

def flock_draw(d, img=None):
    sheep = [(250, 1010, .8), (420, 980, .7), (600, 1000, .75), (780, 990, .8), (330, 1120, 1), (560, 1130, 1.05),
             (800, 1120, 1), (200, 1230, 1.2), (470, 1250, 1.25), (740, 1250, 1.2), (930, 1180, 1.0)]
    for x, y, s in sheep:
        for dx, dy, r in [(-30, 0, 34), (0, -12, 38), (30, 0, 34), (0, 12, 32)]:
            d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill=255)
        d.ellipse([x - 78 * s, y - 28 * s, x - 40 * s, y + 10 * s], fill=255)          # cabeça
        d.rectangle([x - 25 * s, y + 25 * s, x - 15 * s, y + 58 * s], fill=255)
        d.rectangle([x + 15 * s, y + 25 * s, x + 25 * s, y + 58 * s], fill=255)
    # pastor pequeno ao fundo
    d.ellipse([95, 650, 145, 700], fill=255); d.polygon([(85, 705), (155, 705), (165, 900), (75, 900)], fill=255)
    d.line([(180, 620), (180, 900)], fill=255, width=12); d.arc([150, 590, 210, 650], 180, 360, fill=255, width=12)

def text_draw(txt, size, cy=CY):
    def f(d, img=None):
        fnt = font("InterDisplay-Bold.otf", size); bb = d.textbbox((0, 0), txt, font=fnt)
        d.text((CX - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), txt, font=fnt, fill=255)
    return f

def phones_draw(d, img=None):
    for r in range(3):
        for c in range(3):
            x, y = 205 + c * 235, 470 + r * 285
            d.rounded_rectangle([x, y, x + 200, y + 255], 28, outline=255, width=18)
            d.ellipse([x + 75, y + 70, x + 125, y + 120], fill=255)
            d.pieslice([x + 50, y + 130, x + 150, y + 230], 180, 360, fill=255)

def heart_draw(d, img=None):
    t = np.linspace(0, 2 * np.pi, 200)
    x = 16 * np.sin(t) ** 3; y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    d.polygon(list(zip(CX + x * 24, CY - 40 - y * 24)), fill=255)

def bars_draw(d, img=None):
    hs, bw, gap = [140, 230, 330, 450, 590], 120, 46
    x0 = CX - (5 * bw + 4 * gap) / 2
    for i, h in enumerate(hs):
        d.rectangle([x0 + i * (bw + gap), 1160 - h, x0 + i * (bw + gap) + bw, 1160], fill=255)

k = np.arange(N) + 0.5
phi = np.arccos(1 - 2 * k / N); th = np.pi * (1 + 5 ** 0.5) * k
S3 = np.stack([np.sin(phi) * np.cos(th), np.cos(phi), np.sin(phi) * np.sin(th)], 1)
def sphere(t, R=340):
    a = t * 0.8
    x = S3[:, 0] * np.cos(a) + S3[:, 2] * np.sin(a); z = -S3[:, 0] * np.sin(a) + S3[:, 2] * np.cos(a)
    y = S3[:, 1]; tl = 0.35
    y2 = y * np.cos(tl) - z * np.sin(tl); z2 = y * np.sin(tl) + z * np.cos(tl)
    return np.stack([CX + x * R, CY + y2 * R], 1), 0.3 + 0.85 * (z2 + 1) / 2

DUST0 = np.stack([rng.uniform(60, 1020, N), rng.uniform(380, 1380, N)], 1)
DV = rng.normal(0, 1, (N, 2)) * [14, 8] + [0, 18]
def dust(t): return DUST0 + DV * np.sin(t * 0.4) * 2.5, np.full(N, 0.45)

static = {n: from_mask(fn) for n, fn in [("giant", giant_draw), ("king", king_draw), ("crown", crown_draw),
          ("flock", flock_draw), ("30", text_draw("30", 600)), ("phones", phones_draw), ("heart", heart_draw),
          ("bars", bars_draw), ("2", text_draw("2", 820))]}
static["lion"] = from_mask(lion_draw, grid=9, var="shade")
static["harp"] = from_mask(harp_draw, grid=10)
static["fallen"] = giant_fallen()
def shape(name, t):
    if name == "sphere": return sphere(t)
    if name == "dust": return dust(t)
    return static[name]

KEYS = [(-1.0, "dust"), (0.0, "giant"), (S[1], "dust"), (S[2], "flock"), (S[3], "lion"), (at(3, .5), "harp"),
        (S[4], "crown"), (at(4, .42), "dust"), (at(4, .72), "flock"), (S[5], "30"), (S[6], "phones"),
        (S[7], "sphere"), (S[8], "heart"), (S[9], "bars"), (S[10], "giant"), (at(10, .2), "fallen"),
        (at(10, .45), "lion"), (S[11], "giant"), (at(11, .52), "king"), (at(11, .74), "2")]
MD = 0.85
delay = rng.uniform(0, 0.3, N)
burst = rng.normal(0, 1, (N, 2)) * 150
def ease_io(x): x = np.clip(x, 0, 1); return np.where(x < .5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)

def state(t):
    i = max(j for j, (tk, _) in enumerate(KEYS) if tk <= t)
    p, s = shape(KEYS[i][1], t)
    if i > 0:
        u = (t - KEYS[i][0]) / MD
        if u < 1:
            p0, s0 = shape(KEYS[i - 1][1], t)
            uu = ease_io((u - delay) / 0.7)
            p = p0 * (1 - uu[:, None]) + p * uu[:, None] + np.sin(np.pi * uu)[:, None] * burst
            s = s0 * (1 - uu) + s * uu
    p = p + np.stack([np.sin(t * 3 + k * .7), np.cos(t * 2.6 + k * 1.3)], 1) * 1.4
    return p, s

# ---------- terreno ----------
gx, gz = np.meshgrid(np.linspace(-1.6, 1.6, 46), np.linspace(0.15, 1.0, 22))
def terrain(d, t, fade):
    hgt = 0.06 * np.sin(gx * 4 + t * 1.2) * np.cos(gz * 7 - t * .7) + 0.04 * np.sin(gx * 9 - t * 1.4)
    f = 1 / (gz + 0.25)
    X = CX + gx * 520 * f * 0.55; Y = 1460 + (0.6 - hgt) * 240 * f * 0.55 - 180
    r = 1.2 + 2.0 * (1 - gz); al = (40 + 110 * (1 - gz)) * fade
    for x, y, rr, a in zip(X.ravel(), Y.ravel(), r.ravel(), al.ravel()):
        d.ellipse([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS], fill=int(a))

# ---------- textos ----------
SPLIT = ["Davi derrubou um gigante|de quase três metros|com uma única pedra.",
         "Mas a parte mais importante|dessa história|não aconteceu|no campo de batalha.",
         "Aconteceu antes.|Sozinho.|Cuidando de ovelhas|que ninguém via.",
         "Ali ele enfrentou|leão e urso.|Ali ele aprendeu a tocar.",
         "Foi ungido rei ainda jovem.|E não ganhou a coroa.|Voltou pro pasto.",
         "Só se tornou rei|aos trinta anos.",
         "Hoje a gente vive o contrário:|tudo é palco.|Tudo precisa ser visto.",
         "Mas Deus não escolheu Davi|pelo que as pessoas viam.",
         "“O homem vê o exterior,|mas o Senhor vê o coração.”",
         "Talvez o seu tempo escondido|não seja atraso.|Seja treino.",
         "Quem vence o gigante em público|já venceu o leão|em secreto.",
         "Só que o maior gigante|da vida de Davi|não foi Golias.|Foi ele mesmo.|Isso fica pra parte dois."]
def chunks(i):
    parts = SPLIT[i].split("|")
    tot = sum(len(p) for p in parts); out, c = [], 0
    for p in parts:
        a = at(i, c / tot); c += len(p)
        out.append([a - 0.08, None, p])
    for j in range(len(out) - 1): out[j][1] = out[j + 1][0]
    out[-1][1] = S[i] + D[i] - 0.05
    return [tuple(o) for o in out]
CAPS = [c for i in range(len(NARR)) for c in chunks(i)]

def lab(i, a, b, txt): return (a, b, txt)
LBL = [(0.3, at(0, .55), "GOLIAS"), (at(0, .55), S[1], "1 PEDRA"),
       (S[1] + .3, S[2], "O CAMPO DE BATALHA"),
       (S[2] + .2, at(2, .3), "ANTES"), (at(2, .3), S[3], "SOZINHO"),
       (S[3] + .2, at(3, .5), "LEÃO · URSO"), (at(3, .5), S[4], "HARPA"),
       (S[4] + .2, at(4, .42), "UNGIDO"), (at(4, .72), S[5], "DE VOLTA AO PASTO"),
       (S[5] + .2, S[6], "REI AOS 30"),
       (S[6] + .2, S[7], "VISTO"), (S[7] + .2, S[8], "O QUE AS PESSOAS VIAM"),
       (S[8] + .2, S[9], "O CORAÇÃO"), (S[9] + .2, at(9, .55), "ATRASO"), (at(9, .55), S[10], "TREINO"),
       (S[10] + .2, at(10, .55), "EM PÚBLICO"), (at(10, .55), S[11], "EM SECRETO"),
       (S[11] + .2, at(11, .56), "O MAIOR GIGANTE"), (at(11, .52), at(11, .74), "ELE MESMO"), (at(11, .74), TOTAL + 1, "PARTE 2")]
REFS = ["1 SM 17:4", "1 SM 17", "1 SM 16:11", "1 SM 17:34", "1 SM 16:13", "2 SM 5:4", "HOJE", "1 SM 16:7",
        "1 SM 16:7", "1 SM 17:37", "1 SM 17:50", "2 SM 11"]

def fade(t, a, b, f=0.18): return float(np.clip(min((t - a) / f, (b - t) / f), 0, 1))

def overlays(img, t):
    d = ImageDraw.Draw(img)
    sc = max(j for j in range(len(S)) if S[j] <= t)
    d.text((70, 90), "DAVI — Nº 01", font=f_ui, fill=170)
    d.text((W - 70, 90), REFS[sc], font=f_ui, fill=170, anchor="ra")
    d.line([(70, 140), (W - 70, 140)], fill=60, width=2)
    for i in range(40):
        x = 70 + i * (W - 140) / 39; on = i / 39 <= t / TOTAL
        d.line([(x, 1700), (x, 1726 if on else 1712)], fill=230 if on else 70, width=3)
    for a, b, s in LBL:
        al = fade(t, a, b)
        if al > 0:
            n = int(len(s) * np.clip((t - a) / 0.3, 0, 1))
            d.text((CX, 380 + (1 - al) * 10), s[:n], font=f_lbl, fill=int(255 * al), anchor="mm")
            if s == "O CAMPO DE BATALHA" and t > a + .7:
                w = d.textlength(s, font=f_lbl); u = min(1, (t - a - .7) / .4)
                d.line([(CX - w / 2 - 10, 380), (CX - w / 2 - 10 + (w + 20) * u, 380)], fill=int(255 * al), width=4)
    # régua de altura do gigante
    al = fade(t, 0.6, S[1] - .1)
    if al > 0:
        x = 830; d.line([(x, 455), (x, 1240)], fill=int(150 * al), width=2)
        for y in np.linspace(455, 1240, 12): d.line([(x - 10, y), (x + 10, y)], fill=int(150 * al), width=2)
        v = min(2.9, 2.9 * (t - .6) / 1.2)
        d.text((x + 24, 850), f"{v:.1f} M".replace(".", ","), font=f_lbl, fill=int(230 * al), anchor="lm")
    # linha do tempo unção → trono
    al = fade(t, S[5] + .3, S[6] - .05)
    if al > 0:
        u = min(1, (t - S[5] - .3) / 1.2); x0, x1 = 160, 920
        d.line([(x0, 1260), (x0 + (x1 - x0) * u, 1260)], fill=int(220 * al), width=3)
        d.text((x0, 1300), "UNÇÃO", font=f_ui, fill=int(200 * al), anchor="lm")
        if u > .95: d.text((x1, 1300), "TRONO", font=f_ui, fill=int(200 * al), anchor="rm")
    # contador de visualizações
    if S[6] + .4 < t < S[7]:
        v = int(10 ** min(6, (t - S[6] - .4) / 2.2 * 6))
        d.text((CX, 1345), f"{v:,} VISUALIZAÇÕES".replace(",", "."), font=f_lbl, fill=220, anchor="mm")
    al = fade(t, S[9] + .2, S[10])
    if al > 0:
        x0 = CX - (5 * 120 + 4 * 46) / 2
        for i in range(5):
            d.text((x0 + i * 166 + 60, 1200), f"0{i+1}", font=f_ui, fill=int(200 * al), anchor="mm")
    al = fade(t, at(11, .9), TOTAL + 1, .3)
    if al > 0:
        d.text((CX, 1345), "SEGUE PRA NÃO PERDER  →", font=f_lbl, fill=int(235 * al), anchor="mm")
    for a, b, s in CAPS:
        al = fade(t, a, b, 0.07)
        if al > 0:
            d.text((CX, 1560 + (1 - al) * 12), s, font=f_cap, fill=int(255 * al), anchor="mm")

GRAIN = [rng.normal(0, 7, (H, W)).astype(np.float32) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
VIGN = np.clip(1 - 0.55 * (((xx - CX) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2.2, 0.35, 1).astype(np.float32)
HIT = at(0, .85)

def render(fi):
    t = fi / FPS
    master = float(np.clip((TOTAL - t) / 0.35, 0, 1)) if t > TOTAL - 0.35 else 1.0
    big = Image.new("L", (W * SS, H * SS), 0); d = ImageDraw.Draw(big)
    terrain(d, t, 1.0)
    p, s = state(t)
    for (x, y), sc in zip(p[np.argsort(s)], np.sort(s)):
        r = 3.6 * sc; c = int(np.clip(90 + 165 * sc, 0, 255))
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=c)
    # a pedra
    if HIT - 0.9 < t < HIT:
        u = (t - (HIT - 0.9)) / 0.9
        x = 120 + (535 - 120) * u; y = 1350 - (1350 - 560) * u - 260 * np.sin(np.pi * u)
        for j in range(8):
            uj = max(0, u - j * 0.02); xj = 120 + 415 * uj; yj = 1350 - 790 * uj - 260 * np.sin(np.pi * uj)
            r = 9 - j; d.ellipse([(xj - r) * SS, (yj - r) * SS, (xj + r) * SS, (yj + r) * SS], fill=255 - j * 25)
    img = big.resize((W, H), Image.LANCZOS)
    a = np.asarray(img, np.float32); a = a + 0.6 * np.asarray(img.filter(ImageFilter.GaussianBlur(10)), np.float32)
    if HIT <= t < HIT + 0.35: a += 120 * (1 - (t - HIT) / 0.35)  # flash
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); overlays(img, t)
    a = (np.asarray(img, np.float32) * VIGN + GRAIN[fi % 6]) * master
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f"{FR}/f{fi:05d}.png")

# ---------- áudio ----------
def audio():
    SR = 44100; ts = np.arange(int(SR * TOTAL)) / SR; mu = np.zeros_like(ts); n = rng.normal(0, 1, len(ts))
    def lp(x, a):
        from scipy.signal import lfilter
        return lfilter([a], [1, a - 1], x)
    def tone(f, t0, dur, g, att=1.2, rel=1.5):
        m = (ts >= t0) & (ts < t0 + dur + rel); tt = ts[m] - t0
        env = np.clip(tt / att, 0, 1) * np.clip((t0 + dur + rel - ts[m]) / rel, 0, 1)
        mu[m] += g * env * (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * 2 * f * tt + .5 * np.sin(2 * np.pi * .3 * tt)))
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    # Ré menor até a virada (cena 7), depois Sib → Fá → Ré maior
    prog = [(0, [50, 57, 62, 65]), (S[3], [46, 53, 58, 62]), (S[5], [48, 55, 60, 64]), (S[6], [50, 57, 62, 65]),
            (S[7], [46, 53, 58, 62, 65]), (S[8], [41, 48, 57, 60, 65]), (S[9], [43, 50, 58, 62]),
            (S[10], [50, 57, 62, 66, 69]), (S[11], [38, 45, 50, 53]), (at(11, .52), [38, 50, 51, 53])]
    for j, (t0, notes) in enumerate(prog):
        t1 = prog[j + 1][0] if j + 1 < len(prog) else TOTAL
        for m in notes: tone(hz(m), t0, t1 - t0, 0.018, rel=1.2)
    beat = 60 / 76
    for bt in [b for b in np.arange(0.0, TOTAL, beat) if not (at(11, .5) < b < at(11, .62))]:
        for off, g in ((0, .3), (.18, .18)):
            m = ts >= bt + off; tt = ts[m] - bt - off
            mu[m] += g * np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 11)
    wh = lp(n, 0.06)
    for tk, _ in KEYS[1:]:
        env = np.exp(-((ts - tk - MD / 2) / 0.3) ** 2); mu += 0.25 * wh * env
    for a, b, s in LBL:
        m = (ts >= a) & (ts < a + .025); mu[m] += .08 * np.sign(np.sin(2 * np.pi * 2600 * ts[m]))
    for tk, g in ((HIT, 1.0), (at(10, .2) + .6, .8), (at(11, .52), 1.0), (at(11, .74), .9)):
        m = ts >= tk; tt = ts[m] - tk
        mu[m] += g * (.9 * np.sin(2 * np.pi * (60 * np.exp(-tt * 3) + 38) * tt) * np.exp(-tt * 4)
                      + .3 * lp(n[m], .2) * np.exp(-tt * 18))
    mu /= np.abs(mu).max()
    voice = np.zeros_like(ts); ir = rng.normal(0, 1, int(SR * 1.2)) * np.exp(-np.arange(int(SR * 1.2)) / SR * 5)
    for i, x in enumerate(NARR):
        v, sr = sf.read(os.path.join(HERE, "narr", os.path.basename(x["wav"]))); v = resample_poly(v, SR, sr) if sr != SR else v
        v = v / (np.sqrt(np.mean(v ** 2)) + 1e-9) * 0.12
        i0 = int((S[i] + LEAD) * SR); v = v[:len(ts) - i0]; voice[i0:i0 + len(v)] += v
    voice = voice + fftconvolve(voice, ir)[:len(ts)] * 0.004
    venv = lp(np.abs(voice) > 0.01, 0.0005)
    duck = 1 - 0.55 * np.clip(venv * 3, 0, 1)
    out = voice + mu * 0.22 * duck
    out *= np.clip((TOTAL - ts) / 0.35, 0, 1)
    out = out / np.abs(out).max() * 0.9
    with wave.open(os.path.join(HERE, "audio.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    print(f"duração {TOTAL:.1f}s, {NF} quadros")
    if ONLY:
        fis = [int(x * FPS) for x in ONLY]
        with Pool(4) as pl: pl.map(render, fis)
        ims = [Image.open(f"{FR}/f{i:05d}.png").resize((270, 480)) for i in fis]
        g = Image.new("L", (270 * min(6, len(ims)), 480 * ((len(ims) + 5) // 6)))
        for j, im in enumerate(ims): g.paste(im, ((j % 6) * 270, (j // 6) * 480))
        g.save(os.path.join(HERE, "preview.png")); sys.exit()
    with Pool(4) as pl: pl.map(render, range(NF), chunksize=8)
    audio()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/f%05d.png",
                    "-i", os.path.join(HERE, "audio.wav"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", OUTFILE], check=True)
    print("ok", OUTFILE)
