# Edit & Capture Plan: "Manchester City's 115 Charges" (EN)

**Base:** `manchester-city-115-charges-EN.md` (roteiro em inglês)
**Referência de edição:** PELEJA, "Os 115 crimes do Manchester City finalmente explicados" (analisada cena a cena)
**Duração-alvo:** 11:00 · 16:9 · 4K timeline (entrega em 4K/1080p) · 25 fps
**Estilo:** o mesmo ritmo e a mesma estrutura do vídeo de referência, com acabamento de **grande emissora de TV**, como a unidade investigativa de um canal esportivo: vinheta de abertura, bumpers de capítulo, lower thirds animados, "data wall" de estúdio virtual, número em 3D sobre o gramado e áudio mixado como em um telejornal.

---

## 0. O que o vídeo de referência faz (e o que mantemos)

| Elemento da referência | Como fica na nossa versão |
|---|---|
| Sem apresentador; narração em off o tempo todo | **Mantido.** Opcional: 3 inserções de âncora em estúdio virtual (ver §6) |
| Paleta preto + branco + **amarelo canário** | Trocar o amarelo por **âmbar/ouro de emissora** (#F5B700) e somar um azul-escuro de estúdio (#0B1630). Assim o vídeo não fica com a cara do PELEJA |
| Cartelas de capítulo pretas com fio amarelo horizontal | Bumpers de capítulo de TV: 3 s, com fundo de estúdio 3D, fio de luz, título em sans condensada e "stinger" sonoro |
| Prints de matéria com marca-texto amarelo animado | Mantido: "highlight sweep" âmbar, com zoom lento + clique de mouse |
| Valores em 3D rastreados sobre o gramado (£67,5M / £59,5M) | Mantido e ampliado: é a "assinatura" do vídeo |
| Recortes de fotos com borda grunge | Trocar por **cutouts de estúdio**: foto recortada + glow de recorte + fundo de painel LED |
| Moldura amarela para a entrevista remota (Joe, Guardian) | "Remote link" no padrão de TV: moldura com tag LIVE/REMOTE, nome, cargo e logo do veículo em texto |
| Bug fixo no canto superior direito | Bug do **seu** canal (não usar o logo PELEJA) |
| Cortes de 1,5–3 s nas montagens e de 4–7 s em documentos e entrevistas | Mantido |
| Corredor de tribunal, algemas, flashes | Mantido, com flash branco de 2 frames + SFX de câmera |
| Tela final preta com créditos e redes | End screen de emissora: créditos à esquerda, 2 vídeos sugeridos à direita |

---

## 1. Pacote gráfico "TV studio" (montar ANTES de editar)

Crie tudo uma vez em After Effects / Premiere MOGRT (ou DaVinci Fusion) e reutilize ao longo do vídeo.

| ID | Peça | Especificação |
|---|---|---|
| G01 | **Vinheta de abertura (sting)** | 4 s. Câmera 3D voando por um estúdio escuro, telões LED com recortes de documentos, fio âmbar que vira o título **THE 115 CHARGES**. Tipo: Druk Wide / Bebas Neue Pro / Tungsten (condensada), branco. Subtítulo em Inter/Helvetica Now |
| G02 | **Bumper de capítulo** | 3 s. Fundo de estúdio virtual desfocado, número do capítulo grande (01–07) em contorno, título em branco com fio âmbar entrando da esquerda. SFX: whoosh + hit grave |
| G03 | **Lower third: nome** | Barra azul-escura + aba âmbar, nome em CAPS e cargo em minúsculas. Entrada com wipe de 8 frames e saída de 6 frames. Duração na tela: 4 s |
| G04 | **Lower third: fonte / arquivo** | Tag pequena no canto inferior esquerdo, ex.: `ARCHIVE · 2019 · LISBON`. Fica em todo trecho de arquivo (padrão de telejornal) |
| G05 | **Remote link** | Moldura 16:9 a 70% da tela sobre um fundo de estúdio, tag `REMOTE · MANCHESTER`, card de nome do lado esquerdo |
| G06 | **Document reveal** | Print da matéria em um "papel" levemente inclinado, sombra suave, zoom de 105→115% em 5 s, marca-texto âmbar varrendo a frase-chave + clique |
| G07 | **Data wall (telão)** | Telão LED virtual (perspectiva 3D) mostrando números, organogramas e fluxos de dinheiro. Usado nos capítulos Doyen, Etihad, Wega/Fordham e UAE £10bn |
| G08 | **Número 3D no gramado** | Texto extrudado rastreado em plano de estádio (camera tracker do AE ou Blender). Usado em £67.5M, £8M, £59.5M, 115 |
| G09 | **Mapa** | Mapa escuro estilizado com pinos âmbar e linhas pontilhadas animadas (Enschede, Budapeste, Lisboa, Manchester, Abu Dhabi, offshores) |
| G10 | **Contador** | Números rolando (70.000.000 documentos · 3,4 TB · 147 crimes · 114/115) |
| G11 | **Cutout de personagem** | Foto recortada, contorno de luz âmbar e fundo de painel LED com textura de grade. Push-in de 3% |
| G12 | **Terminal / hacker UI** | Texto monoespaçado verde ou âmbar rolando, cursor piscando, efeito CRT leve (só no capítulo do Rui) |
| G13 | **Legendas de arquivo** | Branco com contorno preto suave; palavra-chave em âmbar. Inter SemiBold, 2 linhas no máximo |
| G14 | **Bug do canal** | Logo do seu canal no canto superior direito, com 70% de opacidade |
| G15 | **End screen** | 20 s, créditos à esquerda e 2 slots de vídeo à direita, com fundo de estúdio |
| G16 | **Transições da casa** | (a) flash branco de 2 frames, (b) glitch RGB de 6 frames, (c) light-wipe âmbar de 10 frames, (d) whip pan |

**Grade de cor (LUT da casa):** pretos esmagados, contraste alto, tons levemente dessaturados e quentes nas imagens de arquivo; o azul do City preservado. Grão de filme leve (5%) em tudo que é arquivo, para unificar fontes de qualidades diferentes.

---

## 2. Shot list completa: o que capturar, cena a cena

Legenda de **Fonte**:
- **ARQ-TV**: telejornal ou entrevista coletiva (canais oficiais de notícias no YouTube, agências)
- **ARQ-JOGO**: jogo ou comemoração (highlights oficiais, uso em comentário)
- **DOC**: print de matéria, documento ou registro comercial
- **STOCK**: banco de imagens (Storyblocks, Artgrid, Pond5, Getty)
- **GFX**: gráfico feito por nós (§1)
- **GRAV**: gravação própria ou recriação (mãos, teclado, notebook, papéis)
- **IA**: imagem gerada para recriação, sempre identificada como "illustrative"

### COLD OPEN (0:00 – 0:25)

| # | Tempo | Áudio | Imagem | Fonte | O que buscar / como capturar | Mov. / transição | SFX |
|---|---|---|---|---|---|---|---|
| S001 | 0:00–0:05 | Guardiola: *"Are you accusing me?"* | Guardiola em coletiva, letterbox 2.39:1 | ARQ-TV | "Guardiola press conference 115 charges are you accusing me" | Punch-in digital lento + G03 | Drone grave |
| S002 | 0:05–0:12 | Čeferin: *"Football… is not for sale"* | Čeferin no púlpito da UEFA | ARQ-TV | "Ceferin football is not for sale speech Super League 2021" | Push-in · corte com glitch G16b | Riser começa |
| S003 | 0:12–0:22 | Soriano questionado por repórter | Soriano no corredor, câmera na mão | ARQ-TV | "Ferran Soriano questioned journalist charges" | Câmera na mão | Pulso de baixo |
| S004 | 0:22–0:25 | — | **G01 vinheta de abertura** | GFX | — | Sting 3D | Hit + whoosh do sting |

### 1. TOO GOOD TO BE TRUE (0:25 – 1:15)

| # | Tempo | VO (resumo) | Imagem | Fonte | O que buscar / como capturar | Mov. / transição | SFX |
|---|---|---|---|---|---|---|---|
| S005 | 0:25–0:29 | "Between 2017 and 2023…" | Comemoração de título, chuva de papel picado | ARQ-JOGO | "Man City trophy lift 2018 / 2019 celebration" | Whip pan | Trilha principal entra (beat investigativo) |
| S006 | 0:29–0:33 | "Five titles in six seasons" | Troféus empilhando sobre foto do elenco | GFX + ARQ | 5 troféus da Premier League em PNG + foto do elenco | Pop-ins em sequência no beat | 5 "tiks" no beat |
| S007 | 0:33–0:36 | "A hundred points" | **G08 "100"** em 3D no gramado | GFX | Plano aberto do Etihad (drone stock) | Câmera 3D rastreada | Whoosh |
| S008 | 0:36–0:40 | "More than a billion euros" | Apresentações de contratados (Haaland, Grealish, Rodri…) | ARQ-TV | "Man City unveil signing" | Montagem de 3 cortes de 1,2 s | Flash cuts |
| S009 | 0:40–0:46 | "While the traditional giants…" | Montagem rápida: gols e torcida | ARQ-JOGO | Highlights | Jump cuts de 1,5 s | Narração de gol baixa ao fundo |
| S010 | 0:46–0:50 | "Record commercial revenues" | **G07 data wall**: gráfico de receita comercial subindo | GFX | Dados: Deloitte Football Money League | Câmera desliza até o telão | Tick de UI |
| S011 | 0:50–0:53 | "Too good to be true." | Exterior do Etihad, mural, escudo | STOCK | "Etihad Stadium exterior gimbal" | Push de gimbal à frente | Trilha some |
| S012 | 0:53–0:54 | "It was." | Tela preta, só a palavra **IT WAS.** | GFX | — | Corte seco | **Silêncio de 0,5 s** + hit |
| S013 | 0:54–1:00 | "Found guilty of 114 breaches" | **G06** manchete do veredito | DOC | Manchete em inglês (BBC/Guardian/Sky) | Zoom lento + marca-texto | Clique de mouse |
| S014 | 1:00–1:04 | — | Aéreo do Etihad, close no escudo | STOCK | "Etihad Stadium drone aerial" | Aéreo lento | Sub-hit |
| S015 | 1:04–1:11 | "One man… 3.4 terabytes" | Rui Pinto algemado no corredor + G10 "3.4 TB" | ARQ-TV + GFX | "Rui Pinto handcuffs court Lisbon" | Câmera na mão + contador | Foley de algemas + riser |
| S016 | 1:11–1:15 | — | **G02 bumper**: *01 · THE FIRST DOMINO* | GFX | — | Bumper | Hit + whoosh |

### 2. THE FIRST DOMINO (1:15 – 2:15)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S017 | 1:15–1:19 | "November 2015…" | **G09** mapa: zoom até Enschede (NL) | GFX | — | Zoom de mapa | Whoosh |
| S018 | 1:19–1:25 | "Phone won't stop ringing" | Celular vibrando sobre mesa de escritório | GRAV / STOCK | Close de celular tocando, luz fria | Macro | Vibração + toque |
| S019 | 1:25–1:32 | Presidente do Twente | Aldo van der Laan em coletiva + G03 | ARQ-TV | "Aldo van der Laan FC Twente press conference Doyen" | Reenquadramento | VO |
| S020 | 1:32–1:36 | "Russian server" | **G12** terminal: domínio carregando, tag "RU" | GFX | — | Digitação na tela | Digitação + glitch |
| S021 | 1:36–1:45 | "€5M… seven players" | **G07** escudo Twente → Doyen → €5M, 7 silhuetas com % | GFX | Logos em versão monocromática (uso editorial) | Setas tracejadas animadas | Pops de UI |
| S022 | 1:45–1:49 | "Third-party ownership" | Card de definição **TPO** | GFX | — | Slide | Pad grave |
| S023 | 1:49–1:55 | "Veto clause" | **G06** trecho do contrato com marca-texto | DOC | Documentos publicados pelo Football Leaks / Der Spiegel | Zoom | Riscar de caneta |
| S024 | 1:55–2:02 | "Banned for three years" | Twente: treino, estádio, jogadores saindo de campo | ARQ-JOGO / ARQ-TV | "FC Twente Grolsch Veste 2016" | Pan lento | Melodia em tom menor |
| S025 | 2:02–2:09 | "Nearly bankrupted" | Manchete sobre o banimento do Twente | DOC | Reuters/BBC 2016 | Zoom + marca-texto | Clique |
| S026 | 2:09–2:12 | "Ronaldo and Mourinho" | **G11** split: Ronaldo × Mourinho | GFX + foto | Fotos editoriais | Parallax | Impacto grave |
| S027 | 2:12–2:15 | — | **G02** *02 · WHO IS "JOHN"?* | GFX | — | Bumper | Hit |

### 3. WHO IS "JOHN"? (2:15 – 3:15)

| # | Tempo | VO / áudio | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S028 | 2:15–2:20 | Rui: *"Hi, this is Rui Pinto…"* | Clipe de apresentação do Rui (webcam) | ARQ-TV | "Rui Pinto video statement whistleblower" | Câmera na mão | Áudio original |
| S029 | 2:20–2:27 | "Rui Pedro Gonçalves Pinto" | Páginas de caderno virando + nome gigante | GRAV + GFX | Macro: mãos folheando um caderno | Zoom cinético | Papel + hit |
| S030 | 2:27–2:33 | "Porto fan, history student" | Estádio do Dragão / Porto + cutout do Rui | STOCK + G11 | "Porto Dragao stadium drone", "Porto city" | Parallax | Tom ambiente |
| S031 | 2:33–2:38 | "Budapest… alias John" | **G09** mapa Lisboa → Budapeste + tag "JOHN" | GFX | — | Linha pontilhada | Whoosh |
| S032 | 2:38–2:45 | "Football Leaks" | Cascata de documentos, matriz de dados | GFX | Elementos de UI de dados / partículas | Zoom-out em várias camadas | Glitch de dados |
| S033 | 2:45–2:50 | "70 million documents" | **G10** contador → 70,000,000 | GFX | — | Contagem rolando | Tick acelerando |
| S034 | 2:50–2:56 | "Partnered with EIC / Der Spiegel" | Teclado em macro + G07 logos EIC/Spiegel | GRAV + GFX | Macro de teclado iluminado (gravar em casa) | Puxada de foco | Teclado |
| S035 | 2:56–3:04 | "Hunted… threatened" | Rui de máscara; estádio visto entre galhos | ARQ-TV + STOCK | "Rui Pinto mask" | Tilt para cima | Violoncelo grave |
| S036 | 3:04–3:15 | Rui (entrevista em inglês) | Talking head em close | ARQ-TV | Entrevistas do Rui em inglês (doc *Football Leaks*, DW, Spiegel TV) | Close | Drone grave |

### 4. THE EARTHQUAKE IN PORTUGAL (3:15 – 4:00)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S037 | 3:15–3:20 | "Earthquake" | Brasão de Portugal / mapa PT tremendo | GFX | — | Camera shake | Rumble |
| S038 | 3:20–3:30 | "Benfica emails" | Manchetes sobre os e-mails do Benfica, rolagem vertical | DOC | Record, Público, Expresso: "e-mails do Benfica" | Rolagem automática + marca-texto | Obturador + cliques |
| S039 | 3:30–4:00 | Rui (entrevista na TV, PT, legendada) | Rui com microfones, plano médio | ARQ-TV | "Rui Pinto entrevista RTP Benfica justiça" | Micro-movimentos de mão | Áudio original + legenda G13 |

### 5. THE LINE HE CROSSED (4:00 – 4:30)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S040 | 4:00–4:06 | "€1 million from Doyen" | **G07** e-mail de extorsão (recriação) + "€1,000,000" | GFX | Recriação marcada como "illustrative" | Câmera deslizando | Tick de UI |
| S041 | 4:06–4:12 | "Arrested in Budapest" | Escolta policial, corredor do tribunal, imprensa | ARQ-TV | "Rui Pinto extradition Budapest 2019" | Câmera tremida | Flashes de câmera |
| S042 | 4:12–4:15 | "147 crimes" | **G10** contador 147 | GFX | — | Contagem | Hit |
| S043 | 4:15–4:20 | "Whistleblower" | Silhueta algemada + palavra **WHISTLEBLOWER** | ARQ-TV + GFX | Plano em contraluz | Push-in em câmera lenta | Sub-drop oco |
| S044 | 4:20–4:26 | "Encrypted hard drives… FR, BE, DE" | HDs em sacos de evidência + 3 bandeiras | STOCK + GFX | "evidence bag hard drive" | Tilt | Clique metálico |
| S045 | 4:26–4:30 | — | **G02** *03 · EUROPE'S UNDERWORLD* + G12 terminal | GFX | — | Glitch | Chiado de modem |

### 6. EUROPE'S UNDERWORLD (4:30 – 5:40)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S046 | 4:30–4:38 | "No rules" | Escritórios e monitores à noite | STOCK | "dark office monitors night" | Tracking horizontal | Beat volta |
| S047 | 4:38–4:47 | "European Super League" | **G06** matéria da Super League + escudos | DOC + GFX | Matérias da Super League em 2018 e 2021 | Rolagem + marca-texto | Clique |
| S048 | 4:47–4:55 | "PSG… Neymar, Mbappé" | Apresentações de Neymar e Mbappé no Parc des Princes | ARQ-TV | "Neymar presentation Parc des Princes 2017" | Tracking aberto | Eco do sistema de som do estádio |
| S049 | 4:55–5:02 | "Qatar Tourism €200M vs €3M" | **G07** duas barras: €200M × €3M | GFX | — | Barra encolhendo | Whoosh descendente |
| S050 | 5:02–5:06 | "State money as revenue" | Al-Khelaifi em coletiva + G03 | ARQ-TV | "Nasser Al-Khelaifi press conference" | Corte | Pulso |
| S051 | 5:06–5:14 | "Offshores… €150M image rights" | **G09** pinos: BVI, Luxemburgo, Jersey | GFX | — | Linhas animadas | Pings |
| S052 | 5:14–5:20 | "Tax conviction in Spain" | Ronaldo chegando ao tribunal em Madri | ARQ-TV | "Ronaldo court Madrid 2019 tax" | Câmera na mão | Flashes |
| S053 | 5:20–5:33 | Alegação de Mayorga (com "denied") | **G06** matéria da Der Spiegel + Ronaldo em P&B | DOC | Matéria original da Spiegel; sem fotos da vítima | Zoom lento | Cordas tensas |
| S054 | 5:33–5:40 | "One club kept showing up" | Escudo do City surgindo entre documentos | GFX | — | Documentos se afastando | Riser |

### 7. ABU DHABI'S PROJECT (5:40 – 6:40)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S055 | 5:40–5:46 | — | Voo de drone sobre o estádio → **G02** *04 · THE CITIZENS* | STOCK + GFX | — | Corte seco no bumper | Riser + hit |
| S056 | 5:46–5:55 | "Sheikh Mansour… 2008" | Mansour em cerimônias + G03 | ARQ-TV | "Sheikh Mansour Etihad 2008 / 2010 visit" | Tracking médio | Beat |
| S057 | 5:55–6:00 | "ADUG… hundreds of billions" | **G07** organograma Mansour → ADUG → CFG → City | GFX | — | Nós aparecendo | Pops de UI |
| S058 | 6:00–6:06 | "Khaldoon Al Mubarak" | Khaldoon no lounge do clube + G03 | ARQ-TV | "Khaldoon Al Mubarak interview City TV" | Pan | Beat |
| S059 | 6:06–6:15 | Apresentação do jornalista | **G05** remote link: nome e veículo | GRAV (entrevista sua) | Gravar ou licenciar a entrevista com o jornalista | Pop-in da moldura | Diálogo limpo |
| S060 | 6:15–6:27 | Fala do jornalista (história do City) | Camisas retrô, troféus dos anos 1990, túnel | ARQ / STOCK | "Maine Road 1990s Man City archive" | Pan por vitrines | Legenda G13 |
| S061 | 6:27–6:40 | Volta à entrevista → título de 2012 | G05 → Agüero 93:20 | ARQ-JOGO | "Aguero 93:20 QPR 2012" | Corte | Comemoração baixa |

### 8. THE ETIHAD MATH (6:40 – 7:20) · *cena-assinatura*

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S062 | 6:40–6:46 | "Financial Fair Play, 2011" | Logo do FFP / UEFA no data wall | GFX | — | Câmera deslizando | Whoosh |
| S063 | 6:46–6:52 | "Etihad… £67.5M" | **G08** "£67.5M" em 3D sobre o gramado | GFX + STOCK | Plano aberto do gramado (drone travado) | Whip pan 3D pelas arquibancadas | Varredura de scanner |
| S064 | 6:52–6:58 | "Finance director's emails" | **G06** e-mail com marca-texto em "£8m" | DOC | E-mails publicados pela Der Spiegel | Zoom | Clique |
| S065 | 6:58–7:06 | "£8M… other £59.5M" | **G08** o bloco 3D se parte em £8M + £59.5M | GFX | — | Rachadura e separação | Hit + estalo de vidro |
| S066 | 7:06–7:12 | "Straight from ADUG" | Seta do ADUG → Etihad → City no data wall | GFX | — | Fluxo de dinheiro | Pulso grave |
| S067 | 7:12–7:20 | Jornalista comenta | G05 alternando com Mancini, Agüero, De Bruyne | ARQ-JOGO | Highlights | Cortes médios | Batida de tensão |

### 9. THE SCHEME EVOLVES (7:20 – 8:20)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S068 | 7:20–7:27 | "Guardiola era" | Guardiola na prancheta tática | ARQ-TV | "Guardiola training tactics" | Push | Beat |
| S069 | 7:27–7:34 | "Girona… Pere Guardiola" | Split-screen: escudo do Girona + cutout de Pere (G11) | GFX | — | Pan em split-screen | Slide de UI |
| S070 | 7:34–7:40 | "Wega… £40M" | **G07** contrato "£40M" no telão | GFX | — | Câmera deslizando | Tick |
| S071 | 7:40–7:50 | "No products, no staff… £1,200" | **G06** registro comercial com marca-texto em 4 itens | DOC | Print do registro comercial (Companies House / equivalente) | Zoom em cada item | 4 cliques |
| S072 | 7:50–7:56 | "Image rights → Fordham" | **G07** fluxo: jogadores → Fordham → $ | GFX | — | Setas | Whoosh |
| S073 | 7:56–8:02 | "Vanished from reports" | Linhas de planilha sumindo | GFX | — | Dissolve por pixel | Glitch |
| S074 | 8:02–8:08 | "Feb 2020 UEFA ban" | Matérias sobre o banimento + reação de jogadores | DOC + ARQ | Manchetes de fevereiro de 2020 | Corte | Pulso de sintetizador |
| S075 | 8:08–8:13 | "Overturned… €10M fine" | Carimbo **OVERTURNED** sobre a matéria | GFX | — | Carimbo batendo | Carimbo + hit |
| S076 | 8:13–8:20 | "2026… 114 of 115" | **G10** 114/115 + manchete | GFX + DOC | Matéria do veredito | Contador | Hit forte |

### 10. FOOTBALL AS DIPLOMACY (8:20 – 10:00)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S077 | 8:20–8:26 | — | Soriano caminhando à noite → **G02** *05 · THE POLITICAL CONNECTIONS* | ARQ + GFX | — | Câmera na mão até o bumper | Impacto grave |
| S078 | 8:26–8:34 | "Hostage to diplomacy" | Chegada do ônibus do City; skyline de Abu Dhabi | ARQ + STOCK | "Abu Dhabi skyline night drone" | Drone | Trilha sombria |
| S079 | 8:34–8:42 | "Embassy & Foreign Office" | Fachada do Foreign Office + documento oficial | STOCK + DOC | "Foreign Office London exterior" | Pan | Obturador |
| S080 | 8:42–8:50 | "£10bn invested" | **G07** £10bn dividido em energia, imóveis e infraestrutura | GFX | — | Barras | Ticks |
| S081 | 8:50–8:57 | "Diplomatic crisis" | Aéreo do Parlamento; Haaland no treino | STOCK + ARQ | "Westminster aerial" | Drone | Pulso |
| S082 | 8:57–9:05 | Política local | Andy Burnham em comício → G05 | ARQ-TV | "Andy Burnham speech Man City" | Corte | VO do jornalista |
| S083 | 9:05–9:37 | Jornalista sobre política | Comícios, debate no Parlamento, arquibancada | ARQ-TV | "Commons debate football regulator" | Pans rápidos | Murmúrio de multidão |
| S084 | 9:37–10:00 | Encerramento do jornalista | G05 ↔ loja do City ↔ Soriano em gala | Misto | — | Tilts lentos | VO passa para a narração |

### 11. THE PRICE OF TELLING (10:00 – 11:04)

| # | Tempo | VO | Imagem | Fonte | Buscar / capturar | Mov. | SFX |
|---|---|---|---|---|---|---|---|
| S085 | 10:00–10:04 | — | **G02** *06 · THE PRICE OF TELLING* | GFX | — | Bumper | Hit |
| S086 | 10:04–10:14 | "Gianni Infantino" | Infantino em reunião da FIFA + G03 + tag "ALLEGATION" | ARQ-TV | "Infantino FIFA congress" | Pan de perfil | Tique-taque + sub |
| S087 | 10:14–10:27 | "Witness protection… lost" | Rui no corredor do tribunal, escolta | ARQ-TV | — | Push-in lento | Acordes sombrios |
| S088 | 10:27–10:39 | "Exposed to real danger" | Rui sozinho na sala do tribunal, de máscara | ARQ-TV | — | Push-in atrás da divisória | Narração pesada |
| S089 | 10:39–10:50 | "Political deals…" | Guardiola aplaudindo, dirigentes, Haaland comemorando | ARQ-JOGO | — | Câmera lenta | Trilha cresce |
| S090 | 10:50–10:57 | "One guy… laptop" | **Callback:** notebook brilhando no quarto escuro | GRAV | Gravar: notebook, quarto escuro, luz da tela no rosto (sem mostrar o rosto) | Push-in | Swell |
| S091 | 10:57–11:00 | "…maybe it really is." | Grua sobre estádio vazio → preto | STOCK | "empty stadium crane night" | Grua puxando para trás | **Silêncio** antes da frase final |
| S092 | 11:00–11:20 | — | **G15** end screen | GFX | — | — | Último hit com cauda de reverb |

---

## 3. Lista de captura agrupada (para baixar/gravar em lote)

**A. Arquivo de TV / coletivas (≈30 clipes):** Guardiola, Čeferin, Soriano, van der Laan, Rui Pinto (vídeo de apresentação, entrevistas em EN e PT, tribunal, extradição, algemas, máscara), Al-Khelaifi, Ronaldo no tribunal de Madri, Mansour, Khaldoon, Burnham, Infantino, apresentações de Neymar e Mbappé, contratados do City, debate na Câmara dos Comuns.

**B. Jogos e comemorações (≈15 clipes):** títulos do City de 2018/19/21/22/23, Agüero 93:20, gols de De Bruyne e Haaland, Guardiola aplaudindo, Twente.

**C. Stock (≈20 clipes):** Etihad (drone, gimbal, escudo, gramado travado para o rastreio 3D), Porto, Budapeste, skyline de Abu Dhabi, Westminster, Foreign Office, escritórios à noite, sacos de evidência, estádio vazio com grua.

**D. Documentos e prints (≈15):** veredito (EN), banimento do Twente, e-mails do Benfica, Super League, contrato Qatar/PSG, Ronaldo offshore, matéria da Spiegel sobre Mayorga, e-mail Etihad £8m, registro comercial da Wega, banimento da UEFA em 2020 e reversão no CAS. **Capture em 4K** (zoom do navegador em 200%) e salve o link e a data de cada print.

**E. Gravação própria (1 tarde, sem atores):** celular vibrando, caderno folheando, teclado em macro, notebook no quarto escuro (abertura e fechamento), mãos digitando, papéis sobre a mesa.

**F. Gráficos (§1):** 16 peças de template e ≈40 instâncias.

**G. Entrevista:** a referência tem um jornalista do *The Guardian*. Para a sua versão, **grave a sua própria** entrevista remota (Zoom/Riverside, gravação local em 1080p+) com um jornalista ou analista. Não reaproveite a do PELEJA.

---

## 4. Áudio (padrão de emissora)

- **Narração (EN):** voz masculina grave, tom de documentário (ex.: ElevenLabs/Suno "news anchor deep" ou locutor contratado). Cadeia: HPF 80 Hz → de-esser → compressor 3:1 → limitador. Mixar a narração em **-14 LUFS integrado** e true peak de -1 dB.
- **Trilha:** 3 camadas. (1) Beat investigativo eletrônico/hip-hop, 90–100 BPM, nas montagens; (2) drone/cordas tensas nos trechos de tribunal e de alegações; (3) clímax emocional em 10:39. Duck de -12 dB sob a narração.
- **Pacote de SFX da casa:** stinger do bumper, whoosh, sub-hit, riser, glitch RGB, clique de mouse, obturador, flash de câmera, algemas, chiado de modem, carimbo, ticks de UI.
- **Silêncios estratégicos:** S012 ("It was."), S091 (antes da frase final).

---

## 5. Direitos e segurança (importante)

- **Highlights da Premier League** são os mais vigiados pelo Content ID. Use no máximo 2–4 s por clipe, sempre com narração por cima e algum tratamento (moldura, cor, gráfico). Prefira coletivas e telejornais, que têm risco menor, e substitua o que der por stock e gráficos.
- **Logos de clubes e de mídia** só em contexto editorial; nada de logo de emissora real no seu pacote.
- **Não use** a vinheta, o logo, a cor-assinatura amarela, a entrevista nem as cartelas do PELEJA: recrie tudo com a sua identidade (por isso trocamos para âmbar e azul-escuro).
- **Alegações** (Mayorga, Infantino): mantenha as linhas "denied" na tela e na narração, sem imagens da vítima.
- **Recriações por IA** (e-mail de extorsão etc.): marque com a tag "ILLUSTRATIVE" no canto.

---

## 6. Opcional: âncora em estúdio virtual

Se quiser o visual de "grande estúdio" com apresentador, insira 3 aparições curtas, de 6–10 s cada, gravadas em chroma key com fundo de estúdio virtual (telões com os gráficos G07):
1. Logo depois da vinheta (0:25): âncora abre "Tonight: how one leak…"
2. Na virada para o City (5:40): âncora em frente ao data wall
3. No fechamento (10:50): âncora diz a frase final olhando para a câmera

Equipamento mínimo: tecido verde, 2 softboxes, câmera ou celular em 4K, lapela. Keyer: Ultra Key (Premiere) ou Delta Keyer (DaVinci).

---

## 7. Ordem de produção sugerida

1. Gravar a narração em EN (trava o tempo de tudo)
2. Montar o pacote gráfico §1 (templates)
3. Capturar os grupos A–E da §3 e organizar em pastas `A_ARQ-TV / B_JOGO / C_STOCK / D_DOC / E_GRAV`
4. Fazer o corte de rádio: narração + entrevista no tempo
5. Primeira montagem seguindo a shot list §2 (S001–S092)
6. Gráficos e rastreio 3D (S007, S063, S065)
7. Cor (LUT da casa + grão) → mix de áudio a -14 LUFS → legendas EN (.srt)
8. Revisão de direitos (§5) → exportar em 4K H.264/H.265, 40–60 Mbps
