#!/usr/bin/env python3
"""Encodes every scene, mixes VO + music + synthesized SFX, and muxes the final video + .srt."""
import json, os, re, subprocess, sys, wave
from concurrent.futures import ThreadPoolExecutor
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__)); B = f"{ROOT}/build"; A = f"{ROOT}/assets"
TL = json.load(open(f"{B}/timeline.json")); FPS = TL["fps"]; SR = 48000
OUT = f"{ROOT}/out"; os.makedirs(OUT, exist_ok=True); os.makedirs(f"{B}/seg", exist_ok=True)
X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "50", "-an"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("FFMPEG FAILED\n" + " ".join(cmd) + "\n" + r.stderr[-1500:])


def probe(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def encode(s):
    out = f"{B}/seg/{s['id']}.mp4"; fr = f"{B}/frames/{s['id']}"; nf = s["nf"]
    if "takes" not in s:
        run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", f"{fr}/%05d.jpg", "-frames:v", str(nf)] + X264 + [out]); return out
    takes = s["takes"]; n = len(takes); cmd = ["ffmpeg", "-y", "-v", "error"]; fc = []
    for i, t in enumerate(takes):
        need = t["frames"] / FPS / t["slow"] + 0.4; real = "/real/" in t["src"]
        cmd += ["-ss", f"{t['ss']:.2f}", "-t", f"{need:.2f}", "-i", t["src"]]
        pre = "crop=iw:ih*0.755," if "city_pep_official" in t["src"] else ""
        grade = "eq=contrast=1.07:saturation=0.9:brightness=-0.03" if real else "eq=contrast=1.12:saturation=0.74:brightness=-0.06"
        if t.get("pillar"):
            fc.append(f"[{i}:v]crop=ih*0.70:ih,fps={FPS},split[pa][pb];[pa]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=28:4,eq=brightness=-0.22[pbg];"
                      f"[pb]scale=-2:1080[pfg];[pbg][pfg]overlay=(W-w)/2:0,setsar=1,format=yuv420p,trim=end_frame={t['frames']},setpts=PTS-STARTPTS[v{i}]")
            continue
        fc.append(f"[{i}:v]{pre}setpts={t['slow']:.4f}*(PTS-STARTPTS),fps={FPS},scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1,format=yuv420p,"
                  f"{grade},tpad=stop_mode=clone:stop_duration=30,trim=end_frame={t['frames']},setpts=PTS-STARTPTS[v{i}]")
    cmd += ["-framerate", str(FPS), "-i", f"{fr}/%05d.png"]
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,noise=alls=2:allf=t,vignette=PI/6[bg];[bg][{n}:v]overlay=0:0:format=auto[o]")
    run(cmd + ["-filter_complex", ";".join(fc), "-map", "[o]", "-frames:v", str(nf)] + X264 + [out]); return out


# ------------------------------------------------------------------ audio
def load(p, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", p] + (["-af", af] if af else []) + ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.check_output(cmd), dtype=np.float32).reshape(-1, 2).astype(np.float64)


rng = np.random.default_rng(7)
def env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-np.maximum(0, t - a) / r)

def lp(x, fc):  # one-pole low-pass (fc scalar or array)
    a = 1 - np.exp(-2 * np.pi * np.asarray(fc) / SR) * np.ones(len(x)); y = np.empty(len(x)); z = 0.0
    for i in range(len(x)):
        z += a[i] * (x[i] - z); y[i] = z
    return y

def sfx_whoosh(d=0.7, f0=300, f1=5000):
    n = int(d * SR); x = rng.standard_normal(n); f = f0 * (f1 / f0) ** np.linspace(0, 1, n)
    y = lp(x, f) - lp(x, f * 0.35); return y * np.hanning(n) ** 1.5 / np.abs(y).max()

def sfx_hit(d=1.4, f0=95, f1=36):
    n = int(d * SR); t = np.arange(n) / SR; ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 7)) / SR
    y = np.sin(ph) * np.exp(-t * 3.2) + 0.5 * lp(rng.standard_normal(n), 1800) * np.exp(-t * 38); return np.tanh(y * 2.2) / 1.0

def sfx_tick(f=2600, d=0.03):
    n = int(d * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * f * t) * np.exp(-t * 190)

def sfx_key():
    n = int(0.035 * SR); t = np.arange(n) / SR; return (lp(rng.standard_normal(n), 4200) * 2 + np.sin(2 * np.pi * 1700 * t) * .4) * np.exp(-t * 150)

def sfx_riser(d=2.4):
    n = int(d * SR); t = np.linspace(0, 1, n); x = rng.standard_normal(n); y = lp(x, 400 + 6000 * t ** 2) * 0.7 + 0.35 * np.sin(2 * np.pi * np.cumsum(140 + 900 * t ** 2) / SR)
    return y * t ** 2.2 / np.abs(y).max()

def sfx_thud():
    n = int(0.5 * SR); t = np.arange(n) / SR; return np.tanh((np.sin(2 * np.pi * 110 * t * (1 - t * .6)) * np.exp(-t * 14) + lp(rng.standard_normal(n), 2500) * np.exp(-t * 60)) * 2)

