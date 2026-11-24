#!/usr/bin/env python3
"""Face finder for framing: face_box(image_or_video, t) -> (cx, cy, h) normalised 0..1 of the largest face, or None. Cached in build/faces.json."""
import json, os, subprocess, sys
import cv2, numpy as np
ROOT = os.path.dirname(os.path.abspath(__file__)); CACHE = f"{ROOT}/build/faces.json"
_c = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
D = cv2.data.haarcascades
FRONT = cv2.CascadeClassifier(D + "haarcascade_frontalface_default.xml"); ALT = cv2.CascadeClassifier(D + "haarcascade_frontalface_alt2.xml")
PROF = cv2.CascadeClassifier(D + "haarcascade_profileface.xml")
def _frame(src, t, crop=""):
    if src.endswith((".jpg", ".png")) and not crop: return cv2.imread(src)
    vf = (crop or "") + "scale=960:-2"
    raw = subprocess.run(["ffmpeg", "-v", "error"] + ([] if src.endswith((".jpg", ".png")) else ["-ss", f"{t:.2f}"]) + ["-i", src, "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR) if raw else None
def face_box(src, t=0.0, crop=""):
    key = f"{os.path.basename(src)}|{t:.1f}|{crop}"
    if key in _c: return _c[key]
    img = _frame(src, t, crop); res = None
    if img is not None:
        H, W = img.shape[:2]; g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)); mn = max(24, int(min(W, H) * 0.06))
        found = []
        for cas, flip in ((FRONT, False), (ALT, False), (PROF, False), (PROF, True)):
            gg = cv2.flip(g, 1) if flip else g
            for (x, y, w, h) in cas.detectMultiScale(gg, 1.1, 6, minSize=(mn, mn)):
                if flip: x = W - x - w
                found.append((w * h, x, y, w, h))
        if found:
            _, x, y, w, h = max(found)
            res = [round(float(x + w / 2) / W, 3), round(float(y + h / 2) / H, 3), round(float(h) / H, 3)]
    _c[key] = res; return res
def save(): os.makedirs(os.path.dirname(CACHE), exist_ok=True); json.dump(_c, open(CACHE, "w"))
if __name__ == "__main__":
    for p in sys.argv[1:]: print(p, face_box(p))
    save()
