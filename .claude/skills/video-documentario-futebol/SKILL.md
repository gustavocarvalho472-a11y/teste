---
name: video-documentario-futebol
description: Produz do zero um vídeo-documentário de futebol (8–13 min, 16:9) no estilo do canal — roteiro, narração, takes reais de reportagens cortados a cada 3–5 s dentro de moldura, motion graphics estilo TV em verde-limão e preto, sound design, legendas e MP4 final — tudo por código (ffmpeg + Chromium headless), sem editor de vídeo. Use quando o usuário pedir "faz um vídeo sobre…", "roteiro e edição", "edita igual ao vídeo de referência", "pega os takes", "monta o vídeo", ou mandar um link do YouTube para recriar em outro idioma ou ângulo.
---

# Vídeo-documentário de futebol (roteiro → takes reais → motion → vídeo final)

Esta skill registra o processo que produziu "Manchester City's 115 Charges" (12 min, 81 cenas, 160 takes).
O exemplo completo está em `exemplo/build_manchester_city.py` — **leia-o antes de começar**: é o molde do arquivo que você vai escrever para cada vídeo novo.

## Como funciona (e por que é rápido)

Não existe editor de vídeo nem computador do usuário envolvido. Tudo roda no container da sessão:

| Etapa | Ferramenta | Arquivo |
|---|---|---|
| Linha do tempo (texto + visual de cada cena, sincronizada com a voz) | Python | `build.py` (um por vídeo) |
| Mapear os planos de cada reportagem e gerar folhas de contato | ffmpeg (detecção de corte) | `scripts/shots.py` |
| Motion graphics, quadro a quadro | Chromium headless (Playwright) | `scripts/render.js` |
| Moldura "video wall" | Chromium headless | `scripts/frame.js` |
| Cortar takes, compor, mixar áudio, gerar MP4 e .srt | ffmpeg + numpy | `scripts/assemble.py` |
| Narração gratuita | Kokoro | `scripts/tts_kokoro.py` |

O que dá velocidade:
- **Nada é feito à mão**: um corte é uma linha de dados, não um clique.
- **Paralelismo**: 4 páginas do Chromium renderizam cenas ao mesmo tempo; 3 ffmpeg codificam cenas ao mesmo tempo.
- **Uma cena = um arquivo** em `build/seg/`. Mudou uma cena? `python3 assemble.py --reuse` recodifica só as que faltam e remonta em ~1 min. Apague apenas os `seg/<id>.mp4` (e `frames/<id>/`) do que mudou.
- **Prévia barata antes do render caro**: `node render.js --still <ids>` gera 1 quadro por cena em segundos. Só rode o render completo (~25 min para 12 min de vídeo) depois de aprovar os stills.
- **"Ver" o vídeo sem assistir**: extraia quadros com ffmpeg e junte numa grade (folha de contato). Uma imagem mostra 40 planos. É assim que se escolhem takes e se faz o controle de qualidade.

Preparação da pasta do vídeo:
```bash
mkdir -p video-production/<slug>/{assets/{vo,music,stock,real},build,out} && cd video-production/<slug>
cp <skill>/scripts/* . && npm i --silent d3-geo@3 topojson-client@3 world-atlas@2 @fontsource/bebas-neue @fontsource/oswald
cp <skill>/exemplo/build_manchester_city.py build.py   # depois reescreva CHAPTERS, POOLS e a abertura
```
Chromium e Playwright já vêm instalados; não rode `playwright install`.

## Etapa 0 — Ambiente e custos (resolva antes de tudo)

