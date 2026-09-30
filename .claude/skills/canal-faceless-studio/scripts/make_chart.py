#!/usr/bin/env python3
"""Gera gráficos e cards de texto 1920x1080 (cenas CHART / TEXT_CARD) a partir de um JSON.
Uso: make_chart.py spec.json out.png
spec: {"kind":"bar|line|card", "title":"...", "labels":[...], "values":[...], "unit":"%",
       "source":"Fonte: ...", "text":"(card)", "theme":"dark|light"}"""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

spec = json.load(open(sys.argv[1])); out = sys.argv[2]
dark = spec.get("theme", "dark") == "dark"
bg, fg, ac = ("#0f1720", "#f2f4f7", "#4cc9a4") if dark else ("#faf7f0", "#1b1b1b", "#0b6e4f")
fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=bg)
ax = fig.add_axes([0.08, 0.14, 0.86, 0.66], facecolor=bg)
fig.text(0.08, 0.90, spec.get("title", ""), color=fg, fontsize=40, weight="bold", va="center")

if spec["kind"] == "card":
    ax.axis("off")
    fig.text(0.5, 0.5, spec.get("text", ""), color=fg, fontsize=54, ha="center", va="center", wrap=True)
else:
    labels, vals = spec["labels"], spec["values"]
    if spec["kind"] == "bar":
        bars = ax.bar(labels, vals, color=ac)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v}{spec.get('unit','')}", ha="center", va="bottom", color=fg, fontsize=22)
    else:
        ax.plot(labels, vals, color=ac, linewidth=5, marker="o", markersize=10)
    ax.tick_params(colors=fg, labelsize=22)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(fg)
if spec.get("source"):
    fig.text(0.08, 0.05, spec["source"], color=fg, alpha=0.7, fontsize=18)
fig.savefig(out, facecolor=bg); print("ok:", out)
