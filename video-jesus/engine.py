"""Motor genérico: compõe quadros de qualquer projeto (render.py, prodigo.py…) em 16:9 ou 9:16 e codifica.

Um projeto é um módulo com:
    SCENES  [(rótulo, duração, função_cena(c, t, dur), legendas), ...]
    STARTS, TOTAL, FADES
    verses()           -> dict de versículos no idioma atual (ou None = padrão do render.py)
    TEXTURE (opcional) -> True aplica textura de papel/guache à arte
"""
import importlib
import os
import subprocess
from functools import partial
from multiprocessing import Pool

import cairo
import numpy as np

from render import (FPS, H, W, clamp, draw_caption, draw_chapter, eout, overlay, seg, vignette)

VW, VH = 1080, 1920  # vertical (Shorts)
_TEX = None


def _texture():
    """Textura de papel fixa (grão suave + pinceladas + manchas). Fixa na tela para comprimir bem."""
    global _TEX
    if _TEX is None:
        rng = np.random.default_rng(11)
        tiles = []
        for _ in range(1):
            grain = rng.normal(0, 8, (H, W)).astype(np.float32)
            streak = np.repeat(rng.normal(0, 3, (1, W)), H, 0).astype(np.float32)
            small = rng.normal(0, 1, (18, 32)).astype(np.float32)
            blotch = np.kron(small, np.ones((60, 60), np.float32))[:H, :W]
            # suaviza os blocos (média móvel separável)
            k = np.ones(61, np.float32) / 61
            blotch = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, blotch)
            blotch = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 0, blotch)
            tiles.append((grain * 0.35 + streak + blotch * 6).astype(np.int16)[:, :, None])
        _TEX = tiles
    return _TEX


def _scene_at(proj, T):
    idx = max(k for k, s in enumerate(proj.STARTS) if s <= T + 1e-9)
    idx = min(idx, len(proj.SCENES) - 1)
    label, dur, fn, caps = proj.SCENES[idx][:4]
    return idx, label, dur, fn, caps, T - proj.STARTS[idx]


def _art(proj, fn, t, dur, frame_i):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)
    c.save()
    fn(c, t, dur)
    c.restore()
    if getattr(proj, "TEXTURE", False):
        surf.flush()
        buf = np.ndarray((H, W, 4), np.uint8, buffer=surf.get_data())
        tex = _texture()[0]
        buf[:, :, :3] = np.clip(buf[:, :, :3].astype(np.int16) + tex, 0, 255).astype(np.uint8)
        surf.mark_dirty()
    vignette(c, getattr(proj, "VIGNETTE", 0.55))
    return surf, c


def _fades(proj, c, idx, t, dur):
    fin, fout = proj.FADES.get(idx, ("#000000", "#000000"))
    if fin:
        overlay(c, fin, 1 - eout(t / 0.35))
    if fout and idx + 1 < len(proj.SCENES) and proj.FADES.get(idx + 1, ("#000000",))[0]:
        overlay(c, fout, seg(t, dur - 0.25, dur) * 0.9)


def frame_wide(projname, i):
    proj = importlib.import_module(projname)
    idx, label, dur, fn, caps, t = _scene_at(proj, i / FPS)
    surf, c = _art(proj, fn, t, dur, i)
    active = [cp for cp in caps if cp[0] <= t < cp[1]]
    if active:
        g = cairo.LinearGradient(0, H - 330, 0, H)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.6)
        c.set_source(g)
        c.rectangle(0, H - 330, W, 330)
        c.fill()
        for cp in active:
            draw_caption(c, cp[2], t - cp[0], cp[1] - cp[0], big=len(cp) > 3 and cp[3])
    if label:
        draw_chapter(c, label, t, dur, verses=proj.verses())
    _fades(proj, c, idx, t, dur)
    surf.flush()
    return bytes(surf.get_data())


ART_S = 1512 / 1920          # escala da arte no vertical (mostra ~71% da largura)
ART_Y = 500                  # topo da faixa de arte
ART_H = H * ART_S


