"""Trilha emocional (versão 2) — piano, violoncelo, violinos, coro e percussão sintetizados.

Arco dramático, sincronizado com as cenas de render.py:
  ternura (nascimento) → esperança (batismo/mensagem) → tristeza (ceia, Getsêmani)
  → dor (paixão/cruz) → silêncio → explosão de glória (ressurreição) → amor (apelo final)

Gera trilha_emocional.wav
"""
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

from render import SCENES, STARTS, TOTAL

SR = 44100
N = int(TOTAL * SR) + 2 * SR
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(2024)
L = np.zeros(N)
R = np.zeros(N)
DUCK = np.ones(N)  # sidechain suave para o "silêncio" dramático

# pitch classes
C, D, E, F, G, A, Bb, B = 0, 2, 4, 5, 7, 9, 10, 11


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


# ───────────────────────── partitura por cena ─────────────────────────
# (acordes, q, passo do arpejo, vel piano, pad, tema, violino, gain_pad)
T = lambda k: STARTS[k]
Dur = lambda k: SCENES[k][1]

CUES = {
    # cena: dict(chords=[(pc,q)], step, vel, pad, mel, vln, cello)
    1: dict(chords=[(D, "m"), (Bb, "M")], step=0.30, vel=0.55, pad=0.35, mel="A", mvel=0.5, vln=0.0),
    2: dict(chords=[(F, "M"), (C, "M")], step=0.30, vel=0.58, pad=0.4, mel="A", mvel=0.55, vln=0.35),
    3: dict(chords=[(G, "m"), (A, "M")], step=0.25, vel=0.55, pad=0.45, mel="A", mvel=0.55, vln=0.4),
    4: dict(chords=[(Bb, "M"), (F, "M")], step=0.30, vel=0.62, pad=0.6, mel="A", mvel=0.62, vln=0.55),
    5: dict(chords=[(D, "m"), (G, "m"), (Bb, "M")], step=0.20, vel=0.7, pad=0.7, mel="B", mvel=0.6, vln=0.4),
    6: dict(chords=[(Bb, "M"), (F, "M"), (G, "m"), (C, "M")], step=0.25, vel=0.68, pad=0.85, mel="A", mvel=0.7, vln=0.7),
    7: dict(chords=[(D, "m"), (G, "m")], step=0.45, vel=0.5, pad=0.4, mel="B", mvel=0.6, vln=0.0),
    8: dict(chords=[(Bb, "M"), (A, "M")], step=0.50, vel=0.45, pad=0.45, mel="B", mvel=0.6, vln=0.0),
    9: dict(chords=[(D, "m"), (G, "m")], step=0.40, vel=0.5, pad=0.6, mel="B", mvel=0.7, vln=0.35),
    10: dict(chords=[(G, "m"), (D, "m"), (Bb, "M"), (A, "M")], step=0.45, vel=0.55, pad=0.8, mel="B", mvel=0.8, vln=0.6),
}

# ── introdução: drone + estrela
add(pad_chord(D, "m", 6.5, 0.3, 0.8) * env_ar(int(6.5 * SR), 1.5, 1.5), 0.0, 0.7)
for i, m in enumerate([62, 69, 74, 77, 81]):
    add(piano(m, 3.5, 0.5), 0.8 + i * 0.7, 0.8, pan=-0.3 + i * 0.15)
for i, m in enumerate([86, 90, 93]):
    add(bell(m), 2.6 + i * 0.4, 0.07, pan=0.3)
add(timpani(60, 4.0, 1.0), 0.3, 0.7)

for sc, cfg in CUES.items():
    t0, dur = T(sc), Dur(sc)
    chords = cfg["chords"]
    cd = dur / len(chords)
    for k, (pc, q) in enumerate(chords):
        tc = t0 + k * cd
        pd = cd + 0.9
        s = pad_chord(pc, q, pd, 0.4 + 0.4 * cfg["pad"], 1.0) * env_ar(int(pd * SR), 0.7, 1.0)
        add(s, tc - 0.25, cfg["pad"] * 0.6)
        arpeggio(pc, q, tc, cd, cfg["step"], cfg["vel"], pan=-0.15, gain=0.9)
        # melodia do violoncelo (registro grave/médio) e violinos (uma oitava acima)
        melody(pc, q, tc + 0.15, cd - 0.15, cfg["mel"], cfg["mvel"], oct_up=-1 if cfg["mel"] == "B" else 0,
               bright=0.45, ens=1, gain=0.85, pan=0.15)
        if cfg["vln"] > 0:
            melody(pc, q, tc + 0.3, cd - 0.3, cfg["mel"], cfg["mvel"] * cfg["vln"], oct_up=1,
                   bright=0.65, ens=3, gain=0.8, pan=-0.2)
    if sc != 1:
        add(timpani(58, 3.0, 0.9), t0, 0.5)
    if sc > 1:
        add(whoosh(1.0), t0 - 0.9, 0.16, pan=0.3 if sc % 2 else -0.3)

