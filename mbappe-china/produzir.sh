#!/usr/bin/env bash
# Produção completa. O vídeo publicado é em INGLÊS (narração + legendas + textos na tela).
# O português sai só como ÁUDIO, para validar o conteúdo antes de renderizar.
#
#   bash produzir.sh pt     → saida/validacao_pt.mp3              (rápido: só voz + trilha)
#   bash produzir.sh en     → saida/mbappe_china_en.mp4 + legendas_en.srt + capitulos_en.txt
#   bash produzir.sh        → os dois
set -e
cd "$(dirname "$0")"
alvo="${1:-todos}"
if [ "$alvo" = pt ] || [ "$alvo" = todos ]; then
  VIDEO_LANG=pt python3 narrar.py
  VIDEO_LANG=pt python3 trilha.py
  mkdir -p saida
  ffmpeg -v error -y -i build/pt/mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -b:a 160k saida/validacao_pt.mp3
  echo "OK saida/validacao_pt.mp3"
fi
if [ "$alvo" = en ] || [ "$alvo" = todos ]; then
  VIDEO_LANG=en python3 narrar.py
  VIDEO_LANG=en python3 trilha.py
  VIDEO_LANG=en python3 montar.py
fi
echo FIM
