"""Narração local com Kokoro TTS (open source, sem integrações) + sincronia com as cenas.

1) Gera as falas (uma vez) e calcula quanto cada cena precisa ser desacelerada para caber a voz:
       VIDEO_LANG=en python3 narracao.py prodigo
   → narr/prodigo_en_am_michael/*.wav + timing.json
2) Com VIDEO_NARRATION=<projeto>, o projeto lê timing.json e ajusta durações/legendas (apply()).
3) Mixa voz + trilha (música abaixa sob a voz):
       VIDEO_LANG=en python3 narracao.py prodigo --mix trilha_prodigo_en.wav trilha_prodigo_en_narrada.wav

Modelos (baixar uma vez em ~/tts): kokoro-v1.0.onnx e voices-v1.0.bin
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
"""
import importlib
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VOICE = {"en": "am_michael", "pt": "pm_alex"}
VOICE = os.environ.get("VIDEO_VOICE", DEFAULT_VOICE.get(os.environ.get("VIDEO_LANG", "pt"), "am_michael"))
TTS_LANG = {"a": "en-us", "b": "en-gb", "p": "pt-br"}[VOICE[0]]
SPEED = float(os.environ.get("VIDEO_VOICE_SPEED", "0.92"))
MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.expanduser("~/tts"))
GAP = 0.35    # respiro mínimo entre falas
TAIL = 0.7    # respiro após a última fala da cena
LEAD = 0.12   # a voz entra logo depois da legenda começar a aparecer


def _dir(projname, lang):
    return os.path.join(HERE, "narr", f"{projname}_{lang}_{VOICE}")


def _lines(proj, tr):
    """Por cena: [(início, texto falado, índice da legenda ou None)]."""
    out = []
    extra = getattr(proj, "NARRATION_EXTRA", {})
    for k, sc in enumerate(proj.SCENES):
        lines = [(cp[0], tr(cp[2]).replace("*", ""), j) for j, cp in enumerate(sc[3])]
        lines += [(t0, tr(txt).replace("*", ""), None) for t0, txt in extra.get(k, [])]
        out.append(sorted(lines, key=lambda x: x[0]))
    return out


def generate(projname):
    os.environ.pop("VIDEO_NARRATION", None)
    import render
    proj = importlib.import_module(projname)
    from kokoro_onnx import Kokoro
    import soundfile as sf
    tts = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    lang = render.LANG
    d = _dir(projname, lang)
    os.makedirs(d, exist_ok=True)
    scenes = []
    n = 0
    for k, lines in enumerate(_lines(proj, render.tr)):
        dur0 = proj.SCENES[k][1]
        items = []
        for start, text, cap in lines:
            audio, sr = tts.create(text, voice=VOICE, speed=SPEED, lang=TTS_LANG)
            path = os.path.join(d, f"{n:03d}.wav")
            sf.write(path, audio, sr)
            items.append({"start": start, "dur": len(audio) / sr, "wav": os.path.relpath(path, HERE),
                          "text": text, "caption": cap})
            n += 1
        # menor fator s tal que cada fala caiba antes da próxima e antes do fim da cena
        s = 1.0
        for a, b in zip(items, items[1:]):
            s = max(s, (a["dur"] + GAP + LEAD) / max(0.1, b["start"] - a["start"]))
        if items:
            last = items[-1]
            s = max(s, (last["dur"] + TAIL + LEAD) / max(0.1, dur0 - last["start"]))
        scenes.append({"scale": round(s, 4), "lines": items})
        print(f"cena {k}: x{s:.2f}  " + " | ".join(f'{i["dur"]:.1f}s' for i in items))
    with open(os.path.join(d, "timing.json"), "w") as f:
        json.dump({"voice": VOICE, "speed": SPEED, "scenes": scenes}, f, ensure_ascii=False, indent=1)
    print("OK:", d)


