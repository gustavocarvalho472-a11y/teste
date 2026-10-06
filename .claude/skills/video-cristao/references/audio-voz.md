# Trilha, sound design e narração

## Trilha (`TOOLKIT/<nome>_audio.py`, sintetizador `synth.py`)
Tudo é sintetizado, então não há direito autoral. Escreva a partitura no **tempo original**
(`STARTS0`): o `synth.WARP` reposiciona tudo se a narração esticar alguma cena. Use `T(k)` (início da
cena k) e `Dur(k)` (duração dela).

- **Instrumentos:**
  - `piano(midi, dur, vel)`
  - `bowed` / `strings(notas, dur)`
  - `choir(notas, dur, breathy)`
  - `bell(midi, dur)`
  - `pad_chord(pc, "M"|"m", dur, bright, gain)`
  - `arpeggio(pc, q, t0, dur, step, vel)`
  - `melody(pc, q, t0, dur, "A"|"B"|"C", vel)`: A sobe (esperança), B desce (dor), C é nota longa (paz)
- **Efeitos:**
  - `timpani(f0, dur, vel)`: pancada / impacto
  - `heartbeat(vel)`
  - `whoosh(dur, up)`
  - `cymbal_swell(dur)`
  - `crack(dur)`
  - `tela_audio.py` tem ainda `buzz` (vibração), `ping` (notificação), `swipe`, `click`, `clunk` e `shepard` (tom que sobe sem fim).
- **Mixagem:**
  - `add(sinal, t0, ganho, pan)`
  - `env_ar(n, ataque, release)`
  - `lp` / `hp`: filtros
- **Silêncio dramático:** `DUCK[i0:i1] = 0`, com tempos já passados por `synth.warp()`.
- **Notas:** constantes `C D E F G A Bb B`. Ré menor para dor, Fá/Ré maior para graça.

Arco emocional típico:
1. Tensão grave + coração.
2. Pulso acelerando na montagem.
3. Pancada.
4. Silêncio.
5. Uma nota quente.
6. Acordes maiores crescendo com coro.
7. Explosão no final + sinos no inscreva-se.

**Sincronize cada surpresa visual com um som.** Sem isso, a surpresa perde metade da força.

## Narração (`narracao.py`, Kokoro local, grátis)
- **Vozes:**
  - **PT:** `pm_alex`
  - **EN:** `am_michael`
  - Troque com `VIDEO_VOICE`; velocidade com `VIDEO_VOICE_SPEED` (1.0 = padrão do canal).
- `python3 narracao.py <nome>` gera uma fala por legenda e o `narr/<nome>_<lang>_<voz>/timing.json`.
  - A saída `cena k: x1.00 …` mostra o fator de esticão de cada cena.
  - Se algum passar de ~1.05, encurte a fala ou aumente a cena no roteiro.
- `--mix trilha.wav saida.wav` mistura a narração com a trilha. O ducking é adaptativo: a voz fica pelo menos 8 dB acima da música.

### Pronúncia em PT (já corrigido no código, mas saiba por quê)
O espeak entrega o português com vogais americanizadas: `usa→uzæ`, `que→ky`, `cercado→seɾəkado`.
`narracao._fix_pt` converte de volta (`æ→ɐ`, `y→i`, remove `ə`, ditongos `aɪ→aj`).

**Não mexa nas nasais.** Reescrever `eɪŋ→ẽ` piorou, porque "gente" virou "Jotty"; o modelo aprendeu com
a grafia do espeak.

Palavras em inglês no texto em PT ("like", "feed", "app"…) são pronunciadas em inglês. Adicione novas em
`narracao.EN_WORDS`.

Armadilhas de texto:
- "dEle" é lido "de ele": escreva "para Ele".
- Palavra em CAIXA ALTA no inglês pode ser soletrada ou trocada: "I'M IN" saiu "I take him in". Use “I'm in” entre aspas.
- Números saem bem ("7 dias").

### Verificar (obrigatório)
`python3 <skill>/scripts/checar.py voz <arquivo> pt`

O Whisper às vezes erra o que está certo. Antes de mexer no texto, gere a frase isolada e transcreva de
novo. Exemplos de falso alarme: ouviu "light" onde a voz disse "like"; ouviu "lique" quando o "like" ainda
era pronunciado à portuguesa.

## Limites conhecidos
- O timbre do Alex ainda tem leve sotaque, porque o modelo tem pouco treino em PT-BR. A melhora definitiva é a ElevenLabs (o usuário vai pôr créditos).
  - Para plugar, gere os áudios por fala no mesmo esquema de `narr/.../NNN.wav` + `timing.json`.
- Vozes Piper PT-BR (cadu, faber, jeff) estão em `~/tts/piper`. São nativas, mas o usuário preferiu o Alex.
