"""Monta o vídeo 1920×1080 30 fps a partir de build/timing.json, assets/ e build/mix.wav.

    python3 montar.py                      # render completo → saida/mbappe_china.mp4 + capitulos.txt
    python3 montar.py --quadros 5 12 40    # grade de quadros soltos em build/quadros.png (checagem rápida)
    python3 montar.py --so-audio           # só refaz o áudio/mux (depois de mexer em trilha.py)
    python3 montar.py --assets             # lista o que já existe e o que ainda é placeholder

Asset ausente vira placeholder com o id e a descrição. Basta salvar o arquivo real em assets/<pasta>/ com o
id no começo do nome (ex.: assets/memes/MEME_01_mao_tunica_azul.png) e rodar de novo.
"""
import glob
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

import timeline
from roteiro import B

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = timeline.BUILD
W, H, FPS = 1920, 1080, 30
FONT = os.path.join(HERE, "fonts")
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
YEL, RED, WHITE, BLACK = (255, 214, 0), (226, 30, 38), (255, 255, 255), (0, 0, 0)

FOLDERS = {"MEME": "memes", "PRT": "prints", "FOT": "fotos", "CLP": "clips", "LOG": "logos", "IA": "ia"}
DESC = {
    "MEME_01": "Rosto do Mbappé no corpo de Mao, túnica azul, fundo vermelho com estrelas",
    "MEME_02": "Mesma ideia, túnica cinza/marrom", "MEME_03": "Meme 'Mbappé ditador' (general)",
    "MEME_04": "Meme 'Mbappé ditador' (imperador)", "MEME_05": "Meme 'Mbappé ditador' (líder histórico)",
    "MEME_06": "Meme 'Mbappé ditador' (outro)",
    "CLP_01": "Mbappé no The Bridge, camisa xadrez, legenda francesa da pergunta",
    "FOT_01": "Retrato de Mao na Praça da Paz Celestial", "FOT_02": "Nota de 100 yuans",
    "FOT_03": "Mbappé sério em coletiva", "FOT_04": "Chineses segurando retrato de Mao",
    "FOT_05": "Mao proclamando a República, 1949", "FOT_06": "Garrafas de água com o rosto do Mbappé",
    "FOT_07": "Anúncio da água com Mbappé", "FOT_08": "Mbappé com a camisa 10 do Real",
    "FOT_09": "Javier Tebas", "FOT_10": "Mbappé no The Bridge (recorte do print do Madrid Zone)",
    "PRT_16": "Tweet @theMadridZone com a frase, visto pela interface chinesa do X",
    "PRT_01": "Tweet @MadridZone 'China State TV SUSPENDS La Liga coverage'",
    "PRT_02": "Conta do Mbappé no Weibo com aviso de silenciada",
    "PRT_03": "Tweet Polymarket Español 'SERÁ REMOVIDO DE JOGOS'",
    "PRT_04": "Tweet @KalshiFC 'China CONFIRMS it will not broadcast La Liga'",
    "PRT_05": "Tweet do Tebas com o embaixador", "PRT_06": "Post de desculpas do Mbappé em 3 línguas",
    "PRT_07": "Tweet 'China Media Group RESPONDE ÀS DESCULPAS'", "PRT_08": "Matéria da TIME citando 'Guigui'",
    "PRT_09": "Manchete CNBC: patrocinadores cortam laços", "PRT_10": "Tweet Kalshi 'On's stock has DROPPED'",
    "PRT_11": "Tweet Kalshi 'Real Madrid could suffer ECONOMIC LOSSES'",
    "PRT_12": "Tweet Kalshi 'Javier Tebas APOLOGIZES'", "PRT_13": "Post do House Select Committee on the CCP",
    "PRT_14": "Manchete 2019: Özil / Arsenal fora da CCTV", "PRT_15": "Manchete 2019: NBA fora da TV chinesa",
    "LOG_01": "Dongpeng", "LOG_02": "Mengniu", "LOG_03": "Milkground", "LOG_04": "La Liga",
    "IA_01": "Sala de controle de TV, telas apagando", "IA_02": "Multidão em silhueta com bandeiras vermelhas",
    "IA_03": "Vestiário vazio, cadeira sob holofote", "IA_04": "Contrato rasgando no ar",
    "IA_05": "Celular com feed chinês e notificações", "IA_06": "Card de jogador vazio com cadeado",
    "IA_07": "Gráfico de ações despencando", "IA_08": "Arara de camisas brancas nº 10",
    "IA_09": "Mesa de assinatura, skyline de Pequim", "IA_10": "Cofre vazio com selo vermelho",
    "IA_11": "Bandeiras EUA × China, silhueta no meio", "IA_12": "TV de tubo desligando",
}


