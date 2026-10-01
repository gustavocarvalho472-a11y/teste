"""Sound design + trilha do teste "Tempo de Tela".

Camadas: ambiente do quarto, vibração e notificações do celular, rolagem do feed, coração,
caça-níquel (alavanca, rolos, quase-acerto, prêmio, vazio), tom de Shepard (feed infinito)
e um piano escuro que cresce. Partitura no tempo original; synth.WARP reposiciona na narração.
"""
import os

import numpy as np

import synth
import tela as proj

SCENES, STARTS = proj.SCENES0, proj.STARTS0
synth.setup(proj.TOTAL)
if proj.SCALE != [1.0] * len(proj.SCALE):
    import narracao
    synth.WARP = narracao.warp_fn(proj)
from synth import *  # noqa: E402,F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
T = lambda k: STARTS[k]  # noqa: E731


def tone(f, dur, decay=8.0, harm=((1, 1.0),)):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in harm) * np.exp(-t * decay)


def buzz(dur=0.35):
    """Vibração do celular: grave áspero com tremulação."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 170 * t)) * 0.5 + np.sin(2 * np.pi * 85 * t)
    return lp(s, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t)) * env_ar(n, 0.01, 0.05)


def ping(f=1318.5):
    """Notificação: duas notas curtas e brilhantes."""
    a = tone(f, 0.5, 9, ((1, 1), (2, 0.3), (3, 0.1)))
    b = tone(f * 1.335, 0.7, 7, ((1, 1), (2, 0.3)))
    out = np.zeros(int(0.85 * SR))
    out[:len(a)] += a
    i = int(0.11 * SR)
    out[i:i + len(b)] += b
    return out


def swipe():
    n = int(0.16 * SR)
    x = hp(rng.standard_normal(n), 2500) * np.sin(np.linspace(0, np.pi, n)) ** 2
    return x


def click(f=2400, dur=0.03):
    n = int(dur * SR)
    return hp(rng.standard_normal(n), f) * np.exp(-np.arange(n) / (0.004 * SR))


def clunk():
    out = timpani(70, 0.5, 0.9) * 0.7
    k = click(600, 0.08) * 1.5
    out[:len(k)] += k
    return out


def shepard(dur, up=True):
    """Tom de Shepard: sobe para sempre sem nunca chegar (o feed sem fim)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    rate = 1 / 6.0  # oitavas por segundo
    for k in range(7):
        pos = (k + (rate * t if up else -rate * t)) % 7
        f = 55 * 2 ** pos
        amp = np.exp(-0.5 * ((pos - 3.5) / 1.3) ** 2)
        ph = 2 * np.pi * np.cumsum(f) / SR
        out += amp * np.sin(ph)
    return out / 3 * env_ar(n, 1.5, 1.0)


# ── ambiente do quarto (zumbido baixo) durante o gancho
n = int((T(1) + 0.5) * SR)
add(lp(rng.standard_normal(n), 200) * 0.6 * env_ar(n, 0.5, 0.8), 0.0, 0.15)

# ── gancho: vibração, notificações, rolagem frenética
add(buzz(), 0.05, 0.45)
add(buzz(), 0.55, 0.45)
for tt, f in ((0.8, 1318.5), (2.2, 1174.7), (3.4, 1318.5)):
    add(ping(f), tt, 0.22, pan=0.25)
t = 0.4
while t < 5.4:
    add(swipe(), t, 0.10 + 0.04 * (t / 5.4), pan=rng.uniform(-0.3, 0.3))
    t += max(0.12, 0.42 - 0.06 * t)
# piano escuro (Ré menor) e drone
add(pad_chord(D, "m", 11.5, 0.25, 0.8, low=True) * env_ar(int(11.5 * SR), 2.0, 2.0), 0.3, 0.35)
for i, (dt, m) in enumerate(((0.6, 62), (1.8, 65), (3.0, 69), (4.2, 68))):
    add(piano(m, 3.0, 0.4), dt, 0.6, pan=-0.2)
