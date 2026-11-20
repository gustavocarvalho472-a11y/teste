# Canal de oração — produção de vídeos

O trabalho deste repositório está em `video-salmos/` (branch `video-salmos`). Responda sempre em português do Brasil, de forma curta e direta. O usuário trabalha muito pelo celular.

## Chaves (nunca escrever no código, no chat ou em commits — o repositório é público)
- `PEXELS_API_KEY` (e `CARTESIA_API_KEY`, se usar Cartesia): lidas do ambiente ou de `.env` na raiz (git-ignorado).
- Se faltarem, peça ao usuário para adicioná-las como variáveis do ambiente de nuvem (menu do ambiente → Edit) ou no `.env`. Não peça para colar no chat.
- Pexels exige o header `Authorization: <chave>` sem "Bearer".
- O venv fica em `~/venv-salmos` (o script de setup do ambiente o cria). Se não existir: `python3 -m venv ~/venv-salmos && ~/venv-salmos/bin/pip install -r video-salmos/requirements.txt`.
- Clipes (`clips/*.mp4`), áudios e vídeos não vão para o git: numa sessão nova o `02_pexels.py` baixa de novo o que precisar.

## Fluxo principal hoje: voz do Suno + imagens do Pexels
1. **Roteiro** (quando o usuário pede um texto novo): escrever seguindo as regras de conteúdo abaixo. Para colar no Suno:
   - Tom fixo: "Homem brasileiro, voz grave e acolhedora, orando com sinceridade como um pastor numa oração antes de dormir. Ritmo natural e fluido, sem pressa mas sem arrastar, com pequenas pausas entre as frases. Tom íntimo, calmo e cheio de esperança, como quem fala perto de uma pessoa cansada. Violão suave ao fundo, bem baixo. Português do Brasil, pronúncia clara."
   - O Suno aceita até 5.000 caracteres, mas **corta o áudio perto de 7 min** (~3.400 caracteres). A voz fala ~8 caracteres/s. Para vídeos maiores, dividir em partes de até ~3.300 caracteres, cortando no fim de uma oração.
   - O Suno bloqueia texto bíblico com direitos autorais: versículos sempre em paráfrase própria, nunca a Almeida literal.
   - Entregar o texto no chat dentro de bloco de código (para copiar), mas títulos e descrições em texto simples (o app do YouTube no celular trava com bloco de código, emojis e o símbolo "|").
2. **Áudio**: o usuário manda o MP3 aqui no chat (ou um link de página/artifact). Converter: `ffmpeg -i x.mp3 -ar 48000 -ac 2 work/<nome>/x.wav`.
   - Nunca baixar áudio contornando o limite de downloads do plano dele.
   - Texto exato da gravação: conector Suno → `library-search`/`library-list` → `audio-retrieve` (traz `metadata.lyrics`; clipes concatenados também).
   - Duas partes (ou Suno + outra voz): juntar com `ffmpeg` (atrim/afade/concat), igualar volume com `volume=xdB` para ~-16 LUFS cada, 2–3 s de pausa entre elas.
3. **Roteiro do vídeo** a partir da letra: estrofes viram frases em `roteiro_<nome>_fonte.txt` (`# id | Título do capítulo` e `tag|referência|frase`), depois `python build_roteiro.py roteiro_<nome>_fonte.txt roteiro_<nome>.json`.
4. **Alinhar**: `python 01c_externo.py --audio work/<nome>/x.wav --roteiro roteiro_<nome>.json --outro 8 --texto-final "Escreva amém nos comentários" --tag-final alpes` (gera `audio/narracao.wav` e `timeline.json` com tempo por palavra; >90% casadas é bom).
5. **Cenas**: `CENA_MAX=8 python 02_pexels.py` → `cenas.json`. Depois montar a **folha de contato** (miniaturas de `clips/thumbs/`), olhar e bloquear os ruins em `clips/bloqueados.json`, rodar de novo.
6. **Render**: `rm -rf work/blocos work/seg` e `python 03_edit.py --final-suave 8 --musica-db -90 --saida out/<nome>.mp4` (rodar em segundo plano; ~2x tempo real; retoma blocos prontos; `--musica-db -90` porque o Suno já tem música).
7. **Conferir**: ffprobe (duração), `ebur128` (~-14 LUFS), 4 frames (início, meio, emenda, fim). Trocar clipe ruim direto no `cenas.json` e rodar o render de novo (só o bloco muda).
8. **Cópias**: 1080p `-preset veryfast -crf 22 -maxrate 4000k` (`_envio.mp4`) e 720p `-crf 24 -maxrate 1400k scale=1280:720` (`_720p.mp4`, para baixar no celular). Mandar as duas.
9. **Extras**: `VIDEO=<nome> python 04_extras.py` (srt, capítulos, título, descrição, tags, thumbs). Adicionar um bloco `if/elif` com os textos e as thumbs do vídeo novo.
10. **Depois de entregar**: acrescentar os IDs do `cenas.json` em `clips/usados.json`, apagar o `out/<nome>.mp4` mestre (o disco enche rápido), commit e push.