def font(name, size):
    if name == "cjk":
        return ImageFont.truetype(CJK, size)
    f = ImageFont.truetype(os.path.join(FONT, {"anton": "Anton-Regular.ttf", "bebas": "BebasNeue-Regular.ttf",
                                               "inter": "Inter.ttf", "interb": "Inter.ttf"}[name]), size)
    if name == "interb":
        f.set_variation_by_axes([size if size < 32 else 32, 800])
    return f


_F = {}


def F(name, size):
    if (name, size) not in _F:
        _F[name, size] = font(name, size)
    return _F[name, size]


# ── assets ──────────────────────────────────────────────────────────────────────────────────────────
def find(aid):
    folder = FOLDERS.get(aid.split("_")[0])
    if not folder:
        return None
    hits = sorted(glob.glob(os.path.join(HERE, "assets", folder, aid + "_*")),
                  key=lambda h: ("_manchete_" in h, h))       # tweet/link original antes da manchete provisória
    hits = [h for h in hits if os.path.splitext(h)[1].lower() in
            (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".mkv", ".webm")]
    return hits[0] if hits else None


def is_video(p):
    return p and os.path.splitext(p)[1].lower() in (".mp4", ".mov", ".mkv", ".webm")


def stripes(w, h, c1, c2):
    im = Image.new("RGB", (w, h), c1)
    d = ImageDraw.Draw(im)
    for x in range(-h, w, 60):
        d.line([(x, h), (x + h, 0)], fill=c2, width=18)
    return im


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + ([cur] if cur else [])


def placeholder(aid):
    kind = aid.split("_")[0]
    desc = DESC.get(aid, "")
    if kind == "PRT":
        w, h = 1300, 560
        im = Image.new("RGB", (w, h), (245, 245, 240))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w, 70], fill=(30, 30, 30))
        d.text((30, 14), f"{aid}  ·  PRINT (placeholder)", font=F("interb", 34), fill=YEL)
        y = 120
        for ln in wrap(d, desc, F("interb", 52), w - 80):
            d.text((40, y), ln, font=F("interb", 52), fill=(20, 20, 20))
            y += 66
        d.text((40, h - 60), f"salvar em assets/prints/{aid}_*.png", font=F("inter", 28), fill=(120, 120, 120))
        return im
    if kind == "LOG":
        im = Image.new("RGB", (520, 280), (240, 240, 240))
        d = ImageDraw.Draw(im)
        d.rectangle([4, 4, 515, 275], outline=(60, 60, 60), width=6)
        d.text((260, 120), desc.upper(), font=F("anton", 72), fill=(30, 30, 30), anchor="mm")
        d.text((260, 230), aid, font=F("inter", 26), fill=(120, 120, 120), anchor="mm")
        return im
    col = {"MEME": ((90, 10, 12), (110, 18, 20)), "FOT": ((28, 28, 32), (36, 36, 42)),
           "IA": ((40, 6, 8), (55, 10, 12)), "CLP": ((20, 24, 34), (28, 32, 46))}.get(kind, ((30, 30, 30),) * 2)
    im = stripes(W, H, *col)
    d = ImageDraw.Draw(im)
    d.text((W / 2, 400), aid, font=F("anton", 170), fill=(255, 255, 255), anchor="mm",
           stroke_width=6, stroke_fill=BLACK)
    y = 540
    for ln in wrap(d, desc, F("interb", 50), 1400):
        d.text((W / 2, y), ln, font=F("interb", 50), fill=(235, 235, 235), anchor="mm")
        y += 64
    d.text((W / 2, 780), f"PLACEHOLDER · salvar em assets/{FOLDERS[kind]}/{aid}_*", font=F("inter", 32),
           fill=(200, 200, 200), anchor="mm")
    return im


_IMG = {}


