"""Biblioteca de efeitos sonoros sintetizados (48 kHz, mono float). Sem direitos autorais.
Cada função devolve um np.ndarray. `make(nome)` escolhe pelo nome usado nos CUES da timeline."""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
_r = np.random.default_rng(11)


def _t(d):
    return np.arange(int(d * SR)) / SR


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos"), x)


def lp(x, fc, o=2):
    return sosfilt(butter(o, min(fc, SR * 0.45), "low", fs=SR, output="sos"), x)


def hp(x, fc, o=2):
    return sosfilt(butter(o, fc, "high", fs=SR, output="sos"), x)


def noise(d):
    return _r.standard_normal(int(d * SR))


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / max(d, 1e-4))
    return e


def sweep(f0, f1, d, curve=2.0):
    t = _t(d)
    f = f1 + (f0 - f1) * np.exp(-t * curve / d * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def sat(x, k=2.0):
    return np.tanh(x * k) / np.tanh(k)


def pad(x, d):
    out = np.zeros(int(d * SR))
    out[:min(len(x), len(out))] = x[:len(out)]
    return out


def mixa(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def verb(x, dur=1.2, mix=0.25, lpf=6000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = lp(_r.standard_normal(n) * np.exp(-t / (dur / 4.5)), lpf)
    ir /= np.sqrt(np.sum(ir ** 2))
    from scipy.signal import fftconvolve
    wet = fftconvolve(x, ir)[:len(x) + n]
    return mixa(x, wet * mix)


# ───────── básicos ─────────
def thump(f0=95, f1=45, d=0.35, a=0.9):
    return sweep(f0, f1, d) * env(int(d * SR), 0.002, d / 4) * a


def click(d=0.006, lo=2500, hi=9000):
    return bp(noise(d), lo, hi) * env(int(d * SR), 0.0003, d / 3)


def shutter():
    c1 = pad(click(0.007), 0.12)
    c2 = np.zeros(int(0.12 * SR))
    k = int(0.038 * SR)
    cc = click(0.009, 1800, 7000) * 0.8
    c2[k:k + len(cc)] = cc
    mech = pad(bp(noise(0.03), 300, 1200) * env(int(0.03 * SR), 0.001, 0.008) * 0.5, 0.12)
    return norm(c1 + c2 + mech, 0.7)


def slap(d=0.07, lo=700, hi=4000):
    return bp(noise(d), lo, hi) * env(int(d * SR), 0.001, d / 5)


# ───────── efeitos da timeline ─────────
def drop():
    return norm(mixa(shutter() * 0.8, pad(slap() * 0.7, 0.4), thump(110, 55, 0.3, 0.9)), 0.8)


def drop_heavy():
    return norm(verb(mixa(shutter() * 0.6, pad(slap(0.09) * 0.8, 0.6), thump(80, 38, 0.7, 1.0),
                          pad(lp(noise(0.5), 200) * env(int(0.5 * SR), 0.003, 0.12) * 0.6, 0.6)), 0.9, 0.18), 0.9)


def type_(n=11):
    out = np.zeros(int(1.1 * SR))
    t = 0.0
    for i in range(n):
        k = int(t * SR)
        key = mixa(click(0.008, 2000, 8000) * _r.uniform(0.5, 1.0),
                   bp(noise(0.03), 180, 700) * env(int(0.03 * SR), 0.001, 0.008) * 0.6)
        out[k:k + len(key)] += key[:len(out) - k]
        t += _r.uniform(0.045, 0.095)
        if t > 1.0:
            break
    return norm(out, 0.6)


def whoosh(d=0.65, up=True, low=False):
    n = int(d * SR)
    x = noise(d)
    out = np.zeros(n)
    st = 10
    for k in range(st):
        a, b = k * n // st, (k + 1) * n // st
        fr = k / (st - 1)
        fc = 300 + 5000 * (fr ** 2 if up else (1 - fr) ** 2)
        out[a:b] = bp(x, max(80, fc * 0.4), fc * 1.6)[a:b]
    tt = np.linspace(0, 1, n)
    e = np.sin(np.pi * tt) ** 1.5
    out *= e
    if low:
        out += lp(noise(d), 160) * e * 1.5
    return norm(out, 0.7)


def whoosh_big():
    return norm(mixa(whoosh(1.2, True, True), pad(thump(60, 30, 0.9, 0.6), 1.2)[::-1] * 0.0), 0.8)


def marker(d=0.5):
    n = int(d * SR)
    t = np.arange(n) / SR
    am = 0.55 + 0.45 * np.sin(2 * np.pi * (19 + 4 * np.sin(t * 7)) * t)
    x = bp(noise(d), 1800, 5200) * am * env(n, 0.02, d * 0.6)
    squeak = np.sin(2 * np.pi * (1300 + 300 * np.sin(t * 9)) * t) * 0.08 * env(n, 0.01, 0.12)
    return norm(x + squeak, 0.45)


def pluck(f=98.0, d=0.9):
    n = int(d * SR)
    p = int(SR / f)
    buf = _r.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return norm(lp(out, 2500) * env(n, 0.001, d / 3), 0.6)


def ping():
    t = _t(0.35)
    x = (np.sin(2 * np.pi * 1318.5 * t) + 0.4 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 14)
    return norm(x, 0.35)


def stamp_(big=False):
    body = thump(75 if big else 95, 38 if big else 48, 0.5 if big else 0.32, 1.0)
    rub = pad(bp(noise(0.09), 250, 2200) * env(int(0.09 * SR), 0.001, 0.02), 0.6)
    mech = pad(click(0.012, 900, 4000) * 0.6, 0.6)
    parts = [body, rub * 0.9, mech]
    if big:
        sub = sweep(55, 28, 1.6) * env(int(1.6 * SR), 0.003, 0.45) * 1.1
        parts.append(sub)
    x = mixa(*parts)
    return norm(sat(verb(x, 1.0 if big else 0.6, 0.22), 1.6), 0.95 if big else 0.85)


def paper(d=0.6):
    n = int(d * SR)
    t = np.arange(n) / SR
    crk = (_r.random(n) < 0.02).astype(float) * _r.uniform(0.3, 1, n)
    x = bp(noise(d), 900, 6000) * (0.35 + 0.65 * np.abs(np.sin(t * 13))) + hp(crk, 2000) * 0.6
    return norm(x * env(n, 0.05, d * 0.5), 0.5)


def jet(d=1.6):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = noise(d)
    out = np.zeros(n)
    st = 16
    for k in range(st):
        a, b = k * n // st, (k + 1) * n // st
        fr = k / (st - 1)
        fc = 2400 - 1900 * fr
        out[a:b] = bp(x, fc * 0.5, fc * 1.4)[a:b]
    tone = np.sin(2 * np.pi * np.cumsum(900 - 500 * t / d) / SR) * 0.15
    e = np.exp(-((t - d * 0.45) / (d * 0.28)) ** 2)
    return norm((out + tone) * e, 0.6)


def boom(d=1.8, f0=80, f1=34):
    body = sweep(f0, f1, d) * env(int(d * SR), 0.004, d / 3.2)
    tr = pad(lp(noise(0.12), 900) * env(int(0.12 * SR), 0.001, 0.03), d)
    return norm(sat(verb(mixa(body, tr * 0.7), 1.6, 0.28), 1.8), 0.95)


def boom_deep():
    return norm(mixa(boom(3.2, 62, 26), pad(whoosh(0.5, False) * 0.3, 3.2)), 1.0)


def laser(d=0.9):
    t = _t(d)
    f = 2600 * np.exp(-t * 4) + 180
    car = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.5
    hum = np.sin(2 * np.pi * 60 * t) * 0.4 + np.sin(2 * np.pi * 120 * t) * 0.2
    crack = hp(noise(d), 3000) * 0.25
    x = (lp(car, 6000) + hum + crack) * env(len(t), 0.005, d / 2.5)
    return norm(sat(x, 1.5), 0.8)


def glitch(d=0.45):
    n = int(d * SR)
    out = np.zeros(n)
    pos = 0
    while pos < n:
        L = int(_r.uniform(0.012, 0.05) * SR)
        kind = _r.integers(0, 3)
        if kind == 0:
            seg = np.round(noise(L / SR) * 3) / 3
        elif kind == 1:
            tt = np.arange(L) / SR
            seg = np.sign(np.sin(2 * np.pi * _r.uniform(200, 2200) * tt))
        else:
            seg = np.zeros(L)
        out[pos:pos + L] = seg[:n - pos] * _r.uniform(0.3, 1)
        pos += L
    hitp = pad(thump(120, 50, 0.3, 1.0), d)
    return norm(lp(out, 7000) * 0.5 + hitp, 0.85)


def tick_roll(d=0.9):
    out = np.zeros(int(d * SR))
    t = 0.0
    gap = 0.07
    while t < d - 0.02:
        k = int(t * SR)
        c = click(0.004, 3000, 9000)
        out[k:k + len(c)] += c[:len(out) - k]
        t += gap
        gap = max(0.022, gap * 0.9)
    return norm(out, 0.5)


def swell(d=2.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = hp(noise(d), 3500) * (t / d) ** 3
    return norm(x * (1 - np.exp(-(d - t) * 30)), 0.35)


def riser(d=3.6):
    n = int(d * SR)
    t = np.arange(n) / SR
    nz = noise(d)
    out = np.zeros(n)
    st = 18
    for k in range(st):
        a, b = k * n // st, (k + 1) * n // st
        fc = 300 + 7000 * (k / (st - 1)) ** 2
        out[a:b] = bp(nz, fc * 0.6, fc * 1.4)[a:b]
    tone = np.sin(2 * np.pi * np.cumsum(110 * 2 ** (3 * t / d)) / SR) * 0.35
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * (4 + 14 * t / d) * t)
    x = (out + tone) * (t / d) ** 2.2 * trem
    return norm(x, 0.75)


def riser_short():
    return riser(1.2)


def slam_cut():
    return norm(mixa(boom(1.4, 70, 30), pad(slap(0.12, 200, 1500), 1.4) * 0.8, pad(click(0.01, 800, 3000), 1.4)),
                1.0)


def phone_buzz():
    t = _t(0.3)
    b = np.sign(np.sin(2 * np.pi * 150 * t)) * 0.4 * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t))
    b = lp(b, 900) * env(len(t), 0.01, 0.2)
    return norm(mixa(pad(b, 0.8), np.concatenate([np.zeros(int(0.42 * SR)), b])), 0.5)


def snap():
    cr = hp(noise(0.05), 1500) * env(int(0.05 * SR), 0.0005, 0.008)
    tw = pluck(146.8, 0.7)
    t = _t(0.7)
    tw = tw * np.exp(-t * 2)
    return norm(mixa(pad(cr, 0.7) * 1.4, tw * 0.7), 0.85)


def memory(d=2.4):
    t = _t(d)
    notes = [62, 69, 74, 77]  # ré menor aberto, cristalino
    x = np.zeros(len(t))
    for i, m in enumerate(notes):
        f = 440 * 2 ** ((m - 69) / 12)
        on = (t > i * 0.12).astype(float)
        x += np.sin(2 * np.pi * f * t) * np.exp(-np.maximum(0, t - i * 0.12) * 1.6) * on * 0.5
        x += np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-np.maximum(0, t - i * 0.12) * 3) * on * 0.15
    rev = swell(0.6)
    return norm(verb(mixa(pad(rev * 0.4, d), x), 2.5, 0.5), 0.45)


