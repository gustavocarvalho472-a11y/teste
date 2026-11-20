"""Extras do lote de 10: legenda .srt, capítulos, descrição/títulos/tags e thumbs A (Inter Black) e B (editorial).

  python lote10/extras.py r01      (lê lote10/timeline_r01.json, lote10/cenas_r01.json, lote10/meta.py)
Saída em out/r01/.
"""
import json, os, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
sys.path.insert(0, os.path.dirname(__file__))
from meta import META

V = sys.argv[1]; M = META[V]
tl = json.load(open(f"lote10/timeline_{V}.json")); frases = tl["frases"]
cenas = json.load(open(f"lote10/cenas_{V}.json"))
OUT = f"out/{V}"; os.makedirs(OUT, exist_ok=True); os.makedirs("work/thumb", exist_ok=True)

def srt_t(s):
    ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); ss, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{ss:02d},{ms:03d}"
def mmss(s): s = int(s); return f"{s // 60:02d}:{s % 60:02d}"

with open(f"{OUT}/legenda_{V}.srt", "w", encoding="utf-8") as f:
    for n, fr in enumerate(frases, 1):
        linhas = textwrap.wrap(fr["frase"], 42)
        if len(linhas) > 2:
            meio = len(fr["frase"]) // 2; corte = fr["frase"].rfind(" ", 0, meio + 8)
            linhas = [fr["frase"][:corte], fr["frase"][corte + 1:]]
        f.write(f"{n}\n{srt_t(fr['inicio'])} --> {srt_t(fr['fim'] + 0.3)}\n" + "\n".join(linhas) + "\n\n")

caps, vistos = [], set()
for fr in frases:
    if fr["bloco"] in vistos: continue
    vistos.add(fr["bloco"]); t = 0 if not caps else max(0, fr["inicio"] - 1.0)
    caps.append(f"{mmss(t)} {fr['titulo_bloco']}")

desc = f"""{M['titulo']}

{M['intro']}

Escreva AMÉM nos comentários e deixe o seu pedido de oração, com o seu nome.

Envie esta oração para alguém que precisa dela hoje.

Inscreva-se e ative o sininho para receber uma nova oração.

CAPÍTULOS
{chr(10).join(caps)}

Versículos citados em paráfrase: {M['versos']}.

Narração com voz gerada por IA. Imagens: vídeos gratuitos do Pexels.

{' '.join(M['hashtags'])}
"""
assert len(M["titulo"]) <= 100 and len(desc) <= 5000 and len(M["tags"]) == 18, (len(M["titulo"]), len(desc), len(M["tags"]))
with open(f"{OUT}/descricao_{V}.txt", "w", encoding="utf-8") as f:
    f.write("TÍTULO\n" + M["titulo"] + "\n\nTÍTULOS ALTERNATIVOS\n" + "\n".join("- " + a for a in M["alternativas"]))
    f.write("\n\nTAGS (18)\n" + ", ".join(M["tags"]) + "\n\n" + "=" * 50 + "\nDESCRIÇÃO\n" + "=" * 50 + "\n\n" + desc)

# ---------- thumbs ----------
INTER, SERIF, SERIF_I = "fonts/Inter[opsz,wght].ttf", "fonts/InstrumentSerif-Regular.ttf", "fonts/InstrumentSerif-Italic.ttf"
def inter(size, var="Black"):
    f = ImageFont.truetype(INTER, size); f.set_variation_by_name(var); return f
AMAR, BRANCO = (255, 214, 64, 255), (255, 255, 255, 255)

def frame(clip_id, t):
    path = f"work/thumb/{clip_id}_{t}.png"
    if not os.path.exists(path):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", f"clips/{clip_id}.mp4", "-frames:v", "1", path], check=True)
    return Image.open(path).convert("RGB")