# ── tempestade e relâmpagos (cena 5)
for tt in (T(5) + 1.0, T(5) + 2.6, T(5) + 4.0, T(10) + 6.3):
    add(crack(), tt, 0.5, pan=rng.uniform(-0.5, 0.5))
n = int(6.5 * SR)
add(hp(rng.standard_normal(n), 1600) * env_ar(n, 0.3, 2.0), T(5), 0.05)
for i in range(6):
    add(timpani(50 + (i % 2) * 5, 1.0, 0.7), T(5) + 0.3 + i * 0.9, 0.35)

# ── coração e sombra (Getsêmani → cruz)
t = T(8) + 4.2
while t < T(11) - 0.5:
    add(heartbeat(0.8), t, 0.5)
    t += 0.9
# coro grave "aah" na paixão e na cruz
add(choir([50, 57, 62], 6.0) * env_ar(int(6.0 * SR), 1.5, 1.5), T(9) + 1.0, 0.5)
add(choir([43, 50, 55, 62], 6.0) * env_ar(int(6.0 * SR), 1.5, 2.0), T(10) + 0.3, 0.55)
add(choir([46, 53, 58, 65, 70], 4.0, 0.5) * env_ar(int(4.0 * SR), 0.3, 1.5), T(10) + 4.8, 0.6)   # "consumado"
# "consumado": silêncio dramático imediatamente antes
i0, i1 = int((T(10) + 4.55) * SR), int((T(10) + 4.85) * SR)
DUCK[i0:i1] = np.linspace(1, 0.15, i1 - i0)
DUCK[i1:i1 + int(0.6 * SR)] = np.linspace(0.15, 1, int(0.6 * SR))

# ── silêncio (cena 11): piano esparso, uma nota por vez
sc = 11
for i, (dt, m, v) in enumerate([(0.4, 50, 0.4), (1.7, 57, 0.35), (3.1, 62, 0.35), (4.6, 65, 0.3), (5.7, 57, 0.28)]):
    add(piano(m, 5.0, v), T(sc) + dt, 0.9, pan=-0.2 + 0.1 * i)
add(pad_chord(D, "m", Dur(sc) + 1.0, 0.2, 0.6, low=True) * env_ar(int((Dur(sc) + 1) * SR), 1.5, 1.0), T(sc), 0.32)
# aproximação da manhã: A maior ao fundo
add(pad_chord(A, "M", 3.5, 0.4, 0.8) * np.linspace(0, 1, int(3.5 * SR)) ** 2, T(sc) + 4.0, 0.4)

# ── ressurreição (cena 12)
T12 = T(12)
build = 6.4
sb = pad_chord(D, "m", build, 0.5, 1.0) * np.linspace(0, 1, int(build * SR)) ** 2
add(sb, T12, 0.8)
sb2 = strings([62, 69, 74, 77, 81], 5.0, 0.8, 1.2) * np.linspace(0, 1, int(5.0 * SR)) ** 2.2
add(sb2, T12 + 1.4, 0.7)
add(choir([57, 62, 66, 69, 74], 6.0, 0.4) * np.linspace(0, 1, int(6.0 * SR)) ** 2, T12 + 0.5, 0.7)
add(cymbal_swell(2.6), T12 + 3.7, 0.5)
add(whoosh(1.6), T12 + 4.7, 0.5)
# arpejos de piano acelerando (tensão)
for i in range(30):
    tt = T12 + 0.4 + i * (0.42 - 0.010 * i)
    add(piano(50 + [0, 7, 12, 15, 19][i % 5] + (12 if i > 14 else 0), 1.5, 0.35 + 0.02 * i), tt, 0.7, pan=-0.2)
# rolar da pedra: tremor + rumble
n = int(2.4 * SR)
add(lp(rng.standard_normal(n), 110) * env_ar(n, 0.4, 0.7) * 3, T12 + 3.4, 0.55)
n = int(2.0 * SR)
add(lp(rng.standard_normal(n), 380) * env_ar(n, 0.2, 0.6), T12 + 4.0, 0.35)
# rufar de tímpanos
for i in range(28):
    tt = T12 + 3.4 + i * 0.1
    add(timpani(60, 0.5, 0.25 + 0.03 * i), tt, 0.55)