- **Rede**: o container só baixa de hosts liberados. Necessários: `assets.vidiq.com`, `ai-music-tracks.s3.us-east-1.amazonaws.com`, `videos.pexels.com`, `images.pexels.com`, `storage.googleapis.com`; para Kokoro, `huggingface.co`. Se um download der `403/000`, use `get_environment` e proponha a liberação com `update_environment`/`create_environment` (o usuário aprova). Sites de notícia costumam ser recusados — não conte com print de matéria tirado direto do site.
- **Créditos vidIQ**: confira `vidiq_balance` antes. Referência do vídeo de exemplo: análise visual do vídeo de referência 25; busca YouTube 5 por consulta; transcrição 5; trilha 25 cada; b-roll 1 por busca; narração paga 28 por 1.000 caracteres (evite — use Kokoro). **Importar vídeo do YouTube (`vidiq_video_upload`) é gratuito.**
- O MP4 final passa de 100 MB: não entra no git. Entregue com `SendUserFile` e deixe `assets/real/`, `assets/stock/`, `build/` e `out/*.mp4` no `.gitignore`.

## Etapa 1 — Roteiro

> **Leia primeiro `references/manual-de-roteiro.md`**: como achar o tema da semana, o teste do ângulo, as famílias de título e a estrutura de 8 minutos (formato Becir). A estrutura abaixo é a do documentário longo de exemplo (12 min); use-a quando o vídeo for investigativo.

1. Se houver vídeo de referência: `vidiq_video_transcript` (texto) e `vidiq_video_watch` com pedido de shot list (ordem dos assuntos e do tipo de imagem). Use como mapa de assuntos, nunca copie o corte nem os gráficos do outro canal.
2. Estrutura que funcionou:
   - **Abertura fria (25–35 s, sem narração)**: flash de 5 s de glória (títulos, gols, cortes de ~1,3 s) + 3 a 5 falas reais de acusação com áudio original, cada uma de 4–7 s, terminando no veredito. Depois a vinheta de título.
   - **Capítulo 1**: a promessa ("bom demais para ser verdade") e a apresentação do personagem que ninguém conhece.
   - **5–7 capítulos** de 40–160 s, cada um com cartela numerada. Frases curtas. Um número ou nome próprio por frase.
   - **Fecho** que retoma a frase da abertura.
3. **Idioma:** o vídeo é sempre em inglês. O arquivo do roteiro traz o script em inglês **e, logo abaixo, a tradução completa em português**, só para o usuário validar (nada do português vai para a narração nem para a tela). Mantenha as duas versões sincronizadas a cada alteração.
3b. Escreva o roteiro já **em beats**: cada beat = 1–3 frases (3–20 s de fala) + o visual. Um beat nunca termina no meio de uma frase.
4. Alegações contra pessoas: mantenha "alleged/denied" no texto **e** na tela. Fatos recentes que você não consegue confirmar: avise o usuário.
5. Números em gráfico precisam de fonte. Sem número confiável, não desenhe barra com valor.

## Etapa 2 — Narração

**Padrão: Kokoro (gratuito, licença Apache, voz que o canal já usa).**
```bash
python3 tts_kokoro.py --voice am_michael --beats beats.json --outdir assets/vo   # um MP3 por beat
```
- Vozes boas em inglês: `am_michael`, `am_onyx`, `am_fenrir` (americanas), `bm_george`, `bm_lewis` (britânicas). Português: `--lang p` com `pm_alex`.
- Como é grátis, **gere um arquivo por beat**: a duração de cada arquivo dá o tempo exato da cena e dispensa o alinhamento por silêncio. Adapte `beat_times()` no `build.py` para ler `durations.json` (soma acumulada + 0,25 s de respiro entre beats).
- O script do Kokoro não foi testado no ambiente original (Python 3.13 e huggingface bloqueado). Teste uma frase primeiro. Se não rodar, alternativas gratuitas: **Piper** (leve, roda em qualquer lugar, qualidade menor), **Chatterbox** (MIT, muito natural, pede GPU), **MeloTTS** (MIT). Evite XTTS e F5-TTS em canal monetizado: os pesos têm licença não comercial.
- **Fallback pago**: `vidiq_voiceover_generate` (voz "Daniel – Steady Broadcaster"), um job por capítulo. Aí o `build.py` do exemplo já resolve o tempo dos beats: detecta silêncios (`silencedetect -34dB`) e encaixa cada fim de beat no silêncio mais próximo do tempo estimado por número de caracteres. Confira que nenhum corte caiu fora de um silêncio.
- Siglas: escreva `T.P.O.`, `U.A.E.`; números por extenso quando a leitura for ambígua.

