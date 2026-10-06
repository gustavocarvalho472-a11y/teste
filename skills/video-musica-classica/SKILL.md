---
name: video-musica-classica
description: Produz vídeos longos (30 min a 3h) de música clássica para estudo/foco no estilo do canal "Classical Mind" — imagens de época iluminadas a vela com zoom lento e zoom in/out marcado, crossfades, poeira dourada, chuva, tom âmbar, vinheta, intro com clipes e frases sobre o Efeito Mozart, título em fonte serifada, música em loop com crossfade e sound design leve. Use sempre que o usuário pedir para montar, editar, renderizar ou atualizar um vídeo de música clássica, piano, Mozart, "música para estudar/focar/relaxar", "vídeo de 2h com essas imagens e esse mp3", trocar a música ou o tempo de um vídeo desse tipo, ou mencionar o Classical Mind — mesmo que não cite a skill. Também cobre prévia, entrega do arquivo grande e otimização de render.
---

# Vídeo de música clássica (estilo Classical Mind)

Transforma imagens + clipes curtos + mp3 num vídeo longo pronto para o YouTube,
com um script testado (`scripts/make_video.py`) controlado por um JSON. O trabalho
do Claude é montar a configuração certa, rodar, conferir e entregar — não
reescrever o pipeline. Reescrever custou centenas de linhas e vários ciclos de
erro no projeto que deu origem a esta skill.

## Fluxo

### 1. Uma rodada de perguntas, no início
Ambiguidade descoberta no meio do caminho custa um render inteiro. Pergunte de
uma vez só o que não estiver claro na mensagem:
- duração total; quais músicas, em que ordem e até que minuto cada uma toca;
- título/subtítulo e idioma das frases da intro (padrão: inglês, como o canal);
- quais imagens e clipes (aponte duplicatas — imagens idênticas desperdiçam o ciclo);
- seção dinâmica (zoom in/out marcado) — até que minuto (padrão: 5 min);
- forma de entrega (veja "Entrega").
Se o usuário já respondeu algo, não pergunte de novo. Se ele pedir para não gerar
nada ainda, só prepare a configuração.

### 2. Checagem rápida dos insumos (barata)
```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 arquivo
ffmpeg -i musica.mp3 -af silencedetect=n=-45dB:d=0.5 -f null - 2>&1 | grep silence_
```
Use os silêncios do mp3 para preencher `start`/`end` (muitos mp3 terminam com
10–15 s de silêncio, que viraria um buraco no loop). Não abra os clipes quadro a
quadro: um mosaico (`tile=3x1` de 3 quadros) por clipe basta.

### 3. Configuração
Copie `scripts/config.example.json` para a pasta do projeto e edite. Campos:
- `scenes[]`: `image`, `motion` (`zoom_in` | `zoom_out` | `pan`), `target`
  [dx, dy] = deslocamento do foco a partir do centro (manter |dx|,|dy| ≤ 0.11
  com zoom 0.30, senão o enquadramento trava na borda), `rain` (true só em cena
  com chuva visível).
- `dynamic`: seção de zoom marcado após a intro (`until_min`, `slot` ~12 s,
  `fade` 2 s, `zoom` 0.30). Remova o bloco para não ter seção dinâmica.
- `cycle`: ciclo calmo repetido até o fim (`slot` 60 s, `fade` 3 s, `zoom` 0.14).
- `audio[]`: em ordem; `until_min` diz até quando cada faixa toca; cada faixa
  repete em loop com crossfade e é normalizada à parte (volumes de mp3
  diferentes chegam a 5 dB de diferença).
- `intro`: clipes + legendas `[início, fim, texto]`. Para frases sobre o Efeito
  Mozart, mantenha-as factuais (estudo de 1993, efeito temporário).

