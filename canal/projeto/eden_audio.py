"""Trilha + sound design de O Éden não era o jardim (sintetizada, sem direitos autorais).

    TRILHA_OUT=trilha_eden.wav python3 eden_audio.py

Clima alegre e curioso: levada em Sol maior (I–V–vi–IV) com marimba, pizzicato, shaker e bumbo leve;
efeitos lúdicos sincronizados com a animação (pops dos alfinetes, papel, brilho mágico, passarinhos).
A partitura é escrita no tempo ORIGINAL das cenas; synth.WARP reposiciona se a narração esticar.
"""
import os

import numpy as np

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
rnd = np.random.default_rng(7)


# ───────────────────────── instrumentos alegres ─────────────────────────
def marimba(m, dur=0.9, vel=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    out = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 22)
    out += 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40)
    return out * np.minimum(1, t / 0.002) * vel


def pluck(m, dur=1.2, vel=0.7, bright=0.5):
    """Pizzicato / violão (Karplus-Strong)."""
    n = int(dur * SR)
    p = max(2, int(SR / mtof(m)))
    buf = rnd.uniform(-1, 1, p)
    out = np.zeros(n)
    k = 0.5 + 0.49 * bright
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = k * buf[i % p] + (1 - k) * buf[(i + 1) % p]
        buf[i % p] *= 0.996
    return lp(out, 3500) * vel


def shaker(vel=0.3):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    return hp(rnd.standard_normal(n), 6000) * np.exp(-t * 60) * vel


def kick(vel=0.6):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 55 * (1 + 2.5 * np.exp(-t * 35))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * vel


def snap(vel=0.4):
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    return lp(hp(rnd.standard_normal(n), 1200), 7000) * np.exp(-t * 35) * vel


def pop(m, vel=0.6):
    """'Plop' com glissando para cima (alfinete pousando)."""
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    f = mtof(m) * (0.6 + 0.4 * (1 - np.exp(-t * 60)))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * vel


def sparkle(m0=84, n=10, step=0.045, vel=0.25):
    """Brilho mágico: glissando de sininhos subindo pela escala maior."""
    scale = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28, 31]
    out = np.zeros(int((n * step + 2.0) * SR))
    for i in range(n):
        s = bell(m0 + scale[i % len(scale)], 1.6) * vel * (0.7 + 0.3 * i / n)
        a = int(i * step * SR)
        out[a:a + len(s)] += s[: len(out) - a]
    return out


def paper(dur=0.6, vel=0.25):
    n = int(dur * SR)
    x = hp(rnd.standard_normal(n), 1500) * (rnd.random(n) < 0.25)
    return lp(x, 8000) * np.sin(np.linspace(0, np.pi, n)) * vel


def chirp(vel=0.15):
    """Passarinho: dois piados rápidos."""
    out = []
    for _ in range(int(rnd.integers(2, 4))):
        n = int(rnd.uniform(0.06, 0.1) * SR)
        t = np.arange(n) / SR
        f0 = rnd.uniform(3200, 4200)
        f = f0 + 1500 * np.sin(np.pi * t / t[-1]) * rnd.choice([1, -1])
        out.append(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) ** 2)
        out.append(np.zeros(int(0.04 * SR)))
    return np.concatenate(out) * vel


# ───────────────────────── levada ─────────────────────────
BPM = 104
BEAT = 60 / BPM
PROG = [(G, "M"), (D, "M"), (E, "m"), (C, "M")]   # I – V – vi – IV


def chord_notes(pc, q):
    r = 55 + (pc - 7) % 12   # raiz entre G3 e F#4
    return [r, r + (3 if q == "m" else 4), r + 7]


