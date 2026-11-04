#!/bin/bash
cd "$(dirname "$0")"
echo "Juntando as partes do video..."
cat video_*.part > The_Night_a_King_Talked_to_the_Dead_1080p.mp4
echo "Pronto! O arquivo The_Night_a_King_Talked_to_the_Dead_1080p.mp4 esta nesta pasta."
