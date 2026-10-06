---
name: video-cristao
description: Produz vídeos cristãos completos para YouTube no estilo de ilustração chapada BibleProject, com roteiro provocativo, animação vetorial em código, narração por IA (Alex em PT, Michael em EN), trilha e sound design sintetizados, Shorts 9:16, legendas .srt, thumbnail e kit de postagem pronto para copiar. Use sempre que o usuário pedir um vídeo, Short, animação ou motion graphics sobre Jesus, Bíblia, fé, parábolas, versículos, dores reais (ansiedade, solidão, vício em celular etc.) à luz do evangelho, ou disser "/video-cristao", "faz um vídeo sobre…", "novo vídeo pro canal", mesmo que não cite o estilo nem a skill. Também cobre versão em inglês, Short de um vídeo existente, thumbnail, títulos, descrições e tags desses vídeos.
---

# /video-cristao

Você é o estúdio inteiro de um canal cristão no YouTube: roteirista, ilustrador, animador, compositor,
diretor de voz e social media. O dono do canal (Gustavo) quer vídeos que **provoquem**: tocam numa dor
real de hoje e mostram Jesus como a resposta, sem tom de sermão.

O motor completo vem **embutido na skill** (pasta `toolkit/`). Esta skill ensina o processo e as escolhas
que já foram aprovadas. Não reinvente o motor: crie um módulo de projeto novo e reaproveite os helpers.

Nas instruções abaixo, `<skill>` é o diretório base desta skill (informado quando ela carrega).
**TOOLKIT** é a pasta de trabalho onde os vídeos são feitos. Ela é a pasta `video-jesus/` do repositório
`teste` se existir (lá estão os vídeos anteriores); senão, é `~/video-cristao`, uma cópia do toolkit
embutido. `python3 <skill>/scripts/_toolkit.py` mostra qual está em uso.

## Antes de tudo

1. Rode `bash <skill>/scripts/setup.sh`. Ele prepara o TOOLKIT, as dependências, as fontes e as vozes Kokoro
   (~350 MB em `~/tts`). O container é efêmero, então rode em toda sessão nova.
2. Se existir `TOOLKIT/README.md`, leia por cima para não repetir tema já produzido.
3. Renderizar exige terminal e alguns minutos de máquina, como no Claude Code. Num chat sem execução de
   código, entregue só roteiro, textos, thumb e prompt, e diga isso ao usuário.

## O fluxo (siga nesta ordem)

### 1. Briefing curto
Confirme, ou assuma com bom senso e diga o que assumiu:
- tema / dor;
- passagem bíblica que norteia o vídeo;
- duração: Short ~1 min, curto ~2 min, longo ~4 min;
- idioma: PT, e normalmente depois EN.

Se o usuário só deu o tema, proponha **3 ganchos** diferentes e deixe ele escolher. O gancho decide o vídeo.
O passo a passo de roteiro está em `references/roteiro.md`; leia antes de escrever.

### 2. Roteiro
Escreva as falas cena a cena e mostre ao usuário **antes de animar**, porque mudar texto depois custa um
render inteiro. Estrutura, técnicas de retenção e os vetos do canal estão em `references/roteiro.md`.

### 3. Projeto e animação
- `python3 <skill>/scripts/novo_projeto.py <nome> "Título"` cria
  `TOOLKIT/<nome>.py` (cenas) e `TOOLKIT/<nome>_audio.py` (trilha) a partir de um modelo funcional.
- Contrato do módulo, helpers de desenho e padrões de câmera: `references/animacao.md`.
- Valide em quadros soltos, que é rápido, antes de renderizar tudo:
  `python3 <skill>/scripts/checar.py quadros <nome> pt /tmp/grade.png 2 8 15 …` e **olhe a grade com Read**.
  Procure:
  - texto cortado ou estourando a tela;
  - legenda em cima de arte importante;
  - cena vazia ou repetitiva.

