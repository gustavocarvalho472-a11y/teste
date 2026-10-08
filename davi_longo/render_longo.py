"""Vídeo longo do Davi (16:9).

Linguagem visual:
  - abertura: poeira de partículas em 3D converge e forma a primeira imagem;
  - "morph": a imagem vira partículas (linha de luz), os pontos ganham 3D e voam para formar a próxima imagem;
  - "cloud": a cena fica em partículas girando em 3D (mistério, sem revelar a imagem);
  - "dissolve": troca suave entre imagens nítidas e vivas;
  - virada de capítulo: imagem -> partículas -> título do capítulo -> próxima imagem.
Áudio: piano + cordas sintetizados com dinâmica por trecho, batida de coração, riser, braam, impacto,
whoosh e brilho das partículas sincronizados com os eventos visuais.

  python3 render_longo.py prev 3 10 31        -> grade de prévia (tempos em segundos)
  python3 render_longo.py teste 45            -> renderiza só os primeiros 45s
  python3 render_longo.py                     -> vídeo inteiro
"""
import os, sys, json, wave, subprocess, functools
os.environ["MOTOR_FMT"] = "16x9"
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "motor"))
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
from scipy.signal import lfilter, resample_poly, fftconvolve
from scipy.ndimage import gaussian_filter
import particulas as pt

W, H, FPS = pt.W, pt.H, 30
IMG = os.path.join(ROOT, "motor/img/davi")
FR = os.path.join(HERE, "frames"); os.makedirs(FR, exist_ok=True)
NARRDIR = os.path.join(HERE, "narr")
NARR = json.load(open(os.path.join(NARRDIR, "timing.json")))
FONT = "/usr/share/fonts/opentype/inter/"
f_cap = ImageFont.truetype(FONT + "Inter-SemiBold.otf", 50)
f_ui = ImageFont.truetype(FONT + "Inter-Medium.otf", 22)

GAP, LEAD, TRANS = 0.35, 0.1, 5.0        # respiro entre falas, atraso da voz, virada de capítulo
OPEN = 3.4                               # abertura em partículas
MW = 2.4                                 # duração de um morph imagem -> imagem
PAUSE = {4: 0.9}                         # silêncio extra antes da fala (tensão antes da revelação)

# ---------- linha do tempo a partir da narração ----------
S, SEC, sec_first = [], [], {}
t = 2.0
for i, x in enumerate(NARR):
    if i and x["sec"] != NARR[i - 1]["sec"]:
        t += 0.4 + TRANS
    t += PAUSE.get(i, 0)
    if x["sec"] not in sec_first: sec_first[x["sec"]] = i
    S.append(t); SEC.append(x["sec"]); t += x["dur"] + GAP
TOTAL = t + 2.5
def at(i, f):
    if isinstance(f, str): f = max(0, NARR[i]["text"].find(f)) / len(NARR[i]["text"])
    return S[i] + f * NARR[i]["dur"]
SECS = list(sec_first)
TR = [S[sec_first[s]] - TRANS for s in SECS[1:]]

TITLE = {"1.": ("CAPÍTULO 1", "O FILHO QUE NINGUÉM CHAMOU"), "2.": ("CAPÍTULO 2", "UNGIDO… E DE VOLTA AO PASTO"),
         "3.": ("CAPÍTULO 3", "O MÚSICO DO REI"), "4.": ("CAPÍTULO 4", "QUARENTA DIAS DE MEDO"),
         "5.": ("CAPÍTULO 5", "O ENTREGADOR"), "6.": ("CAPÍTULO 6", "A ARMADURA QUE NÃO SERVIU"),
         "7.": ("CAPÍTULO 7", "UMA PEDRA"), "FE": ("", "")}
REF = {"GA": "1 SM 16:11", "1.": "1 SM 16:1–11", "2.": "1 SM 16:12–13", "3.": "1 SM 16:14–23", "4.": "1 SM 17:1–16",
       "5.": "1 SM 17:15–30", "6.": "1 SM 17:31–40", "7.": "1 SM 17:41–58", "FE": "1 SM 16:7"}

