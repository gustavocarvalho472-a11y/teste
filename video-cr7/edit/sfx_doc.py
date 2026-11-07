"""Efeitos 'documentário de futebol': poucos, graves e quentes. Nada metálico (sem parciais agudos
que ressoam, sem cliques secos). Tudo passa por passa-baixa e reverb escura."""
import numpy as np

from sfx import SR, _t, bp, env, hp, lp, mixa, noise, norm, pad, sweep, verb

_r = np.random.default_rng(23)


def boom_soft(d=3.0):
    """Impacto de cinema: sub que desce + corpo de ruído grave, cauda longa e escura."""
    body = sweep(58, 30, d) * env(int(d * SR), 0.012, d / 3.5)
    air = lp(noise(d), 260) * env(int(d * SR), 0.02, 0.35) * 0.5
    return norm(verb(mixa(body, air), 2.8, 0.35, lpf=2200), 0.9)


def hit_low(d=1.6):
    """Batida grave curta (corte para o preto / virada)."""
    body = sweep(72, 38, d) * env(int(d * SR), 0.006, 0.28)
    knock = pad(lp(noise(0.08), 500) * env(int(0.08 * SR), 0.002, 0.02), d) * 0.5
    return norm(verb(mixa(body, knock), 1.8, 0.25, lpf=1800), 0.85)


def whoosh_soft(d=0.7):
    """Passagem de ar discreta (passa-baixa em 2.2 kHz)."""
    n = int(d * SR)
    x = noise(d)
    out = np.zeros(n)
    st = 10
    for k in range(st):
        a, b = k * n // st, (k + 1) * n // st
        fr = k / (st - 1)
        fc = 220 + 1900 * np.sin(np.pi * fr) ** 2
        out[a:b] = lp(x, fc)[a:b]
    tt = np.linspace(0, 1, n)
    return norm(out * np.sin(np.pi * tt) ** 2, 0.45)


def zap_soft(d=1.0):
    """Energia do laser sem chiado: zumbido grave que incha e some."""
    t = _t(d)
    hum = np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110 * t) + 0.2 * np.sin(2 * np.pi * 165 * t)
    nz = lp(noise(d), 900) * 0.4
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return norm(lp((hum + nz) * e, 1200), 0.5)


def swell_soft(d=2.2):
    """Crescendo de ar (respiração da trilha) — sem agudos."""
    n = int(d * SR)
    t = np.arange(n) / SR
    x = bp(noise(d), 300, 2500) * (t / d) ** 2.5
    return norm(x * (1 - np.exp(-(d - t) * 25)), 0.4)


def riser_soft(d=2.4):
    n = int(d * SR)
    t = np.arange(n) / SR
    nz = noise(d)
    out = np.zeros(n)
    st = 14
    for k in range(st):
        a, b = k * n // st, (k + 1) * n // st
        fc = 250 + 2600 * (k / (st - 1)) ** 2
        out[a:b] = lp(nz, fc)[a:b]
    tone = np.sin(2 * np.pi * np.cumsum(55 * 2 ** (1.0 * t / d)) / SR) * 0.6
    return norm((out * 0.6 + tone) * (t / d) ** 2, 0.55)


def rewind_soft(d=1.4):
    """Fita voltando: ruído filtrado que 'acelera', abafado."""
    n = int(d * SR)
    t = np.arange(n) / SR
    rate = 6 + 26 * (t / d) ** 1.5
    am = 0.55 + 0.45 * np.sin(2 * np.pi * np.cumsum(rate) / SR)
    x = bp(noise(d), 180, 1600) * am
    e = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.25)
    return norm(lp(x * e, 1800), 0.4)


def tv_off_soft():
    """TV desligando: 'tum' grave + ar curto. Sem o apito agudo."""
    d = 1.0
    pop = pad(sweep(140, 55, 0.25) * env(int(0.25 * SR), 0.003, 0.06), d)
    air = pad(lp(noise(0.35), 1400) * env(int(0.35 * SR), 0.004, 0.08) * 0.4, d)
    return norm(verb(mixa(pop, air), 1.2, 0.3, lpf=1600), 0.7)


TABLE = {"boom_soft": boom_soft, "hit_low": hit_low, "whoosh_soft": whoosh_soft, "zap_soft": zap_soft,
         "swell": swell_soft, "riser_soft": riser_soft, "rewind_soft": rewind_soft, "tv_off_soft": tv_off_soft}
_C = {}


def make(name):
    if name not in _C:
        _C[name] = TABLE[name]()
    return _C[name]
