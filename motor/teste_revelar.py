"""Teste: imagem viva -> linha de luz converte em partículas -> ganha 3D e se desfaz em poeira (7s, 9:16)."""
import os, sys, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
from scipy.signal import lfilter
import particulas as pt

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, CX, CY = pt.W, pt.H, pt.W / 2, pt.CY
FPS, DUR = 30, 7.0
NF = int(FPS * DUR)
FR = os.path.join(HERE, "frames_rev"); os.makedirs(FR, exist_ok=True)
f_cap = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 50)
f_ui = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 26)

U0, U1, IMH = 0.15, 0.80, 1080
src = Image.open(os.path.join(HERE, "img/davi/06_leao.jpg")).convert("L")
crop = src.crop((int(U0 * src.width), 0, int(U1 * src.width), src.height))
A = np.asarray(crop, np.float32) / 255
IMW = IMH * crop.width / crop.height
P, I, UV = pt.cloud_from_array(A, IMW, spacing=5.0, gamma=1.1, thresh=0.10, autolevel=True,
                               depth=160, lumdepth=150, feather=0.1, seed=5)
n = len(I)
Z3 = P[:, 2].copy()
rng = np.random.default_rng(2)
DUST = rng.normal(0, 1, (n, 3)).astype(np.float32) * [260, 380, 200] + [0, -140, 120]
PH = rng.random(n).astype(np.float32) * 6.283

# imagem com as mesmas bordas esfumadas da nuvem
gh, gw = A.shape
yy, xx = np.mgrid[0:gh, 0:gw]; u = (xx + .5) / gw; w = (yy + .5) / gh
fe = np.clip(np.minimum.reduce([u, 1 - u, w, 1 - w]) / 0.1, 0, 1); fe = fe * fe * (3 - 2 * fe)
lo, hi = np.percentile(A, [3, 99.7]); AL = np.clip((A - lo) / (hi - lo), 0, 1)

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
T_CONV0, T_CONV1, T_DUST = 2.2, 3.6, 5.6

def frame(fi):
    t = fi / FPS
    dolly = 40 + 90 * t / DUR
    yaw = np.radians(9 * ease((t - 3.4) / 2.2))
    # --- partículas: chatas no começo (alinhadas com a imagem), ganham profundidade depois
    Q = P.copy(); Q[:, 2] = Z3 * ease((t - 3.0) / 1.5)
    Q[:, 0] += 2 * np.sin(0.011 * P[:, 1] + t * 1.1 + PH * .3)
    k = ease((t - T_DUST - PH / 6.283 * .4) / 1.2)[:, None]
    Iv_f = 1 - 0.6 * k[:, 0]
    Q = Q * (1 - k) + (Q + DUST) * k
    x, y, z, s = pt.project(Q, yaw=yaw, dolly=dolly)
    Iv = Iv_f * I * (1 + 0.16 * np.sin(t * 13 + UV[:, 0] * 4) * np.sin(t * 7.3 + UV[:, 1] * 3))
    part = pt.render(x, y, z, s, Iv, focus_z=-40, gain=1.9, glow=.55, dof=.005)
    # --- imagem viva no mesmo enquadramento
    sc = pt.FOCAL / (pt.CAM_D - dolly)
    iw, ih = int(IMW * sc), int(IMH * sc)
    sweep = 1 + 0.35 * np.exp(-((u - ((t * .35) % 1.6 - .3)) / .15) ** 2)          # luz passando
    flick = 1 + 0.06 * np.sin(t * 11) * np.sin(t * 6.1)
    im = Image.fromarray((np.clip(AL * sweep * flick * fe, 0, 1) * 255).astype(np.uint8)).resize((iw, ih), Image.LANCZOS)
    layer = np.zeros((H, W), np.float32)
    x0, y0 = int(CX - iw / 2), int(CY - ih / 2)
    sx0, sy0 = max(0, -x0), max(0, -y0); dx0, dy0 = max(0, x0), max(0, y0)
    wv, hv = min(iw - sx0, W - dx0), min(ih - sy0, H - dy0)
    layer[dy0:dy0 + hv, dx0:dx0 + wv] = np.asarray(im, np.float32)[sy0:sy0 + hv, sx0:sx0 + wv]
    # --- frente de conversão diagonal com linha de luz
    gy, gx = np.mgrid[0:H, 0:W]
    diag = (gx / W * .45 + gy / H * .55)
    front = -0.15 + 1.35 * ease((t - T_CONV0) / (T_CONV1 - T_CONV0))
    M = np.clip((front - diag) / 0.06, 0, 1)
    edge = np.exp(-((diag - front) / 0.006) ** 2) * (0.55 + 0.45 * (np.random.default_rng(fi).random((H, W)) > .6)) * (T_CONV0 < t < T_CONV1 + .3)
    out = layer * (1 - M) + part * M + 200 * edge * (layer > 8)
    img = Image.fromarray(pt.finish(out, t))
    d = ImageDraw.Draw(img)
    d.text((70, 90), "CURIOSIDADES BÍBLICAS — DAVI", font=f_ui, fill=170)
    d.text((W - 70, 90), "1 SM 17:34", font=f_ui, fill=170, anchor="ra")
    d.line([(70, 140), (W - 70, 140)], fill=60, width=2)
    cap = "Ali ele enfrentou" if t < 3.5 else "leão e urso."
    d.text((CX, 1610), cap, font=f_cap, fill=255, anchor="mm")
    img.save(f"{FR}/f{fi:04d}.png")

def audio():
    SR = 44100; ts = np.arange(int(SR * DUR)) / SR; r = np.random.default_rng(0); nz = r.normal(0, 1, len(ts))
    lp = lambda x, a: lfilter([a], [1, a - 1], x)
    mu = sum(0.03 * np.sin(2 * np.pi * f * ts) for f in (73.4, 110, 146.8, 174.6)) * np.clip(ts, 0, 1)
    for bt in np.arange(0, DUR, 60 / 76):
        m = ts >= bt; tt = ts[m] - bt; mu[m] += .3 * np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 11)
    sh = nz - lp(nz, .3)                                                           # chiado da conversão
    mu += .35 * sh * np.exp(-((ts - (T_CONV0 + T_CONV1) / 2) / .55) ** 2)
    mu += .5 * lp(nz, .05) * np.exp(-((ts - T_DUST - .6) / .5) ** 2)               # sopro da poeira
    out = mu / np.abs(mu).max() * .8 * np.clip((DUR - ts) / .4, 0, 1)
    with wave.open(os.path.join(HERE, "audio_rev.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fis = [int(float(x) * FPS) for x in sys.argv[1:]]
        with Pool(4) as pl: pl.map(frame, fis)
        ims = [Image.open(f"{FR}/f{i:04d}.png").resize((270, 480)) for i in fis]
        g = Image.new("L", (270 * len(ims), 480)); [g.paste(im, (j * 270, 0)) for j, im in enumerate(ims)]
        g.save(os.path.join(HERE, "preview_rev.png")); sys.exit()
    with Pool(4) as pl: pl.map(frame, range(NF))
    audio()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/f%04d.png", "-i",
                    os.path.join(HERE, "audio_rev.wav"), "-c:v", "libx264", "-b:v", "6M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest", os.path.join(HERE, "..", "teste_imagem_vira_particulas.mp4")], check=True)
    print("ok")
