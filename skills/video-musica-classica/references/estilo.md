# Estilo de referência — canal Classical Mind (@The-Classical-Mind)

Levantado em out/2026 assistindo ao vídeo mais visto (1,4M views). Não precisa
reassistir, a não ser que o usuário peça um estilo diferente.

## Formato do canal
- Compilações de 1h30 a 3h; títulos tipo "Mozart Effect for Deep Focus |
  Classical Music for Study", às vezes com "432Hz".
- Áudio: piano solo, limpo, sem ambiente (a chuva/sound design é um extra nosso,
  baixo e opcional).

## Visual
- Imagens IA de época: pianista do séc. XVIII/XIX, salões, teatro, corredores,
  luz de vela, noite com lua.
- Cada imagem 8–10 s no canal; nós usamos 12 s na seção dinâmica e 60 s no ciclo
  calmo (vídeo longo, menos repetição perceptível).
- Zoom-in lento contínuo (Ken Burns); crossfade de 1,5–2 s.
- Poeira/partículas douradas, flicker de vela, vinheta forte, grão leve,
  contraste quente (âmbar) x frio (azul da noite).
- Título central em serifa clássica (usamos Cinzel), fade in/out.
- Marca deles (não copiar): nome "CLASSICAL MIND" e cérebro azul brilhante
  sobreposto. Se o usuário quiser um elemento fixo, criar um próprio.

## Menu de efeitos por custo
**Leves** (quase sem custo): transições do `xfade` (~50: fade, fadeblack,
circleopen, slideleft, pixelize, radial…), grading/LUT `.cube` (`lut3d`),
vinheta, barras de cinema (`drawbox`), textos/nome da faixa (`drawtext` com
`textfile`), câmera "respirando"/tremor leve (crop com `sin(t)`, sem 4K),
visualizador de áudio (`showwaves`/`showfreqs`), barra de progresso.

**Médios** (ok se renderizados uma vez e repetidos em loop): partículas
(poeira, chuva, neve, vaga-lumes, bokeh — gerar com numpy, periódicas), light
leaks, glow nas luzes (`gblur` + `blend=screen`), névoa por overlay de vídeo.

**Pesados** (evitar em vídeo longo): grão animado (`noise=allf=t`, arquivo ~10x
maior), muitas imagens num único filter_complex (falta de memória), efeitos que
reagem à batida (análise de áudio quadro a quadro).

## Zoom "estilo CapCut"
O zoom do CapCut é rápido e marcado (0,3–1 s); o nosso padrão é lento e com
ease in-out. Para imitar: `slot` curto + curva rápida no início, ou um
"punch-in" de 1x→1,15x em ~0,3 s. Só implementar se o usuário pedir.
