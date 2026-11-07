"""Trechos de clipe do vídeo completo (além dos da amostra)."""
from concurrent.futures import ThreadPoolExecutor
import doc

LB = dict(fit="letterbox")
TOP = dict(crop=(0, 0, 1790, 1080), anchor="top")
DUB = dict(crop=(0, 70, 1200, 720))
SEGS = [
    ("v05_talk", "v05_piers", 0.0, 12.0, {}),
    ("v06_full", "v06_tb_starlight", 0.0, 10.0, dict(crop=(310, 138, 1671, 942))),
    ("v07_arch", "v07_alnassr", 8.0, 13.5, {}),
    ("v08_benz", "v08_benzema", 2.6, 5.4, {}),
    ("v09_quote", "v09_greve", 6.9, 12.6, {}),
    ("v10_storm", "v10_tb_stormfront", 3.0, 6.9, LB),
    ("v12_talk", "v12_coletiva_irlanda", 11.0, 17.2, {}),
    ("v12_q1", "v12_coletiva_irlanda", 2.9, 5.8, {}),
    ("v12_q2", "v12_coletiva_irlanda", 8.35, 11.15, {}),
    ("v11_wide", "v11_dublin", 18.0, 30.0, DUB),
    ("v11_elbow", "v11_dublin", 34.0, 40.0, dict(DUB, slow=1.4)),
    ("v11_var", "v11_dublin", 54.0, 66.0, DUB),
    ("v11_off", "v11_dublin", 72.0, 100.0, DUB),
    ("v13_smile", "v13_tb_multidao", 10.0, 12.5, dict(crop=(0, 92, 1280, 628))),
    ("v03_grin", "v03_meme_homelander", 8.0, 11.5, dict(crop=(0, 0, 1280, 600))),
    ("v14_hair", "v14_tb_fio_branco", 2.8, 12.6, dict(crop=(0, 140, 1920, 940), fit="letterbox")),
    ("v14_jar", "v14_tb_fio_branco", 16.3, 21.8, dict(crop=(0, 140, 1920, 940), fit="letterbox")),
    ("v14_face", "v14_tb_fio_branco", 28.3, 30.8, dict(crop=(0, 140, 1920, 940), fit="letterbox")),
    ("v15_walk", "v15_congo", 0.0, 7.5, dict(crop=(280, 0, 1920, 1080))),
    ("v15_hug", "v15_congo", 7.5, 13.5, dict(crop=(280, 0, 1920, 1080))),
    ("v16uz_goal", "v16_uzbequistao", 14.0, 20.5, {}),
    ("v16uz_smile", "v16_uzbequistao", 53.0, 56.0, {}),
    ("v17_header", "v17_espanha", 3.6, 7.4, {}),
    ("v17_merino", "v17_espanha", 14.2, 17.8, {}),
    ("v18_off", "v18_gales", 0.0, 13.5, TOP),
    ("v19_goal", "v19_noruega", 104.0, 118.0, TOP),
    ("v19_end", "v19_noruega", 168.0, 180.0, TOP),
    ("v19_alone", "v19_noruega", 148.8, 151.8, TOP),
    ("v20_quote", "v20_jesus_pele_maradona", 9.1, 14.5, {}),
    ("v20_talk", "v20_jesus_pele_maradona", 0.0, 8.0, {}),
    ("v22_prompt", "v22_tb_fora_do_roteiro", 1.2, 4.3, dict(crop=(0, 140, 1920, 940), fit="letterbox")),
    ("v22_quote", "v22_tb_fora_do_roteiro", 3.7, 8.6, dict(crop=(0, 140, 1920, 940), fit="letterbox")),
    ("v22_off", "v22_tb_fora_do_roteiro", 13.3, 19.8, dict(crop=(0, 140, 1920, 940), fit="letterbox")),
    ("v24_fall", "v24_tb_perde_poderes", 18.0, 29.0, dict(crop=(0, 121, 1920, 959), fit="letterbox")),
    ("v24_alone", "v24_tb_perde_poderes", 49.0, 55.5, dict(crop=(0, 121, 1920, 959), fit="letterbox")),
    ("v02_staff", "v02_despedida", 11.8, 17.0, dict(crop=(160, 0, 1760, 900))),
    ("v02_bus", "v02_despedida", 4.6, 6.9, dict(crop=(160, 0, 1760, 900))),
]
AUDIO = [("v05_q_a", "v05_piers", 1.9, 3.5), ("v06_q_a", "v06_tb_starlight", 0.0, 4.1),
         ("v09_q_a", "v09_greve", 6.95, 12.45), ("v12_q1_a", "v12_coletiva_irlanda", 2.9, 5.8),
         ("v12_q2_a", "v12_coletiva_irlanda", 8.35, 11.15), ("v15_a", "v15_congo", 0.0, 13.5),
         ("v11_a", "v11_dublin", 30.0, 100.0), ("v19_amb_a", "v19_noruega", 100.0, 180.0),
         ("v20_q_a", "v20_jesus_pele_maradona", 9.2, 14.45), ("v22_q_a", "v22_tb_fora_do_roteiro", 3.8, 8.5),
         ("v24_a", "v24_tb_perde_poderes", 18.0, 29.0)]

if __name__ == "__main__":
    def run(s):
        nm, clip, a, b, kw = s
        doc.extract(nm, clip, a, b, **kw)
        return nm
    for nm, clip, a, b in AUDIO:
        doc.extract_audio(nm, clip, a, b)
    print("audio ok", flush=True)
    with ThreadPoolExecutor(3) as ex:
        for nm in ex.map(run, SEGS):
            print("ok", nm, flush=True)
    print("FIM")
