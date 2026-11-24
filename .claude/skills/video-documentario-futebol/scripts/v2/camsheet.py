#!/usr/bin/env python3
"""Camera plan check: one tile per shot = clean source frame, white box = framing at the start, lime box = at the end,
red dot = detected face. Writes build/v2/camera_<n>.jpg (36 tiles per page). Usage: python3 camsheet.py [scene ids…]"""
import json, os, subprocess, sys
import cv2, numpy as np
import camera
ROOT = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(ROOT, os.environ.get("BUILD", "build/v2"))
TL = json.load(open(f"{B}/timeline.json")); only = sys.argv[1:]
tiles = []
def rect(sh, P):
    cw, ch, s0 = camera.cover(sh); BW, BH = cw * s0, ch * s0
    z = sh["z0"] + (sh["z1"] - sh["z0"]) * P; fx = sh["fx0"] + (sh["fx1"] - sh["fx0"]) * P; fy = sh["fy0"] + (sh["fy1"] - sh["fy0"]) * P
    Wz, Hz = BW * z, BH * z; x = min(max(fx * Wz - sh["frx"] * 1920, 0), Wz - 1920); y = min(max(fy * Hz - sh["fry"] * 1080, 0), Hz - 1080)
    return x / Wz, y / Hz, 1920 / Wz, 1080 / Hz
for s in TL["scenes"]:
    if only and s["id"] not in only: continue
    for sh in s["shots"]:
        if sh["kind"] == "plate" or sh.get("pillar"): continue
        vf = camera.safe_crop(sh) + "scale=480:270:force_original_aspect_ratio=decrease"
        cmd = ["ffmpeg", "-v", "error"] + ([] if sh["kind"] == "photo" else ["-ss", f"{sh['ss'] + 0.2:.2f}"]) + ["-i", sh["src"], "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"]
        img = cv2.imdecode(np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.uint8), cv2.IMREAD_COLOR)
        if img is None: continue
        h, w = img.shape[:2]; can = np.zeros((290, 480, 3), np.uint8); can[:h, :w] = img
        for P, col in ((0, (255, 255, 255)), (1, (0, 255, 198))):
            x, y, rw, rh = rect(sh, P); cv2.rectangle(can, (int(x * w), int(y * h)), (int((x + rw) * w) - 1, int((y + rh) * h) - 1), col, 2)
        for f in (sh.get("face0"), sh.get("face1")):
            if f: cv2.circle(can, (int(f[0] * w), int(f[1] * h)), 5, (40, 40, 255), -1)
        lab = f"{s['id']} {os.path.basename(sh['src'])[:14]} {sh.get('ss', 0):.0f} z{sh['z0']:.2f}>{sh['z1']:.2f}"
        cv2.putText(can, lab, (4, 284), 0, 0.42, (0, 255, 198), 1); tiles.append(can)
for p in range(0, len(tiles), 36):
    page = tiles[p:p + 36]
    while len(page) % 6: page.append(np.zeros_like(tiles[0]))
    cv2.imwrite(f"{B}/camera_{p // 36}.jpg", np.vstack([np.hstack(page[i:i + 6]) for i in range(0, len(page), 6)]), [cv2.IMWRITE_JPEG_QUALITY, 80])
print(len(tiles), "shots,", (len(tiles) + 35) // 36, "pages")
