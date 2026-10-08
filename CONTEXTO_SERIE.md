# Série "Curiosidades Bíblicas": contexto para continuar

Documento de passagem entre conversas. Branch: `reel-particulas`.

## Objetivo
Criar conteúdo de **curiosidades bíblicas** com identidade visual própria:
- **Shorts e Reels** (9:16, 25–60s) para YouTube, Instagram e TikTok.
- Depois, **vídeos longos de 5 a 8 minutos** (16:9), divididos em capítulos que viram shorts.

## Identidade visual (decidida)
- **Cores:** preto e branco, sem cor de destaque.
- **Visual:** ilustrações em estilo gravura do Gustave Doré, convertidas em partículas de meio-tom com profundidade 3D (inspirado num reel de partículas sobre Michael Jordan).
- **Cabeçalho:** "CURIOSIDADES BÍBLICAS — <PERSONAGEM>" à esquerda e a referência bíblica (ex.: "1 SM 17:4") à direita, com uma linha fina embaixo.
- **Rodapé:** régua de progresso.
- **Anotações com linha:** apontam detalhes da imagem com texto digitado (ex.: "GOLIAS · 2,9 M").
- **Legenda:** fonte Inter SemiBold, branca. Hoje fica embaixo; a ideia é testar no centro, em blocos de 2 a 4 palavras.
- **Transição-assinatura:** a imagem aparece nítida e "viva", uma linha de luz a converte em partículas, os pontos ganham 3D e a câmera gira. Depois os pontos voam e formam a próxima cena ou um gráfico (número, coroa, barras…).
- **Efeitos "vivos":** estrelas cintilando, luz passando pelo céu, relâmpago com trovão, raios de luz, poeira desfocada flutuando, câmera sempre em movimento e pontos que "respiram".

## Imagens
- O usuário gera as imagens por IA a partir dos prompts que eu escrevo.
- **Estilo base,** colado no fim de todo prompt: `19th-century wood engraving in the style of Gustave Doré, black and white, fine cross-hatching, dramatic chiaroscuro, strong rim light, subject isolated against a deep black background, cinematic composition, 16:9, no text, no frame`
- **Personagens fixos:**
  - Davi jovem: `a teenage shepherd boy, slim, curly dark hair, simple wool tunic, leather sling, barefoot`
  - Golias: `a towering Philistine warrior, bronze scale armor, crested helmet, massive spear, round shield`
- **Imagens do Davi que já temos,** em `motor/img/davi/`: `01_davi`, `02_golias`, `03_confronto`, `04_pedra`, `05_pasto` e `06_leao` (2576×1438).
- **Gravura real de Doré** em domínio público: `motor/img/dore_goliath.jpg` (créditos em `motor/img/CREDITOS.md`).

## Código
- **`motor/particulas.py`:** o motor.
  - `cloud_from_array` transforma imagem ou máscara em pontos 3D de meio-tom (opções `autolevel`, `lumdepth` e `feather`; devolve as coordenadas UV para os efeitos).
  - `resample` fixa o número de pontos para transformar uma cena em outra.
  - `project` cuida da câmera (yaw, pitch, dolly, pan).
  - `render` desenha os pontos com retícula, profundidade de campo e brilho; `finish` aplica granulação e vinheta.
  - Velocidade: cerca de 0,3 a 0,6s por quadro com 4 processos.
- **`motor/formas.py`:** formas gráficas (harpa, coroa, rei, número, telas, coração, barras).
- **`motor/teste_revelar.py`:** teste da transição imagem nítida → partículas → poeira (resultado: `teste_imagem_vira_particulas.mp4`).
- **`davi_v2/render_v2.py`:** o short do Davi de 57s com as imagens do usuário, e o modelo mais completo até agora.
  - A lista `KEYS` define as cenas (nuvem, câmera inicial e final, efeitos).
  - `CALLS` define as anotações, `LBL` os rótulos e `SPLIT` as legendas.
  - Também gera o áudio sintetizado. Prévia: `python3 render_v2.py prev 1.2 5 9`.
- **`davi/narrar.py`:** gera a narração com o Kokoro (voz `pm_alex`) e grava `davi/narr/timing.json`. A linha do tempo do vídeo segue a duração das falas.
- **Para preparar o ambiente numa sessão nova:** `pip install kokoro-onnx soundfile scipy faster-whisper`, depois baixar `kokoro-v1.0.onnx` e `voices-v1.0.bin` para `~/tts` (está em `scripts/setup.sh` da skill video-ilustracao). Para conferir a pronúncia, transcrever com o faster-whisper `small`, passando o áudio como array em 16 kHz.
- **Envio de arquivos:** o upload para o usuário aceita no máximo 30 MB, então o vídeo é codificado em cerca de 3,8 Mbps (cerca de 26 MB para 57s).

