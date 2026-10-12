"""Davi v2 — imagens geradas pelo usuário em partículas 3D vivas + gráficos de partículas, narração Alex, 9:16.
Uso: python3 render_v2.py [saida.mp4]            render completo
     python3 render_v2.py prev t1 t2 ...         grade de prévia (preview.png)"""
import json, os, sys, wave, subprocess
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import fftconvolve, resample_poly, lfilter
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "motor"))
import particulas as pt
import formas

W, H, FPS, CX = pt.W, pt.H, 30, pt.W / 2
N = 42000
IMGDIR = os.path.join(ROOT, "motor", "img", "davi")
NARRDIR = os.path.join(ROOT, "davi", "narr")
FR = os.path.join(HERE, "frames"); os.makedirs(FR, exist_ok=True)
F = "/usr/share/fonts/opentype/inter/"
def font(n, s): return ImageFont.truetype(F + n, s)
f_cap, f_ui, f_lbl, f_call = (font("Inter-SemiBold.otf", 50), font("Inter-Medium.otf", 26), font("Inter-Bold.otf", 34),
                              font("Inter-SemiBold.otf", 27))
rng = np.random.default_rng(11)

# ---------- linha do tempo (da narração) ----------
NARR = json.load(open(os.path.join(NARRDIR, "timing.json")))
LEAD, TAIL = 0.25, 0.35
S, D, acc = [], [], 0.0
for i, x in enumerate(NARR):
    d = LEAD + x["dur"] + TAIL + (1.6 if i == len(NARR) - 1 else 0)
    S.append(acc); D.append(d); acc += d
TOTAL = acc; NF = int(TOTAL * FPS)
def at(i, frac): return S[i] + LEAD + NARR[i]["dur"] * frac

# ---------- nuvens ----------
IMH = 1080  # altura da imagem no mundo (px)
def img_cloud(name, u0, u1, seed):
    a = np.asarray(Image.open(os.path.join(IMGDIR, name + ".jpg")).convert("L"), np.float32) / 255
    a = a[:, int(u0 * a.shape[1]):int(u1 * a.shape[1])]
    width = IMH * a.shape[1] / a.shape[0]
    P, I, UV = pt.cloud_from_array(a, width, spacing=5.0, gamma=1.1, thresh=0.10, autolevel=True,
                                   depth=160, lumdepth=150, feather=0.1, seed=seed)
    return pt.resample(P, I, UV, N, seed)

def shape_cloud(fn, seed):
    P, I, UV = pt.cloud_from_array(formas.mask(fn), W, spacing=7.0, gamma=1.0, thresh=0.3, feather=0, enhance=0,
                                   depth=0, seed=seed)
    I = np.full_like(I, 0.85) * (0.8 + 0.3 * np.random.default_rng(seed).random(len(I))).astype(np.float32)
    return pt.resample(P, I, UV, N, seed)

def dust_cloud(seed):
    r = np.random.default_rng(seed)
    P = np.stack([r.uniform(-560, 560, N), r.uniform(-700, 700, N), r.normal(0, 120, N)], 1).astype(np.float32)
    return P, np.full(N, 0.35, np.float32), r.random((N, 2)).astype(np.float32)

C = {
    "confronto": img_cloud("03_confronto", 0.20, 0.80, 1),
    "pedra": img_cloud("04_pedra", 0.25, 0.85, 2),
    "golias": img_cloud("02_golias", 0.22, 0.78, 3),
    "pasto": img_cloud("05_pasto", 0.20, 0.80, 4),
    "leao": img_cloud("06_leao", 0.15, 0.80, 5),
    "davi": img_cloud("01_davi", 0.28, 0.72, 6),
    "harpa": shape_cloud(formas.harp_draw, 7), "coroa": shape_cloud(formas.crown_draw, 8),
    "30": shape_cloud(formas.text_draw("30", 600), 9), "telas": shape_cloud(formas.phones_draw, 10),
    "coracao": shape_cloud(formas.heart_draw, 11), "barras": shape_cloud(formas.bars_draw, 12),
    "2": shape_cloud(formas.text_draw("2", 820), 13), "poeira": dust_cloud(14),
}
GPY = 100  # gráficos foram desenhados com centro em y=860

