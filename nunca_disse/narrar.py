# Narração de "Seis frases que Jesus nunca disse": lê as falas (linhas ">") do ROTEIRO.md, um wav por fala, e grava narr/timing.json.
import sys, os, re, json, glob
import soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
EN = os.environ.get("NARR_LANG") == "en"                                # NARR_LANG=en python3 narrar.py -> versão em inglês
SAY = {"“": "", "”": ""}  # ajustes de fala
lines, sec = [], ""
for l in open(f"{HERE}/ROTEIRO{'_EN' if EN else ''}.md", encoding="utf-8"):
    if l.startswith("## "): sec = l[3:].strip()
    if l.startswith(">"):
        t = l[1:].strip()
        for a, b in SAY.items(): t = t.replace(a, b)
        lines.append({"sec": sec, "text": t})
only = set(int(x) for x in sys.argv[1:])
VOICE, RATE, PITCH = ("en-US-AndrewNeural", "-8%", "-6Hz") if EN else ("pt-BR-AntonioNeural", "-8%", "-14Hz")             # Antonio, um pouco mais grave e calmo
import asyncio, ssl, subprocess, edge_tts, edge_tts.communicate as ec
ec._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")  # proxy do ambiente
def speak(text, wav):
    mp3 = wav[:-4] + ".mp3"
    import time
    for k in range(16):                                                   # o serviço limita requisições: espera e tenta de novo
        try: asyncio.run(edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(mp3)); break
        except Exception as e:
            if k == 15: raise
            w = min(300, 30 * (k + 1)); print("  tentando de novo em", w, "s:", str(e)[:40], flush=True); time.sleep(w)
    time.sleep(1.5)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af",
                    "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                    "-ar", "24000", "-ac", "1", wav], check=True)
    os.remove(mp3); a, sr = sf.read(wav); return len(a) / sr
d = f"{HERE}/narr_en" if EN else f"{HERE}/narr"; old = {}
if os.path.exists(f"{d}/timing.json"): old = {x["wav"]: x for x in json.load(open(f"{d}/timing.json"))}
for i, x in enumerate(lines):
    x["wav"] = f"{i:03d}.wav"; x["voice"] = VOICE + PITCH
    o = old.get(x["wav"], {})
    if not (only and i not in only) and o.get("text") == x["text"] and o.get("voice") == x["voice"] and not only:
        x["dur"] = o["dur"]; continue
    if only and i not in only: x["dur"] = o["dur"]; continue
    x["dur"] = speak(x["text"], f"{d}/{x['wav']}"); print(f"{i:03d} {x['dur']:.2f}s {x['text'][:60]}", flush=True)
json.dump(lines, open(f"{d}/timing.json", "w"), ensure_ascii=False, indent=1)
print("falas", len(lines), "total", round(sum(x["dur"] for x in lines), 1), "s")
