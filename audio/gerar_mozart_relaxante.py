"""Andante em Fá maior no estilo de Mozart (piano + baixo de Alberti + cordas suaves),
lento e calmo, para estudar, descansar ou dormir.
Saída: mozart_relaxante.wav (44.1 kHz, estéreo)."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
rng = np.random.default_rng(1756)
F = lambda n: 440 * 2 ** ((n - 69) / 12)

# ---------------- instrumentos ----------------
_cache = {}
def piano(note, dur, vel):
    """Piano por síntese aditiva: parciais inarmônicas, decaimento por parcial, 2 cordas."""
    key = (note, round(dur, 2), round(vel, 1))
    if key in _cache:
        return _cache[key]
    rel = 0.6
    n = int((dur + rel) * SR); t = np.arange(n) / SR
    f0, B = F(note), 0.00035
    s = np.zeros(n)
    bright = 0.6 + 0.8 * vel
    for k in range(1, 11):
        fk = k * f0 * np.sqrt(1 + B * k * k)
        if fk > 9000:
            break
        amp = (1 / k ** (2.2 - bright)) * np.exp(-0.25 * (k - 1) * (1.2 - vel))
        dec = 0.6 + 0.35 * k + f0 / 600
        for det in (1.0, 1.0007):
            s += amp * np.sin(2 * np.pi * fk * det * t + rng.uniform(0, 6)) * np.exp(-t * dec * det)
    a = int(0.003 * SR); s[:a] *= np.linspace(0, 1, a)
    off = int(dur * SR); s[off:] *= np.exp(-np.arange(n - off) / SR * 9)
    s *= vel * 0.5
    _cache[key] = s
    return s

def strings(note, dur, vel):
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    f = F(note) * (1 + 0.003 * np.sin(2 * np.pi * 4.8 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph + rng.uniform(0, 6)) / k ** 1.6 for k in range(1, 8))
    s += 0.7 * sum(np.sin(k * ph * 1.004) / k ** 1.7 for k in range(1, 6))
    e = np.clip(t / 1.2, 0, 1) * np.clip((dur + 1.2 - t) / 1.2, 0, 1)
    return s * e * vel

# ---------------- partitura ----------------
# acordes: (baixo, (Alberti grave, médio, agudo))
CH = {"F": (41, (53, 57, 60)), "Bb": (46, (50, 53, 58)), "C": (36, (48, 52, 55)),
      "C7": (36, (48, 52, 58)), "Dm": (38, (50, 53, 57)), "Gm": (43, (50, 55, 58))}
A_ch = ["F", "Bb", "F", "C", "F", "Bb", "C7", "F"]
B_ch = ["Dm", "Gm", "C7", "F", "Bb", "Gm", "C", "C7"]
A_mel = [[(69,2),(72,1),(69,1)], [(70,1.5),(69,.5),(67,1),(74,1)], [(72,2),(69,1),(65,1)],
         [(67,2),(64,1),(67,1)], [(69,2),(72,1),(77,1)], [(74,1.5),(72,.5),(70,1),(74,1)],
         [(72,1),(69,1),(67,1),(64,1)], [(65,4)]]
B_mel = [[(77,2),(76,1),(74,1)], [(74,2),(70,1),(67,1)], [(76,1.5),(74,.5),(72,1),(70,1)],
         [(69,3),(72,1)], [(74,2),(77,1),(74,1)], [(70,2),(74,1),(70,1)],
         [(72,2),(76,1),(74,1)], [(72,2),(70,1),(67,1)]]
SCALE = [65, 67, 69, 70, 72, 74, 76]
def up(n):  # nota seguinte na escala de Fá maior
    pc = [s % 12 for s in SCALE]
    m = n + 1
    while m % 12 not in pc:
        m += 1
    return m

def ornament(bar):  # bordadura estilo clássico nas notas longas
    out = []
    for n, d in bar:
        if d >= 2:
            out += [(n, d - 1), (up(n), 0.5), (n, 0.5)]
        else:
            out.append((n, d))
    return out

form = A_ch + A_ch + B_ch + A_ch
mels = A_mel + A_mel + B_mel + A_mel
bars = []  # (acorde, melodia, transposição, seção)
for i in range(32): bars.append((form[i], mels[i], 0, 1))
for i in range(32): bars.append((form[i], ornament(mels[i]) if i % 8 not in (7,) else mels[i], 12 if i >= 16 else 0, 2))
for i in range(32): bars.append((form[i], mels[i], 0, 3))
bars.append(("F", [(65, 4)], 0, 4)); bars.append(("F", [(60, 4)], 0, 4))

# andamento: 54 BPM, ritardando final
bpm = np.full(len(bars), 54.0)
bpm[-12:] = np.linspace(54, 40, 12)
bar_len = 4 * 60 / bpm
starts = np.concatenate([[0], np.cumsum(bar_len)])
total = starts[-1] + 8
out_len = int(total * SR)
L = np.zeros(out_len); R = np.zeros(out_len)

def add(sig, t, pan, g):
    i = int(t * SR); j = min(i + len(sig), out_len)
    L[i:j] += sig[: j - i] * g * np.cos(pan * np.pi / 2)
    R[i:j] += sig[: j - i] * g * np.sin(pan * np.pi / 2)

for b, (ch, mel, tr, sec) in enumerate(bars):
    t0, bl = starts[b], bar_len[b]; beat = bl / 4
    root, (lo, mid, hi) = CH[ch]
    soft = 0.75 if sec == 3 else 1.0
    if sec == 4:  # final: acorde arpejado
        for k, n in enumerate([root, lo, mid, hi, mel[0][0] + 12]):
            add(piano(n, bl * 2 - k * 0.35, 0.35), t0 + k * 0.35, 0.4, 1.0)
        continue
    # baixo + Alberti (pedal segura até o fim do compasso)
    add(piano(root, bl, 0.38 * soft), t0, 0.35, 1.0)
    for k, n in enumerate([lo, hi, mid, hi] * 2):
        tt = t0 + k * beat / 2 + rng.normal(0, 0.006)
        v = (0.30 if k % 2 == 0 else 0.22) * soft
        add(piano(n, bl - k * beat / 2, round(v, 1) or 0.2), tt, 0.4, 0.8)
    # melodia
    tm = t0
    for n, d in mel:
        v = round(0.55 * soft + rng.normal(0, 0.03), 1)
        add(piano(n + tr, d * beat + 0.15, v), tm + rng.normal(0, 0.008), 0.6, 1.0)
        tm += d * beat
    # cordas suaves na seção 2 e início da 3
    if sec == 2 or (sec == 3 and b % 32 < 16):
        for k, n in enumerate((root + 12, mid, hi + 12 if sec == 2 else hi)):
            add(strings(n, bl, 0.025), t0, 0.2 + 0.3 * k, 1.0)

# ---------------- mixagem ----------------
ir_n = int(3.6 * SR)
tt = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-tt * 1.9)
irR = rng.standard_normal(ir_n) * np.exp(-tt * 1.9)
lp = butter(2, 4500, fs=SR, output="sos")
irL, irR = sosfilt(lp, irL), sosfilt(lp, irR)
pre = int(0.02 * SR); irL[:pre] = 0; irR[:pre] = 0
irL /= np.sqrt((irL ** 2).sum()) * 4; irR /= np.sqrt((irR ** 2).sum()) * 4
mix = np.stack([0.8 * L + fftconvolve(L + 0.3 * R, irL)[:out_len],
                0.8 * R + fftconvolve(R + 0.3 * L, irR)[:out_len]], axis=1)
mix = sosfilt(butter(2, [35, 7000], "bandpass", fs=SR, output="sos"), mix, axis=0)
mix /= np.abs(mix).max() / 0.85
fi = int(1.5 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(5 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
wavfile.write("mozart_relaxante.wav", SR, (mix * 32767).astype(np.int16))
print("duração: %d min %02d s" % divmod(int(total), 60))
