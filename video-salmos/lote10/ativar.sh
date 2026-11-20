#!/bin/bash
# ativa um vídeo do lote na raiz (timeline.json, cenas.json, audio/narracao.wav)
set -e; cd "$(dirname "$0")/.."
cp lote10/timeline_$1.json timeline.json; cp lote10/cenas_$1.json cenas.json; cp work/$1/narracao.wav audio/narracao.wav
echo "ativo: $1"
