#!/usr/bin/env python3
"""
Renderizador de vídeos longos de música clássica (estilo "Classical Mind").

Tudo vem de um arquivo de configuração JSON (veja config.example.json):
  python3 make_video.py config.json              # vídeo completo + QA
  python3 make_video.py config.json --preview    # prévia de 2 min em 720p (<25 MB)
  python3 make_video.py config.json --qa-only    # só refaz a checagem do vídeo pronto

Estrutura do vídeo:
  intro (clipes de vídeo + legendas)  ->  seção dinâmica com título (zoom in/out
  marcado, troca a cada ~12s)  ->  ciclo calmo (60s por imagem) repetido por
  cópia de stream até o fim  ->  fade para preto.

Economia de tempo/tokens embutida:
  - cada etapa é guardada em cache pelo hash dos seus parâmetros: mudar só
    título ou música não re-renderiza imagens;
  - log do ffmpeg vai para build/ffmpeg.log; na tela só aparecem as fases;
  - ao final gera build/qa.jpg (mosaico de quadros-chave) e um resumo de
    durações, silêncios e loudness por trecho.
"""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SKILL = Path(__file__).resolve().parent.parent
W, H, FPS = 1920, 1080, 24
WW, WH = 2880, 1620                  # resolução de trabalho do zoom (sem tremido)
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M",
       "-bufsize", "16M", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-r", str(FPS), "-g", str(FPS * 2), "-an"]
MID = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p",
       "-r", str(FPS), "-g", str(FPS), "-an"]          # intermediários
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
GRADE = "colorbalance=rs=-0.02:bs=0.03:rh=0.05:bh=-0.05"
DUST_TINT = "colorchannelmixer=rr=1:gg=0.8:bb=0.52"

BUILD = LOG = None


# ------------------------------------------------------------------ utilitários
def run(cmd):
    """Roda ffmpeg com log em arquivo; em erro mostra só o fim do log."""
    cmd = list(map(str, cmd))
    with open(LOG, "a") as lf:
        lf.write("\n$ " + " ".join(cmd)[:2000] + "\n")
        lf.flush()
        r = subprocess.run(cmd, stdout=lf, stderr=lf)
    if r.returncode:
        tail = LOG.read_text().splitlines()[-15:]
        sys.exit("ERRO no ffmpeg (fim de build/ffmpeg.log):\n" + "\n".join(tail))


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True,
                                check=True).stdout)


def key(*parts):
    return hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:10]


def cached(name, k, fn):
    """Executa fn(out) só se o arquivo com esse hash ainda não existe."""
    out = BUILD / f"{name}_{k}.mp4"
    if out.exists():
        print(f"   (cache) {name}")
    else:
        fn(out)
    return out


def textfile(s, name):
    p = BUILD / f"{name}.txt"      # drawtext via arquivo: sem problema de escape
    p.write_text(s)
    return p


# ------------------------------------------------------------------ overlays
def write_gray(path, frames):
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                          "-s", f"{W // 2}x{H // 2}", "-r", str(FPS), "-i", "-",
                          "-c:v", "ffv1", str(path)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    assert p.wait() == 0


def dust_frames(period=24, count=60, seed=3):
    """Poeira dourada com movimento periódico (loop sem pulo)."""
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
        a = 2 * math.pi * i / n
        c = np.zeros((ph + 2 * m, pw + 2 * m), np.float32)
        for spr, x0, y0, ax, kx, px, rise, amp, kt, pt in parts:
            x = (x0 + ax * math.sin(kx * a + px)) % pw
            y = (y0 - rise * ph * i / n) % ph
            b = amp * (0.55 + 0.45 * math.sin(kt * a + pt))
            r = spr.shape[0] // 2
            xi, yi = int(x) + m, int(y) + m
            c[yi - r:yi + r + 1, xi - r:xi + r + 1] += spr * b
        yield np.clip(c[m:-m, m:-m] * 255, 0, 255).astype(np.uint8)


