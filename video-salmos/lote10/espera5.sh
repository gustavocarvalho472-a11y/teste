#!/bin/bash
# termina o vídeo 5 (que já está renderizando): espera, mede, faz cópias
cd "$(dirname "$0")/.."
while pgrep -f "03_edit.py" >/dev/null; do sleep 20; done
tail -1 lote10/render_r05.log
ffmpeg -hide_banner -nostats -i out/oracao_r05.mp4 -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness" | tail -1
for s in 3.6 60 200; do ffmpeg -y -loglevel error -ss $s -i out/oracao_r05.mp4 -frames:v 1 -vf scale=960:-2 lote10/teste/r05_$s.jpg; done
lote10/copias.sh r05 && rm -f out/oracao_r05.mp4
echo "pronto r05"