def still(aid, frac=0.1):
    """Imagem do asset (ou quadro de um vídeo, ou placeholder)."""
    key = (aid, frac)
    if key in _IMG:
        return _IMG[key]
    p = find(aid)
    if p is None:
        im = placeholder(aid)
    elif is_video(p):
        os.makedirs(os.path.join(BUILD, "cache"), exist_ok=True)
        out = os.path.join(BUILD, "cache", f"{aid}_{frac:.2f}.png")
        if not os.path.exists(out):
            dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                 "-of", "csv=p=0", p]).decode())
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(dur * frac), "-i", p, "-frames:v", "1", out],
                           check=True)
        im = Image.open(out).convert("RGB")
        if im.width < im.height:                     # vídeo vertical: centraliza sobre fundo desfocado
            im = fit_blur(im)
    else:
        im = Image.open(p).convert("RGBA")
        if aid.startswith(("PRT", "LOG")):
            bg = Image.new("RGB", im.size, (255, 255, 255) if aid.startswith("LOG") else (20, 20, 20))
            bg.paste(im, mask=im.split()[3])
            im = bg
        else:
            im = im.convert("RGB")
            if im.width / im.height < 1.4:              # quadrada/vertical: inteira sobre fundo desfocado
                im = fit_blur(im)
    _IMG[key] = im
    return im


def fit_blur(im):
    bg = cover(im).filter(ImageFilter.GaussianBlur(40)).point(lambda v: v * 0.6)
    fg = im.resize((int(im.width * H / im.height), H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, 0))
    return bg


class Clip:
    """Lê quadros de um vídeo em sequência (um processo ffmpeg por trecho contínuo)."""
    def __init__(self):
        self.p, self.key, self.next_t = None, None, None

    def frame(self, path, t):
        dt = 1 / FPS
        if self.key != path or self.next_t is None or abs(t - self.next_t) > dt * 0.5:
            if self.p:
                self.p.kill()
            self.p = subprocess.Popen(
                ["ffmpeg", "-v", "quiet", "-ss", f"{t:.3f}", "-stream_loop", "-1", "-i", path, "-filter_complex",
                 # vídeo vertical (repost de rede social): centralizado sobre o próprio quadro desfocado
                 f"[0:v]fps={FPS},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"boxblur=30:2,eq=brightness=-0.25[bg];[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
                 f"[bg][fg]overlay=(W-w)/2:(H-h)/2",
                 "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
            self.key = path
        buf = self.p.stdout.read(W * H * 3)
        self.next_t = t + dt
        if len(buf) < W * H * 3:
            return Image.new("RGB", (W, H))
        return Image.frombuffer("RGB", (W, H), buf)


CLIP = Clip()


# ── tratamentos ─────────────────────────────────────────────────────────────────────────────────────
def ease(x):
    x = min(1, max(0, x))
    return 1 - (1 - x) ** 3


def cover(im, scale=1.0, fx=0.5, fy=0.5, size=(W, H)):
    w, h = size
    s = max(w / im.width, h / im.height) * scale
    cw, ch = w / s, h / s
    x0 = (im.width - cw) * fx
    y0 = (im.height - ch) * fy
    return im.resize(size, Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def kenburns(im, u, sub, kb=None):
    """u = progresso 0..1 no shot; sub alterna o enquadramento a cada sub-corte."""
    mode = kb or ["in", "pan", "out"][sub % 3]
    if mode == "in":
        return cover(im, 1.0 + 0.08 * u)
    if mode == "out":
        return cover(im, 1.08 - 0.08 * u)
    if mode == "pan":
        return cover(im, 1.12, 0.2 + 0.6 * u, 0.5)
    return cover(im)


def grade_red(im):
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.3, 0.59, 0.11], np.float32)
    out = np.stack([lum * 1.15 + a[..., 0] * 0.15, lum * 0.55, lum * 0.5], -1)
    out = (out - 128) * 1.15 + 118
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def bw(im):
    return ImageOps.grayscale(im).convert("RGB")


_TEX = None


def texture():
    global _TEX
    if _TEX is None:
        r = np.random.default_rng(3)
        n = r.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
        n = np.asarray(Image.fromarray(((n + 3) * 40).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                       np.float32)
        base = 18 + (n - 120) * 0.08
        g = np.linspace(1.15, 0.8, H)[:, None]
        _TEX = Image.fromarray(np.stack([base * g * 1.1, base * g, base * g * 0.95], -1).clip(0, 255).astype(np.uint8))
    return _TEX.copy()


def shadow_paste(canvas, im, cx, cy, angle=0.0):
    im = im.convert("RGBA")
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 170), (40, 50, 40 + im.width, 50 + im.height), mask=im.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    canvas.paste(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2 + 10)), sh)
    canvas.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