def rain_frames(period=2, count=380, seed=5):
    """Chuva: riscos verticais, periódico em `period` segundos."""
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
def prep(path):
    """Remove tarja preta, recorta 16:9 e amplia para a resolução de trabalho."""
    out = BUILD / f"img_{key(str(path), Path(path).stat().st_mtime)}.png"
    if out.exists():
        return out
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.float32).mean(axis=2)
    rows, cols = np.where(a.mean(1) > 6)[0], np.where(a.mean(0) > 6)[0]
    im = im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
    w, h = im.size
    if w / h > W / H:
        nw = round(h * W / H); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = round(w * H / W); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im.resize((WW, WH), Image.LANCZOS).save(out)
    return out


def scene_clip(sc, frames, zoom_expr, rain, out):
    """Um clipe de uma imagem com zoom (e chuva opcional), em arquivo intermediário."""
    cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", FPS, "-i", prep(sc["image"])]
    zp = f"zoompan={zoom_expr}:d=1:s={W}x{H}:fps={FPS},setsar=1"
    if sc.get("rain"):
        cmd += ["-stream_loop", "-1", "-i", rain, "-filter_complex",
                f"[0:v]{zp},format=gbrp[a];[1:v]scale={W}:{H},gblur=sigma=0.8,format=gbrp[r];"
                "[a][r]blend=all_mode=screen:all_opacity=0.35,format=yuv420p[v]", "-map", "[v]"]
    else:
        cmd += ["-vf", f"{zp},format=yuv420p"]
    run(cmd + ["-frames:v", frames, *MID, out])


def chain(clips, slot_f, fade_f, last_full, out):
    """Emenda clipes com crossfade, sem abrir todos de uma vez (evita falta de memória):
    corpo de cada clipe + transição de `fade_f` quadros renderizada à parte."""
    tmp = out.with_suffix("")
    tmp.mkdir(exist_ok=True)
    pieces, n, cf = [], len(clips), slot_f + fade_f
    for k, c in enumerate(clips):
        a = 0 if k == 0 else fade_f
        b = cf if (k == n - 1 and last_full) else slot_f
        if b > a:
            body = tmp / f"body{k:03d}.mp4"
            run(["ffmpeg", "-y", "-v", "error", "-i", c, "-vf",
                 f"trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS", *MID, body])
            pieces.append(body)
        if k < n - 1:
            tr = tmp / f"trans{k:03d}.mp4"
            run(["ffmpeg", "-y", "-v", "error", "-i", c, "-i", clips[k + 1], "-filter_complex",
                 f"[0:v]trim=start_frame={slot_f}:end_frame={cf},setpts=PTS-STARTPTS[a];"
                 f"[1:v]trim=end_frame={fade_f},setpts=PTS-STARTPTS[b];"
                 f"[a][b]xfade=transition=fade:duration={fade_f / FPS}:offset=0[v]",
                 "-map", "[v]", *MID, tr])
            pieces.append(tr)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in pieces))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])


def finish(seq, dust, extra_vf, length, out, period=None):
    """Passada final: grading, flicker de vela, poeira, vinheta (+ título/fades)."""
    p = period or 240
    flick = f"0.010*sin(2*PI*t*97/{p})+0.006*sin(2*PI*t*151/{p})"
    f = (f"[0:v]{GRADE},eq=contrast=1.05:saturation=1.06:brightness='{flick}':eval=frame,"
         f"format=gbrp[base];[1:v]scale={W}:{H},gblur=sigma=1.2,format=rgb24,{DUST_TINT},"
         "format=gbrp[dust];[base][dust]blend=all_mode=screen:shortest=1,format=yuv420p,"
         "vignette=PI/4.5" + (f",{extra_vf}" if extra_vf else "") + "[v]")
    run(["ffmpeg", "-y", "-v", "error", "-i", seq, "-stream_loop", "-1", "-i", dust,
         "-filter_complex", f, "-map", "[v]", "-t", f"{length:.3f}", *ENC, out])