# "Foi feito pra te manter aqui": tudo some, depois o golpe grave quando os fios aparecem
i0 = int(synth.warp(5.45) * SR)
i1 = int(synth.warp(7.1) * SR)
DUCK[i0:i1] = 0.12
DUCK[i1:i1 + int(0.4 * SR)] = np.linspace(0.12, 1, int(0.4 * SR))
add(timpani(42, 4.0, 1.3), 7.2, 0.9)
add(lp(rng.standard_normal(int(2.5 * SR)), 90) * env_ar(int(2.5 * SR), 0.02, 2.0) * 2, 7.2, 0.5)
add(piano(38, 5.0, 0.6), 7.25, 0.8)
add(piano(50, 5.0, 0.4), 7.25, 0.6)
t = 6.0
while t < T(1) - 0.2:
    add(heartbeat(0.7), t, 0.35)
    t += 1.0

# ── Ato I: caça-níquel
T1 = T(1)
for start, stops, targets in proj.SPINS:
    add(clunk(), T1 + start, 0.5, pan=0.4)
    tt = T1 + start + 0.15
    while tt < T1 + stops[-1]:
        add(click(), tt, 0.25, pan=0.1)
        tt += 0.05 + 0.08 * ((tt - T1 - start) / (stops[-1] - start)) ** 2
    for k, s in enumerate(stops):
        add(click(900, 0.06) * 2, T1 + s, 0.35, pan=-0.2 + k * 0.2)
# quase-acerto: "bwomp" descendente
n = int(0.7 * SR)
tt = np.arange(n) / SR
add(np.sin(2 * np.pi * np.cumsum(np.linspace(440, 160, n)) / SR) * np.exp(-tt * 3), T1 + 4.6, 0.25)
# prêmio: sinos + moedas
for i, m in enumerate((84, 88, 91, 96, 91, 96)):
    add(bell(m, 1.5), T1 + 8.8 + i * 0.09, 0.1, pan=-0.3 + i * 0.12)
for i in range(14):
    add(click(5000, 0.02) * 2, T1 + 8.9 + rng.uniform(0, 0.9), 0.15, pan=rng.uniform(-0.6, 0.6))
# vazio: zumbido seco
n = int(0.6 * SR)
add(lp(np.sign(np.sin(2 * np.pi * 110 * np.arange(n) / SR)), 600) * env_ar(n, 0.01, 0.2), T1 + 11.8, 0.2)
# música do Ato I: pulso tenso
add(pad_chord(Bb, "M", 6.5, 0.4, 0.8) * env_ar(int(6.5 * SR), 1.0, 1.5), T1, 0.3)
add(pad_chord(G, "m", 6.5, 0.4, 0.8) * env_ar(int(6.5 * SR), 1.0, 1.5), T1 + 6.2, 0.3)
for i in range(int(12.4 / 0.5)):
    add(piano(43 if i % 2 else 50, 0.6, 0.45), T1 + i * 0.5, 0.35, pan=-0.3)
# feed sem fim: Shepard + piano subindo
add(shepard(7.4), T1 + 12.6, 0.35)
add(pad_chord(D, "m", 7.5, 0.6, 0.9) * env_ar(int(7.5 * SR), 1.5, 1.5), T1 + 12.4, 0.4)
for i, m in enumerate((62, 65, 69, 72, 74, 77, 81)):
    add(piano(m, 2.5, 0.35 + 0.03 * i), T1 + 13.0 + i * 0.85, 0.6, pan=0.2)

# ── cartela final
T2 = T(2)
add(timpani(55, 3.0, 0.8), T2, 0.4)
add(pad_chord(D, "m", 3.6, 0.5, 0.8) * env_ar(int(3.6 * SR), 0.2, 2.0), T2, 0.4)
add(bell(86, 2.5), T2 + 0.3, 0.08)

synth.master(os.environ.get("TRILHA_OUT", os.path.join(HERE, "trilha_tela.wav")))
