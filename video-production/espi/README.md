# Nobody Understood Why Mourinho Signed Carlos Espí (EN, ~5:30, estilo v3 Cinema + Revista)

Roteiro aprovado pelo dono: doc "Roteiro — Nobody Understood Why Mourinho Signed Carlos Espí" (Claude Docs). Narração em `lines.txt` (Kokoro am_michael).

## Fontes de vídeo (todas do site oficial realmadrid.com, baixadas do MP4 público da página)
| Arquivo | Conteúdo | Uso | Risco |
|---|---|---|---|
| mou_presser_espanyol | Coletiva Mourinho pós-Espanyol (22/08), fala do Espí 8:00–9:38 | 4 falas com áudio original | Médio: painel de patrocinadores da LaLiga ao fundo |
| espi_entrevista | Entrevista RMTV (23/08); abraço Espí × Mourinho 77,4–82,7 s | b-roll | Baixo/médio (câmera do clube) |
| espi_firma | Assinatura com Florentino (23/08) | b-roll | Baixo |
| espi_presentacion | Vídeo de apresentação; só a infância (29–38 s) | b-roll | Baixo (resto é jogo da LaLiga: NÃO usado) |
| espi_debut_fiorentina | Entrevista pós-amistoso | b-roll | Baixo |
| training_nov27 | Treino 27/11 | b-roll | Baixo |
| courtois_mixta | Zona mista, tela dividida com jogo da LaLiga | **só áudio** (59,95–71,3 s) | imagem não usada |
| espi_post_roma | Zona mista com painel da UEFA | **só áudio** (0,15–7,25 s) | imagem não usada |
| mou_presser_celta | Coletiva pós-Celta (21/11): "y Carlos Espí, un jugador de área" 243,25–246,55; "la historia del fútbol…" 285,25–296,6; "ya no, ya no" 868 | 2 falas | Baixo (fundo do clube) |
| espi_presentacion (lances) | gols/dribles 121, 76, 152, 160, 227, 210, 165 s — 0,8–1 s cada | sequência da abertura | **Médio/alto: imagem de transmissão da LaLiga** |
| mou_presser_elche | Coletiva pós-Elche (15/09) | não usado | — |
Print: `assets/photos/web/dazn_*.png` (Playwright, marca-texto aplicado na própria página). Fonte: DAZN, 30/07/2026.
Não usados: todos os "RESUMEN" (melhores momentos = transmissão LaLiga/UEFA).

## Fotos
- Galerias oficiais do Real Madrid (Espanyol, Elche, Celta, apresentação) — `assets/rm/`.
- Pinterest (Endrick, Mourinho, Ancelotti, Gonzalo, Espí no Levante) — `assets/pin/`. Conferidas uma a uma (Arda Güler nº 15 e fotos de outros jogadores descartadas).

## Comandos
```bash
python3 build.py && node gfx2.js build/v3 && BUILD=build/v3 python3 camsheet.py
BUILD=build/v3 JOBS=4 python3 assemble3.py      # --reuse para remontar só o que mudou
```
