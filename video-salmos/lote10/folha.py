import json, sys
from PIL import Image, ImageDraw, ImageFont
cenas = json.load(open("cenas.json"))
import os
apr = set(json.load(open("lote10/aprovados.json"))) if os.path.exists("lote10/aprovados.json") and os.environ.get("SO_NOVOS") else set()
ids = [i for i in dict.fromkeys(c["clip"]["id"] for c in cenas) if i not in apr]
start, n = int(sys.argv[1]), int(sys.argv[2]); ids_p = ids[start:start + n]
cols, tw, th = 6, 320, 180
rows = (len(ids_p) + cols - 1) // cols
img = Image.new("RGB", (cols * tw, rows * (th + 22)), "black")
f = ImageFont.truetype("fonts/Inter[opsz,wght].ttf", 16)
d = ImageDraw.Draw(img)
for k, cid in enumerate(ids_p):
    import os, subprocess
    th_p = f"clips/thumbs/{cid}.jpg"
    if not os.path.exists(th_p) and os.path.exists(f"clips/{cid}.mp4"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2", "-i", f"clips/{cid}.mp4", "-frames:v", "1", "-vf", "scale=320:-2", th_p])
    try: t = Image.open(th_p).convert("RGB")
    except Exception: continue
    t = t.resize((tw, int(t.height * tw / t.width))).crop((0, 0, tw, th))
    x, y = (k % cols) * tw, (k // cols) * (th + 22)
    img.paste(t, (x, y)); tag = next(c["clip"]["tag"] for c in cenas if c["clip"]["id"] == cid)
    d.text((x + 4, y + th + 2), f"{start+k} {cid} {tag}", fill="white", font=f)
img.save(sys.argv[3]); print(len(ids), "clipes")
