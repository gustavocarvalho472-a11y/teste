"""Roteiro bilíngue (PT | EN) cena a cena como página para Artifact → saida/roteiro/index.html"""
import html
import json
import os

os.environ["VIDEO_LANG"] = "pt"
from roteiro import B                      # noqa: E402  (versão PT; o EN vem dos overrides)
from roteiro_en import EN, TITLE as TITLE_EN  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DESC_FILE = os.path.join(HERE, "montar.py")
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("m", DESC_FILE)
src = open(DESC_FILE).read()
DESC = eval(src[src.index("DESC = {") + 7: src.index("}\n", src.index("DESC = {")) + 1])
GFX = {"linha_tempo": "Gráfico: linha do tempo 1949–1976", "contadores": "Gráfico: contadores de seguidores",
       "valor_migu": "Gráfico: US$ 400–465 mi (Migu)", "pizza": "Gráfico: 10–15% do merchandising",
       "mito": "Gráfico: carimbo MITO sobre “900 milhões”", "nao_perdoado": "Gráfico: 不接受，不原谅",
       "endscreen": "Tela final: vídeo Nike → On + inscreva-se"}
EXTRA = {"FOT_11": "Hasteamento da bandeira, Praça da Paz Celestial", "FOT_13": "Guarda de honra do Exército",
         "FOT_14": "Xi Jinping", "FOT_15": "Multidão em rua de Pequim", "FOT_16": "Sessão do Congresso Nacional do Povo",
         "FOT_17": "Helicópteros formando “70” no desfile de 2019", "FOT_18": "Soldados com baionetas",
         "FOT_19": "Caças J-20 no desfile de 2019", "PRT_16": "Tweet do Madrid Zone visto em chinês"}


def visual(s):
    a, o = (s, {}) if isinstance(s, str) else s
    if a.startswith("gfx:"):
        return GFX.get(a[4:], a)
    if a.startswith("title:"):
        return "Cartela de título"
    if a == "black":
        return "Tela preta"
    ids = o.get("grid") or o.get("split") or o.get("logos") or [a]
    return " + ".join(EXTRA.get(i, DESC.get(i, i)) for i in ids)


tm = json.load(open(os.path.join(HERE, "build", "en", "timing.json")))
times = {b["id"]: b["start"] for b in tm["blocks"]}
total = tm["total"]
tc = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"
esc = html.escape

rows, toc, n_act = [], [], 0
for b in B:
    en = EN.get(b["id"], {})
    if b.get("ato"):
        n_act += 1
        t = times.get(b["id"], 0)
        toc.append(f'<a href="#ato{n_act}"><span>{tc(t)}</span>{esc(b["ato"])}</a>')
        rows.append(f'<h2 id="ato{n_act}"><span class="tc">{tc(t)}</span>{esc(b["ato"])}'
                    f'<span class="en-act">{esc(en.get("ato", ""))}</span></h2>')
    if not b["fala"]:
        if b["id"] == "TITULO":
            rows.append(f'<div class="card"><div class="meta"><b>{b["id"]}</b><span>{tc(times.get(b["id"], 0))}</span></div>'
                        f'<div class="cols"><p class="txt">Cartela: <em>O MEME QUE A CHINA NÃO PERDOOU</em></p>'
                        f'<p class="txt" lang="en">Title card: <em>{esc(TITLE_EN)}</em></p></div></div>')
        continue
    txt_pt = b.get("txt")
    txt_en = en.get("txt")
    onscreen = ""
    if txt_pt or txt_en:
        onscreen = (f'<div class="cols"><p class="txt">Na tela: <em>{esc(txt_pt[0] if txt_pt else "")}</em></p>'
                    f'<p class="txt" lang="en">On screen: <em>{esc(txt_en[0] if txt_en else "")}</em></p></div>')
    pun = f'<span class="pun">Punição {b["pun"]}/5</span>' if b.get("pun") else ""
    vis = " → ".join(visual(s) for s in b["shots"])
    rows.append(f'''<div class="card">
  <div class="meta"><b>{b["id"]}</b><span>{tc(times.get(b["id"], 0))}</span>{pun}</div>
  <div class="cols"><p class="pt">{esc(b["fala"])}</p><p class="en" lang="en">{esc(en.get("fala", ""))}</p></div>
  {onscreen}
  <p class="vis">{esc(vis)}</p>
</div>''')

SOURCES = [
    ("TIME — What to know", "https://time.com/article/2026/10/28/kylian-mbappe-china-mao-zedong-dictator-meme-backlash-controversy-explainer/"),
    ("CNBC — sponsors cut ties", "https://www.cnbc.com/2026/10/28/china-mbappe-football-sponsor-meme-controversy.html"),
    ("Al Jazeera — Mbappé apologises", "https://www.aljazeera.com/sports/2026/10/27/kylian-mbappe-apologises-after-dictator-comment-angers-chinese-fans"),
    ("Swissinfo/Bloomberg — On shares", "https://www.swissinfo.ch/eng/mbapp%c3%a9-apologizes-for-perceived-mao-insult-after-china-backlash/92283541"),
    ("Africa Soccer (Le Monde) — €6,7 mi", "https://africasoccer.com/kylian-mbappe-faces-e6-7m-sponsorship-blow-after-china-controversy/"),
    ("Stevivor — FC Online China", "https://stevivor.com/news/fc-online-china-removes-mbappe-promo-material-and-plans-a-game-update/"),
    ("Africa Soccer — Migu muda a grade", "https://africasoccer.com/mbappe-fallout-reaches-la-liga-as-chinas-migu-changes-weekend-coverage/"),
    ("Africa Soccer — deputado dos EUA", "https://africasoccer.com/?p=645964"),
    ("ESPN — Özil 2019", "https://africa.espn.com/football/arsenal/story/4013387/ozil-row-sees-arsenal-manchester-city-pulled-from-china-state-tv"),
    ("WITF/AP — NBA 2019", "https://witf.org/2019/10/08/chinese-state-tv-suspends-2-nba-preseason-game-broadcasts"),
]
src_html = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{esc(n)}</a></li>' for n, u in SOURCES)

