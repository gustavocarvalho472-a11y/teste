#!/usr/bin/env python3
"""v2 assembler ('Cinema + Revista'): shots with face-framed camera moves + plates + fading overlays, film grain,
quiet sound design, VO/nat/music mix with ducking, loudnorm -14 LUFS, .srt.
Usage: python3 assemble2.py [--reuse] [scene ids…]  (reads build/v2/timeline.json, writes out/<name>.mp4)"""
import json, os, re, subprocess, sys, wave
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import camera

ROOT = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(ROOT, os.environ.get("BUILD", "build/v2")); A = f"{ROOT}/assets"
TL = json.load(open(f"{B}/timeline.json")); FPS = TL["fps"]; SR = 48000; NAME = TL["name"]
OUT = f"{ROOT}/out"; os.makedirs(OUT, exist_ok=True); os.makedirs(f"{B}/seg", exist_ok=True)
X264 = ["-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "50", "-an"]
REUSE = "--reuse" in sys.argv

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit("FFMPEG FAILED\n" + " ".join(cmd) + "\n" + r.stderr[-2500:])

def shot_chain(k, sh, idx):
    """returns (input args, filter text producing [v{k}])"""
    F = sh["frames"]; D = F / FPS; tail = f"setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=6,trim=end_frame={F},setpts=PTS-STARTPTS[v{k}]"
    grade = camera.GRADE[sh.get("grade", "color")]
    if sh["kind"] == "plate":
        args = []; fc = []
        for j, (t0, f) in enumerate(sh["states"]):
            args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{D + 0.3:.2f}", "-i", f]
        n0 = idx; cur = f"[{n0}:v]fps={FPS},format=rgb24[s{k}_0]"; fc.append(cur); last = f"[s{k}_0]"
        for j, (t0, f) in enumerate(sh["states"][1:], 1):
            fc.append(f"[{n0 + j}:v]fps={FPS},format=rgba,fade=t=in:st={t0:.2f}:d=0.35:alpha=1[s{k}_{j}a];{last}[s{k}_{j}a]overlay=0:0:format=auto[s{k}_{j}]"); last = f"[s{k}_{j}]"
        fc.append(f"{last}{camera.move_chain(sh)},{tail}")
        return args, ";".join(fc), len(sh["states"])
    if sh["kind"] == "photo":
        args = ["-loop", "1", "-framerate", str(FPS), "-t", f"{D + 0.3:.2f}", "-i", sh["src"]]
        return args, f"[{idx}:v]fps={FPS},{camera.safe_crop(sh)}{camera.move_chain(sh)},{grade},{tail}", 1
    need = F / FPS / sh.get("slow", 1) + 0.6
    args = ["-ss", f"{sh['ss']:.2f}", "-t", f"{need:.2f}", "-i", sh["src"]]
    if sh.get("pillar"):   # square/vertical source: blurred fill + sharp centre, slow breathe
        return args, (f"[{idx}:v]{sh['pillar']},fps={FPS},split[pa{k}][pb{k}];[pa{k}]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=28:4,eq=brightness=-0.25[pbg{k}];"
                      f"[pb{k}]scale=-2:1080[pfg{k}];[pbg{k}][pfg{k}]overlay=(W-w)/2:0,{grade},{tail}"), 1
    return args, f"[{idx}:v]setpts={sh.get('slow', 1):.4f}*(PTS-STARTPTS),fps={FPS},{camera.safe_crop(sh)}{camera.move_chain(sh)},{grade},{tail}", 1

def encode(s):
    out = f"{B}/seg/{s['id']}.mp4"; nf = s["nf"]; D = nf / FPS
    if REUSE and os.path.exists(out) and os.path.getsize(out) > 1000: return out
    cmd = ["ffmpeg", "-y", "-v", "error"]; fc = []; idx = 0
    for k, sh in enumerate(s["shots"]):
        a, f, used = shot_chain(k, sh, idx); cmd += a; fc.append(f); idx += used
    n = len(s["shots"]); plate = all(x["kind"] == "plate" for x in s["shots"])
    look = "noise=c0s=3:c0f=t" + ("" if plate else ",vignette=angle=PI/5")
    fc.append("".join(f"[v{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=0,{look}[b0]")
    cur = "[b0]"
    for j, o in enumerate(s["ovs"]):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{D + 0.2:.2f}", "-i", o["file"]]
        sub = o["file"].endswith(("_sub.png",)); fd = 0.12 if sub else 0.4; t0, t1 = o["t0"], o["t1"]
        fo = f",fade=t=out:st={max(t0, t1 - fd):.2f}:d={fd}:alpha=1" if t1 < D - 0.05 else ""
        fc.append(f"[{idx}:v]format=rgba,fade=t=in:st={t0:.2f}:d={fd}:alpha=1{fo}[o{j}];{cur}[o{j}]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})':format=auto[b{j + 1}]")
        cur = f"[b{j + 1}]"; idx += 1
    fades = []
    if s.get("fin"): fades.append(f"fade=t=in:st=0:d={s['fin']}")
    if s.get("fout"): fades.append(f"fade=t=out:st={D - s['fout']:.2f}:d={s['fout']}")
    fc.append(f"{cur}{','.join(fades) or 'null'},format=yuv420p[o]")
    run(cmd + ["-filter_complex", ";".join(fc), "-map", "[o]", "-frames:v", str(nf)] + X264 + [out]); return out

# ------------------------------------------------------------------ audio
def load(p, af=None, ss=None, t=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + (["-t", str(t)] if t else []) + ["-i", p] + (["-af", af] if af else []) + ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.check_output(cmd), dtype=np.float32).reshape(-1, 2).astype(np.float64)
rng = np.random.default_rng(7)
def lp(x, fc):
    a = 1 - np.exp(-2 * np.pi * np.asarray(fc) / SR) * np.ones(len(x)); y = np.empty(len(x)); z = 0.0
    for i in range(len(x)): z += a[i] * (x[i] - z); y[i] = z
    return y
def whoosh(d=0.8, f0=250, f1=3800):
    n = int(d * SR); x = rng.standard_normal(n); f = f0 * (f1 / f0) ** np.linspace(0, 1, n); y = lp(x, f) - lp(x, f * 0.35)
    return y * np.hanning(n) ** 1.5 / np.abs(y).max()
def boom(d=2.6, f0=70, f1=28):
    n = int(d * SR); t = np.arange(n) / SR; ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 5)) / SR
    return np.tanh((np.sin(ph) * np.exp(-t * 2.2) + 0.3 * lp(rng.standard_normal(n), 900) * np.exp(-t * 20)) * 1.8)
