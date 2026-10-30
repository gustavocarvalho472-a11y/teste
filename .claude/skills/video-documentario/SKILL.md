---
name: video-documentario
description: Monta vídeos documentais de YouTube a partir de um handoff (roteiro decupado + lista de assets), no formato "polêmica/notícia" com prints de tweets, memes, fotos e imagens IA, narração, trilha, SFX e legendas karaokê. O vídeo publicado é em INGLÊS; o português sai só como áudio para validar. Use quando o usuário mandar um handoff/roteiro de vídeo desse tipo, pedir storyboard, caça de assets, prompts de imagem para o Flow ou o render do vídeo, mesmo sem citar a skill.
---

# /video-documentario

O motor está em `mbappe-china/` (primeiro vídeo feito assim). Para um vídeo novo, copie a pasta, troque
`roteiro.py`/`roteiro_en.py` e `assets/`, e reaproveite o resto. `mbappe-china/README.md` descreve cada script.

## Regras do usuário (não negociáveis)

1. **Idioma:** o vídeo final é em **inglês**, com narração, legendas e todo texto na tela em inglês.
   O **português é só áudio**, para o usuário validar o conteúdo (`saida/validacao_pt.mp3`). Nunca renderize
   vídeo em PT, a não ser que ele peça.
2. **Nada de PDF.** Storyboard, checklists e revisões visuais saem como **Artifact** publicado na conversa
   (`storyboard.py` → `saida/storyboard/index.html`, publicado com os quadros em `files`). Republique no
   mesmo link a cada atualização.
3. **Imagens IA:** quem gera é o usuário, no **Google Flow**. Entregue **um único bloco** para colar de uma
   vez: o estilo comum no topo e todas as imagens embaixo, cada uma com seu código (`IA_01 — …`). Nunca
   gere imagem por conta própria nem ofereça ferramentas pagas (ex.: Figma) sem ele pedir.
4. **Caça de assets:** o usuário pesquisa e manda **links** (`ID url`, um por linha). Entregue a lista do que
   falta como Artifact de checklist, com link de busca pronto (X com `filter:images`, Google Imagens) e o
   termo para copiar. Depois, baixe tudo você mesmo.
5. Não aceite fato duvidoso calado: se um tweet ou fonte contradiz o roteiro, aponte e proponha a troca.

## Fluxo

1. **Roteiro**: blocos em `roteiro.py` (PT, base) e overrides em `roteiro_en.py` (`EN[id]` com fala/txt/hl/ato,
   `PRON_EN` para nomes, `FALL_WORD`). Adapte o inglês, não traduza literalmente.
2. **Storyboard** (Artifact) antes de buscar assets: `VIDEO_LANG=en python3 storyboard.py`.
3. **Assets**:
   - links do usuário em `assets/links.txt` → `python3 baixar_links.py`
     - post do X: mídia via `cdn.syndication.twimg.com/tweet-result` (endpoint de embed);
       `PRT_*` vira print do embed oficial (`platform.twitter.com/embed/Tweet.html?id=`);
     - URL direta: baixa; SVG renderizado pelo Chromium.
   - provisórios: `capturar_prints.py` (manchetes públicas) quando ainda não houver tweet.
   - **Wikimedia:** o download do arquivo original (`upload.wikimedia.org/.../arquivo.jpg`) dá 429 a partir
     do IP do container, mas a miniatura padrão de 1280 px passa. `baixar_links.py` já converte o link
     sozinho (`wikimedia_thumb`). Não use mirrors do X (nitter etc.).
   - Confira tudo numa grade antes de encaixar: link errado acontece (ex.: post sem a imagem descrita).
4. **Produção**: `bash mbappe-china/produzir.sh pt` (áudio de validação) e
   `nohup bash mbappe-china/produzir.sh en > produzir.log 2>&1 &` (vídeo; ~20 min, sempre em segundo plano).
   Narração final do usuário: `audio/narracao_en.mp3` (e `narracao_pt.mp3` se houver); o Whisper alinha.
   Sem ela, usa Kokoro (`am_michael` EN, `pm_alex` PT) como provisória.
5. **Entrega**: prévia 720p < 30 MB com `SendUserFile`, `legendas_en.srt`, `capitulos_en.txt`.
   Commit e push só dos scripts (`assets/`, `audio/`, `build/`, `saida/` ficam fora do git).

## Lições técnicas

- Imagem quadrada/vertical (meme, foto de celular, vídeo de repost): inteira sobre fundo desfocado, nunca
  cortada por zoom. Print de tweet alto usa a altura da tela.
- Imagens do Flow já vêm no tom do vídeo: não aplicar gradação de cor por cima.
- Grão de filme em todo quadro estoura o bitrate (2 GB). Só em FOTO/IA, com poucas texturas reaproveitadas.
- Texto com ideograma chinês precisa de fonte CJK (`wqy-zenhei`); Anton não tem os glifos.
- `np.convolve` com janela longa em 20 M amostras trava: use média móvel por soma acumulada.