# ---------- planos ----------
# (fala, fração ou palavra-âncora, imagem, (cx, cy, zoom) inicial, final, tipo, efeito sonoro extra)
SHOTS = [
    (0, 0, "19_davi_sozinho", (.60, .40, 1.75), (.60, .42, 1.55), "open", ""),
    (1, 0, "07_samuel_filhos", (.30, .50, 1.25), (.25, .48, 1.45), "dissolve", ""),
    (2, 0, "07_samuel_filhos", (.68, .52, 1.55), (.62, .52, 1.35), "dissolve", ""),
    (2, "Menos", "19_davi_sozinho", (.58, .40, 1.8), (.56, .44, 1.5), "morph", "hit"),
    (3, "cuidando", "19_davi_sozinho", (.30, .62, 1.7), (.40, .55, 1.25), "dissolve", ""),
    (4, 0, "01_davi", (.50, .36, 1.55), (.50, .36, 1.8), "morph", "braam"),
    (5, 0, "03_confronto", (.50, .50, 1.0), (.45, .45, 1.2), "dissolve", ""),
    (5, "derrubou", "18_golias_caido", (.55, .55, 1.15), (.62, .50, 1.35), "morph", "boom"),
    (5, "um detalhe", "26_saul_pergunta", (.5, .5, 1.0), (.5, .5, 1.0), "cloud", "mystery"),
    (6, 0, "07_samuel_filhos", (.17, .45, 1.9), (.19, .46, 1.65), "dissolve", ""),
    (7, 0, "07_samuel_filhos", (.50, .50, 1.05), (.52, .50, 1.2), "dissolve", ""),
    (8, "Eliabe", "08_eliabe", (.56, .38, 1.5), (.55, .45, 1.15), "morph", ""),
]
KIND = [s[5] for s in SHOTS]

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

def shot_times():
    st = []
    for j, (li, fr, *_r) in enumerate(SHOTS):
        if j == 0: st.append(0.0); continue
        first = sec_first[SEC[li]] == li and fr == 0
        st.append(S[li] if first else (at(li, fr) - (0.2 if fr == 0 else 0)))
    en = []
    for j in range(len(SHOTS)):
        nxt = st[j + 1] if j + 1 < len(SHOTS) else TOTAL
        sec_next = SEC[SHOTS[j + 1][0]] if j + 1 < len(SHOTS) else None
        if sec_next and sec_next != SEC[SHOTS[j][0]]: nxt = S[sec_first[sec_next]] - TRANS
        en.append(nxt)
    return st, en
ST, EN = shot_times()
# janelas de morph: centradas no início do plano
MORPH = {j: (ST[j] - MW / 2, ST[j] + MW / 2) for j in range(len(SHOTS)) if KIND[j] in ("morph", "cloud")}

@functools.lru_cache(maxsize=8)
def load(name):
    return Image.open(os.path.join(IMG, name + ".jpg")).convert("L")

def params(j, t):
    _, _, name, p0, p1, kind, _ = SHOTS[j]
    if kind == "cloud": return name, list(p0)
    t0 = 0 if kind == "open" else ST[j]
    u = np.clip((t - t0) / max(1e-3, EN[j] - t0), -.1, 1.15); k = u * u * (3 - 2 * u) * .5 + u * .5
    return name, [a + (b - a) * k for a, b in zip(p0, p1)]

def view(name, p):
    im = load(name); cx, cy, z = p
    cw = im.width / z; ch = cw * H / W
    if ch > im.height / z: ch = im.height / z; cw = ch * W / H
    x0 = np.clip(cx * im.width - cw / 2, 0, im.width - cw); y0 = np.clip(cy * im.height - ch / 2, 0, im.height - ch)
    return np.asarray(im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC), np.float32)

GY, GX = np.mgrid[0:H, 0:W].astype(np.float32)
DIAG = GX / W * .45 + GY / H * .55
def alive(a, t, seed=0):
    """Imagem 'viva': luz atravessando devagar e respiração de brilho."""
    sweep = 1 + .22 * np.exp(-((GX / W * .8 + GY / H * .2 - ((t * .07 + seed * .37) % 1.6 - .3)) / .18) ** 2)
    return np.clip(a * sweep * (1 + .035 * np.sin(t * 1.7 + seed)), 0, 255)

