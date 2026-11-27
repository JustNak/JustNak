"""Render the language-mix card from public GitHub data.

Counts bytes per language across JustNak's public, non-fork repositories
(excluding this profile repo) and labels the card with the month it was run.
Run by hand; there is no scheduled workflow. Uses only the unauthenticated
public API, so private repositories never leak into the numbers.
"""
from __future__ import annotations

import json
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

from render_profile import DARK as DARK_BASE
from render_profile import FULL, LIGHT as LIGHT_BASE
from html import escape

from render_profile import FONT, MONO, card, svg, text

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER = "JustNak"

DARK = {**DARK_BASE, "ramp": ["#e07a5f", "#d98e72", "#c9a08b", "#b8a18f", "#99897a", "#776b60"]}
LIGHT = {**LIGHT_BASE, "ramp": ["#b4441f", "#cc6a44", "#dc8e6d", "#e4b29a", "#cdb8a4", "#a99a88"]}


def api(path: str):
    req = urllib.request.Request(
        f"https://api.github.com/{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "justnak-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def languages_svg(theme: dict, langs: list[tuple[str, int]], month: str) -> str:
    total = sum(n for _, n in langs) or 1
    h = 132
    bar_x, bar_y, bar_w, bar_h, gap = 36, 62, FULL - 72, 12, 2
    inner = bar_w - gap * (len(langs) - 1)
    segments, legend = [], []
    cursor = bar_x
    col = bar_w / len(langs)
    for i, (name, n) in enumerate(langs):
        colour = theme["ramp"][i % len(theme["ramp"])]
        width = max(5.0, inner * n / total)
        segments.append(
            f'  <rect x="{cursor:.1f}" y="{bar_y}" width="{width:.1f}" height="{bar_h}" '
            f'rx="3" fill="{colour}"/>'
        )
        cursor += width + gap
        x = bar_x + i * col
        legend.append(f'  <circle cx="{x + 4}" cy="{102}" r="3.6" fill="{colour}"/>')
        legend.append(
            f'  <text x="{x + 16}" y="107" font-family="{escape(FONT)}" font-size="14" fill="{theme["text"]}">'
            f'{escape(name)}<tspan dx="8" font-family="{escape(MONO)}" font-size="11" fill="{theme["muted"]}">'
            f'{n / total * 100:.1f}%</tspan></text>'
        )
    body = "\n".join([
        card(0, FULL, h, theme),
        text(36, 40, "LANGUAGES", 11, theme["accent"], family=MONO, spacing=1.6),
        text(FULL - 40, 40, f"PUBLIC REPOS · BY BYTES · AS OF {month.upper()}", 11, theme["faint"],
             family=MONO, anchor="end", spacing=1.2),
        *segments,
        *legend,
    ])
    return svg(FULL, h, f"Languages across public repositories, as of {month}", body)


def main() -> None:
    repos = [
        r["name"] for r in api(f"users/{USER}/repos?per_page=100&type=owner")
        if not r["fork"] and r["name"] != USER
    ]
    bytes_by_lang: dict[str, int] = defaultdict(int)
    for name in repos:
        for lang, n in api(f"repos/{USER}/{name}/languages").items():
            bytes_by_lang[lang] += int(n)

    ranked = sorted(bytes_by_lang.items(), key=lambda kv: kv[1], reverse=True)
    top = ranked[:4]
    if len(ranked) > 4:
        top.append(("Other", sum(n for _, n in ranked[4:])))

    month = date.today().strftime("%B %Y")
    for suffix, theme in (("dark", DARK), ("light", LIGHT)):
        (ASSETS / f"languages-{suffix}.svg").write_text(
            languages_svg(theme, top, month), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
