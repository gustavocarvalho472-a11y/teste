# Publicação: kit "só pegar e postar"

Tudo vai para `video-jesus/postar/`:
- os vídeos (`<saida>.mp4`, `short_<saida>.mp4`);
- as thumbs PNG;
- as `.srt`;
- `LEIA_E_POSTE.md` (use o kit de "Tempo de Tela" como modelo; ele já está nessa pasta);
- `publicar.json` (manifesto para a API).

## Textos: um bloco de código por item (o usuário copia direto)
Para **cada vídeo** (longo PT, Short PT, longo EN, Short EN):
- **Título:** 1 principal + 2 alternativas. Até ~60 caracteres visíveis, com curiosidade e dor.
- **Descrição:**
  1. As 2 primeiras linhas são o gancho. Em EN, comece com "✝️ A Christian message about …" para sinalizar a fé.
  2. Resumo e versículo central por extenso.
  3. O 🔥 desafio.
  4. **Capítulos** `00:00 …`, tirados de `STARTS` com `VIDEO_NARRATION` ativo.
  5. 📖 lista de versículos.
  6. Linha de apoio emocional em tema sensível: CVV 188 / cvv.org.br em PT; 988 nos EUA.
  7. Inscreva-se.
  8. 3–5 hashtags.
- **Tags:** uma linha separada por vírgulas, com até 500 caracteres. Misture a dor ("ansiedade"), a solução ("jesus", "fé") e a passagem ("joão 4").
- **Comentário fixado:** o desafio + a palavra para comentar.
- **Short:**
  - **Título:** com `#shorts` (+ ✝️ em EN).
  - **Descrição:** 2 linhas + "O desafio está no vídeo completo 👆" + hashtags.

Lembre o usuário do que só se faz no app:
- fixar o comentário;
- no Short, escolher o vídeo longo em **"Vídeo relacionado"**;
- thumb personalizada exige o canal verificado por telefone.

## Thumbnail
- **Gerada aqui:** em `video-jesus/thumb.py`, crie uma função `_art_<nome>(c)` que desenha a cena mais
  forte, com a figura à direita, e chame `make_thumb(arte, kicker, linha1, linha2, selo, saída)`.
  O texto fica à esquerda em Montserrat; o selo é o versículo. O título deve ter 2–4 palavras e terminar
  em pergunta ou tensão. Exemplos: "PRESO NA TELA?" / "HOOKED ON YOUR PHONE?".
- **Prompt para ChatGPT** (entregue sempre, em PT e EN): siga esta estrutura.
  ```
  Crie uma thumbnail de YouTube 16:9 (1280x720) no estilo das animações do BibleProject: ilustração vetorial
  flat, formas geométricas simples, figuras sem rosto, textura sutil de papel e paleta limitada.
  CENA (lado direito, ~55%): <metáfora visual central do vídeo, com cores e luz>. <um feixe de luz dourada = esperança>.
  FUNDO: <ambiente em 2–3 cores>.
  TEXTO (lado esquerdo, ~45%, área escura limpa): linha pequena verde-água (#5fe0cf) "<kicker>";
  título grande branco, sans-serif extra bold (tipo Montserrat ExtraBold), 2 linhas "<L1>" / "<L2>";
  barra dourada (#ffd25a); selo em pílula dourada "<Livro x:y>".
  ESTILO: alto contraste, minimalista, cinematográfico, legível no celular. Sem outros textos, logotipos ou marca d'água.
  ```
  Dê também uma variação para teste A/B, com outra metáfora e outro título.

## Legendas .srt
O `produzir.sh` já gera os arquivos. Para gerar à mão: `VIDEO_LANG=pt VIDEO_NARRATION=<nome> python3 srt.py <nome> postar/legendas_x.srt [t0:t1]`.

No YouTube: Legendas → Adicionar idioma → Enviar arquivo → Com sincronização.

## Publicar pela API (opcional)
`video-jesus/youtube_upload.py` lê o `postar/publicar.json` (siga o formato do de "Tempo de Tela").

- **Credenciais:** `YT_CLIENT_ID`, `YT_CLIENT_SECRET` e `YT_REFRESH_TOKEN` no ambiente, com os escopos `youtube.upload` + `youtube.force-ssl`.
  - O token vale para um canal só.
  - Nunca peça para colar a credencial no chat; ela vai nas variáveis do ambiente.
- **Testar sem enviar:** `python3 youtube_upload.py postar/publicar.json --dry-run`.
- **Envio:**
  - Por padrão, os vídeos sobem **privados**.
  - `--agendar 2026-10-10T21:00:00-03:00` agenda os longos para esse horário e os Shorts para 3 h depois.
  - `--publico` publica na hora.
- No Short, use `{link:pt_longo}` na descrição: o link é preenchido depois que o longo sobe.
