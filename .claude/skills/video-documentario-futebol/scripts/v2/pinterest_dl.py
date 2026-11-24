import re, sys, os, subprocess, json
from concurrent.futures import ThreadPoolExecutor
src, key, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
OUT = "/home/user/teste/video-production/vinicius/assets/pin"
h = open(src, encoding="utf-8", errors="ignore").read()
seen = []
for m in re.finditer(r'https://i\.pinimg\.com/(?:\d+x|originals)/([0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32})\.jpg', h):
    if m.group(1) not in seen: seen.append(m.group(1))
def dl(i_p):
    i, p = i_p; f = f"{OUT}/{key}_{i:02d}.jpg"
    if os.path.exists(f) and os.path.getsize(f) > 5000: return f
    for size in ("originals", "736x"):
        r = subprocess.run(["curl", "-s", "-f", "-o", f, f"https://i.pinimg.com/{size}/{p}.jpg"])
        if r.returncode == 0 and os.path.getsize(f) > 5000: return f
    if os.path.exists(f): os.remove(f)
with ThreadPoolExecutor(6) as ex: got = [x for x in ex.map(dl, enumerate(seen[:n])) if x]
print(key, len(seen), "found,", len(got), "downloaded")
