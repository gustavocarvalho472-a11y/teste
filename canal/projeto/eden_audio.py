"""Trilha + sound design de O Éden não era o jardim (sintetizada, sem direitos autorais).

    TRILHA_OUT=trilha_eden.wav python3 eden_audio.py

A partitura é escrita no tempo ORIGINAL das cenas (SCENES0/STARTS0); se a narração esticou alguma cena,
synth.WARP reposiciona tudo automaticamente.
"""
import os

import eden as proj
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

# ── 0 · mapa: mistério (Ré menor); cada alfinete que pousa é uma nota; o vermelho dos furos é uma pancada
add(pad_chord(D, "m", Dur(0) + 1.5, 0.3, 0.8) * env_ar(int((Dur(0) + 1.5) * SR), 2.0, 1.5), T(0), 0.32)
for i, (tp, m) in enumerate(zip(proj.PIN_T, (74, 69, 72, 76, 74, 77, 81))):
    add(piano(m, 2.0, 0.55), T(0) + tp, 0.42, pan=-0.4 + i * 0.13)
    add(whoosh(0.4, up=False), T(0) + tp - 0.4, 0.05)
add(timpani(44, 3.0, 1.0), T(0) + 6.4, 0.7)
add(piano(50, 3.5, 0.7), T(0) + 6.4, 0.4)
add(piano(51, 3.5, 0.5), T(0) + 6.42, 0.25)

# ── 1 · a Bíblia: whoosh do recuo, sino quando a palavra acende
add(whoosh(1.2, up=True), T(1), 0.18)
add(pad_chord(Bb, "M", Dur(1) + 1, 0.4, 0.8) * env_ar(int((Dur(1) + 1) * SR), 1.0, 1.5), T(1), 0.3)
for i, m in enumerate((86, 93, 98)):
    add(bell(m, 3.0), T(1) + 2.4 + i * 0.09, 0.12, pan=0.2)
add(cymbal_swell(2.6), T(1) + Dur(1) - 2.6, 0.18)

# ── 2 · linha do tempo: calor (Fá maior → Dó), arpejo acompanhando o fio dourado; coro no arco
add(timpani(53, 2.5, 0.6), T(2), 0.4)
for k, (pc, q) in enumerate(((F, "M"), (C, "M"))):
    tc, dd = T(2) + k * Dur(2) / 2, Dur(2) / 2
    add(pad_chord(pc, q, dd + 1, 0.6, 1.0) * env_ar(int((dd + 1) * SR), 0.8, 1.2), tc, 0.4)
    arpeggio(pc, q, tc, dd, 0.22, 0.45, pan=-0.1, gain=0.7)
add(choir([65, 69, 72, 77], Dur(2) - 4.5, 0.3) * env_ar(int((Dur(2) - 4.5) * SR), 1.5, 1.5), T(2) + 4.8, 0.35)
for i, m in enumerate((84, 88, 91, 96)):
    add(bell(m, 2.5), T(2) + 7.0 + i * 0.12, 0.08, pan=-0.3 + i * 0.2)

# ── 3 · túmulo: silêncio quase total; cordas graves e uma nota suspensa
add(strings([50, 57, 62, 65], Dur(3) + 0.5, 0.35, 0.6) * env_ar(int((Dur(3) + 0.5) * SR), 1.5, 1.2), T(3), 0.35)
add(piano(81, 4.0, 0.35), T(3) + 1.0, 0.25, pan=0.3)
add(piano(76, 4.0, 0.3), T(3) + 3.0, 0.22, pan=-0.3)
add(cymbal_swell(1.6), T(4) - 1.6, 0.3)

# ── 4 · título: pancada + sino + acorde aberto
add(timpani(41, 3.5, 1.2), T(4), 0.9)
add(pad_chord(D, "M", Dur(4) + 2, 0.9, 1.1) * env_ar(int((Dur(4) + 2) * SR), 0.02, 2.5), T(4), 0.5)
add(choir([62, 66, 69, 74], Dur(4) + 1.5, 0.2) * env_ar(int((Dur(4) + 1.5) * SR), 0.1, 2.0), T(4), 0.35)
for i, m in enumerate((86, 90, 93)):
    add(bell(m, 3.0), T(4) + 0.5 + i * 0.12, 0.12)

synth.master(os.environ.get("TRILHA_OUT", os.path.join(HERE, "trilha_eden.wav")))
