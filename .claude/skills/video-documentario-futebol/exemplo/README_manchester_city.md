# Manchester City's 115 Charges — produção do vídeo (EN)

Pipeline que gera o vídeo completo a partir do roteiro em `../roteiros/`.

| Arquivo | Função |
|---|---|
| `build.py` | Roteiro cena a cena (texto da narração + visual) e linha do tempo sincronizada com a narração → `build/timeline.json` |
| `render.js` | Pacote gráfico de estúdio (HTML/CSS) renderizado quadro a quadro com Chromium |
| `assemble.py` | Codifica as cenas, trata o b-roll, mixa narração + trilha + efeitos sonoros e gera o MP4 e o `.srt` |
| `assets/vo`, `assets/music` | Narração (8 capítulos) e 3 trilhas, geradas por IA |
| `assets/stock_manifest.tsv` | Clipes de banco usados (Pexels) — os arquivos em si não ficam no git |

Para refazer: `python3 build.py && node render.js && python3 assemble.py` (saída em `out/`).
Para baixar o b-roll de novo: `https://videos.pexels.com/video-files/<coluna 2>.mp4` → `assets/stock/<coluna 1>.mp4`.

## Créditos de imagem (colar na descrição do YouTube)

Footage via Pexels:
- Necip Duman — https://www.pexels.com/video/excited-soccer-stadium-crowd-cheering-at-match-34605059/
- Tio Nazih — https://www.pexels.com/video/football-match-on-stadium-11918917/
- Luis Quintero — https://www.pexels.com/video/soccer-players-are-playing-on-the-field-15462750/
- Luis Quintero — https://www.pexels.com/video/football-players-trying-to-score-a-goal-during-a-match-15448985/
- K — https://www.pexels.com/video/aerial-view-of-a-soccer-field-at-night-2249402/
- Tima Miroshnichenko — https://www.pexels.com/video/drone-footage-of-a-football-field-6079615/
- Fábio Reis de Abreu — https://www.pexels.com/video/person-with-laptop-in-darkness-13375774/
- Matias Mango — https://www.pexels.com/video/a-man-programming-his-laptop-6330778/
- Thirdman — https://www.pexels.com/video/close-up-video-of-a-person-signing-a-document-8471105/
- Mikhail Nilov — https://www.pexels.com/video/people-sitting-beside-wooden-table-8847938/
- Aaron Hairston — https://www.pexels.com/video/porto-aerial-19909834/
- Dima Krivoy — https://www.pexels.com/video/blue-colored-cables-1085656/
- RDNE Stock project — https://www.pexels.com/video/a-keyboard-with-backlight-7914768/
- Mikhail Nilov — https://www.pexels.com/video/a-person-typing-on-a-keyboard-7534237/
- Sergei Skrynnik — https://www.pexels.com/video/man-walking-on-sidewalk-at-night-11839713/
- Aaron Hairston — https://www.pexels.com/video/lisbon-aerial-19909760/
- HTJ Media Advertising — https://www.pexels.com/video/the-front-of-a-large-building-with-columns-28122932/
- Kindel Media — https://www.pexels.com/video/close-up-of-handcuffed-hands-7773315/
- Paice Street — https://www.pexels.com/video/a-computer-hard-drive-part-spinning-in-operation-3289546/
- Glenn Langhorst — https://www.pexels.com/video/clear-sky-over-skyscrapers-and-harbor-11336420/
- Ming Z — https://www.pexels.com/video/illuminated-city-at-night-13176774/
- Jack Todhunter — https://www.pexels.com/video/westminster-17859923/
- Florian Delée — https://www.pexels.com/video/aerial-view-of-the-city-20046742/
- MART PRODUCTION — https://www.pexels.com/video/architectural-design-of-a-modern-building-7317314/
- Pixabay — https://www.pexels.com/video/counting-money-855388/
- Kampus Production — https://www.pexels.com/video/businessmen-shaking-hands-8426327/
- Abdul Raheem — https://www.pexels.com/video/empty-football-stadium-with-colorful-seats-28598596/
- C Sherives — https://www.pexels.com/video/aerial-cityscape-of-manchester-10883708/
- RDNE Stock project — https://www.pexels.com/video/a-cabinet-of-trophies-8499699/
- Dmytro Glazunov — https://www.pexels.com/video/a-person-walking-down-a-hallway-3988278/

Narration and music: AI-generated. Graphics: illustrative recreations.
Based on reporting by Football Leaks / European Investigative Collaborations (EIC) / Der Spiegel.

## Fontes de imagem real (v2 — takes de 3–5 s)

Os takes reais vêm destas reportagens do YouTube (baixadas para `assets/real/`, fora do git). `shots.py` detecta os planos de cada uma e `build.py` (POOLS / SCENE_POOLS) define qual tema entra em cada trecho da narração.

| Arquivo | YouTube ID | Origem |
|---|---|---|
| city_bbc_long | m_l52IF6H0Q | BBC News |
| rui_trial_reuters | PCMMXsXOk5U | Reuters |
| city_pep_official | W4NnL8DbkcY | Man City (canal oficial) |
| city_ban_itv | JYn0zYNBezU | ITV News |
| city_stage23 / city_parade23 / city_parade18 / city_parade22 | bWTidCmiNEU / z66_IMQl1i4 / Vt6T_5G7vBg / yu5ShU0EMY0 | AFP |
| neymar_present / infantino_afp | 7tyJQ873_fc / -XYR3CrLr10 | AFP |
| ronaldo_court_ap / mourinho_court | vvXBIdxxyY4 / D6cgvtzieC8 | AP Archive |
| mansour_goal | MbH5Fjlftus | upload de terceiro |
| twente_fans | SDs4EFaBaoc | FC Twente (canal oficial) |
| abudhabi_drone | k8oS1URc_yk | Travel Beyond Maps |
| pep_furious (abertura, com áudio original) | 6I302sgnTyE | coletiva pós-final da FA Cup 2019 |

Esse material é de terceiros e não está licenciado: ver os avisos de direitos no plano de edição.
