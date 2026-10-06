# Animação: contrato do projeto, helpers e padrões

Todo o desenho usa **pycairo** em 1920×1080, quadro a quadro. Uma cena é `fn(c, t, d)` e deve desenhar
**tudo** em função de `t`, sem guardar estado entre quadros, porque os quadros são renderizados em
paralelo e fora de ordem.

## Contrato do módulo `video-jesus/<nome>.py`
| Nome | Obrigatório | O que é |
|---|---|---|
| `SCENES` | sim | `[(rótulo, duração, fn, [(início, fim, "legenda *destaque*"), …]), …]` |
| `STARTS`, `TOTAL` | sim | calculados a partir de `SCENES` (copie do modelo) |
| `SCALE`, `SCENES0`, `STARTS0` | sim | `[1.0]*n` e cópias; a narração os reescreve |
| `FADES` | sim | `{índice: (cor_entrada_ou_None, cor_saída_ou_None)}` |
| `verses()` | sim | devolve `VERSES` ou `VERSES_EN` conforme o `LANG` |
| `NARRATION_EXTRA` | não | `{cena: [(t, "fala sem legenda")]}` |
| `TEXTURE`, `VIGNETTE` | não | textura de papel (sempre `True` neste estilo) e vinheta |
| `CAPTION_SCALE`, `NARR_GAP` | não | 0.78 e 0.12 são o padrão do canal |
| `SHORT_OVERLAY(c, t_abs, vw, vh)` | não | texto extra só no Short (selo no topo, CTA "vídeo completo ↓") |
| `SHORT` | não | o motor liga a flag no 9:16. Use para encolher ou esconder o que sai do miolo |
| Bloco `narracao.apply` | sim | as últimas 3 linhas do modelo; não remova |

Duas regras práticas:
- O rótulo `""` mostra a cena sem título de capítulo. Um rótulo `"III · O PREÇO"` mostra o título e o versículo `III`.
- Todo texto desenhado na tela passa por `tr("…")` e ganha uma tradução em `EN.update`.

## CLI do motor (rode dentro de `video-jesus/`)
```
python3 engine.py wide  <nome> <saida.mp4> [audio.wav]          # 16:9
python3 engine.py short <nome> <t0>[:<t1>] <saida.mp4> [audio]  # 9:16 com fundo desfocado
python3 engine.py snap  <nome> wide|short:<t0> <prefixo> t1 t2  # PNGs de teste
```
Variáveis de ambiente:
- `VIDEO_LANG=pt|en`
- `VIDEO_NARRATION=<nome>`: aplica o timing da narração. Sem ele, as cenas ficam na duração original.

## Helpers de desenho (importe dos módulos existentes)
**`prodigo.py`** (estilo chapado):
- **Pintura:**
  - `paint(c, cor)`
  - `fill(c, cor, a)`
  - `bands(c, [cores], y0, y1)`: céu em faixas
  - `blob(c, cx, cy, r, seed)`: mancha orgânica
  - `sun(c, x, y, r, cores)`
  - `cloud(c, x, y, s)`
- **Personagens:**
  - `person(c, x, y, h, pose, facing, col, sash, scarf, ragged, phase, run)`: personagem geométrico sem rosto. Poses: `stand reach give open raised dance`.
  - `sitting(c, x, y, h, facing, col, look_up, sash)`
  - `hug(c, x, y, h)`
- **Cenário e objetos:** `house(c, x, y, s, lit)`, `tree`, `coin`, `bag`, `pig`, `lanterns`, `zoom(c, z, cx, cy)`.
- **Paleta:** `INK #140d1b`, `TEAL #5fe0cf`, `CREAM #fff4dc`, e `GOLD` (vem do `render`).

**`jesus_flat.py`:**
- `halo(c, x, y, h, a)`: auréola de Jesus
- `kneel(c, x, y, h, …)`: pessoa ajoelhada, orando
- `wings`, `bust`, `cross(c, x, y, h)`, `disk`
- `geo_rays(c, x, y, n, rot, cor, a)`: raios geométricos
- `_tomb(…)`: túmulo
- Cenas inteiras reaproveitáveis: `s_cruz`, `s_ressurreicao`, `s_ceia`, `s_nascimento`…

**`render.py`:**
- **Easing e tempo:** `seg(t, a, b)` (0→1 entre a e b), `eio`, `eout`, `eback`, `lerp`, `clamp`, `mix(cor1, cor2, t)`.
- **Luz e atmosfera:**
  - `glow(c, x, y, r, cor, a)`
  - `rays`
  - `particles(c, t, n, seed, cor)`
  - `stars`
  - `ridge` (montanhas)
  - `town` (cidade com janelas acesas)
  - `water`
  - `overlay(c, cor, a)`: fades
- **Texto:**
  - `text_center(c, s, x, y, size, face=SANS, col, a, spacing)`
  - `title_text(c, s, x, y, size, …, shine)`: título dourado com brilho
  - `appeal_lines(c, lines, lt, dur, cy)`: apelo final em linhas
  - `subscribe(c, lt, dur)`: animação de inscreva-se

**`tela.py`** (Tempo de Tela, o mais avançado):
- `kinetic(c, palavra, lt, size, col, dur, y)`: palavra "soco" que se ajusta à largura e respeita o Short
- `phone(c, cx, cy, h, scroll, banners, rot, spinner, content)`: celular com feed; `content` desenha algo dentro da tela
- `strings(c, top, pts, a, sway, fall)`: fios de marionete, com corte e queda
- `rrect`, `heart`, `star`, `flame`, `feed_card`
- `_room(c, t, clock, day)`: quarto noite→manhã
- `brush(c, a)`: pinceladas pictóricas
- `well(…)`: poço
- `_fit(c, bw, bh, draw, …)`: desenha uma cena inteira dentro de um retângulo, útil para zoom contínuo

Antes de desenhar algo do zero, faça `grep -n "^def " video-jesus/*.py` e reaproveite.

## Padrões que deram certo
- **Câmera contínua (mergulho):** desenhe o mundo A, aplique `c.translate/scale` crescente centrado num objeto (a tela do celular), e dentro do objeto desenhe o mundo B com `_fit`. Quando o objeto cobrir a tela, troque para desenhar B direto. Veja `tela._gancho` e `tela._slot`.
- **Recuo:** o inverso. A cena atual vira um card pequeno dentro de um mundo maior (a multidão em `tela.draw_crowd`).
- **Montagem acelerando:** lista `BEATS = [(t, tipo, PALAVRA)]`, um card por batida e um `kinetic` em `y=H*0.86` (veja `tela._montage`). As batidas encurtam: 1.6 s, depois 1.5, 1.1, 0.9.
- **Silêncio visual:** tela preta + uma única luz pequena (a notificação de Mateus 11:28 em `tela._notif`).
- **Grupo com crossfade:** `c.push_group()` + desenha + `c.pop_group_to_source()` + `c.paint_with_alpha(a)`.
- **Short:** o 9:16 mostra só ~71% central da largura. Mantenha texto e ação entre `W*0.15` e `W*0.85`. Use a flag `SHORT` para encolher o `kinetic` e esconder rótulos laterais.

## Armadilhas já encontradas
- **Gradiente radial em retângulo pequeno** cria uma linha visível. Desenhe o retângulo bem maior que o raio (o bug do `draw_chapter`).
- **`mix()` devolve tupla:** use `fill(c, mix(...))`, que aceita tupla.
- **Texto `kinetic` comprido** estoura a tela. Ele já se auto-ajusta, mas confira na grade.
- **Arte acima de `H*0.72`** briga com a legenda (a faixa de legenda fica embaixo).