## Etapa 3 — Buscar as fontes reais

Objetivo: 20–30 reportagens que cubram todos os assuntos do roteiro.

1. **Buscar**: `vidiq_youtube_search` com `type:["video"]`, `videoDuration:"short"`, `limit` 4–8 (resposta compacta). O `youtube_search` do Nexlev é grátis, mas devolve ~4 mil tokens por busca — use pouco.
2. **O que procurar** (do melhor para o pior):
   - Agências com imagem bruta e sem apresentador: **AFP, Reuters, AP Archive** (1–2 min, quase tudo aproveitável).
   - Reportagens longas de TV (**BBC, Sky, ITV**): rendem dezenas de planos e falas com áudio.
   - Documentários (ex.: NDR/STRG_F) para o personagem principal.
   - Canal oficial do clube: imagem linda, mas mistura épocas e é o que mais gera bloqueio.
   - Evite: vídeos com tarja de texto o tempo todo, marca d'água grande (Ruptly), uploads de terceiros em 360p.
3. **Importar**: `vidiq_video_upload` com a URL do YouTube (grátis, vem em até 1080p). Máximo ~10 jobs simultâneos; se recusar, espere e reenvie. Faça `vidiq_job_poll` e baixe o `videoUrl` com `curl` para `assets/real/<nome>.mp4` (nomes curtos: `city_bbc_long`, `rui_trial_reuters`).
4. **Transcrição das fontes com fala** (`vidiq_video_transcript`, 5 créditos): é onde aparecem as falas de acusação para a abertura e a confirmação de quem é quem.
5. **Banco de imagens** (`vidiq_find_broll`, Pexels) só para o que não tem arquivo: cidades, teclado, documentos, dinheiro. Prefira os links `hd_1920_1080`; vários só vêm em 360p.
6. Registre toda fonte (arquivo, ID do YouTube, emissora) no README do vídeo.

## Etapa 4 — Escolher os takes

```bash
python3 shots.py            # detecta planos das fontes novas e gera build/shots/sheet_new_*.jpg
```
Abra cada folha com `Read`. Cada miniatura traz `fonte índice (duração)`. Anote por tema os índices bons.

Regras aprendidas (cada uma veio de um erro real):
- **Época e clube certos.** Vídeo de carreira mistura fases: o Guardiola apareceu de Bayern/Barcelona num vídeo sobre o City. Confira camisa, patrocinador e fundo antes de pôr o plano no pool.
- **Sem texto queimado**: descarte planos com tarja, legenda de outro idioma, "comunicado" ou gráfico da emissora. Logo pequeno de canto (AP, AFP, ITV) é tolerável; avise o usuário.
- **Legenda embutida em entrevista**: corte com `crop` (ex.: `crop=iw*0.78:ih*0.76:iw*0.11:ih*0.02,`) em vez de descartar.
- **Vídeo vertical ou com barras** (Shorts, Sky no celular): nunca deixe o corte automático pegar o centro — só aparece o terno. Use o modo `pillar` (recorte + fundo desfocado) e confira o rosto.
- **Plano único longo** (coletiva, torcida): use como janela `win(fonte, início, fim)`; o alocador fatia em pedaços de ~4,6 s.
- **Não identifique ninguém pelo rosto.** Nome em legenda só quando a transcrição ou a descrição da fonte disser quem é.
- Para conferir um plano duvidoso, extraia quadros a cada 2 s daquele trecho numa mini-folha.

## Etapa 5 — Pools e linha do tempo (`build.py`)

