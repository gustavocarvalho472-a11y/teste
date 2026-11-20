"""Folha de revisão em resolução maior (quadro de cada clipe aos 3 s), 4 colunas de 480 px.
Uso: folha_hd.py cenas.json inicio n saida.jpg"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
cenas = json.load(open(sys.argv[1])); ini, n, saida = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
ids = list(dict.fromkeys(c["clip"]["id"] for c in cenas))[ini:ini + n]
tags = {c["clip"]["id"]: c["clip"]["tag"] for c in cenas}
cols, tw, th = 4, 480, 270
os.makedirs("work/hd", exist_ok=True)
img = Image.new("RGB", (cols * tw, ((len(ids) + cols - 1) // cols) * (th + 24)), "black")
d = ImageDraw.Draw(img); f = ImageFont.truetype("fonts/Inter[opsz,wght].ttf", 18)
for k, cid in enumerate(ids):
    p = f"work/hd/{cid}.jpg"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "3", "-i", f"clips/{cid}.mp4", "-frames:v", "1",
                        "-vf", f"scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th}", p])
    try: t = Image.open(p)
    except Exception: continue
    x, y = (k % cols) * tw, (k // cols) * (th + 24)
    img.paste(t, (x, y)); d.text((x + 4, y + th + 2), f"{ini + k} {cid} {tags[cid]}", fill="white", font=f)
img.save(saida, quality=85); print(len(ids), "clipes")
