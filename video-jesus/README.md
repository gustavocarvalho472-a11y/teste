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

Para ajustar textos e tempos, edite a lista `SCENES` em `render.py`.
