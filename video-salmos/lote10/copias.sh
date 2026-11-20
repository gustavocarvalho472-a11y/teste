#!/bin/bash
# uso: lote10/copias.sh r03  -> out/r03/oracao_r03_envio.mp4 (1080p) e _720p.mp4; apaga o mestre no fim
cd "$(dirname "$0")/.."; V=$1; mkdir -p out/$V
nice -n 15 ffmpeg -y -loglevel error -i out/oracao_$V.mp4 -c:v libx264 -preset veryfast -crf 22 -maxrate 4000k -bufsize 8000k -c:a copy -movflags +faststart out/$V/oracao_${V}_envio.mp4 &&
nice -n 15 ffmpeg -y -loglevel error -i out/oracao_$V.mp4 -vf scale=1280:720 -c:v libx264 -preset veryfast -crf 24 -maxrate 1400k -bufsize 2800k -c:a aac -b:a 128k -movflags +faststart out/$V/oracao_${V}_720p.mp4 &&
echo "copias_ok $V"
