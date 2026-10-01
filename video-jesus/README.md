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
| `jesus_history_en_narrated.mp4` | The Story of Jesus, inglês **narrado** (voz Michael, 1min59s) | emocional + narração |
| `historia_de_jesus_narrado.mp4` | A História de Jesus no **novo design**, português narrado (voz Alex, 1min59s) | emocional + narração |
| `short_historia_de_jesus_narrado.mp4` | Short 9:16 do novo design, narrado (54s) | idem |
| `filho_prodigo_narrado.mp4` | O Filho Pródigo, português **narrado** (voz Alex, 1min31s) | `prodigo_audio.py` + narração |
| `short_filho_prodigo_narrado.mp4` | Short 9:16 em português narrado (52s) | idem |
| `prodigal_son_en_narrated.mp4` | The Prodigal Son, inglês **narrado** (voz Michael, 1min34s) | `prodigo_audio.py` + narração |
| `short_prodigal_son_en_narrated.mp4` | Short 9:16 em inglês narrado (52s) | idem |
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

### Narração em inglês (local, sem integrações)

Voz gerada com o [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) (open source, licença Apache 2.0), voz `am_michael`.
Modelos em `~/tts`: `kokoro-v1.0.onnx` e `voices-v1.0.bin`. `pip install kokoro-onnx soundfile`.

```bash
export VIDEO_LANG=en
python3 narracao.py prodigo                         # gera falas + timing.json (cenas desaceleram se a fala não couber)
export VIDEO_NARRATION=prodigo
TRILHA_OUT=trilha_prodigo_en.wav python3 prodigo_audio.py
python3 narracao.py prodigo --mix trilha_prodigo_en.wav trilha_prodigo_en_narrada.wav   # música abaixa ≥8 dB sob a voz
python3 engine.py wide  prodigo prodigal_son_en_narrated.mp4 trilha_prodigo_en_narrada.wav
python3 engine.py short prodigo 41.52 short_prodigal_son_en_narrated.mp4 trilha_prodigo_en_narrada.wav
```

Vídeo principal narrado (voz na velocidade 1.0 para caber em 2 minutos):

```bash
export VIDEO_LANG=en VIDEO_VOICE_SPEED=1.0
python3 narracao.py render
export VIDEO_NARRATION=render
TRILHA_OUT=trilha_emocional_en.wav python3 audio_emocional.py      # partitura original, reposicionada no tempo narrado
python3 narracao.py render --mix trilha_emocional_en.wav trilha_jesus_en_narrada.wav
python3 engine.py wide render jesus_history_en_narrated.mp4 trilha_jesus_en_narrada.wav
```

Português narrado (voz `pm_alex`) e thumbnails:

```bash
export VIDEO_LANG=pt VIDEO_VOICE_SPEED=1.0
python3 narracao.py prodigo
export VIDEO_NARRATION=prodigo
TRILHA_OUT=trilha_prodigo_pt.wav python3 prodigo_audio.py
python3 narracao.py prodigo --mix trilha_prodigo_pt.wav trilha_prodigo_pt_narrada.wav
python3 engine.py wide  prodigo filho_prodigo_narrado.mp4 trilha_prodigo_pt_narrada.wav
python3 engine.py short prodigo 39.14 short_filho_prodigo_narrado.mp4 trilha_prodigo_pt_narrada.wav
python3 thumb.py      # thumb_filho_prodigo_pt.png, thumb_prodigal_son_en.png (1280x720)
```

História de Jesus no novo design (`jesus_flat.py`, mesmo roteiro/tempos de `render.py`):

```bash
export VIDEO_LANG=pt VIDEO_VOICE_SPEED=1.0
python3 narracao.py jesus_flat
export VIDEO_NARRATION=jesus_flat
TRILHA_PROJ=jesus_flat TRILHA_OUT=trilha_jesus_flat_pt.wav python3 audio_emocional.py
python3 narracao.py jesus_flat --mix trilha_jesus_flat_pt.wav trilha_jesus_flat_pt_narrada.wav
python3 engine.py wide  jesus_flat historia_de_jesus_narrado.mp4 trilha_jesus_flat_pt_narrada.wav
python3 engine.py short jesus_flat 65.03 short_historia_de_jesus_narrado.mp4 trilha_jesus_flat_pt_narrada.wav
```

## Tempo de Tela (vídeo de ~4 min)

`tempo_de_tela.mp4` — 3min53s, narrado (Alex), passagem central João 4:13-14. Ato I em câmera contínua (quarto → mergulho na tela → caça-níquel → estrada do feed → montagem → multidão → silêncio → notificação), legendas reduzidas (`CAPTION_SCALE`), fios de marionete cortados no Ato IV.
Atos: gancho (o aplicativo que te prende) → por que não conseguimos parar (caça-níquel, feed infinito,
comparação, ansiedade, solidão, insônia) → a sede (mulher no poço) → o preço (a cruz) → o que muda
(paz, descanso, identidade, presença) → desafio dos 7 dias ("ACEITO").

```bash
export VIDEO_LANG=pt VIDEO_VOICE_SPEED=1.0
python3 narracao.py tela
export VIDEO_NARRATION=tela
TRILHA_OUT=trilha_tela.wav python3 tela_audio.py        # sound design + trilha
python3 narracao.py tela --mix trilha_tela.wav trilha_tela_narrada.wav
python3 engine.py wide tela tempo_de_tela_hq.mp4 trilha_tela_narrada.wav
# < 30 MB: ffmpeg -i tempo_de_tela_hq.mp4 -crf 27 -preset slow -c:a aac -b:a 128k tempo_de_tela.mp4
```

### Tempo de Tela — versão em inglês (Michael)
`screen_time_en_narrated.mp4` — legendas, palavras na tela e versículos (KJV) em inglês.
```
export VIDEO_LANG=en VIDEO_VOICE_SPEED=1.0
python3 narracao.py tela
export VIDEO_NARRATION=tela
python3 narracao.py tela --mix trilha_tela.wav trilha_tela_en_narrada.wav   # mesma trilha do PT
python3 engine.py wide tela screen_time_hq.mp4 trilha_tela_en_narrada.wav
```

### Shorts do Tempo de Tela (Ato I inteiro, 68,6s)
`short_tempo_de_tela_narrado.mp4` (PT) e `short_screen_time_en_narrated.mp4` (EN). Selo no topo e CTA
"o desafio de 7 dias está no vídeo completo ↓" no fim (`tela.SHORT_OVERLAY`); `engine.py short` aceita `<t0>:<t1>`.
```
VIDEO_LANG=pt VIDEO_NARRATION=tela python3 engine.py short tela 0:68.6 short_tempo_de_tela_narrado.mp4 trilha_tela_narrada.wav
VIDEO_LANG=en VIDEO_NARRATION=tela python3 engine.py short tela 0:68.6 short_screen_time_en_narrated.mp4 trilha_tela_en_narrada.wav
```

### Kit de postagem
`postar/`: vídeos finais, thumbs, legendas `.srt` (`srt.py`) e `LEIA_E_POSTE.md` (títulos, descrições, tags, comentário fixado e prompt de thumb). Thumbs: `python3 thumb.py tela`.
