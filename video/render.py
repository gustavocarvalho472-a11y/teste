#!/usr/bin/env python3
"""
Renderizador de vídeos de música clássica no estilo "Classical Mind".

Estilo:
  - cada imagem fica ~10s na tela com zoom-in lento e contínuo (Ken Burns)
  - crossfade longo (~2s) entre as imagens
  - poeira/partículas douradas flutuando, flicker sutil de vela
  - grading quente (âmbar nas luzes, sombras levemente frias), vinheta forte, grão de filme
  - título em fonte serifada clássica (Cinzel) no início, fade in/out

Estratégia para vídeos longos (1-3h): renderiza UM loop perfeito (imagens 1..N -> 1)
e repete esse loop com cópia de stream (sem re-encode). Só a intro (com título) e a
outro (fade para preto) são re-encodadas. Um vídeo de 2h renderiza em poucos minutos.

Uso:
  python3 render.py --preview                       # prévia de ~1min40, sem áudio
  python3 render.py --audio musicas/*.mp3           # vídeo completo com a duração do áudio
  python3 render.py --audio a.mp3 b.mp3 --hz432 --title "Mozart for Deep Focus"
"""
import argparse
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
W, H = 1920, 1080
WORK_W, WORK_H = 3840, 2160  # zoompan em alta resolução para evitar tremido
# CRF com teto de bitrate: o grão de filme sozinho levaria a >100 Mbps.
# 12 Mbps é o recomendado pelo YouTube para 1080p (2h ~ 11 GB).
X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-maxrate", "12M", "-bufsize", "24M",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", None]


def run(cmd):
    print("+", " ".join(str(c) for c in cmd[:6]), "...", flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def x264(fps):
    return [str(fps) if a is None else a for a in X264]


# --------------------------------------------------------------------------- imagens
def prepare_images(src_dir, build):
    """Remove tarjas pretas, recorta para 16:9 e amplia para 4K."""
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    files = sorted(p for p in Path(src_dir).iterdir() if p.suffix.lower() in exts)
    if not files:
        sys.exit(f"Nenhuma imagem em {src_dir}")
    out = []
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        a = np.asarray(im).astype(np.float32).mean(axis=2)
        rows = np.where(a.mean(axis=1) > 6)[0]
        cols = np.where(a.mean(axis=0) > 6)[0]
        im = im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))  # tira letterbox
        w, h = im.size
        target = W / H
        if w / h > target:
            nw = round(h * target)
            im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = round(w / target)
            im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        im = im.resize((WORK_W, WORK_H), Image.LANCZOS)
        p = build / f"img{i:02d}.png"
        im.save(p)
        out.append(p)
        print(f"  imagem {i + 1}: {f.name}")
    return out


# --------------------------------------------------------------------------- partículas
def render_particles(path, length, fps, count, seed=7):
    """Poeira luminosa flutuando. Movimento periódico -> o loop não 'pula'."""
    rng = np.random.default_rng(seed)
    pw, ph = W // 2, H // 2
    frames = int(round(length * fps))

    def sprite(sigma):
        r = int(math.ceil(sigma * 3))
        y, x = np.mgrid[-r:r + 1, -r:r + 1]
        return np.exp(-(x * x + y * y) / (2 * sigma * sigma)).astype(np.float32)

    parts = []
    for _ in range(count):
        bokeh = rng.random() < 0.15
        sigma = rng.uniform(3.5, 6.0) if bokeh else rng.uniform(0.6, 1.8)
        parts.append(dict(
            spr=sprite(sigma),
            x0=rng.uniform(0, pw), y0=rng.uniform(0, ph),
            ax=rng.uniform(8, 40), kx=rng.integers(1, 4), px=rng.uniform(0, 2 * math.pi),
            rise=int(rng.integers(0, 2)),  # 0 = só balança, 1 = sobe uma tela por loop
            amp=rng.uniform(0.10, 0.22) if bokeh else rng.uniform(0.35, 0.9),
            kt=rng.integers(1, 6), pt=rng.uniform(0, 2 * math.pi),
        ))

    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray",
         "-s", f"{pw}x{ph}", "-r", str(fps), "-i", "-",
         "-c:v", "ffv1", str(path)], stdin=subprocess.PIPE)
    margin = 20
    for n in range(frames):
        ph_ = 2 * math.pi * n / frames  # fase do loop (0..2π)
        canvas = np.zeros((ph + 2 * margin, pw + 2 * margin), np.float32)
        for p in parts:
            x = (p["x0"] + p["ax"] * math.sin(p["kx"] * ph_ + p["px"])) % pw
            y = (p["y0"] - p["rise"] * ph * n / frames) % ph
            b = p["amp"] * (0.55 + 0.45 * math.sin(p["kt"] * ph_ + p["pt"]))
            s = p["spr"]
            r = s.shape[0] // 2
            xi, yi = int(x) + margin, int(y) + margin
            if r > margin:
                continue
            canvas[yi - r:yi + r + 1, xi - r:xi + r + 1] += s * b
        frame = np.clip(canvas[margin:-margin, margin:-margin] * 255, 0, 255).astype(np.uint8)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait():
        sys.exit("falha ao gerar partículas")


