# Armadilhas conhecidas (e a correção)

Cada item custou pelo menos um render ou um ciclo de depuração. Consulte antes de
depurar.

| Sintoma | Causa | Correção |
|---|---|---|
| Arquivo de 100+ Mbps (2h ≈ 100 GB) | grão animado `noise=allf=t` com CRF baixo | sem grão ou grão leve + `-maxrate 8M -bufsize 16M` |
| Processo morto (SIGKILL) | ~20+ imagens 4K com `zoompan` num só filter_complex | renderizar clipe a clipe e emendar (função `chain`) |
| `xfade ... timebase do not match` | `blend`/overlay muda a base de tempo | `settb=1/24` em cada entrada antes do `xfade` |
| Áudio com 413 s em vez de 40 min | `asplit` + cadeia de `acrossfade` encerra cedo | cada repetição como `-i` separado |
| Buraco de silêncio no loop da música | mp3 termina com 10–15 s de silêncio | `silencedetect` e usar `end` antes do silêncio |
| Volume pulando na troca de música | mp3s com loudness diferentes | `loudnorm` por faixa antes do crossfade + no mix |
| Texto com vírgula/dois-pontos quebra o drawtext | escape do filtergraph | `textfile=` em vez de `text=` |
| Shell morre com exit 144 | `pkill -f nome` casa com o próprio comando | matar por PID ou `pkill -x ffmpeg` |
| Espera termina na hora | grep "error" casou com `-v error` no log | esperar por `^pronto|ERRO|Traceback` |
| Saída de 85 KB no contexto | `-stats` do ffmpeg no terminal | log em arquivo; `tail` |
| Envio do vídeo falha (502) | limite do chat entre 25 e 60 MB | prévia ≤ 25 MB; final via Git LFS |
| Tarja preta na imagem aparece no vídeo | imagem gerada com letterbox | `prep()` corta linhas/colunas escuras |
| Zoom "trava" na borda e dá tranco | alvo fora da área válida | |dx|,|dy| ≤ 0.11 com zoom 0.30 |
| f-string com aspas aninhadas falha (Python < 3.12) | `f"...{fn("x")}..."` | usar aspas simples por dentro |
