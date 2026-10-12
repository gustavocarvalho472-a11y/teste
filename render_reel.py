import numpy as np, os, wave, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 5.0
NF = int(FPS * DUR)
SS = 2  # supersampling
N = 2600
OUT = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(OUT, "frames"); os.makedirs(FR, exist_ok=True)
rng = np.random.default_rng(7)

F = "/usr/share/fonts/opentype/inter/"
def font(name, size): return ImageFont.truetype(F + name, size)
f_cap = font("Inter-SemiBold.otf", 50)
f_ui = font("Inter-Medium.otf", 26)
f_lbl = font("Inter-Bold.otf", 34)

CX, CY = W / 2, 860

# ---------- particle targets (screen space) ----------
def text_targets(txt, size, cy, n=N, grid=14):
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    fnt = font("InterDisplay-Bold.otf", size)
    bb = d.textbbox((0, 0), txt, font=fnt)
    d.text((CX - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), txt, font=fnt, fill=255)
    a = np.array(img)
    ys, xs = np.mgrid[0:H:grid, 0:W:grid]
    m = a[ys, xs] > 128
    pts = np.stack([xs[m], ys[m]], 1).astype(float)
    idx = rng.choice(len(pts), n, replace=len(pts) < n)
    p = pts[idx] + rng.normal(0, 1.2, (n, 2))
    return p, np.full(n, 1.0)

def bars_targets(cy, n=N):
    hs = [140, 230, 330, 450, 590]
    bw, gap, grid = 120, 46, 14
    x0 = CX - (5 * bw + 4 * gap) / 2
    base = cy + 300
    pts = []
    for i, h in enumerate(hs):
        for yy in np.arange(base - h, base, grid):
            for xx in np.arange(x0 + i * (bw + gap), x0 + i * (bw + gap) + bw, grid):
                pts.append((xx, yy))
    pts = np.array(pts, float)
    idx = rng.choice(len(pts), n, replace=len(pts) < n)
    return pts[idx], np.full(n, 1.0)

# sphere (fibonacci), projected each frame
k = np.arange(N) + 0.5
phi = np.arccos(1 - 2 * k / N); th = np.pi * (1 + 5 ** 0.5) * k
S3 = np.stack([np.sin(phi) * np.cos(th), np.cos(phi), np.sin(phi) * np.sin(th)], 1)

def sphere(t, cy=CY, R=360):
    a = t * 0.9
    x = S3[:, 0] * np.cos(a) + S3[:, 2] * np.sin(a)
    z = -S3[:, 0] * np.sin(a) + S3[:, 2] * np.cos(a)
    y = S3[:, 1]
    tilt = 0.35
    y2 = y * np.cos(tilt) - z * np.sin(tilt); z2 = y * np.sin(tilt) + z * np.cos(tilt)
    s = 1.0 + 0.0 * t
    p = np.stack([CX + x * R * s, cy + y2 * R * s], 1)
    depth = (z2 + 1) / 2  # 0 back, 1 front
    return p, 0.35 + 0.85 * depth

T06 = text_targets("06", 640, CY)
TBAR = bars_targets(CY - 40)
T10 = text_targets("10X", 470, CY)

delay = rng.uniform(0, 0.35, N)
burst = rng.normal(0, 1, (N, 2)) * 160

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def ease_io(x): x = np.clip(x, 0, 1); return np.where(x < .5, 4 * x**3, 1 - (-2 * x + 2) ** 3 / 2)

# timeline: (start, end) of each morph
M = [(1.15, 1.85), (2.45, 3.15), (3.55, 4.25)]

def state(t):
    shapes = [sphere(t), T06, TBAR, T10]
    p, s = shapes[0]
    for i, (a, b) in enumerate(M):
        u = (t - a) / (b - a)
        uu = ease_io(np.clip((u - delay) / (1 - 0.35), 0, 1))[:, None]
        q, s2 = shapes[i + 1]
        bump = np.sin(np.pi * uu) * burst
        p = p * (1 - uu) + q * uu + bump
        s = s * (1 - uu[:, 0]) + s2 * uu[:, 0]
    # breathing jitter
    p = p + np.stack([np.sin(t * 3 + k * .7), np.cos(t * 2.6 + k * 1.3)], 1) * 1.5
    return p, s

# ---------- dot terrain floor ----------
gx, gz = np.meshgrid(np.linspace(-1.6, 1.6, 46), np.linspace(0.15, 1.0, 22))
def terrain(d, t):
    hgt = 0.06 * np.sin(gx * 4 + t * 1.8) * np.cos(gz * 7 - t) + 0.04 * np.sin(gx * 9 - t * 2)
    f = 1 / (gz + 0.25)
    X = CX + gx * 520 * f * 0.55
    Y = 1460 + (0.6 - hgt) * 240 * f * 0.55 - 180
    r = 1.2 + 2.0 * (1 - gz)
    al = (40 + 120 * (1 - gz)).astype(int)
    for x, y, rr, a in zip(X.ravel(), Y.ravel(), r.ravel(), al.ravel()):
        d.ellipse([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS], fill=int(a))

# ---------- overlays ----------
CAPS = [(0.0, 1.25, "Michael Jordan ganhou seis títulos."),
        (1.25, 2.55, "Quanto melhor ele ficava,"),
        (2.55, 3.65, "mais alto ficava o padrão."),
        (3.65, 5.01, "Crie 10x mais rápido.\nSeja 10x mais exigente.")]
