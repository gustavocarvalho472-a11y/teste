"""Trilha (tensa, doc/trap lento em Ré menor), SFX e mixagem → build/mix.wav

Se existirem audio/musica.mp3 ou audio/sfx/<nome>.wav, eles substituem os sintetizados.
Mixagem do handoff: narração 0 dB, música −22 dB com ducking sob a voz, SFX −8 dB.
"""
import os
import subprocess

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

import timeline

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
rng = np.random.default_rng(7)


def db(x):
    return 10 ** (x / 20)


def lp(x, fc, o=2):
    return sosfilt(butter(o, fc / (SR / 2), "low", output="sos"), x)


def hp(x, fc, o=2):
    return sosfilt(butter(o, fc / (SR / 2), "high", output="sos"), x)


def bp(x, f1, f2, o=2):
    return sosfilt(butter(o, [f1 / (SR / 2), f2 / (SR / 2)], "band", output="sos"), x)


def env(n, a, r):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def tt(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


def norm(x, peak=0.9):
    return x / (np.abs(x).max() + 1e-9) * peak


# ── SFX ─────────────────────────────────────────────────────────────────────────────────────────────
def sfx_whoosh(d=0.55, low=False):
    t = tt(d)
    x = noise(d)
    f = (300 + 3500 * (t / d) ** 1.5) if not low else (80 + 600 * (t / d))
    out = np.zeros_like(x)
    for k in range(0, len(x), 1024):          # varredura de filtro em blocos
        fc = float(f[k])
        seg = bp(x[k:k + 1024], max(40, fc * 0.6), min(SR / 2 - 100, fc * 1.6))
        out[k:k + 1024] = seg
    e = np.sin(np.pi * t / d) ** 2
    return norm(out * e, 0.7 if low else 0.6)


def sfx_impact(d=0.9, f0=60, deep=False):
    t = tt(d)
    f = f0 * (1 + 2.5 * np.exp(-t * 18))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (3 if deep else 5))
    hit = lp(noise(d), 2500) * np.exp(-t * 30)
    return norm(np.tanh(1.8 * body) + 0.5 * hit, 0.95)


def sfx_boom():
    x = sfx_impact(2.2, 42, deep=True)
    tail = lp(noise(2.2), 200) * np.exp(-tt(2.2) * 2) * 0.4
    return norm(x + tail, 0.95)


def sfx_scratch():
    d = 0.5
    t = tt(d)
    f = 300 + 900 * np.sin(2 * np.pi * 6 * t) ** 2 * (1 - t / d)
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return norm(bp(saw + 0.3 * noise(d), 200, 4000) * env(len(t), 0.01, 0.1), 0.7)


def sfx_tv_off():
    d = 0.7
    t = tt(d)
    click = np.zeros(len(t))
    click[:200] = rng.standard_normal(200)
    tone = np.sin(2 * np.pi * np.cumsum(1200 * np.exp(-t * 6) + 60) / SR) * np.exp(-t * 4)
    hum = lp(noise(d), 120) * np.exp(-t * 3)
    return norm(click + 0.5 * tone + 0.6 * hum, 0.7)


def sfx_paper_rip():
    d = 0.55
    t = tt(d)
    am = (rng.random(len(t)) < 0.02).astype(float)
    am = lp(am, 60) * 40
    return norm(hp(noise(d), 1500) * np.clip(am, 0, 1) * env(len(t), 0.02, 0.15), 0.6)


def sfx_glitch():
    d = 0.45
    x = noise(d)
    x = np.round(x * 3) / 3                       # bitcrush
    gate = np.repeat(rng.random(int(d * 40)) > 0.4, SR // 40)[: len(x)]
    sq = np.sign(np.sin(2 * np.pi * 180 * tt(d)))
    return norm(bp(x, 300, 6000) * gate[: len(x)] + 0.3 * sq * gate[: len(x)], 0.5)


def sfx_cash_drop():
    d = 1.0
    t = tt(d)
    f = 900 * np.exp(-t * 2.5) + 60
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.01, 0.3)
    return norm(tone + 0.8 * sfx_impact(1.0, 50) * (t > 0.55), 0.8)