def sfx_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * (420 + 500 * np.exp(-t * 40)) * t) * np.exp(-t * 34)


def build_audio():
    N = int(TL["total"] * SR) + SR; vo = np.zeros((N, 2)); mus = np.zeros((N, 2)); fx = np.zeros((N, 2))
    def put(buf, x, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i < 0 or i >= N: return
        x = x[: N - i]
        if x.ndim == 1: x = np.stack([x * (1 - max(0, pan)), x * (1 + min(0, pan))], 1)
        buf[i:i + len(x)] += x * g
    for v in TL["vo"]:
        put(vo, load(f"{A}/vo/{v['file']}", "highpass=f=75,acompressor=threshold=-21dB:ratio=3:attack=6:release=140:makeup=2.5"), v["start"])
    vo *= 0.12 / np.sqrt((vo[np.abs(vo).sum(1) > 0.02] ** 2).mean())
    for s in TL["scenes"]:
        if s.get("nat"):
            x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(s["nat"]["ss"]), "-t", str(s["dur"]), "-i", s["nat"]["src"], "-af", "highpass=f=90,acompressor=threshold=-22dB:ratio=3:makeup=3,afade=t=in:d=0.15,afade=t=out:st=" + str(s["dur"] - 0.4) + ":d=0.4", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]), dtype=np.float32).reshape(-1, 2).astype(np.float64)
            put(vo, x * (0.11 / np.sqrt((x ** 2).mean() + 1e-9)), s["start"])
    # --- music runs (merge consecutive identical tracks)
    runs = []
    for m in TL["music"]:
        if runs and runs[-1][0] == m["track"]: continue
        runs.append([m["track"], max(0, m["start"])])
    tracks = {}
    for k, (name, t0) in enumerate(runs):
        t1 = runs[k + 1][1] if k + 1 < len(runs) else TL["total"]
        if name not in tracks:
            x = load(f"{A}/music/{name}.wav"); tracks[name] = x * (0.1 / np.sqrt((x ** 2).mean()))
        x = tracks[name]; a = int(max(0, t0 - 0.4) * SR); b = min(N, int((t1 + 1.6) * SR)); idx = np.arange(b - a) % len(x)
        seg = x[idx].copy(); fi = int(1.2 * SR); fo = int(2.0 * SR)
        seg[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2 if k else 1; seg[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
        mus[a:b] += seg
    # --- ducking under the voice
    p = (np.abs(vo).max(1) > 0.012).astype(np.float64); w = int(0.5 * SR); c = np.cumsum(np.concatenate([[0], p]))
    pres = np.clip((c[np.minimum(N, np.arange(N) + w)] - c[np.maximum(0, np.arange(N) - w)]) / w * 3, 0, 1)
    k = int(0.35 * SR); pres = np.convolve(pres, np.ones(k) / k, "same")
    gain = 0.62 - (0.62 - 0.17) * pres
    for s in TL["scenes"]:
        if s.get("mute_music"):
            a, b = int((s["start"] - 0.25) * SR), int((s["start"] + s["dur"] - 0.1) * SR); r = int(0.12 * SR)
            gain[a:b] *= np.concatenate([np.linspace(1, 0, r), np.zeros(b - a - 2 * r), np.linspace(0, 1, r)])
    mus *= gain[:, None]
    # --- sound design
    W, WS, HIT, BOOM, THUD, POP, RISE = sfx_whoosh(), sfx_whoosh(0.4, 900, 7000), sfx_hit(), sfx_hit(2.4, 80, 30), sfx_thud(), sfx_pop(), sfx_riser()
    for s in TL["scenes"]:
        g = s["gfx"]; t = s["start"]; D = s["dur"]; ty = g["type"]
        if ty == "sting":
            put(fx, RISE, t + 0.9 - 2.4, 0.5); put(fx, BOOM, t + 0.9, 0.95); put(fx, W, t + 0.2, 0.4); continue
        if ty == "bumper":
            put(fx, W, t - 0.15, 0.55, -0.4); put(fx, HIT, t + 0.5, 0.8); put(fx, WS, t + 0.45, 0.3, 0.4); continue
        if ty == "quote":
            for dt in (0.6, 2.7, 4.3): put(fx, HIT, t + dt, 0.3)
            continue
        if ty == "end": continue
        put(fx, WS, t - 0.1, 0.24)
        if ty == "counter":
            t0 = (g.get("t0") or 0.08) * D; t1 = t0 + min(2.4, D * 0.3)
            for q in np.arange(t0, t1, 0.055): put(fx, sfx_tick(2200 + 900 * (q - t0) / (t1 - t0)), t + q, 0.16)
            put(fx, HIT, t + t1, 0.5)
        elif ty == "list":
            n = len(g["items"]); t0 = g.get("t0") or 0.2
            for i in range(n): put(fx, POP, t + (g["ats"][i] if "ats" in g else t0 + (0.88 - t0) * i / n) * D, 0.4)
            if g.get("stamp"): put(fx, THUD, t + (g.get("stampat") or 0.7) * D, 0.9)
        elif ty == "define":
            put(fx, HIT, t + 0.3, 0.35)
            if g.get("stamp"): put(fx, THUD, t + D * 0.68, 0.9)
        elif ty == "terminal":
            n = len(g["lines"]); st = D * 0.78 / n
            for i in range(n):
                for q in np.arange(0, st * 0.7, 0.07): put(fx, sfx_key(), t + 0.4 + i * st + q + rng.uniform(0, 0.03), rng.uniform(0.18, 0.3))
        elif ty in ("bigtext",):
            put(fx, HIT, t + (g.get("late") or 0) * D + 0.15, 0.7 if g.get("bare") else 0.5)
        elif ty == "doc":
            put(fx, WS, t + D * 0.42, 0.4)
            if g.get("foot"): put(fx, HIT, t + D * 0.76, 0.4)
        elif ty == "pitch":
            t0 = (g.get("late") or 0.06) * D
            for i in range(len(g["parts"])): put(fx, W, t + t0 + i * min(2.2, D * 0.3) - 0.1, 0.45); put(fx, HIT, t + t0 + i * min(2.2, D * 0.3) + 0.35, 0.4)
        elif ty == "map":
            if g.get("route"): put(fx, W, t + (g.get("late") or 0.12) * D, 0.4); put(fx, POP, t + (g.get("late") or 0.12) * D + 1.5, 0.5)
            else:
                for i in range(len(g["pins"])): put(fx, POP, t + 0.5 + i * min(1.6, D * 0.16), 0.5)
            if g.get("shake"): put(fx, BOOM, t + 1.1, 0.7)
        elif ty in ("flow", "flow3", "org", "names", "bars", "icons", "trend", "chips"):
            k = {"flow": [0.22, 0.55], "bars": [i["at"] for i in g.get("items", []) if isinstance(i, dict) and "at" in i], "names": [0.3, 0.42, 0.74]}.get(ty)
            if ty == "icons": k = [(0.2 + i * 0.28) / D for i in range(g["count"])]
            if ty == "chips":
                n = len(g["items"]); t0 = g.get("t0") or 0.12; k = [t0 + i * (0.86 - t0) / n for i in range(n)]
            if ty == "flow3":
                t0 = g.get("late") or 0.08; st = min(1.6, D * 0.16) / D; k = [t0 + i * st for i in range(3)]
            if ty == "org": k = [(0.3 + i * 0.55) / D for i in range(len(g["nodes"]))]
            for q in (k or []): put(fx, POP, t + q * D, 0.4)
        elif ty in ("word", "stat", "lower"):
            t0 = (g.get("late") or 0.1) * D
            put(fx, THUD if g.get("stamp") else HIT, t + t0 + 0.1, 0.8 if g.get("stamp") else 0.38)
    mix = vo + mus + fx * 0.11
    fo = int(3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = np.tanh(mix * 2.2) / 2.2
    mix = mix[: int(TL["total"] * SR)]
    with wave.open(f"{B}/mix.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix * 3, -1, 1) * 32767).astype(np.int16).tobytes())


def srt():
    def ts(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    out = []; k = 1
    for s in TL["scenes"]:
        if "text" not in s: continue
        parts = [p.strip() for p in re.split(r"(?<=[.?!:])\s+|(?<=,)\s+(?=\S{0,}.{38,}$)", s["text"]) if p.strip()]
        chunks = []
        for p in parts:
            while len(p) > 84:
                c = p.rfind(" ", 0, 84); c2 = p.rfind(", ", 30, 84); c = c2 + 1 if c2 > 0 else c
                chunks.append(p[:c].strip()); p = p[c:].strip()
            chunks.append(p)
        a = s["vo0"]; b = s["start"] + s["dur"] - 0.25; tot = sum(len(c) + 8 for c in chunks); t = a
        for c in chunks:
            dt = (b - a) * (len(c) + 8) / tot
            if len(c) > 42:
                m = c.rfind(" ", 0, len(c) // 2 + 6); c = c[:m] + "\n" + c[m + 1:]
            out.append(f"{k}\n{ts(t)} --> {ts(t + dt - 0.05)}\n{c}\n"); k += 1; t += dt
    open(f"{OUT}/manchester-city-115-charges-EN.srt", "w").write("\n".join(out))


if __name__ == "__main__":
    only = sys.argv[1:]
    scenes = [s for s in TL["scenes"] if not only or s["id"] in only]
    with ThreadPoolExecutor(3) as ex:
        for i, o in enumerate(ex.map(encode, scenes)): print("seg", i + 1, len(scenes), flush=True)
    if only: sys.exit()
    open(f"{B}/concat.txt", "w").write("".join(f"file 'seg/{s['id']}.mp4'\n" for s in TL["scenes"]))
    print("audio…", flush=True); build_audio(); srt()
    final = f"{OUT}/manchester-city-115-charges-EN.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{B}/concat.txt", "-i", f"{B}/mix.wav", "-c:v", "copy",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", final])
    print("DONE", final, f"{os.path.getsize(final)/1e6:.0f} MB", probe(final))
