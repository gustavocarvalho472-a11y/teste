"""Storyboard como página (publicada como Artifact): um card por cena com quadro renderizado, tempo,
narração, assets (✓/✗) e efeitos.

    python3 storyboard.py      → saida/storyboard/index.html + saida/storyboard/quadros/<id>.jpg

Rode de novo depois de salvar assets e republique o artefato: os cards passam a mostrar a imagem real.
"""
import html
import os

from PIL import Image

import montar
import timeline
from montar import find, DESC, FOLDERS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "saida", "storyboard")


def assets_of(b):
    out = []
    for s in b["shots"]:
        a, o = (s, {}) if isinstance(s, str) else s
        for x in [a] + o.get("grid", []) + o.get("split", []) + o.get("logos", []):
            if (x.split("_")[0] in FOLDERS or x.startswith("gfx:")) and x not in out:
                out.append(x)
    return out


def fx_of(b):
    bits = []
    if b.get("txt"):
        bits.append(f'texto “{b["txt"][0]}”')
    if b.get("hl"):
        bits.append(f'destaque “{b["hl"]}”')
    if b.get("sfx"):
        bits.append("sfx " + b["sfx"])
    if b.get("mus"):
        bits.append("música " + b["mus"])
    return bits


def tc(t):
    return f"{int(t) // 60}:{int(t) % 60:02d}"


def main():
    tm, blocks, shots, total = timeline.load()
    os.makedirs(os.path.join(OUT, "quadros"), exist_ok=True)
    cards, n_ok, n_all, acts = [], 0, 0, []
    for b, bt in zip(timeline.B, blocks):
        t_mid = min(bt["start"] + 0.55 * max(0.6, bt["end"] - bt["start"]), total - 0.1)
        im = Image.fromarray(montar.frame(t_mid, int(t_mid * 30), shots)).resize((960, 540), Image.LANCZOS)
        im.save(os.path.join(OUT, "quadros", f'{b["id"]}.jpg'), quality=80)
        chips, missing = [], 0
        for a in assets_of(b):
            if a.startswith("gfx:"):
                chips.append(f'<li class="chip gfx" title="gerado em código">{html.escape(a[4:])}</li>')
                continue
            ok = find(a) is not None
            n_all += 1
            n_ok += ok
            missing += not ok
            tip = html.escape(os.path.basename(find(a)) if ok else DESC.get(a, ""))
            chips.append(f'<li class="chip {"ok" if ok else "miss"}" title="{tip}">'
                         f'<span aria-hidden="true">{"✓" if ok else "✗"}</span>{a}</li>')
        if b.get("ato"):
            acts.append((b["ato"], bt["start"]))
            cards.append(f'<h2 class="act" id="ato-{len(acts)}"><span>{tc(bt["start"])}</span>'
                         f'{html.escape(b["ato"])}</h2>')
        pun = f'<span class="pun">Punição {b["pun"]}/5</span>' if b.get("pun") else ""
        fx = "".join(f"<li>{html.escape(x)}</li>" for x in fx_of(b))
        cards.append(f'''<article class="card" data-missing="{missing}">
  <figure><img src="quadros/{b["id"]}.jpg" alt="Quadro da cena {b["id"]}" loading="lazy" width="960" height="540">
    <figcaption><b>{b["id"]}</b><span>{tc(bt["start"])}</span>{pun}</figcaption></figure>
  <p class="fala">{html.escape(b["fala"]) or '<i>sem fala</i>'}</p>
  <ul class="chips">{"".join(chips)}</ul>
  {f'<ul class="fx">{fx}</ul>' if fx else ""}
</article>''')
    nav = "".join(f'<a href="#ato-{i + 1}">{html.escape(a)}</a>' for i, (a, _) in enumerate(acts))
    page = TEMPLATE.format(cards="\n".join(cards), nav=nav, ok=n_ok, all=n_all, pct=round(100 * n_ok / n_all),
                           dur=tc(total), cenas=len(blocks))
    open(os.path.join(OUT, "index.html"), "w").write(page)
    print(os.path.join(OUT, "index.html"), f"assets {n_ok}/{n_all}")


