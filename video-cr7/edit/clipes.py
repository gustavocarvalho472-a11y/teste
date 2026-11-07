"""Baixa os clipes do Drive (pasta compartilhada por link) e gera folhas de contato com minutagem.
    python3 clipes.py baixar                 # baixa tudo de CLIPS
    python3 clipes.py folha v11_dublin 1.0   # folha com um quadro a cada 1.0 s
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "clips")
CLIPS = {  # nome: id do arquivo no Drive
    "v02_despedida": "1pJyz7G6sko51UycDHaPa48e8XrCy5TGh",
    "v03_meme_homelander": "1pW_RsP_ITnqyazV8ZqC6tTy4SfMLSKj1",
    "v04_tunel": "1ihmsksC636-Z71ZJQLvZ5noGHtkOBdpB",
    "v05_piers": "1NalcwzIyd3-EUx72H1Z2z7tcdYu78fD7",
    "v06_tb_starlight": "18qH2XidPOKcurJpS31umJOmxevVnB9sv",
    "v07_alnassr": "1pbNQOO3cx8_-2RJ4BCavc9sAY5Goi9WM",
    "v08_benzema": "10kdyc6_AZHiTum1WFnjcRqvHzEUSpoV3",
    "v09_greve": "1gAsBv3aPbdSWCtdht75vcifVyDJMwKlH",
    "v10_tb_stormfront": "1Fco9WZj3o1EuV0QVZRe-GsSqhmZ8JaaK",
    "v11_dublin": "1-q5uK5_bzZqO0GPrWjF17ur0Pn-uihY4",
    "v12_coletiva_irlanda": "1l_QrX7qs9b9-twwyGIDU8a_5uSTX0N1l",
    "v13_tb_multidao": "1p_IwCdAb8gQZGGEwUFrkiTzlV-a2I5Hd",
    "v14_tb_fio_branco": "1Nc5TABWg3DwiaQnGhNo5pN2utW_wHa95",
    "v15_congo": "1HlwHcdb2da4C-bPQfiKa8nlT19C1P-w5",
    "v16_uzbequistao": "1Sz45qxFt1JCbrR8t7n59NJVZS0p3AmlH",
    "v16_croacia": "15_B6JqLnE0aWJr2mzxtx8J9Mh7O9RmSJ",
    "v17_espanha": "1H66Um4V5l6kJPhr7F9xiecBb3UyPganF",
    "v17_lagrimas": "1FW6vSv0qSrWpu3nUj6--0QqWZoQhEDFR",
    "v18_gales": "1iZR5_x1d4UTL3LN-WRXT92YtmKUaSuMD",
    "v19_noruega": "1oW2oQ2fKsi7rjaINb6kObCT_5wh4oCD9",
    "v20_jesus_pele_maradona": "1bEt2qfSoTDO0I9XwzwHnLt9zj-d4sHcO",
    "v21_copenhague": "1yrjwmCWeEmN2lAdGIR1lYunjWq3MwHZp",
    "v22_tb_fora_do_roteiro": "1vGtXgYAY5VNevw00yx9bFYhEbAGGZo-i",
    "v24_tb_perde_poderes": "1omWy_kE-FNxW-EbJhUFps-KvhvMrsVIt",
}


def baixar(only=None):
    os.makedirs(OUT, exist_ok=True)
    for nm, fid in CLIPS.items():
        if only and nm not in only:
            continue
        p = os.path.join(OUT, nm + ".mp4")
        if os.path.exists(p) and os.path.getsize(p) > 100000:
            continue
        url = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
        r = subprocess.run(["curl", "-sSL", "--max-time", "900", "-o", p, url])
        ok = os.path.exists(p) and os.path.getsize(p) > 100000
        print(nm, "OK" if ok else "FALHOU", os.path.getsize(p) if os.path.exists(p) else 0, flush=True)


def info(nm):
    p = os.path.join(OUT, nm + ".mp4")
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", p],
                                  capture_output=True, text=True).stdout)
    v = [s for s in j["streams"] if s["codec_type"] == "video"][0]
    return float(j["format"]["duration"]), int(v["width"]), int(v["height"])


def folha(nm, step=1.0, t0=0.0, t1=None):
    from PIL import Image, ImageDraw
    p = os.path.join(OUT, nm + ".mp4")
    dur, w, h = info(nm)
    t1 = dur if t1 is None else min(t1, dur)
    tmp = os.path.join(OUT, "_f")
    os.makedirs(tmp, exist_ok=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", p, "-vf", f"fps=1/{step},scale=320:-2",
                    os.path.join(tmp, "f_%05d.jpg")], check=True)
    fs = sorted(os.listdir(tmp))
    cols = 6
    th = Image.open(os.path.join(tmp, fs[0])).height
    sheet = Image.new("RGB", (320 * cols, (th + 18) * ((len(fs) + cols - 1) // cols)), "black")
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(fs):
        x, y = (k % cols) * 320, (k // cols) * (th + 18)
        sheet.paste(Image.open(os.path.join(tmp, f)), (x, y))
        d.text((x + 4, y + th + 2), f"{t0 + k * step:6.1f}s", fill="yellow")
    out = os.path.join(OUT, f"_folha_{nm}.jpg")
    sheet.save(out, quality=80)
    print(out, f"dur={dur:.1f}s {w}x{h}")


if __name__ == "__main__":
    if sys.argv[1] == "baixar":
        baixar(sys.argv[2:] or None)
    else:
        folha(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0,
              float(sys.argv[4]) if len(sys.argv) > 4 else 0.0, float(sys.argv[5]) if len(sys.argv) > 5 else None)
