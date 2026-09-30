"""Sintetizador da trilha: instrumentos (piano, cordas, coro, percussão), harmonia e master.

Uso:
    import synth
    synth.setup(duracao_em_segundos)
    from synth import *          # add(), piano(), pad_chord(), ...
    ...
    synth.master("saida.wav")
"""
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
rng = np.random.default_rng(2024)
TOTAL = N = 0
L = R = DUCK = None

# pitch classes
C, D, E, F, G, A, Bb, B = 0, 2, 4, 5, 7, 9, 10, 11


def setup(total):
    """Zera o mix para uma trilha de `total` segundos."""
    global TOTAL, N, L, R, DUCK, rng
    TOTAL = total
    N = int(total * SR) + 2 * SR
    rng = np.random.default_rng(2024)
    L = np.zeros(N)
    R = np.zeros(N)
    DUCK = np.ones(N)  # sidechain suave para silêncios dramáticos


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or len(sig) == 0:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    sig = sig[: N - i0]
    L[i0:i0 + len(sig)] += sig * gain * np.sqrt(0.5 * (1 - pan))
    R[i0:i0 + len(sig)] += sig * gain * np.sqrt(0.5 * (1 + pan))


def env_ar(n, a, r):
    e = np.ones(n)
    na, nr = min(int(a * SR), n), min(int(r * SR), n)
    if na:
        e[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
    if nr:
        e[n - nr:] *= np.cos(np.linspace(0, np.pi / 2, nr)) ** 2
    return e


# ───────────────────────── instrumentos ─────────────────────────
def piano(m, dur=3.0, vel=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    dec = 1.0 + max(0, m - 36) * 0.03
    out = np.zeros(n)
    for k in range(1, 10):
        fk = f * k * np.sqrt(1 + 0.0003 * k * k)
        if fk > 9000:
            break
        amp = 1 / k ** 1.2
        out += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * dec * (1 + 0.28 * (k - 1)))
    # leve segunda corda desafinada (chorus natural do piano)
    out += 0.35 * np.sin(2 * np.pi * f * 1.0012 * t) * np.exp(-t * dec * 0.9)
    hn = int(0.025 * SR)
    click = rng.standard_normal(hn) * np.exp(-np.arange(hn) / (0.005 * SR))
    out[:hn] += lp(click, 3000) * 0.12
    out *= np.minimum(1, t / 0.004)
    out *= env_ar(n, 0, 0.15)
    return lp(out, 1800 + 5500 * vel) * vel * 0.9


def bowed(m, dur, vel=0.7, bright=0.5, vib=1.0, ens=1):
    """Violoncelo/violino: serra filtrada com vibrato que 'abre' depois do ataque."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    out = np.zeros(n)
    for v in range(ens):
        det = 2 ** (rng.uniform(-0.06, 0.06) / 12) if ens > 1 else 1.0
        vd = np.clip((t - 0.3) / 0.6, 0, 1) * 0.0055 * vib
        rate = 5.2 + rng.uniform(-0.4, 0.4)
        ph = 2 * np.pi * np.cumsum(f * det * (1 + vd * np.sin(2 * np.pi * rate * t + rng.uniform(0, 6)))) / SR
        for k in range(1, 16):
            if f * k > 9000:
                break
            out += np.sin(k * ph) / k ** (1.15 - 0.35 * bright)
    out /= ens
    out = lp(out, 1100 + 3600 * bright)
    bow = lp(rng.standard_normal(n), 2500) * 0.02
    out = (out + bow) * env_ar(n, 0.14, min(0.5, dur * 0.4))
    return out * vel * 0.55


def strings(notes, dur, bright=0.6, vib=1.0):
    n = int(dur * SR)
    out = np.zeros(n)
    for m in notes:
        out += bowed(m, dur, 1.0, bright, vib, ens=3)
    return out / max(1, len(notes)) * 1.6


def choir(notes, dur, breathy=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        f = mtof(m)
        for _ in range(4):
            ff = f * 2 ** (rng.uniform(-0.12, 0.12) / 12)
            vib = 1 + 0.006 * np.sin(2 * np.pi * rng.uniform(4.5, 6) * t + rng.uniform(0, 6))
            ph = 2 * np.pi * ff * np.cumsum(vib) / SR
            out += sum(np.sin(k * ph) / k for k in range(1, 12) if ff * k < 8000)
    out = sum(sosfilt(butter(2, [fc * 0.85, fc * 1.15], "band", fs=SR, output="sos"), out) * g
              for fc, g in ((800, 1.0), (1150, 0.6), (2900, 0.25)))
    if breathy:
        out += hp(rng.standard_normal(n), 3000) * breathy * 0.02
    return out / (len(notes) * 4) * 3


def timpani(f0=70, dur=2.5, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.5 * np.exp(-t * 25))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    nz = lp(rng.standard_normal(n), 700) * np.exp(-t * 25) * 0.5
    return (body + nz) * vel


def heartbeat(vel=1.0):
    a = timpani(52, 0.35, 0.8 * vel)
    b = timpani(48, 0.6, 0.6 * vel)
    gap = np.zeros(int(0.11 * SR))
    return np.concatenate([a, gap, b])


def whoosh(dur=1.0, up=True):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    steps = 8
    for k in range(steps):
        a, b = k * n // steps, (k + 1) * n // steps
        fc = 250 + 4500 * ((k / (steps - 1)) ** 2 if up else (1 - k / (steps - 1)) ** 2)
        out[a:b] = lp(x, fc)[a:b]
    t = np.linspace(0, 1, n)
    return out * (np.sin(np.pi * t) ** 2) * (t if up else 1 - t)


def cymbal_swell(dur):
    n = int(dur * SR)
    x = hp(rng.standard_normal(n), 4500) * np.linspace(0, 1, n) ** 3
    return x


def crack(dur=1.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 200) * np.exp(-t * 3) + timpani(45, dur, 1.0) * 0.8


def bell(m, dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    return sum(np.sin(2 * np.pi * f * r * t) * g * np.exp(-t * d)
               for r, g, d in ((1, 1, 1.2), (2.0, 0.5, 2.0), (2.76, 0.35, 2.8), (5.4, 0.15, 4)))


# ───────────────────────── harmonia ─────────────────────────
def bass_of(pc):
    return 36 + pc  # C2..B2


def tones(pc, q):
    """notas do acorde acima do baixo (registro médio)."""
    b = bass_of(pc)
    third = 3 if q == "m" else 4
    return b, third


def pad_chord(pc, q, dur, bright=0.5, gain=1.0, vib=1.0, low=True):
    b, th = tones(pc, q)
    notes = [b + 12, b + 12 + th, b + 19, b + 24, b + 24 + th, b + 31]
    s = strings(notes, dur, bright, vib)
    if low:
        s = s + bowed(b, dur, 0.9, 0.3, 0.6) * 0.8 + bowed(b + 12, dur, 0.7, 0.35, 0.7) * 0.4
    return s * gain


def arpeggio(pc, q, t0, dur, step, vel, pan=0.0, pattern=None, gain=1.0):
    b, th = tones(pc, q)
    seq = [b + 12, b + 19, b + 24, b + 24 + th, b + 31, b + 24 + th, b + 24, b + 19]
    pat = pattern or [0, 1, 2, 3, 4, 3, 2, 1]
    n = int(dur / step)
    add(piano(b, min(dur + 0.8, 4.0), vel * 0.9), t0, gain * 0.9, pan=-0.15)
    for i in range(n):
        m = seq[pat[i % len(pat)]]
        v = vel * (0.85 if i % 4 else 1.05) * rng.uniform(0.92, 1.05)
        add(piano(m, 2.4, min(v, 1.0)), t0 + i * step + rng.uniform(0, 0.012), gain, pan=pan + rng.uniform(-0.1, 0.1))


def melody(pc, q, t0, dur, kind="A", vel=0.7, oct_up=0, bright=0.5, ens=1, gain=1.0, pan=0.0):
    """Motivo do tema. 'A' = ascendente (esperança), 'B' = descendente (dor), 'C' = nota longa (paz)."""
    b, th = tones(pc, q)
    r, third, fifth = b + 24, b + 24 + th, b + 31
    o = 12 * oct_up
    if kind == "A":
        pat = [(0.00, fifth, 0.36), (0.36, r + 12, 0.30), (0.66, r + 14, 0.20), (0.86, r + 12, 0.20)]
    elif kind == "B":
        pat = [(0.00, r + 12, 0.42), (0.42, third + 12, 0.30), (0.72, fifth, 0.30)]
    else:
        pat = [(0.00, r + 12, 0.95)]
    for a, m, d in pat:
        dd = max(0.35, d * dur)
        s = bowed(m + o, dd + 0.25, vel, bright, 1.0, ens=ens)
        add(s, t0 + a * dur, gain, pan=pan)




def master(path):
    """Aplica ducking, reverb, fade final e normalização; grava WAV estéreo 16-bit."""
    global L, R
    L *= DUCK
    R *= DUCK
    ir_n = int(3.4 * SR)
    tt = np.arange(ir_n) / SR
    irs = []
    for _ in range(2):
        ir = lp(rng.standard_normal(ir_n) * np.exp(-tt / 0.95), 5500)
        ir = ir * np.minimum(1, tt / 0.03)
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    wetL = fftconvolve(L, irs[0])[:N]
    wetR = fftconvolve(R, irs[1])[:N]
    out = np.stack([L * 0.75 + wetL * 0.55, R * 0.75 + wetR * 0.55], 1)[: int(TOTAL * SR)]
    fo = int(2.5 * SR)
    out[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
    out = hp(out.T, 28).T
    out /= np.max(np.abs(out)) + 1e-9
    out = np.tanh(out * 1.5) / np.tanh(1.5) * 0.92
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("OK:", path, f"{len(pcm) / SR:.1f}s")