# EXPLOSÃO em Ré maior com o tema triunfante
TX = T12 + 6.25
add(timpani(55, 5.0, 1.2), TX, 1.0)
add(crack(3.0), TX, 0.3)
add(cymbal_swell(0.01), TX, 0.0)
prog = [(D, "M", 3.0), (G, "M", 2.0), (A, "M", 1.2), (D, "M", 1.4)]
tc = TX
for pc, q, dd in prog:
    s = pad_chord(pc, q, dd + 1.2, 1.0, 1.2, 1.3) * env_ar(int((dd + 1.2) * SR), 0.05, 1.0)
    add(s, tc, 1.0)
    add(choir([bass_of(pc) + 24, bass_of(pc) + 31, bass_of(pc) + 36, bass_of(pc) + 40], dd + 1.0, 0.3)
        * env_ar(int((dd + 1.0) * SR), 0.15, 0.9), tc, 0.9, pan=0.1)
    arpeggio(pc, q, tc, dd, 0.16, 0.85, pan=0.1, pattern=[0, 1, 2, 3, 4, 3, 2, 3], gain=0.85)
    melody(pc, q, tc, dd, "A", 0.95, oct_up=1, bright=0.9, ens=4, gain=1.0, pan=-0.1)
    melody(pc, q, tc, dd, "A", 0.8, oct_up=0, bright=0.7, ens=2, gain=0.8, pan=0.15)
    tc += dd

# ── final: apelo (amor) — mesma progressão, mais íntima, crescendo até "ELE TE AMA"
T13 = T(13)
FINAL = [(0.0, D, "M", "A"), (2.2, G, "M", "A"), (4.5, B, "m", "B"), (6.3, G, "M", "B"), (8.1, D, "M", "A"),
         (9.9, A, "M", "A"), (11.8, B, "m", "A"), (13.3, G, "M", "A"), (14.9, D, "M", "C")]
DUR13 = Dur(13)
add(timpani(55, 4.0, 1.0), T13, 0.6)
for k, (t0, pc, q, kind) in enumerate(FINAL):
    t1 = FINAL[k + 1][0] if k + 1 < len(FINAL) else DUR13
    dd = t1 - t0
    tail = 1.2 if k + 1 < len(FINAL) else 2.6
    big = k >= 6  # "Ele nos amou / ELE TE AMA"
    gain = 0.75 if not big else 1.05
    s = pad_chord(pc, q, dd + tail, 0.7 if big else 0.5, 1.0) * env_ar(int((dd + tail) * SR), 0.4, tail)
    add(s, T13 + t0 - 0.2, gain * 0.75)
    if k < 8:
        arpeggio(pc, q, T13 + t0, dd, 0.28 if not big else 0.22, 0.5 if not big else 0.7, pan=-0.1,
                 gain=0.85)
        melody(pc, q, T13 + t0 + 0.1, dd - 0.1, kind, 0.6 if not big else 0.85, oct_up=1 if big else 0,
               bright=0.7, ens=3 if big else 1, gain=0.9, pan=0.1)
    else:
        for i, m in enumerate([50, 57, 62, 66, 69, 74, 78, 81, 86]):
            add(piano(m, 4.5, 0.55 - i * 0.03), T13 + t0 + i * 0.14, 0.7, pan=-0.3 + i * 0.08)
        add(strings([62, 66, 69, 74, 78, 81], dd + tail, 0.8, 1.2) * env_ar(int((dd + tail) * SR), 0.2, tail),
            T13 + t0, 0.55)
add(choir([62, 66, 69, 74], 9.0, 0.3) * env_ar(int(9.0 * SR), 1.5, 3.5), T13 + 0.6, 0.55, pan=0.2)
add(choir([59, 62, 66, 71, 74], 6.0, 0.3) * env_ar(int(6.0 * SR), 1.0, 2.5), T13 + 11.8, 0.7)
for tt in (4.5, 8.1, 11.8):
    add(timpani(55, 2.5, 0.8), T13 + tt, 0.45)
    add(whoosh(0.8), T13 + tt - 0.7, 0.14)
for i, m in enumerate([86, 90, 93, 98]):
    add(bell(m, 2.5), T13 + 14.9 + 1.75 + i * 0.12, 0.10, pan=-0.3 + i * 0.2)

# ───────────────────────── mix ─────────────────────────
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
path = os.path.join(HERE, "trilha_emocional.wav")
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("OK:", path, f"{len(pcm) / SR:.1f}s")