def print_shot(aid, tl, sub, shot):
    c = texture()
    im = still(aid)
    s = min(W * 0.70 / im.width, H * (0.84 if im.height > im.width else 0.70) / im.height)   # tweet alto: usa a altura
    s *= 0.92 + 0.08 * ease(tl / 0.25) if not sub else 1.0
    s *= 1 + 0.03 * (tl / 4)                                  # deriva lenta
    pim = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    ang = (1.5 if (shot["blk"] + sub) % 2 else -1.5)
    shadow_paste(c, pim, W / 2, H / 2 - 40, ang)
    return c


def meme_shot(aid, tl, u, sub, opts):
    im = still(aid)
    if opts.get("small"):
        c = Image.new("RGB", (W, H), (150, 10, 14))
        sm = cover(im, 1.0, size=(760, 428))
        k = 0.9 + 0.1 * ease(tl / 0.4)
        sm = sm.resize((int(760 * k), int(428 * k)))
        shadow_paste(c, sm, W / 2, H / 2 - 40)
        return c
    if opts.get("kb") == "shrink":
        c = Image.new("RGB", (W, H), (6, 6, 6))
        k = 1.0 - 0.62 * ease(u)
        sm = cover(im, 1.0).resize((max(2, int(W * k)), max(2, int(H * k))))
        shadow_paste(c, sm, W / 2, H / 2 - 30 * ease(u))
        return c
    punch = 1.0 + 0.15 * ease(tl / 0.3) if not sub and not opts.get("kb") else 1.15
    fr = cover(im, punch + 0.04 * u)
    if opts.get("dark"):
        fr = Image.blend(fr, Image.new("RGB", (W, H)), 0.15 + 0.45 * u)
    return fr


def logos_shot(ids, tl, falls, fall):
    c = texture()
    n = len(ids)
    for k, aid in enumerate(ids):
        im = still(aid)
        s = min(460 / im.width, 260 / im.height)
        li = im.resize((int(im.width * s), int(im.height * s)))
        cx = W / 2 + (k - (n - 1) / 2) * 560
        appear = ease((tl - 0.25 * k) / 0.3)
        if appear <= 0:
            continue
        cy, ang = H / 2 - 60 + (1 - appear) * 80, 0
        if fall:
            tf = falls[k]                                          # mesmos tempos dos rasgos (timeline.events)
            if tl > tf:
                x = tl - tf
                cy += 2200 * x * x
                ang = -25 * x * (1 if k % 2 else -1)
                li = bw(li)
        shadow_paste(c, li, cx, cy, ang)
    return c


def crack_shot(aid, tl, d):
    c = Image.new("RGB", (W, H), (10, 10, 10))
    im = bw(still(aid))
    s = min(700 / im.width, 520 / im.height)
    shadow_paste(c, im.resize((int(im.width * s), int(im.height * s))), W / 2, H / 2 - 40)
    p = ease((tl - 0.4) / 1.2)
    if p > 0:
        dr = ImageDraw.Draw(c)
        r = np.random.default_rng(11)
        for k in range(7):
            x, y = W / 2 + r.uniform(-30, 30), H / 2 - 40 + r.uniform(-30, 30)
            a = k * 2 * math.pi / 7 + r.uniform(-0.3, 0.3)
            pts = [(x, y)]
            for j in range(int(9 * p)):
                a += r.uniform(-0.5, 0.5)
                x += math.cos(a) * 55
                y += math.sin(a) * 55
                pts.append((x, y))
            if len(pts) > 1:
                dr.line(pts, fill=(255, 255, 255), width=4)
                dr.line(pts, fill=(0, 0, 0), width=1)
    return c


# ── GFX ─────────────────────────────────────────────────────────────────────────────────────────────
def bg_red():
    a = np.asarray(texture(), np.float32)
    a[..., 0] = a[..., 0] * 2.2 + 40
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def txt(d, xy, s, f, fill=WHITE, stroke=6, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=BLACK)