def shot_index(t):
    j = 0
    for k in range(len(SHOTS)):
        if ST[k] <= t: j = k
    return j

# ---------- poeira flutuando ----------
rng = np.random.default_rng(7)
DN = 220
DUST = np.c_[rng.random(DN) * W, rng.random(DN) * H, rng.random(DN)]
def dust(t):
    buf = np.zeros((H, W), np.float32)
    x = (DUST[:, 0] + t * (8 + 20 * DUST[:, 2]) + 30 * np.sin(t * .3 + DUST[:, 1])) % W
    y = (DUST[:, 1] - t * (5 + 12 * DUST[:, 2])) % H
    pt.splat(x.astype(np.float32), y.astype(np.float32),
             (40 + 80 * DUST[:, 2] * (.6 + .4 * np.sin(t * 2 + DUST[:, 0]))).astype(np.float32), buf)
    return gaussian_filter(buf, 2.2) * 12

# ---------- nuvens ----------
N = 120000
@functools.lru_cache(maxsize=6)
def img_cloud(name, p):
    """Nuvem de uma vista (sempre a mesma semente por imagem: os pontos casam entre efeitos seguidos)."""
    arr = view(name, list(p))
    P, I, UV = pt.cloud_from_array(arr / 255, W, spacing=4.0, gamma=1.15, thresh=.08, autolevel=True,
                                   depth=150, lumdepth=170, feather=.03, enhance=.7, seed=sum(map(ord, name)) % 997)
    return pt.resample(P, I, UV, N, seed=sum(map(ord, name)) % 991)[:2]

def key(j, t):
    name, p = params(j, t); return name, tuple(round(float(v), 4) for v in p)

def title_mask(a, b):
    img = Image.new("L", (W, H), 0); d = ImageDraw.Draw(img)
    d.text((W / 2, H / 2 - 70), a, font=ImageFont.truetype(FONT + "Inter-Medium.otf", 34), fill=200, anchor="mm")
    fs = 92 if len(b) < 22 else 76
    d.text((W / 2, H / 2 + 10), b, font=ImageFont.truetype(FONT + "Inter-Bold.otf", fs), fill=255, anchor="mm")
    d.line([(W / 2 - 60, H / 2 + 90), (W / 2 + 60, H / 2 + 90)], fill=180, width=3)
    return np.asarray(img, np.float32) / 255

@functools.lru_cache(maxsize=2)
def title_cloud(k):
    a, b = TITLE[SECS[k + 1][:2]]
    P, I, _ = pt.cloud_from_array(title_mask(a, b), W, spacing=2.6, gamma=1, thresh=.3, enhance=0, depth=0, feather=0, seed=5)
    P, I, _ = pt.resample(P, I, np.zeros((len(I), 2), np.float32), N, seed=6)
    return P, I * .3

R = np.random.default_rng(3)
PH = R.random(N).astype(np.float32); RN = R.normal(0, 1, (N, 3)).astype(np.float32)
SCAT = (R.normal(0, 1, (N, 3)) * [900, 520, 700]).astype(np.float32)          # poeira inicial da abertura

def draw_particles(Q, I, t, yaw=0., pitch=0., dolly=0.):
    I = I * (1 + .12 * np.sin(t * 9 + PH * 30))                                  # pontos que respiram
    x, y, z, s = pt.project(Q, yaw=yaw, pitch=pitch, dolly=dolly)
    return pt.render(x, y, z, s, I, focus_z=0, dof=.006, gain=1.5, glow=.5)

def sweep_edge(f, img):
    return 190 * np.exp(-((DIAG - f) / .005) ** 2) * (img > 10)

def mix_sweep(sharp, part, front, inverse=False):
    """front avança na diagonal; atrás dele já é partícula (ou imagem, se inverse)."""
    M = np.clip((front - DIAG) / .05, 0, 1)
    out = part * (1 - M) + sharp * M if inverse else sharp * (1 - M) + part * M
    return out + sweep_edge(front, sharp)

