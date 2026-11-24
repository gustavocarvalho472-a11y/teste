# Estilo v2 — "Cinema + Revista" (padrão do canal desde nov/2026)

O dono aprovou este estilo no vídeo "Arteta Tried To Save Vinicius" e pediu que ele seja o padrão dos próximos vídeos. Ele **substitui** a moldura "video wall" e os motion graphics estilo TV da v1 (`render.js`/`frame.js`), que ficaram só como legado.

## O que o dono pediu, nas palavras dele (nov/2026)
- "Trabalhar mais com as imagens e o motion ser secundário": menos motion, sem bordas e com menos letreiro.
- "Mais imagens do Vini": o personagem principal aparece o tempo todo.
- "Edição mais voltada para o público que quer assistir futebol, um público um pouco mais velho".
- "Aprender os ângulos da câmera, onde você dá o zoom nos takes, deixar mais no rosto dos personagens".
- "Quando não tiver take, trabalhar as animações com a foto: zoom in, zoom out, colocando algum elemento".
- Ele gostou da mistura de A (cinema/documentário) com B (revista/editorial) e pediu acabamento "no mais alto nível", com serifa e componentes de editorial.

## Princípios
1. **A imagem manda.** Tela cheia, sem moldura e sem HUD. Quase todo plano é take real ou foto animada. Gráfico entra só quando informa algo que a imagem não mostra: data/local, nome, placar, citação ou matéria.
2. **Câmera motivada.** Todo plano tem um movimento lento e com intenção, sempre em direção ao rosto ou saindo dele. Nada de zoom aleatório no centro.
3. **Ritmo de documentário.** Planos de 4–5 s no corpo do vídeo e 3–3,5 s na abertura, que continua dinâmica pelo corte e pelo som, não por efeitos. Entre cenas, corte seco. Só capítulo, título e fim fazem fade (dip to black de 0,35–0,45 s).
4. **Pouco texto, bem desenhado.** No máximo um elemento gráfico por plano e nunca uma frase longa na tela. A legenda de fala (soundbite) é a exceção, e cada frase aparece sozinha.
5. **Cor de cinema.** Contraste +7%, saturação −18%, leve calor nos médios. Grão de filme temporal só na luminância e vinheta suave. P&B para passado, capítulos e citações.

## Identidade (tokens) — `kitlib.js`
| Token | Valor | Uso |
|---|---|---|
| lime | `#C6FF00` | destaque: palavra-chave da fala, fio do lower third, ponto do slate, círculo do callout, número do capítulo |
| paper | `#ECE7DC` | recortes de jornal, etiquetas, placar |
| ink | `#111111` | texto sobre papel |
| dim | `#BDBAB2` | rótulos secundários |
| margem | 120 px | todo texto alinha a 120 px da borda |

Papéis de tipografia (fontes via `@fontsource`, todas grátis):
- **Playfair Display** (serifa): nomes, citações (itálico), títulos do filme, legendas de foto.
- **Barlow Condensed 800**: só palavras de impacto em caixa alta (título do capítulo, "4 GAMES. 4 WINS.", "72'").
- **IBM Plex Mono**: datas, locais, rótulos e fontes, sempre em caixa alta com espaçamento largo.
- **Inter 600**: legenda das falas.

## Componentes (`kitlib.js`) e quando usar
Overlays (PNG transparente sobre o take, com fade de 0,4 s; as legendas usam 0,12 s):
| Componente | Quando | Frequência |
|---|---|---|
| `slate` | data e local no canto superior esquerdo ("06 · 08 · 2026 — Renews until 2032") | ~1 a cada 40 s; substitui as cartelas de data |
| `l3` | nome em serifa e cargo em mono, na **primeira** vez que a pessoa aparece | 1 por personagem |
| `sub` + `shade` | legenda de fala real, uma frase por vez, com `*palavra*` em lime; `who` em mono quando quem fala não está na tela | todo soundbite |
| `score` | placar final (papel no meio) com nota em lime ("Vinicius · suspended") | só quando o resultado é a notícia |
| `cta` | pílula "Subscribe"/"Tell me in the comments" no canto inferior direito, com o take rodando por baixo | 3 por vídeo (após a intro, no meio e no fim) |

Plates (quadro cheio renderizado em 2×, 3840×2160, para a câmera passear sem perder nitidez):
| Componente | Quando | Movimento |
|---|---|---|
| `title` | título do filme logo após a abertura, sobre foto P&B escura com marcas de corte | push 6% + riser + boom |
| `chapter` | abertura de capítulo: foto P&B à esquerda (rosto centralizado via `panel_pos`), número em itálico lime, data mono, título condensado e sinopse em itálico | push 4% + boom, fade |
| `clipping` | matéria de jornal citada (AS, The Athletic, post): recorte de papel com clipe, borda rasgada e marca-texto lime; rodapé "Paraphrased · not a quote" | push 12% sobre a mesa + whoosh |
| `quote` | frase que não temos em vídeo: foto P&B escura, aspas lime, itálico serifado e atribuição mono | push 6% |
| `impact` | número que o vídeo vai lembrar ("72'", "4 GAMES. 4 WINS.") sobre foto P&B | push 7% + impacto |
| `results` | sequência de resultados; as linhas entram uma a uma, sincronizadas com a narração (`states`) | push 4% |
| `timeline` | resumo final em polaroids com a data acesa avançando (`states`) | push 4% |
| `print` | foto impressa com borda branca, girada, sobre papel escuro, com legenda em itálico e data | push 8% |
| `callout` | apresentar alguém numa foto: círculo lime no rosto, fio com cotovelo e etiqueta escura (nome em serifa, dados em mono) | push 8% em direção ao círculo |
| `end` | encerramento com pílula de inscrição e créditos curtos | push 3%, fade |