# ------------------------------------------------------------------ seções
def motion(kind, F, zoom, target):
    dx, dy = target
    ease = f"(on/{F})*(on/{F})*(3-2*on/{F})"
    if kind == "pan":
        return f"z={1 + zoom * 0.8:.3f}:x='(iw-iw/zoom)*on/{F}':y='ih/2-ih/zoom/2'"
    e = ease if kind == "zoom_in" else f"(1-{ease})"
    return (f"z='1+{zoom}*{e}':x='iw*(0.5+{dx}*{e})-iw/zoom/2'"
            f":y='ih*(0.5+{dy}*{e})-ih/zoom/2'")


def render_intro(cfg, dust, out):
    it = cfg["intro"]
    clips = [cfg["_dir"] / c for c in it["clips"]]
    d = [dur(c) for c in clips]
    xf = 1.0
    total = sum(d) - xf * (len(clips) - 1)
    f = [f"[{i}:v]scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1,format=yuv420p,settb=1/{FPS}[c{i}]"
         for i in range(len(clips))]
    prev, off = "c0", 0.0
    for i in range(1, len(clips)):
        off += d[i - 1] - xf
        f.append(f"[{prev}][c{i}]xfade=transition=fade:duration={xf}:offset={off:.3f}[i{i}]")
        prev = f"i{i}"
    txt = []
    for n, (s, e, t) in enumerate(it.get("captions", [])):
        al = f"if(lt(t,{s}),0,if(lt(t,{s}+0.8),(t-{s})/0.8,if(lt(t,{e}-0.8),1,if(lt(t,{e}),({e}-t)/0.8,0))))"
        txt.append(f"drawtext=fontfile='{SERIF_IT}':textfile='{textfile(t, f'cap{n}')}'"
                   f":fontsize=54:fontcolor=0xF6EBD2:x=(w-tw)/2:y=h*0.80:alpha='{al}'"
                   ":shadowcolor=black@0.7:shadowx=0:shadowy=3")
    k = len(clips)
    f.append(f"[{prev}]{GRADE},format=gbrp[base];[{k}:v]scale={W}:{H},gblur=sigma=1.2,"
             f"format=rgb24,{DUST_TINT},format=gbrp[dust];[base][dust]blend=all_mode=screen:shortest=1,"
             "format=yuv420p,vignette=PI/4.5" + "".join("," + t for t in txt)
             + f",fade=in:d=1.5,fade=out:st={total - 1.2:.3f}:d=1.2[v]")
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for c in clips:
        cmd += ["-i", c]
    run(cmd + ["-stream_loop", "-1", "-i", dust, "-filter_complex", ";".join(f), "-map", "[v]",
               "-t", f"{total:.3f}", *ENC, out])


def title_vf(cfg):
    font = SKILL / "assets" / "Cinzel.ttf"
    al = "if(lt(t,1.5),0,if(lt(t,3.5),(t-1.5)/2,if(lt(t,9),1,if(lt(t,11),(11-t)/2,0))))"
    al2 = al.replace("1.5", "2.3").replace("3.5", "4.3")
    vf = (f"drawtext=fontfile='{font}':textfile='{textfile(cfg['title'], 'title')}':fontsize=100"
          f":fontcolor=white:x=(w-tw)/2:y=(h-th)/2-40:alpha='{al}':shadowcolor=black@0.6:shadowy=4")
    if cfg.get("subtitle"):
        vf += (f",drawtext=fontfile='{font}':textfile='{textfile(cfg['subtitle'], 'subtitle')}'"
               f":fontsize=38:fontcolor=0xF3E3C0:x=(w-tw)/2:y=h/2+50:alpha='{al2}'"
               ":shadowcolor=black@0.6:shadowy=3")
    return vf


