#!/usr/bin/env python3
"""
Vídeo simples: divide o tempo total entre as imagens, cada uma com zoom lento,
vinheta, tom quente e fade suave entre elas. Só precisa de ffmpeg.

Uso:
  python3 render.py --audio musica.mp3                 # duração = duração do áudio
  python3 render.py --duracao 7200                     # 2h sem áudio
  python3 render.py --audio musica.mp3 --imagens minhas_fotos/
"""
import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FPS = 24


def duracao(arquivo):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(arquivo)], capture_output=True, text=True, check=True)
    return float(out.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--imagens", default=HERE / "assets" / "images")
    ap.add_argument("--audio")
    ap.add_argument("--duracao", type=float, help="segundos (se não tiver áudio)")
    ap.add_argument("--zoom", type=float, default=0.15, help="zoom total por imagem (0.15 = 15%%)")
    ap.add_argument("--fade", type=float, default=2, help="segundos de fade entre imagens")
    ap.add_argument("--saida", default=HERE / "output" / "video.mp4")
    a = ap.parse_args()

    imgs = sorted(p for p in Path(a.imagens).iterdir()
                  if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    total = duracao(a.audio) if a.audio else a.duracao
    if not imgs or not total:
        raise SystemExit("precisa de imagens e de --audio ou --duracao")
    cada = total / len(imgs)
    frames = int(cada * FPS)
    print(f"{len(imgs)} imagens x {cada / 60:.1f} min cada = {total / 60:.1f} min")

    tmp = Path(a.saida).parent / "partes"
    tmp.mkdir(parents=True, exist_ok=True)
    partes = []
    for i, img in enumerate(imgs):
        parte = tmp / f"{i:03d}.mp4"
        filtro = (
            # recorta para 16:9 e amplia (zoom mais suave)
            "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
            # zoom lento e contínuo no centro
            f"zoompan=z='1+{a.zoom}*on/{frames}':d={frames}:s=1920x1080:fps={FPS}"
            ":x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2',"
            # efeitos leves: tom quente + vinheta + fade de entrada/saída
            "colorbalance=rh=0.04:bh=-0.04,vignette=PI/5,"
            f"fade=in:d={a.fade},fade=out:st={cada - a.fade:.2f}:d={a.fade},format=yuv420p"
        )
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats", "-i", img, "-vf", filtro,
                        "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "23", "-tune", "stillimage", parte], check=True)
        partes.append(parte)
        print(f"  imagem {i + 1}/{len(imgs)} ok")

    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p.resolve()}'\n" for p in partes))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista]
    if a.audio:
        cmd += ["-i", a.audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", a.saida]
    subprocess.run([str(c) for c in cmd], check=True)
    print(f"pronto: {a.saida}")


if __name__ == "__main__":
    main()
