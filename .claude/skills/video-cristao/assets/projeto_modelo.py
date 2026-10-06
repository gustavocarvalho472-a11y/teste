"""__TITULO__ — projeto gerado pela skill /video-cristao (ilustração chapada estilo BibleProject).

    VIDEO_LANG=pt python3 narracao.py __NOME__
    export VIDEO_LANG=pt VIDEO_NARRATION=__NOME__
    TRILHA_OUT=trilha___NOME__.wav python3 __NOME___audio.py
    python3 narracao.py __NOME__ --mix trilha___NOME__.wav trilha___NOME___narrada.wav
    python3 engine.py wide __NOME__ __NOME___hq.mp4 trilha___NOME___narrada.wav

Cada cena é uma função (c, t, d): c = contexto cairo 1920x1080, t = segundos desde o início da cena,
d = duração da cena. Desenhe TUDO a cada quadro em função de t (sem estado entre quadros).
"""
import math
import os

from jesus_flat import geo_rays, halo
from prodigo import CREAM, INK, TEAL, bands, blob, cloud, fill, paint, person, sitting, sun
from render import (EN, GOLD, LANG, SANS, TITLE, H, W, eio, eout, glow, lerp, overlay, seg, subscribe,
                    text_center, title_text, tr)
from tela import kinetic

TEXTURE = True        # textura de papel (assinatura do estilo)
VIGNETTE = 0.4
CAPTION_SCALE = 0.78  # legendas discretas (preferência do canal)
NARR_GAP = 0.12       # respiro mínimo entre falas da narração


# ───────────────────────── cenas ─────────────────────────
def s_gancho(c, t, d):
    """Gancho: imagem forte + palavra-chave em 'soco'. Troque pelo seu conceito visual."""
    bands(c, ["#0b0e28", "#141a44", "#23306a"], 0, H * 0.72)
    c.rectangle(0, H * 0.72, W, H * 0.28)
    fill(c, "#0a0c22")
    glow(c, W * 0.5, H * 0.62, 380, "#6f9cff", 0.3 + 0.05 * math.sin(t * 6))
    sitting(c, W * 0.5, H * 0.74, 300, 1, INK, ragged=False, sash="#3a4a8a")
    kinetic(c, "PALAVRA", t - 3.0)
    overlay(c, "#000000", 1 - eout(t / 0.6))


def s_virada(c, t, d):
    """A virada: a luz entra (Jesus/a Palavra como resposta)."""
    e = eio(seg(t, 0.5, 4.0))
    bands(c, ["#2a1a3a", "#4a2f5c", "#f28c1e"], 0, H * 0.75)
    geo_rays(c, W / 2, H * 0.75, 16, t * 0.03, "#ffd25a", 0.12 * e)
    sun(c, W / 2, H * 0.75, lerp(120, 300, e))
    c.rectangle(0, H * 0.75, W, H * 0.25)
    fill(c, "#1a1024")
    person(c, W / 2, H * 0.8, 320, "open" if e > 0.6 else "stand", sash=GOLD)
    halo(c, W / 2, H * 0.8, 320, a=e)


def s_final(c, t, d):
    """Apelo + inscreva-se."""
    paint(c, "#2a1a3a")
    geo_rays(c, W / 2, H * 0.86, 24, t * 0.04, "#ffd25a", 0.1)
    sun(c, W / 2, H * 0.86, 260)
    a = eout(seg(t, 0.3, 1.2)) * (1 - seg(t, 7.6, 8.0))
    title_text(c, tr("ELE TE AMA"), W / 2, H * 0.42, 170, a=a, shine=seg(t, 1.0, 2.4), face=SANS)
    if t > 8.0:
        subscribe(c, t - 8.0, d - 8.0)
    overlay(c, "#000000", seg(t, d - 0.8, d))


# ───────────────────────── roteiro ─────────────────────────
# (rótulo do capítulo, duração, função, [(início, fim, "legenda com *destaque*"), ...])
# Rótulos "II · TÍTULO" puxam o versículo de VERSES["II"]. Rótulo vazio = sem título.
SCENES = [
    ("", 10.0, s_gancho, [
        (0.6, 5.0, "Frase de gancho que *provoca* em até 5 segundos."),
        (5.4, 9.6, "Segunda frase que abre uma *pergunta*.")]),
    ("I · A VIRADA", 12.0, s_virada, [
        (0.4, 6.0, "Aqui entra a *resposta* de Deus."),
        (6.4, 11.6, "“Versículo central do vídeo.”")]),
    ("", 14.0, s_final, []),
]
VERSES = {"I": ("Texto do versículo (ARC).", "Livro 0:0")}
VERSES_EN = {"I": ("Verse text (KJV).", "Book 0:0")}
FADES = {0: ("#000000", None)}

STARTS = []
_acc = 0.0
for _s in SCENES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc
SCALE = [1.0] * len(SCENES)
SCENES0, STARTS0 = SCENES, STARTS
# falas narradas sem legenda: {índice_da_cena: [(início, "texto"), ...]}
NARRATION_EXTRA = {2: [(0.4, "Ele te ama."), (8.2, "Inscreva-se para mais histórias que transformam vidas.")]}

EN.update({
    "I · A VIRADA": "I · THE TURN", "PALAVRA": "WORD", "ELE TE AMA": "HE LOVES YOU",
    "Frase de gancho que *provoca* em até 5 segundos.": "A hook line that *provokes* within 5 seconds.",
    "Segunda frase que abre uma *pergunta*.": "A second line that opens a *question*.",
    "Aqui entra a *resposta* de Deus.": "Here comes God's *answer*.",
    "“Versículo central do vídeo.”": "“The video's key verse.”",
    "Ele te ama.": "He loves you.",
    "Inscreva-se para mais histórias que transformam vidas.": "Subscribe for more stories that change lives.",
})


def verses():
    return VERSES_EN if LANG == "en" else VERSES


if os.environ.get("VIDEO_NARRATION") == "__NOME__":
    import narracao
    narracao.apply(globals(), "__NOME__")