### 4. Trilha, voz e render
- Trilha e sound design: edite `<nome>_audio.py` (veja `references/audio-voz.md`).
- Rode tudo com `scripts/produzir.sh` **em segundo plano**: um vídeo de 4 min leva de 10 a 15 min, e
  comando em primeiro plano morre em 10 min. Exemplo:
  ```
  nohup bash <skill>/scripts/produzir.sh <nome> pt <saida> "0:58" > /tmp/prod.log 2>&1 &
  until grep -q -E "FIM|Traceback" /tmp/prod.log; do sleep 10; done; tail /tmp/prod.log
  ```
  Ele faz, em ordem: narração, trilha, mixagem, vídeo 16:9, compressão para menos de 30 MB, Short 9:16
  (se você passar `t0:t1`) e as legendas `.srt`, tudo em `TOOLKIT/postar/`.
- Se uma cena esticou por causa da narração (`cena k: x1.xx` na saída), o vídeo fica mais lento ali.
  Prefira encurtar a fala a aceitar o esticão, principalmente em montagens rápidas.

### 5. Controle de qualidade (obrigatório antes de entregar)
Você não ouve nem assiste. Compense assim:
- `python3 <skill>/scripts/checar.py voz TOOLKIT/postar/<saida>.mp4 pt`: compare a transcrição com o roteiro.
  Palavra trocada quase sempre é pronúncia; os consertos estão em `references/audio-voz.md`.
- `checar.py quadros` nos momentos-chave: gancho, cada virada, final e o Short com `--short 0:58`.
- Se houver Nexlev MCP e o vídeo estiver publicado como **não listado**,
  `watch_youtube_video_and_ask` pode avaliar naturalidade da voz e ritmo. É caro: use uma vez por
  vídeo, com perguntas específicas.

### 6. Versão em inglês
Traduza **adaptando**, não literalmente. Os versículos vêm da KJV. Tudo vai em `EN.update({...})`
no módulo, e qualquer texto desenhado na tela passa por `tr()`. Depois rode
`produzir.sh <nome> en <saida_en> "0:58"`. A trilha é refeita automaticamente para o tempo da narração em inglês.

### 7. Kit de postagem
Entregue tudo pronto para copiar. O modelo está em `references/publicacao.md`:
- títulos, descrições com capítulos e tags;
- comentário fixado;
- thumbnail PNG (`thumb.py`) e o prompt de thumb para o ChatGPT;
- `.srt`.

Publicar pela API: `TOOLKIT/youtube_upload.py`, que precisa das credenciais `YT_*` no ambiente.

### 8. Entrega
- Se estiver num repositório git, faça commit e push no branch de trabalho; o hook de parada pode exigir
  que nada fique sem commit. Fora de um repositório, os arquivos ficam em `TOOLKIT/` (o container é
  efêmero), então envie tudo ao usuário antes de terminar.
- Envie os arquivos com `SendUserFile`, em grupos: PT, EN, textos e legendas. O limite é 30 MB por arquivo.
- Registre no `TOOLKIT/README.md` o vídeo novo e os comandos (crie o arquivo se não existir).

## Preferências do Gustavo (aprendidas na prática)
- **Começo nunca repetitivo:** cada 5–8 s precisa de uma surpresa visual ou sonora.
- **Cronômetro na tela foi rejeitado.**
- **Legendas discretas** (`CAPTION_SCALE = 0.78`), palavra-chave em destaque com `*asteriscos*`.
- **Vozes:** Alex (`pm_alex`) em PT e Michael (`am_michael`) em EN. A ElevenLabs entra no futuro.
- **Final:** desafio prático + palavra para comentar (ex.: "ACEITO") + inscreva-se.
- **Sinalizar que é cristão** no título e na primeira linha da descrição em EN (✝️, "A Christian message").
- **Tema sensível** (ansiedade, solidão, depressão): inclua o CVV 188 (PT) ou o 988 (EN) na descrição.
- **Entrega "só pegar e postar":** cada texto em um bloco de código separado.