def cam(yaw=0, dolly=0, px=0, py=0, focus=-60, pitch=0): return dict(yaw=yaw, dolly=dolly, px=px, py=py, focus=focus, pitch=pitch)
G0 = cam(py=GPY, focus=0)
# (início, nuvem, câmera inicial, câmera final, efeitos)
KEYS = [
    (-1.0, "poeira", G0, G0, ()),
    (0.0, "confronto", cam(-6, -60, 150, 40), cam(5, 90, -110, 10), ("ceu", "vivo")),
    (at(0, .72), "pedra", cam(4, 0, 0, 0), cam(-4, 160, -20, -20), ("brasas", "vivo")),
    (S[1], "golias", cam(-5, -40, 40, 80), cam(5, 110, -20, -30), ("relampago", "vivo")),
    (S[2], "pasto", cam(6, -80, 90, 30), cam(-6, 100, -70, 0), ("estrelas", "ceu", "vivo")),
    (S[3], "leao", cam(-4, 0, 110, 20), cam(4, 150, -40, 0), ("tremor", "chama", "vivo")),
    (at(3, .5), "harpa", G0, cam(py=GPY, dolly=90, yaw=4), ()),
    (S[4], "coroa", G0, cam(py=GPY, dolly=80, yaw=-4), ("brilho",)),
    (at(4, .42), "poeira", G0, G0, ()),
    (at(4, .72), "pasto", cam(-6, -150, 0, 40), cam(4, 0, 0, 0), ("estrelas", "ceu", "vivo")),
    (S[5], "30", G0, cam(py=GPY, dolly=90), ()),
    (S[6], "telas", G0, cam(py=GPY, dolly=60, yaw=5), ()),
    (S[7], "davi", cam(0, -40, 0, 100), cam(-4, 130, 0, 0), ("raios", "vivo")),
    (S[8], "coracao", G0, cam(py=GPY, dolly=100), ("pulso",)),
    (S[9], "barras", G0, cam(py=GPY, dolly=60, yaw=-5), ()),
    (S[10], "golias", cam(5, 0, -40, 40), cam(-3, 120, 30, 0), ("relampago", "vivo")),
    (at(10, .45), "leao", cam(4, 60, -60, 0), cam(-3, 170, 40, 0), ("chama", "vivo")),
    (S[11], "golias", cam(-3, 100, 0, -20), cam(3, 200, 0, -50), ("relampago", "vivo")),
    (at(11, .52), "davi", cam(3, 150, 0, -40), cam(-2, 260, 0, -60), ("sombra", "vivo")),
    (at(11, .74), "2", G0, cam(py=GPY, dolly=60), ("brilho",)),
]
MD = 0.95
FLASH = {S[1] + 1.1: 1.0, S[1] + 1.25: .6, S[1] + 3.6: .8, S[10] + .6: .9, S[11] + .3: 1.0, S[11] + .45: .5, S[11] + 1.9: .7}

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def ease_io(x): x = np.clip(x, 0, 1); return np.where(x < .5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)

def cam_at(k, t):
    t0 = KEYS[k][0]; t1 = KEYS[k + 1][0] + MD if k + 1 < len(KEYS) else TOTAL
    u = ease((t - t0) / max(.1, t1 - t0))
    a, b = KEYS[k][2], KEYS[k][3]
    c = {key: a[key] + (b[key] - a[key]) * u for key in a}
    if "tremor" in KEYS[k][4] and t - t0 < .6:
        amp = 14 * (1 - (t - t0) / .6); r = np.random.default_rng(int(t * 1000))
        c["px"] += r.normal(0, amp); c["py"] += r.normal(0, amp)
    return c