def opening(t):
    j = 0; name, p = key(j, OPEN)
    PB, IB = img_cloud(name, p)
    m = ease((t - .2 - PH * 1.1) / 1.5)[:, None]
    zf = 1 - ease((t - 2.3) / .5)
    QB = PB.copy(); QB[:, 2] *= zf
    Q = SCAT * (1 - m) + QB * m
    I = (.25 * (1 - m[:, 0]) + IB * m[:, 0]) * np.clip(t / .6, 0, 1)
    orbit = 1 - ease(t / 2.8)
    part = draw_particles(Q, I, t, yaw=np.radians(28) * orbit, pitch=np.radians(-8) * orbit, dolly=-250 * orbit)
    if t < OPEN - .65: return part
    B = alive(view(*params(0, t)), t, 0)
    return mix_sweep(B, part, -0.1 + 1.25 * ease((t - (OPEN - .65)) / .65), inverse=True)

def morph(j, t):
    w0, w1 = MORPH[j]; u = t - w0; cloud_b = KIND[j] == "cloud"
    PA, IA = img_cloud(*key(j - 1, w0)); PB, IB = img_cloud(*key(j, w1))
    zA = ease((u - .2) / .5); zB = 1 - ease((u - 1.6) / .4) if not cloud_b else ease((u - 1.2) / .8)
    m = ease((u - .55 - PH * .4) / .85)[:, None]
    QA = PA.copy(); QA[:, 2] *= zA; QB = PB.copy(); QB[:, 2] *= zB if not cloud_b else 0
    fly = np.sin(np.pi * m)
    Q = QA * (1 - m) + QB * m + fly * RN * [90, 70, 90]
    I = (IA * (1 - m[:, 0]) + IB * m[:, 0]) * (1 - .35 * fly[:, 0])
    orbit = ease((u - .3) / .6) * (1 - ease((u - 1.5) / .5)) if not cloud_b else ease((u - .3) / .6) * 0
    part = draw_particles(Q, I, t, yaw=np.radians(10) * orbit, pitch=np.radians(-3) * orbit, dolly=80 * orbit)
    A = alive(view(*params(j - 1, w0)), t, j - 1)
    if u < .6: part = mix_sweep(A, part, -0.1 + 1.25 * ease(u / .45))
    if not cloud_b and u > 1.85:
        part = mix_sweep(alive(view(*params(j, t)), t, j), part, -0.1 + 1.25 * ease((u - 1.85) / .55), inverse=True)
    return part

def cloud_shot(j, t):
    """Cena só em partículas, girando devagar (mistério)."""
    t0 = ST[j] + MW / 2; t1 = EN[j]; u = np.clip((t - t0) / max(.1, t1 - t0), 0, 1)
    PB, IB = img_cloud(*key(j, t0))
    zf = ease(u / .3) * (1 - ease((u - .85) / .15))
    Q = PB.copy(); Q[:, 2] *= zf * 1.4
    env = np.sin(np.pi * u)
    return draw_particles(Q, IB * (.85 + .25 * env), t, yaw=np.radians(22) * np.sin(np.pi * u) * zf,
                          pitch=np.radians(-6) * zf, dolly=140 * env)

