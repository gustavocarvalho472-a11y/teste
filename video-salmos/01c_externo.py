"""Usa uma narração gravada fora (ex.: Suno) no lugar do 01_tts.py + 01b_alinhar.py.

  python 01c_externo.py --audio work/suno_dl/x.wav --roteiro roteiro_x.json \
         [--ate "começo da última frase narrada"] [--outro 12] [--texto-final "Escreva amém nos comentários"]

Transcreve o áudio inteiro com faster-whisper (tempo por palavra), casa as palavras com o roteiro,
interpola as que não casarem e grava audio/narracao.wav + timeline.json (com "palavras"), no mesmo
formato que o resto do pipeline espera. O texto exibido é sempre o do roteiro.
"""
import argparse, json, re, difflib, unicodedata, subprocess
import numpy as np, soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("--audio", required=True)
ap.add_argument("--roteiro", required=True)
ap.add_argument("--ate", default="", help="corta o roteiro na frase que começa com este texto (inclusive)")
ap.add_argument("--tirar-fim", default="", help="texto removido do fim da última frase (ex.: ' Amém.')")
ap.add_argument("--inicio", type=float, default=1.0)
ap.add_argument("--outro", type=float, default=12.0, help="segundos depois da voz (música sobe)")
ap.add_argument("--texto-final", default="")
ap.add_argument("--tag-final", default="nascer_sol")
ap.add_argument("--tempo", type=float, default=1.0, help="o áudio foi esticado com este fator (ex.: 0.92); escala os tempos do Suno")
ap.add_argument("--suno-align", nargs="+", default=None,
                help="alinhamentos do Suno (audio-lyrics-alignment) da cadeia, em ordem: arq.json[:corte_s] ... "
                     "o corte é o continue_at da extensão seguinte; dispensa o Whisper")
a = ap.parse_args()

SR = 48000
def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

roteiro = json.load(open(a.roteiro, encoding="utf-8"))
if a.ate:
    k = next(i for i, f in enumerate(roteiro) if f["frase"].startswith(a.ate))
    roteiro = roteiro[:k + 1]
if a.tirar_fim and roteiro[-1]["frase"].endswith(a.tirar_fim):
    roteiro[-1] = {**roteiro[-1], "frase": roteiro[-1]["frase"][: -len(a.tirar_fim)]}

# áudio: estéreo 48 kHz, com silêncio no início e o outro no fim
x, sr = sf.read(a.audio, dtype="float32", always_2d=True)
if sr != SR:
    raise SystemExit(f"esperado {SR} Hz, veio {sr}")
voz_dur = len(x) / SR
pad0 = np.zeros((int(a.inicio * SR), x.shape[1]), np.float32)
pad1 = np.zeros((int(a.outro * SR), x.shape[1]), np.float32)
audio = np.concatenate([pad0, x, pad1])
sf.write("audio/narracao.wav", audio, SR)
total = len(audio) / SR

class W:
    def __init__(s, word, start, end): s.word, s.start, s.end = word, start, end

def palavras_suno(specs):
    """Junta os tokens do Suno (pedaços de palavra) em palavras, aplicando o deslocamento de cada trecho da cadeia."""
    out, off = [], 0.0
    for spec in specs:
        arq, _, corte = spec.partition(":")
        corte = float(corte) if corte else None
        chars = []
        for t in json.load(open(arq))["words"]:
            if corte is not None and t["start_s"] >= corte: break
            n = max(1, len(t["word"]))
            for k, ch in enumerate(t["word"]):
                a_ = t["start_s"] + (t["end_s"] - t["start_s"]) * k / n
                chars.append(((ch, (off + a_) / a.tempo, (off + t["start_s"] + (t["end_s"] - t["start_s"]) * (k + 1) / n) / a.tempo)))
        cur = []
        for ch in chars + [(" ", 0, 0)]:
            if ch[0].isspace():
                if cur:
                    # o Suno cola a pontuação no começo do token seguinte (".\n\nRep"): ela não conta no tempo
                    # da palavra, senão o fim da frase estica até o início da próxima e as legendas se sobrepõem
                    al = [c for c in cur if c[0].isalnum()] or cur
                    fim = al[-1][2]
                    for k in range(1, len(al)):  # última sílaba jogada para depois da pausa ('rit' ... 'o')
                        if al[k][1] - al[k - 1][2] > 0.35: fim = al[k - 1][2] + 0.09 * (len(al) - k); break
                    out.append(W("".join(c[0] for c in cur), al[0][1], fim)); cur = []
            else: cur.append(ch)
        off += corte if corte is not None else 0
    return out