def counter(d=0.95):
    out = np.zeros(int(d * SR))
    t, gap, f = 0.0, 0.05, 1200
    while t < d - 0.02:
        k = int(t * SR)
        tt = _t(0.02)
        c = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 300) * 0.6 + pad(click(0.003), 0.02) * 0.3
        out[k:k + len(c)] += c[:len(out) - k]
        t += gap
        gap = max(0.028, gap * 0.95)
        f *= 1.01
    return norm(out, 0.45)


def lock():
    return norm(mixa(thump(140, 60, 0.4, 1.0), pad(click(0.015, 600, 3000), 0.4) * 0.8,
                     pad(np.sin(2 * np.pi * 1760 * _t(0.25)) * np.exp(-_t(0.25) * 18) * 0.2, 0.4)), 0.85)


def braam(d=3.0):
    t = _t(d)
    x = np.zeros(len(t))
    for f, g in ((55, 1.0), (55 * 1.5, 0.6), (110, 0.6), (55 * 1.006, 0.8), (110 * 0.994, 0.4)):
        ph = 2 * np.pi * f * t
        saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
        x += saw * g
    x = lp(x, 520, 4)
    e = np.minimum(1, t / 0.06) * np.exp(-t / 1.1)
    sub = np.sin(2 * np.pi * 41 * t) * np.exp(-t / 0.9) * 0.9
    return norm(sat(verb((x * 0.6 + sub) * e, 2.0, 0.35), 2.2), 1.0)