# --------------------------------------------------------------------------- loop
def render_loop(images, particles, out, a):
    n = len(images)
    S, D, fps = a.slot, a.fade, a.fps
    C = S + D
    L = n * S
    frames = int(round(C * fps))
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats"]
    seq = images + [images[0]]  # volta pra 1ª imagem -> loop perfeito
    for img in seq:
        cmd += ["-loop", "1", "-framerate", str(fps), "-t", f"{C}", "-i", img]
    cmd += ["-i", particles]
    pi = len(seq)

    z = a.zoom
    f = []
    for i in range(len(seq)):
        f.append(
            f"[{i}:v]zoompan=z='1+{z}*on/{frames}':d=1:s={W}x{H}:fps={fps}"
            f":x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2',setsar=1,format=yuv420p[c{i}]")
    prev = "c0"
    for k in range(1, len(seq)):
        f.append(f"[{prev}][c{k}]xfade=transition=fade:duration={D}:offset={k * S}[x{k}]")
        prev = f"x{k}"
    # recorta [D, D+L): começa e termina no mesmo quadro da imagem 1
    flick = (f"0.010*sin(2*PI*t*97/{L})+0.006*sin(2*PI*t*151/{L})"
             f"+0.004*sin(2*PI*t*53/{L})")
    f.append(
        f"[{prev}]trim=start={D}:duration={L},setpts=PTS-STARTPTS,"
        f"colorbalance=rs=-0.03:bs=0.04:rm=0.03:bm=-0.02:rh=0.05:gh=0.01:bh=-0.05,"
        f"eq=contrast=1.06:saturation=1.08:brightness='{flick}':eval=frame,"
        f"format=gbrp[base]")
    f.append(
        f"[{pi}:v]scale={W}:{H}:flags=bicubic,gblur=sigma=1.2,format=rgb24,"
        f"colorchannelmixer=rr=1:gg=0.80:bb=0.52,format=gbrp[dust]")
    f.append(
        "[base][dust]blend=all_mode=screen,format=yuv420p,"
        "vignette=angle=PI/4.2,noise=alls=4:allf=t,format=yuv420p[v]")
    cmd += ["-filter_complex", ";".join(f), "-map", "[v]", "-t", f"{L}",
            *x264(fps), "-g", str(fps * 2), "-an", out]
    run(cmd)
    return L


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def render_intro(loop, out, a):
    font = HERE / "assets" / "fonts" / "Cinzel.ttf"
    alpha = "if(lt(t,1.5),0,if(lt(t,3.5),(t-1.5)/2,if(lt(t,9.5),1,if(lt(t,11.5),(11.5-t)/2,0))))"
    alpha2 = "if(lt(t,2.5),0,if(lt(t,4.5),(t-2.5)/2,if(lt(t,9.5),1,if(lt(t,11.5),(11.5-t)/2,0))))"
    vf = [
        "fade=in:st=0:d=3",
        f"drawtext=fontfile='{font}':text='{esc(a.title)}':fontsize=104:fontcolor=white"
        f":x=(w-tw)/2:y=(h-th)/2-40:alpha='{alpha}'"
        ":shadowcolor=black@0.55:shadowx=0:shadowy=4",
    ]
    if a.subtitle:
        vf.append(
            f"drawtext=fontfile='{font}':text='{esc(a.subtitle)}':fontsize=40"
            f":fontcolor=0xF3E3C0:x=(w-tw)/2:y=(h/2)+50:alpha='{alpha2}'"
            ":shadowcolor=black@0.55:shadowx=0:shadowy=3")
    run(["ffmpeg", "-y", "-v", "error", "-stats", "-i", loop, "-vf", ",".join(vf),
         *x264(a.fps), "-g", str(a.fps * 2), "-an", out])


def render_outro(loop, out, length, a):
    run(["ffmpeg", "-y", "-v", "error", "-stats", "-stream_loop", "2", "-i", loop,
         "-t", f"{length:.3f}", "-vf", f"fade=out:st={max(0, length - 5):.3f}:d=5",
         *x264(a.fps), "-g", str(a.fps * 2), "-an", out])


