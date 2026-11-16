# Manual de roteiro e de ângulo (v1 — baseado no estudo do Becir, Second Half Football e AUGUZTO)

Estudo feito em nov/2026: 38 vídeos longos do Becir e 50 do Second Half (títulos, views, breakout score) e a transcrição completa de 4 acertos do Becir ("Mourinho Was Right All Along" 1,9 mi; "Van Dijk Is What Maldini Warned Us About" 1,6 mi; "Amorim Tried to Warn Us" 431 mil; "Kobe Was Right About Neymar" 182 mil). AUGUZTO: só títulos e thumbs (vídeos de 17–60 min).

## 1. O ângulo (é aqui que o vídeo ganha ou perde)

O Becir quase nunca conta a notícia. Ele pega **uma frase antiga de alguém famoso** e mostra que **um fato de agora deu razão a ela**. O espectador já conhece os dois nomes; a novidade é a ligação entre eles.

Fórmula: **[AUTORIDADE] + [frase ou atitude antiga] + [FATO NOVO que a confirma ou inverte]**

Teste do ângulo — só aprove se responder "sim" às quatro:
1. **Dois nomes grandes?** A autoridade (Mourinho, Ronaldo, Maldini, Zlatan, Guardiola, Messi, Ferguson) e o assunto do momento. Nome médio derruba o vídeo: Chicharito 17 mil, Sesko 21 mil, Musiala 35 mil, contra 400 mil–1,9 mi quando os dois nomes são gigantes.
2. **Existe a fala gravada?** Sem o clipe da frase original não há abertura. Ache o vídeo da fala antes de escrever.
3. **Tem gancho de agora?** O vídeo do Mourinho saiu 5 dias depois do veredito do City; o do Amorim, na semana da crise do United. A frase é velha, o motivo para clicar é desta semana.
4. **O título esconde a resposta?** "Kane Never Forgot Him", "Ronaldo Wanted Him 5 Years Ago": quem é "ele"? A pessoa clica para saber.

Famílias de título que funcionaram (com o melhor resultado de cada uma):
| Família | Exemplo | Melhor resultado |
|---|---|---|
| X Was Right (All Along / But Nobody Listened) | Mourinho Was Right All Along | 1,9 mi |
| Y Is What X Warned Us About | Van Dijk Is What Maldini Warned Us About | 1,6 mi |
| X Warned Us About Y | Zlatan Warned Us About Mbappe | 704 mil |
| X Wanted Him / Never Forgot Him (o "ele" oculto) | Ronaldo Wanted Him 5 Years Ago | 682 mil |
| Why X Never / Always [dado estranho] | Why Donnarumma Never Dives First | 605 mil |
| X Never Talks. Until He Saw Y. | Messi Never Talks. Until He Saw Nico Paz. | 567 mil |
| Cruzar esportes | Kobe Was Right About Neymar | 182 mil |
| How To Destroy / Save A Club ft. | How To Destroy A Club ft. Tottenham | 267 mil |

O Second Half copia as mesmas famílias em vídeos de 12–15 min e posta quase todo dia; os picos dele são "X Has Become Exactly What Y Was Scared Of" e "X Was Right About Y… Nobody Listened". O AUGUZTO (PT-BR) usa outro caminho: um jogador só, uma palavra na thumb (GOAT, CULPADO, MENTIRA, VINGANÇA) e uma tese contra o senso comum ("O Problema Nunca Foi o Neymar", "Romário Seria Proibido Hoje").

Onde procurar ângulo novo: a mesma notícia vista por (a) quem avisou antes, (b) quem perdeu por causa dela, (c) quem prometeu algo que agora cobra, (d) um ídolo de outro esporte, (e) o personagem invisível (hacker, auditor, diretor).

## 2. Estrutura do roteiro (formato Becir, 8 minutos)

Todos os acertos têm **8:00–8:10** (cerca de 1.250–1.350 palavras de narração + falas).

| Trecho | Tempo | O que acontece |
|---|---|---|
| Fala fria | 0:00–0:10 | Clipe real da frase antiga, sem introdução |
| Paradoxo | 0:10–0:30 | Narrador: "Por X anos, [autoridade] disse/fez Y e quase ninguém entendeu por quê." |
| Fato novo | 0:30–0:50 | Data exata + o que aconteceu agora + segunda fala curta |
| Volta no tempo | 0:50–3:30 | Cronologia: cada parágrafo começa com data ou jogo e termina numa fala real |
| Virada | ~4:00–5:00 | Algo parece desmentir a tese ("That moment did not last." / "If that's true, he wasn't the victim. He was the problem.") |
| Segunda virada | 5:00–7:00 | Novo fato devolve a razão à autoridade; o outro lado também fala |
| Fecho | 7:30–8:00 | Repete a frase da abertura com sentido novo + pergunta aberta. Sem "inscreva-se". |

Regras de texto observadas:
- **Uma fala real a cada 20–30 s.** O narrador liga as falas; quem opina são os personagens.
- **Presente do indicativo** ("In August 2018, United lose 3–0…"). Datas, placares e números exatos.
- **Narrador não julga.** Nada de "absurdo", "vergonha". A ironia vem da ordem dos fatos.
- **Gancho no fim de cada bloco**: "But…", "Then he says the line the media will dig up years later."
- **Frase-espelho**: a primeira e a última frase dizem quase a mesma coisa.
- O outro lado sempre aparece (Guardiola responde, City nega). Isso também protege juridicamente.
- Nenhuma introdução do canal, nenhum resumo do que vem.

## 3. Como achar o tema da semana (processo)

1. `vidiq_channel_videos` (5 créditos) nos canais de referência, lista recente: anote o que tem `vph` alto ou `breakoutScore` ≥ 3 nos últimos 15 dias. Isso mostra o assunto quente.
2. Para cada assunto quente, liste 5 autoridades que já falaram dele no passado. Busque a fala (`vidiq_youtube_search`, vídeos curtos) e confirme com `vidiq_video_transcript`.
3. Passe cada par (autoridade + fato) no teste das quatro perguntas.
4. Escreva o título em uma das famílias da tabela e as duas palavras da thumb.
5. Só então escreva o roteiro, já em beats, com a fala real que fecha cada bloco.

## 4. Adaptação ao pipeline desta skill

- Vídeo de 8 min neste formato tem ~15–20 falas reais: use cenas `caps` (áudio original + palavra marcada) intercaladas com a narração, não só na abertura.
- Menos gráficos de dados e mais `lower`/`stat` sobre o take. Reserve `counter`, `bars` e `article` para 3–5 momentos.
- Thumb: dois rostos (o de trás apagado), fundo escuro, duas palavras nas laterais.