def click_():
    return norm(mixa(click(0.004, 3000, 10000), pad(click(0.006, 1500, 5000) * 0.6, 0.05)), 0.6)


def ding():
    t = _t(1.2)
    x = sum(np.sin(2 * np.pi * 1046.5 * r * t) * g * np.exp(-t * d) for r, g, d in
            ((1, 1, 3), (2.0, 0.4, 5), (2.76, 0.25, 7)))
    return norm(verb(x, 1.0, 0.3), 0.4)


def check():
    return norm(mixa(marker(0.18) * 0.8, pad(thump(200, 90, 0.08, 0.4), 0.18)), 0.5)


def crowd(d=3.2):
    n = int(d * SR)
    out = lp(noise(d), 1400) * 0.25
    t = np.arange(n) / SR
    rate = 60
    k = 0
    nclap = int(rate * d)
    for i in range(nclap):
        pos = int(_r.uniform(0, n - 600))
        c = bp(noise(0.012), 700, 3500) * env(int(0.012 * SR), 0.0005, 0.003) * _r.uniform(0.2, 0.8)
        out[pos:pos + len(c)] += c
    e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
    return norm(verb(out * e, 1.5, 0.4), 0.5)


def tv_on():
    t = _t(0.5)
    st = hp(noise(0.5), 2000) * np.exp(-t * 6) * 0.5
    wh = np.sin(2 * np.pi * 15700 * t) * 0.05
    return norm(st + wh + pad(thump(160, 80, 0.12, 0.5), 0.5), 0.5)