IDX = np.arange(N)
PH = np.random.default_rng(5).random(N).astype(np.float32) * 6.283
TWK = np.random.default_rng(6).random(N) < 0.04
def fx_mult(k, t, UV, I):
    fx = KEYS[k][4]; u, w = UV[:, 0], UV[:, 1]; m = np.ones(N, np.float32)
    if "ceu" in fx:
        c = -0.3 + ((t * 0.17 + k * .3) % 1.6)
        m *= 1 + 0.9 * np.exp(-((u - c) / .18) ** 2 - ((w - .22) / .2) ** 2) * (w < .6)
        m *= 1 + 0.18 * np.sin(7 * u + t * .9 + 5 * w) * (w < .55)
    if "estrelas" in fx:
        tw = np.maximum(0, np.sin(t * (2 + 3 * PH / 6.28) + PH)) ** 8
        m *= np.where(TWK & (w < .55) & (I > .35), 1 + 2.2 * tw, 1)
    if "relampago" in fx:
        fl = sum(g * np.exp(-((t - tf) / .045) ** 2) for tf, g in FLASH.items())
        m *= 1 + 2.6 * fl * np.clip(1.15 - w, 0, 1)
    if "raios" in fx:
        ang = np.arctan2(u - (.5 + .1 * np.sin(t * .5)), w + .25)
        beams = sum(np.exp(-((ang - a0 - .05 * np.sin(t * .7 + a0 * 9)) / .045) ** 2) for a0 in (-.32, -.1, .12, .3))
        m *= 1 + 0.75 * beams * np.clip(1.1 - w, 0, 1)
    if "chama" in fx:
        m *= 1 + 0.16 * np.sin(t * 13 + u * 4) * np.sin(t * 7.3 + w * 3)
    if "brasas" in fx:
        m *= np.where(TWK & (I < .5), 1 + 1.8 * np.maximum(0, np.sin(t * 4 + PH)) ** 6, 1)
    if "brilho" in fx:
        m *= 1 + 0.6 * np.exp(-((u - ((t * .5) % 1.6 - .3)) / .08) ** 2)
    if "pulso" in fx:
        m *= 1 + 0.25 * np.exp(-(((t - KEYS[k][0]) % (60 / 64)) / .12) ** 2)
    if "sombra" in fx:
        m *= 0.45 + 0.45 * np.clip(w * 1.3, 0, 1)
    return m

def project_key(k, t):
    P, I, UV = C[KEYS[k][1]]
    c = cam_at(k, t)
    Q = P
    if "vivo" in KEYS[k][4]:  # respiração: ondulação lenta + leve vento
        Q = P.copy()
        Q[:, 0] += 2.2 * np.sin(0.011 * P[:, 1] + t * 1.1 + PH * .3)
        Q[:, 1] += 1.6 * np.cos(0.009 * P[:, 0] + t * .8 + PH * .3)
    x, y, z, s = pt.project(Q, yaw=np.radians(c["yaw"]), pitch=np.radians(c["pitch"]), dolly=c["dolly"], pan=(c["px"], c["py"]))
    return x, y, z, s, I * fx_mult(k, t, UV, I), c["focus"]

MOTES = np.stack([rng.uniform(-900, 900, 260), rng.uniform(-1200, 1200, 260), rng.uniform(-1150, -500, 260)], 1).astype(np.float32)
MV = rng.normal(0, 1, (260, 3)).astype(np.float32) * [6, 4, 3] + [0, -14, 0]

def state(t):
    k = max(i for i, key in enumerate(KEYS) if key[0] <= t)
    x, y, z, s, I, foc = project_key(k, t)
    u = (t - KEYS[k][0]) / MD
    if k > 0 and u < 1:
        x0, y0, z0, s0, I0, f0 = project_key(k - 1, t)
        xn = np.clip(x / W, 0, 1)
        dl = .28 * xn + .12 * PH / 6.28
        uu = ease_io((u - dl) / .6)
        bump = np.sin(np.pi * uu)
        x = x0 * (1 - uu) + x * uu + bump * np.cos(PH * 3) * 120
        y = y0 * (1 - uu) + y * uu + bump * np.sin(PH * 3) * 120
        z = z0 * (1 - uu) + z * uu; s = s0 * (1 - uu) + s * uu; I = I0 * (1 - uu) + I * uu
        foc = f0 + (foc - f0) * float(ease(u))
    return x, y, z, s, I, foc

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
    parts = SPLIT[i].split("|"); tot = sum(len(p) for p in parts); out, c = [], 0
    for p in parts:
        a = at(i, c / tot); c += len(p); out.append([a - 0.08, None, p])
    for j in range(len(out) - 1): out[j][1] = out[j + 1][0]
    out[-1][1] = S[i] + D[i] - 0.05
    return [tuple(o) for o in out]
CAPS = [c for i in range(len(NARR)) for c in chunks(i)]
LBL = [(S[1] + .3, S[2], "O CAMPO DE BATALHA"),
       (at(3, .5), S[4], "HARPA"), (S[4] + .2, at(4, .42), "UNGIDO"), (at(4, .72), S[5], "DE VOLTA AO PASTO"),
       (S[5] + .2, S[6], "REI AOS 30"), (S[6] + .2, S[7], "VISTO"), (S[8] + .2, S[9], "O CORAÇÃO"),
       (S[9] + .2, at(9, .55), "ATRASO"), (at(9, .55), S[10], "TREINO"),
       (S[10] + .2, at(10, .45), "EM PÚBLICO"), (at(10, .45), S[11], "EM SECRETO"),
       (S[11] + .2, at(11, .52), "O MAIOR GIGANTE"), (at(11, .52), at(11, .74), "ELE MESMO"), (at(11, .74), TOTAL + 1, "PARTE 2")]