def transition(k, u, t):
    """Virada de capítulo k (u: 0..TRANS). Se o plano anterior é 'cloud', já começa em partículas."""
    t0 = TR[k]; j_prev = shot_index(t0 - 1e-3); j_next = shot_index(t0 + TRANS + 1e-3)
    from_cloud = KIND[j_prev] == "cloud"
    PA, IA = img_cloud(*key(j_prev, t0)); PB, IB = img_cloud(*key(j_next, t0 + TRANS)); PT, IT = title_cloud(k)
    zA = 0 if from_cloud else ease((u - .7) / 1.0)
    zB = 1 - ease((u - 3.5) / .8)
    m1 = ease((u - (1.0 if from_cloud else 1.5) - PH * .5) / 1.1)[:, None]
    m2 = ease((u - 3.3 - PH * .4) / 1.0)[:, None]
    QA = PA.copy(); QA[:, 2] *= zA
    QB = PB.copy(); QB[:, 2] *= min(zB, ease((u - 3.0) / .6))
    Q = QA * (1 - m1) + PT * m1; Q = Q * (1 - m2) + QB * m2
    fly = (np.sin(np.pi * m1[:, 0]) + np.sin(np.pi * m2[:, 0]))[:, None]
    Q = Q + fly * RN * [110, 80, 110]
    I = IA * (1 - m1[:, 0]) + IT * m1[:, 0]; I = (I * (1 - m2[:, 0]) + IB * m2[:, 0]) * (1 - .45 * np.clip(fly[:, 0], 0, 1))
    orbit = ease((u - (.2 if from_cloud else .8)) / 1.2) * (1 - ease((u - 3.4) / 1.0))
    part = draw_particles(Q, I, t, yaw=np.radians(16) * orbit * np.sin(u * .6 + .3), pitch=np.radians(-5) * orbit,
                          dolly=120 * orbit)
    if not from_cloud and u < 1.2:
        part = mix_sweep(alive(view(*params(j_prev, t0)), t, 1), part, -0.1 + 1.25 * ease(u / 1.0))
    if u > 4.15:
        part = mix_sweep(alive(view(*params(j_next, t)), t, 2), part, -0.1 + 1.25 * ease((u - 4.15) / .8), inverse=True)
    return part

