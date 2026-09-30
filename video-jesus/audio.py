"""Trilha sonora sintetizada (pads orquestrais, tímpanos, whooshes, sinos e coro).

Gera trilha.wav sincronizada com as cenas de render.py.
"""
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

from render import SCENES, STARTS, TOTAL

SR = 44100
N = int(TOTAL * SR) + SR
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    sig = sig[: N - i0]
    L[i0:i0 + len(sig)] += sig * gain * np.sqrt(0.5 * (1 - pan))
    R[i0:i0 + len(sig)] += sig * gain * np.sqrt(0.5 * (1 + pan))


def env_ar(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
    if nr:
        e[-nr:] *= np.cos(np.linspace(0, np.pi / 2, nr)) ** 2
    return e


# ───────────── pads (cordas sintéticas) ─────────────
def pad(notes, dur, bright=1.0, vib=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        f = mtof(m)
        for det in (-0.08, 0.0, 0.08):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            mod = 1 + vib * 0.004 * np.sin(2 * np.pi * 5.2 * t + ph)
            phase = 2 * np.pi * ff * np.cumsum(mod) / SR + ph
            for k in range(1, 7):
                if ff * k > 6000:
                    break
                out += np.sin(k * phase) / k ** (1.6 - 0.4 * bright)
    out /= max(1, len(notes)) * 3
    return lp(out, 900 + 2600 * bright)


def chord(root, q="m"):
    third = 3 if q == "m" else 4
    return [root - 12, root, root + 7, root + 12, root + 12 + third, root + 19]


D, F, C, Bb, G, A = 50, 53, 48, 46, 43, 45

# (cena, [(acorde, qualidade), ...], ganho, brilho)
PLAN = [
    (0, [(D, "m"), (Bb, "M")], 0.55, 0.6),
    (1, [(F, "M"), (C, "M")], 0.5, 0.8),
    (2, [(Bb, "M"), (F, "M")], 0.55, 0.8),
    (3, [(G, "m"), (A, "M")], 0.55, 0.7),
    (4, [(F, "M"), (C, "M")], 0.6, 0.9),
    (5, [(D, "m"), (D, "m"), (F, "M"), (C, "M")], 0.65, 0.7),
    (6, [(Bb, "M"), (F, "M"), (C, "M"), (F, "M")], 0.65, 0.9),
    (7, [(D, "m"), (G, "m")], 0.5, 0.5),
    (8, [(Bb, "M"), (A, "M")], 0.5, 0.45),
    (9, [(D, "m"), (G, "m")], 0.6, 0.55),
    (10, [(G, "m"), (D, "m"), (Bb, "M"), (A, "M")], 0.7, 0.6),
    (11, [(D, "m")], 0.3, 0.3),
]
for sc, chords, gain, br in PLAN:
    t0 = STARTS[sc]
    dur = SCENES[sc][1]
    step = dur / len(chords)
    for k, (root, q) in enumerate(chords):
        d = step + 1.2
        s = pad(chord(root, q), d, br) * env_ar(int(d * SR), 0.6, 1.0)
        add(s, t0 + k * step - 0.3, gain, pan=0.0)

# ressurreição: crescendo → explosão em Ré maior
T12 = STARTS[12]
build = 6.4
s = pad(chord(D, "m") + [62 + 12], build, 0.5, vib=1)
e = np.linspace(0, 1, len(s)) ** 2
add(s * e * env_ar(len(s), 0.3, 0.8), T12, 0.9)
s = pad(chord(A, "M"), 3.0, 0.8, vib=1)
add(s * np.linspace(0, 1, len(s)) ** 1.5, T12 + 3.6, 0.7)
for k, (root, q, dd) in enumerate([(D, "M", 3.0), (G, "M", 2.0), (D, "M", 1.6)]):
    tt = T12 + 6.3 + sum(x[2] for x in [(D, "M", 3.0), (G, "M", 2.0)][:k])
    s = pad(chord(root, q) + [root + 24], dd + 1.0, 1.0, vib=1)
    add(s * env_ar(len(s), 0.05, 0.9), tt, 1.2)
# final
T13 = STARTS[13]
for k, (root, q) in enumerate([(D, "M"), (G, "M"), (Bb, "M"), (D, "M")]):
    dd = 2.0 + (2.0 if k == 3 else 0)
    s = pad(chord(root, q) + [root + 24], dd + 1.0, 0.9, vib=1)
    add(s * env_ar(len(s), 0.4, 1.2 if k < 3 else 2.5), T13 + k * 2.0 - 0.2, 0.9)


# ───────────── coro ("aah") ─────────────
def choir(notes, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        f = mtof(m)
        for v in range(4):
            ff = f * 2 ** (rng.uniform(-0.12, 0.12) / 12)
            vib = 1 + 0.006 * np.sin(2 * np.pi * rng.uniform(4.5, 6) * t + rng.uniform(0, 6))
            ph = 2 * np.pi * ff * np.cumsum(vib) / SR
            sig = sum(np.sin(k * ph) * (1 / k) for k in range(1, 12) if ff * k < 8000)
            out += sig
    # formantes aproximados de "a"
    out = sum(sosfilt(butter(2, [fc * 0.85, fc * 1.15], "band", fs=SR, output="sos"), out) * g
              for fc, g in ((800, 1.0), (1150, 0.6), (2900, 0.25)))
    return out / (len(notes) * 4) * 3


s = choir([62, 66, 69, 74, 78], 10.0)
add(s * env_ar(len(s), 0.4, 3.0), T12 + 6.3, 0.9, pan=-0.2)
s = choir([62, 67, 71, 74], 8.0)
add(s * env_ar(len(s), 1.5, 4.0), T13 + 0.5, 0.6, pan=0.2)


# ───────────── percussão ─────────────
def boom(dur=2.5, f0=62, f1=38, noise=0.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 12)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    nz = lp(rng.standard_normal(n), 900) * np.exp(-t * 18) * noise
    return body + nz


def heartbeat():
    return np.concatenate([boom(0.22, 70, 45, 0.1) * 0.9, np.zeros(int(0.06 * SR)), boom(0.5, 65, 42, 0.1) * 0.7])


def crack(dur=1.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    return hp(x, 200) * np.exp(-t * 3.0) * (0.6 + 0.4 * (rng.random(n) > 0.97)) + boom(dur, 50, 30, 0.8) * 0.8


def whoosh(dur=0.9):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    for k in range(6):
        a, b = k * n // 6, (k + 1) * n // 6
        fc = 300 + 3000 * (k / 5) ** 2
        out[a:b] = lp(x, fc)[a:b]
    return out * np.sin(np.pi * t) ** 2 * t


def bell(m, dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    return sum(np.sin(2 * np.pi * f * r * t) * g * np.exp(-t * d)
               for r, g, d in ((1, 1, 1.4), (2.0, 0.5, 2.2), (2.76, 0.35, 3.0), (5.4, 0.15, 5)))


def pluck(m, dur=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    ph = 2 * np.pi * f * t
    s = sum(np.sin(k * ph) / k for k in range(1, 10))
    return lp(s * np.exp(-t * 9), 1800)


for k, st in enumerate(STARTS):
    if k in (12,):
        continue
    add(boom(), st, 0.55 if k else 0.8)
    if k and k not in (12, 13):
        add(whoosh(), st - 0.85, 0.25, pan=0.3 if k % 2 else -0.3)

add(boom(4, 70, 32, 0.6), 0.3, 0.8)
# relâmpagos
for tt in (STARTS[5] + 1.0, STARTS[5] + 2.6, STARTS[5] + 4.0, STARTS[10] + 6.3):
    add(crack(), tt, 0.5, pan=rng.uniform(-0.5, 0.5))
# chuva / tempestade
n = int(7.5 * SR)
rain = hp(rng.standard_normal(n), 1500) * env_ar(n, 0.3, 2.0)
add(rain, STARTS[5], 0.06, pan=0.0)
# batidas de coração na paixão e na cruz
t = STARTS[8] + 4.0
while t < STARTS[11] - 0.5:
    add(heartbeat(), t, 0.6)
    t += 0.85
# ostinato de cordas (tensão)
for sc, root in ((5, D), (9, D), (10, G)):
    t0, dur = STARTS[sc], SCENES[sc][1]
    steps = int((dur - (5 if sc == 5 else 0.5)) / 0.25)
    for i in range(steps):
        m = root - 12 + (12 if i % 2 else 0)
        if sc == 10 and i * 0.25 > 5.5:
            m = [G, D, Bb, A][min(3, int(i * 0.25 / 2.5))] - 12 + (12 if i % 2 else 0)
        add(pluck(m), t0 + i * 0.25, 0.22 + 0.1 * (i % 4 == 0), pan=-0.3)
# sinos da estrela / anjo / final
for sc, notes in ((0, [74, 81, 86]), (1, [77, 81, 84, 89]), (2, [81, 86, 89, 93]), (3, [79, 86, 91]),
                  (4, [77, 84, 89]), (13, [86, 90, 93, 98])):
    for i, m in enumerate(notes):
        add(bell(m), STARTS[sc] + 0.6 + i * 0.35, 0.09, pan=(-0.5 + i * 0.35))
# ressurreição: tremor, rolar da pedra, explosão
n = int(2.2 * SR)
add(lp(rng.standard_normal(n), 120) * env_ar(n, 0.3, 0.6) * 3, T12 + 3.4, 0.5)
n = int(2.0 * SR)
add(lp(rng.standard_normal(n), 400) * env_ar(n, 0.2, 0.5), T12 + 4.0, 0.35)
add(boom(5, 80, 30, 1.0), T12 + 6.25, 1.1)
add(crack(3.0), T12 + 6.25, 0.35)
s = whoosh(1.4)
add(s, T12 + 4.9, 0.4)
add(boom(3, 60, 35, 0.3), T13, 0.6)

# ───────────── mix + reverb ─────────────
ir_n = int(2.6 * SR)
tt = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-tt / 0.75)
irR = rng.standard_normal(ir_n) * np.exp(-tt / 0.75)
irL, irR = lp(irL, 5000), lp(irR, 5000)
irL /= np.sqrt(np.sum(irL ** 2))
irR /= np.sqrt(np.sum(irR ** 2))
wetL = fftconvolve(L, irL)[:N]
wetR = fftconvolve(R, irR)[:N]
outL = L * 0.8 + wetL * 0.45
outR = R * 0.8 + wetR * 0.45
out = np.stack([outL, outR], 1)[: int(TOTAL * SR)]
# fade final e normalização suave
fo = int(2.0 * SR)
out[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
out = hp(out.T, 25).T
out /= np.max(np.abs(out)) + 1e-9
out = np.tanh(out * 1.6) / np.tanh(1.6) * 0.93
pcm = (out * 32767).astype(np.int16)
path = os.path.join(HERE, "trilha.wav")
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("OK:", path, f"{len(pcm) / SR:.1f}s")
