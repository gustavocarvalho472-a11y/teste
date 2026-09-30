# A História de Jesus — vídeo em motion graphics

`jesus_historia.mp4` — 1920x1080 (16:9, YouTube), 30 fps, 1min59s, legendas narradas em PT-BR, trilha sonora original sintetizada e mensagem final de apelo com chamada para se inscrever no canal.

Do nascimento à ressurreição, em 12 capítulos: a promessa, o nascimento, a estrela, o batismo, os milagres, a mensagem, a última ceia, Getsêmani, a paixão, a cruz, o silêncio e a ressurreição.

## Como regenerar

```bash
pip install pycairo numpy scipy imageio-ffmpeg
# fontes (Italiana, Cinzel e Montserrat, licença OFL) estão em fonts/ — instale-as no sistema:
mkdir -p ~/.fonts && cp fonts/*.ttf ~/.fonts && fc-cache -f
python3 audio.py    # gera trilha.wav
python3 render.py   # gera jesus_historia.mp4
```

## Versões

| Arquivo | Idioma | Trilha |
|---|---|---|
| `jesus_historia.mp4` | Português | original (`audio.py`) |
| `jesus_historia_musica_nova.mp4` | Português | emocional (`audio_emocional.py`) |
| `jesus_history_en.mp4` | Inglês (versículos KJV) | emocional (`audio_emocional.py`) |
| `short_jesus.mp4` | Short 9:16 (paixão → ressurreição → apelo, 54s) | emocional |
| `filho_prodigo.mp4` | O Filho Pródigo, estilo ilustração chapada (1min31s) | `prodigo_audio.py` |
| `short_filho_prodigo.mp4` | Short 9:16 do Filho Pródigo (despertar → abraço → apelo, 52s) | `prodigo_audio.py` |

### Filho Pródigo e Shorts (`engine.py`)

```bash
python3 prodigo_audio.py                                              # trilha_prodigo.wav
python3 engine.py wide  prodigo filho_prodigo.mp4 trilha_prodigo.wav
python3 engine.py short prodigo 39 short_filho_prodigo.mp4 trilha_prodigo.wav
python3 engine.py short render  65 short_jesus.mp4 trilha_emocional.wav
# versão em inglês: prefixe com VIDEO_LANG=en
```

- `synth.py`: instrumentos e master das trilhas; `prodigo.py`: cenas do Filho Pródigo.
- `amostra_voz_*.mp3`: testes de narração em inglês com o modelo Kokoro (open source, roda local).

```bash
python3 audio_emocional.py    # gera trilha_emocional.wav
VIDEO_LANG=en VIDEO_AUDIO=trilha_emocional.wav VIDEO_OUT=jesus_history_en.mp4 python3 render.py
```

Para ajustar textos e tempos, edite a lista `SCENES` em `render.py`.
