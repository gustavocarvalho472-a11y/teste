#!/usr/bin/env python3
"""
Vídeo "Mozart for Deep Focus" (40 min).

Estrutura:
  0:00  intro: 2 clipes de vídeo + texto sobre o Efeito Mozart
  0:17  título + ciclo de imagens (60s cada, crossfade de 3s), repetido até o fim
  39:54 fade para preto

Visual: zoom/pan lento diferente por imagem, chuva animada no pavilhão, poeira
dourada flutuando, flicker de vela, tom quente e vinheta.
Áudio: mp3 repetido com crossfade + chuva suave de fundo + swell/impacto no título.

Para ser rápido, renderiza só UM ciclo (4 min) e repete com cópia de stream.
"""
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
A = HERE / "assets"
BUILD = HERE / "build"
OUT = HERE / "output" / "mozart_40min.mp4"

TOTAL = 40 * 60
FPS = 24
W, H = 1920, 1080
WW, WH = 2880, 1620          # resolução de trabalho do zoom (sem tremido)
SLOT, FADE = 60, 3           # segundos por imagem / crossfade
TITLE = "Mozart for Deep Focus"
SUBTITLE = "Classical Music for Study & Concentration"
CINZEL = A / "fonts" / "Cinzel.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

# imagem, movimento
SCENES = [
    ("01-pavilhao-chuva.webp", "zoom_out"),
    ("02-teatro.webp", "zoom_in"),
    ("03-close.webp", "pan"),
    ("05-corredor.webp", "zoom_in"),
]
CAPTIONS = [  # (início, fim, texto) sobre os clipes da intro
    (0.8, 5.8, "In 1993, researchers noticed something remarkable."),
    (6.3, 11.3, "A few minutes of Mozart seemed to sharpen the mind."),
    (11.8, 16.0, "They called it the Mozart Effect."),
]
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M",
       "-bufsize", "16M", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-r", str(FPS), "-g", str(FPS * 2), "-an"]


def run(cmd):
    print("+", " ".join(map(str, cmd))[:110], flush=True)
    subprocess.run(list(map(str, cmd)), check=True)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True,
                                check=True).stdout)


def textfile(s, name):
    """drawtext lê o texto de arquivo: evita problemas de escape (vírgula, dois-pontos)."""
    p = BUILD / f"{name}.txt"
    p.write_text(s)
    return p


# ------------------------------------------------------------------ overlays
def write_gray(path, frames_iter, size):
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                          "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-",
                          "-c:v", "ffv1", str(path)], stdin=subprocess.PIPE)
    for f in frames_iter:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    assert p.wait() == 0


def dust_frames(period=24, count=60, seed=3):
    """Poeira dourada; movimento periódico (loop sem pulo)."""
    rng = np.random.default_rng(seed)
    pw, ph, m = W // 2, H // 2, 20
    n = period * FPS
    parts = []
    for _ in range(count):
        big = rng.random() < 0.15
        s = rng.uniform(3.5, 5.5) if big else rng.uniform(0.6, 1.6)
        r = int(math.ceil(s * 3))
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        parts.append((np.exp(-(xx * xx + yy * yy) / (2 * s * s)).astype(np.float32),
                      rng.uniform(0, pw), rng.uniform(0, ph), rng.uniform(6, 30),
                      int(rng.integers(1, 3)), rng.uniform(0, 6.3), int(rng.integers(0, 2)),
                      rng.uniform(.08, .18) if big else rng.uniform(.3, .8),
                      int(rng.integers(1, 4)), rng.uniform(0, 6.3)))
    for i in range(n):
        ph_ = 2 * math.pi * i / n
        c = np.zeros((ph + 2 * m, pw + 2 * m), np.float32)
        for spr, x0, y0, ax, kx, px, rise, amp, kt, pt in parts:
            x = (x0 + ax * math.sin(kx * ph_ + px)) % pw
            y = (y0 - rise * ph * i / n) % ph
            b = amp * (0.55 + 0.45 * math.sin(kt * ph_ + pt))
            r = spr.shape[0] // 2
            xi, yi = int(x) + m, int(y) + m
            c[yi - r:yi + r + 1, xi - r:xi + r + 1] += spr * b
        yield np.clip(c[m:-m, m:-m] * 255, 0, 255).astype(np.uint8)