def gfx(name, tl, u, d):
    c = bg_red() if name not in ("endscreen", "title") else texture()
    dr = ImageDraw.Draw(c)
    if name == "linha_tempo":
        x0, x1, y = 260, 1660, 520
        p = ease(tl / 2.2)
        dr.line([(x0, y), (x1, y)], fill=(90, 30, 30), width=10)
        dr.line([(x0, y), (x0 + (x1 - x0) * p, y)], fill=YEL, width=14)
        for k, (yr, lab) in enumerate([(1949, "REPÚBLICA POPULAR"), (1966, "REVOLUÇÃO CULTURAL"), (1976, "MORTE DE MAO")]):
            x = x0 + (x1 - x0) * (yr - 1949) / 27
            if p * 27 + 1949 >= yr - 0.01:
                dr.ellipse([x - 22, y - 22, x + 22, y + 22], fill=YEL, outline=BLACK, width=4)
                txt(dr, (x, y - 90), str(yr), F("anton", 96))
                txt(dr, (x, y + 75), lab, F("bebas", 54), stroke=4)
        txt(dr, (W / 2, 220), "27 ANOS NO PODER", F("anton", 110), fill=YEL)
    elif name == "contadores":
        for k, lab in enumerate(["WEIBO", "XIAOHONGSHU"]):
            x = W / 2 + (k - 0.5) * 760
            v = int(1_000_000 * ease((tl - 0.3 - 1.4 * k) / 1.6))
            txt(dr, (x, 330), lab, F("anton", 90))
            txt(dr, (x, 520), "~" + f"{v:,}".replace(",", "."), F("anton", 150), fill=YEL)
            txt(dr, (x, 650), "SEGUIDORES", F("bebas", 60), stroke=4)
    elif name == "valor_migu":
        k = 0.7 + 0.3 * ease(tl / 0.4)
        txt(dr, (W / 2, 260), "MIGU · CHINA MOBILE · ATÉ 2030", F("bebas", 70), stroke=4)
        txt(dr, (W / 2, 500), "US$ 400–465 MI", F("anton", int(230 * k)), fill=YEL, stroke=10)
        txt(dr, (W / 2, 690), "VALOR NÃO DIVULGADO · ESTIMATIVA DE MERCADO", F("bebas", 52), stroke=3)
    elif name == "pizza":
        cx, cy, r = W / 2 - 330, H / 2 - 40, 280
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 20, 22), outline=BLACK, width=6)
        p = ease(tl / 1.0)
        dr.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * 0.10 * p, fill=RED, outline=BLACK, width=4)
        dr.pieslice([cx - r, cy - r, cx + r, cy + r], -90 + 36 * p, -90 + 54 * p, fill=(255, 120, 120),
                    outline=BLACK, width=4)
        dr.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=(40, 12, 14))
        txt(dr, (W / 2 + 330, cy - 70), "10–15%", F("anton", 200), fill=YEL, stroke=8)
        txt(dr, (W / 2 + 330, cy + 90), "DO MERCHANDISING", F("bebas", 66), stroke=4)
        txt(dr, (W / 2 + 330, cy + 150), "INTERNACIONAL VEM DA CHINA", F("bebas", 66), stroke=4)
    elif name == "mito":
        txt(dr, (W / 2, 380), "“LA LIGA PERDEU", F("anton", 120))
        txt(dr, (W / 2, 520), "900 MILHÕES SÓ NA CHINA”", F("anton", 120))
        if tl > 1.2:
            dr.text((W / 2, 760), "€900 mi = direitos internacionais no MUNDO TODO", font=F("interb", 46),
                    fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=BLACK)
            stamp(c, "MITO", (W / 2, 450), tl - 1.2, size=260)
    elif name == "nao_perdoado":
        s = "不接受，不原谅"
        n = min(len(s), int(tl / 0.18) + 1)
        txt(dr, (W / 2, 420), s[:n], F("cjk", 190), stroke=8)
        if n == len(s):
            txt(dr, (W / 2, 640), "“NÃO ACEITO, NÃO PERDOADO”", F("anton", 100), fill=YEL)
            dr.text((W / 2, 750), "— comentário viral de usuários nas redes chinesas", font=F("inter", 40),
                    fill=(230, 230, 230), anchor="mm")
    elif name == "endscreen":
        dr.rounded_rectangle([140, 220, 140 + 960, 220 + 540], 18, fill=(25, 25, 28), outline=YEL, width=6)
        txt(dr, (620, 440), "VÍDEO: NIKE → ON", F("anton", 90), fill=YEL)
        dr.text((620, 540), "(elemento de tela final do YouTube)", font=F("inter", 34), fill=(200, 200, 200),
                anchor="mm")
        dr.ellipse([1300, 300, 1700, 700], fill=(25, 25, 28), outline=RED, width=10)
        txt(dr, (1500, 500), "INSCREVA-SE", F("anton", 70))
        txt(dr, (W / 2, 120), "COMENTA AÍ: ELE DEVIA TER PEDIDO DESCULPAS?", F("anton", 74))
    return c