TEMPLATE = """<title>Storyboard Mbappé × China</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;600&family=JetBrains+Mono:wght@500&display=swap">
<style>
/* Sala de edição: grade de cards 16:9 por ato; amarelo-legenda e vermelho-carimbo vêm do próprio vídeo */
:root {{
  --bg: #f3f1ec; --panel: #ffffff; --fg: #1b1a18; --muted: #6b665d; --line: #dcd7cc;
  --yellow: #c99a00; --red: #c8221c; --ok: #1d7a43; --chip: #ece8de;
  --display: "Anton", "Impact", "Arial Narrow", sans-serif;
  --body: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #131210; --panel: #1d1b18; --fg: #efebe3; --muted: #9c968b; --line: #34312c;
  --yellow: #ffd600; --red: #ff4b40; --ok: #4fc47f; --chip: #2a2723; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #131210; --panel: #1d1b18; --fg: #efebe3; --muted: #9c968b; --line: #34312c;
  --yellow: #ffd600; --red: #ff4b40; --ok: #4fc47f; --chip: #2a2723; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.5 var(--body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
.wrap {{ max-width: 1280px; margin: 0 auto; padding-block: 28px 64px; }}
header {{ display: grid; gap: 14px; margin-bottom: 8px; }}
h1 {{ font: 400 clamp(34px, 6vw, 64px)/1 var(--display); letter-spacing: .01em; margin: 0; text-wrap: balance; }}
h1 em {{ font-style: normal; color: var(--red); }}
.meta {{ display: flex; flex-wrap: wrap; gap: 8px 22px; color: var(--muted); font: 500 13px var(--mono); }}
.meta b {{ color: var(--fg); font-weight: 500; }}
.bar {{ height: 6px; background: var(--chip); border-radius: 3px; overflow: hidden; max-width: 420px; }}
.bar i {{ display: block; height: 100%; width: {pct}%; background: var(--ok); }}
.tools {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg);
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; padding-block: 12px; border-bottom: 1px solid var(--line); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }}
.tools nav {{ display: flex; flex-wrap: wrap; gap: 6px; min-width: 0; }}
.tools a {{ color: var(--fg); text-decoration: none; font-size: 13px; padding: 4px 10px; border: 1px solid var(--line); border-radius: 999px; }}
.tools a:hover, .tools a:focus-visible {{ border-color: var(--fg); outline: none; }}
.tools label {{ margin-left: auto; display: flex; gap: 8px; align-items: center; font-size: 13px; cursor: pointer; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 380px), 1fr)); gap: 22px 20px; margin-top: 18px; }}
h2.act {{ grid-column: 1 / -1; font: 400 28px/1.1 var(--display); margin: 26px 0 0; display: flex; gap: 14px; align-items: baseline;
  border-top: 3px solid var(--red); padding-top: 10px; scroll-margin-top: 70px; }}
h2.act span {{ font: 500 14px var(--mono); color: var(--red); }}
.card {{ display: grid; gap: 10px; align-content: start; min-width: 0; }}
figure {{ margin: 0; position: relative; }}
figure img {{ display: block; width: 100%; height: auto; aspect-ratio: 16 / 9; border-radius: 4px; background: #000; }}
figcaption {{ position: absolute; left: 8px; top: 8px; display: flex; gap: 6px; font: 500 12px var(--mono); }}
figcaption > * {{ background: rgba(0,0,0,.78); color: #fff; padding: 3px 7px; border-radius: 3px; }}
figcaption b {{ color: #ffd600; font-weight: 500; }}
figcaption .pun {{ background: #c8221c; }}
.fala {{ margin: 0; font-size: 15px; }}
.fala i {{ color: var(--muted); }}
.chips, .fx {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px; }}
.chip {{ font: 500 12px var(--mono); padding: 3px 8px; border-radius: 3px; background: var(--chip); display: flex; gap: 5px; }}
.chip.ok {{ color: var(--ok); }}
.chip.miss {{ color: var(--red); }}
.chip.gfx {{ color: var(--muted); }}
.fx li {{ font-size: 12px; color: var(--muted); }}
.fx li + li::before {{ content: "· "; }}
body.only-missing .card[data-missing="0"] {{ display: none; }}
@media (prefers-reduced-motion: no-preference) {{ figure img {{ transition: transform .2s; }} figure img:hover {{ transform: scale(1.015); }} }}
</style>
<div class="wrap">
<header>
  <h1>Mbappé <em>OFENDEU</em> a China · storyboard</h1>
  <div class="meta"><span><b>{cenas}</b> cenas</span><span>duração <b>{dur}</b></span><span>assets prontos <b>{ok}/{all}</b></span></div>
  <div class="bar" role="img" aria-label="{pct}% dos assets prontos"><i></i></div>
</header>
<div class="tools">
  <nav aria-label="Atos">{nav}</nav>
  <label for="falta"><input type="checkbox" id="falta"> só cenas com asset faltando</label>
</div>
<main class="grid">
{cards}
</main>
</div>
<script>
const box = document.getElementById("falta");
const apply = () => document.body.classList.toggle("only-missing", box.checked);
try {{ box.checked = localStorage.getItem("falta") === "1"; }} catch (e) {{}}
apply();
box.addEventListener("change", () => {{ apply(); try {{ localStorage.setItem("falta", box.checked ? "1" : "0"); }} catch (e) {{}} }});
</script>
"""


if __name__ == "__main__":
    main()