def rain_frames(period=2, count=380, seed=5):
    """Chuva: riscos verticais caindo, periódico em `period` segundos."""
    rng = np.random.default_rng(seed)
    pw, ph = W // 2, H // 2
    n = period * FPS
    drops = [(int(rng.integers(0, pw)), rng.uniform(0, ph), int(rng.integers(2, 5)),
              int(rng.integers(10, 28)), rng.uniform(.25, .7)) for _ in range(count)]
    for i in range(n):
        c = np.zeros((ph + 40, pw), np.float32)
        for x, y0, k, ln, b in drops:
            y = int((y0 + k * ph * i / n) % ph)
            c[y:y + ln, x] += b * np.linspace(0.2, 1, ln)
        yield np.clip(c[:ph] * 255, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ imagens
def prep(name, i):
    im = Image.open(A / "images" / name).convert("RGB")
    a = np.asarray(im).astype(np.float32).mean(axis=2)
    rows, cols = np.where(a.mean(1) > 6)[0], np.where(a.mean(0) > 6)[0]
    im = im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))  # tira tarja preta
    w, h = im.size
    if w / h > W / H:
        nw = round(h * W / H); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = round(w * H / W); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    p = BUILD / f"img{i}.png"
    im.resize((WW, WH), Image.LANCZOS).save(p)
    return p


def motion(kind, F):
    c = "x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
    if kind == "zoom_in":
        return f"z='1+0.14*on/{F}':{c}"
    if kind == "zoom_out":
        return f"z='1.14-0.14*on/{F}':{c}"
    return f"z=1.12:x='(iw-iw/zoom)*on/{F}':y='ih/2-ih/zoom/2'"  # pan esq->dir


def render_cycle(dust, rain):
    seq = SCENES + [SCENES[0]]           # termina na 1ª imagem -> loop perfeito
    C = SLOT + FADE
    F = C * FPS
    L = len(SCENES) * SLOT
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats"]
    for i, (name, _) in enumerate(seq):
        cmd += ["-loop", "1", "-framerate", FPS, "-t", C, "-i", prep(name, i)]
    nd = len(seq)
    cmd += ["-stream_loop", "-1", "-i", dust, "-stream_loop", "-1", "-i", rain]
    f = []
    for i, (name, kind) in enumerate(seq):
        f.append(f"[{i}:v]zoompan={motion(kind, F)}:d=1:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p,settb=1/{FPS}[z{i}]")
    # chuva só nas cenas do pavilhão (1ª e cópia final)
    rain_ids = [i for i, (n, _) in enumerate(seq) if "chuva" in n]
    f.append(f"[{nd + 1}:v]scale={W}:{H},gblur=sigma=0.8,format=yuv420p,split={len(rain_ids)}"
             + "".join(f"[r{i}]" for i in rain_ids))
    for i in rain_ids:
        f.append(f"[z{i}]format=gbrp[zb{i}];[r{i}]format=gbrp,trim=duration={C}[rb{i}];"
                 f"[zb{i}][rb{i}]blend=all_mode=screen:all_opacity=0.35,format=yuv420p,settb=1/{FPS}[z{i}r]")
    lbl = [f"z{i}r" if i in rain_ids else f"z{i}" for i in range(len(seq))]
    prev = lbl[0]
    for k in range(1, len(seq)):
        f.append(f"[{prev}][{lbl[k]}]xfade=transition=fade:duration={FADE}:offset={k * SLOT}[x{k}]")
        prev = f"x{k}"
    flick = f"0.010*sin(2*PI*t*97/{L})+0.006*sin(2*PI*t*151/{L})"
    f.append(f"[{prev}]trim=start={FADE}:duration={L},setpts=PTS-STARTPTS,"
             "colorbalance=rs=-0.02:bs=0.03:rh=0.05:bh=-0.05,"
             f"eq=contrast=1.05:saturation=1.06:brightness='{flick}':eval=frame,format=gbrp[base]")
    f.append(f"[{nd}:v]scale={W}:{H},gblur=sigma=1.2,format=rgb24,"
             "colorchannelmixer=rr=1:gg=0.8:bb=0.52,format=gbrp[dust]")
    f.append("[base][dust]blend=all_mode=screen,format=yuv420p,vignette=PI/4.5[v]")
    out = BUILD / "cycle.mp4"
    run(cmd + ["-filter_complex", ";".join(f), "-map", "[v]", "-t", L, *ENC, out])
    return out, L


