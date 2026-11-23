# Arteta Tried To Save Vinicius — produção (EN)

Roteiro: `../../roteiros/vinicius-arteta-tried-to-save.md` (PT v4 aprovado). Narração em inglês: `lines.txt` (38 beats).

| Arquivo | Função |
|---|---|
| `lines.txt` | Narração em beats (`id|texto`) |
| `tts.py` | Kokoro ONNX (`am_michael`), dicionário de pronúncia (Ar-tetta, Shahbee, Jee-rona, Vee-ya-ray-al…) |
| `asr.py` | Transcrição local Whisper small multilíngue (`/opt/asr/sherpa-onnx-whisper-small`), `asr.py arquivo es|en janela [início fim]` |
| `peek.py` | Folha de contato por tempo |
| `photos.py` | Busca no Commons pelo HTML (a API e as imagens grandes deram 429 neste IP; não foi usado no vídeo) |
| `build.py` | Linha do tempo → `build/timeline.json`; `clips_extra.json` liga falas achadas depois (senão vira cartela de citação) |
| `render.js` / `frame.js` / `assemble.py` | Gráficos, moldura e montagem final → `out/vinicius-arteta-EN.mp4` + `.srt` |

## Fontes (`assets/real/`, fora do git; importadas pelo vidIQ, grátis)

| Arquivo | YouTube ID | Origem | Uso | Risco |
|---|---|---|---|---|
| arteta_girona | QDCU0XTNTEs | vídeo de celular na zona mista (vlogger) | "When is Vini joining?" / "Thank you so much" (236.3–241.9) | baixo |
| arteta_respect | I1mqieNxlHM | coletiva do Arsenal (vertical, legenda queimada → recorte + fundo desfocado) | "respect and commitment" (32.9–38.3) | médio |
| mou_presser_sevilla | hqyUWWzX6lI | AS TV, coletiva no Real Madrid (recorte tira o logo) | "Si soy yo en su lugar…" (781–811) + b-roll | médio |
| mou_presser_aug25 | MnRXGhjkDkA | Real Madrid TV, coletiva 25/08/2026 | "intentando que Vini tenga más control emocional…" (545–562) | médio |
| xabi_supercopa_pre | uVvssXBRGIc | canal de comentário; só o ÁUDIO da coletiva do Xabi (imagem = quadros do Xabi) | "es imprescindible la presión de todos…" (485.6–503) | médio |
| xabi_presentation | rn-MH7k4Oiw | AS TV, coletiva da apresentação (recorte tira o logo) | b-roll do Xabi | médio |
| vini_booed_betis | 5Sa6sES_7E4 | Blancology, imagem da arquibancada (recorte tira logo e legendas) | b-roll do Vini | médio |
| ars_parade_fans | b3cTLkpfKIE | Beanyman Sports, desfile do título (recorte tira o logo) | b-roll do Arsenal | baixo-médio |
| diomande_signing / diomande_words | CI7IjIc6W2E / XQopu_MLZ28 | AS TV (imagens do Real Madrid TV) | b-roll do Diomande | médio |
| racism_fans | 4Z1zvS9D-tM | NBC News NOW (rua, Bernabéu, entrevistas) | b-roll Madri / racismo | médio |
| mou_chiringuito | V13ajaL0WCI | El Chiringuito (comentário) | procurado "no lo pedí"; se não achar, cartela | — |

Sem imagem de transmissão de LaLiga, Champions, Premier League, Mundial ou Supercopa. Coletiva da UEFA ("só o escudo é intocável") e do Mundial de Clubes ("os onze defendem") entram só como texto.
"Fotos" do vídeo = quadros congelados das fontes acima, animados. Nenhuma foto do Commons (bloqueado por 429).

Narration: AI voice (Kokoro, Apache-2.0). Music: AI-generated (faixas do canal reaproveitadas).
