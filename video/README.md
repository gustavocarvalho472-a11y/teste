# Vídeo de música clássica no estilo "Classical Mind"

Gera vídeos longos (1 a 3h) de piano clássico para estudo/foco, a partir de imagens
estáticas + música, no estilo do canal [@The-Classical-Mind](https://www.youtube.com/@The-Classical-Mind).

## O que o script faz (estilo da referência)

| Elemento | Referência | Aqui |
|---|---|---|
| Tempo por imagem | ~8–10s | `--slot 10` |
| Movimento | zoom-in lento e contínuo | `--zoom 0.10` (10% por imagem) |
| Transição | crossfade de ~1,5–2s | `--fade 2` |
| Atmosfera | poeira/partículas, flicker de vela | partículas douradas + oscilação sutil de brilho |
| Acabamento | vinheta forte, grão de filme, tons quentes | vinheta, grão, âmbar nas luzes |
| Título | serifa clássica centralizada | fonte Cinzel, fade in/out nos primeiros 12s |
| Áudio | piano solo, sem ambiente, às vezes 432 Hz | normalização de volume + `--hz432` opcional |

Para vídeos longos ele renderiza **um único loop perfeito** (imagens 1→5→1) e repete com
cópia de stream, sem re-encodar. Só intro (título) e outro (fade para preto) são re-encodadas.

## Uso

Requer `ffmpeg` e `pip install numpy pillow`.

```bash
# prévia (~1min40, sem áudio)
python3 render.py --preview

# vídeo completo: a duração acompanha o áudio; faixas tocam na ordem dada
python3 render.py --audio musicas/01_Sonata_K545.mp3 musicas/02_Sonata_K331.mp3 \
  --title "Mozart for Deep Focus" --subtitle "Classical Music for Study & Concentration"

# trocar só a música/título reaproveitando o loop já renderizado
python3 render.py --reuse --audio outras/*.mp3 --title "Mozart Effect" --hz432
```

Saídas em `output/`:
- `video.mp4` — 1080p, H.264 ~12 Mbps, AAC 256k
- `video.tracklist.txt` — minutagem de cada faixa (cole na descrição → capítulos do YouTube).
  O nome da faixa vem do nome do arquivo (`_` vira espaço).

Imagens: coloque em `assets/images/` (ordem alfabética). Tarjas pretas são removidas e a
imagem é recortada para 16:9 automaticamente.

## Sobre a música

As composições de Mozart, Beethoven, Chopin etc. são domínio público, **mas as gravações
não**. Use gravações próprias, licenciadas ou de domínio público (ex.: Musopen) para não
levar Content ID / perder a monetização.