O fluxo antigo com voz Cartesia (`01_tts.py --motor cartesia --voz Rafael` + `01b_alinhar.py`) continua funcionando, mas o plano grátis só dá ~1 vídeo/mês.

## Regras de conteúdo (pedidas pelo usuário)
- Estrutura de cada parte: contexto real de quem ouve ("Hoje eu quero orar por você que...") → versículo → explicação curta → oração em tom humano, em primeira pessoa.
- Frases longas e fluidas, nada picado. Nunca "Deus me mostrou", revelação ou testemunho inventado.
- Prosperidade como provisão, trabalho e paz; não prometer enriquecer.
- Imagens só de natureza e paisagens bonitas (montanhas, céu estrelado, lagos, vales com névoa, nascer do sol): sem pessoas, mãos, cidades, luzes de cidade, estradas, casas, barcos ou imagens de outras religiões.
- **Nunca repetir clipes de vídeos anteriores**: `clips/usados.json` guarda todos os IDs já usados e o `02_pexels.py` os evita (busca mais páginas no Pexels quando faltam clipes novos).
- **O vídeo começa com uma montanha** (primeira frase com tag `alpes` ou outra de montanha), nunca com o mesmo céu estrelado.
- Tags de cena: alpes, picos_neve, dolomitas, cordilheira, estrelas_montanha, lago_alpino, paisagem_aerea, lago_montanha, vale_nevoa, montanha, ceu_noturno, lua, nascer_sol, luz_divina, cachoeira, campo_flores, mar_calmo, rio, floresta. Para criar busca nova, acrescentar em `QUERIES`, `RELACIONADAS` e `POOL_NATUREZA` (`02_pexels.py`) e em `TAGS` (`build_roteiro.py`).
- Legenda centralizada, Inter bold branca, palavra por palavra; chuva leve ao fundo; -14 LUFS; no fim "Escreva amém nos comentários".
- Thumbnails: texto grande em 3-4 linhas alternando branco e amarelo (Inter Black), fundo de montanha ou céu estrelado claro o bastante (estilo dos outliers pesquisados no vidIQ). Fazer A e B.
- Título até 100 caracteres. Descrição até 5.000 caracteres, com capítulos e "Imagens: vídeos gratuitos do Pexels." Lembrar de marcar "conteúdo sintético" (voz de IA).
- Entregar ao final: vídeo (720p e 1080p), thumbs A e B, legenda, e título + 2 alternativas + descrição + 18 tags no chat em texto simples.

## Vídeos já feitos
- `oracao_noite_v2` (12 min, Cartesia): medo, contas, família, trabalho, pessoas, saúde — `roteiro16_fonte.txt`.
- `oracao_esperanca` (6 min, Cartesia): prosperidade, Jeremias 29:11 e Hebreus 6:19 — `roteiro_esperanca_fonte.txt`.
- `oracao_ansiedade` (7,5 min, Suno): ansiedade antes de dormir — `roteiro_ansiedade_fonte.txt`.
- `oracao_salmo1` (10 min, Suno + Gemini): Salmo 1 — `roteiro_salmo1_fonte.txt`.
- `oracao_noite19` (19 min, Suno): Durma na presença de Deus — `roteiro_noite19_fonte.txt`.
- `oracao_s128` (10,5 min, Suno): Salmo 128 e ansiedade — `roteiro_s128_fonte.txt`.
- Roteiro pronto ainda não gravado: 1 Crônicas 16:24 (lembrar, agradecer e contar) — `roteiro_maravilhas_fonte.txt`.