- `POOLS`: tema → lista de takes (`sh(fonte, índices…)`, `win(fonte, a, b)`, `st(banco…)`, `shc(fonte, crop, índices…)`).
- `SCENE_POOLS`: para cada beat, os temas que ilustram aquela fala (`"mansour+etihad"`). O alocador alterna os temas e nunca repete o mesmo take em sequência.
- **Ritmo**: padrão 4 s por take (resultado: 3–5 s). `SCENE_CUT` acelera cenas específicas (abertura e primeiros beats: 1,3–1,8 s).
- Siga a ordem de assuntos do vídeo de referência, com fontes próprias.
- Cada beat escolhe o gráfico: `S(...)` = take dominante com texto leve (`stat`, `word`, `lower`, `chips`, `none`) e moldura; `G(...)` = gráfico de dados sobre o take escurecido (`counter`, `list`, `bars`, `flow`, `flow3`, `org`, `define`, `doc`, `terminal`, `names`, `trend`, `bigtext`). Tela cheia sem vídeo só para `bumper`, `sting`, `map`, `article`, `end`.
- Abertura: cenas `caps` com `takes` fixos e `nat` (áudio original). Frases com `*palavra*` ficam marcadas em destaque. Ache o tempo das falas pela transcrição + envelope de volume; se não der para medir, diga ao usuário que é estimado.
- `python3 build.py > build/timeline.txt` e leia o resumo: duração total, takes por cena, % de arquivo real (meta ≥ 65%).

## Etapa 6 — Motion graphics (identidade do canal)

- Paleta: **verde-limão `#C6FF00` + preto**, branco para texto, vermelho `#FF5247` só para alerta/carimbo. Fontes: Bebas Neue (títulos), Oswald (rótulos), Inter (texto), JetBrains Mono (terminal).
- Elementos fixos: selo "SPECIAL REPORT", bug do canal no canto superior direito, faixa inferior com o capítulo. Troque o texto do bug pelo nome do canal.
- Cada template é uma função em `render.js` que devolve HTML com animações CSS; o renderizador pausa as animações e avança o tempo quadro a quadro (25 fps), então o resultado é determinístico.
- Sempre: `node render.js --still <ids>` → montar folha → olhar → só então `node render.js`.
- Erros de layout já vistos: título quebrando em duas linhas, carimbo sobre o texto, rótulo de mapa em cima do título, legenda grande cobrindo rosto. Olhe os stills procurando exatamente isso.
- Print de matéria com marca-texto (`article`): use manchete real que apareça dentro de uma reportagem (recorte o quadro) e anime as marcações por cima. **Não desenhe página falsa de jornal.** Recriações de e-mail/contrato levam a etiqueta "ILLUSTRATIVE RECREATION".

## Etapa 7 — Sound design e mixagem (já dentro do `assemble.py`)

- **Trilhas**: 3 faixas instrumentais (`vidiq_generate_music`, 25 créditos cada, ou Suno): batida investigativa ~95 BPM, drone tenso ~70 BPM, final emotivo. Cada capítulo aponta para uma (`"music"`). Reaproveite as do exemplo quando o tom for o mesmo.
- **Ducking automático**: a trilha cai para ~17% quando há voz e sobe para ~62% nas pausas.
- **Efeitos sintetizados em numpy** (não precisam de banco): whoosh em cada corte, impacto grave nas cartelas e palavras-chave, riser antes do título, ticks nos contadores, teclas nos terminais, pop em itens de lista, baque no carimbo.
- **Silêncio de impacto**: `mute_music: True` na frase-virada ("It was.").
- Saída normalizada em **-14 LUFS**. Você não consegue ouvir: diga isso ao usuário e peça que confira a mixagem.

## Etapa 8 — Montagem e render

```bash
node frame.js                                  # uma vez: moldura
node render.js                                 # camadas gráficas (~25 min / 12 min de vídeo)
python3 assemble.py                            # tudo; ou: python3 assemble.py --reuse
```
Rode os dois comandos longos em segundo plano e acompanhe pelo log. O `.srt` sai junto em `out/`.

## Etapa 9 — Controle de qualidade (obrigatório antes de entregar)

