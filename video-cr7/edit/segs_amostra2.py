"""Trechos de clipe usados na amostra v2 (extração única para cache/seg)."""
import sys
from concurrent.futures import ThreadPoolExecutor
import doc

SEGS = [
    # nome, clipe, t0, t1, opções
    ("v10_eyes", "v10_tb_stormfront", 0.0, 2.9, dict(fit="letterbox")),
    ("v10_eyes_c", "v10_tb_stormfront", 0.0, 2.9, dict()),
    ("v10_room", "v10_tb_stormfront", 7.0, 10.9, dict(fit="letterbox")),
    ("v02_sad", "v02_despedida", 0.0, 1.95, dict(crop=(160, 0, 1760, 900), slow=1.6)),
    ("v02_letter", "v02_despedida", 17.6, 19.45, dict(crop=(160, 0, 1760, 900))),
    ("v02_captain", "v02_despedida", 1.9, 6.9, dict()),
    ("v02_euro16", "v02_despedida", 8.6, 11.9, dict(crop=(160, 0, 1760, 900))),
    ("v04_tunnel", "v04_tunel", 0.0, 11.9, dict()),
    ("v04_tunnel_slow", "v04_tunel", 3.0, 8.0, dict(slow=2.0)),
    ("v09_strike", "v09_greve", 4.0, 9.0, dict()),
    ("v19_bench", "v19_noruega", 135.0, 147.0, dict(crop=(0, 0, 1790, 1080), anchor="top")),
    ("v16_roar", "v16_croacia", 63.8, 66.0, dict(slow=1.65)),
    ("v21_car", "v21_copenhague", 1.6, 5.6, dict(crop=(250, 200, 1920, 1080))),
    ("v20_jesus", "v20_jesus_pele_maradona", 8.0, 11.5, dict()),
    ("v16_pen", "v16_croacia", 54.5, 61.0, dict()),
    ("v03_costume", "v03_meme_homelander", 36.0, 41.5, dict(crop=(0, 0, 1280, 600), slow=1.5)),
    ("v13_walk", "v13_tb_multidao", 0.0, 3.5, dict(crop=(0, 92, 1280, 628), fit="letterbox")),
    ("v13_crowd_c", "v13_tb_multidao", 6.6, 9.9, dict(crop=(0, 92, 1280, 628))),
    ("v06_stage_c", "v06_tb_starlight", 0.0, 6.6, dict(crop=(310, 138, 1671, 942))),
    ("v07_unveil", "v07_alnassr", 2.0, 6.5, dict()),
    ("v11_cry", "v11_dublin", 46.0, 52.0, dict(crop=(0, 70, 1200, 720))),
    ("v22_speech", "v22_tb_fora_do_roteiro", 4.5, 9.5, dict(crop=(0, 140, 1920, 940), fit="letterbox")),
]
AUDIO = [("v02_captain_a", "v02_despedida", 1.9, 6.9), ("v04_tunnel_a", "v04_tunel", 0.0, 11.9),
         ("v11_cry_a", "v11_dublin", 46.0, 52.0), ("v19_bench_a", "v19_noruega", 135.0, 147.0),
         ("v13_crowd_a", "v13_tb_multidao", 6.6, 9.9), ("v16_pen_a", "v16_croacia", 54.5, 61.0),
         ("v07_unveil_a", "v07_alnassr", 2.0, 6.5)]

if __name__ == "__main__":
    def run(s):
        nm, clip, a, b, kw = s
        doc.extract(nm, clip, a, b, **kw)
        return nm
    with ThreadPoolExecutor(3) as ex:
        for nm in ex.map(run, SEGS):
            print("ok", nm, flush=True)
    for nm, clip, a, b in AUDIO:
        doc.extract_audio(nm, clip, a, b)
    print("FIM")