def apply(g, projname):
    """Ajusta SCENES/STARTS/TOTAL/SCALE do projeto (dicionário de globais `g`) para a narração."""
    import render
    path = os.path.join(_dir(projname, render.LANG), "timing.json")
    if not os.path.exists(path):
        raise SystemExit(f"Narração não gerada: rode  VIDEO_LANG={render.LANG} python3 narracao.py {projname}")
    timing = json.load(open(path))
    new, scale, narr = [], [], []
    acc = 0.0
    for (label, dur, fn, caps), info in zip(g["SCENES"], timing["scenes"]):
        s = info["scale"]
        caps2 = []
        for j, cp in enumerate(caps):
            st = cp[0] * s
            line = next((x for x in info["lines"] if x["caption"] == j), None)
            end = cp[1] * s
            if line:
                end = max(end, st + LEAD + line["dur"] + 0.2)
            caps2.append((st, min(end, dur * s - 0.05)) + tuple(cp[2:]))
        for x in info["lines"]:
            narr.append((acc + x["start"] * s + LEAD, os.path.join(HERE, x["wav"])))
        new.append((label, dur * s, _stretch(fn, s), caps2))
        scale.append(s)
        acc += dur * s
    g["SCENES0"], g["STARTS0"] = g["SCENES"], g["STARTS"]
    g["SCENES"] = new
    g["SCALE"] = scale
    g["NARRATION"] = narr
    starts, acc = [], 0.0
    for sc in new:
        starts.append(acc)
        acc += sc[1]
    g["STARTS"], g["TOTAL"] = starts, acc


def warp_fn(proj):
    """Converte um tempo da linha do tempo original para a linha do tempo narrada."""
    s0, s1, sc = proj.STARTS0, proj.STARTS, proj.SCALE

    def w(t):
        k = max([i for i, x in enumerate(s0) if x <= t] or [0])
        return s1[k] + (t - s0[k]) * sc[k]
    return w


def _stretch(fn, s):
    return lambda c, t, d: fn(c, t / s, d / s)


def _read(path):
    with wave.open(path) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16 if w.getsampwidth() == 2 else np.int32)
    a = a.reshape(-1, ch).astype(np.float64) / (32768 if a.dtype == np.int16 else 2 ** 31)
    return a, sr


def _read_float(path):
    import soundfile as sf
    a, sr = sf.read(path, always_2d=True)
    return a.mean(1), sr


def mix(projname, music_path, out_path):
    os.environ["VIDEO_NARRATION"] = projname
    proj = importlib.import_module(projname)
    music, sr = _read(music_path)
    voice = np.zeros(len(music))
    spans = []
    for t0, wav in proj.NARRATION:
        v, vsr = _read_float(wav)
        if vsr != sr:
            x = np.arange(int(len(v) * sr / vsr)) * vsr / sr
            v = np.interp(x, np.arange(len(v)), v)
        v = v / (np.sqrt(np.mean(v ** 2)) + 1e-9) * 0.11          # nivela todas as falas
        i0 = int(t0 * sr)
        v = v[: max(0, len(voice) - i0)]
        voice[i0:i0 + len(v)] += v
        spans.append((i0, i0 + len(v)))
    # ducking adaptativo: em cada fala a música fica pelo menos 8 dB abaixo da voz
    mono = music.mean(1)
    gain = np.ones(len(music))
    for a, b in spans:
        vr = np.sqrt(np.mean(voice[a:b] ** 2))
        mr = np.sqrt(np.mean(mono[a:b] ** 2)) + 1e-9
        g = min(0.45, vr / 10 ** (8 / 20) / mr)
        lo, hi = max(0, a - int(0.25 * sr)), min(len(gain), b + int(0.35 * sr))
        gain[lo:hi] = np.minimum(gain[lo:hi], g)
    k = int(0.3 * sr)
    duck = np.convolve(np.pad(gain, (k, k), mode="edge"), np.ones(k) / k, "same")[k:-k]
    # leve "sala" na voz
    ir = np.random.default_rng(1).standard_normal(int(0.35 * sr)) * np.exp(-np.arange(int(0.35 * sr)) / (0.07 * sr))
    ir /= np.sqrt(np.sum(ir ** 2))
    from scipy.signal import fftconvolve
    vroom = voice + fftconvolve(voice, ir)[: len(voice)] * 0.12
    out = music * duck[:, None] * 0.9 + vroom[:, None] * 1.0
    out /= np.max(np.abs(out)) + 1e-9
    out = np.tanh(out * 1.3) / np.tanh(1.3) * 0.93
    pcm = (out * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    print("OK:", out_path, f"{len(pcm) / sr:.1f}s, {len(proj.NARRATION)} falas")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--mix":
        mix(sys.argv[1], sys.argv[3], sys.argv[4])
    else:
        generate(sys.argv[1])