LBL = [(0.15, 1.2, "MICHAEL JORDAN"), (1.6, 2.5, "TÍTULOS DA NBA"),
       (2.9, 3.6, "A EXIGÊNCIA"), (4.0, 5.01, "EXIGÊNCIA ↑")]
YEARS = ["1991", "1992", "1993", "1996", "1997", "1998"]

def fade(t, a, b, f=0.18):
    return float(np.clip(min((t - a) / f, (b - t) / f), 0, 1))

def overlays(img, t):
    d = ImageDraw.Draw(img)
    # HUD corners
    d.text((70, 90), "Nº 06 — PADRÃO", font=f_ui, fill=170)
    d.text((W - 70, 90), f"00:{t:05.2f}", font=f_ui, fill=170, anchor="ra")
    d.line([(70, 140), (W - 70, 140)], fill=60, width=2)
    # progress ticks
    for i in range(30):
        x = 70 + i * (W - 140) / 29
        on = i / 29 <= t / DUR
        d.line([(x, 1700), (x, 1712 if not on else 1726)], fill=230 if on else 70, width=3)
    # labels
    for a, b, s in LBL:
        al = fade(t, a, b)
        if al > 0:
            # typewriter
            n = int(len(s) * np.clip((t - a) / 0.3, 0, 1))
            d.text((CX, 380 + (1 - al) * 10), s[:n], font=f_lbl, fill=int(255 * al), anchor="mm")
    # level scale for bars
    al = fade(t, 2.9, 3.6)
    if al > 0:
        x0 = CX - (5 * 120 + 4 * 46) / 2
        for i in range(5):
            d.text((x0 + i * 166 + 60, CY - 40 + 345), f"0{i+1}", font=f_ui, fill=int(200 * al), anchor="mm")
    # years under 06
    al = fade(t, 1.75, 2.5)
    if al > 0:
        for i, y in enumerate(YEARS):
            if t > 1.75 + i * 0.07:
                d.text((CX - 375 + i * 150, 1240), y, font=f_ui, fill=int(210 * al), anchor="mm")
    # multiplier counter before 10X
    if 3.2 < t < 3.75:
        v = 1.6 * 2 ** ((t - 3.2) / 0.55 * 7.3)
        d.text((CX, 1240), f"x {v:,.1f}".replace(",", "."), font=f_lbl, fill=220, anchor="mm")
    # caption
    for a, b, s in CAPS:
        al = fade(t, a, b, 0.12)
        if al > 0:
            d.multiline_text((CX, 1560 + (1 - al) * 14), s, font=f_cap, fill=int(255 * al),
                             anchor="mm", align="center", spacing=14)

grain_bank = [rng.normal(0, 7, (H, W)) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
vign = 1 - 0.55 * (((xx - CX) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2.2
vign = np.clip(vign, 0.35, 1)

for fi in range(NF):
    t = fi / FPS
    big = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(big)
    terrain(d, t)
    p, s = state(t)
    order = np.argsort(s)
    for (x, y), sc in zip(p[order], s[order]):
        r = 3.6 * sc
        c = int(np.clip(90 + 165 * sc, 0, 255))
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=c)
    img = big.resize((W, H), Image.LANCZOS)
    glow = img.filter(ImageFilter.GaussianBlur(10))
    a = np.array(img, float) + 0.6 * np.array(glow, float)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    overlays(img, t)
    a = np.array(img, float) * vign + grain_bank[fi % 6]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f"{FR}/f{fi:04d}.png")

# ---------- audio ----------
SR = 44100
ts = np.arange(int(SR * DUR)) / SR
au = np.zeros_like(ts)
beat = 60 / 108
for bt in np.arange(0, DUR, beat / 2):
    m = ts >= bt; tt = ts[m] - bt
    au[m] += 0.22 * np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 9)
for fq in [110, 164.8, 220, 261.6]:
    au += 0.03 * np.sin(2 * np.pi * fq * ts + 0.3 * np.sin(2 * np.pi * 0.4 * ts)) * np.clip(ts / 0.8, 0, 1)
noise = rng.normal(0, 1, len(ts))
def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y
whn = lp(noise, 0.08)
for a, b in M:
    env = np.exp(-((ts - (a + b) / 2) / ((b - a) / 3)) ** 2)
    au += 0.35 * whn * env
for c in [0.15, 1.6, 2.9, 4.0] + [1.75 + i * .07 for i in range(6)]:
    m = (ts >= c) & (ts < c + 0.03)
    au[m] += 0.15 * np.sign(np.sin(2 * np.pi * 2400 * ts[m]))
# swish of the net at 10X landing
sw = noise - lp(noise, 0.3)
env = np.exp(-np.clip(ts - 4.2, 0, None) * 6) * (ts >= 4.2)
au += 0.35 * sw * env
au *= np.clip((DUR - ts) / 0.4, 0, 1)
au = au / np.abs(au).max() * 0.85
with wave.open(os.path.join(OUT, "audio.wav"), "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((au * 32767).astype(np.int16).tobytes())

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/f%04d.png",
                "-i", os.path.join(OUT, "audio.wav"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "17", "-c:a", "aac", "-b:a", "192k", "-shortest",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "reel_particulas_5s.mp4")], check=True)
print("ok")
