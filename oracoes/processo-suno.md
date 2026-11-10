# Processo de áudio de oração no Suno

## Regra para não deixar a voz metálica
- Cada sequência: 1 áudio inicial (`speech-create`, ~5 min de fala) + no máximo 2 emendas normais + 1 fechamento curto (com o Amém).
- A partir da 3ª emenda a voz acumula artefatos (fica metálica/robotizada). Medido no áudio de 09/11: a planicidade espectral nos trechos com fala subiu de ~0,02 para 0,05–0,07 a partir da 3ª emenda.
- Texto de cada emenda: ~120–170 palavras. Textos maiores tendem a pular frases.
- Emendar 2–3 s depois da última palavra (conferir com `audio-lyrics-alignment`), nunca colado no início de uma palavra.
- Não emendar a partir de uma música já juntada (`full-song`): degrada desde o início.
- Parafrasear versículos famosos que viraram letra de música (ex.: Salmo 121, Isaías 40:31); o Suno barra como "copyrighted".
- A avaliação "de ouvido" do Suno (`audio-listen`) não detecta o metálico; medir com ffmpeg `aspectralstats` (flatness) nos trechos com fala.

## Resultado por sequência
- ~10 a 12 min de áudio limpo = 1 download.

## Oração da Noite – Salmo 128 e ansiedade (10/11)
- Suno: https://suno.com/song/71da120c-6ee2-41fa-b2be-c12d02f091e9
- Partes: Salmo 128 + Mateus 11:28 · Filipenses 4:6-7 + 1 Pedro 5:7 · Mateus 6:25-34 + João 14:27 · 2 Timóteo 1:7 + Amém
- Fala vai até 10:01 (Amém); arquivo final cortado em 10:18 com fade.
