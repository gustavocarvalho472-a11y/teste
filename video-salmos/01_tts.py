"""Gera um .wav por frase, monta audio/narracao.wav e timeline.json.

  python 01_tts.py                                   # Kokoro pm_alex, roteiro inteiro (38-42 min)
  python 01_tts.py --motor cartesia --voz Rafael \\
         --blocos abertura,salmo23,salmo91,bencao --meta 15-17

Cartesia: chave em CARTESIA_API_KEY (.env). Nunca escrever a chave no código.
"""
import argparse, json, hashlib, io, os, sys, time
import numpy as np, soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("--motor", default="kokoro", choices=["kokoro", "cartesia"])
ap.add_argument("--voz", default=None, help="kokoro: id (pm_alex); cartesia: nome ou id da voz")
ap.add_argument("--blocos", default="", help="lista separada por vírgula; vazio = todos")
ap.add_argument("--meta", default="38-42", help="faixa de duração em minutos")
ap.add_argument("--velocidade", type=float, default=None)
ap.add_argument("--amostra", default="", help="só gera esta frase em audio/amostras/<voz>.wav")
args = ap.parse_args()

PAUSA_FRASE, PAUSA_BLOCO, INICIO, FIM = 0.7, 2.5, 1.0, 6.0
SR = 24000
os.makedirs("audio/frases", exist_ok=True)


def carregar_env():
    for p in (".env", "../.env"):
        if os.path.exists(p):
            for linha in open(p, encoding="utf-8"):
                linha = linha.strip()
                if linha and not linha.startswith("#") and "=" in linha:
                    k, v = linha.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ---------------- motores ----------------
if args.motor == "kokoro":
    from kokoro_onnx import Kokoro
    VOZ = args.voz or "pm_alex"
    SPEED = args.velocidade or 0.88
    _k = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")

    def sintetizar(texto):
        s, sr = _k.create(texto, voice=VOZ, speed=SPEED, lang="pt-br")
        return np.asarray(s, np.float32), sr
else:
    import requests
    carregar_env()
    KEY = os.environ.get("CARTESIA_API_KEY")
    if not KEY:
        sys.exit("CARTESIA_API_KEY não encontrada no .env")
    API = "https://api.cartesia.ai"
    HDR = {"X-API-Key": KEY, "Cartesia-Version": "2025-04-16"}
    MODELO = os.environ.get("CARTESIA_MODELO", "sonic-3")
    SPEED = args.velocidade or 0.85

    def achar_voz(nome):
        if len(nome) == 36 and nome.count("-") == 4:
            return nome, nome
        cache = "audio/cartesia_vozes.json"
        if os.path.exists(cache):
            vozes = json.load(open(cache))
        else:
            vozes, cursor = [], None
            while True:
                q = {"limit": 100, "language": "pt"}
                if cursor: q["starting_after"] = cursor
                r = requests.get(f"{API}/voices", headers=HDR, params=q, timeout=60); r.raise_for_status()
                j = r.json(); data = j.get("data", j if isinstance(j, list) else [])
                vozes += data
                if not (isinstance(j, dict) and j.get("has_more")) or not data: break
                cursor = data[-1]["id"]
            json.dump(vozes, open(cache, "w"), ensure_ascii=False, indent=1)
        achadas = [v for v in vozes if v.get("name", "").lower().startswith(nome.lower())]
        if not achadas:
            sys.exit(f"voz '{nome}' não encontrada. Disponíveis: " + ", ".join(v['name'] for v in vozes[:40]))
        v = achadas[0]
        print(f"voz: {v['name']}  ({v['id']})")
        return v["id"], v["name"]

    VOZ_ID, VOZ = achar_voz(args.voz or "Rafael")

    def sintetizar(texto, tentativas=5):
        corpo = {
            "model_id": MODELO, "transcript": texto, "language": "pt",
            "voice": {"mode": "id", "id": VOZ_ID},
            "output_format": {"container": "wav", "encoding": "pcm_f32le", "sample_rate": SR},
            "generation_config": {"speed": SPEED},
        }
        for n in range(tentativas):
            r = requests.post(f"{API}/tts/bytes", headers=HDR, json=corpo, timeout=120)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 ** n); continue
            if r.status_code != 200:
                sys.exit(f"Cartesia {r.status_code}: {r.text[:300]}")
            x, sr = sf.read(io.BytesIO(r.content), dtype="float32")
            return (x if x.ndim == 1 else x.mean(1)), sr
        sys.exit("Cartesia: falhou após várias tentativas")