def base(img, brilho):
    img = ImageOps.fit(img, (1280, 720), Image.LANCZOS)
    img = ImageEnhance.Brightness(img).enhance(brilho); img = ImageEnhance.Contrast(img).enhance(0.95)
    r, g, b = img.split()  # toque quente de filme
    return Image.merge("RGB", (r.point(lambda v: min(255, v * 1.05 + 6)), g.point(lambda v: v + 4), b.point(lambda v: v * 0.94 + 8)))

def sombra(img, xy, txt, font, fill, anchor="mt", blur=10):
    s = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(s)
    ds.text((xy[0] + 3, xy[1] + 5), txt, font=font, fill=(0, 0, 0, 255), anchor=anchor, stroke_width=4, stroke_fill=(0, 0, 0, 255))
    s = s.filter(ImageFilter.GaussianBlur(blur)); img.alpha_composite(s); img.alpha_composite(s)
    ImageDraw.Draw(img).text(xy, txt, font=font, fill=fill, anchor=anchor)

def clip(tag_ou_id):
    if isinstance(tag_ou_id, int): return tag_ou_id
    return next(c["clip"]["id"] for c in cenas if c["clip"]["tag"] == tag_ou_id)

# A: Inter Black, linhas alternando branco e amarelo
cid, t = M["thumb_a_fundo"]
img = base(frame(clip(cid), t), M.get("thumb_a_brilho", 0.82)).convert("RGBA")
y = M.get("thumb_a_y", 90); d = ImageDraw.Draw(img)
for txt, size, cor in M["thumb_a"]:
    f = inter(size); sombra(img, (640, y), txt, f, AMAR if cor == "a" else BRANCO)
    y += d.textbbox((0, 0), txt, font=f)[3] + M.get("thumb_a_gap", 24)
img.convert("RGB").save(f"{OUT}/thumb_A_{V}.jpg", quality=92)

# B: editorial (serifa grande com palavra em itálico amarelo, grade fina, micro texto espaçado)
cid, t = M["thumb_b_fundo"]
img = base(frame(clip(cid), t), M.get("thumb_b_brilho", 0.78)).convert("RGBA")
d = ImageDraw.Draw(img)
for y in (150, 590): d.line((0, y, 1280, y), fill=(255, 255, 255, 120), width=2)
for x in (110, 1170): d.line((x, 0, x, 720), fill=(255, 255, 255, 120), width=2)
for x, y in ((110, 150), (1170, 150), (110, 590), (1170, 590)): d.rectangle((x - 7, y - 7, x + 7, y + 7), outline=(255, 255, 255, 230), width=2)
fm = inter(24, "SemiBold")
def micro(xy, txt, anchor):
    sp = "  ".join(" ".join(p) for p in txt.split(" "))
    sombra(img, xy, sp, fm, BRANCO, anchor=anchor, blur=6)
micro((124, 138), M["thumb_b_ref"], "ld"); micro((1156, 138), M["thumb_b_rodape"], "rd")
micro((124, 602), "ORAÇÃO", "la"); micro((1156, 602), M["thumb_b_tema"], "ra")
# linhas da frase editorial: palavras entre * em itálico amarelo
for (linha, size), y in zip(M["thumb_b"], M.get("thumb_b_ys", [215, 385])):
    partes = [(w.replace("*", ""), w.startswith("*")) for w in linha.split(" ")]
    while True:  # ajusta o tamanho para caber em ~1000 px
        fr, fi = ImageFont.truetype(SERIF, size), ImageFont.truetype(SERIF_I, size)
        larg = sum(d.textlength(p + " ", font=fi if it else fr) for p, it in partes) - d.textlength(" ", font=fr)
        if larg <= 1000 or size < 80: break
        size -= 6
    x = 640 - larg / 2
    for p, it in partes:
        f = fi if it else fr
        sombra(img, (x, y), p, f, AMAR if it else BRANCO, anchor="la", blur=12)
        x += d.textlength(p + " ", font=f)
img.convert("RGB").save(f"{OUT}/thumb_B_{V}.jpg", quality=92)
print("ok", OUT, "| título", len(M["titulo"]), "| descrição", len(desc))