def sfx_shutter():
    d = 0.18
    x = np.zeros(int(d * SR))
    for o in (0, int(0.07 * SR)):
        x[o:o + 400] += hp(rng.standard_normal(400), 2000) * np.exp(-np.arange(400) / 80)
    return norm(x, 0.6)


def sfx_crack():
    d = 1.4
    t = tt(d)
    pops = (rng.random(len(t)) < 0.004 * np.exp(-t * 3)).astype(float) * rng.standard_normal(len(t))
    return norm(hp(pops, 800) * 3 + 0.6 * sfx_impact(1.4, 45), 0.85)


def sfx_notifs():
    out = np.zeros(int(2.0 * SR))
    for k in range(14):
        o = int(SR * 1.6 * (k / 14) ** 0.8)
        d = 0.12
        p = np.sin(2 * np.pi * (1760 if k % 2 else 2093) * tt(d)) * np.exp(-tt(d) * 30)
        out[o:o + len(p)] += p * (0.5 + 0.5 * k / 14)
    return norm(out, 0.5)


SFX = {"whoosh": sfx_whoosh, "whoosh_low": lambda: sfx_whoosh(0.9, True), "impact": sfx_impact,
       "boom": sfx_boom, "scratch": sfx_scratch, "tv_off": sfx_tv_off, "paper_rip": sfx_paper_rip,
       "glitch": sfx_glitch, "cash_drop": sfx_cash_drop, "shutter": sfx_shutter, "crack": sfx_crack,
       "notifs": sfx_notifs}


def load_audio(path):
    a, sr = sf.read(path, always_2d=True)
    a = a.mean(1)
    if sr != SR:
        a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    return a


def get_sfx(name, cache={}):
    if name not in cache:
        p = os.path.join(HERE, "audio", "sfx", name + ".wav")
        cache[name] = load_audio(p) if os.path.exists(p) else SFX[name]()
    return cache[name]


# ── música ──────────────────────────────────────────────────────────────────────────────────────────
def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def pad(notes, d):
    t = tt(d)
    x = np.zeros(len(t))
    for m in notes:
        for det in (-0.12, 0.0, 0.11):
            ph = rng.random()
            x += 2 * (((mtof(m + det) * t) + ph) % 1) - 1
    return lp(x / len(notes), 900) * env(len(t), 0.8, 1.2)


def sub808(m, d):
    t = tt(d)
    f = mtof(m) * (1 + 1.2 * np.exp(-t * 40))
    return np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 1.6)


def hat(d=0.05, v=1.0):
    return hp(noise(d), 7000) * np.exp(-tt(d) * 90) * v


def clap():
    d = 0.3
    x = bp(noise(d), 800, 5000)
    e = np.exp(-tt(d) * 25)
    for o in (0.01, 0.02):
        e += np.roll(np.exp(-tt(d) * 60), int(o * SR)) * 0.6
    return x * e * 0.5