page = f"""<title>Roteiro Mbappé × China</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=JetBrains+Mono:wght@500&display=swap">
<style>
/* Roteiro de leitura: coluna PT | EN por cena; cabeçalho de ato com régua vermelha (identidade do vídeo) */
:root {{
  --bg: #f4f2ed; --panel: #ffffff; --fg: #1c1b19; --muted: #6a655c; --line: #ddd8cd;
  --red: #c4221c; --en: #1f4f8f; --chip: #ece8de;
  --display: "Anton", "Impact", "Arial Narrow", sans-serif;
  --body: "Source Serif 4", Georgia, "Times New Roman", serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #141311; --panel: #1d1b18; --fg: #ece8e0; --muted: #9b958a; --line: #34312c;
  --red: #ff5348; --en: #8fb6ff; --chip: #2a2723; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #141311; --panel: #1d1b18; --fg: #ece8e0; --muted: #9b958a; --line: #34312c;
  --red: #ff5348; --en: #8fb6ff; --chip: #2a2723; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 17px/1.55 var(--body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
.wrap {{ max-width: 1080px; margin: 0 auto; padding-block: 32px 72px; display: grid; gap: 18px; }}
header {{ display: grid; gap: 10px; }}
h1 {{ font: 400 clamp(32px, 6vw, 58px)/1.02 var(--display); margin: 0; text-wrap: balance; }}
h1 em {{ font-style: normal; color: var(--red); }}
.sub {{ margin: 0; color: var(--muted); font-size: 16px; max-width: 70ch; }}
.facts {{ display: flex; flex-wrap: wrap; gap: 6px 20px; font: 500 13px var(--mono); color: var(--muted); }}
.facts b {{ color: var(--fg); font-weight: 500; }}
nav {{ display: flex; flex-wrap: wrap; gap: 6px; }}
nav a {{ font: 500 12px var(--mono); color: var(--fg); text-decoration: none; border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; display: flex; gap: 6px; }}
nav a span {{ color: var(--red); }}
nav a:hover, nav a:focus-visible {{ border-color: var(--fg); outline: none; }}
.legend {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; font: 500 12px var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); border-bottom: 1px solid var(--line); padding-bottom: 6px; }}
.legend span:last-child {{ color: var(--en); }}
h2 {{ font: 400 26px/1.15 var(--display); margin: 26px 0 0; padding-top: 10px; border-top: 3px solid var(--red); display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: baseline; scroll-margin-top: 16px; }}
h2 .tc {{ font: 500 14px var(--mono); color: var(--red); }}
h2 .en-act {{ font: 400 18px var(--display); color: var(--en); }}
.card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 14px 18px; display: grid; gap: 8px; }}
.meta {{ display: flex; gap: 10px; align-items: center; font: 500 12px var(--mono); color: var(--muted); }}
.meta b {{ color: var(--fg); font-weight: 500; background: var(--chip); padding: 2px 7px; border-radius: 3px; }}
.pun {{ color: #fff; background: var(--red); padding: 2px 7px; border-radius: 3px; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.cols > * {{ min-width: 0; margin: 0; }}
.en {{ color: var(--en); }}
.txt {{ font-size: 14px; color: var(--muted); }}
.txt em {{ font-style: normal; font-weight: 600; color: var(--fg); }}
.vis {{ margin: 0; font: 500 12px/1.5 var(--mono); color: var(--muted); }}
.vis::before {{ content: "Visual: "; color: var(--fg); }}
footer {{ margin-top: 28px; border-top: 1px solid var(--line); padding-top: 14px; display: grid; gap: 8px; }}
footer h3 {{ font: 400 22px var(--display); margin: 0; }}
footer ul {{ margin: 0; padding-left: 20px; columns: 2 280px; font-size: 15px; }}
footer a {{ color: var(--en); }}
@media (max-width: 640px) {{ .cols, .legend {{ grid-template-columns: 1fr; gap: 8px; }} .legend span:last-child {{ display: none; }} }}
</style>
<div class="wrap">
<header>
  <h1>Mbappé <em>OFENDEU</em> a China</h1>
  <p class="sub">Roteiro completo, cena a cena, em português (versão de validação) e em inglês (versão publicada). Os tempos são da versão em inglês.</p>
  <div class="facts"><span>duração EN <b>{tc(total)}</b></span><span>cenas <b>{sum(1 for b in B if b["fala"])}</b></span><span>atos <b>{n_act}</b></span><span>título EN <b>Mbappé OFFENDED China — and China Took Revenge</b></span></div>
  <nav aria-label="Atos">{"".join(toc)}</nav>
</header>
<div class="legend"><span>Português</span><span>English</span></div>
{"".join(rows)}
<footer>
  <h3>Fontes</h3>
  <ul>{src_html}</ul>
</footer>
</div>
"""
os.makedirs(os.path.join(HERE, "saida", "roteiro"), exist_ok=True)
open(os.path.join(HERE, "saida", "roteiro", "index.html"), "w").write(page)
print("ok", len(page))
