# Narração do vídeo longo: lê as falas (linhas ">") do ROTEIRO.md, gera um wav por fala e grava narr/timing.json.
import sys, os, re, json, glob
sys.path.insert(0, glob.glob("/root/.claude/skills/synced/*/video-ilustracao/toolkit")[0])
os.environ["VIDEO_LANG"] = "pt"
import narracao, soundfile as sf
from kokoro_onnx import Kokoro
HERE = os.path.dirname(os.path.abspath(__file__))
SAY = {"1 Samuel 16:7.": "Primeiro Samuel, dezesseis, sete."}  # como a referência deve ser falada
lines, sec = [], ""
for l in open(f"{HERE}/ROTEIRO.md", encoding="utf-8"):
    if l.startswith("## "): sec = l[3:].strip()
    if sec.startswith("Prompts") or l.startswith("# Prompts"): break
    if l.startswith(">"):
        t = l[1:].strip()
        for a, b in SAY.items(): t = t.replace(a, b)
        lines.append({"sec": sec, "text": t})
only = set(int(x) for x in sys.argv[1:])
tts = Kokoro(os.path.expanduser("~/tts/kokoro-v1.0.onnx"), os.path.expanduser("~/tts/voices-v1.0.bin"))
d = f"{HERE}/narr"; old = {}
if os.path.exists(f"{d}/timing.json"): old = {x["wav"]: x for x in json.load(open(f"{d}/timing.json"))}
for i, x in enumerate(lines):
    x["wav"] = f"{i:03d}.wav"
    if only and i not in only and x["wav"] in old and old[x["wav"]]["text"] == x["text"]:
        x["dur"] = old[x["wav"]]["dur"]; continue
    a, sr = narracao.speak(tts, x["text"]); sf.write(f"{d}/{x['wav']}", a, sr)
    x["dur"] = len(a) / sr; print(f"{i:03d} {x['dur']:.2f}s {x['text'][:60]}", flush=True)
json.dump(lines, open(f"{d}/timing.json", "w"), ensure_ascii=False, indent=1)
print("falas", len(lines), "total", round(sum(x["dur"] for x in lines), 1), "s")