REFS = ["1 SM 17:4", "1 SM 17:5", "1 SM 16:11", "1 SM 17:34", "1 SM 16:13", "2 SM 5:4", "HOJE", "1 SM 16:7",
        "1 SM 16:7", "1 SM 17:37", "1 SM 17:50", "2 SM 11"]

def key_of(name, t0):
    return max(i for i, k in enumerate(KEYS) if k[1] == name and k[0] <= t0 + 1e-6)
def anchor(name, uv):
    UV = C[name][2]; return int(np.argmin(((UV - uv) ** 2).sum(1)))
# (início, fim, nuvem, uv, deslocamento da etiqueta, texto)
CALLS = [(0.9, at(0, .72), "confronto", (.70, .16), (90, -90), "GOLIAS · 2,9 M"),
         (1.7, at(0, .72), "confronto", (.25, .42), (-60, 170), "DAVI · UM PASTOR"),
         (at(0, .75) + .3, S[1], "pedra", (.42, .45), (80, 200), "PEDRA LISA · 1 SM 17:40"),
         (S[1] + 1.6, S[2], "golias", (.55, .42), (-150, -170), "ARMADURA · 57 KG"),
         (S[2] + 1.2, S[3], "pasto", (.47, .30), (130, -150), "ONDE NINGUÉM VIA"),
         (S[3] + .9, at(3, .5), "leao", (.53, .25), (-110, -150), "1 SM 17:34-35")]
CALLS = [(a, b, n, anchor(n, np.array(uv)), off, txt) for a, b, n, uv, off, txt in CALLS]

def fade(t, a, b, f=0.18): return float(np.clip(min((t - a) / f, (b - t) / f), 0, 1))

def overlays(img, t):
    d = ImageDraw.Draw(img)
    sc = max(j for j in range(len(S)) if S[j] <= t)
    d.text((70, 90), "CURIOSIDADES BÍBLICAS — DAVI", font=f_ui, fill=170)
    d.text((W - 70, 90), REFS[sc], font=f_ui, fill=170, anchor="ra")
    d.line([(70, 140), (W - 70, 140)], fill=60, width=2)
    for i in range(40):
        x = 70 + i * (W - 140) / 39; on = i / 39 <= t / TOTAL
        d.line([(x, 1740), (x, 1766 if on else 1752)], fill=230 if on else 70, width=3)
    for a, b, s in LBL:
        al = fade(t, a, b)
        if al > 0:
            n = int(len(s) * np.clip((t - a) / 0.3, 0, 1))
            d.text((CX, 300 + (1 - al) * 10), s[:n], font=f_lbl, fill=int(255 * al), anchor="mm")
            if s == "O CAMPO DE BATALHA" and t > a + .7:
                w = d.textlength(s, font=f_lbl); u = min(1, (t - a - .7) / .4)
                d.line([(CX - w / 2 - 10, 300), (CX - w / 2 - 10 + (w + 20) * u, 300)], fill=int(255 * al), width=4)
    for a, b, name, idx, (dx, dy), txt in CALLS:
        al = fade(t, a, b, .2)
        if al <= 0: continue
        k = key_of(name, a); c = cam_at(k, t)
        ax, ay, _, _ = pt.project(C[name][0][idx:idx + 1], yaw=np.radians(c["yaw"]), pitch=np.radians(c["pitch"]),
                                  dolly=c["dolly"], pan=(c["px"], c["py"]))
        ax, ay = float(ax[0]), float(ay[0])
        u = float(ease((t - a) / .5)); ex, ey = ax + dx * u, ay + dy * u
        side = 1 if dx >= 0 else -1; tw = d.textlength(txt, font=f_call)
        hx = ex + side * (tw + 24) * float(ease((t - a - .35) / .45)); col = int(240 * al)
        r = 9 + 3 * np.sin(t * 5)
        d.ellipse([ax - r, ay - r, ax + r, ay + r], outline=col, width=3); d.ellipse([ax - 3, ay - 3, ax + 3, ay + 3], fill=col)
        d.line([(ax, ay), (ex, ey), (hx, ey)], fill=col, width=2)
        nch = int(len(txt) * np.clip((t - a - .45) / .5, 0, 1))
        d.text((ex + side * 12, ey - 10), txt[:nch], font=f_call, fill=col, anchor="ls" if side > 0 else "rs")
    al = fade(t, S[5] + .3, S[6] - .05)
    if al > 0:
        u = min(1, (t - S[5] - .3) / 1.2); x0, x1 = 160, 920
        d.line([(x0, 1260), (x0 + (x1 - x0) * u, 1260)], fill=int(220 * al), width=3)
        d.text((x0, 1300), "UNÇÃO", font=f_ui, fill=int(200 * al), anchor="lm")
        if u > .95: d.text((x1, 1300), "TRONO", font=f_ui, fill=int(200 * al), anchor="rm")
    if S[6] + .4 < t < S[7]:
        v = int(10 ** min(6, (t - S[6] - .4) / 2.2 * 6))
        d.text((CX, 1345), f"{v:,} VISUALIZAÇÕES".replace(",", "."), font=f_lbl, fill=220, anchor="mm")
    al = fade(t, S[9] + .2, S[10])
    if al > 0:
        x0 = CX - (5 * 120 + 4 * 46) / 2
        for i in range(5): d.text((x0 + i * 166 + 60, 1200), f"0{i+1}", font=f_ui, fill=int(200 * al), anchor="mm")
    al = fade(t, at(11, .9), TOTAL + 1, .3)
    if al > 0: d.text((CX, 1430), "SEGUE PRA NÃO PERDER  →", font=f_lbl, fill=int(235 * al), anchor="mm")
    for a, b, s in CAPS:
        al = fade(t, a, b, 0.07)
        if al > 0: d.text((CX, 1610 + (1 - al) * 12), s, font=f_cap, fill=int(255 * al), anchor="mm")

