"""Formas gráficas desenhadas (máscaras 1080x1920) para virar partículas: coroa, harpa, número, telas, coração, barras, rei."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
CX, CY = W / 2, 960
F = "/usr/share/fonts/opentype/inter/"
def font(n, s): return ImageFont.truetype(F + n, s)


def mask(draw_fn):
    """Desenha a forma e devolve um array 0..1 do quadro inteiro."""
    img = Image.new("L", (W, H), 0); draw_fn(ImageDraw.Draw(img), img)
    return np.asarray(img, np.float32) / 255


def king_draw(d, img=None):
    d.ellipse([480, 520, 600, 640], fill=255)                                        # cabeça
    d.polygon([(470, 530), (470, 450), (505, 490), (540, 430), (575, 490), (610, 450), (610, 530)], fill=255)  # coroa
    d.rectangle([470, 515, 610, 532], fill=0)
    d.rectangle([520, 630, 560, 670], fill=255)
    d.polygon([(450, 670), (630, 670), (720, 1240), (360, 1240)], fill=255)          # manto
    d.line([(540, 690), (540, 1240)], fill=0, width=14)
    d.polygon([(450, 670), (400, 700), (370, 900), (410, 905)], fill=255)            # braços
    d.polygon([(630, 670), (680, 700), (710, 900), (670, 905)], fill=255)

def harp_draw(d, img=None):
    d.line([(370, 1200), (370, 560)], fill=255, width=34)
    xs = np.linspace(370, 740, 40); ys = 600 - 70 * np.sin((xs - 370) / 370 * np.pi) + (xs - 370) * 0.12
    d.line(list(zip(xs, ys)), fill=255, width=30)
    d.line([(740, 645), (400, 1190)], fill=255, width=38)
    for x in np.arange(420, 720, 34):
        ytop = np.interp(x, xs, ys); ybot = 645 + (740 - x) / 340 * 545
        d.line([(x, ytop), (x, ybot)], fill=255, width=9)

def crown_draw(d, img=None):
    d.polygon([(290, 1080), (290, 690), (415, 880), (540, 620), (665, 880), (790, 690), (790, 1080)], fill=255)
    d.rectangle([290, 990, 790, 1010], fill=0)
    for x, y in [(290, 690), (540, 620), (790, 690)]:
        d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=255)
    for x in (400, 540, 680):
        d.ellipse([x - 26, 925, x + 26, 977], fill=0)

def text_draw(txt, size, cy=CY):
    def f(d, img=None):
        fnt = font("InterDisplay-Bold.otf", size); bb = d.textbbox((0, 0), txt, font=fnt)
        d.text((CX - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), txt, font=fnt, fill=255)
    return f

def phones_draw(d, img=None):
    for r in range(3):
        for c in range(3):
            x, y = 205 + c * 235, 470 + r * 285
            d.rounded_rectangle([x, y, x + 200, y + 255], 28, outline=255, width=18)
            d.ellipse([x + 75, y + 70, x + 125, y + 120], fill=255)
            d.pieslice([x + 50, y + 130, x + 150, y + 230], 180, 360, fill=255)

def heart_draw(d, img=None):
    t = np.linspace(0, 2 * np.pi, 200)
    x = 16 * np.sin(t) ** 3; y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    d.polygon(list(zip(CX + x * 24, CY - y * 24)), fill=255)

def bars_draw(d, img=None):
    hs, bw, gap = [140, 230, 330, 450, 590], 120, 46
    x0 = CX - (5 * bw + 4 * gap) / 2
    for i, h in enumerate(hs):
        d.rectangle([x0 + i * (bw + gap), 1160 - h, x0 + i * (bw + gap) + bw, 1160], fill=255)
