"""Alinha cada palavra do roteiro ao áudio (faster-whisper com word timestamps) -> timeline.json ganha "palavras".

O texto exibido é sempre o do roteiro; o reconhecimento só fornece os tempos. Palavras que o
reconhecedor não casar recebem tempo interpolado entre as vizinhas, proporcional ao tamanho.
"""
import json, re, difflib, unicodedata, time
import numpy as np, soundfile as sf
from faster_whisper import WhisperModel

def carregar16k(path):
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    n = int(len(x) * 16000 / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)

def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

tl = json.load(open("timeline.json", encoding="utf-8"))
model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
t0, casadas, total = time.time(), 0, 0
for n, f in enumerate(tl["frases"]):
    palavras = f["frase"].split()
    segs, _ = model.transcribe(carregar16k(f["wav"]), language="pt", word_timestamps=True, beam_size=1,
                               initial_prompt=f["frase"], vad_filter=False, condition_on_previous_text=False)
    rec = [w for s in segs for w in (s.words or [])]
    a = [norm(p) for p in palavras]; b = [norm(w.word) for w in rec]
    tempos = [None] * len(palavras)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            w = rec[blk.b + k]; tempos[blk.a + k] = [w.start, w.end]
    # interpolação para as que faltaram (âncoras: início 0 e fim = duração da frase)
    dur = f["duracao"]
    i = 0
    while i < len(palavras):
        if tempos[i] is not None: i += 1; continue
        j = i
        while j < len(palavras) and tempos[j] is None: j += 1
        ini = tempos[i - 1][1] if i > 0 else 0.0
        fim = tempos[j][0] if j < len(palavras) else dur
        if fim < ini: fim = ini
        pesos = [len(p) + 2 for p in palavras[i:j]]; acc = ini
        for k, pw in zip(range(i, j), pesos):
            d = (fim - ini) * pw / sum(pesos); tempos[k] = [acc, acc + d]; acc += d
        i = j
    # garante monotonicidade e limites
    last = 0.0
    for tt in tempos:
        tt[0] = min(max(tt[0], last), dur); tt[1] = min(max(tt[1], tt[0] + 0.05), dur); last = tt[0]
    casadas += sum(1 for x in a if x in set(b)); total += len(a)
    f["palavras"] = [{"w": p, "ini": round(f["inicio"] + s, 3), "fim": round(f["inicio"] + e, 3)}
                     for p, (s, e) in zip(palavras, tempos)]
    if n % 40 == 0: print(f"{n}/{len(tl['frases'])}  {time.time()-t0:.0f}s", flush=True)
json.dump(tl, open("timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"ok: {total} palavras, ~{100*casadas/total:.1f}% reconhecidas pelo alinhador")