SCRIM = (1 - 0.85 * np.clip((np.arange(H)[:, None] - 1420) / 160, 0, 1) * np.clip((1820 - np.arange(H)[:, None]) / 60, 0, 1)
         - 0.6 * np.clip((200 - np.arange(H)[:, None]) / 80, 0, 1)).astype(np.float32)

def render(fi):
    t = fi / FPS
    x, y, z, s, I, foc = state(t)
    k = max(i for i, key in enumerate(KEYS) if key[0] <= t); c = cam_at(k, t)
    M = MOTES + MV * t
    mx, my, mz, ms = pt.project(M, yaw=np.radians(c["yaw"]), dolly=c["dolly"] * .5)
    x = np.concatenate([x, mx]); y = np.concatenate([y, my]); z = np.concatenate([z, mz]); s = np.concatenate([s, ms])
    I = np.concatenate([np.clip(I, 0, 3), np.full(len(mx), .5, np.float32) * (.6 + .4 * np.sin(t * 1.3 + np.arange(len(mx))))])
    a = pt.render(x, y, z, s, I, focus_z=foc, gain=1.2, glow=.4, dof=.005)
    a *= SCRIM
    master = float(np.clip((TOTAL - t) / .35, 0, 1)) if t > TOTAL - .35 else 1.0
    img = Image.fromarray(pt.finish(a, t)); overlays(img, t)
    if master < 1: img = Image.fromarray((np.asarray(img, np.float32) * master).astype(np.uint8))
    img.save(f"{FR}/f{fi:05d}.png")

