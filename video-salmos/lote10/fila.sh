#!/bin/bash
# Fila de render: para cada vídeo, ativa, renderiza, mede loudness, gera cópias e apaga o mestre.
# Uso: nohup lote10/fila.sh r06 r07 r08 r09 r10 > lote10/fila.log 2>&1 &
# Retomar depois de queda: RETOMAR=1 nohup lote10/fila.sh r02 r03 ... > lote10/fila.log 2>&1 &
cd "$(dirname "$0")/.."
PY=~/venv-salmos/bin/python
for V in "$@"; do
  echo "=== $V $(date +%H:%M) ==="
  # espera outro render (ex.: o vídeo 5) terminar
  while pgrep -f "03_edit.py" >/dev/null; do sleep 20; done
  # restos de um render interrompido (arquivos pela metade) sempre saem; a trilha é refeita
  rm -f work/blocos/*.tmp.mp4 work/seg/*.tmp.mp4 work/audio_*.wav
  # RETOMAR=1: o primeiro vídeo da fila reaproveita blocos e segmentos prontos (ex.: depois de reiniciar o worker)
  [ -z "$RETOMAR" ] && rm -f work/blocos/*.mp4 work/seg/*.mp4
  RETOMAR=
  lote10/ativar.sh $V
  $PY 03_edit.py --final-suave 8 --musica-db -90 --saida out/oracao_$V.mp4 > lote10/render_$V.log 2>&1 || { echo "ERRO render $V"; continue; }
  tail -1 lote10/render_$V.log
  ffmpeg -hide_banner -nostats -i out/oracao_$V.mp4 -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness" | tail -1
  mkdir -p lote10/teste
  for s in 3.6 60 200; do ffmpeg -y -loglevel error -ss $s -i out/oracao_$V.mp4 -frames:v 1 -vf scale=960:-2 lote10/teste/${V}_$s.jpg; done
  lote10/copias.sh $V && rm -f out/oracao_$V.mp4
  echo "pronto $V $(date +%H:%M)"
done
echo "FILA_OK"
