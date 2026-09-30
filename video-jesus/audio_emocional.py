"""Trilha emocional (versão 2) — piano, violoncelo, violinos, coro e percussão sintetizados.

Arco dramático, sincronizado com as cenas de render.py:
  ternura (nascimento) → esperança (batismo/mensagem) → tristeza (ceia, Getsêmani)
  → dor (paixão/cruz) → silêncio → explosão de glória (ressurreição) → amor (apelo final)

Gera trilha_emocional.wav
"""
import os

import numpy as np

import render
import synth
from render import SCENES0 as SCENES, STARTS0 as STARTS, TOTAL

synth.setup(TOTAL)
if render.SCALE != [1.0] * len(render.SCALE):
    import narracao
    synth.WARP = narracao.warp_fn(render)
from synth import *  # noqa: E402,F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))


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
i0, i1 = int(synth.warp(T(10) + 4.55) * SR), int(synth.warp(T(10) + 4.85) * SR)
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
synth.master(os.environ.get("TRILHA_OUT", os.path.join(HERE, "trilha_emocional.wav")))
