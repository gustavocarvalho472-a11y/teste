"""Motor de partículas v2: imagem -> nuvem 3D de pontos finos, câmera em órbita, profundidade de campo, brilho."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

W, H = 1080, 1920
CX, CY = W / 2, H / 2 - 100
FOCAL = 1700.0
CAM_D = 1700.0


def image_cloud(path, spacing=4.2, width=1000, crop=None, invert=False, gamma=1.5, depth=260, subject=None,
                feather=0.12, thresh=0.06, seed=1):
    """Meio-tom: grade regular de pontos sobre a imagem; o tom local define o brilho/tamanho de cada ponto.
    Retorna (P[n,3], I[n]) em pixels de tela, centrado em (0,0,0)."""
    rng = np.random.default_rng(seed)
    im = Image.open(path).convert("L")
    if crop: im = im.crop([int(c * d) for c, d in zip(crop, im.size * 2)])
    gw = int(width / spacing); gh = int(gw * im.size[1] / im.size[0])
    a = np.asarray(im.resize((gw, gh), Image.LANCZOS), np.float32) / 255
    a = np.clip(a + 0.9 * (a - gaussian_filter(a, 6)), 0, 1)                    # realça linhas e volumes
    v = 1 - a if invert else a
    v = np.clip((v - 0.05) / 0.95, 0, 1) ** gamma
    yy, xx = np.mgrid[0:gh, 0:gw]
    u = (xx + 0.5) / gw; w = (yy + 0.5) / gh
    f = np.clip(np.minimum.reduce([u, 1 - u, w, 1 - w]) / feather, 0, 1)        # bordas esfumadas
    f = f * f * (3 - 2 * f)
    v = v * f
    m = v > thresh * (0.6 + 0.8 * rng.random(v.shape))                           # borda irregular
    u, w, v = u[m], w[m], v[m]
    n = len(v)
    height = width * gh / gw
    X = (u - 0.5) * width + rng.normal(0, spacing * 0.12, n)
    Y = (w - 0.5) * height + rng.normal(0, spacing * 0.12, n)
    Z = depth * (0.5 - w)
    if subject is not None:
        sx, sy, sr, sz = subject
        Z -= sz * np.exp(-(((u - sx) / sr) ** 2 + ((w - sy) / (sr * 1.3)) ** 2))
    Z += rng.normal(0, 4, n)
    return np.stack([X, Y, Z], 1).astype(np.float32), v.astype(np.float32)


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
