"""Gera uma peça curta em estilo barroco/clássico (Ré maior, progressão tipo Pachelbel)
para uso como trilha de vídeo. Saída: musica_classica.wav (44.1 kHz, estéreo)."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
BPM = 66
BEAT = 60 / BPM
rng = np.random.default_rng(7)

def freq(n):  # MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)

def env(n, a, r):
    e = np.ones(n)
    a, r = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    e[:a] = np.linspace(0, 1, a)
    e[n - r:] *= np.linspace(1, 0, r)
    return e

def strings(note, dur, vib=0.004):
    n = int(dur * SR); t = np.arange(n) / SR
    f = freq(note) * (1 + vib * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.4, 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph + rng.uniform(0, 6)) / k ** 1.3 for k in range(1, 12))
    # leve "ensemble": segunda voz desafinada
    s += 0.6 * sum(np.sin(k * ph * 1.003) / k ** 1.4 for k in range(1, 9))
    return s * env(n, 0.25, 0.35)

def harp(note, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * freq(note) * k * t) * np.exp(-t * (2.2 + k * 1.5)) / k ** 1.5 for k in range(1, 8))
    return s * env(n, 0.004, 0.05)

out_len = int((8 * 8 * 2 * BEAT + 8) * SR)
L = np.zeros(out_len); R = np.zeros(out_len)

def add(sig, start, pan, gain):
    i = int(start * SR); j = min(i + len(sig), out_len)
    L[i:j] += sig[: j - i] * gain * np.cos(pan * np.pi / 2)
    R[i:j] += sig[: j - i] * gain * np.sin(pan * np.pi / 2)

# Progressão: D A Bm F#m G D G A (2 tempos cada... aqui 4 tempos por acorde)
bass  = [38, 33, 35, 30, 31, 26, 31, 33]
chords = [[62, 66, 69], [61, 64, 69], [62, 66, 71], [61, 66, 69],
          [62, 67, 71], [62, 66, 69], [62, 67, 71], [61, 64, 69]]
# melodias em colcheias para variações
mel_a = [78, 76, 74, 73, 71, 69, 71, 73]  # descida clássica (uma nota por acorde)
mel_b = [[74,76,78,74],[73,71,73,76],[74,73,71,74],[73,71,69,73],
         [71,69,67,71],[69,74,73,71],[71,74,76,79],[78,76,73,69]]

bar = 4 * BEAT
for rep in range(8):
    for c in range(8):
        t0 = (rep * 8 + c) * bar / 2  # 2 tempos por acorde
        d = bar / 2
        if rep < 7:
            add(strings(bass[c], d + 0.3, 0.002), t0, 0.35, 0.22)       # cello/contrabaixo
        if rep >= 1:
            for k, nt in enumerate(chords[c]):                           # violas/pad
                add(strings(nt - 12, d + 0.3), t0, 0.3 + 0.2 * k, 0.05)
        if rep >= 1 and rep < 7:                                         # harpa arpejando
            arp = [bass[c] + 24] + chords[c] + [chords[c][1] + 12, chords[c][0]]
            for k in range(8):
                add(harp(arp[k % len(arp)], 1.2), t0 + k * d / 8, 0.65, 0.06)
        if rep in (2, 3):
            add(strings(mel_a[c], d + 0.3), t0, 0.55, 0.11)             # violino 1
        if rep in (4, 5, 6):
            for k, nt in enumerate(mel_b[c]):
                add(strings(nt, d / 4 + 0.25, 0.005), t0 + k * d / 4, 0.55, 0.10)
            if rep >= 5:
                add(strings(mel_a[c] - 3 if c % 2 else mel_a[c] - 4, d + 0.3), t0, 0.45, 0.06)  # violino 2
        if rep == 7:
            add(strings(mel_a[c], d + 0.3), t0, 0.55, 0.10)

# acorde final
tf = 8 * 8 * bar / 2
for nt in [38, 50, 62, 66, 69, 74]:
    add(strings(nt, 5.0), tf, 0.5, 0.09)

# reverb (resposta impulsiva sintética de sala)
ir_n = int(2.8 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 2.3)
ir = sosfilt(butter(2, 6000, fs=SR, output="sos"), ir); ir /= np.abs(ir).sum() ** 0.5 * 30
wetL = fftconvolve(L, ir)[:out_len]; wetR = fftconvolve(R, np.roll(ir, 211))[:out_len]
mix = np.stack([0.75 * L + wetL, 0.75 * R + wetR], axis=1)
mix = sosfilt(butter(2, 40, "hp", fs=SR, output="sos"), mix, axis=0)
mix /= np.abs(mix).max() / 0.89
fade = int(3 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
wavfile.write("musica_classica.wav", SR, (mix * 32767).astype(np.int16))
print("duração: %.1fs" % (len(mix) / SR))