## Vídeos já feitos
- `reel_particulas_5s.mp4`: primeiro teste.
- `reel_davi.mp4`: Davi 57s, só com gráficos de partículas.
- `reel_davi_v2.mp4`: Davi 57s com as imagens do usuário. **Pontos fracos:** a cena do pasto está escura, a anotação "ONDE NINGUÉM VIA" está desalinhada e a cena da pedra é curta.
- `teste_motor_v2.mp4` e `teste_imagem_vira_particulas.mp4`: testes do motor.

## O que aprendemos com as referências
1. **Reel do Jordan (partículas):** gancho com nome famoso e número → ideia → aplicação → frase de fechamento. Preto e branco, morph de partículas, voz calma.
2. **Reels devocionais virais** ("Deus falou com o mar", "Paulo – Fp 4:13"):
   - 22 a 39 segundos, uma ideia só.
   - Gancho em **pergunta**.
   - **Regra de três** ou pares de opostos.
   - Termina num **versículo**, sem chamada para ação.
   - Cortes a cada 1,5 a 2 segundos.
   - Voz grave e calma, piano ou lo-fi.
   - Legenda no centro.
3. **Isaac, "Blew Up a Shorts Channel in 7 Days":**
   - O nicho que viraliza é "coisa estranha que parece sem sentido até alguém explicar → genial".
   - O gancho de **role-play** ("Você é X e tem um problema…") com a revelação no fim ("era a Nescafé").
   - Copiar a **estrutura** de um viral, não o conteúdo.
   - O visual decide: ele animou as imagens com IA de vídeo.
   - Métricas de referência: **taxa de permanência acima de 80%** e **retenção acima de 90%**.
   - O tema não pode ser deprimente e o vídeo precisa de recompensa no final.

## Minha avaliação crítica (combinada com o usuário)
- **Aplicar sem medo:** gancho em pergunta ou role-play, vídeos mais curtos, final com versículo, regra de três.
- **Maior risco: a VOZ.** O Alex (Kokoro) tem sotaque. Recomendo gravar a narração ou usar a ElevenLabs.
- **Cortes rápidos brigam com as partículas:** usar imagens nítidas com cortes de 2 a 3 segundos e partículas só em 1 ou 2 viradas por vídeo.
- **Formato proposto:** fato curioso no início → lição + versículo no fim. É uma hipótese, e deve ser testada com dados.

## Próximos passos
1. **Short do Gideão (Jz 7), em role-play,** como piloto do formato novo:
   > Você é um general… 32 mil homens… "é gente demais"… 22 mil vão embora, sobram 10 mil… o teste da água, sobram 300… trombetas, jarros e tochas… o inimigo luta entre si… "Esse general era Gideão." Fecha com Jz 7:2.
   - Fontes: Jz 7:3–4, 7:6, 7:16–22 e 8:10 (mais de 100 mil inimigos).
2. **Alternativa: short da regra dos cantos do campo** (Lv 19:9–10 → Rute colhendo as sobras no campo de Boaz → bisneto: Davi, Rt 4:17).
3. **Para cada um:**
   - Eu faço o storyboard com os prompts de imagem e marco quais cenas valem animar por IA (Kling, Runway ou Veo; quem gera é o usuário).
   - Gero a narração.
   - Monto o vídeo no motor. O motor ainda não converte clipe de vídeo em partículas: essa função precisa ser criada.
4. **Sprint de 7 dias:** 1 short por dia nas 3 plataformas, olhando taxa de permanência e retenção antes de fazer o próximo.
5. **Vídeo longo do Davi (5 min):** o roteiro em 7 capítulos já está escrito na conversa anterior (cerca de 700 palavras). Faltam 8 imagens: Samuel e os filhos de Jessé, Eliabe, a unção, a harpa diante de Saul, o exército com medo, Davi levando pão e queijo, a armadura de Saul e as 5 pedras no riacho.
6. **Criar uma skill** que faça o processo inteiro a partir de um tema.

## Preferências do usuário
- Conversa em português.
- Quer ver testes curtos antes do render completo.
- Gosta de análise crítica honesta.
- Os fatos bíblicos sempre com a referência, e interpretações marcadas como interpretação.
