"""Monta o vídeo com FFmpeg a partir de cenas.json + timeline.json + audio/narracao.wav.

  python 03_edit.py --previa 120     -> out/previa_2min.mp4
  python 03_edit.py                  -> out/oracao_da_noite_salmos.mp4

Etapas, todas retomáveis (o que já existe em work/ é reaproveitado):
  1. um segmento por cena (clipe em câmera lenta + Ken Burns + texto do versículo)
  2. um arquivo por bloco (crossfade de 1 s entre cenas + look: escurecer, tom quente, vinheta, grão)
  3. concatena os blocos
  4. trilha (pad sintetizado), ducking sob a voz, final só música + voz baixinha, -14 LUFS
"""
import argparse, hashlib, json, math, os, subprocess, sys, textwrap
from concurrent.futures import ThreadPoolExecutor
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, XF = 1920, 1080, 30, 1.0
LOOK = ("eq=brightness=-0.06:saturation=0.85,"
        "colorbalance=rs=0.05:gs=0.01:bs=-0.05:rm=0.04:bm=-0.04,"
        "vignette=angle=PI/4.5,noise=c0s=5:c0f=t,format=yuv420p")
FONTE = "fonts/Inter[opsz,wght].ttf"  # sem serifa moderna, peso Bold
WORK = "work"
for d in (WORK, f"{WORK}/seg", f"{WORK}/txt", f"{WORK}/blocos", "out"): os.makedirs(d, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd) + "\n" + r.stderr[-3000:]); raise RuntimeError("ffmpeg falhou")
    return r

def h(obj): return hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:10]

# ---------- texto na tela ----------
def png_texto(frase, ref):
    path = f"{WORK}/txt/{h([frase, ref])}.png"
    if os.path.exists(path): return path
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f_txt = ImageFont.truetype(FONTE, 62); f_txt.set_variation_by_axes([32, 700])
    f_ref = ImageFont.truetype(FONTE, 30); f_ref.set_variation_by_axes([32, 600])
    linhas = textwrap.wrap(frase, 34)
    lh = 78
    bloco_h = lh * len(linhas) + (60 if ref else 0)
    y0 = int(H / 2 - bloco_h / 2)
    def escrever(d, dx, dy, fill, stroke=0):
        for i, l in enumerate(linhas):
            d.text((W / 2 + dx, y0 + i * lh + dy), l, font=f_txt, fill=fill, anchor="ma",
                   stroke_width=stroke, stroke_fill=fill)
        if ref:
            d.text((W / 2 + dx, y0 + lh * len(linhas) + 22 + dy), ref.upper(), font=f_ref, fill=fill, anchor="ma",
                   stroke_width=stroke, stroke_fill=fill)
    # sombra preta: halo borrado largo + sombra deslocada mais firme, para contraste em qualquer fundo
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0)); escrever(ImageDraw.Draw(halo), 0, 0, (0, 0, 0, 255), stroke=6)
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(18)))
    drop = Image.new("RGBA", (W, H), (0, 0, 0, 0)); escrever(ImageDraw.Draw(drop), 3, 4, (0, 0, 0, 220))
    img.alpha_composite(drop.filter(ImageFilter.GaussianBlur(3)))
    escrever(ImageDraw.Draw(img), 0, 0, (255, 255, 255, 255))
    img.save(path)
    return path

# ---------- 1. segmentos ----------
def render_segmento(job):
    c, L, fade_in, fade_out, textos, path = job
    if os.path.exists(path): return path
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", "0.3", "-stream_loop", "-1",
           "-i", c["clip"]["arquivo_local"]]
    fc = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,"
          f"setpts=1.25*PTS,fps={FPS},trim=duration={L:.3f},setpts=PTS-STARTPTS,"
          f"scale=w='trunc({W}*(1+0.06*t/{L:.3f})/2)*2':h=-2:eval=frame:flags=bicubic,crop={W}:{H}"]
    if fade_in: fc[0] += ",fade=t=in:st=0:d=1.2"
    if fade_out: fc[0] += f",fade=t=out:st={max(0, L - 1.6):.3f}:d=1.5"
    fc[0] += "[v0]"
    last = "v0"
    for k, (png, a, b, fin, fout) in enumerate(textos, 1):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{L:.3f}", "-i", png]
        chain = f"[{k}:v]format=rgba"
        if fin: chain += f",fade=t=in:st={a:.3f}:d=0.3:alpha=1"
        if fout: chain += f",fade=t=out:st={b - 0.3:.3f}:d=0.3:alpha=1"
        fc.append(chain + f"[t{k}]")
        fc.append(f"[{last}][t{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k}]")
        last = f"v{k}"
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{last}]", "-t", f"{L:.3f}", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS),
            path + ".tmp.mp4"]
    run(cmd); os.replace(path + ".tmp.mp4", path)
    return path

