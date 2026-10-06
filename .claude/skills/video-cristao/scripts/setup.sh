#!/usr/bin/env bash
# Prepara o ambiente da skill /video-cristao (idempotente). Imprime a pasta de trabalho (toolkit) no fim.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
TK="$(python3 "$HERE/_toolkit.py")"
if [ ! -f "$TK/engine.py" ]; then            # sem repositório: usa a cópia embutida na skill
  mkdir -p "$TK" && cp -r "$HERE/../toolkit/." "$TK/"
  echo "toolkit copiado para $TK"
fi

python3 -c "import cairo, numpy, scipy, imageio_ffmpeg, soundfile, kokoro_onnx, faster_whisper, PIL, requests" 2>/dev/null \
  || pip install -q pycairo numpy scipy imageio-ffmpeg soundfile kokoro-onnx faster-whisper pillow requests

mkdir -p ~/.fonts
if ! fc-list 2>/dev/null | grep -qi montserrat; then cp "$TK"/fonts/*.ttf ~/.fonts/ && (fc-cache -f >/dev/null 2>&1 || true); fi

M="${KOKORO_DIR:-$HOME/tts}"; mkdir -p "$M"
URL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$M/$f" ] || { echo "baixando $f (~350 MB no total)…"; curl -sSL -o "$M/$f" "$URL/$f"; }
done
echo "OK — TOOLKIT=$TK  (vozes em $M)"
