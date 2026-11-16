#!/usr/bin/env python3
"""Narração gratuita com Kokoro (voz padrão do canal). Gera um MP3 por texto.

Uso:
  python3 tts_kokoro.py --voice am_michael --out assets/vo/ch1.mp3 --text-file ch1.txt
  python3 tts_kokoro.py --voice am_michael --beats beats.json --outdir assets/vo
     (beats.json = [{"id": "ch1_b00", "text": "..."}, ...] -> um MP3 por beat + durations.json)

Requisitos: Python 3.10-3.12, `pip install kokoro soundfile`, `apt-get install -y espeak-ng`,
e acesso a huggingface.co (o modelo Kokoro-82M baixa na primeira execução).
NÃO foi testado no ambiente em que a skill foi escrita (Python 3.13, huggingface bloqueado):
valide com uma frase curta antes de gerar o vídeo inteiro.
"""
import argparse, json, os, subprocess, sys
import numpy as np


def synth(pipeline, text, voice, speed):
    import soundfile as sf  # noqa: F401  (garante a dependência cedo)
    parts = [np.asarray(audio) for _, _, audio in pipeline(text, voice=voice, speed=speed)]
    return np.concatenate(parts) if parts else np.zeros(1, dtype=np.float32)


def save_mp3(audio, path):
    import soundfile as sf
    wav = path[:-4] + ".wav"; sf.write(wav, audio, 24000)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-ar", "48000", "-b:a", "192k", path], check=True)
    os.remove(wav); return len(audio) / 24000


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="am_michael")  # inglês americano masculino; bm_george = britânico
    ap.add_argument("--lang", default="a")            # a = inglês americano, b = britânico, p = português BR
    ap.add_argument("--speed", type=float, default=0.95)
    ap.add_argument("--text-file"); ap.add_argument("--out")
    ap.add_argument("--beats"); ap.add_argument("--outdir")
    a = ap.parse_args()
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=a.lang)
    if a.beats:
        os.makedirs(a.outdir, exist_ok=True); durs = {}
        for b in json.load(open(a.beats)):
            durs[b["id"]] = save_mp3(synth(pipe, b["text"], a.voice, a.speed), f"{a.outdir}/{b['id']}.mp3")
            print(b["id"], round(durs[b["id"]], 2), flush=True)
        json.dump(durs, open(f"{a.outdir}/durations.json", "w"), indent=1)
    elif a.text_file and a.out:
        print(round(save_mp3(synth(pipe, open(a.text_file).read(), a.voice, a.speed), a.out), 2))
    else:
        sys.exit("informe --text-file/--out ou --beats/--outdir")