# ---------- áudio ----------
def audio():
    SR = 44100; ts = np.arange(int(SR * TOTAL)) / SR; mu = np.zeros_like(ts); n = rng.normal(0, 1, len(ts))
    lp = lambda x, a: lfilter([a], [1, a - 1], x)
    def tone(f, t0, dur, g, att=1.2, rel=1.5):
        m = (ts >= t0) & (ts < t0 + dur + rel); tt = ts[m] - t0
        env = np.clip(tt / att, 0, 1) * np.clip((t0 + dur + rel - ts[m]) / rel, 0, 1)
        mu[m] += g * env * (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * 2 * f * tt + .5 * np.sin(2 * np.pi * .3 * tt)))
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    prog = [(0, [50, 57, 62, 65]), (S[3], [46, 53, 58, 62]), (S[5], [48, 55, 60, 64]), (S[6], [50, 57, 62, 65]),
            (S[7], [46, 53, 58, 62, 65]), (S[8], [41, 48, 57, 60, 65]), (S[9], [43, 50, 58, 62]),
            (S[10], [50, 57, 62, 66, 69]), (S[11], [38, 45, 50, 53]), (at(11, .52), [38, 50, 51, 53])]
    for j, (t0, notes) in enumerate(prog):
        t1 = prog[j + 1][0] if j + 1 < len(prog) else TOTAL
        for m in notes: tone(hz(m), t0, t1 - t0, 0.018, rel=1.2)
    for bt in [b for b in np.arange(0.0, TOTAL, 60 / 76) if not (at(11, .45) < b < at(11, .62))]:
        for off, g in ((0, .3), (.18, .18)):
            m = ts >= bt + off; tt = ts[m] - bt - off; mu[m] += g * np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 11)
    wh = lp(n, 0.06)
    for key in KEYS[1:]: mu += 0.25 * wh * np.exp(-((ts - key[0] - MD / 2) / 0.3) ** 2)
    for a, b, s in LBL:
        m = (ts >= a) & (ts < a + .025); mu[m] += .08 * np.sign(np.sin(2 * np.pi * 2600 * ts[m]))
    for a, *_ in CALLS:
        m = (ts >= a + .45) & (ts < a + .47); mu[m] += .07 * np.sign(np.sin(2 * np.pi * 3100 * ts[m]))
    thunder = lp(lp(n, .02), .05)
    for tf, g in FLASH.items():  # trovão logo depois do clarão
        m = ts >= tf + .15; tt = ts[m] - tf - .15
        mu[m] += 2.2 * g * thunder[m] * np.exp(-tt * 2.2) * np.clip(tt / .05, 0, 1)
    for tk, g in ((at(0, .72), .8), (S[3], 1.0), (at(11, .52), 1.0), (at(11, .74), .9)):
        m = ts >= tk; tt = ts[m] - tk
        mu[m] += g * (.9 * np.sin(2 * np.pi * (60 * np.exp(-tt * 3) + 38) * tt) * np.exp(-tt * 4) + .3 * lp(n[m], .2) * np.exp(-tt * 18))
    mu /= np.abs(mu).max()
    voice = np.zeros_like(ts); ir = rng.normal(0, 1, int(SR * 1.2)) * np.exp(-np.arange(int(SR * 1.2)) / SR * 5)
    for i, x in enumerate(NARR):
        v, sr = sf.read(os.path.join(NARRDIR, os.path.basename(x["wav"]))); v = resample_poly(v, SR, sr) if sr != SR else v
        v = v / (np.sqrt(np.mean(v ** 2)) + 1e-9) * 0.12
        i0 = int((S[i] + LEAD) * SR); v = v[:len(ts) - i0]; voice[i0:i0 + len(v)] += v
    voice = voice + fftconvolve(voice, ir)[:len(ts)] * 0.004
    duck = 1 - 0.55 * np.clip(lp((np.abs(voice) > 0.01).astype(float), 0.0005) * 3, 0, 1)
    out = voice + mu * 0.22 * duck
    out *= np.clip((TOTAL - ts) / .35, 0, 1); out = out / np.abs(out).max() * 0.9
    with wave.open(os.path.join(HERE, "audio.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    print(f"duração {TOTAL:.1f}s, {NF} quadros")
    if len(sys.argv) > 1 and sys.argv[1] == "prev":
        fis = [int(float(x) * FPS) for x in sys.argv[2:]]
        with Pool(4) as pl: pl.map(render, fis)
        ims = [Image.open(f"{FR}/f{i:05d}.png").resize((270, 480)) for i in fis]
        cols = min(6, len(ims)); g = Image.new("L", (270 * cols, 480 * ((len(ims) + cols - 1) // cols)))
        for j, im in enumerate(ims): g.paste(im, ((j % cols) * 270, (j // cols) * 480))
        g.save(os.path.join(HERE, "preview.png")); sys.exit()
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "reel_davi_v2.mp4")
    with Pool(4) as pl: pl.map(render, range(NF), chunksize=6)
    audio()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/f%05d.png",
                    "-i", os.path.join(HERE, "audio.wav"), "-c:v", "libx264", "-b:v", "3.8M", "-maxrate", "4.5M",
                    "-bufsize", "8M", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", out], check=True)
    print("ok", out)