def render_dynamic(cfg, dust, rain, length, out):
    dy = cfg["dynamic"]
    slot_f, fade_f = round(dy["slot"] * FPS), round(dy["fade"] * FPS)
    n = max(1, round((length * FPS - fade_f) / slot_f))
    slot_f = round((length * FPS - fade_f) / n)          # fecha exato no tempo pedido
    cf = slot_f + fade_f
    scenes = cfg["scenes"]
    clips = []
    for k in range(n):
        sc = scenes[k % len(scenes)]
        zin = (k + k // len(scenes)) % 2 == 0           # alterna in/out a cada volta
        expr = motion("zoom_in" if zin else "zoom_out", cf, dy["zoom"], sc.get("target", [0, 0]))
        c = BUILD / f"dclip_{key(sc, expr, cf)}.mp4"
        if not c.exists():
            scene_clip(sc, cf, expr, rain, c)
        clips.append(c)
    seq = out.with_name(out.stem + "_seq.mp4")
    chain(clips, slot_f, fade_f, True, seq)
    L = (n * slot_f + fade_f) / FPS
    finish(seq, dust, f"fade=in:d=2.5,{title_vf(cfg)},fade=out:st={L - 0.8:.3f}:d=0.8", L, out,
           period=97 / 0.4)


def render_cycle(cfg, dust, rain, out):
    """Um ciclo calmo que termina exatamente no quadro em que começa (loop perfeito)."""
    cy = cfg["cycle"]
    slot_f, fade_f = round(cy["slot"] * FPS), round(cy["fade"] * FPS)
    cf = slot_f + fade_f
    scenes = cfg["scenes"]
    clips = []
    for sc in scenes + [scenes[0]]:
        expr = motion(sc.get("motion", "zoom_in"), cf, cy["zoom"], sc.get("target", [0, 0]))
        c = BUILD / f"cclip_{key(sc, expr, cf)}.mp4"
        if not c.exists():
            scene_clip(sc, cf, expr, rain, c)
        clips.append(c)
    seq = out.with_name(out.stem + "_seq.mp4")
    chain(clips, slot_f, fade_f, False, seq)
    L = len(scenes) * slot_f / FPS
    # recorta a partir do fim da 1ª transição: início e fim no mesmo quadro
    trimmed = out.with_name(out.stem + "_trim.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", seq, "-vf",
         f"trim=start_frame={fade_f}:end_frame={fade_f + len(scenes) * slot_f},setpts=PTS-STARTPTS",
         *MID, trimmed])
    finish(trimmed, dust, "", L, out, period=L)


# ------------------------------------------------------------------ áudio
def render_audio(cfg, total, title_at, out):
    xf = 4
    inputs, f, parts = [], [], []
    t = 0.0
    for pi, a in enumerate(cfg["audio"]):
        path = cfg["_dir"] / a["file"]
        a0 = a.get("start", 0.0)
        a1 = a.get("end") or dur(path)
        until = min(total, a.get("until_min", 1e9) * 60)
        seg = a1 - a0
        need = until - t + 8
        reps = math.ceil(need / (seg - xf)) + 1
        labels = []
        for r in range(reps):                       # cada repetição = entrada separada
            idx = len(inputs) // 2
            inputs += ["-i", path]
            f.append(f"[{idx}:a]atrim={a0}:{a1},asetpts=PTS-STARTPTS,afade=t=out:st={seg - 1}:d=1,"
                     f"aresample=48000,aformat=channel_layouts=stereo[p{pi}r{r}]")
            labels.append(f"p{pi}r{r}")
        prev = labels[0]
        for r, lb in enumerate(labels[1:], 1):
            f.append(f"[{prev}][{lb}]acrossfade=d={xf}[p{pi}x{r}]")
            prev = f"p{pi}x{r}"
        f.append(f"[{prev}]atrim=0:{need:.3f},loudnorm=I=-16:TP=-2:LRA=11,aresample=48000[part{pi}]")
        parts.append((f"part{pi}", until))
        t = until
        if until >= total:
            break
    prev = parts[0][0]
    for k in range(1, len(parts)):
        f.append(f"[{prev}]atrim=0:{parts[k - 1][1] + 3:.3f}[pre{k}];[pre{k}][{parts[k][0]}]"
                 f"acrossfade=d=6[mix{k}]")
        prev = f"mix{k}"
    f.append(f"[{prev}]atrim=0:{total:.3f},afade=t=in:d=4,afade=t=out:st={total - 8:.3f}:d=8[music]")
    mix = ["[music]"]
    sd = cfg.get("sound_design", {})
    if sd.get("rain", True):
        f.append(f"anoisesrc=color=pink:r=48000:a=0.5:d={total:.3f},highpass=f=500,lowpass=f=6500,"
                 "tremolo=f=0.15:d=0.3,volume=0.05,"
                 f"afade=t=in:d=3,afade=t=out:st={total - 8:.3f}:d=8,aformat=channel_layouts=stereo[rain]")
        mix.append("[rain]")
    if sd.get("title_hit", True) and title_at > 5:
        ms = int((title_at - 4.5) * 1000)
        f.append("anoisesrc=color=white:r=48000:a=0.4:d=5,bandpass=f=1800:w=1.5,afade=t=in:d=4.2,"
                 f"afade=t=out:st=4.2:d=0.8,volume=0.35,adelay={ms}|{ms},aformat=channel_layouts=stereo[swell]")
        ms = int(title_at * 1000 + 1500)
        f.append("sine=f=48:r=48000:d=4,volume='exp(-1.4*t)':eval=frame,volume=0.6,"
                 f"aecho=0.8:0.6:120|260:0.35|0.2,adelay={ms}|{ms},aformat=channel_layouts=stereo[boom]")
        mix += ["[swell]", "[boom]"]
    f.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,"
             "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(f),
         "-map", "[a]", "-t", f"{total:.3f}", "-c:a", "aac", "-b:a", "192k", out])