# ---------- 2. blocos ----------
def render_bloco(segs, slots, path):
    if os.path.exists(path): return path
    dur = sum(slots)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for s in segs: cmd += ["-i", s]
    fc, last, off = [], "0:v", 0.0
    for k in range(1, len(segs)):
        off += slots[k - 1]
        fc.append(f"[{last}][{k}:v]xfade=transition=fade:duration={XF}:offset={off - 0 :.3f}[x{k}]")
        last = f"x{k}"
    fc.append(f"[{last}]{LOOK}[out]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-t", f"{dur:.3f}", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-g", "60", path + ".tmp.mp4"]
    run(cmd); os.replace(path + ".tmp.mp4", path)
    return path

# ---------- 4. trilha ----------
def gerar_musica(dur, path, sr=44100):
    if os.path.exists(path) and sf.info(path).duration >= dur - 0.5: return path
    print("sintetizando pad ambiente...", flush=True)
    rng = np.random.default_rng(7)
    acordes = [[50, 57, 62, 66, 69], [47, 54, 62, 66, 69], [43, 50, 59, 62, 66], [45, 52, 57, 62, 64],
               [50, 57, 62, 66, 69, 76], [43, 50, 55, 59, 66], [40, 47, 55, 59, 62], [45, 52, 57, 61, 64]]
    N = int(dur * sr) + sr
    out = np.zeros((N, 2), np.float32)
    passo, ataque = 12.0, 5.0
    win = passo + ataque
    n_ac = int(math.ceil(dur / passo)) + 1
    t = np.arange(int(win * sr)) / sr
    env = np.ones_like(t)
    a = t < ataque; env[a] = 0.5 - 0.5 * np.cos(np.pi * t[a] / ataque)
    r = t > win - ataque; env[r] = 0.5 + 0.5 * np.cos(np.pi * (t[r] - (win - ataque)) / ataque)
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    for i in range(n_ac):
        notas = acordes[i % len(acordes)]
        s0 = int(i * passo * sr)
        if s0 >= N: break
        buf = np.zeros((len(t), 2), np.float32)
        for m in notas:
            f = hz(m); amp = 0.16 if m < 48 else 0.11
            trem = 1 + 0.12 * np.sin(2 * np.pi * (0.07 + 0.03 * rng.random()) * t + rng.random() * 6.28)
            for ch, det in ((0, -0.15), (1, 0.15)):
                v = np.zeros_like(t)
                for hh, ah in ((1, 1.0), (2, 0.28), (3, 0.09), (4, 0.03)):
                    v += ah * np.sin(2 * np.pi * (f + det) * hh * t + rng.random() * 6.28)
                buf[:, ch] += (amp * v * trem).astype(np.float32)
        # notas de "piano" esparsas (seno com decaimento) sobre o acorde
        for k in range(2):
            st = rng.uniform(1.5, passo)
            m = int(rng.choice(notas[-3:])) + 12
            tt = t[int(st * sr):] - st
            nota = (np.sin(2 * np.pi * hz(m) * tt) + 0.2 * np.sin(4 * np.pi * hz(m) * tt)) * np.exp(-tt / 2.8)
            nota *= np.minimum(1, tt / 0.02) * 0.07
            pan = rng.uniform(0.3, 0.7)
            buf[int(st * sr):, 0] += (nota * (1 - pan)).astype(np.float32)
            buf[int(st * sr):, 1] += (nota * pan).astype(np.float32)
        buf *= env[:, None]
        e = min(N, s0 + len(t)); out[s0:e] += buf[: e - s0]
    out = out[: int(dur * sr)]
    fade = int(4 * sr); out[:fade] *= np.linspace(0, 1, fade)[:, None]; out[-fade * 2:] *= np.linspace(1, 0, fade * 2)[:, None]
    out /= np.abs(out).max() / 0.89
    tmp = path + ".dry.wav"; sf.write(tmp, out, sr, subtype="PCM_16")
    # reverberação simples
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tmp, "-af",
         "aecho=0.8:0.75:90|180|330|520:0.35|0.25|0.16|0.10,lowpass=f=5200,alimiter=limit=0.9", path])
    os.remove(tmp)
    return path