def crt_off():
    t = _t(1.2)
    wh = np.sin(2 * np.pi * np.cumsum(9000 * np.exp(-t * 3) + 300) / SR) * 0.12 * np.exp(-t * 3)
    pop = pad(thump(180, 60, 0.15, 1.0), 1.2)
    st = hp(noise(1.2), 2500) * (_r.random(len(t)) < 0.05) * np.exp(-t * 4) * 0.8
    return norm(wh + pop + st, 0.8)


def tear(d=0.8):
    n = int(d * SR)
    t = np.arange(n) / SR
    crk = (_r.random(n) < 0.06).astype(float) * _r.uniform(0.2, 1, n)
    x = bp(noise(d), 800, 7000) * (0.4 + 0.6 * (_r.random(n) < 0.3)) + hp(crk, 1500)
    x *= env(n, 0.02, d * 0.45) * (1 - t / d) ** 0.5
    return norm(x, 0.7)


def spot_off():
    t = _t(1.4)
    clunk = pad(mixa(thump(120, 60, 0.25, 1.0), pad(click(0.02, 400, 2500), 0.3)), 1.4)
    hum = (np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 100 * t)) * np.exp(-t * 2.5) * 0.3
    return norm(clunk + hum, 0.75)


def heartbeat(vel=1.0):
    a = thump(62, 40, 0.22, 1.0)
    b = thump(56, 36, 0.32, 0.75)
    out = np.zeros(int(0.9 * SR))
    out[:len(a)] += a
    k = int(0.2 * SR)
    out[k:k + len(b)] += b
    return norm(lp(out, 180), 0.95)


def slide(d=1.2):
    return norm(mixa(whoosh(d, False) * 0.7, bp(noise(d), 200, 1200) * np.linspace(1, 0, int(d * SR)) * 0.3), 0.6)


def lens():
    t = _t(0.8)
    sh = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) * g for f, g, dcy in ((2093, 0.5, 5), (3136, 0.3, 7), (4186, 0.2, 9)))
    return norm(mixa(sh, whoosh(0.4, True) * 0.4), 0.4)


def rewind(d=1.4):
    t = _t(d)
    f = 900 * np.exp(-t * 1.2) + 120
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    chat = (np.sin(2 * np.pi * np.cumsum(f * 0.25) / SR) > 0.7).astype(float)
    x = lp(saw, 3000) * 0.4 + hp(noise(d), 2000) * chat * 0.3
    x *= np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1)
    return norm(x, 0.6)


TABLE = {
    "drop": drop, "drop_heavy": drop_heavy, "type": type_, "whoosh": whoosh, "whoosh_big": whoosh_big,
    "whoosh_up": lambda: whoosh(0.9, True, True), "marker": marker, "pluck": pluck, "ping": ping,
    "stamp": lambda: stamp_(False), "stamp_big": lambda: stamp_(True), "paper": paper, "jet": jet, "boom": boom,
    "boom_deep": boom_deep, "laser": laser, "glitch": glitch, "tick_roll": tick_roll, "swell": swell,
    "riser": riser, "riser_short": riser_short, "slam_cut": slam_cut, "phone_buzz": phone_buzz, "snap": snap,
    "memory": memory, "counter": counter, "lock": lock, "braam": braam, "click": click_, "ding": ding,
    "check": check, "crowd": crowd, "tv_on": tv_on, "crt_off": crt_off, "tear": tear, "spot_off": spot_off,
    "heartbeat": heartbeat, "slide": slide, "lens": lens, "rewind": rewind,
}
_CACHE = {}


def make(name):
    if name not in _CACHE:
        _CACHE[name] = TABLE[name]()
    return _CACHE[name]