def music(total, marks):
    n = int(total * SR)
    mus = np.zeros(n)

    def put(sig, t0, g=1.0):
        i = int(t0 * SR)
        if i >= n:
            return
        sig = sig[: n - i]
        mus[i:i + len(sig)] += sig * g

    bpm = 70
    beat = 60 / bpm
    bar = 4 * beat
    prog = [(50, [62, 65, 69]), (46, [62, 65, 70]), (43, [62, 67, 70]), (45, [61, 64, 69])]   # Dm Bb Gm A
    nbars = int(total / bar) + 1
    resolve_t = next((t for t, m in marks if m == "resolve"), total)
    for b in range(nbars):
        t0 = b * bar
        root, ch = prog[(b // 2) % 4]
        if t0 >= resolve_t:
            root, ch = 50, [62, 66, 69]          # Ré maior no fim
        if b % 2 == 0:
            put(pad([m - 12 for m in ch], 2 * bar + 1.5), t0, 0.28)
        if t0 < resolve_t:
            put(sub808(root - 12, beat * 2.2), t0, 0.55)
            put(sub808(root - 12, beat * 1.2), t0 + 2.5 * beat, 0.4)
            put(clap(), t0 + 2 * beat, 0.35)
            for k in range(8):
                put(hat(v=0.5 if k % 2 else 0.8), t0 + k * beat / 2, 0.18)
            if b % 4 == 3:
                for k in range(6):
                    put(hat(v=0.6), t0 + 3 * beat + k * beat / 6, 0.15)
    # bell melancólico a cada 4 compassos
    for b in range(0, nbars, 4):
        t0 = b * bar
        if t0 < resolve_t:
            for k, m in enumerate([74, 72, 69]):
                d = 2.0
                put(np.sin(2 * np.pi * mtof(m) * tt(d)) * np.exp(-tt(d) * 2.5), t0 + k * beat * 1.5, 0.12)
    # marcas: off = silêncio até o próximo "in"; up = +4 dB por 12 s
    gain = np.ones(n)
    state_on, last = True, 0.0
    first_in = next((t for t, m in marks if m == "in"), 0)
    gain[: int(first_in * SR)] = 0
    for t, m in marks:
        i = int(t * SR)
        if m == "off":
            j = next((int(t2 * SR) for t2, m2 in marks if t2 > t and m2 == "in"), n)
            gain[i:j] = 0
        elif m == "up":
            gain[i:i + int(12 * SR)] *= db(4)
    gain = smooth(gain, 0.25)                                                        # sem cliques
    # fade final
    f = int(4 * SR)
    gain[-f:] *= np.linspace(1, 0, f)
    return mus * gain


def smooth(x, win):
    """Média móvel centrada (soma acumulada: O(n), ao contrário de np.convolve com janela longa)."""
    k = max(1, int(win * SR))
    c = np.concatenate([[0], np.cumsum(x)])
    i = np.arange(len(x))
    a, b = np.clip(i - k // 2, 0, len(x)), np.clip(i + k // 2 + 1, 0, len(x))
    return (c[b] - c[a]) / (b - a)


def rms_env(x, win):
    return np.sqrt(np.maximum(smooth(x ** 2, win), 0))


def main():
    tm, blocks, shots, total = timeline.load()
    voice = load_audio(os.path.join(HERE, tm["audio"]))
    n = int(total * SR)
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    voice = voice / (np.sqrt(np.mean(voice[np.abs(voice) > 0.01] ** 2)) + 1e-9) * db(-18)   # voz ≈ −18 dBFS RMS

    mp = os.path.join(HERE, "audio", "musica.mp3")
    if os.path.exists(mp):
        m = load_audio(mp)
        m = np.tile(m, int(n / len(m)) + 1)[:n]
    else:
        m = music(total, timeline.music_marks(blocks))
    m = m / (np.sqrt(np.mean(m[np.abs(m) > 1e-4] ** 2)) + 1e-9) * db(-18 - 22 + 6)   # −22 dB sob a voz (+6 fora dela)
    v_env = rms_env(voice, 0.3)
    duck = np.clip(v_env / db(-30), 0, 1)
    m = m * (1 - duck * (1 - db(-6)))

    fx = np.zeros(n)
    for t, name in timeline.events(blocks, shots):
        s = get_sfx(name)
        i = int(t * SR)
        s = s[: max(0, n - i)]
        fx[i:i + len(s)] += s
    fx = fx * db(-18 - 8 + 12)        # pico dos SFX ≈ −8 dB abaixo do pico da voz

    mix = voice + m + fx
    peak = np.abs(mix).max()
    if peak > 0.97:
        mix = np.tanh(mix / peak * 1.1) * 0.95
    st = np.stack([mix, mix], 1).astype(np.float32)
    out = os.path.join(timeline.BUILD, "mix.wav")
    sf.write(out, st, SR)
    print("OK", out, f"{total:.1f}s")


if __name__ == "__main__":
    main()