# --------------------------------------------------------------------------- áudio
def build_audio(files, out, a):
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats"]
    for f in files:
        cmd += ["-i", f]
    chain = "".join(f"[{i}:a]" for i in range(len(files)))
    chain += f"concat=n={len(files)}:v=0:a=1,aresample=48000"
    if a.hz432:  # afina 440 -> 432 Hz sem mudar o andamento
        chain += ",asetrate=48000*432/440,aresample=48000,atempo=440/432"
    chain += ",loudnorm=I=-18:TP=-1.5:LRA=11,aresample=48000[a]"
    cmd += ["-filter_complex", chain, "-map", "[a]", "-c:a", "pcm_s16le", out]
    run(cmd)
    dur = probe_duration(out)
    final = out.with_suffix(".m4a")
    run(["ffmpeg", "-y", "-v", "error", "-i", out, "-af",
         f"afade=in:d=2,afade=out:st={max(0, dur - 5):.3f}:d=5",
         "-c:a", "aac", "-b:a", "256k", final])
    return final, dur


def tracklist(files, a):
    t = 0.0
    lines = []
    for f in files:
        h, rem = divmod(int(t), 3600)
        m, s = divmod(rem, 60)
        stamp = f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        name = Path(f).stem.replace("_", " ")
        lines.append(f"{stamp} {name}")
        t += probe_duration(f)  # atempo mantém a duração mesmo em 432 Hz
    return "\n".join(lines)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", default=HERE / "assets" / "images")
    ap.add_argument("--audio", nargs="*", default=[], help="faixas na ordem (mp3/wav/flac)")
    ap.add_argument("--title", default="Mozart for Deep Focus")
    ap.add_argument("--subtitle", default="Classical Music for Study & Concentration")
    ap.add_argument("--slot", type=float, default=10, help="segundos por imagem")
    ap.add_argument("--fade", type=float, default=2, help="duração do crossfade")
    ap.add_argument("--zoom", type=float, default=0.10, help="zoom total por imagem (0.10 = 10%%)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--particles", type=int, default=70)
    ap.add_argument("--hz432", action="store_true", help="afinar áudio em 432 Hz")
    ap.add_argument("--preview", action="store_true", help="só intro + 1 loop, sem áudio")
    ap.add_argument("--reuse", action="store_true",
                    help="reaproveita build/loop.mp4 (troca só música/título, bem mais rápido)")
    ap.add_argument("--out", default=HERE / "output" / "video.mp4")
    ap.add_argument("--build", default=HERE / "build")
    a = ap.parse_args()

    build = Path(a.build)
    build.mkdir(parents=True, exist_ok=True)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    loop = build / "loop.mp4"
    if a.reuse and loop.exists():
        print("1-3/5 reaproveitando loop existente")
        L = probe_duration(loop)
    else:
        print("1/5 preparando imagens")
        imgs = prepare_images(a.images, build)
        L = len(imgs) * a.slot
        print(f"2/5 partículas ({L:.0f}s)")
        parts = build / "particles.mkv"
        render_particles(parts, L, a.fps, a.particles)
        print("3/5 loop principal")
        render_loop(imgs, parts, loop, a)
    print("4/5 intro com título")
    intro = build / "intro.mp4"
    render_intro(loop, intro, a)

    concat = build / "concat.txt"
    if a.preview or not a.audio:
        if not a.preview:
            print("  (sem --audio: gerando só a prévia)")
        out = out.with_name("preview.mp4")
        concat.write_text(f"file '{intro}'\nfile '{loop}'\n")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat,
             "-c", "copy", "-movflags", "+faststart", out])
        print(f"\nPrévia: {out}")
        return

    print("5/5 áudio + montagem final")
    audio, dur = build_audio(a.audio, build / "audio.wav", a)
    loops = max(1, int((dur - 6) // L))  # intro conta como 1º loop
    rest = dur - loops * L               # outro fica entre 6s e L+6s
    outro = build / "outro.mp4"
    render_outro(loop, outro, rest, a)
    lines = [f"file '{intro}'"] + [f"file '{loop}'"] * (loops - 1) + [f"file '{outro}'"]
    concat.write_text("\n".join(lines) + "\n")
    run(["ffmpeg", "-y", "-v", "error", "-stats", "-f", "concat", "-safe", "0", "-i", concat,
         "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy",
         "-movflags", "+faststart", "-t", f"{dur:.3f}", out])
    tl = tracklist(a.audio, a)
    (out.with_suffix(".tracklist.txt")).write_text(tl + "\n")
    print(f"\nVídeo: {out}  ({dur / 60:.1f} min)\nTracklist (capítulos do YouTube):\n{tl}")


if __name__ == "__main__":
    main()