1. Folha de contato do vídeo final: 1 quadro a cada ~12 s, e **1 a cada ~1,2 s nos primeiros 40 s**.
2. Procure: rosto cortado, legenda sobre boca/olhos, take de outra época ou clube, texto de emissora por baixo de título, quadro preto, gráfico vazando da tela.
3. `ffmpeg -i out.mp4 -af ebur128 -f null -` → perto de -14 LUFS.
4. Corrigiu algo? Apague só os `seg` afetados e `assemble.py --reuse`.

## Etapa 10 — Entrega

- `SendUserFile` com o MP4 e o `.srt`; commit dos scripts, narração, trilhas e manifestos.
- Diga sempre, sem enfeite: o que não tem imagem real, onde há logo de emissora, quais tempos de legenda são estimados, quais números não foram confirmados, e que **todo material de arquivo é de terceiros e não licenciado** (jogos e canal oficial de clube são os mais visados pelo Content ID).
- Thumb e título: dois rostos (um nítido, um apagado atrás), fundo escuro, duas palavras que não explicam sozinhas; título curto que completa a história.

## Lições do vídeo do Brasil (nov/2026) — siga sempre

**Roteiro e validação**
- Sempre entregue o roteiro em PT no chat para o usuário validar antes de gerar narração (ele lê no celular e não abre arquivos). O vídeo é sempre em inglês.
- Narração corrida, estilo Becir: frases que puxam a próxima, ganchos no fim de cada bloco. Frases curtas e truncadas soam como IA e foram rejeitadas.
- Checagem de fatos antes de escrever: o usuário traz memes, falas e números; confirme (WebSearch) e diga o que mudou. Ex.: a fala do Raphinha sobre "férias" era sobre o Mundial de Clubes; a "Bola de Ouro" do Vini é na verdade o The Best da FIFA.
- O narrador não acusa; críticas pesadas ficam na boca de torcedores, ídolos ou comentaristas. Evite termos como "afeminados" (risco de desmonetização e briga nos comentários).
- CTA (like, inscrever, mandar para um amigo) logo depois da introdução/título, não no final.
- Para validar sem gastar créditos: versão PT com `espeak-ng` (apt) e legenda PT queimada no topo (ver `exemplo/build_brazil.py` e o histórico).

**Imagens e direitos autorais**
- NÃO use nenhum vídeo da FIFA (Copas, FIFA TV, FIFA+, gols em Copas, premiação The Best): o vídeo foi bloqueado no mundo todo por isso. Antes de publicar, suba como não listado e espere as reivindicações.
- Substitutos que funcionaram: reportagens da AP Archive (torcida, ruas), lances por clube (Barcelona etc.), entrevistas (UOL, ESPN FC, Fora de Campo) e **fotos livres do Wikimedia Commons** (Agência Brasil CC BY 3.0 BR tem fotos de jogos da seleção; Pelé 1970 é domínio público). Hosts a liberar: `commons.wikimedia.org`, `upload.wikimedia.org`. A API tem limite (429): uma busca a cada ~25 s.
- Fotos entram animadas (`ph("nome")` no pool → zoom/pan + flash no `assemble.py`); fotos verticais vão para 16:9 com fundo desfocado. Misture foto + vídeo — o usuário gostou.
- Liste os créditos das fotos em `assets/photos/CREDITS.md` e entregue o texto pronto para a descrição.
- Não use takes com texto solto em PT de canais brasileiros, cartelas, miniaturas de Shorts nem logos de outros canais.
- Fala em PT com áudio original → legenda em EN.

**Edição**
- Abertura muito dinâmica: cortes de ~1 s, gráficos pequenos no canto (não números gigantes parados), misture jogo + reação.
- Quando citar um craque antigo, mostre ele jogando (lances/skills) ou foto; quando citar um personagem (ex.: Zico), coloque imagem dele para a pessoa saber quem é.
- O render completo passa de 30 min; rode em background com timeout longo e reaproveite segmentos (`--reuse`, apagando só `build/seg/<id>.mp4` das cenas alteradas).