Frequência que funcionou (12 min): 1 título, 5 capítulos, 3 recortes, 5 citações, 2 impactos, 1 resultados, 1 linha do tempo, 2 prints, 1 callout. Plates ocupam ~22% do tempo. Takes de vídeo ~50% e fotos animadas ~28%.

## Linguagem de câmera (`camera.py`)
O editor decide a câmera pelo rosto. A regra é automática, com correção manual onde o detector erra:
- **Fala (`talk`)**: plano médio fechado, rosto com ~40% da altura do quadro e olhos no terço superior (o centro do rosto fica a 42% da altura). Respira 3–5% para dentro.
- **Punch-in (`tight`)**: na segunda frase de um soundbite, corte para um plano mais fechado do mesmo take (rosto ~52%, mínimo de 1,14×). É o "jump zoom" de documentário, que esconde o corte e dá energia sem efeito.
- **B-roll (`broll`)**: rosto com ~30% da altura. Alterna **push-in** (do plano aberto para o rosto) e **pull-out** (do rosto para o contexto). Se o rosto se mexe, o foco vai da posição inicial à final ("tracking").
- **Foto (`photo`)**: Ken Burns mais forte (12–22%), sempre entrando ou saindo do rosto. Foto sem rosto (estádio, ônibus) faz drift lateral (`move: "pan"`) ou push no ponto de interesse (`focus`).
- **Texto do lado esquerdo** (lower third): o rosto vai para o terço direito (`frx = 0.6`).
- **Limites**: nunca ampliar a fonte mais que 2,45× (vídeo) ou 2,0× (foto). Nunca mostrar fora da área limpa (`safe`): logos de emissora, relógio, tarjas "MADRID" e legendas queimadas ficam sempre fora.
- Movimento com easing seno (entra e sai devagar). Ele é implementado com `scale=…:eval=frame` + `crop` com expressões em `t`, o que dá zoom sub-pixel suave (o `zoompan` treme).

Detecção de rosto: `faces.py` usa cascatas Haar do OpenCV. **Instale `pip install "opencv-python-headless<5"`**, porque a versão 5 não traz as cascatas e o download do YuNet no GitHub dá 403. Em coletivas o detector acerta quase sempre. Em imagem de torcida ele trava em torcedores, então o Vini precisa de foco manual (`VFIX` por janela e `FIX` por foto). A caixa Haar cobre da testa ao queixo, então a altura dela é a altura do rosto.

**Conferência obrigatória antes do render**: `python3 camsheet.py` gera `build/v2/camera_*.jpg`, com um quadro por plano, a caixa branca (enquadramento inicial), a caixa lime (final) e um ponto vermelho no rosto detectado. Procure três coisas: caixa no torcedor em vez do jogador, cabeça cortada pela área limpa e plano estático demais. Corrija `FIX`/`VFIX` e gere de novo.

## Som (`assemble2.py`)
- Música mais baixa que na v1: base 0,085 RMS, que cai para 15% sob a voz e sobe para 60% nas pausas. O público é mais velho e quer ouvir a história.
- Efeitos só onde a imagem muda de natureza: boom grave no capítulo, riser + boom no título, impacto no `impact`, whoosh suave ao entrar em recorte/print/citação e tick discreto no lower third e no placar. Nenhum efeito por corte.
- Áudio original (`nat`) em todo soundbite. Sai em −14 LUFS.

## Pipeline v2 (arquivos em `scripts/v2/`, modelo em `exemplo/build_vinicius_v2.py`)
```bash
cd video-production/<slug>
cp <skill>/scripts/v2/* . && cp <skill>/exemplo/build_vinicius_v2.py build2.py
npm i --silent @fontsource/playfair-display @fontsource/barlow-condensed @fontsource/ibm-plex-mono @fontsource/inter
pip install -q "opencv-python-headless<5"
python3 build2.py        # timeline + lista de gráficos (detecta rostos; cache em build/faces.json)
python3 camsheet.py      # CONFERIR o enquadramento
node gfx2.js             # overlays e plates (cache por conteúdo e pela data das fotos)
JOBS=4 python3 assemble2.py c00 n03 k15  # testar algumas cenas e olhar quadros
JOBS=4 nohup python3 assemble2.py > build/v2/assemble.log 2>&1 &   # tudo (~2× o tempo do vídeo)
```
No `build2.py`, a DSL é:
- `SB(...)`: soundbite com punch-in automático.
- `L("B07", F(.55, "xabi", L3(...)), PLT(.45, "quote", ...))`: um beat de narração dividido em partes, sendo `F` takes de um pool e `PLT` um plate.
- `CARD(...)`: título, capítulo, citação ou fim.
- `SL` / `L3` / `SC` / `CTA`: overlays.

Cada pool mistura janelas de vídeo (`V`/`span`) e fotos (`Ph`), e `SAFE` define a área limpa de cada fonte.

## Fotos
- Antes de usar qualquer quadro congelado como foto, olhe-o grande. Já apareceram relógio de TV, tarja de canal e etiqueta "MADRID" da NBC. Recorte para 16:9 limpo (`assets/photos/orig/` guarda o original).
- Quando o Commons funcionar, prefira fotos livres e credite na descrição. Quando der 429, use quadros das fontes (sem crédito de foto, mas com crédito da fonte).
