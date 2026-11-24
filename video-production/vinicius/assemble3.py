#!/usr/bin/env python3
"""v3 assembler — smooth camera. Every shot is moved with a sub-pixel affine warp (OpenCV) instead of ffmpeg's
integer crop, so slow zooms/pans glide instead of stepping ("tremido"). Moves follow an ease-in-out sine curve;
overlays fade in with an ease-out cubic glide. Frames are piped raw into ffmpeg, which adds grain, vignette,
the overlays and the fades. Usage: BUILD=build/v3 python3 assemble3.py [--reuse] [scene ids…]"""
import json, math, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np, cv2
os.environ.setdefault("BUILD", "build/v3")
import assemble2 as A2          # audio mix, srt and helpers are shared with v2
import camera
cv2.setNumThreads(2)
ROOT = os.path.dirname(os.path.abspath(__file__)); B = A2.B; TL = A2.TL; FPS = TL["fps"]; W, H = 1920, 1080
X264 = ["-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "50", "-an"]
REUSE = "--reuse" in sys.argv
os.makedirs(f"{B}/seg", exist_ok=True)

def ease(p):                     # camera: slow in, slow out (sine)
    p = min(1.0, max(0.0, p)); return 0.5 - 0.5 * math.cos(math.pi * p)

def grade(img, g):
    if g == "none": return img
    if g == "bw":
        y = cv2.convertScaleAbs(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), alpha=1.18, beta=128 * (1 - 1.18) - 4)
        return cv2.cvtColor(y, cv2.COLOR_GRAY2BGR)
    img = cv2.convertScaleAbs(img, alpha=1.07, beta=128 * (1 - 1.07) - 4)                      # contrast, a touch darker
    gray = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    img = cv2.addWeighted(img, 0.82, gray, 0.18, 0)                                              # saturation 82%
    return cv2.add(img, (-3, 0, 4, 0))                                                           # slightly warm

def safe_px(shape, safe):
    h, w = shape[:2]; sw, sh, sx, sy = safe or (1, 1, 0, 0)
    x, y = int(round(w * sx)), int(round(h * sy)); cw, ch = int(w * sw) // 2 * 2, int(h * sh) // 2 * 2
    return x, y, min(cw, w - x), min(ch, h - y)

class Mover:
    """affine for frame i of a shot: scale S = s0*z(t), focus point placed at (frx, fry) of the screen, clamped to the picture."""
    def __init__(self, sh, cw, ch):
        self.sh, self.cw, self.ch = sh, cw, ch; self.s0 = max(W / cw, H / ch); self.n = max(1, sh["frames"] - 1)
        zmax = max(sh.get("z0", 1), sh.get("z1", 1)); smax = self.s0 * zmax
        self.pre = min(1.0, smax * 1.15)          # big sources are reduced once (area filter) so the warp never minifies hard
    def M(self, i):
        sh = self.sh; p = ease(i / self.n)
        z = sh.get("z0", 1) + (sh.get("z1", 1) - sh.get("z0", 1)) * p
        fx = sh.get("fx0", .5) + (sh.get("fx1", .5) - sh.get("fx0", .5)) * p; fy = sh.get("fy0", .5) + (sh.get("fy1", .5) - sh.get("fy0", .5)) * p
        S = self.s0 * z; Wz, Hz = self.cw * S, self.ch * S
        x = min(max(fx * Wz - sh.get("frx", .5) * W, 0), Wz - W); y = min(max(fy * Hz - sh.get("fry", .5) * H, 0), Hz - H)
        k = S / self.pre
        return np.float32([[k, 0, -x], [0, k, -y]])

def warp(src, M): return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT101)

def frames_photo(sh):
    img = cv2.imread(sh["src"]); x, y, cw, ch = safe_px(img.shape, sh.get("safe")); img = img[y:y + ch, x:x + cw]
    mv = Mover(sh, cw, ch)
    if mv.pre < 1: img = cv2.resize(img, (round(cw * mv.pre), round(ch * mv.pre)), interpolation=cv2.INTER_AREA)
    img = grade(img, sh.get("grade", "color"))
    for i in range(sh["frames"]): yield warp(img, mv.M(i))

def frames_plate(sh):
    st = []
    for t0, f in sh["states"]:
        im = cv2.imread(f); st.append((t0, im))
    ch, cw = st[0][1].shape[:2]; mv = Mover(sh, cw, ch)
    if mv.pre < 1: st = [(t0, cv2.resize(im, (round(cw * mv.pre), round(ch * mv.pre)), interpolation=cv2.INTER_AREA)) for t0, im in st]
    for i in range(sh["frames"]):
        t = i / FPS; cur = st[0][1]
        for t0, im in st[1:]:
            a = (t - t0) / 0.35
            if a >= 1: cur = im
            elif a > 0: cur = cv2.addWeighted(cur, 1 - ease(a), im, ease(a), 0)
        yield warp(cur, mv.M(i))

