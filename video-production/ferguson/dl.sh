#!/bin/bash
# usage: dl.sh name url  (downloads into assets/real/name.mp4 in background-friendly way)
cd "$(dirname "$0")/assets/real" && curl -sS -L --retry 4 -o "$1.mp4" "$2" && echo "$1 $(ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 $1.mp4 | tr '\n' ' ')"
