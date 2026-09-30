"""Thumbnails 1280x720 no estilo ilustração chapada (texto à esquerda, arte à direita).

    python3 thumb.py            # gera as thumbs do Filho Pródigo e da História de Jesus (PT e EN)
"""
import math
import os

import cairo
import numpy as np
from PIL import Image

from engine import _texture
from prodigo import GOLD, H, TEAL, TAU, W, blob, fill, hug, paint, sun

HERE = os.path.dirname(os.path.abspath(__file__))


def text(c, s, x, y, size, col, bold=True):
    c.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    c.move_to(x + 4, y + 6)
    c.set_source_rgba(0, 0, 0, 0.35)
    c.show_text(s)
    c.move_to(x, y)
    c.set_source_rgb(*[int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    c.show_text(s)
    return c.text_extents(s).x_advance


def pill(c, s, x, y, size):
    c.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    w = c.text_extents(s).x_advance
    h = size * 1.6
    r = h / 2
    c.new_sub_path()
    c.arc(x + r, y, r, math.pi / 2, 3 * math.pi / 2)
    c.arc(x + w + size * 0.8 + r, y, r, -math.pi / 2, math.pi / 2)
    c.close_path()
    fill(c, GOLD)
    c.move_to(x + r + size * 0.4, y + size * 0.36)
    c.set_source_rgb(0.1, 0.06, 0.12)
    c.show_text(s)


def _art_prodigo(c):
    paint(c, "#4a2f5c")
    blob(c, W * 0.74, H * 0.6, 640, 4)
    fill(c, "#3a2249")
    # raios geométricos + sol
    cx, cy = W * 0.73, H * 0.58
    for k in range(16):
        a = k / 16 * TAU
        c.move_to(cx, cy)
        c.line_to(cx + math.cos(a - 0.06) * 1300, cy + math.sin(a - 0.06) * 1300)
        c.line_to(cx + math.cos(a + 0.06) * 1300, cy + math.sin(a + 0.06) * 1300)
        c.close_path()
        fill(c, "#5a3a6c", 0.7)
    sun(c, cx, cy, 400)
    # chão
    c.move_to(W * 0.42, H + 10)
    c.curve_to(W * 0.5, H * 0.88, W * 0.9, H * 0.86, W + 10, H * 0.9)
    c.line_to(W + 10, H + 10)
    fill(c, "#2c1b38")
    # pai abraçando o filho, grande e cortado pela borda inferior
    hug(c, W * 0.75, H * 1.04, 720)


def _art_jesus(c):
    from jesus_flat import geo_rays, halo
    from prodigo import person
    paint(c, "#23306a")
    blob(c, W * 0.74, H * 0.6, 640, 9)
    fill(c, "#1a2250")
    cx, cy = W * 0.74, H * 0.6
    geo_rays(c, cx, cy, 16, 0.1, "#2d3e8a", 1.0)
    sun(c, cx, cy, 400)
    c.move_to(W * 0.42, H + 10)
    c.curve_to(W * 0.5, H * 0.9, W * 0.9, H * 0.86, W + 10, H * 0.9)
    c.line_to(W + 10, H + 10)
    fill(c, "#141a3a")
    fx, fy = W * 0.74, H * 1.08
    person(c, fx, fy, 640, "raised", sash=GOLD)
    halo(c, fx, fy, 640)


def make_thumb(art, kicker, line1, line2, badge, out):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    art(c)
    s.flush()
    buf = np.ndarray((H, W, 4), np.uint8, buffer=s.get_data())
    buf[:, :, :3] = np.clip(buf[:, :, :3].astype(np.int16) + _texture()[0], 0, 255).astype(np.uint8)
    s.mark_dirty()
    # texto
    c.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(200)
    widest = max(c.text_extents(line1).x_advance, c.text_extents(line2).x_advance)
    size = min(200, 200 * (W * 0.5 - 110) / widest)   # o título nunca invade a ilustração
    text(c, kicker, 110, 330, 66, TEAL)
    text(c, line1, 100, 520, size, "#ffffff")
    text(c, line2, 100, 520 + size, size, "#ffffff")
    c.rectangle(108, 570 + size, 300, 14)
    fill(c, GOLD)
    if badge:
        pill(c, badge, 108, 670 + size, 54)
    s.flush()
    img = Image.frombuffer("RGBA", (W, H), bytes(s.get_data()), "raw", "BGRA", 0, 1).convert("RGB")
    img.resize((1280, 720), Image.LANCZOS).save(out, optimize=True)
    print("OK:", out)


if __name__ == "__main__":
    make_thumb(_art_prodigo, "Uma parábola de Jesus", "O Filho", "Pródigo", "Lucas 15",
               os.path.join(HERE, "thumb_filho_prodigo_pt.png"))
    make_thumb(_art_prodigo, "A parable of Jesus", "The Prodigal", "Son", "Luke 15",
               os.path.join(HERE, "thumb_prodigal_son_en.png"))
    make_thumb(_art_jesus, "Do nascimento à ressurreição", "A História", "de Jesus", "em 2 minutos",
               os.path.join(HERE, "thumb_historia_de_jesus_pt.png"))
    make_thumb(_art_jesus, "From birth to resurrection", "The Story", "of Jesus", "in 2 minutes",
               os.path.join(HERE, "thumb_story_of_jesus_en.png"))
