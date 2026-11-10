# Canal de oração — produção de vídeos

O trabalho deste repositório está em `video-salmos/` (branch `video-salmos`). Responda sempre em português do Brasil.

## Chaves (nunca escrever no código, no chat ou em commits — o repositório é público)
- `PEXELS_API_KEY` e `CARTESIA_API_KEY`: lidas do ambiente ou de `.env` na raiz (git-ignorado).
- Se faltarem, peça ao usuário para adicioná-las como variáveis do ambiente de nuvem (menu do ambiente → Edit) ou no `.env`. Não peça para colar no chat.
- Pexels exige o header `Authorization: <chave>` sem "Bearer".

## Pipeline (rodar dentro de `video-salmos/`, com `~/venv-salmos/bin/python`)
1. Roteiro: `xxx_fonte.txt` → `python build_roteiro.py xxx_fonte.txt xxx.json`
   - Formato: `# id | Título do bloco` e linhas `tag|referência|frase` (referência só nos versículos).
   - Sem números, parênteses ou travessões na frase (escrever "noventa e um"). Sem frases duplicadas.
   - Tags: ceu_noturno, lua, nascer_sol, luz_divina, vela, campo, pastor_ovelhas, rio, mar_calmo, montanha, floresta, chuva_janela, cruz, aguia.
2. Voz: `python 01_tts.py --motor cartesia --voz Rafael --velocidade 1.0 --roteiro xxx.json --pausa-frase 0.45 --pausa-bloco 1.6 --meta MIN-MAX`
   - Gera `audio/narracao.wav` e `timeline.json`. Cache por frase em `audio/frases/`.
   - Cartesia cobra 1 crédito por caractere (plano grátis: 20 mil/mês ≈ 1 vídeo de 12 min). Conferir o tamanho antes.
3. Alinhar legenda: `python 01b_alinhar.py` (faster-whisper; palavras com tempo em `timeline.json`).
4. Cenas: `python 02_pexels.py` (baixa clipes para `clips/`, monta `cenas.json`, sem repetir em 10 min, cena máx. 7,5 s).
5. Render: `python 03_edit.py --final-suave 0 --saida out/NOME.mp4` (≈2x tempo real; retoma blocos prontos). `--previa 120` faz prévia de 2 min.
6. Extras: `VIDEO=<nome> python 04_extras.py` (srt, capítulos, título, descrição, tags, thumbs). Adicionar um bloco `elif` com os textos do vídeo novo.
7. Cópia para envio (< 500 MB): `ffmpeg -i out/NOME.mp4 -vf hqdn3d=2:2:5:5 -c:v libx264 -preset medium -crf 21 -maxrate 5000k -bufsize 10000k -c:a copy -movflags +faststart out/NOME_envio.mp4`

## Regras de conteúdo (pedidas pelo usuário)
- Estrutura de cada parte: contexto real de quem ouve ("Hoje eu quero orar por você que...") → versículo → explicação curta → oração em tom humano, em primeira pessoa.
- Frases longas e fluidas, nada picado. Nunca "Deus me mostrou", revelação ou testemunho inventado.
- Prosperidade como provisão, trabalho e paz; não prometer enriquecer.
- Versículos em paráfrase própria baseada em Almeida.
- Imagens só de natureza e paisagens: sem pessoas, mãos, cidades, estradas, casas ou imagens de outras religiões.
- Nunca repetir clipes de vídeos anteriores: `clips/usados.json` guarda todos os IDs já usados e o `02_pexels.py` os evita (busca mais páginas no Pexels quando faltam clipes novos). Depois de entregar um vídeo, acrescente os IDs do `cenas.json` em `clips/usados.json`.
- O vídeo começa com uma montanha (primeira frase com tag `alpes` ou outra de montanha), nunca com o mesmo céu estrelado.
- Antes de renderizar, montar uma folha de contato com as miniaturas dos clipes escolhidos, olhar e bloquear (`clips/bloqueados.json`) os ruins.
- Áudio do Suno: o texto exato está na conta do Suno (conector Suno, `audio-retrieve` traz `metadata.lyrics`); use `01c_externo.py` e `03_edit.py --musica-db -90` quando o áudio já tiver música.
- Legenda centralizada, Inter bold branca, palavra por palavra; chuva leve e trilha suave ao fundo; -14 LUFS.
- Thumbnails: texto grande em 3-4 linhas alternando branco e amarelo, fundo de natureza ou noite (estilo dos outliers pesquisados no vidIQ).
- Descrição do YouTube até 5.000 caracteres (crédito do Pexels em uma linha). Marcar "conteúdo sintético" (voz de IA).
- Entregar ao final: vídeo, thumbs A e B, e título, alternativas, descrição e tags no chat.

## Vídeos já feitos
- `oracao_noite_v2` (12 min): medo, contas, família, trabalho, pessoas, saúde — `roteiro16_fonte.txt`.
- `oracao_esperanca` (6 min): prosperidade, Jeremias 29:11 e Hebreus 6:19 — `roteiro_esperanca_fonte.txt`.
