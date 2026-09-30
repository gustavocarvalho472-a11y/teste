#!/usr/bin/env python3
"""Monta o vídeo final: cenas (imagem/vídeo) + narração + legendas + música. Só ffmpeg.
Uso: build_video.py project.json out.mp4 [--preview]
project.json:
 {"narration":"audio/narration.mp3","captions":"audio/captions.srt","music":"audio/music.mp3",
  "scenes":[{"file":"assets/s01.mp4","duration":6.5,"motion":"zoom_in|zoom_out|pan_left|pan_right|none"}, ...]}
As durações são reescaladas para somar exatamente a duração da narração."""
import json, os, subprocess, sys, tempfile
from _common import FFMPEG, run, duration

W, H, FPS = (1280, 720, 24) if "--preview" in sys.argv else (1920, 1080, 30)
args = [a for a in sys.argv[1:] if not a.startswith("--")]
proj = json.load(open(args[0])); out = args[1]
base = os.path.dirname(os.path.abspath(args[0]))
P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)

scenes = proj["scenes"]
narr = P(proj["narration"]); total = duration(narr)
k = total / sum(s["duration"] for s in scenes)
tmp = tempfile.mkdtemp(); segs = []
IMG = {".png", ".jpg", ".jpeg", ".webp"}

for i, s in enumerate(scenes):
    d = s["duration"] * k; f = P(s["file"]); seg = f"{tmp}/seg{i:03}.mp4"; n = max(1, round(d * FPS))
    fade = f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(d-0.25,0):.2f}:d=0.25"
    if os.path.splitext(f)[1].lower() in IMG:
        m = s.get("motion", "zoom_in")
        z = {"zoom_in": f"z='min(zoom+0.0006,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
             "zoom_out": f"z='max(1.15-0.0006*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
             "pan_left": f"z=1.12:x='(iw-iw/zoom)*(1-on/{n})':y='ih/2-(ih/zoom/2)'",
             "pan_right": f"z=1.12:x='(iw-iw/zoom)*on/{n}':y='ih/2-(ih/zoom/2)'",
             "none": "z=1:x=0:y=0"}[m]
        vf = f"scale=3840:-2,zoompan={z}:d={n}:s={W}x{H}:fps={FPS},{fade},format=yuv420p"
        cmd = [FFMPEG, "-y", "-loop", "1", "-i", f, "-vf", vf, "-t", f"{d:.3f}"]
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{fade},format=yuv420p"
        cmd = [FFMPEG, "-y", "-stream_loop", "-1", "-i", f, "-vf", vf, "-t", f"{d:.3f}", "-an"]
    run(cmd + ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", seg]); segs.append(seg)
    print(f"cena {i+1}/{len(scenes)} ok")

lst = f"{tmp}/list.txt"; open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
silent = f"{tmp}/silent.mp4"
run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])

# vídeo + legendas queimadas (se libass disponível)
vin, vf = ["-i", silent], []
srt = proj.get("captions") and P(proj["captions"])
style = "FontName=DejaVu Sans,FontSize=22,Bold=1,Outline=2,Shadow=0,MarginV=60,PrimaryColour=&H00FFFFFF"
if srt and os.path.exists(srt):
    esc = srt.replace("\\", "/").replace(":", "\\:")
    vf = ["-vf", f"subtitles='{esc}':force_style='{style}'"]

# áudio: narração + música a ~20% com ducking
ain = ["-i", narr]
if proj.get("music"):
    ain += ["-stream_loop", "-1", "-i", P(proj["music"])]
    af = ("[2:a]volume=0.20[m];[1:a]asplit[n1][n2];[m][n1]sidechaincompress=threshold=0.05:ratio=8[md];"
          "[md][n2]amix=inputs=2:duration=first:normalize=0[a]")
    amap = ["-filter_complex", af, "-map", "0:v", "-map", "[a]"]
else:
    amap = ["-map", "0:v", "-map", "1:a"]
try:
    run([FFMPEG, "-y", *vin, *ain, *vf, *amap, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", out])
except SystemExit:
    print("Legendas falharam (libass?); exportando sem legendas.")
    run([FFMPEG, "-y", *vin, *ain, *amap, "-c:v", "copy", "-c:a", "aac", "-t", f"{total:.3f}", out])
print("ok:", out, f"{total:.1f}s")
