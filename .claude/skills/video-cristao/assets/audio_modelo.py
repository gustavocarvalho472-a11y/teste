"""Trilha + sound design de __TITULO__ (sintetizada, sem direitos autorais).

    TRILHA_OUT=trilha___NOME__.wav python3 __NOME___audio.py

A partitura é escrita no tempo ORIGINAL das cenas (SCENES0/STARTS0); se a narração esticou alguma cena,
synth.WARP reposiciona tudo automaticamente.
"""
import os

import numpy as np

import __NOME__ as proj
import synth

SCENES, STARTS = proj.SCENES0, proj.STARTS0
synth.setup(proj.TOTAL)
if proj.SCALE != [1.0] * len(proj.SCALE):
    import narracao
    synth.WARP = narracao.warp_fn(proj)
from synth import *  # noqa: E402,F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
T = lambda k: STARTS[k]  # noqa: E731
Dur = lambda k: SCENES[k][1]  # noqa: E731

# ── 0 · gancho: tensão (Ré menor), coração, pancada no "soco"
add(pad_chord(D, "m", Dur(0) + 1, 0.3, 0.8) * env_ar(int((Dur(0) + 1) * SR), 1.5, 1.5), T(0), 0.35)
for i, m in enumerate((62, 65, 69, 68)):
    add(piano(m, 3.0, 0.4), T(0) + 0.6 + i * 1.2, 0.6, pan=-0.2)
t = T(0) + 1.0
while t < T(1):
    add(heartbeat(0.6), t, 0.3)
    t += 1.0
add(timpani(42, 3.0, 1.2), T(0) + 3.0, 0.8)

# ── 1 · virada: luz (Fá maior → Dó), arpejo, coro
add(cymbal_swell(1.5), T(1) - 1.5, 0.3)
for k, (pc, q) in enumerate(((F, "M"), (C, "M"))):
    tc, dd = T(1) + k * Dur(1) / 2, Dur(1) / 2
    add(pad_chord(pc, q, dd + 1, 0.6, 1.0) * env_ar(int((dd + 1) * SR), 1.0, 1.2), tc, 0.5)
    arpeggio(pc, q, tc, dd, 0.25, 0.5, pan=-0.1, gain=0.8)
    melody(pc, q, tc + 0.2, dd - 0.2, "A", 0.6, gain=0.75)
add(choir([60, 65, 69, 72], Dur(1), 0.3) * env_ar(int(Dur(1) * SR), 2.0, 2.0), T(1) + 2, 0.4)

# ── 2 · final: explosão quente + sinos no inscreva-se
add(timpani(55, 4.0, 1.1), T(2), 0.8)
add(pad_chord(D, "M", Dur(2), 1.0, 1.2) * env_ar(int(Dur(2) * SR), 0.05, 3.0), T(2), 0.6)
add(choir([62, 66, 69, 74, 78], Dur(2) - 1, 0.3) * env_ar(int((Dur(2) - 1) * SR), 0.3, 3.0), T(2), 0.5)
for i, m in enumerate((86, 90, 93, 98)):
    add(bell(m, 2.5), T(2) + 8.0 + i * 0.12, 0.10, pan=-0.3 + i * 0.2)

synth.master(os.environ.get("TRILHA_OUT", os.path.join(HERE, "trilha___NOME__.wav")))