### 4. Prévia antes do vídeo completo
```bash
python3 scripts/make_video.py config.json --preview > build_log.txt 2>&1; tail -8 build_log.txt
```
Gera 2 min em 720p (<25 MB, cabe no envio do chat) e já deixa em cache o ciclo e
os clipes — o render completo depois reaproveita tudo. Envie a prévia e espere o
OK quando o usuário quiser revisar; se ele pediu para "gerar direto", siga.

### 5. Render completo
```bash
python3 scripts/make_video.py config.json > build_log.txt 2>&1; tail -8 build_log.txt
```
Rode em segundo plano e espere com **uma** condição que cubra sucesso e erro
(`until grep -qE "^pronto|ERRO|Traceback" build_log.txt; do sleep 10; done`).
Não use padrões que casem com o próprio comando (ex.: "error" casa com `-v error`).
Tempos de referência (4 CPUs): 40 min de vídeo ≈ 20–25 min de render; mudar só
título ou música ≈ 2–3 min, graças ao cache.

### 6. Conferência
O script imprime durações, silêncios e loudness e grava `build/qa.jpg` (mosaico
com 9 momentos: intro, título, seção dinâmica, emenda das 5:00, emenda do loop,
final). Leia **só** esse mosaico — uma imagem substitui uma dúzia de leituras.
Critérios: vídeo e áudio com a mesma duração; nenhum silêncio > 1 s; loudness
entre -15 e -13 LUFS; título legível; quadros da emenda do loop parecidos.

### 7. Entrega
- Prévias e trechos de até ~25 MB: envie pelo chat (arquivos de 60 MB+ falharam).
- Vídeo final: Git LFS numa branch separada, só com o vídeo. Veja
  `references/entrega.md` — tem os comandos e os avisos (cota de 1 GB/mês do
  LFS gratuito e se o repositório é público).

### 8. Aprendizados (sempre, ao final)
Feche cada vídeo com um bloco curto para o usuário:
```
Lições deste vídeo:
- o que deu errado ou custou caro (tempo, tokens, re-render)
- o que o usuário corrigiu ou pediu diferente
Ajuste sugerido na skill: <uma ou duas mudanças concretas>
```
Se o usuário aprovar, registre em `references/aprendizados.md` (no repositório
dele, se a skill estiver versionada lá) e ofereça reempacotar a skill. Antes de
começar um vídeo novo, leia `references/aprendizados.md` — é onde ficam as
preferências já descobertas.

## Economia de tokens (o que mais pesou na origem desta skill)
- Não reassista o canal de referência: o estilo está em `references/estilo.md`.
- Não reescreva o pipeline; edite o JSON. Se precisar de um efeito novo,
  acrescente uma função pequena ao script e registre em aprendizados.
- Saída do ffmpeg nunca no contexto: o script já manda para `build/ffmpeg.log`;
  ao chamar, redirecione para arquivo e use `tail`.
- Antes de depurar um erro, consulte `references/armadilhas.md` — os erros que
  já aconteceram estão lá com a correção.
- Efeitos: prefira os da lista "leves" em `references/estilo.md`. Grão de filme
  animado multiplica o arquivo por ~10; muitas imagens num único filtro estoura
  a memória (por isso o script renderiza clipe a clipe).
- Prévia curta antes do completo; nunca renderize o completo para testar.
- Um único mosaico de QA em vez de vários frames.

## Arquivos
- `scripts/make_video.py` — pipeline completo (cache, log, QA embutidos).
- `scripts/config.example.json` — configuração do vídeo de referência (40 min).
- `references/estilo.md` — especificação do estilo e menu de efeitos por custo.
- `references/armadilhas.md` — erros conhecidos e correções.
- `references/entrega.md` — entrega via chat e Git LFS.
- `references/aprendizados.md` — preferências e lições acumuladas.
- `assets/Cinzel.ttf` — fonte do título (licença OFL).

Requisitos: `ffmpeg` com libx264, Python 3 com `numpy` e `pillow`
(`pip install numpy pillow`), fonte Liberation Serif para as legendas.
