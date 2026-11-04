"""Gera legenda .srt, capítulos, descrição/títulos/tags e 2 thumbnails.

  python 04_extras.py
"""
import json, os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

tl = json.load(open("timeline.json")); frases = tl["frases"]
os.makedirs("out", exist_ok=True); os.makedirs("work/thumb", exist_ok=True)

def srt_t(s):
    ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); ss, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{ss:02d},{ms:03d}"

def mmss(s):
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"

# ---------- legenda ----------
with open("out/legenda_v2.srt" if os.environ.get("VIDEO") == "v2" else "out/legenda.srt", "w", encoding="utf-8") as f:
    for n, fr in enumerate(frases, 1):
        linhas = textwrap.wrap(fr["frase"], 42)
        if len(linhas) > 2:  # reequilibra em 2 linhas
            meio = len(fr["frase"]) // 2; corte = fr["frase"].rfind(" ", 0, meio + 8)
            linhas = [fr["frase"][:corte], fr["frase"][corte + 1:]]
        f.write(f"{n}\n{srt_t(fr['inicio'])} --> {srt_t(fr['fim'] + 0.3)}\n" + "\n".join(linhas) + "\n\n")

# ---------- capítulos ----------
caps, vistos = [], set()
for fr in frases:
    if fr["bloco"] in vistos: continue
    vistos.add(fr["bloco"])
    t = 0 if not caps else max(0, fr["inicio"] - 1.0)
    caps.append(f"{mmss(t)} {fr['titulo_bloco'].replace(' · ', ': ')}")

# ---------- créditos ----------
creditos = open("out/creditos.txt", encoding="utf-8").read().strip() if os.path.exists("out/creditos.txt") else ""

V2 = os.environ.get("VIDEO") == "v2"
if V2:
    TITULO = "ORAÇÃO DA NOITE para Dormir em Paz | Entregue a Deus o Medo, as Contas e a Ansiedade"
    ALTERNATIVAS = [
        "Oração Poderosa Antes de Dormir com os SALMOS 91, 23 e 121 | Durma em Paz Hoje",
        "ORAÇÃO PARA DORMIR | Pela Sua Família, Seu Trabalho, Suas Finanças e Sua Saúde",
    ]
    TAGS = ["oração da noite", "oração para dormir", "oração antes de dormir", "salmo 91", "salmo 23", "salmo 121",
            "oração contra ansiedade", "oração contra o medo", "oração pelas finanças", "oração pela família",
            "oração pelo trabalho", "oração pela saúde", "oração de proteção", "oração poderosa",
            "salmos para dormir", "pai nosso", "oração para acalmar o coração", "oração da noite de hoje"]
    desc = f"""{TITULO}

Esta é uma oração da noite para você que deitou, mas não consegue descansar. Nós vamos orar juntos pelo medo que aperta o peito, pelas contas e o sustento da sua casa, pela sua família, pelo seu trabalho, pelas pessoas que te feriram ou te perseguem e pela saúde do seu corpo e da sua mente. Cada parte tem um Salmo: Salmo 91, Salmo 23, Salmo 37, Salmo 121, Salmo 27, Salmo 103 e Salmo 4, e terminamos com o Pai-Nosso.

🙏 Escreva AMÉM nos comentários e deixe o seu pedido de oração. Vamos orar por você e pela sua família.

📲 Conhece alguém que está passando por isso? Envie esta oração para essa pessoa.

🔔 Inscreva-se e ative o sininho para receber uma nova oração toda noite.

CAPÍTULOS
{chr(10).join(caps)}

Leituras bíblicas em paráfrase própria baseada na tradução de João Ferreira de Almeida.

CRÉDITOS DE IMAGEM
{creditos.replace('Vídeos de stock: Pexels (pexels.com)', 'Vídeos de stock gratuitos do Pexels (pexels.com):')}

#oraçãodanoite #oraçãoparadormir #salmo91
"""
else:
    TITULO = "ORAÇÃO DA NOITE com SALMO 91, 23 e 121 | Durma em Paz e Acorde Protegido"
    ALTERNATIVAS = [
        "Durma Ouvindo os SALMOS 91, 23 e 121 | Oração da Noite para Acalmar a Ansiedade",
        "ORAÇÃO PARA DORMIR com os Salmos | Entregue Sua Noite a Deus e Durma em Paz",
    ]
    TAGS = ["oração da noite", "oração para dormir", "salmo 91", "salmo 23", "salmo 121", "salmos para dormir",
            "oração contra ansiedade", "oração de proteção", "oração poderosa", "oração da noite de hoje",
            "salmo 27", "salmo 46", "salmo 139", "pai nosso", "oração para acalmar o coração",
            "palavra de deus para dormir", "oração antes de dormir", "bíblia para dormir"]
    desc = f"""{TITULO}

    Esta é uma oração da noite para dormir em paz, guiada pelos Salmos: Salmo 4, Salmo 23, Salmo 91, Salmo 121, Salmo 27, Salmo 46 e Salmo 139. Se o seu coração está pesado, se a ansiedade não deixa você descansar ou se você precisa sentir a proteção de Deus sobre a sua casa, deite-se, apague as luzes e deixe a Palavra falar com você. São cerca de 40 minutos de oração para dormir, contra a ansiedade e o medo, terminando com a bênção e o Pai-Nosso, bem suave, para quem já adormeceu.

    🙏 Escreva AMÉM nos comentários e deixe o seu pedido de oração. Vamos orar por você, pela sua família e por cada nome que você escrever.

    🔔 Inscreva-se e ative o sininho para receber uma nova oração toda noite.

    CAPÍTULOS
    {chr(10).join(caps)}

    Leituras bíblicas em paráfrase própria baseada na tradução de João Ferreira de Almeida.

    CRÉDITOS DE IMAGEM
    {creditos.replace('Vídeos de stock: Pexels (pexels.com)', 'Vídeos de stock gratuitos do Pexels (pexels.com):')}

    {' '.join('#' + t.replace(' ', '') for t in ['oraçãodanoite', 'salmo91', 'oraçãoparadormir'])}
    """