def trim(x, sr, thr=0.004, pad=0.04):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    p = int(pad * sr)
    return x[max(0, idx[0] - p): idx[-1] + p]


def frase_wav(texto):
    h = hashlib.md5(f"{args.motor}{VOZ}{SPEED}{texto}".encode()).hexdigest()[:10]
    path = f"audio/frases/{h}.wav"
    if not os.path.exists(path):
        x, sr = sintetizar(texto)
        assert sr == SR, sr
        sf.write(path, trim(x, sr), sr)
    return path


if args.amostra:
    os.makedirs("audio/amostras", exist_ok=True)
    x, _ = sf.read(frase_wav(args.amostra), dtype="float32")
    out = f"audio/amostras/{args.motor}_{VOZ.replace(' ', '_')}_{SPEED}.wav"
    sf.write(out, x, SR); print(out); sys.exit()

# ---------------- roteiro ----------------
roteiro = json.load(open("roteiro.json", encoding="utf-8"))
if args.blocos:
    quero = args.blocos.split(",")
    roteiro = [f for f in roteiro if f["bloco"] in quero]
    roteiro.sort(key=lambda f: quero.index(f["bloco"]))  # estável: mantém ordem interna
print(f"{len(roteiro)} frases, {sum(len(f['frase']) for f in roteiro)} caracteres")

pecas, timeline, t = [np.zeros(int(INICIO * SR), np.float32)], [], INICIO
t0 = time.time()
for i, item in enumerate(roteiro):
    x, _ = sf.read(frase_wav(item["frase"]), dtype="float32")
    if i > 0:
        gap = PAUSA_BLOCO if item["bloco"] != roteiro[i - 1]["bloco"] else PAUSA_FRASE
        pecas.append(np.zeros(int(round(gap * SR)), np.float32)); t += gap
    dur = len(x) / SR
    timeline.append({**item, "idx": i, "wav": frase_wav(item["frase"]),
                     "inicio": round(t, 3), "fim": round(t + dur, 3), "duracao": round(dur, 3)})
    pecas.append(x); t += dur
    if i % 25 == 0: print(f"{i}/{len(roteiro)}  {t/60:.1f} min de áudio  ({time.time()-t0:.0f}s)", flush=True)
pecas.append(np.zeros(int(FIM * SR), np.float32)); t += FIM
audio = np.concatenate(pecas)
sf.write("audio/narracao.wav", audio, SR)
json.dump({"duracao_total": round(len(audio) / SR, 3), "motor": args.motor, "voz": VOZ, "frases": timeline},
          open("timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = len(audio) / SR
lo, hi = map(float, args.meta.split("-"))
print(f"\nDuração total: {int(tot//60)}:{int(tot%60):02d}  ({tot/60:.2f} min)")
print(f"DENTRO da meta {args.meta} min" if lo * 60 <= tot <= hi * 60 else f"FORA da meta {args.meta} min: ajustar roteiro")
for b in dict.fromkeys(f["bloco"] for f in timeline):
    fs = [f for f in timeline if f["bloco"] == b]
    print(f"  {b:10s} começa {fs[0]['inicio']/60:5.2f} min, dura {(fs[-1]['fim']-fs[0]['inicio'])/60:4.2f} min")