def groove(t0, t1, dens=1.0, perc=True, bass=True, gain=1.0):
    """Toca a levada de t0 a t1 (segundos). dens < 1 deixa só os tempos fortes."""
    t = t0
    i = 0
    while t < t1 - 0.05:
        bar = int(i // 8)
        pc, q = PROG[bar % 4]
        notes = chord_notes(pc, q)
        step = i % 8
        if step in (0, 3, 6) or dens >= 1.0:
            m = notes[[0, 2, 1, 2, 0, 2, 1, 2][step]] + 12
            add(marimba(m, 0.8, 0.55 if step % 2 else 0.7), t, 0.32 * gain, pan=0.25 if step % 2 else -0.15)
        if bass and step in (0, 4):
            add(pluck(36 + pc, 1.2, 0.9, 0.3), t, 0.55 * gain, pan=-0.05)
        if perc:
            add(shaker(0.28 if step % 2 else 0.18), t, 0.5 * gain, pan=0.35)
            if step == 0 or step == 4:
                add(kick(0.7), t, 0.45 * gain)
            if step in (2, 6) and dens >= 1.0:
                add(snap(0.35), t, 0.35 * gain, pan=-0.2)
        t += BEAT / 2
        i += 1


# ── 0 · mapa: levada leve (marimba + shaker); cada alfinete é um 'plop' subindo a escala
add(paper(1.0, 0.35), T(0) + 0.1, 0.5)
groove(T(0) + 0.6, T(0) + 6.3, dens=0.6, bass=False, gain=0.8)
for i, tp in enumerate(proj.PIN_T):
    add(pop([67, 71, 74, 76, 79, 81, 83][i], 0.7), T(0) + tp, 0.5, pan=-0.5 + i * 0.16)
    add(marimba([79, 83, 86, 88, 91, 93, 95][i], 0.6, 0.5), T(0) + tp, 0.2, pan=-0.5 + i * 0.16)
# "uh-oh": os furos ficam vermelhos — tudo para, duas notas descendo, e a levada volta
add(marimba(76, 0.9, 0.8), T(0) + 6.4, 0.45)
add(marimba(72, 1.2, 0.8), T(0) + 6.65, 0.45)
add(pluck(36, 1.5, 0.9, 0.2), T(0) + 6.4, 0.4)
groove(T(0) + 7.2, T(1), dens=1.0, gain=0.85)

# ── 1 · a Bíblia: papel arrastando, página, brilho mágico na palavra
add(paper(0.8, 0.4), T(1) + 0.1, 0.45, pan=-0.3)
add(whoosh(0.9, up=True), T(1) + 0.5, 0.12, pan=0.4)
groove(T(1), T(1) + 2.4, dens=1.0, gain=0.8)
add(sparkle(84, 12, 0.04, 0.3), T(1) + 2.35, 0.45, pan=0.2)
groove(T(1) + 2.4, T(2), dens=0.6, perc=False, gain=0.7)
add(cymbal_swell(1.4), T(2) - 1.4, 0.18)

# ── 2 · linha do tempo: levada completa + melodia de sinos acompanhando o fio dourado
add(kick(0.9), T(2), 0.5)
add(sparkle(79, 6, 0.06, 0.25), T(2), 0.3, pan=-0.4)
groove(T(2), T(3) - 0.4, dens=1.0, gain=1.0)
mel = [(0.0, 83), (0.5, 86), (1.0, 88), (1.5, 86), (2.0, 91), (3.0, 88), (3.5, 86), (4.0, 83), (5.0, 86),
       (5.5, 88), (6.0, 91), (6.5, 95)]
for dt, m in mel:
    add(bell(m, 1.4) * 0.7, T(2) + 0.6 + dt * BEAT * 1.15, 0.16, pan=0.2)
    add(marimba(m, 0.6, 0.6), T(2) + 0.6 + dt * BEAT * 1.15, 0.16, pan=0.2)
add(sparkle(86, 10, 0.05, 0.25), T(2) + 4.9, 0.35, pan=0.4)   # arco ligando os jardins
add(choir([67, 71, 74, 79], 3.0, 0.4) * env_ar(int(3.0 * SR), 0.8, 1.5), T(2) + 5.0, 0.22)

# ── 3 · túmulo no jardim: a levada respira; acorde aberto, passarinhos, sininhos de mistério bom
add(pad_chord(C, "M", Dur(3) + 0.5, 0.7, 0.8) * env_ar(int((Dur(3) + 0.5) * SR), 0.6, 1.0), T(3), 0.28)
groove(T(3), T(4) - 0.3, dens=0.6, perc=False, bass=True, gain=0.6)
for k in range(5):
    add(chirp(0.18), T(3) + 0.6 + k * 1.1 + rnd.uniform(0, 0.4), 0.6, pan=rnd.uniform(-0.8, 0.8))
add(bell(88, 3.0), T(3) + 2.4, 0.1, pan=0.3)
add(bell(91, 3.0), T(3) + 2.7, 0.08, pan=0.3)
add(cymbal_swell(1.4), T(4) - 1.4, 0.3)

# ── 4 · título: pancada alegre (Sol maior), brilho e um último 'ta-dá' de marimba
add(kick(1.0), T(4), 0.6)
add(timpani(43, 2.0, 0.8), T(4), 0.5)
add(pad_chord(G, "M", Dur(4) + 2, 0.9, 1.0) * env_ar(int((Dur(4) + 2) * SR), 0.02, 2.5), T(4), 0.4)
add(sparkle(91, 10, 0.035, 0.3), T(4) + 0.1, 0.4)
for i, m in enumerate((79, 83, 86, 91)):
    add(marimba(m, 1.2, 0.8), T(4) + 0.05 + i * 0.07, 0.3, pan=-0.3 + i * 0.2)

synth.master(os.environ.get("TRILHA_OUT", os.path.join(HERE, "trilha_eden.wav")))