SUF = "_v2" if V2 else ""
with open(f"out/descricao{SUF}.txt", "w", encoding="utf-8") as f:
    f.write("TÍTULO\n" + TITULO + "\n\nTÍTULOS ALTERNATIVOS\n" + "\n".join("- " + a for a in ALTERNATIVAS))
    f.write("\n\nTAGS (" + str(len(TAGS)) + ")\n" + ", ".join(TAGS) + "\n\n")
    f.write("=" * 60 + "\nDESCRIÇÃO (copiar daqui para baixo)\n" + "=" * 60 + "\n\n" + desc)

# ---------- thumbnails ----------
PF = "fonts/PlayfairDisplay[wght].ttf"
def fonte(size, var):
    f = ImageFont.truetype(PF, size); f.set_variation_by_name(var); return f

def frame(clip, t, path):
    if not os.path.exists(path):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", clip, "-frames:v", "1", path], check=True)
    return Image.open(path).convert("RGB")

def base(img, escurecer=0.55, quente=True):
    img = ImageOps.fit(img, (1280, 720), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(0.9)
    img = ImageEnhance.Brightness(img).enhance(escurecer)
    if quente:
        r, g, b = img.split()
        img = Image.merge("RGB", (r.point(lambda v: min(255, v * 1.12)), g.point(lambda v: v * 1.0), b.point(lambda v: v * 0.82)))
    return img

def vinheta(img, forca=0.75):
    m = Image.new("L", img.size, 0); d = ImageDraw.Draw(m)
    d.ellipse((-200, -160, img.width + 200, img.height + 160), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(160))
    preto = Image.new("RGB", img.size, (8, 5, 3))
    return Image.composite(img, Image.blend(img, preto, forca), m)

def texto_sombra(img, xy, txt, font, fill, anchor="la", sombra=10, stroke=0):
    s = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(s)
    ds.text((xy[0] + 4, xy[1] + 6), txt, font=font, fill=(0, 0, 0, 255), anchor=anchor, stroke_width=stroke + 4, stroke_fill=(0, 0, 0, 255))
    s = s.filter(ImageFilter.GaussianBlur(sombra))
    img.alpha_composite(s); img.alpha_composite(s)
    ImageDraw.Draw(img).text(xy, txt, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(40, 20, 5, 255))

def selo(img, xy, anchor_center=False):
    d = ImageDraw.Draw(img); f = fonte(30, "Bold"); txt = "ORAÇÃO DA NOITE"
    w = d.textlength(txt, font=f) + 44
    x, y = (xy[0] - w / 2, xy[1]) if anchor_center else xy
    d.rounded_rectangle((x, y, x + w, y + 54), 27, fill=(232, 182, 92, 255))
    d.text((x + w / 2, y + 27), txt, font=f, fill=(35, 20, 5, 255), anchor="mm")

cenas = json.load(open("cenas.json"))
def clip_da_tag(tag, n=0):
    ids = []
    for c in cenas:
        if c["clip"]["tag"] == tag and c["clip"]["id"] not in [i["id"] for i in ids]: ids.append(c["clip"])
    return ids[n % len(ids)]["arquivo_local"]

OURO, CREME = (246, 206, 120, 255), (255, 246, 228, 255)
if V2:
    img = vinheta(base(frame(clip_da_tag("luz_divina", 0), 3, "work/thumb/a_v2.png"), 0.62)).convert("RGBA")
    grad = Image.new("L", (1280, 720)); gd = ImageDraw.Draw(grad)
    for x in range(1280): gd.line((x, 0, x, 720), fill=int(max(0, 210 - x * 0.27)))
    img = Image.composite(Image.new("RGBA", img.size, (10, 6, 2, 255)), img, grad)
    selo(img, (60, 70))
    texto_sombra(img, (56, 145), "DURMA", fonte(178, "Black"), OURO)
    texto_sombra(img, (60, 345), "EM PAZ", fonte(150, "Black"), CREME)
    texto_sombra(img, (64, 560), "entregue tudo a Deus", fonte(58, "SemiBold"), CREME, sombra=6)
    img.convert("RGB").save("out/thumb_A_v2.jpg", quality=92)

    img = vinheta(base(frame(clip_da_tag("nascer_sol", 1), 3, "work/thumb/b_v2.png"), 0.6), 0.6).convert("RGBA")
    selo(img, (640, 48), anchor_center=True)
    texto_sombra(img, (640, 255), "DURMA EM PAZ", fonte(128, "Black"), OURO, anchor="mm", sombra=14)
    texto_sombra(img, (640, 440), "ENTREGUE TUDO A DEUS", fonte(76, "Black"), CREME, anchor="mm", sombra=12)
    d = ImageDraw.Draw(img); d.line((470, 545, 810, 545), fill=(246, 206, 120, 200), width=3)
    texto_sombra(img, (640, 600), "medo · contas · família · trabalho", fonte(42, "SemiBold"), CREME, anchor="mm", sombra=6)
    img.convert("RGB").save("out/thumb_B_v2.jpg", quality=92)
else:
    # A: raios de luz entre nuvens, texto à esquerda
    img = vinheta(base(frame(clip_da_tag("luz_divina", 0), 3, "work/thumb/a.png"), 0.62)).convert("RGBA")
    grad = Image.new("L", (1280, 720)); gd = ImageDraw.Draw(grad)
    for x in range(1280): gd.line((x, 0, x, 720), fill=int(max(0, 200 - x * 0.28)))
    img = Image.composite(Image.new("RGBA", img.size, (10, 6, 2, 255)), img, grad)
    selo(img, (60, 70))
    texto_sombra(img, (56, 150), "SALMO 91", fonte(178, "Black"), OURO)
    texto_sombra(img, (62, 365), "DURMA", fonte(122, "Black"), CREME)
    texto_sombra(img, (62, 500), "EM PAZ", fonte(122, "Black"), CREME)
    img.convert("RGB").save("out/thumb_A.jpg", quality=92)

    # B: nascer do sol dourado, texto centralizado
    img = vinheta(base(frame(clip_da_tag("nascer_sol", 1), 3, "work/thumb/b2.png"), 0.6), 0.6).convert("RGBA")
    selo(img, (640, 48), anchor_center=True)
    texto_sombra(img, (640, 250), "SALMO 91", fonte(190, "Black"), OURO, anchor="mm", sombra=14)
    texto_sombra(img, (640, 470), "DURMA EM PAZ", fonte(112, "Black"), CREME, anchor="mm", sombra=14)
    d = ImageDraw.Draw(img); d.line((470, 580, 810, 580), fill=(246, 206, 120, 200), width=3)
    texto_sombra(img, (640, 625), "Salmos 23 · 91 · 121", fonte(44, "SemiBold"), CREME, anchor="mm", sombra=6)
    img.convert("RGB").save("out/thumb_B.jpg", quality=92)

print("ok: out/legenda.srt, out/descricao.txt, out/thumb_A.jpg, out/thumb_B.jpg")
print("\n".join(caps))
