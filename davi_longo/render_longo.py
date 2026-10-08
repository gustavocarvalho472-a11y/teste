"""Vídeo longo do Davi (16:9). Imagens nítidas e vivas com câmera lenta; na virada de cada capítulo
a imagem vira partículas, os pontos ganham 3D, formam o título do capítulo e depois a próxima imagem.

  python3 render_longo.py prev 3 10 31        -> grade de prévia (tempos em segundos)
  python3 render_longo.py teste 42            -> renderiza só os primeiros 42s
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
import particulas as pt

W, H, FPS = pt.W, pt.H, 30
IMG = os.path.join(ROOT, "motor/img/davi")
FR = os.path.join(HERE, "frames"); os.makedirs(FR, exist_ok=True)
NARRDIR = os.path.join(HERE, "narr")
NARR = json.load(open(os.path.join(NARRDIR, "timing.json")))
FONT = "/usr/share/fonts/opentype/inter/"
f_cap = ImageFont.truetype(FONT + "Inter-SemiBold.otf", 50)
f_ui = ImageFont.truetype(FONT + "Inter-Medium.otf", 22)

GAP, LEAD, TRANS = 0.35, 0.1, 5.0          # respiro entre falas, atraso da voz, duração da virada de capítulo

# ---------- linha do tempo a partir da narração ----------
S, SEC, sec_first = [], [], {}
t = 0.6
for i, x in enumerate(NARR):
    if i and x["sec"] != NARR[i - 1]["sec"]:
        t += 0.4 + TRANS
    if x["sec"] not in sec_first: sec_first[x["sec"]] = i
    S.append(t); SEC.append(x["sec"]); t += x["dur"] + GAP
TOTAL = t + 2.5
NF = int(TOTAL * FPS)
def at(i, f): return S[i] + f * NARR[i]["dur"]
SECS = list(sec_first)                                   # ordem dos capítulos
TR = [S[sec_first[s]] - TRANS for s in SECS[1:]]         # início de cada virada

TITLE = {"1.": ("CAPÍTULO 1", "O FILHO QUE NINGUÉM CHAMOU"), "2.": ("CAPÍTULO 2", "UNGIDO… E DE VOLTA AO PASTO"),
         "3.": ("CAPÍTULO 3", "O MÚSICO DO REI"), "4.": ("CAPÍTULO 4", "QUARENTA DIAS DE MEDO"),
         "5.": ("CAPÍTULO 5", "O ENTREGADOR"), "6.": ("CAPÍTULO 6", "A ARMADURA QUE NÃO SERVIU"),
         "7.": ("CAPÍTULO 7", "UMA PEDRA"), "FE": ("", "")}
REF = {"GA": "1 SM 16:11", "1.": "1 SM 16:1–11", "2.": "1 SM 16:12–13", "3.": "1 SM 16:14–23", "4.": "1 SM 17:1–16",
       "5.": "1 SM 17:15–30", "6.": "1 SM 17:31–40", "7.": "1 SM 17:41–58", "FE": "1 SM 16:7"}

# ---------- planos: (fala, fração da fala, imagem, (cx, cy, zoom) inicial, final) ----------
SHOTS = [
    (0, 0, "19_davi_sozinho", (.62, .40, 1.9), (.60, .42, 1.6)),
    (1, 0, "07_samuel_filhos", (.30, .50, 1.25), (.25, .48, 1.45)),
    (2, 0, "07_samuel_filhos", (.68, .52, 1.55), (.62, .52, 1.35)),
    (2, .62, "15_davi_chega", (.20, .55, 1.9), (.22, .55, 1.7)),
    (3, 0, "19_davi_sozinho", (.32, .62, 1.6), (.48, .50, 1.05)),
    (4, 0, "01_davi", (.50, .38, 1.5), (.50, .36, 1.75)),
    (5, 0, "03_confronto", (.50, .50, 1.0), (.45, .45, 1.2)),
    (5, .5, "18_golias_caido", (.55, .55, 1.15), (.62, .50, 1.35)),
    (6, 0, "07_samuel_filhos", (.17, .45, 1.9), (.19, .46, 1.65)),
    (7, 0, "07_samuel_filhos", (.50, .50, 1.05), (.52, .50, 1.2)),
    (8, 0, "08_eliabe", (.56, .38, 1.5), (.55, .45, 1.15)),
]

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

def shot_times():
    st = []
    for j, (li, fr, *_r) in enumerate(SHOTS):
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

@functools.lru_cache(maxsize=8)
def load(name):
    return Image.open(os.path.join(IMG, name + ".jpg")).convert("L")

def params(j, t):
    _, _, name, p0, p1 = SHOTS[j]
    u = (t - ST[j]) / max(1e-3, EN[j] - ST[j])
    u = np.clip(u, -.1, 1.15); k = u * u * (3 - 2 * u) * .5 + u * .5            # leve aceleração/desaceleração
    return name, [a + (b - a) * k for a, b in zip(p0, p1)]

def view(name, p):
    im = load(name); cx, cy, z = p
    cw = im.width / z; ch = cw * H / W
    if ch > im.height / z * 1.0: ch = im.height / z; cw = ch * W / H
    x0 = np.clip(cx * im.width - cw / 2, 0, im.width - cw); y0 = np.clip(cy * im.height - ch / 2, 0, im.height - ch)
    return np.asarray(im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC), np.float32)

GY, GX = np.mgrid[0:H, 0:W].astype(np.float32)
def alive(a, t, seed=0):
    """Imagem 'viva': luz atravessando devagar, respiração de brilho, contraste levemente realçado."""
    sweep = 1 + .22 * np.exp(-((GX / W * .8 + GY / H * .2 - ((t * .07 + seed * .37) % 1.6 - .3)) / .18) ** 2)
    br = 1 + .035 * np.sin(t * 1.7 + seed)
    return np.clip(a * sweep * br, 0, 255)

def shot_index(t):
    j = 0
    for k in range(len(SHOTS)):
        if ST[k] <= t: j = k
    return j

# ---------- poeira flutuando (desfocada) ----------
rng = np.random.default_rng(7)
DN = 220
DUST = np.c_[rng.random(DN) * W, rng.random(DN) * H, rng.random(DN)]
def dust(t):
    buf = np.zeros((H, W), np.float32)
    x = (DUST[:, 0] + t * (8 + 20 * DUST[:, 2]) + 30 * np.sin(t * .3 + DUST[:, 1])) % W
    y = (DUST[:, 1] - t * (5 + 12 * DUST[:, 2])) % H
    pt.splat(x.astype(np.float32), y.astype(np.float32), (40 + 80 * DUST[:, 2] * (.6 + .4 * np.sin(t * 2 + DUST[:, 0]))).astype(np.float32), buf)
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(buf, 2.2) * 12

# ---------- nuvens para a virada de capítulo ----------
N = 120000
def title_mask(a, b):
    img = Image.new("L", (W, H), 0); d = ImageDraw.Draw(img)
    d.text((W / 2, H / 2 - 70), a, font=ImageFont.truetype(FONT + "Inter-Medium.otf", 34), fill=200, anchor="mm")
    fs = 92 if len(b) < 22 else 76
    d.text((W / 2, H / 2 + 10), b, font=ImageFont.truetype(FONT + "Inter-Bold.otf", fs), fill=255, anchor="mm")
    d.line([(W / 2 - 60, H / 2 + 90), (W / 2 + 60, H / 2 + 90)], fill=180, width=3)
    return np.asarray(img, np.float32) / 255

def img_cloud(arr, seed):
    P, I, UV = pt.cloud_from_array(arr / 255, W, spacing=4.0, gamma=1.15, thresh=.08, autolevel=True,
                                   depth=150, lumdepth=170, feather=.03, enhance=.7, seed=seed)
    return pt.resample(P, I, UV, N, seed=seed)

@functools.lru_cache(maxsize=2)
def trans_clouds(k):
    t0 = TR[k]; j_prev = shot_index(t0 - 1e-3); j_next = shot_index(t0 + TRANS + 1e-3)
    A = view(*params(j_prev, t0)); B = view(*params(j_next, t0 + TRANS))
    PA, IA, _ = img_cloud(A, 3 + k); PB, IB, _ = img_cloud(B, 11 + k)
    a, b = TITLE[SECS[k + 1][:2]]
    PT, IT, _ = pt.cloud_from_array(title_mask(a, b), W, spacing=2.6, gamma=1, thresh=.3, enhance=0,
                                    depth=0, feather=0, seed=5)
    PT, IT, _ = pt.resample(PT, IT, np.zeros((len(IT), 2), np.float32), N, seed=6)
    r = np.random.default_rng(k)
    return A, B, PA, IA, PB, IB, PT, IT * .3, r.random(N).astype(np.float32), r.normal(0, 1, (N, 3)).astype(np.float32)

def transition(k, u, t):
    """u: 0..TRANS dentro da virada k."""
    A, B, PA, IA, PB, IB, PT, IT, PH, RN = trans_clouds(k)
    zA = ease((u - .7) / 1.0); zB = 1 - ease((u - 3.5) / .8)
    m1 = ease((u - 1.5 - PH * .5) / 1.1)[:, None]                  # imagem -> título (cada ponto no seu tempo)
    m2 = ease((u - 3.3 - PH * .4) / 1.0)[:, None]                  # título -> próxima imagem
    QA = PA.copy(); QA[:, 2] *= zA
    QB = PB.copy(); QB[:, 2] *= min(zB, ease((u - 3.0) / .6))
    Q = QA * (1 - m1) + PT * m1
    Q = Q * (1 - m2) + QB * m2
    fly = (np.sin(np.pi * m1[:, 0]) + np.sin(np.pi * m2[:, 0]))[:, None]
    Q = Q + fly * RN * [110, 80, 110]
    I = IA * (1 - m1[:, 0]) + IT * m1[:, 0]; I = I * (1 - m2[:, 0]) + IB * m2[:, 0]
    I = I * (1 + .12 * np.sin(t * 9 + PH * 30)) * (1 - .45 * np.clip(fly[:, 0], 0, 1))                      # pontos que respiram
    orbit = ease((u - .8) / 1.2) * (1 - ease((u - 3.4) / 1.0))
    x, y, z, s = pt.project(Q, yaw=np.radians(16) * orbit * np.sin(u * .6 + .3), pitch=np.radians(-5) * orbit,
                            dolly=120 * orbit)
    part = pt.render(x, y, z, s, I, focus_z=0, dof=.006, gain=1.5, glow=.5)
    # frente de conversão (linha de luz) na entrada e na saída
    diag = GX / W * .45 + GY / H * .55
    f_in = -0.1 + 1.25 * ease(u / 1.0); f_out = -0.1 + 1.25 * ease((u - 4.15) / .8)
    MA = np.clip((f_in - diag) / .05, 0, 1)                           # 1 = já virou partícula
    MB = np.clip((f_out - diag) / .05, 0, 1)                          # 1 = já virou imagem
    a_img = alive(A, t, 1); b_img = alive(B, t, 2)
    out = a_img * (1 - MA) + part * MA
    out = out * (1 - MB) + b_img * MB
    edge = lambda f: np.exp(-((diag - f) / .005) ** 2)
    if u < 1.2: out += 190 * edge(f_in) * (a_img > 10)
    if u > 4.1: out += 190 * edge(f_out) * (b_img > 10)
    return out

# ---------- legendas (blocos de 2 a 4 palavras) ----------
def chunks(text):
    """Quebra por pontuação e divide cada trecho em blocos equilibrados de até 4 palavras."""
    out, cl = [], []
    for x in text.replace('"', "").split():
        cl.append(x)
        if x[-1] in ".,:;?!…": out += split_even(cl); cl = []
    return out + split_even(cl)
def split_even(ws):
    if not ws: return []
    g = -(-len(ws) // 4); b = np.linspace(0, len(ws), g + 1).round().astype(int)
    return [" ".join(ws[b[k]:b[k + 1]]) for k in range(g)]
CAPS = []
for i, x in enumerate(NARR):
    cs = chunks(x["text"]); tot = sum(len(c) for c in cs); c0 = 0
    for c in cs:
        CAPS.append([S[i] + LEAD + x["dur"] * c0 / tot - .05, S[i] + LEAD + x["dur"] * (c0 + len(c)) / tot, c]); c0 += len(c)
for j in range(len(CAPS) - 1):
    if CAPS[j + 1][0] - CAPS[j][1] < .4: CAPS[j][1] = CAPS[j + 1][0]

def overlays(img, t):
    d = ImageDraw.Draw(img)
    sec = SEC[max(0, np.searchsorted(S, t, "right") - 1)]
    d.text((60, 46), "CURIOSIDADES BÍBLICAS — DAVI", font=f_ui, fill=175)
    d.text((W - 60, 46), REF.get(sec[:2], ""), font=f_ui, fill=175, anchor="ra")
    d.line([(60, 84), (W - 60, 84)], fill=70, width=1)
    d.line([(60, H - 34), (W - 60, H - 34)], fill=45, width=2)
    d.line([(60, H - 34), (60 + (W - 120) * t / TOTAL, H - 34)], fill=200, width=2)
    for a, b, c in CAPS:
        if a <= t < b:
            al = min(1, (t - a) / .12, (b - t) / .12)
            sh = Image.new("L", img.size, 0); ImageDraw.Draw(sh).text((W / 2, H - 140), c, font=f_cap, fill=255, anchor="mm")
            sh = sh.filter(ImageFilter.GaussianBlur(8))
            base = np.asarray(img, np.float32) * (1 - .55 * al * np.asarray(sh, np.float32) / 255)
            img.paste(Image.fromarray(base.astype(np.uint8)))
            ImageDraw.Draw(img).text((W / 2, H - 140), c, font=f_cap, fill=int(255 * al), anchor="mm")

def render(fi):
    t = fi / FPS
    k = next((k for k, t0 in enumerate(TR) if t0 <= t < t0 + TRANS), None)
    if k is not None:
        a = transition(k, t - TR[k], t)
    else:
        j = shot_index(t)
        a = alive(view(*params(j, t)), t, j)
        if j and t - ST[j] < .6 and SEC[SHOTS[j][0]] == SEC[SHOTS[j - 1][0]]:   # dissolve entre planos
            q = ease((t - ST[j]) / .6); a = a * q + alive(view(*params(j - 1, t)), t, j - 1) * (1 - q)
        a = a + dust(t)
    master = min(1, t / .8, (TOTAL - t) / 1.2)
    img = Image.fromarray(pt.finish(a * master, t, grain=5, vignette=.5)); overlays(img, t)
    img.save(f"{FR}/f{fi:05d}.png")

# ---------- áudio ----------
def audio(T):
    SR = 44100; ts = np.arange(int(SR * T)) / SR; mu = np.zeros_like(ts); n = rng.normal(0, 1, len(ts))
    lp = lambda x, a: lfilter([a], [1, a - 1], x)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    def tone(f, t0, dur, g, att=2.0, rel=2.0):
        m = (ts >= t0) & (ts < t0 + dur + rel); tt = ts[m] - t0
        env = np.clip(tt / att, 0, 1) * np.clip((t0 + dur + rel - ts[m]) / rel, 0, 1)
        mu[m] += g * env * (np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * 2 * f * tt + .5 * np.sin(2 * np.pi * .2 * tt)))
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64], [45, 52, 57, 61]]
    for j, t0 in enumerate(np.arange(0, T, 9.0)):
        for m in chords[j % 4]: tone(hz(m), t0, 9.0, .016)
    for bt in np.arange(0, T, 60 / 64):
        m = ts >= bt; tt = ts[m] - bt; mu[m] += .16 * np.sin(2 * np.pi * 50 * tt) * np.exp(-tt * 10)
    wh = lp(n, .06)
    for t0 in TR:
        if t0 > T: break
        mu += .5 * wh * np.exp(-((ts - t0 - .5) / .4) ** 2)               # sopro da conversão
        mu += .4 * wh * np.exp(-((ts - t0 - 3.7) / .5) ** 2)
        m = ts >= t0 + 2.4; tt = ts[m] - t0 - 2.4                            # impacto no título
        mu[m] += .9 * np.sin(2 * np.pi * (55 * np.exp(-tt * 3) + 36) * tt) * np.exp(-tt * 3)
    mu /= np.abs(mu).max()
    voice = np.zeros_like(ts); ir = rng.normal(0, 1, int(SR * 1.2)) * np.exp(-np.arange(int(SR * 1.2)) / SR * 5)
    for i, x in enumerate(NARR):
        i0 = int((S[i] + LEAD) * SR)
        if i0 >= len(ts): break
        v, sr = sf.read(os.path.join(NARRDIR, x["wav"])); v = resample_poly(v, SR, sr) if sr != SR else v
        v = v / (np.sqrt(np.mean(v ** 2)) + 1e-9) * .12; v = v[:len(ts) - i0]; voice[i0:i0 + len(v)] += v
    voice = voice + fftconvolve(voice, ir)[:len(ts)] * .004
    duck = 1 - .5 * np.clip(lp((np.abs(voice) > .01).astype(float), .0005) * 3, 0, 1)
    out = voice + mu * .2 * duck
    out *= np.clip((T - ts) / 1.0, 0, 1); out = out / np.abs(out).max() * .9
    with wave.open(os.path.join(HERE, "audio.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    print(f"duração {TOTAL:.1f}s; viradas em {[round(x, 1) for x in TR]}")
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
                    "-i", os.path.join(HERE, "audio.wav"), "-frames:v", str(nf), "-c:v", "libx264", "-b:v", "4.5M",
                    "-maxrate", "5.5M", "-bufsize", "9M", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], check=True)
    print("ok", out)
