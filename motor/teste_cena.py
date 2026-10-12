"""Teste 5s: gravura de Doré em partículas 3D, órbita + push-in, montagem, anotações com linha, narração."""
import os, sys, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
import soundfile as sf
from scipy.signal import resample_poly
import particulas as pt

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, DUR = 30, 5.0
NF = int(FPS * DUR)
W, H, CX = pt.W, pt.H, pt.W / 2
FR = os.path.join(HERE, "frames"); os.makedirs(FR, exist_ok=True)
F = "/usr/share/fonts/opentype/inter/"
f_ui, f_cap, f_call = (ImageFont.truetype(F + "Inter-Medium.otf", 26), ImageFont.truetype(F + "Inter-SemiBold.otf", 50),
                       ImageFont.truetype(F + "Inter-SemiBold.otf", 28))

CROP, WIDTH = (0.12, 0.02, 0.98, 0.92), 1000
SUBJ = (0.45, 0.45, 0.28, 170)
P, I = pt.image_cloud(os.path.join(HERE, "img/dore_goliath.jpg"), spacing=6.0, gamma=1.6, thresh=0.14, feather=0.2,
                      crop=CROP, width=WIDTH, subject=SUBJ)
HEIGHT = WIDTH * (CROP[3] - CROP[1]) * 2413 / ((CROP[2] - CROP[0]) * 1920)
rng = np.random.default_rng(3)
n = len(I)
SCAT = P * [1.3, 1.3, 1] + (rng.normal(0, 1, (n, 3)) * [260, 360, 160] + [0, 0, 900]).astype(np.float32)
DELAY = (rng.random(n) * 0.5 + 0.35 * (P[:, 1] - P[:, 1].min()) / np.ptp(P[:, 1])).astype(np.float32)  # monta de cima p/ baixo

def anchor(u, w):  # coordenadas na gravura original -> ponto 3D
    uc = (u - CROP[0]) / (CROP[2] - CROP[0]); wc = (w - CROP[1]) / (CROP[3] - CROP[1])
    X = (uc - .5) * WIDTH; Y = (wc - .5) * HEIGHT; Z = 260 * (.5 - wc)
    sx, sy, sr, sz = SUBJ
    Z -= sz * np.exp(-(((uc - sx) / sr) ** 2 + ((wc - sy) / (sr * 1.3)) ** 2))
    return np.array([[X, Y, Z]], np.float32)

CALLS = [(1.5, anchor(0.63, 0.62), (60, -120), "GOLIAS · 2,9 M"),
         (2.7, anchor(0.30, 0.64), (90, 230), "A ESPADA DO PRÓPRIO GIGANTE")]
CAPS = [(0.25, 1.75, "Davi derrubou um gigante"), (1.75, 3.25, "de quase três metros"), (3.25, 5.0, "com uma única pedra.")]

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def cam(t):
    u = t / DUR
    return dict(yaw=np.radians(-12 + 18 * ease(u)), pitch=np.radians(4 - 4 * u), dolly=40 + 300 * u ** 1.3, pan=(0, 40 - 60 * u))
def fade(t, a, b, f=.15): return float(np.clip(min((t - a) / f, (b - t) / f), 0, 1))

SCRIM = (1 - 0.8 * np.clip((np.arange(H)[:, None] - 1380) / 220, 0, 1) * np.clip((1800 - np.arange(H)[:, None]) / 80, 0, 1)).astype(np.float32)

