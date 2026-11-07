"""Mixagem: narração + trilha arranjada (vidIQ) + sound design (CUES da timeline) + silêncios + ducking + master.
    python3 mix.py amostra saida.wav
"""
import importlib
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt

import sfx

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))


def load(path, sr_out=SR):
    a, sr = sf.read(path, always_2d=True, dtype="float64")
    if a.shape[1] == 1:
        a = np.repeat(a, 2, 1)
    if sr != sr_out:
        from math import gcd
        g = gcd(sr, sr_out)
        a = resample_poly(a, sr_out // g, sr // g, axis=0)
    return a


def fade(n, a, b):
    """envelope linear de a até b em n amostras (cos)"""
    return a + (b - a) * (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n)))


def place(bus, x, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= len(bus):
        return
    if x.ndim == 1:
        l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        x = np.stack([x * l * 1.414, x * r * 1.414], 1)
    if i0 < 0:
        x = x[-i0:]
        i0 = 0
    n = min(len(x), len(bus) - i0)
    bus[i0:i0 + n] += x[:n] * gain


def music_seg(bus, track, src0, t0, t1, gain=1.0, fin=0.05, fout=0.25):
    """coloca track[src0 : src0+(t1-t0)] em [t0, t1) com fades."""
    a = int(src0 * SR)
    n = int((t1 - t0) * SR)
    x = track[a:a + n].copy()
    if len(x) < n:
        x = np.concatenate([x, np.zeros((n - len(x), 2))])
    fi, fo = int(fin * SR), int(fout * SR)
    if fi:
        x[:fi] *= fade(fi, 0, 1)[:, None]
    if fo:
        x[-fo:] *= fade(fo, 1, 0)[:, None]
    place(bus, x, t0, gain)


def envelope(x, att=0.01, rel=0.25):
    m = np.abs(x).max(1) if x.ndim > 1 else np.abs(x)
    m = sosfilt(butter(2, 30, "low", fs=SR, output="sos"), m)
    out = np.zeros_like(m)
    ga, gr = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    e = 0.0
    # seguidor de envelope rápido (em blocos para velocidade)
    step = 48
    for i in range(0, len(m), step):
        v = m[i:i + step].max()
        e = ga * e + (1 - ga) * v if v > e else gr * e + (1 - gr) * v
        out[i:i + step] = e
    return out


def main(name, out):
    sys.path.insert(0, HERE)
    P = importlib.import_module(name)
    N = int((P.TOTAL + 1.0) * SR)
    # ── narração
    narr = load(os.path.join(HERE, "narr", name, "narracao.wav"))
    voice = np.zeros((N, 2))
    place(voice, narr, 0.0, 1.0)
    # leve EQ de presença + compressão suave na voz
    v_m = voice[:, 0]
    pres = sosfilt(butter(2, [2500, 5000], "band", fs=SR, output="sos"), v_m) * 0.18
    body = sosfilt(butter(2, 120, "high", fs=SR, output="sos"), v_m)
    vv = body + pres
    vv = np.tanh(vv * 1.6) / np.tanh(1.6)
    voice = np.stack([vv, vv], 1)
    # ── trilha (arranjo da amostra)
    ten = load(os.path.join(HERE, "music", "tensao.wav"))
    vil = load(os.path.join(HERE, "music", "vilao.wav"))
    pia = load(os.path.join(HERE, "music", "piano.wav"))
    mus = np.zeros((N, 2))
    A, NO_T = 0.0, P.T_NO
    music_seg(mus, ten, 2.5, 0.0, NO_T + 0.06, 0.95, fin=0.02, fout=0.06)            # gancho
    music_seg(mus, ten, 26.0, P.S("L08") - 0.1, P.D0, 0.95, fin=0.15, fout=0.2)      # poderes + troféus
    music_seg(mus, ten, 47.6, P.D0, P.D_END, 1.05, fin=0.05, fout=0.03)              # contra todos (forte)
    music_seg(mus, pia, 3.7, P.T_NOV - 0.35, P.I_END + 0.05, 1.0, fin=0.4, fout=0.6)  # hoje → recuo
    music_seg(mus, vil, 0.0, P.J0, P.TOTAL + 0.5, 0.95, fin=0.05, fout=1.2)          # título → fim
    # silêncios dramáticos
    for a, b in P.SILENCE:
        i0, i1 = int(a * SR), int(b * SR)
        r = int(0.03 * SR)
        mus[i0:i1] = 0
        if i0 - r > 0:
            mus[i0 - r:i0] *= fade(r, 1, 0)[:, None]
        if i1 + r < N:
            mus[i1:i1 + r] *= fade(r, 0, 1)[:, None]
    # fim da amostra
    fo = int(0.8 * SR)
    e0 = int((P.TOTAL - 0.8) * SR)
    mus[e0:e0 + fo] *= fade(fo, 1, 0)[:, None]
    mus[e0 + fo:] = 0
    # ducking pela voz
    ve = envelope(voice, 0.015, 0.35)
    ve = ve / (ve.max() + 1e-9)
    duck_db = float(os.environ.get("DUCK", -10.5)) * np.clip(ve * 3.2, 0, 1)
    mus *= (10 ** (duck_db / 20))[:, None]
    # ── sound design
    fxb = np.zeros((N, 2))
    for t, nm, g, pan in P.CUES:
        place(fxb, sfx.make(nm), t, g, pan)
    # ── soma e master
    MUS_G, FX_G = float(os.environ.get("MUS_G", 0.42)), float(os.environ.get("FX_G", 0.55))
    vm = np.abs(voice[:, 0])
    act = envelope(voice, 0.01, 0.2) > 0.02

    def db(x):
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
    print(f"voz (ativa) {db(voice[act, 0]):.1f} dB | trilha sob a voz {db(mus[act, 0] * MUS_G):.1f} dB | "
          f"trilha nos respiros {db(mus[~act, 0] * MUS_G):.1f} dB | efeitos {db(fxb[:, 0] * FX_G):.1f} dB")
    mixd = voice * 1.0 + mus * MUS_G + fxb * FX_G
    # cola: compressor simples no master
    env = envelope(mixd, 0.005, 0.18)
    thr = 0.5
    gr = np.where(env > thr, (thr + (env - thr) * 0.35) / (env + 1e-9), 1.0)
    mixd *= gr[:, None]
    mixd = np.tanh(mixd * 1.1) / np.tanh(1.1)
    mixd = mixd[:int(P.TOTAL * SR)]
    tmp = out.replace(".wav", "_pre.wav")
    sf.write(tmp, mixd.astype(np.float32), SR, subtype="FLOAT")
    # loudness YouTube (-14 LUFS, pico -1.5 dBTP)
    os.system(f'ffmpeg -y -loglevel error -i "{tmp}" -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar {SR} "{out}"')
    os.remove(tmp)
    print("OK", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
