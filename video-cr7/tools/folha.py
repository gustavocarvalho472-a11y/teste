import sys, glob, os
from PIL import Image, ImageDraw
d, pref = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(os.path.join(d, pref + "_*.jpg")))
W, cols = 400, 5; rows = (len(fs) + cols - 1) // cols
s = Image.new("RGB", (W * cols, rows * 250), "black"); dr = ImageDraw.Draw(s)
for k, f in enumerate(fs):
    im = Image.open(f); w, h = im.size; im.thumbnail((W - 6, 225))
    x, y = (k % cols) * W, (k // cols) * 250
    s.paste(im, (x + 3, y + 3)); dr.text((x + 5, y + 232), f"{os.path.basename(f)} {w}x{h}", fill="yellow")
os.makedirs(os.path.join(d, "_folhas"), exist_ok=True)
s.save(os.path.join(d, "_folhas", pref + ".jpg"), quality=75)
