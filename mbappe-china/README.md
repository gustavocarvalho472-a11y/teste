# Mbappé OFENDEU a China — montagem automática

Pipeline Python + FFmpeg que monta o vídeo do handoff (1920×1080, 30 fps, H.264 CRF 20 veryfast, AAC 192k).
Asset que ainda não existe vira **placeholder** com o id e a descrição. Basta salvar o arquivo real e rodar de novo.

## Rodar

```bash
cd mbappe-china
python3 narrar.py        # narração + alinhamento Whisper → build/timing.json
python3 trilha.py        # trilha + SFX + mixagem → build/mix.wav
python3 montar.py        # vídeo → saida/mbappe_china.mp4 + saida/capitulos.txt  (~10–15 min, rode com nohup)
```

Comandos de checagem:
- `python3 montar.py --assets`: mostra o que já tem e o que falta.
- `python3 montar.py --quadros 7 26.5 50`: gera uma grade de quadros soltos em `build/quadros.png`.

Dependências: as mesmas da skill `video-ilustracao`. Rode `bash <skill>/scripts/setup.sh` para instalar
kokoro-onnx, faster-whisper, scipy, soundfile e as vozes em `~/tts`.

## Onde colocar os arquivos

```
audio/narracao.mp3     # narração final. Se existir, substitui a voz provisória (Kokoro pm_alex)
audio/musica.mp3       # trilha. Se não existir, uma trilha tensa em Ré menor é sintetizada
audio/sfx/<nome>.wav   # whoosh, whoosh_low, impact, boom, scratch, tv_off, paper_rip, glitch,
                       # cash_drop, shutter, crack, notifs. Os que faltarem são sintetizados
assets/memes/MEME_01_qualquer_coisa.png
assets/prints/PRT_01_….png
assets/fotos/FOT_01_….jpg
assets/clips/CLP_01_….mp4   # vídeo toca de verdade; S03 usa um quadro congelado (opção frame)
assets/logos/LOG_01_….png   # PNG transparente fica melhor
assets/ia/IA_01_….png
```

O arquivo é encontrado pelo **id no começo do nome**. A tabela completa (o que é cada id e onde achar) está
na seção 3 do handoff, e os prompts das imagens IA na seção 4.

## Como funciona

| Arquivo | Papel |
|---|---|
| `roteiro.py` | Decupagem: blocos com fala, shots, texto na tela, SFX, contador e marcas de trilha. `PRON` corrige a pronúncia da voz provisória |
| `narrar.py` | Com `audio/narracao.mp3`, transcreve com Whisper e acha o início de cada bloco pelo texto. Sem ele, gera a voz com Kokoro. Nos dois casos sai o tempo de cada palavra para a legenda karaokê |
| `timeline.py` | Divide cada bloco em shots e corta qualquer shot com mais de 4 s em sub-cortes que alternam o enquadramento (zoom in / pan / zoom out). Também gera os eventos de SFX e os capítulos |
| `trilha.py` | Música −22 dB com ducking sob a voz, SFX −8 dB, narração em 0 dB |
| `montar.py` | Tratamentos do handoff: PRINT (fundo texturizado, ±1,5°, entrada 92→100 %, caixa amarela, "Fonte"), MEME (punch-in 100→115 %), FOTO/IA (Ken Burns, grade vermelho/preto na IA), GFX em código, carimbos, contador "PUNIÇÃO n/5" e legenda com a palavra ativa em amarelo |

## Pendências conhecidas

- **Caixa amarela dos prints:** como o script não sabe onde a frase está na imagem, ela aparece como faixa
  amarela abaixo do print, com o texto de `hl`.
- **Duração:** com a voz provisória o vídeo fica em ~7:45, já contando os respiros dos ATOS 3 e 6. A
  narração gravada costuma ser mais lenta. Se ainda ficar curta, aumente `respiro` nesses blocos em
  `roteiro.py`.
- **Checagem de fatos (seção 5 do handoff):** os textos na tela seguem o roteiro. A On divulga o
  resultado do 3º tri em 10/11, então revise S33 se publicar depois disso.