# ------------------------------------------------------------------ QA
def qa(video, marks):
    """Resumo objetivo + mosaico de quadros-chave numa única imagem."""
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    print("QA durações (tipo,seg):", " | ".join(out.split()))
    an = subprocess.run(["ffmpeg", "-i", str(video), "-vn", "-af",
                         "silencedetect=n=-40dB:d=1,ebur128", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    sil = [l.split("]")[-1].strip() for l in an.splitlines() if "silence_start" in l]
    loud = [l.strip() for l in an.splitlines() if l.strip().startswith("I:")]
    print("QA silêncios >1s:", sil[:5] or "nenhum", "| loudness:", loud[-1] if loud else "?")
    marks = [m for m in marks if m < dur(video)][:9]
    tiles = []
    for i, t in enumerate(marks):
        p = BUILD / f"qa{i}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                        "-frames:v", "1", "-vf", f"scale=480:-1,drawtext=fontfile='{SERIF_IT}'"
                        f":text='{int(t // 60)}m{t % 60:04.1f}s':x=8:y=8:fontsize=22:fontcolor=yellow", str(p)])
        tiles.append(p)
    while len(tiles) % 3:
        tiles.append(tiles[-1])
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in tiles:
        cmd += ["-i", str(p)]
    rows = len(tiles) // 3
    lay = "|".join(f"{c * 480}_{r * 270}" for r in range(rows) for c in range(3))
    subprocess.run(cmd + ["-filter_complex", f"xstack=inputs={len(tiles)}:layout={lay}",
                          str(BUILD / "qa.jpg")])
    print(f"QA mosaico: {BUILD / 'qa.jpg'}  (marcas: {', '.join(f'{m:.0f}s' for m in marks)})")