def title_card(text, tl):
    c = Image.new("RGB", (W, H), (0, 0, 0))
    lay = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(lay)
    lines = wrap(d, text, F("anton", 140), 1600)
    for k, ln in enumerate(lines):
        d.text((W / 2, H / 2 + (k - (len(lines) - 1) / 2) * 160), ln, font=F("anton", 140), fill=WHITE, anchor="mm")
    off = int(30 * max(0, 1 - tl / 0.5))
    r, g, b = lay.split()
    r = r.transform(r.size, Image.AFFINE, (1, 0, off, 0, 1, 0))
    b = b.transform(b.size, Image.AFFINE, (1, 0, -off, 0, 1, 0))
    c = Image.merge("RGB", (r, g, b))
    if tl < 0.4:
        a = np.asarray(c).copy()
        rng = np.random.default_rng(int(tl * 100))
        for _ in range(6):
            y = rng.integers(0, H - 40)
            a[y:y + 30] = np.roll(a[y:y + 30], rng.integers(-80, 80), 1)
        c = Image.fromarray(a)
    return c


# ── overlays ────────────────────────────────────────────────────────────────────────────────────────
def stamp(c, text, xy, tl, size=170):
    if tl < 0:
        return
    k = 1.6 - 0.6 * ease(tl / 0.15)
    f = F("anton", int(size * k))
    tmp = Image.new("RGBA", (W, int(size * 2.2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bb = d.textbbox((W / 2, tmp.height / 2), text, font=f, anchor="mm")
    pad = int(26 * k)
    d.rectangle([bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad], outline=RED + (235,), width=int(12 * k))
    d.text((W / 2, tmp.height / 2), text, font=f, fill=RED + (235,), anchor="mm")
    tmp = tmp.rotate(-7, resample=Image.BICUBIC)
    c.paste(tmp, (int(xy[0] - W / 2), int(xy[1] - tmp.height / 2)), tmp)


def overlay_text(c, spec, tl, dur):
    text, style = spec
    if tl < 0.25:
        return
    tl -= 0.25
    d = ImageDraw.Draw(c)
    if style == "stamp":
        stamp(c, text, (W / 2, 470), tl)
    elif style == "type":
        n = min(len(text), int(tl * 28))
        f = F("interb", 58)
        tw = d.textlength(text, font=f)
        d.rectangle([W / 2 - tw / 2 - 30, 700, W / 2 + tw / 2 + 30, 790], fill=(0, 0, 0))
        d.text((W / 2 - tw / 2, 745), text[:n] + ("▌" if n < len(text) else ""), font=f, fill=YEL, anchor="lm")
    else:
        k = 0.7 + 0.3 * ease(tl / 0.2)
        fill = YEL if any(ch.isdigit() for ch in text) else WHITE
        words = text.split()
        cjk = any("\u4e00" <= ch <= "\u9fff" for ch in text)       # Anton não tem ideogramas
        f = F("cjk" if cjk else "anton", int(170 * k))
        if cjk:
            fill = YEL
        if len(words) > 1 and fill == WHITE:      # palavra-chave (a última) em vermelho
            head = " ".join(words[:-1]) + " "
            tw = d.textlength(head + words[-1], font=f)
            x = W / 2 - tw / 2
            d.text((x, 470), head, font=f, fill=WHITE, anchor="lm", stroke_width=8, stroke_fill=BLACK)
            d.text((x + d.textlength(head, font=f), 470), words[-1], font=f, fill=RED, anchor="lm", stroke_width=8,
                   stroke_fill=BLACK)
        else:
            d.text((W / 2, 470), text, font=f, fill=fill, anchor="mm", stroke_width=8, stroke_fill=BLACK)


def counter(c, n):
    d = ImageDraw.Draw(c)
    d.rectangle([40, 40, 470, 130], fill=RED)
    d.text((255, 85), f"PUNIÇÃO {n}/5", font=F("anton", 64), fill=WHITE, anchor="mm")


def highlight(c, text, tl):
    if tl < 0.6:
        return
    d = ImageDraw.Draw(c)
    f = F("interb", 48)
    p = ease((tl - 0.6) / 0.25)
    tw = d.textlength(text, font=f)
    x0, y = W / 2 - tw / 2 - 24, 870 - 150
    d.rectangle([x0, y - 38, x0 + (tw + 48) * p, y + 38], fill=YEL)
    if p > 0.95:
        d.text((W / 2, y), text, font=f, fill=BLACK, anchor="mm")


def source(c, text):
    d = ImageDraw.Draw(c)
    d.text((40, H - 40), "Fonte: " + text, font=F("inter", 28), fill=(210, 210, 210), anchor="ls",
           stroke_width=2, stroke_fill=BLACK)


def chunks(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        n = sum(len(x[0]) + 1 for x in cur)
        if n > 46 or (n > 26 and w[0][-1] in ".?!:,—") or len(cur) >= 9:
            out.append(cur)
            cur = []
    return out + ([cur] if cur else [])


def captions(c, bt, t):
    ws = bt.get("words") or []
    if not ws or t > bt["end"] + 0.35 or t < ws[0][1] - 0.15:
        return
    groups = chunks(ws)
    g = groups[0]
    for gr in groups:
        if gr[0][1] - 0.15 <= t:
            g = gr
    d = ImageDraw.Draw(c)
    f = F("interb", 54)
    lines = wrap(d, " ".join(w for w, _ in g), f, 1500)
    idx, k = [], 0
    for ln in lines:
        n = len(ln.split())
        idx.append(g[k:k + n])
        k += n
    active = max([i for i, w in enumerate(g) if w[1] <= t] or [0])
    y0 = H - 110 - (len(lines) - 1) * 66
    k = 0
    for li, row in enumerate(idx):
        s = " ".join(w for w, _ in row)
        x = W / 2 - d.textlength(s, font=f) / 2
        for w, _ in row:
            col = YEL if k == active else WHITE
            d.text((x, y0 + li * 66), w, font=f, fill=col, anchor="ls", stroke_width=6, stroke_fill=BLACK)
            x += d.textlength(w + " ", font=f)
            k += 1


_VIG = None


_GRAIN = None


def finish(c, fi, grain=False):
    """Vinheta em tudo; grão leve só em FOTO/IA (grão em todo quadro estoura o bitrate do H.264)."""
    global _VIG, _GRAIN
    a = np.asarray(c, np.float32)
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = np.clip(1 - 0.35 * (r - 0.55).clip(0) ** 1.4, 0.4, 1)[..., None].astype(np.float32)
    a *= _VIG
    if grain:
        if _GRAIN is None:
            r = np.random.default_rng(5)
            _GRAIN = [r.normal(0, 4, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
                      for _ in range(4)]
        a += _GRAIN[(fi // 3) % 4]
    return np.clip(a, 0, 255).astype(np.uint8)


# ── frame ───────────────────────────────────────────────────────────────────────────────────────────
def frame(t, fi, shots):
    sh = next((s for s in shots if s["t0"] <= t < s["t1"]), shots[-1])
    a, o, b = sh["asset"], sh["opts"], sh["b"]
    tl, d = t - sh["t0"], sh["t1"] - sh["t0"]
    u = tl / max(d, 1e-6)
    kind = a.split("_")[0]
    if a == "black":
        c = Image.new("RGB", (W, H))
    elif a.startswith("title:"):
        c = title_card(a[6:], tl)
    elif a.startswith("gfx:"):
        c = gfx(a[4:], t - sh["bt0"], u, d)
    elif a == "grid":
        c = texture()
        for k, g in enumerate(o["grid"]):
            if t - sh["bt0"] >= 0.35 * k:
                cell = cover(still(g), 1.0 + 0.05 * u, size=(940, 520))
                c.paste(cell, (10 + (k % 2) * 950, 15 + (k // 2) * 530))
    elif a == "split":
        c = Image.new("RGB", (W, H))
        for k, g in enumerate(o["split"]):
            c.paste(cover(still(g), 1.04 + 0.05 * u, size=(W // 2 - 6, H)), (k * (W // 2 + 6), 0))
    elif a == "logos":
        c = logos_shot(o["logos"], t - sh["bt"]["start"], timeline.fall_times(sh["bt"]), o.get("fall"))
    elif o.get("crack"):
        c = crack_shot(a, tl, d)
    elif kind == "PRT":
        c = print_shot(a, tl, sh["sub"], sh)
    elif kind == "MEME":
        c = meme_shot(a, tl, u, sh["sub"], o)
    elif kind == "CLP" and is_video(find(a)) and not o.get("frame"):
        c = CLIP.frame(find(a), o.get("ss", 0) + t - sh["bt0"])
    elif kind == "CLP":
        c = kenburns(still(a, o.get("frame", 0.1)), u, sh["sub"], "in")
    else:
        c = kenburns(still(a), u, sh["sub"], o.get("kb"))
        if kind == "IA" and find(a) is None:          # a imagem do Flow já vem no tom vermelho/preto
            c = grade_red(c)
    if o.get("bw"):
        c = bw(c)
    bt = sh["bt"]
    tb = t - bt["start"]
    if b.get("txt"):
        overlay_text(c, b["txt"], tb, bt["end"] - bt["start"])
    if kind == "PRT":
        if b.get("hl") and b["hl"] != "bloco em chinês":
            highlight(c, b["hl"], tl)
        f = find(a) or ""
        if "_manchete_" in f:                         # print provisório de manchete: crédito = site da matéria
            source(c, os.path.splitext(f.split("_manchete_")[1])[0])
        elif "_x_" in f:                              # print de tweet: crédito = @ do autor
            source(c, "X / @" + os.path.splitext(f.split("_x_")[1])[0])
        elif b.get("fonte"):
            source(c, b["fonte"])
    if b.get("pun"):
        counter(c, b["pun"])
    captions(c, bt, t)
    return finish(c, fi, kind in ("FOT", "IA") and find(a) is not None)


def render_part(args):
    i0, i1, out = args
    tm, blocks, shots, total = timeline.load()
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in range(i0, i1):
        p.stdin.write(frame(fi / FPS, fi, shots).tobytes())
        if fi % 300 == 0:
            print(f"  quadro {fi}", flush=True)
    p.stdin.close()
    p.wait()
    return out


def main():
    tm, blocks, shots, total = timeline.load()
    if "--assets" in sys.argv:
        used = sorted({x for s in shots for x in ([s["asset"]] + s["opts"].get("grid", []) +
                       s["opts"].get("split", []) + s["opts"].get("logos", [])) if x.split("_")[0] in FOLDERS})
        for a in used:
            print(("OK   " if find(a) else "FALTA"), a, find(a) or DESC.get(a, ""))
        return
    if "--quadros" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--quadros") + 1:]]
        ims = [Image.fromarray(frame(t, int(t * FPS), shots)).resize((640, 360)) for t in ts]
        cols = 3
        g = Image.new("RGB", (640 * cols, 360 * ((len(ims) + cols - 1) // cols)))
        for k, im in enumerate(ims):
            ImageDraw.Draw(im).text((10, 10), f"{t_fmt(ts[k])}", font=F("interb", 28), fill=YEL)
            g.paste(im, ((k % cols) * 640, (k // cols) * 360))
        g.save(os.path.join(BUILD, "quadros.png"))
        print("build/quadros.png")
        return
    n = int(total * FPS)
    os.makedirs(os.path.join(BUILD, "parts"), exist_ok=True)
    k = int(os.environ.get("JOBS", os.cpu_count() or 4))
    edges = [n * j // k for j in range(k + 1)]
    parts = [(edges[j], edges[j + 1], os.path.join(BUILD, "parts", f"p{j:02d}.mp4")) for j in range(k)]
    if "--so-audio" in sys.argv:          # remux: reaproveita os pedaços de vídeo já renderizados
        outs = [p[2] for p in parts]
    else:
        with Pool(k) as pool:
            outs = pool.map(render_part, parts)
    lst = os.path.join(BUILD, "parts", "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.basename(o)}'\n" for o in outs))
    os.makedirs(os.path.join(HERE, "saida"), exist_ok=True)
    out = os.path.join(HERE, "saida", "mbappe_china.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", os.path.join(BUILD, "mix.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    open(os.path.join(HERE, "saida", "capitulos.txt"), "w").write("\n".join(timeline.chapters(blocks)) + "\n")
    print("OK", out)


def t_fmt(t):
    return f"{int(t) // 60}:{t % 60:04.1f}"


if __name__ == "__main__":
    main()
