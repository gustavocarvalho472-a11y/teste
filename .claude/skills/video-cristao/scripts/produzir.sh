#!/usr/bin/env bash
# Pipeline completo de UM idioma: narração → trilha → mix → vídeo 16:9 → compressão (<30 MB) → Short → .srt
#   bash produzir.sh <nome> <pt|en> <saida_base> [short_t0:short_t1]
# ex.: bash produzir.sh ansiedade pt ansiedade "0:58"
# Rode em segundo plano (nohup … &): um vídeo de 4 min leva ~10–15 min.
set -e
NOME=$1; LANG_=$2; OUT=$3; SHORT=${4:-}
TK="${TOOLKIT:-$(cd "$(dirname "$0")/../../../.." && pwd)/video-jesus}"
cd "$TK"
export VIDEO_LANG=$LANG_ VIDEO_VOICE_SPEED=${VIDEO_VOICE_SPEED:-1.0}
FF=$(python3 -c "import imageio_ffmpeg as i;print(i.get_ffmpeg_exe())")
mkdir -p postar

unset VIDEO_NARRATION
python3 narracao.py "$NOME"                                   # falas + timing.json
export VIDEO_NARRATION=$NOME
# a trilha é refeita por idioma: a narração de cada língua estica as cenas de um jeito
TRILHA_OUT="trilha_${NOME}_${LANG_}.wav" python3 "${NOME}_audio.py"
python3 narracao.py "$NOME" --mix "trilha_${NOME}_${LANG_}.wav" "trilha_${NOME}_${LANG_}_narrada.wav"
python3 engine.py wide "$NOME" "${OUT}_hq.mp4" "trilha_${NOME}_${LANG_}_narrada.wav"
"$FF" -y -loglevel error -i "${OUT}_hq.mp4" -c:v libx264 -crf ${CRF:-27} -preset slow -pix_fmt yuv420p \
      -c:a aac -b:a 128k -movflags +faststart "postar/${OUT}.mp4" && rm "${OUT}_hq.mp4"
python3 srt.py "$NOME" "postar/legendas_${OUT}.srt"
if [ -n "$SHORT" ]; then
  python3 engine.py short "$NOME" "$SHORT" "postar/short_${OUT}.mp4" "trilha_${NOME}_${LANG_}_narrada.wav"
  python3 srt.py "$NOME" "postar/legendas_short_${OUT}.srt" "$SHORT"
fi
ls -la postar/ | grep "$OUT"
echo FIM
