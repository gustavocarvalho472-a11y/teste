#!/usr/bin/env bash
# Prepara o ambiente da skill /video-cristao (idempotente: pula o que já existe).
set -e
TK="${1:-$(cd "$(dirname "$0")/../../../.." && pwd)/video-jesus}"
[ -f "$TK/engine.py" ] || { echo "toolkit não encontrado em $TK"; exit 1; }

python3 -c "import cairo, numpy, scipy, imageio_ffmpeg, soundfile, kokoro_onnx, faster_whisper, PIL, requests" 2>/dev/null \
  || pip install -q pycairo numpy scipy imageio-ffmpeg soundfile kokoro-onnx faster-whisper pillow requests

mkdir -p ~/.fonts
if ! fc-list | grep -qi montserrat; then cp "$TK"/fonts/*.ttf ~/.fonts/ && fc-cache -f >/dev/null; fi

M="${KOKORO_DIR:-$HOME/tts}"; mkdir -p "$M"
URL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$M/$f" ] || { echo "baixando $f…"; curl -sSL -o "$M/$f" "$URL/$f"; }
done
echo "OK: toolkit=$TK  vozes=$M"