# ---------- legendas (blocos de 2 a 4 palavras) ----------
def split_even(ws):
    if not ws: return []
    g = -(-len(ws) // 4); b = np.linspace(0, len(ws), g + 1).round().astype(int)
    return [" ".join(ws[b[k]:b[k + 1]]) for k in range(g)]
def chunks(text):
    out, cl = [], []
    for x in text.replace('"', "").split():
        cl.append(x)
        if x[-1] in ".,:;?!…": out += split_even(cl); cl = []
    return out + split_even(cl)
CAPS = []
for i, x in enumerate(NARR):
    cs = chunks(x["text"]); tot = sum(len(c) for c in cs); c0 = 0
    for c in cs:
        CAPS.append([S[i] + LEAD + x["dur"] * c0 / tot - .05, S[i] + LEAD + x["dur"] * (c0 + len(c)) / tot, c]); c0 += len(c)
for j in range(len(CAPS) - 1):
    if CAPS[j + 1][0] - CAPS[j][1] < .4: CAPS[j][1] = CAPS[j + 1][0]

def overlays(img, t):
    d = ImageDraw.Draw(img)
    hdr = np.clip((t - 2.6) / .8, 0, 1)                                        # cabeçalho entra depois da abertura
    sec = SEC[max(0, np.searchsorted(S, t, "right") - 1)]
    d.text((60, 46), "CURIOSIDADES BÍBLICAS — DAVI", font=f_ui, fill=int(175 * hdr))
    d.text((W - 60, 46), REF.get(sec[:2], ""), font=f_ui, fill=int(175 * hdr), anchor="ra")
    d.line([(60, 84), (60 + (W - 120) * hdr, 84)], fill=70, width=1)
    d.line([(60, H - 34), (W - 60, H - 34)], fill=int(45 * hdr), width=2)
    d.line([(60, H - 34), (60 + (W - 120) * t / TOTAL, H - 34)], fill=int(200 * hdr), width=2)
    for a, b, c in CAPS:
        if a <= t < b:
            al = min(1, (t - a) / .12, (b - t) / .12)
            sh = Image.new("L", img.size, 0); ImageDraw.Draw(sh).text((W / 2, H - 140), c, font=f_cap, fill=255, anchor="mm")
            sh = np.asarray(sh.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
            base = np.asarray(img, np.float32) * (1 - .8 * al * np.clip(sh * 1.6, 0, 1))
            img.paste(Image.fromarray(base.astype(np.uint8)))
            ImageDraw.Draw(img).text((W / 2, H - 140), c, font=f_cap, fill=int(255 * al), anchor="mm")

def render(fi):
    t = fi / FPS
    k = next((k for k, t0 in enumerate(TR) if t0 <= t < t0 + TRANS), None)
    jm = next((j for j, (a, b) in MORPH.items() if a <= t < b), None)
    j = shot_index(t)
    if k is not None: a = transition(k, t - TR[k], t)
    elif t < OPEN: a = opening(t)
    elif jm is not None: a = morph(jm, t)
    elif KIND[j] == "cloud": a = cloud_shot(j, t)
    else:
        a = alive(view(*params(j, t)), t, j)
        if (j and KIND[j] == "dissolve" and t - ST[j] < .6 and SEC[SHOTS[j][0]] == SEC[SHOTS[j - 1][0]]
                and SHOTS[j][2] != SHOTS[j - 1][2]):                              # mesma imagem: corte seco
            q = ease((t - ST[j]) / .6); a = a * q + alive(view(*params(j - 1, t)), t, j - 1) * (1 - q)
        a = a + dust(t)
    master = min(1, (TOTAL - t) / 1.2)
    img = Image.fromarray(pt.finish(a * master, t, grain=5, vignette=.5)); overlays(img, t)
    img.save(f"{FR}/f{fi:05d}.png")

# ---------- áudio ----------
SR = 44100
def audio(T):
    n_ = int(SR * T); ts = np.arange(n_) / SR; R2 = np.random.default_rng(1); nz = R2.normal(0, 1, n_)
    lp = lambda x, a: lfilter([a], [1, a - 1], x)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    def seg(t0, dur):
        i0 = max(0, int(t0 * SR)); i1 = min(n_, int((t0 + dur) * SR)); return i0, i1, ts[i0:i1] - t0
    def env_pts(pts):                                                     # automação de volume por pontos (t, g)
        x, y = zip(*pts); return np.interp(ts, x, y)
    # ----- marcos -----
    REV = ST[5]; GIANT = ST[7]; MYST = ST[8]; T1 = TR[0] if TR else T
    # ----- piano -----
    piano = np.zeros(n_)
    def pnote(f, t0, g):
        i0, i1, tt = seg(t0, 4.5)
        if i1 <= i0: return
        v = sum((1 / k ** 1.4) * np.sin(2 * np.pi * f * k * (1 + .0004 * k * k) * tt) * np.exp(-tt * (.9 + .7 * k)) for k in range(1, 7))
        piano[i0:i1] += g * v * np.clip(tt / .004, 0, 1)
    prog = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [41, 48, 53, 57, 60], [48, 55, 60, 64, 67]]   # Dm Bb F C
    BAR = 60 / 66 * 4
    melody = {0: [74, 72, 69], 1: [70, 69, 65], 2: [69, 67, 65], 3: [67, 64, 67]}
    for b, t0 in enumerate(np.arange(0, T, BAR)):
        ch = prog[b % 4]
        for s16, idx in enumerate([0, 2, 3, 4, 3, 2, 1, 2]):              # arpejo em colcheias
            pnote(hz(ch[idx] + 12), t0 + s16 * BAR / 8, .05 * (1.15 if s16 == 0 else .8))
        pnote(hz(ch[0] - 12), t0, .09)
        if t0 > REV - 1:                                                  # melodia entra na revelação
            for q, m in enumerate(melody[b % 4]): pnote(hz(m + 12), t0 + q * BAR / 3, .07)
    # ----- cordas -----
    strings = np.zeros(n_)
    for b, t0 in enumerate(np.arange(0, T, BAR)):
        i0, i1, tt = seg(t0, BAR + 1.5)
        if i1 <= i0: continue
        e = np.clip(tt / 1.2, 0, 1) * np.clip((BAR + 1.5 - tt) / 1.5, 0, 1)
        for m in prog[b % 4][:4]:
            f = hz(m); v = 0
            for dt in (-.004, 0, .005):
                v = v + sum((1 / k) * np.sin(2 * np.pi * f * (1 + dt) * k * tt + k * .7 + 2.2 * np.sin(2 * np.pi * 5.2 * tt) * .002 * k)
                            for k in range(1, 8))
            strings[i0:i1] += .012 * e * v
    low = np.zeros(n_)                                                    # drone grave
    low += .05 * np.sin(2 * np.pi * hz(38) * ts) + .03 * np.sin(2 * np.pi * hz(45) * ts)
    # dinâmica: abre íntimo, cai para quase nada antes da revelação, cresce até o título
    pg = env_pts([(0, 0), (2, .55), (ST[3] - .3, .7), (ST[3], .25), (S[4] - .9, .2), (S[4] - .4, 0), (REV + .2, .9),
                  (T1, 1.0), (T1 + 2.4, .2), (T1 + 5, .7), (T + 99, .7)])
    sg = env_pts([(0, 0), (REV - .2, 0), (REV + .4, .8), (GIANT, 1.0), (MYST, .7), (T1 + 2.0, 1.25), (T1 + 2.5, .35),
                  (T1 + 6, .45), (T + 99, .45)])
    lg = env_pts([(0, .6), (3, 1), (S[4] - .4, 1), (S[4] - .3, 0), (REV + .3, 1), (T + 99, .6)])
    music = piano * pg + strings * sg + low * lg
    # ----- sound design -----
    fx = np.zeros(n_)
    def add(t0, v):
        i0 = int(t0 * SR); i1 = min(n_, i0 + len(v))
        if i1 > i0 >= 0: fx[i0:i1] += v[:i1 - i0]
    def whoosh(dur, g, up=True):
        k = int(dur * SR); tt = np.arange(k) / SR; x = R2.normal(0, 1, k)
        a = np.linspace(.02, .35, k) if up else np.linspace(.35, .02, k)
        y = np.zeros(k); yp = 0.0
        for i in range(0, k, 256):                                        # filtro com corte variando
            b = a[i]; y[i:i + 256] = lfilter([b], [1, b - 1], x[i:i + 256], zi=[(1 - b) * yp])[0]; yp = y[min(i + 255, k - 1)]
        return g * y * np.sin(np.pi * tt / dur) ** 2
    def sparkle(dur, g, dens=40):
        k = int(dur * SR); y = np.zeros(k)
        for _ in range(int(dens * dur)):
            i = R2.integers(0, k); f = R2.uniform(2500, 7000); L = int(.12 * SR); tt = np.arange(min(L, k - i)) / SR
            y[i:i + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 40) * R2.uniform(.3, 1)
        return g * y * np.sin(np.pi * np.arange(k) / k)
    def boom(g):
        tt = np.arange(int(2.5 * SR)) / SR
        return g * (np.sin(2 * np.pi * (70 * np.exp(-tt * 4) + 30) * tt) * np.exp(-tt * 1.8)
                    + .5 * lp(R2.normal(0, 1, len(tt)), .08) * np.exp(-tt * 9))
    def braam(g, root=38):
        tt = np.arange(int(3.2 * SR)) / SR; v = 0
        op = np.clip(tt / .15, 0, 1) * np.exp(-tt * .9)
        for m in (root, root + 7, root + 12):
            for k in range(1, 22):
                v = v + np.sin(2 * np.pi * hz(m) * k * tt + k) / k * np.exp(-(k / (3 + 16 * op)) ** 2)
        return g * v * np.clip(tt / .03, 0, 1) * np.exp(-tt * .8)
    def riser(dur, g):
        k = int(dur * SR); tt = np.arange(k) / SR; f = 150 * (14 ** (tt / dur))
        tone_ = np.sin(2 * np.pi * np.cumsum(f) / SR)
        hiss = R2.normal(0, 1, k); hiss = hiss - lp(hiss, .2)
        return g * (tt / dur) ** 2.2 * (.5 * tone_ + .5 * hiss)
    def hit(g):
        tt = np.arange(int(1.2 * SR)) / SR
        return g * (np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 5) + .4 * lp(R2.normal(0, 1, len(tt)), .3) * np.exp(-tt * 25))
    def heart(t0, t1, g):
        for b in np.arange(t0, t1, .95):
            for off, gg in ((0, 1), (.27, .65)):
                tt = np.arange(int(.35 * SR)) / SR
                add(b + off, g * gg * np.sin(2 * np.pi * (48 + 20 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14))
    # abertura: brilho das partículas + riser até a imagem nítida
    add(0, sparkle(OPEN, .25, 60)); add(.2, whoosh(2.4, 1.0)); add(OPEN - 2.0, riser(2.0, .35)); add(OPEN - .05, hit(.6))
    heart(ST[2], S[4] - .2, .9)
    for j, (w0, w1) in MORPH.items():
        if w0 > T: continue
        add(w0, whoosh(1.4, 1.1)); add(w0 + .5, sparkle(1.5, .22)); add(w0 + 1.3, whoosh(1.0, .6, up=False))
        sfx = SHOTS[j][6]
        if sfx == "hit": add(ST[j] + .3, hit(.8))
        if sfx == "braam": add(S[4] - .9, riser(.9, .25)); add(ST[j] + .35, braam(.30)); add(ST[j] + .35, boom(.6))
        if sfx == "boom": add(ST[j] + .4, boom(1.0))
        if sfx == "mystery": add(ST[j] + .3, sparkle(3.0, .3, 25))
    for t0 in TR:
        if t0 > T: break
        add(t0, whoosh(1.6, 1.0)); add(t0 + .4, sparkle(2.5, .25)); add(t0 + .5, riser(1.9, .35))
        add(t0 + 2.4, braam(.28, 36)); add(t0 + 2.4, boom(.9)); add(t0 + 3.3, whoosh(1.3, .7, up=False))
    # ----- voz -----
    voice = np.zeros(n_)
    for i, x in enumerate(NARR):
        i0 = int((S[i] + LEAD) * SR)
        if i0 >= n_: break
        v, sr = sf.read(os.path.join(NARRDIR, x["wav"])); v = resample_poly(v, SR, sr) if sr != SR else v
        v = v / (np.sqrt(np.mean(v ** 2)) + 1e-9) * .12; v = v[:n_ - i0]; voice[i0:i0 + len(v)] += v
    ir = R2.normal(0, 1, int(SR * 2.8)) * np.exp(-np.arange(int(SR * 2.8)) / SR * 2.2)
    music = music / (np.abs(music).max() + 1e-9)
    music = .75 * music + .5 * fftconvolve(music, ir)[:n_] / np.sqrt(len(ir)) * 3
    fx = fx / (np.abs(fx).max() + 1e-9); fx = .85 * fx + .25 * fftconvolve(fx, ir)[:n_] / np.sqrt(len(ir)) * 3
    voice = voice + fftconvolve(voice, ir[:int(SR * 1.0)])[:n_] * .003
    duck = 1 - .45 * np.clip(lp((np.abs(voice) > .01).astype(float), .0005) * 3, 0, 1)
    out = voice + .26 * music / np.abs(music).max() * duck + .30 * fx / np.abs(fx).max() * (1 - .3 * (1 - duck))
    out *= np.clip((T - ts) / 1.0, 0, 1); out = np.tanh(out / np.abs(out).max() * 1.3) / np.tanh(1.3) * .92
    with wave.open(os.path.join(HERE, "audio.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    print(f"duração {TOTAL:.1f}s; viradas em {[round(x, 1) for x in TR]}; planos {[round(x, 1) for x in ST]}")
    if len(sys.argv) > 1 and sys.argv[1] == "audio":
        audio(float(sys.argv[2])); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "prev":
        fis = [int(float(x) * FPS) for x in sys.argv[2:]]
        with Pool(4) as pl: pl.map(render, fis)
        ims = [Image.open(f"{FR}/f{i:05d}.png").resize((640, 360)) for i in fis]
        cols = min(3, len(ims)); g = Image.new("L", (640 * cols, 360 * ((len(ims) + cols - 1) // cols)))
        for j, im in enumerate(ims): g.paste(im, ((j % cols) * 640, (j // cols) * 360))
        g.save(os.path.join(HERE, "preview.png")); sys.exit()
    T = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "teste" else TOTAL
    out = os.path.join(ROOT, "davi_longo_teste.mp4" if T < TOTAL else "davi_longo.mp4")
    nf = int(T * FPS)
    with Pool(4) as pl: pl.map(render, range(nf), chunksize=4)
    audio(T)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/f%05d.png",
                    "-i", os.path.join(HERE, "audio.wav"), "-frames:v", str(nf), "-c:v", "libx264", "-b:v", os.environ.get("VBR", "4.5M"),
                    "-maxrate", "5.5M", "-bufsize", "9M", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], check=True)
    print("ok", out)
