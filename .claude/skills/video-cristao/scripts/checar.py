"""Controle de qualidade: grade de quadros + transcrição da voz (você não ouve; o Whisper ouve por você).

    python3 checar.py quadros <nome> <pt|en> <saida.png> t1 t2 t3 ...   [--short t0:t1]
    python3 checar.py voz <arquivo.mp4|.wav> <pt|en> [inicio fim]

`quadros` renderiza só os instantes pedidos (rápido) e monta uma grade para você olhar com Read.
`voz` imprime a transcrição com tempos: compare com o roteiro e caça palavras trocadas
(ex.: "lique" no lugar de "like", "de ele" no lugar de "dEle").
"""
import glob
import os
import subprocess
import sys
import tempfile

TK = os.environ.get("TOOLKIT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../video-jesus"))


def quadros(nome, lang, out, times, short=None):
    from PIL import Image
    tmp = tempfile.mkdtemp()
    env = dict(os.environ, VIDEO_LANG=lang, VIDEO_NARRATION=nome)
    mode = f"short:{short.split(':')[0]}" if short else "wide"
    subprocess.run([sys.executable, "engine.py", "snap", nome, mode, f"{tmp}/q", *times], cwd=TK, env=env,
                   check=True, stdout=subprocess.DEVNULL)
    fs = sorted(glob.glob(f"{tmp}/q_*.png"))
    tw, th = (270, 480) if short else (640, 360)
    cols = 4 if short else 2
    ims = [Image.open(f).resize((tw, th)) for f in fs]
    grid = Image.new("RGB", (tw * cols, th * ((len(ims) + cols - 1) // cols)))
    for k, im in enumerate(ims):
        grid.paste(im, ((k % cols) * tw, (k // cols) * th))
    grid.save(out)
    print("grade:", out, "| quadros:", ", ".join(times))


def voz(path, lang, a=None, b=None):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", compute_type="int8")
    kw = {"clip_timestamps": f"{a},{b}"} if a else {}
    for s in m.transcribe(path, language=lang, **kw)[0]:
        print(f"{s.start:6.1f}  {s.text.strip()}")


if __name__ == "__main__":
    if sys.argv[1] == "quadros":
        args = sys.argv[2:]
        short = None
        if "--short" in args:
            i = args.index("--short")
            short = args[i + 1]
            args = args[:i] + args[i + 2:]
        quadros(args[0], args[1], os.path.abspath(args[2]), args[3:], short)
    else:
        voz(*sys.argv[2:])
