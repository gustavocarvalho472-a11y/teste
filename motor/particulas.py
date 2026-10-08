"""Motor de partículas v2: imagem -> nuvem 3D de pontos finos, câmera em órbita, profundidade de campo, brilho."""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

WIDE = os.environ.get("MOTOR_FMT") == "16x9"          # vídeo longo: 1920x1080
W, H = (1920, 1080) if WIDE else (1080, 1920)
CX, CY = W / 2, H / 2 - (0 if WIDE else 100)
FOCAL = 1700.0
CAM_D = 1700.0


def cloud_from_array(a, width, spacing=6.0, invert=False, gamma=1.5, depth=260, subject=None, lumdepth=0.0,
                     feather=0.12, thresh=0.06, enhance=0.9, autolevel=False, seed=1):
    """Meio-tom a partir de um array 0..1 (já recortado). Retorna P[n,3], I[n], UV[n,2] (UV em 0..1 do recorte)."""
    rng = np.random.default_rng(seed)
    H0, W0 = a.shape
    gw = int(width / spacing); gh = max(2, int(gw * H0 / W0))
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((gw, gh), Image.LANCZOS), np.float32) / 255
    if autolevel:                                                                  # estica os níveis da imagem
        lo, hi = np.percentile(a, [3, 99.7]); a = np.clip((a - lo) / max(1e-3, hi - lo), 0, 1)
    if enhance: a = np.clip(a + enhance * (a - gaussian_filter(a, 6)), 0, 1)        # realça linhas e volumes
    v = 1 - a if invert else a
    v = np.clip((v - 0.05) / 0.95, 0, 1) ** gamma
    yy, xx = np.mgrid[0:gh, 0:gw]
    u = (xx + 0.5) / gw; w = (yy + 0.5) / gh
    if feather:
        f = np.clip(np.minimum.reduce([u, 1 - u, w, 1 - w]) / feather, 0, 1)        # bordas esfumadas
        v = v * f * f * (3 - 2 * f)
    lum = gaussian_filter(a, 8)
    m = v > thresh * (0.6 + 0.8 * rng.random(v.shape))                           # borda irregular
    u, w, v, lum = u[m], w[m], v[m], lum[m]
    n = len(v)
    height = width * gh / gw
    X = (u - 0.5) * width + rng.normal(0, spacing * 0.12, n)
    Y = (w - 0.5) * height + rng.normal(0, spacing * 0.12, n)
    Z = depth * (0.5 - w) - lumdepth * (lum - 0.3)                                 # claro = mais perto
    if subject is not None:
        sx, sy, sr, sz = subject
        Z -= sz * np.exp(-(((u - sx) / sr) ** 2 + ((w - sy) / (sr * 1.3)) ** 2))
    Z += rng.normal(0, 4, n)
    return (np.stack([X, Y, Z], 1).astype(np.float32), v.astype(np.float32),
            np.stack([u, w], 1).astype(np.float32))


def image_cloud(path, spacing=4.2, width=1000, crop=None, **kw):
    """Abre a imagem (com recorte opcional em frações x0,y0,x1,y1) e devolve (P, I)."""
    im = Image.open(path).convert("L")
    if crop: im = im.crop([int(c * d) for c, d in zip(crop, im.size * 2)])
    P, I, _ = cloud_from_array(np.asarray(im, np.float32) / 255, width, spacing=spacing, **kw)
    return P, I


def resample(P, I, UV, n, seed=0):
    """Fixa a quantidade de pontos em n (para transformar uma cena em outra ponto a ponto)."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(I), n, replace=len(I) < n)
    jit = np.zeros((n, 3), np.float32)
    if len(I) < n: jit[:, :2] = rng.normal(0, 1.2, (n, 2))
    return P[idx] + jit, I[idx], UV[idx]


def project(P, yaw=0.0, pitch=0.0, dolly=0.0, pan=(0, 0)):
    """Câmera orbitando em torno da origem. Retorna x, y de tela, profundidade z e escala."""
    cy, sy, cp, sp = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    X = P[:, 0] * cy + P[:, 2] * sy; Z = -P[:, 0] * sy + P[:, 2] * cy
    Y = P[:, 1] * cp - Z * sp; Z = P[:, 1] * sp + Z * cp
    d = CAM_D - dolly + Z
    d = np.maximum(d, 50)
    s = FOCAL / d
    return CX + (X + pan[0]) * s, CY + (Y + pan[1]) * s, Z, s


def splat(x, y, wgt, buf):
    """Acumula pontos com interpolação bilinear (subpixel) num buffer HxW."""
    m = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
    x, y, wgt = x[m], y[m], wgt[m]
    x0 = x.astype(np.int32); y0 = y.astype(np.int32); fx = x - x0; fy = y - y0
    flat = buf.ravel()
    for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        flat += np.bincount((y0 + dy) * W + x0 + dx, wgt * ww, minlength=W * H)[: W * H]


def render(x, y, z, s, inten, focus_z=0.0, dof=0.010, dot=1.0, gain=1.0, glow=0.45):
    """Pontos nítidos no plano de foco e desfocados longe dele; pontos de tom alto ficam maiores (meio-tom)."""
    coc = np.minimum(np.abs(z - focus_z) * dof, 4.0)
    out = np.zeros((H, W), np.float32)
    cls_id = np.digitize(inten, [0.25, 0.5, 0.75])
    for lo, hi, sig in ((0, 1.0, 0.0), (1.0, 2.5, 1.8), (2.5, 1e9, 4.0)):
        for c, size in enumerate((0.55, 0.8, 1.1, 1.45)):
            m = (coc >= lo) & (coc < hi) & (cls_id == c)
            if not m.any(): continue
            buf = np.zeros((H, W), np.float32)
            splat(x[m], y[m], inten[m] ** 0.7 * s[m] ** 2, buf)
            k = np.hypot(dot * size * s[m].mean(), sig)
            buf = gaussian_filter(buf, k) * (2 * np.pi * k * k) ** 0.75
            out += buf
    out *= gain * 230
    out = 255 * (1 - np.exp(-out / 255))                                          # compressão suave
    if glow: out += glow * gaussian_filter(out, 14)
    return out


def finish(a, t, grain=6.0, vignette=0.55, seed=0):
    yy, xx = np.mgrid[0:H, 0:W]
    v = np.clip(1 - vignette * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2.2, 0.3, 1)
    g = np.random.default_rng(int(t * 1000) + seed).normal(0, grain, (H, W))
    return np.clip(a * v + g, 0, 255).astype(np.uint8)