def mixar_audio(limite, total_video, path):
    """voz + trilha com ducking; nos últimos 3 min a trilha sobe e a voz fica baixinha; -14 LUFS."""
    musica = gerar_musica(math.ceil(total_video) + 2, f"{WORK}/musica.wav")
    T = total_video
    rampa = f"clip((t-{T - 180:.2f})/12,0,1)"
    fc = (f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{limite:.3f},"
          f"volume='1-0.6*{rampa}':eval=frame,asplit=2[voz][sc];"
          f"[1:a]aresample=48000,atrim=0:{limite:.3f},volume=-22dB,volume='1+1.5*{rampa}':eval=frame[mus];"
          f"[mus][sc]sidechaincompress=threshold=0.015:ratio=5:attack=120:release=1200:makeup=1[duck];"
          f"[voz][duck]amix=inputs=2:normalize=0:duration=first[mix]")
    mix = f"{WORK}/mix_{int(limite)}.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", "audio/narracao.wav", "-i", musica,
         "-filter_complex", fc, "-map", "[mix]", "-c:a", "pcm_f32le", mix])
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix, "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:"
          f"offset={js['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", mix, "-af", ln + ",aresample=48000",
         "-c:a", "pcm_s16le", path])
    os.remove(mix)
    return path

# ---------- plano ----------
def planejar(limite):
    tl = json.load(open("timeline.json")); frases = tl["frases"]; total = tl["duracao_total"]
    cenas = [c for c in json.load(open("cenas.json")) if c["inicio"] < limite - 0.5]
    cenas[-1] = {**cenas[-1], "fim": min(cenas[-1]["fim"], limite)}
    blocos = []
    for i, c in enumerate(cenas):
        if not blocos or blocos[-1]["id"] != c["bloco"]: blocos.append({"id": c["bloco"], "cenas": []})
        blocos[-1]["cenas"].append(i)
    jobs, plano = [], []
    for b in blocos:
        segs, slots = [], []
        for n, i in enumerate(b["cenas"]):
            c = cenas[i]; slot = c["fim"] - c["inicio"]
            ultimo = n == len(b["cenas"]) - 1
            L = slot + (0 if ultimo else XF)
            textos = []
            for fi in sorted({f for cc in cenas for f in cc["frases"]}):
                f = frases[fi]  # legenda central em todas as frases; versículos levam a referência
                a, bb = f["inicio"] + 0.05, f["fim"] + 0.3
                if bb <= c["inicio"] or a >= c["inicio"] + L: continue
                ra, rb = max(0, a - c["inicio"]), min(L, bb - c["inicio"])
                textos.append((png_texto(f["frase"], f["referencia"]), ra, rb,
                               a >= c["inicio"], bb <= c["inicio"] + slot))
            key = h([c["clip"]["id"], round(L, 3), n == 0, ultimo, [t[1:] + (os.path.basename(t[0]),) for t in textos]])
            path = f"{WORK}/seg/{i:04d}_{key}.mp4"
            jobs.append((c, L, n == 0, ultimo, textos, path))
            segs.append(path); slots.append(slot)
        plano.append((b["id"], segs, slots))
    return plano, jobs, total, len(cenas)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--previa", type=float); ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    tl_total = json.load(open("timeline.json"))["duracao_total"]
    limite = a.previa or tl_total
    plano, jobs, total, ncenas = planejar(limite)
    print(f"{ncenas} cenas em {len(plano)} blocos, {limite/60:.1f} min", flush=True)
    feitos = [0]
    def seg(j):
        render_segmento(j); feitos[0] += 1
        if feitos[0] % 20 == 0: print(f"  segmentos {feitos[0]}/{len(jobs)}", flush=True)
    with ThreadPoolExecutor(a.jobs) as ex: list(ex.map(seg, jobs))
    print("segmentos ok", flush=True)
    blocos = []
    for bid, segs, slots in plano:
        p = f"{WORK}/blocos/{bid}_{h([segs, slots])}.mp4"
        render_bloco(segs, slots, p); blocos.append(p)
        print(f"  bloco {bid} ok ({sum(slots)/60:.2f} min)", flush=True)
    lista = f"{WORK}/concat_{int(limite)}.txt"
    open(lista, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in blocos))
    video = f"{WORK}/video_{int(limite)}.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video])
    audio = mixar_audio(limite, tl_total if not a.previa else limite + 180 + 60, f"{WORK}/audio_{int(limite)}.wav")
    saida = "out/previa_2min.mp4" if a.previa else "out/oracao_da_noite_salmos.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{limite:.3f}",
         "-movflags", "+faststart", saida])
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", saida],
                             capture_output=True, text=True).stdout)
    print(f"OK {saida}  {int(d//60)}:{d%60:05.2f}")

if __name__ == "__main__":
    main()