## Lições do vídeo do Ferguson/Pochettino (nov/2026) — ambiente e velocidade

**Ferramentas grátis que funcionam neste container (huggingface, YouTube, Openverse e Flickr estão bloqueados)**
- **Narração**: Kokoro em ONNX, com o modelo baixado do GitHub (não do huggingface):
  `pip install kokoro-onnx soundfile` e os arquivos `kokoro-v1.0.onnx` / `voices-v1.0.bin` de `github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/` em `/opt/kokoro`.
  Script: `scripts/tts_kokoro_onnx.py` (lê `lines.txt` no formato `id|texto`, gera um MP3 por beat + `durations.json`, corta silêncio das pontas, e tem um dicionário `SAY` de pronúncia: Pochettino → "Potchettino", Solskjær → "Solshare" etc.). ~2 s por frase em CPU.
  Atenção: o comando em segundo plano pode "terminar" antes do download acabar; confira o tamanho dos arquivos antes de testar.
- **Transcrição (achar falas e tempos) sem gastar créditos**: sherpa-onnx + Whisper base.en do GitHub:
  `pip install sherpa-onnx` e `github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-base.en.tar.bz2` em `/opt/asr`.
  `python3 scripts/asr.py fonte.mp4 [inicio fim janela]` imprime `[t] texto` por janela (8 s para varrer, 2–3 s para cravar o início e o fim da fala). 60 s de áudio em ~6 s. Use no lugar de `vidiq_video_transcript` (5 créditos) e do Nexlev (5 transcrições/dia).
- **Nexlev grátis**: 5 transcrições por 24 h e **50 chamadas por semana no total** (as buscas gastam ~5 mil tokens cada). Planeje as buscas: uma rodada só, anotando todos os IDs úteis de cada resultado.
- **Importar do YouTube**: `vidiq_video_upload` (grátis), no máximo ~10 jobs ao mesmo tempo; baixe o `videoUrl` com `curl` (host `storage.googleapis.com`).
- **Wikimedia Commons**: a API (`commons.wikimedia.org/w/api.php`) pode ficar dias em 429 para o IP de saída, e as miniaturas vêm de `thumb.wikimedia.org` (bloqueado). Baixe o original de `upload.wikimedia.org` e reduza com ffmpeg (`scripts/photos_commons.py`). Se der 429, deixe um laço tentando a cada 5 min e siga com vídeo.

**Escolha de takes**
- Fontes de câmera contínua (discurso, coletiva) têm 1–3 "planos" no `shots.py`; use `scripts/peek.py nome passo` (quadro a cada N s com o tempo escrito) e `win(fonte, a, b)`.
- Coletiva em plano aberto (três pessoas na mesa): recorte no rosto com `CROP` (ex.: `crop=iw*0.38:ih*0.38:iw*0.285:ih*0.36,`).
- Canal de fã com logo no canto e vídeo de notícia com tarja de nome: recorte (`crop=iw*0.8:ih*0.8:iw*0.2:ih*0.2,` tira o canto superior esquerdo; `crop=iw*0.8:ih*0.8:iw*0.1:0,` tira o rodapé).
- Vídeo que "lê" matéria com voz robótica não é fala real: use só o texto citado, confirmado na imprensa, como gráfico `define` com a data.
- Nome em `lower` só sobre take em que a pessoa aparece de rosto; take de treino genérico não serve.

**Render mais rápido**
- `render.js` agora para de capturar quadros quando todas as animações da cena terminam (calcula o fim pelas animações CSS + contadores + digitação) e o `assemble.py` congela o último quadro (`overlay` repete o último quadro; cenas de tela cheia usam `tpad=stop_mode=clone`). Por isso o ponto vermelho do selo não pisca mais (animação infinita impede a otimização).
- `assemble.py` com `-preset fast`.
- Prévia: `node render.js --still` leva ~3 s para 69 cenas. Monte a grade com PIL (o `concat` do ffmpeg com JPEGs de formatos diferentes sai preto).
