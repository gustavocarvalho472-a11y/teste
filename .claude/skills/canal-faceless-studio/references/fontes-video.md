# Fontes de vídeo livre

Sempre registrar em `assets/credits.csv` (o `find_clips.py download` faz isso). Licença incerta = não usar.

## Óbvios (qualidade alta, licença simples)
| Site | Chave | Licença | Bom para |
|---|---|---|---|
| Pexels Videos | `PEXELS_API_KEY` (grátis) | Pexels License, uso comercial, sem atribuição | cidades, escritórios, dinheiro, natureza |
| Pixabay Videos | `PIXABAY_API_KEY` (grátis) | Pixabay Content License | b-roll genérico, animações |
| Coverr | não (manual) | Coverr License | b-roll cinematográfico, tech |
| Mixkit | não (manual) | Mixkit License | b-roll e trilhas |

## Não óbvios (mais distintivos — evitam o "visual de todo canal")
| Site | Chave | Licença | Bom para |
|---|---|---|---|
| Internet Archive (Prelinger, opensource_movies) | não | domínio público em geral (checar item) | arquivo histórico, filmes educativos, propaganda antiga, economia do séc. XX |
| Wikimedia Commons | não | CC / domínio público (autor+licença vêm na API) | eventos reais, políticos, bolsas, fábricas, documentários |
| NASA Image & Video Library (images.nasa.gov) | não | domínio público | espaço, Terra à noite, tecnologia |
| Library of Congress (loc.gov/film-and-videos) | não | vários, checar direitos | história dos EUA, Grande Depressão, guerras |
| NOAA / USGS / USDA (YouTube e sites .gov) | não | governo dos EUA, domínio público | clima, agricultura, portos, commodities |
| European Parliament / Comissão Europeia (audiovisual) | não | reuso livre com crédito | política econômica da UE, sessões |
| Europeana | não | varia por item (filtrar por "free reuse") | história europeia |
| Wellcome Collection | não | CC-BY / PD | saúde, ciência |
| Videezy / Videvo | não | **varia por clipe — checar cada um** | b-roll e motion graphics |
| Mazwai, Life of Vids | não | CC0/CC-BY | b-roll autoral |
| Vimeo com filtro Creative Commons | não | por vídeo | documentários curtos |
| Open Government (data.gov, gov.uk, planalto/Agência Brasil) | não | domínio público / CC | pronunciamentos, obras, indicadores |

## Estratégia de busca
- Buscar em inglês, termos concretos ("container port aerial", "trading floor 1980s"), não abstratos ("inflation").
- Para conceitos abstratos: usar cena CHART/TEXT_CARD ou metáfora visual (padaria, supermercado, preço na prateleira).
- Misturar: ~50% stock/arquivo, ~30% gráficos/mapas, ~20% imagens IA — evita cara de "banco de imagem" e reduz créditos de IA.
- Preferir 1080p+, paisagem, sem marca d'água, sem pessoas reconhecíveis fora de contexto editorial.
- Material de arquivo/notícia (CNBC, TV) **não** é livre, mesmo estando no Archive — só usar itens com licença/domínio público claros.

## Seleção automática pelo Claude
1. `find_clips.py search scenes.json > candidates.json`
2. Claude lê os candidatos e escolhe 1 por cena: duração ≥ cena, título/tags coerentes com a narração, licença clara, variedade entre cenas (não repetir a mesma fonte/plano em sequência).
3. Se possível, baixar a thumbnail (`preview`) e conferir visualmente antes de decidir.
4. Gravar `selection.json` e rodar `find_clips.py download selection.json assets/`.
5. Mostrar ao usuário uma tabela cena → clipe escolhido (+ 1 alternativa) para aprovar só as exceções.
