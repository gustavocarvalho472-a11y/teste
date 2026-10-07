import sys, os, json, glob
sys.path.insert(0, glob.glob("/root/.claude/skills/synced/*/video-ilustracao/toolkit")[0])
os.environ["VIDEO_LANG"] = "pt"
import narracao, soundfile as sf
from kokoro_onnx import Kokoro
LINES = [
 "Davi derrubou um gigante de quase três metros com uma única pedra.",
 "Mas a parte mais importante dessa história não aconteceu no campo de batalha.",
 "Aconteceu antes. Sozinho. Cuidando de ovelhas que ninguém via.",
 "Ali ele enfrentou leão e urso. Ali ele aprendeu a tocar.",
 "Foi ungido rei ainda jovem. E não ganhou a coroa. Voltou pro pasto.",
 "Só se tornou rei aos trinta anos.",
 "Hoje a gente vive o contrário: tudo é palco. Tudo precisa ser visto.",
 "Mas Deus não escolheu Davi pelo que as pessoas viam.",
 "O homem vê o exterior, mas o Senhor vê o coração.",
 "Talvez o seu tempo escondido não seja atraso. Seja treino.",
 "Quem vence o gigante em público já venceu o leão em secreto.",
 "Só que o maior gigante da vida de Davi não foi Golias. Foi ele mesmo. Isso fica pra parte dois.",
]
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "narr")
tts = Kokoro(os.path.expanduser("~/tts/kokoro-v1.0.onnx"), os.path.expanduser("~/tts/voices-v1.0.bin"))
out = []
for i, t in enumerate(LINES):
    a, sr = narracao.speak(tts, t)
    p = f"{d}/{i:02d}.wav"; sf.write(p, a, sr)
    out.append({"text": t, "wav": os.path.basename(p), "dur": len(a) / sr})
    print(f"{i}: {len(a)/sr:.2f}s")
json.dump(out, open(f"{d}/timing.json", "w"), ensure_ascii=False, indent=1)
print("total", sum(x["dur"] for x in out))
