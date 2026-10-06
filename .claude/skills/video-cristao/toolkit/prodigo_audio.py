"""Trilha do Filho Pródigo — mesmo sintetizador da trilha emocional (synth.py).

Arco: ternura (casa do pai) → melancolia (partida) → festa agitada que se apaga → fome vazia
      → despertar/esperança → volta hesitante → o pai corre (crescendo) → abraço (explosão) → festa → apelo.
Gera trilha_prodigo.wav
"""
import os

import numpy as np

import prodigo
import synth
from prodigo import SCENES, STARTS, TOTAL

synth.setup(TOTAL)
from synth import *  # noqa: E402,F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
SC = prodigo.SCALE  # fator de desaceleração de cada cena (1.0 sem narração)
T = lambda k: STARTS[k]  # noqa: E731
Dur = lambda k: SCENES[k][1]  # noqa: E731
at = lambda k, x: T(k) + x * SC[k]  # noqa: E731  (tempo local "original" → absoluto)


def cue(sc, chords, step, vel, pad, mel, mvel, vln=0.0, t_from=0.0, t_to=None, timp=True):
    t0 = at(sc, t_from)
    dur = ((t_to if t_to is not None else Dur(sc) / SC[sc]) - t_from) * SC[sc]
    cd = dur / len(chords)
    for k, (pc, q) in enumerate(chords):
        tc = t0 + k * cd
        pd = cd + 0.9
        add(pad_chord(pc, q, pd, 0.4 + 0.4 * pad, 1.0) * env_ar(int(pd * SR), 0.7, 1.0), tc - 0.25, pad * 0.6)
        if step:
            arpeggio(pc, q, tc, cd, step, vel, pan=-0.15, gain=0.9)
        if mel:
            melody(pc, q, tc + 0.15, cd - 0.15, mel, mvel, oct_up=-1 if mel == "B" else 0, bright=0.45,
                   gain=0.85, pan=0.15)
            if vln:
                melody(pc, q, tc + 0.3, cd - 0.3, mel, mvel * vln, oct_up=1, bright=0.65, ens=3, gain=0.8,
                       pan=-0.2)
    if timp and sc > 0:
        add(timpani(58, 3.0, 0.8), T(sc), 0.4)
        add(whoosh(1.0), T(sc) - 0.9, 0.14, pan=0.3 if sc % 2 else -0.3)


# 0 · introdução: piano sozinho, tema terno
add(pad_chord(D, "M", 6.8, 0.3, 0.8) * env_ar(int(6.8 * SR), 1.5, 1.5), 0.0, 0.5)
for i, m in enumerate([62, 66, 69, 74, 73, 69, 71, 66]):
    add(piano(m, 3.0, 0.5), 0.5 + i * 0.62, 0.85, pan=-0.2 + i * 0.05)
add(timpani(60, 4.0, 0.9), 0.3, 0.5)

# 1 · a herança (casa do pai, ainda doce)
cue(1, [(D, "M"), (B, "m")], 0.30, 0.55, 0.4, "A", 0.5)
# 2 · a partida (melancolia)
cue(2, [(G, "M"), (D, "M"), (E, "m"), (A, "M")], 0.40, 0.5, 0.5, "B", 0.6, vln=0.4)
# 3 · o desperdício: festa rápida (arpejo acelerado) que se apaga em 5,2 s
cue(3, [(D, "M"), (G, "M"), (A, "M"), (D, "M")], 0.13, 0.62, 0.45, None, 0, t_to=5.4)
for i in range(int(5.2 / 0.25)):
    add(timpani(90 if i % 2 else 70, 0.3, 0.4), at(3, i * 0.25), 0.3)
i0 = int(at(3, 5.2) * SR)
DUCK[i0:i0 + int(0.5 * SR)] = np.linspace(1, 0.2, int(0.5 * SR))
DUCK[i0 + int(0.5 * SR):i0 + int(2.8 * SR)] = np.linspace(0.2, 1, int(2.3 * SR))
add(piano(50, 4.0, 0.5), at(3, 5.6), 0.9)
add(piano(57, 4.0, 0.35), at(3, 6.4), 0.9)
# 4 · a fome (vazio, grave)
cue(4, [(B, "m"), (E, "m"), (B, "m")], 0.6, 0.4, 0.45, "B", 0.6)
add(choir([47, 54, 59], 7.0) * env_ar(int(7.0 * SR), 2.0, 2.0), at(4, 1.0), 0.35)
# 5 · o despertar (piano esparso → esperança)
for i, (dt, m, v) in enumerate([(0.3, 59, 0.4), (1.2, 62, 0.4), (2.1, 66, 0.45), (3.0, 71, 0.45)]):
    add(piano(m, 4.0, v), at(5, dt), 0.9, pan=-0.2 + 0.1 * i)
