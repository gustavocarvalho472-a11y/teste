# Ferguson Told Them To Stand By The Manager. They Never Did. — produção (EN)

Roteiro: `../../roteiros/ferguson-ghost-pochettino.md` (EN + PT de validação).

| Arquivo | Função |
|---|---|
| `lines.txt` | Narração em beats (`id|texto`) |
| `tts.py` | Narração grátis com Kokoro ONNX (modelo baixado do GitHub, `/opt/kokoro`), um MP3 por beat + `durations.json` |
| `asr.py` | Transcrição grátis local (sherpa-onnx Whisper base.en, `/opt/asr`) para achar falas e tempos |
| `peek.py` | Folha de contato por tempo (fontes de câmera contínua) |
| `photos.py` / `photo_wait.sh` | Busca de fotos livres no Wikimedia Commons (API com limite 429) |
| `build.py` | Linha do tempo (POOLS, SEQ) → `build/timeline.json` |
| `render.js` | Gráficos quadro a quadro; **para quando as animações terminam** (o `assemble.py` congela o último quadro) |
| `assemble.py` | Cenas + áudio + `.srt` → `out/ferguson-ghost-EN.mp4` |

Refazer: `python3 build.py && node render.js && python3 assemble.py` (ou `--reuse` apagando só `build/seg/<id>.mp4`).

## Fontes de vídeo (`assets/real/`, fora do git; importadas via vidIQ, grátis)

| Arquivo | YouTube ID | Origem | Uso |
|---|---|---|---|
| fergie_line | 8E11U1cGeKU | Sky Sports Retro | Fala de abertura e fecho (0:05–0:20) |
| fergie_speech | HgWvOYMzQHs | Sky Sports Retro | Discurso de 2013: Ferguson, torcida, elenco |
| fergie_final_game | C-dkDqE3Vp8 | Sky Sports Retro | Entrevista pós-jogo 2013 |
| fergie_aljazeera | LJppzglI7Mc | Al Jazeera English | Estátua, Old Trafford, arquivo anos 90, torcida (logo cortado) |
| fergie_first_interview | ZL2_fdnzVxY | upload de terceiro (arquivo 1986) | Ferguson jovem em Old Trafford, torcida anos 80 |
| fergie_itv_dressing | K8iA47dvJyc | ITV Sport | Arquivo anos 90: Ferguson, Class of '92, Cantona, Solskjær jovem |
| fergie_fan | SlVe7S3adTs | vídeo de torcedor | reserva |
| moyes_sacked | izQvIst96BU | AP | Moyes 2013–14 (logo AP cortado) |
| mourinho_greatest | VjnvtIMDphc | Sky Sports PL | Fala do Mourinho, 31/08/2018 (5:38–5:50) |
| mourinho_second | QWi57iPpZHg | upload de terceiro | reserva (versão 2019 da mesma ideia) |
| rangnick_heart | 4zoXQn8-hDM | Sky Sports Retro | Fala do Rangnick, abr/2022 (0:37–0:46) |
| amorim_manager | Z4q80oezi3k | The Independent | Fala do Amorim, 04/01/2026 (0:09–0:23) |
| amorim_rants_sky | M0J-29sXRjw | Sky Sports PL | Amorim em coletivas |
| same_problems_hayters | d0xn8TbSMUY | HaytersTV | Coletivas: Mourinho, Rangnick, Ten Hag, Amorim |
| poch_presser_sky | FEvsyLh_jPk | Sky Sports News | Pochettino, coletiva de despedida da USMNT (recorte central) |
| poch_spurs_presser | 6201MIS_Cdw | BeanymanSports | Pochettino no Tottenham, 2019 (recorte sem legenda) |
| poch_arrival | qBwfvhzAbJQ | The United Forge (fã) | Chegada a Carrington (logo cortado) |
| poch_on_fergie_2019 | lDIa_s6icco | Hoop Headlines | só referência de texto (voz robótica, não usado) |
| lfc_parade_hayters / lfc_parade_4k | 0FgGY9S4bfY / JEMVsk_bKu4 | HaytersTV / Compass Media | Desfile do título do Liverpool, 2025 |

Nenhum vídeo da FIFA. Todo material de arquivo é de terceiros e não licenciado (Sky, ITV e AP são os mais prováveis de reivindicar).

Narration: AI voice (Kokoro, Apache-2.0). Music: AI-generated (reused channel tracks).

## Auditoria de direitos (v2, após a reivindicação da Premier League)

Reivindicação recebida: **"MUN_vs_SWA" — FA Premier League — visual — bloqueio mundial** (0:03–0:19 e 9:58–10:03). As imagens do discurso de despedida do Ferguson são a transmissão oficial do jogo United x Swansea (12/05/2013), mesmo no upload do Sky Sports Retro.

| Fonte | Dono provável | Decisão |
|---|---|---|
| fergie_line, fergie_speech | Premier League (sinal do jogo) | **Removidas** (imagem). A fala agora usa o **áudio gravado por um torcedor na arquibancada** (`fergie_fan`, 1:49–2:04) com fotos animadas |
| fergie_final_game | Premier League (entrevista pós-jogo com painel da PL) | **Removida** |
| poch_spurs_presser | UEFA (coletiva de Champions League) | **Removida** |
| same_problems_hayters 0:39–1:00 e 4:33–4:45 | UEFA (coletivas de Champions/Europa League) | **Trechos removidos** |
| fergie_itv_dressing | ITV | **Removida** (risco alto de Content ID) |
| fergie_aljazeera: inserts de arquivo (treinos anos 90, taças, Ronaldo) | agências/clube | **Removidos**; ficam só as imagens próprias da Al Jazeera (estátua, fachada, torcida, banner) e quadros congelados delas |
| lfc_parade_4k | Compass Media (agência de licenciamento) | **Removida** |
| fergie_first_interview (1986) | provavelmente Granada/ITV | Mantida (única imagem do Ferguson jovem) — **risco médio** |
| coletivas do United (Mourinho, Rangnick, Ten Hag, Amorim) via Sky/HaytersTV/The Independent | clubes / Sky | Mantidas — risco médio (Sky às vezes reivindica uploads próprios) |
| moyes_sacked | AP | Mantida — risco baixo/médio |
| poch_presser_sky | US Soccer / Sky News | Mantida — risco baixo/médio |
| lfc_parade_hayters | HaytersTV | Mantida — risco médio |
| fergie_fan | torcedor | Mantida — gravação própria, não é a transmissão |

Fotos: o Wikimedia Commons bloqueou o IP de saída (429), então as "fotos" animadas são quadros congelados das fontes mantidas (`assets/photos/*.jpg`). Quando o Commons liberar, `photos.py` baixa fotos livres em `assets/photos/cand/`.

**v5 (escolha do usuário):** os trechos do discurso usam **prints** da transmissão de 12/05/2013 (`assets/photos/sp_*.jpg`) como fotos animadas de ~1,4 s, dentro da moldura, com o áudio do torcedor. Risco: o Content ID também compara imagem; conferir subindo como não listado.