# reconhecimento com tempo por palavra
mono = x.mean(1)
n16 = int(len(mono) * 16000 / SR)
y = np.interp(np.linspace(0, len(mono) - 1, n16), np.arange(len(mono)), mono).astype(np.float32)
if a.suno_align:
    rec = palavras_suno(a.suno_align)
else:
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
    segs, _ = model.transcribe(y, language="pt", word_timestamps=True, beam_size=5, vad_filter=False,
                               initial_prompt="Oração antes de dormir, ansiedade, Senhor, Jesus, amém.")
    rec = [w for s in segs for w in (s.words or [])]

palavras = [(i, p) for i, f in enumerate(roteiro) for p in f["frase"].split()]
A = [norm(p) for _, p in palavras]; B = [norm(w.word) for w in rec]
tempos = [None] * len(palavras)
for blk in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks():
    for k in range(blk.size):
        w = rec[blk.b + k]; tempos[blk.a + k] = [w.start, w.end]
casadas = sum(t is not None for t in tempos)
i = 0
while i < len(palavras):
    if tempos[i] is not None: i += 1; continue
    j = i
    while j < len(palavras) and tempos[j] is None: j += 1
    ini = tempos[i - 1][1] if i > 0 else 0.0
    fim = tempos[j][0] if j < len(palavras) else voz_dur
    fim = max(fim, ini)
    pesos = [len(p) + 2 for _, p in palavras[i:j]]; acc = ini
    for k, pw in zip(range(i, j), pesos):
        d = (fim - ini) * pw / sum(pesos); tempos[k] = [acc, acc + d]; acc += d
    i = j
last = 0.0
for t in tempos:
    t[0] = min(max(t[0], last), voz_dur); t[1] = min(max(t[1], t[0] + 0.05), voz_dur); last = t[0]

frases = []
for idx, f in enumerate(roteiro):
    ws = [(p, tempos[k]) for k, (fi, p) in enumerate(palavras) if fi == idx]
    ini, fim = ws[0][1][0] + a.inicio, ws[-1][1][1] + a.inicio
    frases.append({**f, "idx": idx, "wav": a.audio, "inicio": round(ini, 3), "fim": round(fim, 3),
                   "duracao": round(fim - ini, 3),
                   "palavras": [{"w": p, "ini": round(s + a.inicio, 3), "fim": round(e + a.inicio, 3)} for p, (s, e) in ws]})

if a.texto_final:
    ini = a.inicio + voz_dur + 1.5
    ws = a.texto_final.split(); passo = 2.4 / len(ws)
    frases.append({"bloco": frases[-1]["bloco"], "titulo_bloco": frases[-1]["titulo_bloco"], "frase": a.texto_final,
                   "tag_visual": a.tag_final, "mostrar_texto": False, "referencia": None, "idx": len(frases),
                   "destaque": a.texto_final.replace("amém", "*amém*") + ".", "rodape": "DEIXE O SEU PEDIDO DE ORAÇÃO", "so_destaque": True,
                   "wav": None, "inicio": round(ini, 3), "fim": round(total - 1.0, 3), "duracao": round(total - 1.0 - ini, 3),
                   "palavras": [{"w": w, "ini": round(ini + k * passo, 3), "fim": round(ini + (k + 1) * passo, 3)} for k, w in enumerate(ws)]})

json.dump({"duracao_total": round(total, 3), "motor": "externo", "voz": a.audio, "frases": frases},
          open("timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(roteiro)} frases, voz {voz_dur/60:.2f} min, total {int(total//60)}:{int(total%60):02d}")
print(f"{casadas}/{len(palavras)} palavras casadas ({100*casadas/len(palavras):.1f}%)")
for b in dict.fromkeys(f["bloco"] for f in frases):
    fs = [f for f in frases if f["bloco"] == b]
    print(f"  {b:12s} {fs[0]['inicio']/60:5.2f} min")