# ------------------------------------------------------------------ main
def main():
    global BUILD, LOG
    cfg_path = Path(sys.argv[1]).resolve()
    cfg = json.loads(cfg_path.read_text())
    cfg["_dir"] = cfg_path.parent
    for sc in cfg["scenes"]:
        sc["image"] = str(cfg["_dir"] / sc["image"])
    preview = "--preview" in sys.argv
    BUILD = cfg["_dir"] / cfg.get("build_dir", "build")
    BUILD.mkdir(exist_ok=True)
    LOG = BUILD / "ffmpeg.log"
    out = cfg["_dir"] / cfg.get("output", "output/video.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    total = cfg["total_min"] * 60
    if preview:
        total = min(total, 120)
        out = out.with_name(out.stem + "_preview_full.mp4")
    if "--qa-only" in sys.argv:
        qa(out, [5, 30, 60, 120, 299.5, 300.5, total / 2, total - 3])
        return

    print("1/6 overlays")
    dust, rain = BUILD / "dust.mkv", BUILD / "rain.mkv"
    if not dust.exists():
        write_gray(dust, dust_frames())
    if not rain.exists():
        write_gray(rain, rain_frames())

    print("2/6 intro")
    il = 0.0
    segs = []
    if cfg.get("intro"):
        intro = cached("intro", key(cfg["intro"]), lambda o: render_intro(cfg, dust, o))
        il = dur(intro)
        segs.append(intro)

    print("3/6 ciclo calmo")
    cyc_key = key(cfg["scenes"], cfg["cycle"])
    cycle = cached("cycle", cyc_key, lambda o: render_cycle(cfg, dust, rain, o))
    L = dur(cycle)

    print("4/6 seção dinâmica + título")
    dyn_end = min(total - 30, cfg["dynamic"]["until_min"] * 60) if cfg.get("dynamic") else il
    dl = 0.0
    if cfg.get("dynamic") and dyn_end > il + 20:
        dk = key(cfg["scenes"], cfg["dynamic"], cfg["title"], cfg.get("subtitle"), round(dyn_end - il, 2))
        dyn = cached("dynamic", dk, lambda o: render_dynamic(cfg, dust, rain, dyn_end - il, o))
        dl = dur(dyn)
        segs.append(dyn)
        first = cached("cycle_in", key(cyc_key, "fadein"),
                       lambda o: run(["ffmpeg", "-y", "-v", "error", "-i", cycle, "-vf", "fade=in:d=0.8", *ENC, o]))
    else:                                   # sem seção dinâmica: título no 1º ciclo
        first = cached("cycle_title", key(cyc_key, cfg["title"], cfg.get("subtitle")),
                       lambda o: run(["ffmpeg", "-y", "-v", "error", "-i", cycle, "-vf",
                                      f"fade=in:d=2.5,{title_vf(cfg)}", *ENC, o]))
    remain = total - il - dl
    n = int(remain // L)
    rest = remain - n * L
    if rest < 30:
        n -= 1
        rest += L
    if n >= 1:
        segs += [first] + [cycle] * (n - 1)
        outro_src = cycle
    else:
        outro_src = first
    outro = BUILD / f"outro_{key(cyc_key, round(rest, 3))}.mp4"
    if not outro.exists():
        run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "1", "-i", outro_src, "-t", f"{rest:.3f}",
             "-vf", f"fade=out:st={rest - 6:.3f}:d=6", *ENC, outro])
    segs.append(outro)

    print("5/6 áudio")
    audio = BUILD / f"audio_{key(cfg['audio'], cfg.get('sound_design'), total, round(il, 2))}.m4a"
    if not audio.exists():
        render_audio(cfg, total, il, audio)

    print("6/6 montagem")
    lst = BUILD / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in segs))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio,
         "-map", "0:v", "-map", "1:a", "-c", "copy", "-t", f"{total:.3f}", "-movflags", "+faststart", out])
    if preview:
        small = out.with_name(out.stem.replace("_preview_full", "_preview") + ".mp4")
        run(["ffmpeg", "-y", "-v", "error", "-i", out, "-vf", "scale=1280:720", "-c:v", "libx264",
             "-crf", "24", "-preset", "fast", "-maxrate", "2M", "-bufsize", "4M",
             "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", small])
        print(f"prévia: {small} ({small.stat().st_size / 1e6:.0f} MB)")
    print(f"pronto: {out} ({dur(out) / 60:.2f} min, {out.stat().st_size / 1e6:.0f} MB)")
    t_dyn = il + dl
    qa(out, [il * 0.5, il + 6, il + 20, il + 45, t_dyn - 1, t_dyn + 1, t_dyn + L * 0.6,
             t_dyn + L - 0.1, total - 2])


if __name__ == "__main__":
    main()