def frames_video(sh):
    src = sh["src"]; vw, vh = camera.size(src); x, y, cw, ch = safe_px((vh, vw), sh.get("safe"))
    slow = sh.get("slow", 1.0); need = sh["frames"] / FPS / slow + 0.6
    if sh.get("pillar"):
        vf = f"{sh['pillar']},fps={FPS},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:4,eq=brightness=-0.25[bg];[b]scale=-2:{H}[fg];[bg][fg]overlay=(W-w)/2:0"
        cw, ch = W, H; sh = {**sh, "z0": 1, "z1": 1.03, "fx0": .5, "fx1": .5, "fy0": .5, "fy1": .5}
    else:
        vf = f"setpts={slow:.4f}*(PTS-STARTPTS),fps={FPS},crop={cw}:{ch}:{x}:{y}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{sh['ss']:.2f}", "-t", f"{need:.2f}", "-i", src, "-filter_complex" if sh.get("pillar") else "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    mv = Mover(sh, cw, ch); size = cw * ch * 3; last = None
    for i in range(sh["frames"]):
        buf = p.stdout.read(size)
        if len(buf) == size: last = grade(np.frombuffer(buf, np.uint8).reshape(ch, cw, 3), sh.get("grade", "color"))
        if last is None: last = np.zeros((ch, cw, 3), np.uint8)
        yield warp(last, mv.M(i))
    p.stdout.close(); p.wait()

def shot_frames(sh):
    return {"photo": frames_photo, "plate": frames_plate, "video": frames_video}[sh["kind"]](sh)

GLIDE = {"_l3.png": 18, "_slate.png": 10, "_score.png": 10, "_cta.png": 14}
def encode(s):
    out = f"{B}/seg/{s['id']}.mp4"; nf = s["nf"]; D = nf / FPS
    if REUSE and os.path.exists(out) and os.path.getsize(out) > 1000: return out
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]; fc = []
    plate = all(x["kind"] == "plate" for x in s["shots"])
    fc.append("[0:v]format=yuv420p,noise=c0s=3:c0f=t" + ("" if plate else ",vignette=angle=PI/5") + "[b0]"); cur = "[b0]"
    for j, o in enumerate(s["ovs"]):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{D + 0.2:.2f}", "-i", o["file"]]
        sub = o["file"].endswith("_sub.png"); fd = 0.14 if sub else 0.45; t0, t1 = o["t0"], o["t1"]
        fo = f",fade=t=out:st={max(t0, t1 - fd):.2f}:d={fd}:alpha=1" if t1 < D - 0.05 else ""
        g = next((v for k, v in GLIDE.items() if o["file"].endswith(k)), 0)
        y = f"'{g}*pow(max(0\\,1-(t-{t0:.2f})/0.7)\\,3)'" if g else "0"         # ease-out cubic glide into place
        fc.append(f"[{j + 1}:v]format=rgba,fade=t=in:st={t0:.2f}:d={fd}:alpha=1{fo}[o{j}];{cur}[o{j}]overlay=x=0:y={y}:eval=frame:enable='between(t,{t0:.2f},{t1:.2f})':format=auto[b{j + 1}]")
        cur = f"[b{j + 1}]"
    fades = []
    if s.get("fin"): fades.append(f"fade=t=in:st=0:d={s['fin']}")
    if s.get("fout"): fades.append(f"fade=t=out:st={D - s['fout']:.2f}:d={s['fout']}")
    fc.append(f"{cur}{','.join(fades) or 'null'},format=yuv420p[o]")
    p = subprocess.Popen(cmd + ["-filter_complex", ";".join(fc), "-map", "[o]", "-frames:v", str(nf)] + X264 + [out], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    n = 0
    try:
        for sh in s["shots"]:
            for fr in shot_frames(sh):
                if n >= nf: break
                p.stdin.write(np.ascontiguousarray(fr).tobytes()); n += 1
        while n < nf: p.stdin.write(fr.tobytes()); n += 1
        p.stdin.close()
    except BrokenPipeError: pass
    err = p.stderr.read().decode()[-1500:]; p.wait()
    if p.returncode: raise RuntimeError(f"{s['id']}: {err}")
    return out

if __name__ == "__main__":
    only = [x for x in sys.argv[1:] if not x.startswith("--")]
    scenes = [s for s in TL["scenes"] if not only or s["id"] in only]
    with ProcessPoolExecutor(int(os.environ.get("JOBS", 3))) as ex:
        for i, o in enumerate(ex.map(encode, scenes)): print("seg", i + 1, len(scenes), flush=True)
    if only: sys.exit()
    open(f"{B}/concat.txt", "w").write("".join(f"file 'seg/{s['id']}.mp4'\n" for s in TL["scenes"]))
    print("audio…", flush=True); A2.build_audio(); A2.srt()
    final = f"{A2.OUT}/{TL['name']}.mp4"
    A2.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{B}/concat.txt", "-i", f"{B}/mix.wav", "-c:v", "copy",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", final])
    print("DONE", final, f"{os.path.getsize(final) / 1e6:.0f} MB")