def frame_vertical(projname, t0, i):
    """Short 9:16: fundo desfocado da própria cena + arte ampliada no meio, título/versículo no topo, legenda embaixo."""
    proj = importlib.import_module(projname)
    idx, label, dur, fn, caps, t = _scene_at(proj, t0 + i / FPS)
    art, _ = _art(proj, fn, t, dur, i)
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, VW, VH)
    c = cairo.Context(out)
    # fundo: reduz muito e amplia de volta = desfoque barato
    small = cairo.ImageSurface(cairo.FORMAT_RGB24, 96, 54)
    sc = cairo.Context(small)
    sc.scale(96 / W, 54 / H)
    sc.set_source_surface(art)
    sc.paint()
    mid = cairo.ImageSurface(cairo.FORMAT_RGB24, 384, 216)
    mc = cairo.Context(mid)
    mc.scale(4, 4)
    mc.set_source_surface(small)
    mc.get_source().set_filter(cairo.FILTER_BILINEAR)
    mc.paint()
    k = VH / 216
    c.save()
    c.translate(VW / 2 - 384 * k / 2, 0)
    c.scale(k, k)
    c.set_source_surface(mid)
    c.get_source().set_filter(cairo.FILTER_BILINEAR)
    c.paint()
    c.restore()
    overlay(c, "#000000", 0.62)
    g = cairo.LinearGradient(0, ART_Y + ART_H * 0.8, 0, VH)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(0.35, 0, 0, 0, 0.75)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.9)
    c.set_source(g)
    c.rectangle(0, ART_Y + ART_H * 0.8, VW, VH)
    c.fill()
    # arte central com bordas suavizadas
    c.save()
    c.translate(VW / 2 - W * ART_S / 2, ART_Y)
    c.scale(ART_S, ART_S)
    c.set_source_surface(art)
    c.get_source().set_filter(cairo.FILTER_GOOD)
    m = cairo.LinearGradient(0, 0, 0, H)
    for pos, a in ((0, 0), (0.08, 1), (0.92, 1), (1, 0)):
        m.add_color_stop_rgba(pos, 0, 0, 0, a)
    c.mask(m)
    c.restore()
    # título do capítulo + versículo (maiores, para celular)
    if label:
        c.save()
        c.translate(0, 70)
        c.scale(1.3, 1.3)
        draw_chapter(c, label, t, dur, verses=proj.verses(), wrapw=700)
        c.restore()
    for cp in caps:
        if cp[0] <= t < cp[1]:
            draw_caption(c, cp[2], t - cp[0], cp[1] - cp[0], big=len(cp) > 3 and cp[3],
                         cx=VW / 2, bottom=ART_Y + ART_H + 200, maxw=960, scale=1.15)
    _fades(proj, c, idx, t, dur)
    out.flush()
    return bytes(out.get_data())


def encode(frame_fn, n, out, audio=None, size=(W, H), audio_ss=0.0, crf=21):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{size[0]}x{size[1]}",
           "-r", str(FPS), "-i", "-"]
    if audio and os.path.exists(audio):
        cmd += ["-ss", f"{audio_ss:.3f}", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k",
                "-shortest"]
        if audio_ss > 0:
            cmd += ["-af", "afade=t=in:d=0.8"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for k, fr in enumerate(pool.imap(frame_fn, range(n), chunksize=4)):
            proc.stdin.write(fr)
            if k % 300 == 0:
                print(f"{k}/{n} quadros", flush=True)
    proc.stdin.close()
    proc.wait()
    print("OK:", out, f"{n / FPS:.1f}s")


def render_wide(projname, out, audio=None):
    proj = importlib.import_module(projname)
    encode(partial(frame_wide, projname), int(round(proj.TOTAL * FPS)), out, audio)


def render_vertical(projname, t0, out, audio=None, t1=None):
    proj = importlib.import_module(projname)
    t1 = proj.TOTAL if t1 is None else t1
    encode(partial(frame_vertical, projname, t0), int(round((t1 - t0) * FPS)), out, audio, size=(VW, VH),
           audio_ss=t0)


def snapshot(frame_fn, times, prefix, size=(W, H)):
    """Exporta PNGs de teste (tempos em segundos)."""
    outs = []
    for ts in times:
        data = frame_fn(int(float(ts) * FPS))
        s = cairo.ImageSurface.create_for_data(bytearray(data), cairo.FORMAT_RGB24, *size)
        path = f"{prefix}_{float(ts):06.2f}.png"
        s.write_to_png(path)
        outs.append(path)
    return outs


if __name__ == "__main__":
    import sys
    # python3 engine.py short <projeto> <t0> <saida.mp4> [audio.wav]
    # python3 engine.py wide  <projeto> <saida.mp4> [audio.wav]
    # python3 engine.py snap  <projeto> wide|short:<t0> <prefixo> t1 t2 ...
    cmd, proj = sys.argv[1], sys.argv[2]
    if cmd == "wide":
        render_wide(proj, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "short":
        render_vertical(proj, float(sys.argv[3]), sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else None)
    elif cmd == "snap":
        mode = sys.argv[3]
        if mode == "wide":
            fn, size = partial(frame_wide, proj), (W, H)
        else:
            fn, size = partial(frame_vertical, proj, float(mode.split(":")[1])), (VW, VH)
        for p in snapshot(fn, sys.argv[5:], sys.argv[4], size):
            print(p)
