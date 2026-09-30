import imageio_ffmpeg, subprocess, sys

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit(f"ffmpeg falhou: {' '.join(cmd[:6])}...")
    return r

def duration(path):
    """Duração em segundos via ffmpeg -i (o binário estático não traz ffprobe)."""
    import re
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)
