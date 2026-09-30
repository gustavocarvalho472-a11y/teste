#!/usr/bin/env bash
# Instala tudo que o estúdio precisa (sem sudo). Uso: bash setup.sh
set -e
pip install -q imageio-ffmpeg edge-tts faster-whisper pillow matplotlib requests
python3 - <<'PY'
import imageio_ffmpeg, os
exe = imageio_ffmpeg.get_ffmpeg_exe()
print("ffmpeg:", exe)
os.makedirs(os.path.expanduser("~/.local/bin"), exist_ok=True)
link = os.path.expanduser("~/.local/bin/ffmpeg")
if not os.path.exists(link):
    os.symlink(exe, link)
print("Adicione ~/.local/bin ao PATH se necessário.")
PY
