"""Mix do estilo documentário: narração + trilha arranjada (MUSIC) + áudio original dos clipes (CLIPA)
+ efeitos suaves (CUES, sfx_doc). Falas originais (SPEECH_CLIPS) também abaixam a trilha.
    python3 mix2.py amostra2 saida.wav
"""
import importlib
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

import sfx_doc
from mix import SR, envelope, fade, load, music_seg, place

HERE = os.path.dirname(os.path.abspath(__file__))


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def main(name, out):
    sys.path.insert(0, HERE)
    P = importlib.import_module(name)
    N = int((P.TOTAL + 1.5) * SR)
    # ── narração (EQ leve: corta grave, um pouco de presença, saturação suave)
    voice = np.zeros((N, 2))
    place(voice, load(os.path.join(HERE, "narr", "fiel", "narracao.wav")), 0.0, 1.0)
    vm = voice[:, 0]
    body = sosfilt(butter(2, 90, "high", fs=SR, output="sos"), vm)
    pres = sosfilt(butter(2, [2500, 5000], "band", fs=SR, output="sos"), vm) * 0.15
    vv = np.tanh((body + pres) * 1.5) / np.tanh(1.5)
    voice = np.stack([vv, vv], 1)
    # ── áudio original dos clipes
    amb = np.zeros((N, 2))
    speech = np.zeros((N, 2))
    for t, nm, g, fi, fo, dur, off in P.CLIPA:
        a = load(os.path.join(HERE, "cache", "seg", nm + ".wav"))[int(off * SR):]
        if dur:
            a = a[:int(dur * SR)]
        if len(a) == 0:
            continue
        a = a.copy()
        nfi, nfo = min(len(a), int(fi * SR)), min(len(a), int(fo * SR))
        if nfi:
            a[:nfi] *= fade(nfi, 0, 1)[:, None]
        if nfo:
            a[-nfo:] *= fade(nfo, 1, 0)[:, None]
        if nm in P.SPEECH_CLIPS:   # fala real: nivela com a narração
            a = a / (np.sqrt(np.mean(a ** 2)) + 1e-9) * 10 ** (-21 / 20)
            place(speech, a, t, g)
        else:
            place(amb, a, t, g)
    # ── trilha
    tracks, mus = {}, np.zeros((N, 2))
    for t0, t1, tr, src0, g, fin, fout in P.MUSIC:
        if tr not in tracks:
            tracks[tr] = load(os.path.join(HERE, "music", tr + ".wav"))
            tracks[tr] /= (np.sqrt(np.mean(tracks[tr] ** 2)) + 1e-9) / 10 ** (-18 / 20)   # mesma energia média
        music_seg(mus, tracks[tr], src0, t0, t1, g, fin, fout)
    for a, b in P.SILENCE:
        i0, i1 = int(a * SR), min(N, int(b * SR))
        r = int(0.04 * SR)
        mus[i0:i1] = 0
        if i0 - r > 0:
            mus[i0 - r:i0] *= fade(r, 1, 0)[:, None]
        if i1 + r < N:
            mus[i1:i1 + r] *= fade(r, 0, 1)[:, None]
    # ── ducking pela voz (narração + falas originais)
    ve = envelope(voice + speech, 0.015, 0.4)
    ve /= ve.max() + 1e-9
    k = np.clip(ve * 3.2, 0, 1)
    mus *= (10 ** (float(os.environ.get("DUCK", -9.5)) * k / 20))[:, None]
    amb *= (10 ** (-5.0 * k / 20))[:, None]
    # ── efeitos
    fxb = np.zeros((N, 2))
    for t, nm, g, pan in P.CUES:
        place(fxb, sfx_doc.make(nm), t, g, pan)
    MUS_G, FX_G = float(os.environ.get("MUS_G", 0.5)), float(os.environ.get("FX_G", 0.5))
    act = ve > 0.04
    print(f"voz {db(voice[act, 0]):.1f} dB | trilha sob a voz {db(mus[act, 0] * MUS_G):.1f} | "
          f"trilha nos respiros {db(mus[~act, 0] * MUS_G):.1f} | efeitos {db(fxb[:, 0] * FX_G):.1f} | "
          f"ambiente {db(amb[:, 0]):.1f} | falas originais {db(speech[np.abs(speech[:, 0]) > 1e-4, 0]):.1f}")
    mixd = voice + speech + mus * MUS_G + amb + fxb * FX_G
    # cola no master
    env = envelope(mixd, 0.005, 0.18)
    thr = 0.5
    mixd *= np.where(env > thr, (thr + (env - thr) * 0.35) / (env + 1e-9), 1.0)[:, None]
    mixd = np.tanh(mixd * 1.1) / np.tanh(1.1)
    n_end = int(P.TOTAL * SR)
    fo = int(0.6 * SR)
    mixd[n_end - fo:n_end] *= fade(fo, 1, 0)[:, None]
    mixd = mixd[:n_end]
    tmp = out.replace(".wav", "_pre.wav")
    sf.write(tmp, mixd.astype(np.float32), SR, subtype="FLOAT")
    os.system(f'ffmpeg -y -loglevel error -i "{tmp}" -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar {SR} "{out}"')
    os.remove(tmp)
    print("OK", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
