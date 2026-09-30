---
name: canal-economia-faceless
description: Fluxo completo para criar um canal faceless de economia no YouTube e produzir vídeos longos — identidade do canal (nome, descrição, tags, handles), análise de padrões de um canal de referência, ideias originais, roteiro travado, blueprint visual (prompts de imagem e vídeo por cena), voz off e montagem. Use quando o usuário quiser montar um canal faceless de economia, gerar ideias/roteiro de vídeo de economia explicada, ou converter um roteiro em cenas com prompts de imagem/vídeo para Flow, ElevenLabs e CapCut.
---

# Canal Faceless de Economia — do zero ao vídeo

Baseado no método "Economics Explained → sistema replicável". O objetivo é estudar **o sistema** de um canal de referência (nicho, títulos, ganchos, ritmo, linguagem visual) e construir algo **100% original** em cima dos padrões transferíveis.

## Regras invioláveis

1. **Nunca copiar** nome, branding, logos, títulos exatos, thumbnails, roteiros, redação ou ideias distintivas do canal de referência. Extrair só princípios transferíveis.
2. **Tudo na mesma conversa**: cada etapa depende do contexto das anteriores (canal, nome, tópico, roteiro).
3. **Narração travada**: depois que o roteiro é aprovado, nenhuma etapa posterior o altera.
4. **Parar só nos pontos de decisão** indicados. Fora deles, executar a etapa inteira numa única resposta.
5. Idioma: responder no idioma do usuário; gerar os prompts de imagem/vídeo em inglês (funcionam melhor em Flow/ferramentas de IA), a menos que o usuário peça outro idioma. O roteiro segue o idioma do canal.

## Como conduzir

Identifique em qual etapa o usuário está (ele pode chegar no meio do fluxo) e continue dali. Se ele pedir "o fluxo todo", comece na Etapa 1. Os prompts-mestres completos estão em `references/prompts.md` — leia o arquivo da etapa correspondente antes de executá-la.

### Etapa 1 — Configuração do canal
Entrada: 1 screenshot da página de um canal de referência.
Saída (numa só resposta): análise do nicho + estilo visual → subnicho específico (economia global, economias de países, política econômica, tributação, desigualdade, mercados, sistemas financeiros, história econômica…) → **10 nomes originais**, descrição completa, **15 tags**, **3 opções de handle**.
**PARAR e perguntar somente:** qual número de nome.
Depois: entregar resumo único (nome, handle + variante, linha da descrição a atualizar, prompts de logo/banner).

### Etapa 2 — Roteiro
Entrada: títulos de alta performance + 2–3 transcrições do canal de referência, coladas junto.
Saída: análise de ganchos, ritmo, estrutura narrativa, padrões de seleção de tópico e de curiosidade (open loops) → **5 ideias ORIGINAIS** com resumo de uma linha.
**PARAR e perguntar:** (1) número da ideia; (2) duração — 8, 10 ou 12 minutos.
Depois: escrever o roteiro completo de narração e pedir revisão. Checklist para o usuário:
- as primeiras linhas criam motivo para continuar assistindo?
- o corpo tem progressão clara (não fatos soltos)?
- o final responde à promessa do gancho?
Ao aprovar, declarar o roteiro **TRAVADO**.

### Etapa 3 — Blueprint visual
Dividir o roteiro travado em cenas: nova cena a cada nova ideia, local, estatística, empresa, país, argumento ou virada emocional. Manter tudo **viável para iniciante**.
Por cena: número, trecho da narração, descrição visual, **prompt de imagem** (keyframe congelado: sujeito, ambiente, composição, ângulo, luz, estilo gráfico, informação visível), **prompt de vídeo** (só o movimento daquele mesmo keyframe: movimento do sujeito, câmera, ritmo, atmosfera), duração estimada, tipo **STATIC** ou **MOTION**.
Prioridade visual: cidades/distritos financeiros, prédios de governo, mapas, gráficos econômicos, documentos, imagens de empresas, manchetes, imagens financeiras, gráficos editoriais simples.
Depois: (a) gerar um **prompt de imagem de referência** (âncora de estilo); (b) extrair só os **prompts de imagem** num bloco numerado; (c) extrair só os **prompts de vídeo** com a mesma numeração e ordem, sem reescrever nem encurtar.

### Etapa 4 — Produção visual (Flow / Flow Agent)
Guiar o usuário: gerar 1 imagem de referência no Flow → baixar → abrir o Agent → arrastar a referência → colar o bloco numerado de prompts de imagem → pedir que gere todas as cenas mantendo o estilo. Corrigir **só a cena errada** com instrução precisa. Depois animar apenas as cenas marcadas MOTION com o bloco de prompts de vídeo; STATIC pode ser imagem, mapa, gráfico animado ou push-in lento.

### Etapa 5 — Voz off
Gerar a versão **limpa** da narração (sem marcações de cena/produção), pronta para TTS. Ajustar só a linha que o usuário apontar. Sugestão de voz no ElevenLabs: calma, clara, confiante, estilo documentário. Exportar MP3.

### Etapa 6 — Montagem (CapCut)
Voz off na timeline primeiro (espinha dorsal) → visuais por cima seguindo a ideia da fala (país → mapa/cidade; estatística → gráfico; empresa/política/imposto → manchete/imagem da empresa) → cortar excessos → abaixar áudio dos clipes → legendas automáticas com template simples e alto contraste → transições sutis (fade, dissolve) → trilha calma/documental/piano a ~20% → preview completo → exportar.

## Formato de resposta
- Cada etapa em uma única resposta, com cabeçalhos claros.
- Blocos numerados copiáveis (prompts de imagem / vídeo) em blocos de código, `Scene 01`, `Scene 02`…
- Ao terminar uma etapa, dizer explicitamente qual é o próximo passo.
