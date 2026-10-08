# Amplia imagens pequenas (512x286) para 2576x1438.
# Mistura EDSR x4 (contornos limpos) com Lanczos (mantém a textura da hachura) e soma grão fino.
import sys, os, cv2, numpy as np
M = os.path.expanduser("~/sr/EDSR_x4.pb"); W, H = 2576, 1438
def us(x, s, a): return cv2.addWeighted(x, 1 + a, cv2.GaussianBlur(x, (0, 0), s), -a, 0)
sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(M); sr.setModel("edsr", 4)
for p in sys.argv[1:]:
    lo = cv2.imread(p)
    ed = cv2.resize(sr.upsample(lo), (W, H), interpolation=cv2.INTER_LANCZOS4)
    lz = cv2.resize(lo, (W, H), interpolation=cv2.INTER_LANCZOS4)
    im = cv2.addWeighted(us(ed, 1.5, .6), .5, us(lz, 2.5, .9), .5, 0)
    im = np.clip(im + np.random.default_rng(0).normal(0, 7, (H, W, 1)), 0, 255).astype(np.uint8)
    out = os.path.join(os.path.dirname(os.path.dirname(p)), os.path.basename(p))
    cv2.imwrite(out, im, [cv2.IMWRITE_JPEG_QUALITY, 93]); print(out, flush=True)