def riser(d=2.2):
    n = int(d * SR); t = np.linspace(0, 1, n); y = lp(rng.standard_normal(n), 300 + 4000 * t ** 2) * 0.8; return y * t ** 2.4 / np.abs(y).max()
def tick():
    n = int(0.05 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 120) * 0.6

def build_audio():
    N = int(TL["total"] * SR) + SR; vo = np.zeros((N, 2)); mus = np.zeros((N, 2)); fx = np.zeros((N, 2))
    def put(buf, x, t, g=1.0):
        i = int(t * SR)
        if i < 0 or i >= N: return
        x = x[: N - i]
        if x.ndim == 1: x = np.stack([x, x], 1)
        buf[i:i + len(x)] += x * g
    for v in TL["vo"]:
        put(vo, load(f"{A}/vo/{v['file']}", "highpass=f=75,acompressor=threshold=-21dB:ratio=3:attack=6:release=140:makeup=2.5"), v["start"])
    vo *= 0.12 / np.sqrt((vo[np.abs(vo).sum(1) > 0.02] ** 2).mean())
    for s in TL["scenes"]:
        if s.get("nat"):
            x = load(s["nat"]["src"], f"highpass=f=90,acompressor=threshold=-22dB:ratio=3:makeup=3,afade=t=in:d=0.12,afade=t=out:st={s['dur'] - 0.35}:d=0.35", s["nat"]["ss"], s["dur"])
            put(vo, x * (0.11 / np.sqrt((x ** 2).mean() + 1e-9)), s["start"])
    runs = []
    for m in TL["music"]:
        if runs and runs[-1][0] == m["track"]: continue
        runs.append([m["track"], max(0, m["start"])])
    tracks = {}
    for k, (name, t0) in enumerate(runs):
        t1 = runs[k + 1][1] if k + 1 < len(runs) else TL["total"]
        if name not in tracks:
            x = load(f"{A}/music/{name}.wav"); tracks[name] = x * (0.085 / np.sqrt((x ** 2).mean()))
        x = tracks[name]; a = int(max(0, t0 - 0.4) * SR); b = min(N, int((t1 + 1.8) * SR)); idx = np.arange(b - a) % len(x)
        seg = x[idx].copy(); fi = int(1.4 * SR); fo = int(2.2 * SR)
        if k: seg[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2
        seg[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2; mus[a:b] += seg
    p = (np.abs(vo).max(1) > 0.012).astype(np.float64); w = int(0.5 * SR); c = np.cumsum(np.concatenate([[0], p]))
    pres = np.clip((c[np.minimum(N, np.arange(N) + w)] - c[np.maximum(0, np.arange(N) - w)]) / w * 3, 0, 1)
    k = int(0.4 * SR); pres = np.convolve(pres, np.ones(k) / k, "same")
    mus *= (0.6 - (0.6 - 0.15) * pres)[:, None]
    W, BM, RS, TK = whoosh(), boom(), riser(), tick()
    for s in TL["scenes"]:
        for name, dt in s.get("sfx", []):
            t = s["start"] + dt
            if name == "whoosh": put(fx, W, t - 0.25, 0.32)
            elif name == "boom": put(fx, BM, t + 0.05, 0.55); put(fx, W, t - 0.35, 0.25)
            elif name == "title": put(fx, RS, t - 2.1, 0.4); put(fx, BM, t + 0.05, 0.8)
            elif name == "hit": put(fx, BM, t + 0.05, 0.65)
            elif name == "tick": put(fx, TK, t + 0.1, 0.35)
    mix = vo + mus + fx * 0.14
    fo = int(3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = np.tanh(mix * 2.2) / 2.2; mix = mix[: int(TL["total"] * SR)]
    with wave.open(f"{B}/mix.wav", "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(mix * 3, -1, 1) * 32767).astype(np.int16).tobytes())

def srt():
    def ts(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    out = []; k = 1
    for s in TL["scenes"]:
        if "text" not in s: continue
        parts = [p.strip() for p in re.split(r"(?<=[.?!:])\s+", s["text"]) if p.strip()]; chunks = []
        for p in parts:
            while len(p) > 84:
                c = p.rfind(" ", 0, 84); c2 = p.rfind(", ", 30, 84); c = c2 + 1 if c2 > 0 else c
                chunks.append(p[:c].strip()); p = p[c:].strip()
            chunks.append(p)
        a = s["vo0"]; b = s["vo0"] + s["vod"]; tot = sum(len(c) + 8 for c in chunks); t = a
        for c in chunks:
            dt = (b - a) * (len(c) + 8) / tot
            if len(c) > 42: m = c.rfind(" ", 0, len(c) // 2 + 6); c = c[:m] + "\n" + c[m + 1:]
            out.append(f"{k}\n{ts(t)} --> {ts(t + dt - 0.05)}\n{c}\n"); k += 1; t += dt
    open(f"{OUT}/{NAME}.srt", "w").write("\n".join(out))

if __name__ == "__main__":
    only = [x for x in sys.argv[1:] if not x.startswith("--")]
    scenes = [s for s in TL["scenes"] if not only or s["id"] in only]
    with ThreadPoolExecutor(int(os.environ.get("JOBS", 3))) as ex:
        for i, o in enumerate(ex.map(encode, scenes)): print("seg", i + 1, len(scenes), flush=True)
    if only: sys.exit()
    open(f"{B}/concat.txt", "w").write("".join(f"file 'seg/{s['id']}.mp4'\n" for s in TL["scenes"]))
    print("audio…", flush=True); build_audio(); srt()
    final = f"{OUT}/{NAME}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{B}/concat.txt", "-i", f"{B}/mix.wav", "-c:v", "copy",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", final])
    print("DONE", final, f"{os.path.getsize(final) / 1e6:.0f} MB")
