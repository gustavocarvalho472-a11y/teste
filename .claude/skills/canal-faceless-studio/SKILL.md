---
name: canal-faceless-studio
description: Estúdio completo para canais faceless do YouTube (economia e qualquer outro nicho) feito quase todo dentro do Claude — identidade do canal, análise de canal de referência, ideias originais, roteiro travado, divisão em cenas, busca e seleção automática de vídeos reais gratuitos (Pexels, Pixabay, Internet Archive, Wikimedia, NASA etc.), gráficos, voz off, legendas e montagem final em MP4 com ffmpeg. Use quando o usuário quiser criar um canal faceless, roteirizar, achar vídeos livres para edição, ou montar/editar o vídeo sem CapCut.
---

# Faceless Studio

Estuda **o sistema** de um canal de referência (nicho, títulos, ganchos, ritmo, visual) e constrói algo **100% original**. A produção acontece aqui: o Claude escreve, busca clipes, gera gráficos, narra, legenda e monta o MP4.

## Regras invioláveis
1. **Nunca copiar** nome, branding, títulos, thumbnails, roteiros ou ideias distintivas do canal de referência — só princípios transferíveis.
2. **Narração travada** depois de aprovada; etapas seguintes não a alteram.
3. **Licença clara ou não usa.** Todo clipe externo entra em `assets/credits.csv`.
4. **Parar só nos pontos de decisão** abaixo; fora deles, executar a etapa inteira numa resposta.
5. Responder no idioma do usuário; prompts de imagem/vídeo e `stock_query` em inglês.
6. Não afirmar que algo funcionou sem checar o arquivo gerado (existe, duração correta, áudio presente).

## Etapa 0 — Projeto e nicho
- Perguntar/definir o nicho. Ler `references/niches/economia.md` ou `generico.md`.
- Criar `projects/<slug>/{assets,audio,out}` (relativo ao diretório de trabalho) e `script.md`, `scenes.json`, `project.json`.
- Rodar `bash scripts/setup.sh` uma vez (instala ffmpeg via imageio-ffmpeg, edge-tts, faster-whisper, matplotlib). Sem `ffmpeg` no PATH os scripts usam o binário do imageio.
- Perguntar se o usuário tem `PEXELS_API_KEY` / `PIXABAY_API_KEY` (grátis) — sem elas, só Wikimedia e Internet Archive.
- Ambientes restritos (proxy): se `edge-tts` ou downloads falharem por certificado, exportar `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` com o CA do ambiente; se o TTS continuar bloqueado, pedir o MP3 ao usuário (ElevenLabs etc.) e seguir.

## Etapa 1 — Identidade do canal
Entrada: 1 screenshot de canal de referência. Numa só resposta: análise de nicho + estilo visual, subnicho, **10 nomes originais**, descrição, **15 tags**, **3 handles**. **Parar e perguntar só o número do nome.** Depois, resumo final (nome, handle + variante, linha da descrição, prompts de logo/banner). Prompts: `references/prompts.md`.

## Etapa 2 — Padrões, ideias e roteiro
Entrada: títulos + 2–3 transcrições do canal de referência. Analisar ganchos, ritmo, estrutura, seleção de tópicos e curiosidade; dar **5 ideias originais** (uma linha). **Parar e perguntar:** número da ideia e duração (8/10/12 min). Escrever o roteiro completo em `script.md`; checklist: gancho forte, progressão clara, final cumpre a promessa. Ao aprovar, declarar **TRAVADO**.

## Etapa 3 — Cenas (plano de produção)
Dividir o roteiro em cenas (nova cena a cada ideia, local, número, empresa, país, argumento ou virada emocional). Gravar em `scenes.json`:
```json
{"scenes":[{"id":1,"narration":"...","duration":6.5,
  "source":"STOCK_VIDEO","stock_query":"stock exchange trading floor",
  "visual":"...","image_prompt":"(só AI_IMAGE)","video_prompt":"(só AI_VIDEO)","motion":"zoom_in"}]}
```
`source` ∈ `STOCK_VIDEO | CHART | MAP | TEXT_CARD | AI_IMAGE | AI_VIDEO`. Seguir o mix do preset do nicho. Estimar `duration` pelo número de palavras (~2,5 palavras/s). Para AI_IMAGE/AI_VIDEO gerar a âncora de estilo e os blocos numerados de prompts (`references/prompts.md`) — o usuário gera no Flow; o Claude não gera imagens.

## Etapa 4 — Material visual
1. **STOCK_VIDEO**: `python3 scripts/find_clips.py search scenes.json > candidates.json` → escolher 1 clipe por cena (critérios em `references/fontes-video.md`), gravar `selection.json`, `python3 scripts/find_clips.py download selection.json projects/<slug>/assets`. Para Internet Archive, baixar o .mp4 manualmente com `curl -L`. Mostrar tabela cena → clipe (+ alternativa) e pedir só exceções. Sugerir ao usuário fontes óbvias **e não óbvias** (`fontes-video.md`).
2. **CHART / MAP / TEXT_CARD**: montar `spec.json` e `python3 scripts/make_chart.py spec.json assets/sNN.png`. Dados reais só com fonte citada no próprio gráfico; nunca inventar números.
3. **AI_IMAGE / AI_VIDEO**: usuário gera no Flow com os prompts numerados e coloca os arquivos em `assets/sNN.*`. Corrigir só a cena errada.

Nomear tudo `assets/sNN.<ext>` (NN = id da cena com 2 dígitos).

## Etapa 5 — Voz e legendas
- Versão limpa da narração (sem marcações) em `audio/narration.txt`.
- `python3 scripts/tts.py audio/narration.txt audio/narration.mp3 --voice en-US-GuyNeural` (ou `--elevenlabs VOICE_ID` com `ELEVENLABS_API_KEY`).
- `python3 scripts/captions.py audio/narration.mp3 audio/captions.srt --lang en`.

## Etapa 6 — Montagem aqui (padrão)
1. Montar `project.json` (`narration`, `captions`, opcional `music`, `scenes[{file,duration,motion}]`). Vídeos são cortados/cropados para 16:9; imagens ganham Ken Burns (`zoom_in|zoom_out|pan_left|pan_right|none`); durações são reescaladas para casar com a narração.
2. Preview rápido: `python3 scripts/build_video.py project.json out/preview.mp4 --preview` (720p). Mostrar ao usuário e ajustar cenas apontadas.
3. Final: `python3 scripts/build_video.py project.json out/final.mp4` (1080p, legendas queimadas, música a 20% com ducking).
4. Verificar: arquivo existe, duração ≈ narração, tem trilha de áudio. Entregar `out/final.mp4` + `assets/credits.csv` (para descrição do vídeo).
Limitações: sem sincronização por cena com palavras-chave (proporcional à estimativa) — se uma cena ficar fora de sincronia, ajustar `duration` dela. CapCut permanece como alternativa manual.

## Resposta padrão
Cada etapa em uma resposta, com blocos copiáveis, dizendo qual é o próximo passo e o que precisa de decisão do usuário.
