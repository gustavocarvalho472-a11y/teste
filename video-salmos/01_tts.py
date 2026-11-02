"""Gera um .wav por frase com Kokoro (pm_alex), monta narracao.wav e timeline.json."""
import json, hashlib, os, sys, time
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

VOZ, LANG, SPEED = "pm_alex", "pt-br", 0.88
PAUSA_FRASE, PAUSA_BLOCO, INICIO, FIM = 0.7, 2.5, 1.0, 6.0
SR = 24000
os.makedirs("audio/frases", exist_ok=True)
roteiro = json.load(open("roteiro.json", encoding="utf-8"))
k = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")

def trim(x, thr=0.004, pad=0.04):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    p = int(pad * SR)
    return x[max(0, idx[0] - p): idx[-1] + p]

pecas, timeline, t = [np.zeros(int(INICIO * SR), np.float32)], [], INICIO
t0 = time.time()
for i, item in enumerate(roteiro):
    h = hashlib.md5(f"{VOZ}{SPEED}{item['frase']}".encode()).hexdigest()[:10]
    path = f"audio/frases/{h}.wav"
    if not os.path.exists(path):
        s, sr = k.create(item["frase"], voice=VOZ, speed=SPEED, lang=LANG)
        sf.write(path, trim(np.asarray(s, np.float32)), sr)
    x, _ = sf.read(path, dtype="float32")
    if i > 0:
        gap = PAUSA_BLOCO if item["bloco"] != roteiro[i - 1]["bloco"] else PAUSA_FRASE
        pecas.append(np.zeros(int(round(gap * SR)), np.float32)); t += gap
    dur = len(x) / SR
    timeline.append({**item, "idx": i, "wav": path, "inicio": round(t, 3), "fim": round(t + dur, 3), "duracao": round(dur, 3)})
    pecas.append(x); t += dur
    if i % 25 == 0: print(f"{i}/{len(roteiro)}  {t/60:.1f} min de áudio  ({time.time()-t0:.0f}s)", flush=True)
pecas.append(np.zeros(int(FIM * SR), np.float32)); t += FIM
audio = np.concatenate(pecas)
sf.write("audio/narracao.wav", audio, SR)
json.dump({"duracao_total": round(len(audio) / SR, 3), "frases": timeline},
          open("timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = len(audio) / SR
print(f"\nDuração total: {int(tot//60)}:{int(tot%60):02d}  ({tot/60:.2f} min)")
ok = 38 * 60 <= tot <= 42 * 60
print("DENTRO da meta 38-42 min" if ok else "FORA da meta 38-42 min: ajustar roteiro")
for b in dict.fromkeys(f["bloco"] for f in timeline):
    fs = [f for f in timeline if f["bloco"] == b]
    print(f"  {b:10s} começa {fs[0]['inicio']/60:5.2f} min, dura {(fs[-1]['fim']-fs[0]['inicio'])/60:4.2f} min")