cue(5, [(G, "M"), (D, "M"), (A, "M")], 0.3, 0.5, 0.5, "A", 0.6, vln=0.5, t_from=3.4)
for i, m in enumerate([86, 90, 93]):
    add(bell(m), at(5, 2.0 + i * 0.35), 0.07, pan=0.3)
# 6 · a volta (hesitante, cordas crescendo)
cue(6, [(B, "m"), (G, "M"), (D, "M"), (A, "M")], 0.45, 0.5, 0.65, "B", 0.65, vln=0.5)
# 7 · o pai corre: crescendo até o abraço (5,0 s) e explosão
T7 = T(7)
add(timpani(58, 3.0, 0.8), T7, 0.4)
sb = pad_chord(B, "m", 5.2 * SC[7], 0.6, 1.0) * np.linspace(0.2, 1, int(5.2 * SC[7] * SR)) ** 2
add(sb, T7, 0.8)
for i in range(22):
    tt = at(7, 1.8 + i * (0.16 - 0.002 * i))
    add(piano(59 + [0, 7, 12, 15, 19][i % 5] + (12 if i > 11 else 0), 1.2, 0.35 + 0.02 * i), tt, 0.7)
for i in range(20):
    add(timpani(60, 0.5, 0.25 + 0.035 * i), at(7, 3.0 + i * 0.1), 0.55)
add(cymbal_swell(2.0 * SC[7]), at(7, 3.0), 0.45)
TX = at(7, 5.0)
add(timpani(55, 5.0, 1.2), TX, 1.0)
tc = TX
for pc, q, dd in ((D, "M", 2.0 * SC[7]), (G, "M", 2.0 * SC[7])):
    add(pad_chord(pc, q, dd + 1.2, 1.0, 1.2, 1.3) * env_ar(int((dd + 1.2) * SR), 0.05, 1.0), tc, 1.0)
    add(choir([bass_of(pc) + 24, bass_of(pc) + 31, bass_of(pc) + 36, bass_of(pc) + 40], dd + 1.0, 0.3)
        * env_ar(int((dd + 1.0) * SR), 0.15, 0.9), tc, 0.9)
    arpeggio(pc, q, tc, dd, 0.16, 0.85, pan=0.1, pattern=[0, 1, 2, 3, 4, 3, 2, 3], gain=0.85)
    melody(pc, q, tc, dd, "A", 0.95, oct_up=1, bright=0.9, ens=4, gain=1.0, pan=-0.1)
    tc += dd
# 8 · a festa do pai (alegria, rápido)
cue(8, [(D, "M"), (G, "M"), (A, "M"), (D, "M")], 0.16, 0.7, 0.8, "A", 0.8, vln=0.8)
for i in range(int(Dur(8) / SC[8] / 0.5)):
    add(timpani(80 if i % 2 else 62, 0.4, 0.5), at(8, i * 0.5), 0.3)
# 9 · apelo final (I–V–vi–IV) + coro, sinos no botão de inscrever
T9 = T(9)
FINAL = [(0.0, D, "M", "A"), (2.2, A, "M", "A"), (4.4, B, "m", "B"), (6.4, G, "M", "A"), (8.4, D, "M", "A"),
         (10.3, A, "M", "A"), (12.2, D, "M", "C")]
add(timpani(55, 4.0, 1.0), T9, 0.5)
for k, (t0, pc, q, kind) in enumerate(FINAL):
    t1 = FINAL[k + 1][0] if k + 1 < len(FINAL) else Dur(9) / SC[9]
    dd = (t1 - t0) * SC[9]
    tail = 1.2 if k + 1 < len(FINAL) else 2.6
    big = 4 <= k <= 5
    add(pad_chord(pc, q, dd + tail, 0.7 if big else 0.5, 1.0) * env_ar(int((dd + tail) * SR), 0.4, tail),
        at(9, t0) - 0.2, 0.8 if big else 0.6)
    if k + 1 < len(FINAL):
        arpeggio(pc, q, at(9, t0), dd, 0.22 if big else 0.28, 0.7 if big else 0.5, pan=-0.1, gain=0.85)
        melody(pc, q, at(9, t0) + 0.1, dd - 0.1, kind, 0.85 if big else 0.6, oct_up=1 if big else 0, bright=0.7,
               ens=3 if big else 1, gain=0.9, pan=0.1)
add(choir([62, 66, 69, 74], 8.0, 0.3) * env_ar(int(8.0 * SR), 1.5, 3.0), at(9, 0.6), 0.5, pan=0.2)
add(choir([57, 62, 66, 69, 74], 5.0, 0.3) * env_ar(int(5.0 * SR), 0.8, 2.0), at(9, 8.4), 0.65)
for i, m in enumerate([86, 90, 93, 98]):
    add(bell(m, 2.5), at(9, 12.2 + 1.75 + i * 0.12), 0.10, pan=-0.3 + i * 0.2)

synth.master(os.environ.get("TRILHA_OUT", os.path.join(HERE, "trilha_prodigo.wav")))
