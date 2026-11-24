# Canal de futebol no YouTube — contexto obrigatório

Este repositório produz vídeos-documentário de futebol para um canal do YouTube em inglês. Antes de qualquer tarefa de vídeo, leia:

1. `.claude/skills/video-documentario-futebol/SKILL.md` (pipeline completo e a seção "Lições do vídeo do Brasil")
2. `.claude/skills/video-documentario-futebol/references/manual-de-roteiro.md` (ângulo e estrutura no formato Becir)
3. `.claude/skills/video-documentario-futebol/references/conhecimento-do-canal.md` (histórico, preferências, vídeos publicados, checklist de publicação)
4. `.claude/skills/video-documentario-futebol/references/estilo-v2-cinema-revista.md` (**estilo visual padrão desde nov/2026**: Cinema + Revista, câmera no rosto, fotos animadas, pouco texto)

## Regras que o dono do canal já definiu
- Fale com ele sempre em português. O vídeo final é sempre em inglês.
- Ele acompanha pelo celular e não abre arquivos: roteiro, títulos e textos para colar vão no chat.
- Roteiro em PT no chat para validação ANTES de gerar narração. Narração corrida (frases que puxam a próxima), nunca frases curtas e truncadas.
- Autoridade do ângulo tem de ser um nome global; ídolo local entra como complemento.
- Nenhum vídeo da FIFA (Copas, FIFA TV/FIFA+, The Best) nem imagens de transmissão da Premier League/UEFA: os vídeos do Brasil e do Ferguson foram bloqueados por isso.
- Fotos: o dono liberou qualquer imagem (Pinterest/Google), não precisa ser livre. O Pinterest funciona neste ambiente; o Commons dá 429. Priorize foto em alta resolução, quase parada, em vez de take ruim; nunca repita take.
- Abertura muito dinâmica; CTA logo depois da introdução.
- Créditos vidIQ são limitados: avise antes de gastar.
- Identidade visual: verde-limão (#C6FF00) e preto, no estilo v2/v3 "Cinema + Revista": imagem em tela cheia sem moldura, zoom lento e liso (subpixel + easing) no rosto dos personagens, fotos com elemento editorial (dupla/trio lado a lado, foto impressa, recorte), serifa + mono, pouco letreiro. A moldura e o motion estilo TV da v1 foram recusados; movimento tremido também.

## Git
Branch de trabalho: `claude/video-script-english-38w7l3`. MP4 e mídia pesada não vão para o git (entregue pelo chat).
