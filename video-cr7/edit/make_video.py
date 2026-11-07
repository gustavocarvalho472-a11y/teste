"""Gera video.py = timeline da amostra v2 (com os ajustes da abertura e da data) + video_rest.py + trilha completa."""
src = open("amostra2.py").read()
old_cam = """    k1 = eio(seg(t, T_BELOW - 0.25, T_BELOW + 0.75))       # topo → base
    k2 = eio(seg(t, T_OF - 0.35, T_OF + 0.9))               # base → inteiro
    z = lerp(lerp(1.62, 1.62, k1), 0.93, k2) * (1 + 0.025 * seg(t, T_OF, H02a))
    fy = lerp(lerp(0.265, 0.735, k1), 0.5, k2)"""
new_cam = """    k0 = eio(seg(t, 2.05, 2.8))                              # meme inteiro → topo ("next to Jorge Jesus")
    k1 = eio(seg(t, T_BELOW - 0.25, T_BELOW + 0.75))       # topo → base
    k2 = eio(seg(t, T_OF - 0.35, T_OF + 0.9))               # base → inteiro
    z0 = 0.93 + 0.03 * seg(t, 0, 2.05)
    z = lerp(lerp(z0, 1.62, k0), 0.93, k2) * (1 + 0.025 * seg(t, T_OF, H02a))
    fy = lerp(lerp(lerp(0.5, 0.265, k0), 0.735, k1), 0.5, k2)"""
imp = "from fx import FPS, H, W, clamp, eio, eout, ein, font, lerp, pulse, rgb, seg, surf, text, text_width\n"
rep = [(old_cam, new_cam),
       ('    text(c, "TODAY", W / 2, H / 2 - 110, 40, DISPLAY, LIME, a, "center", 16)\n', ''),
       ('TOTAL = round(T_SKY + 3.55 + 1.0, 2)\nSILENCE.append((T_GOT - 0.1, TOTAL + 1))\ncue(TOTAL - 1.0, "hit_low", 0.8)',
        'SILENCE.append((T_GOT - 0.1, S("A104") - 0.3))'),
       ('@shot(T_GOT - 0.15, TOTAL)', '@shot(T_GOT - 0.15, T_SKY + 3.55)'),
       ("""    score_bug(c, t, T_GOT + 0.3, TOTAL - 0.4, "MUN", 2, "TOT", 0, "89'")\n    fx["fade"] = seg(t, TOTAL - 0.7, TOTAL)""",
        """    score_bug(c, t, T_GOT + 0.3, T_SKY + 3.4, "MUN", 2, "TOT", 0, "89'")"""),
       (imp, imp + "from fx import SERIF\nfrom doc import DARK\n")]
for a, b in rep:
    assert a in src, "NAO ACHEI: " + a[:80]
    src = src.replace(a, b, 1)
head, tail = src.split('SPEECH_CLIPS = {"v02_captain_a", "v04_tunnel_a"}')
music_block = tail.split("SHOTS.sort(key=lambda s: s[0])")[0]
rest = open("video_rest.py").read()
extra = '''
SPEECH_CLIPS = {"v02_captain_a", "v04_tunnel_a", "v05_q_a", "v06_q_a", "v09_q_a", "v12_q1_a", "v12_q2_a", "v20_q_a",
                "v22_q_a"}
''' + music_block + '''
MUSIC += [
    (S("A104") - 0.3, ACT2 + 0.05, "tensao", 24.0, 0.9, 0.8, 0.3),
    (ACT2, ACT3 + 0.05, "doc_tensao", 0.0, 0.95, 0.05, 0.3),
    (ACT3, ACT3 + 76.0, "vilao", 0.0, 1.0, 0.05, 0.5),
    (ACT3 + 75.5, S("A308") - 0.1, "doc_tensao", 23.0, 0.9, 0.5, 0.3),
    (S("A308") - 0.1, ACT4 + 0.05, "doc_emocao", 28.0, 0.8, 0.5, 0.4),
    (ACT4, T_DALLAS_END + 3.4, "doc_emocao", 0.0, 1.0, 0.05, 0.6),
    (ACT5, ACT5 + 80.0, "tensao", 2.5, 0.9, 0.05, 0.5),
    (ACT5 + 79.5, S("A509") - 0.3, "doc_tensao", 46.0, 0.9, 0.5, 0.3),
    (T_JQ + 5.3, FALL + 0.05, "vilao", 38.0, 1.0, 0.3, 0.3),
    (FALL, ENDA + 0.05, "doc_tensao", 60.0, 0.9, 0.05, 0.4),
    (ENDA, S("F06") - 0.1, "piano", 3.5, 1.0, 0.3, 0.6),
    (S("F06") - 0.3, TOTAL, "doc_emocao", 62.0, 1.0, 0.8, 2.5),
]

SHOTS.sort(key=lambda s: s[0])


def frame(i):
    t = i / FPS
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    fx = {"grain": 0.8}
    fn, logo = SHOTS[-1][2], True
    for a, b, f, lg in SHOTS:
        if a <= t < b:
            fn, logo = f, lg
            break
    fn(c, t, fx)
    for a, b, f in OVER:
        if a <= t <= b:
            f(c, t)
    if logo:
        logo_bug(c, 0.8)
    return doc.post(s, i, fx)
'''
open("video.py", "w").write('"""Vídeo completo: Cristiano Ronaldo Became Homelander (Beyond Success)."""\n' + head + rest + extra)
print("video.py gerado")
