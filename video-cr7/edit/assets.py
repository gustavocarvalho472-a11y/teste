"""Fábrica de assets do dossiê: fotos viram provas impressas (cor, borda de papel, sombra), carimbos com
textura de tinta, textura do quadro e do papel. Tudo vai para cache/ (PNG com alfa).

    python3 assets.py            # gera o que falta
    python3 assets.py --force    # refaz tudo
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "clipes", "imagens")
CACHE = os.path.join(HERE, "cache")
FONTS = os.path.expanduser("~/.fonts/dossie")
os.makedirs(CACHE, exist_ok=True)
FORCE = "--force" in sys.argv
rng = np.random.default_rng(7)

# nome: (arquivo, recorte (x0,y0,x1,y1) ou None, largura salva, gradação, borda(px na largura salva) ou 0)
PRINTS = {
    # gancho: o meme
    "mA": ("g1_cr7_jesus_coletiva_16", None, 1024, "news", 20),
    "mB": ("tb_final_02", (0, 40, 2560, 1380), 1600, "show", 30),
    # o "mural da internet"
    "w_arg": ("a3_dublin_24", None, 900, "news", 18),
    "w_point": ("q_suspensao_04", None, 945, "news", 18),
    "w_room": ("tb_s3promo_02", (0, 120, 2560, 1560), 2200, "show", 36),
    "w_poster": ("tb_homelander_04", None, 1400, "show", 24),
    "w_piers": ("a1_piers_12", None, 1000, "news", 18),
    "w_hero": ("tb_homelander_02", None, 1080, "show", 20),
    # tela cheia
    "p_fly": ("tb_final_01", None, 1000, "show", 0),
    "p_laser": ("tb_laser_00", None, 1413, "show", 0),
    "p_control": ("tb_ep308_00", (0, 120, 2560, 1560), 2200, "show", 0),
    "p_trophy": ("g5_retiro_00", None, 1600, "warm", 0),
    # brigas
    "f_grim": ("g1_cr7_jesus_coletiva_40", (220, 0, 1630, 900), 1440, "news", 24),
    "f_tenhag": ("a1_tenhag_13", None, 1200, "news", 20),
    "f_jesus": ("g1_cr7_jesus_coletiva_28", (0, 0, 1920, 1280), 1200, "news", 20),
    "f_club": ("a2_greve_31", (300, 0, 4644, 2781), 1400, "news", 22),
    "f_exec": ("g1_cr7_jesus_coletiva_45", None, 650, "news", 12),
    # despedida / saída
    "ph_post": ("g5_retiro_18", (150, 0, 587, 546), 437, "news", 0),
    "k_bus": ("a5_copenhague_33", None, 1200, "news", 20),
    "k_jesus": ("g1_cr7_jesus_coletiva_38", None, 1200, "news", 20),
    "k_memory": ("a5_gales_jesus_26", None, 1000, "sepia", 26),
    "r_bg": ("a5_comunicado_00", None, 1080, "dark", 0),
    "gb_cry": ("g5_retiro_18", None, 728, "news", 16),
    # parte 2: Homelander
    "s_adored": ("tb_grisalho_00", (0, 0, 1080, 1190), 1080, "show", 0),
    "p_fly2": ("tb_homelander_02", None, 1080, "show", 0),
    "w_bench": ("a5_noruega_02", None, 900, "news", 18),
    "w_dub": ("a3_dublin_12", None, 900, "news", 18),
    "s_share": ("tb_starlight_cocapita_01", None, 1600, "show", 26),
    "s_lost": ("tb_stormfront_03", (0, 0, 2300, 1066), 1800, "show", 0),
    "s_bench": ("a5_noruega_02", None, 1440, "news", 22),
    "s_tunnel": ("a1_tunel_00", (0, 0, 1000, 673), 1110, "news", 18),
    "s_dublin": ("a3_dublin_12", None, 1200, "news", 20),
    "s_billboard": ("tb_homelander_04", None, 960, "show", 0),
}


def grade(im, kind):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    l = a @ np.array([0.299, 0.587, 0.114], np.float32)
    P = {  # contraste, saturação, sombras frias, luzes quentes, levantar pretos, brilho
        "news": (1.10, 0.80, 0.045, 0.030, 0.035, 1.00),
        "show": (1.06, 0.88, 0.035, 0.020, 0.025, 1.00),
        "warm": (1.08, 0.92, 0.020, 0.060, 0.030, 1.02),
        "dark": (1.05, 0.55, 0.050, 0.000, 0.000, 0.55),
        "sepia": (1.02, 0.15, 0.000, 0.000, 0.060, 1.00),
    }[kind]
    con, sat, teal, warm, lift, gain = P
    a = 0.5 + (a - 0.5) * con
    l = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = l[..., None] + (a - l[..., None]) * sat
    sh = np.clip(1 - l, 0, 1)[..., None] ** 2
    hi = np.clip(l, 0, 1)[..., None] ** 2
    a = a + sh * np.array([-teal * 0.5, teal * 0.25, teal], np.float32)
    a = a + hi * np.array([warm, warm * 0.45, -warm * 0.8], np.float32)
    if kind == "sepia":
        a = a * np.array([1.06, 0.96, 0.80], np.float32)
    a = lift + a * (1 - lift)
    a = np.clip(a * gain, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def paper_border(w, h, b):
    """Papel fotográfico off-white levemente irregular, com bordas mais escuras."""
    base = np.ones((h, w, 3), np.float32) * np.array([0.93, 0.915, 0.885], np.float32)
    n = gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), 1.2) * 0.018
    base += n[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    edge = np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy])
    base *= (0.86 + 0.14 * np.clip(edge / max(6, b * 0.6), 0, 1))[..., None]
    return base


def make_print(name, src, crop, out_w, kind, border):
    p_png = os.path.join(CACHE, f"{name}.png")
    if os.path.exists(p_png) and not FORCE:
        return
    im = Image.open(os.path.join(IMG, src + ".jpg")).convert("RGB")
    if crop:
        im = im.crop(crop)
    if im.width != out_w:
        im = im.resize((out_w, round(im.height * out_w / im.width)), Image.LANCZOS)
    im = grade(im, kind)
    if border:
        w, h = im.width + 2 * border, im.height + 2 * border
        pap = paper_border(w, h, border)
        ph = np.asarray(im).astype(np.float32) / 255
        # sombra interna fininha: a foto parece impressa no papel, não colada
        pap[border:border + im.height, border:border + im.width] = ph
        k = 3
        pap[border - k:border, border - k:border + im.width + k] *= 0.92
        pap[border + im.height:border + im.height + k, border - k:border + im.width + k] *= 0.96
        arr = np.clip(pap * 255, 0, 255).astype(np.uint8)
        out = Image.fromarray(arr).convert("RGBA")
    else:
        out = im.convert("RGBA")
    out.save(p_png)
    # sombra suave (só alfa), com margem
    pad = int(out.width * 0.06)
    sh = Image.new("L", (out.width + 2 * pad, out.height + 2 * pad), 0)
    ImageDraw.Draw(sh).rectangle([pad, pad, pad + out.width, pad + out.height], fill=255)
    sh = sh.filter(ImageFilter.GaussianBlur(pad / 2.2))
    shadow = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    shadow.putalpha(sh)
    shadow.save(os.path.join(CACHE, f"{name}_sh.png"))
    return out.size


def ink_mask(w, h, seed, rough=0.5):
    r = np.random.default_rng(seed)
    n = gaussian_filter(r.standard_normal((h, w)).astype(np.float32), 2.0)
    n2 = gaussian_filter(r.standard_normal((h, w)).astype(np.float32), 9.0) * 1.5
    v = n + n2
    v = (v - v.mean()) / (v.std() + 1e-6)
    holes = (v < -1.15 - (1 - rough)).astype(np.float32)
    specks = (r.random((h, w)) < 0.004).astype(np.float32)
    specks = gaussian_filter(specks, 1.0) > 0.05
    m = 1 - np.clip(holes + specks * 0.8, 0, 1)
    m *= 0.88 + 0.12 * np.clip(gaussian_filter(r.random((h, w)).astype(np.float32), 3), 0, 1)
    return m


def make_stamp(name, text, font="Anton-Regular.ttf", size=220, color=(214, 38, 30), border=True, sub=None, seed=1):
    p = os.path.join(CACHE, f"st_{name}.png")
    if os.path.exists(p) and not FORCE:
        return
    f = ImageFont.truetype(os.path.join(FONTS, font), size)
    fs = ImageFont.truetype(os.path.join(FONTS, "BebasNeue-Regular.ttf"), int(size * 0.28)) if sub else None
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    sw = 0
    if sub:
        sbb = fs.getbbox(sub)
        sw, shh = sbb[2] - sbb[0], sbb[3] - sbb[1]
    padx, pady = int(size * 0.32), int(size * 0.22)
    w = max(tw, sw) + 2 * padx
    h = th + 2 * pady + (int(size * 0.36) if sub else 0)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    if border:
        lw = max(6, size // 18)
        d.rounded_rectangle([lw, lw, w - lw, h - lw], radius=size // 10, outline=255, width=lw)
        d.rounded_rectangle([lw * 3, lw * 3, w - lw * 3, h - lw * 3], radius=size // 14, outline=255, width=max(2, lw // 3))
    d.text(((w - tw) / 2 - bb[0], pady - bb[1] + int(size * 0.02)), text, font=f, fill=255)
    if sub:
        d.text(((w - sw) / 2 - sbb[0], pady + th + int(size * 0.1) - sbb[1]), sub, font=fs, fill=255)
    a = np.asarray(im).astype(np.float32) / 255
    a = gaussian_filter(a, 0.7)
    a *= ink_mask(w, h, seed)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = color
    rgba[..., 3] = np.clip(a * 235, 0, 255).astype(np.uint8)
    Image.fromarray(rgba).save(p)


def tileable_noise(n, sigma, seed):
    r = np.random.default_rng(seed)
    return gaussian_filter(r.standard_normal((n, n)).astype(np.float32), sigma, mode="wrap")


def make_board():
    p = os.path.join(CACHE, "board.png")
    if os.path.exists(p) and not FORCE:
        return
    n = 1024
    base = np.array([0.067, 0.086, 0.106], np.float32)  # #11161B
    big = tileable_noise(n, 60, 1)
    big /= big.std()
    mid = tileable_noise(n, 6, 2)
    mid /= mid.std()
    fine = tileable_noise(n, 0.7, 3)
    fine /= fine.std()
    v = 1 + big * 0.07 + mid * 0.035 + fine * 0.03
    img = np.clip(base[None, None, :] * v[..., None], 0, 1)
    Image.fromarray((img * 255).astype(np.uint8)).save(p)


def make_paper():
    p = os.path.join(CACHE, "paper.png")
    if os.path.exists(p) and not FORCE:
        return
    n = 1024
    base = np.array([0.925, 0.905, 0.862], np.float32)
    fib = tileable_noise(n, 1.0, 4)
    fib /= fib.std()
    blot = tileable_noise(n, 40, 5)
    blot /= blot.std()
    v = 1 + fib * 0.012 + blot * 0.02
    img = np.clip(base[None, None, :] * v[..., None], 0, 1)
    Image.fromarray((img * 255).astype(np.uint8)).save(p)


def make_manila():
    p = os.path.join(CACHE, "manila.png")
    if os.path.exists(p) and not FORCE:
        return
    n = 1024
    base = np.array([0.66, 0.56, 0.40], np.float32)
    fib = tileable_noise(n, 0.9, 6)
    fib /= fib.std()
    blot = tileable_noise(n, 50, 7)
    blot /= blot.std()
    v = 1 + fib * 0.02 + blot * 0.04
    img = np.clip(base[None, None, :] * v[..., None], 0, 1)
    Image.fromarray((img * 255).astype(np.uint8)).save(p)


def main():
    meta = {}
    for name, (src, crop, w, kind, b) in PRINTS.items():
        make_print(name, src, crop, w, kind, b)
        im = Image.open(os.path.join(CACHE, f"{name}.png"))
        meta[name] = {"w": im.width, "h": im.height, "border": b}
    make_stamp("no", "NO.", size=360, seed=3)
    make_stamp("retired", "RETIRED", size=200, sub="05 · 11 · 2026", seed=4)
    make_stamp("atwar", "AT WAR", size=170, seed=5)
    make_stamp("case", "CASE 07", size=150, seed=6)
    make_stamp("classified", "HOMELANDO", size=170, seed=8, sub="CASE FILE · SUBJECT A")
    make_board()
    make_paper()
    make_manila()
    for f in os.listdir(CACHE):
        if f.startswith("st_"):
            im = Image.open(os.path.join(CACHE, f))
            meta[f[:-4]] = {"w": im.width, "h": im.height}
    json.dump(meta, open(os.path.join(CACHE, "meta.json"), "w"), indent=1)
    print("assets:", len(meta))


if __name__ == "__main__":
    main()