def render_intro(dust):
    clips = sorted((A / "clips").glob("*.mp4"))
    d0 = dur(clips[0])
    total = d0 + dur(clips[1]) - 1
    f = [f"[{i}:v]scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1,format=yuv420p[c{i}]"
         for i in range(2)]
    f.append(f"[c0][c1]xfade=transition=fade:duration=1:offset={d0 - 1},"
             "colorbalance=rh=0.04:bh=-0.04,eq=contrast=1.04,format=gbrp[base]")
    f.append(f"[2:v]scale={W}:{H},gblur=sigma=1.2,format=rgb24,"
             "colorchannelmixer=rr=1:gg=0.8:bb=0.52,format=gbrp[dust]")
    txt = []
    for s, e, t in CAPTIONS:
        al = f"if(lt(t,{s}),0,if(lt(t,{s}+0.8),(t-{s})/0.8,if(lt(t,{e}-0.8),1,if(lt(t,{e}),({e}-t)/0.8,0))))"
        txt.append(f"drawtext=fontfile='{SERIF_IT}':textfile='{textfile(t, f'cap{s}')}':fontsize=54:fontcolor=0xF6EBD2"
                   f":x=(w-tw)/2:y=h*0.80:alpha='{al}':shadowcolor=black@0.7:shadowx=0:shadowy=3")
    f.append("[base][dust]blend=all_mode=screen,format=yuv420p,vignette=PI/4.5,"
             + ",".join(txt) + f",fade=in:d=1.5,fade=out:st={total - 1.2}:d=1.2[v]")
    out = BUILD / "intro.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", clips[0], "-i", clips[1],
         "-stream_loop", "-1", "-i", dust,
         "-filter_complex", ";".join(f), "-map", "[v]", "-t", total, *ENC, out])
    return out, total


def render_titled(cycle):
    al = "if(lt(t,1.5),0,if(lt(t,3.5),(t-1.5)/2,if(lt(t,9),1,if(lt(t,11),(11-t)/2,0))))"
    al2 = al.replace("1.5", "2.3").replace("3.5", "4.3")
    vf = ("fade=in:d=2.5,"
          f"drawtext=fontfile='{CINZEL}':textfile='{textfile(TITLE, 'title')}':fontsize=100:fontcolor=white"
          f":x=(w-tw)/2:y=(h-th)/2-40:alpha='{al}':shadowcolor=black@0.6:shadowy=4,"
          f"drawtext=fontfile='{CINZEL}':textfile='{textfile(SUBTITLE, 'subtitle')}':fontsize=38:fontcolor=0xF3E3C0"
          f":x=(w-tw)/2:y=h/2+50:alpha='{al2}':shadowcolor=black@0.6:shadowy=3")
    out = BUILD / "titled.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", cycle, "-vf", vf, *ENC, out])
    return out


def render_outro(cycle, length):
    out = BUILD / "outro.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", cycle, "-t", f"{length:.3f}",
         "-vf", f"fade=out:st={length - 6:.3f}:d=6", *ENC, out])
    return out