def frame(fi):
    t = fi / FPS
    k = ease((t - DELAY) / 1.3)[:, None]
    Q = SCAT * (1 - k) + P * k
    c = cam(t)
    x, y, z, s = pt.project(Q, **c)
    focus = -60 + 700 * (1 - ease(t / 1.6))           # puxa o foco para o assunto
    a = pt.render(x, y, z, s, I, focus_z=focus, gain=1.9)
    a = a * SCRIM
    img = Image.fromarray(pt.finish(a, t)); d = ImageDraw.Draw(img)
    d.text((70, 90), "DAVI — Nº 01", font=f_ui, fill=170); d.text((W - 70, 90), "1 SAMUEL 17", font=f_ui, fill=170, anchor="ra")
    d.line([(70, 140), (W - 70, 140)], fill=60, width=2)
    for t0, A, (dx, dy), txt in CALLS:
        al = fade(t, t0, DUR + 1)
        if al <= 0: continue
        ax, ay, _, _ = pt.project(A, **c); ax, ay = float(ax[0]), float(ay[0])
        u = ease((t - t0) / 0.5)
        ex, ey = ax + dx * u, ay + dy * u
        side = 1 if dx >= 0 else -1
        tw = d.textlength(txt, font=f_call)
        hx = ex + side * (tw + 24) * ease((t - t0 - .35) / .45)
        col = int(240 * al)
        r = 9 + 4 * np.sin(t * 5)
        d.ellipse([ax - r, ay - r, ax + r, ay + r], outline=col, width=3); d.ellipse([ax - 3, ay - 3, ax + 3, ay + 3], fill=col)
        d.line([(ax, ay), (ex, ey), (hx, ey)], fill=col, width=2)
        nch = int(len(txt) * np.clip((t - t0 - .45) / .5, 0, 1))
        tx = ex + side * 12
        d.text((tx, ey - 10), txt[:nch], font=f_call, fill=col, anchor="ls" if side > 0 else "rs")
    for a0, b0, txt in CAPS:
        al = fade(t, a0, b0, .08)
        if al > 0: d.text((CX, 1600 + (1 - al) * 12), txt, font=f_cap, fill=int(255 * al), anchor="mm")
    for i in range(40):
        xx = 70 + i * (W - 140) / 39; on = i / 39 <= t / 57
        d.line([(xx, 1740), (xx, 1766 if on else 1752)], fill=230 if on else 70, width=3)
    img.save(f"{FR}/f{fi:04d}.png")

def audio():
    SR = 44100; ts = np.arange(int(SR * DUR)) / SR; mu = np.zeros_like(ts)
    rng2 = np.random.default_rng(0); nz = rng2.normal(0, 1, len(ts))
    from scipy.signal import lfilter
    lp = lambda x, a: lfilter([a], [1, a - 1], x)
    for f in (73.4, 110, 146.8, 174.6): mu += 0.03 * np.sin(2 * np.pi * f * ts) * np.clip(ts / 1.0, 0, 1)
    for bt in np.arange(0, DUR, 60 / 76):
        m = ts >= bt; tt = ts[m] - bt; mu[m] += .3 * np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 11)
    mu += .5 * lp(nz, .05) * np.exp(-((ts - .8) / .45) ** 2)                 # whoosh da montagem
    for t0, *_ in CALLS:
        m = (ts >= t0 + .45) & (ts < t0 + .47); mu[m] += .1 * np.sign(np.sin(2 * np.pi * 2600 * ts[m]))
    mu /= np.abs(mu).max()
    v, sr = sf.read(os.path.join(HERE, "../davi/narr/00.wav"))
    v = resample_poly(v, SR, sr); v = v / np.sqrt(np.mean(v ** 2)) * .12
    voice = np.zeros_like(ts); i0 = int(.3 * SR); voice[i0:i0 + len(v)] = v[:len(ts) - i0]
    out = voice + mu * .2 * (1 - .5 * (np.abs(lp(voice, .001)) > .002))
    out = out / np.abs(out).max() * .9 * np.clip((DUR - ts) / .3, 0, 1)
    with wave.open(os.path.join(HERE, "audio.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fis = [int(float(x) * FPS) for x in sys.argv[1:]]
        with Pool(4) as pl: pl.map(frame, fis)
        ims = [Image.open(f"{FR}/f{i:04d}.png").resize((360, 640)) for i in fis]
        g = Image.new("L", (360 * len(ims), 640)); [g.paste(im, (j * 360, 0)) for j, im in enumerate(ims)]
        g.save(os.path.join(HERE, "preview.png")); sys.exit()
    with Pool(4) as pl: pl.map(frame, range(NF))
    audio()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/f%04d.png", "-i",
                    os.path.join(HERE, "audio.wav"), "-c:v", "libx264", "-b:v", "6M", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-shortest", os.path.join(HERE, "../teste_motor_v2.mp4")], check=True)
    print("ok")
