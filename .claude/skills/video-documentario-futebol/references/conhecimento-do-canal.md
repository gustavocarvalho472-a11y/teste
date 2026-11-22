# Conhecimento do canal (atualizado em nov/2026)

Resumo de tudo o que foi aprendido na primeira conversa de produção (vídeos do Manchester City e do Brasil). Leia junto com `SKILL.md` e `manual-de-roteiro.md`.

## O dono do canal
- Brasileiro, fala português; o canal é em inglês para alcançar público global.
- Acompanha pelo celular: mande roteiros, títulos, descrições e respostas no chat, prontos para copiar.
- Quer ver o roteiro em PT antes de qualquer gasto. Gosta de receber versões de validação em PT (voz `espeak-ng` + legenda PT queimada, sem gastar créditos).
- Dá feedback direto e visual (prints). Responda com mudanças concretas, não com perguntas.
- Narração: não tem ElevenLabs pago; normalmente usa Kokoro. No vidIQ, a voz usada foi "Daniel – Steady Broadcaster" (`onwK4e9ZLuTAKqWW03F9`), 28 créditos por 1.000 caracteres. Restavam cerca de 210 créditos no fim de nov/2026.

## Canais de referência
- @becir04 (principal), @SecondHalfFootball, AUGUZTO. A fórmula do Becir está em `manual-de-roteiro.md`.
- Thumbs no estilo Becir: dois rostos, fundo escuro, duas palavras nas laterais (ex.: "GLORY / RUIN", "TOO / LATE", "SAME / PERSON").

## Vídeos publicados
| Vídeo | Título publicado | Observações |
|---|---|---|
| Manchester City | "Man City's Secret Sponsorship Trick Finally Exposed" | thumb TOO/LATE; comentários acusando o City: responda sem dizer "fraude" (não provado) |
| Brasil / Vini Jr | "The decline of the Brazilian national team - Vinicius Jr" | thumb GLORY/RUIN, 11:19; primeira versão bloqueada pela FIFA |
| Outros no canal | "Why the Internet Is Calling Ronaldo the R...", "The Joke That Cost Mbappé Millions in C..." | feitos fora deste repositório |

## O vídeo do Brasil — ângulo e conceito (modelo de referência)
- **Ângulo:** "o 7x1 não foi o fundo do poço". Parte de algo que todo mundo sabe (7x1 = pior momento) e mostra que o que veio depois é pior, porque o torcedor parou de esperar.
- **Fio condutor:** uma pessoa (Vinícius Jr): melhor do mundo da FIFA em 2024 → vaiado no Bernabéu → meme do "sósia que substituiu o Vini que morreu na cirurgia". O meme vira metáfora do vídeo.
- **Quatro movimentos:** choque (7x1 + queda do Vini + meme) → provas no elenco atual (falas reais de Raphinha e Zico, 24 s de silêncio, pênalti do Bruno, ESPN) → virada (parece vaidade, mas o Ronaldo de 2002 tinha o pior cabelo e ganhou; o problema é a fama antes da taça e sair do Brasil aos 16) → fechamento em espelho (volta ao 7x1 e ao meme, pergunta sobre 2030).
- **Tom:** o narrador não ataca; as críticas vêm de quem tem autoridade (Zico, Ronaldinho, Romário, ESPN, o próprio capitão).
- Roteiro completo (EN + PT): `roteiros/brazil-7-1-wasnt-the-bottom.md` e `video-production/brazil/v3/`.

## Pedidos e correções que o dono fez (não repetir os erros)
- Primeira versão com Zlatan como autoridade não engajou: o ângulo precisa de emoção e conflito, não só de uma frase elogiosa.
- "A internet não decide nada": descreva memes como zoação ("tiram sarro dizendo que...").
- Abertura parada (um take longo ou número gigante na tela) foi rejeitada duas vezes: cortes de cerca de 1 s, misturando lances, fotos e reação.
- Mostrar sempre quem está sendo citado (foto ou lance), com gols e skills para craques antigos.
- Fotos animadas + vídeos: aprovado ("fotos + vídeos ficaram legais").
- Textos soltos em PT de canais brasileiros dentro dos takes: proibido.
- Áudio original em PT → legenda em EN.
- Tirou Lula da foto do Romário: evitar política.

## Checklist de publicação
1. Subir como não listado e esperar a verificação de direitos autorais; se houver reivindicação, trocar só os minutos apontados.
2. Enviar o `.srt` em inglês.
3. Descrição com resumo, pergunta para comentários, créditos das fotos (`assets/photos/CREDITS.md`), fontes das imagens e hashtags.
4. Tags com os nomes buscados (jogador, seleção, tema).
5. Responder os primeiros comentários com uma pergunta, dar coração e fixar um.

## Ideias aprovadas e ainda não feitas
- Pochettino / Manchester United: "Ferguson Chose Him 10 Years Ago".
- Para novos temas: checar o que está em alta nos canais de referência (vidiq_channel_videos, 5 créditos) e propor 3 a 5 ângulos com título e ideia de thumb.

## Ambiente
- Hosts liberados: assets.vidiq.com, ai-music-tracks.s3.us-east-1.amazonaws.com, videos.pexels.com, images.pexels.com, commons.wikimedia.org, upload.wikimedia.org.
- Download de vídeos do YouTube: `vidiq_video_upload` com a URL (grátis) → `vidiq_job_poll` → curl do link storage.googleapis.com.
- Busca no YouTube sem custo: Nexlev `youtube_search` e `get_video_transcript`.
- API do Commons tem limite: uma busca a cada ~25 s; troque `thumb.wikimedia.org` por `upload.wikimedia.org` nos links.
- Render completo passa de 30 min: rode em background e reaproveite segmentos com `--reuse`.
