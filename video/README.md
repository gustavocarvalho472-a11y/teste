# Vídeo simples de música clássica

Divide o tempo total entre as imagens. Cada imagem ganha zoom lento, tom quente,
vinheta e fade suave. Só precisa de `ffmpeg`.

```bash
python3 render.py --audio musica.mp3          # duração = duração do áudio
python3 render.py --duracao 7200              # 2h sem áudio
```

- Imagens: `assets/images/` (ordem alfabética) ou `--imagens pasta/`
- Ajustes: `--zoom 0.15` (15% por imagem), `--fade 2` (segundos)
- Saída: `output/video.mp4` (1080p, 24fps)
