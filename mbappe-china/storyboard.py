"""Storyboard: um painel por bloco do roteiro (quadro renderizado + tempo + narração + assets e status).

    python3 storyboard.py      → saida/storyboard.pdf (e saida/storyboard_NN.png)

Rode de novo depois de salvar assets: os painéis passam a mostrar a imagem real e o status vira OK.
"""
import os

from PIL import Image, ImageDraw

import montar
import timeline
from montar import F, find, wrap, DESC, FOLDERS, YEL, RED, WHITE

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 2480, 3508                  # A4 a 300 dpi, retrato
COLS, ROWS = 2, 4
TW, TH = 1120, 630                   # quadro 16:9 em cada painel


def assets_of(b):
    out = []
    for s in b["shots"]:
        a, o = (s, {}) if isinstance(s, str) else s
        for x in [a] + o.get("grid", []) + o.get("split", []) + o.get("logos", []):
            if x.split("_")[0] in FOLDERS and x not in out:
                out.append(x)
            elif x.startswith("gfx:") and x not in out:
                out.append(x)
    return out


def fx_of(b):
    bits = []
    if b.get("txt"):
        t = "".join(ch for ch in b["txt"][0] if not "\u4e00" <= ch <= "\u9fff").strip()
        bits.append(f'texto "{t}" ({b["txt"][1]})')
    if b.get("hl"):
        bits.append(f'destaque "{b["hl"]}"')
    if b.get("sfx"):
        bits.append("sfx " + b["sfx"])
    if b.get("pun"):
        bits.append(f'PUNIÇÃO {b["pun"]}/5')
    if b.get("mus"):
        bits.append("música " + b["mus"])
    return " · ".join(bits)


def main():
    tm, blocks, shots, total = timeline.load()
    pages, page, k = [], None, 0
    per = COLS * ROWS
    n_ok = n_all = 0
    for i, (b, bt) in enumerate(zip(timeline.B, blocks)):
        if k % per == 0:
            page = Image.new("RGB", (PW, PH), (245, 243, 238))
            d = ImageDraw.Draw(page)
            d.text((80, 70), "STORYBOARD · Mbappé OFENDEU a China", font=F("anton", 80), fill=(20, 20, 20))
            d.text((PW - 80, 110), f"pág. {len(pages) + 1}", font=F("inter", 40), fill=(90, 90, 90), anchor="rs")
            pages.append(page)
        d = ImageDraw.Draw(page)
        c, r = k % COLS, (k % per) // COLS
        x0, y0 = 80 + c * (TW + 160), 220 + r * 820
        t_mid = min(bt["start"] + 0.9 * max(0.6, bt["end"] - bt["start"]) * 0.6, total - 0.1)
        im = Image.fromarray(montar.frame(t_mid, int(t_mid * 30), shots)).resize((TW, TH), Image.LANCZOS)
        page.paste(im, (x0, y0))
        d.rectangle([x0, y0, x0 + TW, y0 + TH], outline=(30, 30, 30), width=3)
        if b.get("ato"):
            d.rectangle([x0, y0 - 52, x0 + TW, y0 - 6], fill=RED)
            d.text((x0 + 14, y0 - 29), "ATO · " + b["ato"].upper(), font=F("anton", 34), fill=WHITE, anchor="lm")
        t = bt["start"]
        d.rectangle([x0, y0, x0 + 330, y0 + 56], fill=(0, 0, 0))
        d.text((x0 + 14, y0 + 28), f'{b["id"]}  {int(t) // 60}:{int(t) % 60:02d}', font=F("anton", 40), fill=YEL,
               anchor="lm")
        y = y0 + TH + 14
        fala = b["fala"] or "(sem fala)"
        for ln in wrap(d, fala, F("inter", 28), TW)[:3]:
            d.text((x0, y), ln, font=F("inter", 28), fill=(25, 25, 25))
            y += 34
        line = []
        for a in assets_of(b):
            if a.startswith("gfx:"):
                line.append((a, (90, 90, 90)))
            else:
                ok = find(a) is not None
                n_all += 1
                n_ok += ok
                line.append((("✓ " if ok else "✗ ") + a, (20, 140, 60) if ok else (200, 30, 30)))
        xx = x0
        for s, col in line:
            w = d.textlength(s + "   ", font=F("interb", 28))
            if xx + w > x0 + TW:
                xx, y = x0, y + 34
            d.text((xx, y + 4), s, font=F("interb", 28), fill=col)
            xx += w
        y += 40
        fx = fx_of(b)
        if fx:
            d.text((x0, y), wrap(d, fx, F("inter", 24), TW)[0], font=F("inter", 24), fill=(110, 110, 110))
        k += 1
    for p in pages:
        ImageDraw.Draw(p).text((80, PH - 80), f"assets prontos: {n_ok}/{n_all}", font=F("interb", 36),
                               fill=(60, 60, 60))
    os.makedirs(os.path.join(HERE, "saida"), exist_ok=True)
    pdf = os.path.join(HERE, "saida", "storyboard.pdf")
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=300)
    for j, p in enumerate(pages):
        p.resize((PW // 2, PH // 2), Image.LANCZOS).save(os.path.join(HERE, "saida", f"storyboard_{j + 1:02d}.png"))
    print(pdf, len(pages), "páginas", f"assets {n_ok}/{n_all}")


if __name__ == "__main__":
    main()