# ------------------------------------------------------------------ áudio
def render_audio(intro_len):
    mp3 = A / "audio" / "mozart_relaxante.mp3"
    music_len = 437.0                     # corta o silêncio do final do mp3
    xf = 4
    reps = math.ceil(TOTAL / (music_len - xf)) + 1
    # cada repetição é uma entrada separada (asplit + acrossfade encerra cedo)
    f = [f"[{i}:a]atrim=0:{music_len},afade=t=out:st={music_len - 1}:d=1,aresample=48000[m{i}]"
         for i in range(reps)]
    prev = "m0"
    for i in range(1, reps):
        f.append(f"[{prev}][m{i}]acrossfade=d={xf}[mx{i}]")
        prev = f"mx{i}"
    f.append(f"[{prev}]atrim=0:{TOTAL},afade=t=in:d=4,afade=t=out:st={TOTAL - 8}:d=8,"
             "aformat=channel_layouts=stereo[music]")
    # chuva suave: ruído rosa filtrado + leve oscilação
    f.append(f"anoisesrc=color=pink:r=48000:a=0.5:d={TOTAL},highpass=f=500,lowpass=f=6500,"
             "tremolo=f=0.15:d=0.3,volume=0.05,"
             f"afade=t=in:d=3,afade=t=out:st={TOTAL - 8}:d=8,aformat=channel_layouts=stereo[rain]")
    # swell de ar antes do título + impacto grave quando o título aparece
    t0 = intro_len
    f.append(f"anoisesrc=color=white:r=48000:a=0.4:d=5,bandpass=f=1800:w=1.5,"
             f"afade=t=in:d=4.2,afade=t=out:st=4.2:d=0.8,volume=0.35,"
             f"adelay={int((t0 - 4.5) * 1000)}|{int((t0 - 4.5) * 1000)},"
             "aformat=channel_layouts=stereo[swell]")
    f.append(f"sine=f=48:r=48000:d=4,volume='exp(-1.4*t)':eval=frame,volume=0.6,"
             f"aecho=0.8:0.6:120|260:0.35|0.2,adelay={int(t0 * 1000 + 1500)}|{int(t0 * 1000 + 1500)},"
             "aformat=channel_layouts=stereo[boom]")
    f.append("[music][rain][swell][boom]amix=inputs=4:normalize=0:duration=first,"
             "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    out = BUILD / "audio.m4a"
    run(["ffmpeg", "-y", "-v", "error", "-stats", *(["-i", mp3] * reps), "-filter_complex", ";".join(f),
         "-map", "[a]", "-t", TOTAL, "-c:a", "aac", "-b:a", "192k", out])
    return out


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.parent.mkdir(exist_ok=True)
    dust, rain = BUILD / "dust.mkv", BUILD / "rain.mkv"
    print("1/6 overlays (poeira, chuva)")
    write_gray(dust, dust_frames(), (W // 2, H // 2))
    write_gray(rain, rain_frames(), (W // 2, H // 2))
    print("2/6 intro")
    intro, il = render_intro(dust)
    print("3/6 ciclo de imagens")
    cycle, L = render_cycle(dust, rain)
    print("4/6 título + final")
    titled = render_titled(cycle)
    n = int((TOTAL - il - L) // L)        # ciclos inteiros depois do título
    rest = TOTAL - il - L - n * L
    if rest < 30:
        n -= 1; rest += L
    outro = render_outro(cycle, rest)
    print("5/6 áudio")
    audio = render_audio(il)
    print("6/6 montagem")
    lst = BUILD / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in [intro, titled] + [cycle] * n + [outro]))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio,
         "-map", "0:v", "-map", "1:a", "-c", "copy", "-t", TOTAL, "-movflags", "+faststart", OUT])
    print(f"pronto: {OUT} ({dur(OUT) / 60:.2f} min)")


if __name__ == "__main__":
    main()
