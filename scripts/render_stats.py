"""Render local GitHub stats cards from gh API data."""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

OWNED = [
    "ChannelCargo",
    "ChefBook",
    "DNSBenchPro",
    "PeerCargo",
    "Rustic-AT",
    "RusticDL",
    "RusticGU",
    "SimpleDownloadManager",
    "smartboard",
]

LANG_COLORS = {
    "Rust": "#dea584",
    "TypeScript": "#3178c6",
    "Svelte": "#ff3e00",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "NSIS": "#6b7280",
    "PowerShell": "#012456",
    "Python": "#3572a5",
    "Shell": "#89e051",
}

DARK = {
    "bg": "#161b22",
    "border": "#30363d",
    "title": "#2dd4bf",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "empty": "#21262d",
    "heat": ["#21262d", "#0f3d38", "#1a7a6e", "#2dd4bf", "#99f6e4"],
}
LIGHT = {
    "bg": "#ffffff",
    "border": "#d0d7de",
    "title": "#0d9488",
    "text": "#1f2328",
    "muted": "#656d76",
    "empty": "#ebedf0",
    "heat": ["#ebedf0", "#99f6e4", "#5eead4", "#14b8a6", "#0f766e"],
}


def gh(*args: str) -> str:
    return subprocess.check_output(["gh", *args], text=True)


def gh_json(*args: str):
    return json.loads(gh(*args))


def fmt(n: int) -> str:
    return f"{n:,}"


def streaks(days: list[tuple[date, int]]) -> tuple[int, int]:
    current = longest = run = 0
    today = date.today()
    for day, count in days:
        if count > 0:
            run += 1
            longest = max(longest, run)
        else:
            if day < today:
                run = 0
    current = run
    if days and days[-1][0] < today and days[-1][1] == 0:
        current = 0
    return current, longest


def svg_card(width: int, height: int, theme: dict, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="{theme["bg"]}" stroke="{theme["border"]}"/>
  {body}
</svg>
'''


CARD_W, CARD_H = 420, 278


def stats_svg(theme: dict, commits: int, contribs: int, prs: int, repos: int) -> str:
    rows = [
        ("Commits", fmt(commits)),
        ("Contributions this year", fmt(contribs)),
        ("Pull requests", fmt(prs)),
        ("Repositories", fmt(repos)),
    ]
    items = []
    y = 86
    for label, value in rows:
        items.append(
            f'<text x="28" y="{y}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="{theme["muted"]}">{label}</text>'
            f'<text x="{CARD_W - 28}" y="{y}" text-anchor="end" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" font-weight="600" fill="{theme["text"]}">{value}</text>'
        )
        y += 44
    body = f'''<text x="28" y="36" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" font-weight="600" fill="{theme["title"]}">GitHub stats</text>
  {"".join(items)}'''
    return svg_card(CARD_W, CARD_H, theme, body)


def langs_svg(theme: dict, langs: list[tuple[str, int]]) -> str:
    total = sum(n for _, n in langs) or 1
    bars = []
    y = 62
    bar_w = CARD_W - 56
    for name, n in langs:
        pct = n / total * 100
        width = max(8, round(bar_w * n / total))
        color = LANG_COLORS.get(name, "#8b949e")
        bars.append(
            f'<text x="28" y="{y}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="{theme["text"]}">{name}</text>'
            f'<text x="{CARD_W - 28}" y="{y}" text-anchor="end" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="{theme["muted"]}">{pct:.1f}%</text>'
            f'<rect x="28" y="{y + 8}" width="{bar_w}" height="8" rx="4" fill="{theme["empty"]}"/>'
            f'<rect x="28" y="{y + 8}" width="{width}" height="8" rx="4" fill="{color}"/>'
        )
        y += 36
    body = f'''<text x="28" y="36" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" font-weight="600" fill="{theme["title"]}">Top languages</text>
  {"".join(bars)}'''
    return svg_card(CARD_W, CARD_H, theme, body)


def streak_svg(theme: dict, current: int, longest: int, total: int) -> str:
    body = f'''<text x="28" y="34" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" font-weight="600" fill="{theme["title"]}">Streak</text>
  <text x="165" y="92" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="36" font-weight="700" fill="{theme["title"]}">{current}</text>
  <text x="165" y="116" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="{theme["muted"]}">Current</text>
  <text x="330" y="92" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="36" font-weight="700" fill="{theme["text"]}">{longest}</text>
  <text x="330" y="116" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="{theme["muted"]}">Longest</text>
  <text x="495" y="92" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="36" font-weight="700" fill="{theme["text"]}">{fmt(total)}</text>
  <text x="495" y="116" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="{theme["muted"]}">This year</text>'''
    return svg_card(660, 148, theme, body)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)

    commits = gh_json(
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "/search/commits?q=author:JustNak",
    )["total_count"]

    payload = gh_json(
        "api",
        "graphql",
        "-f",
        "query=query { user(login: \"JustNak\") { pullRequests { totalCount } repositories(ownerAffiliations: OWNER, isFork: false) { totalCount } contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }",
    )["data"]["user"]

    prs = payload["pullRequests"]["totalCount"]
    repos = payload["repositories"]["totalCount"]
    calendar = payload["contributionsCollection"]["contributionCalendar"]
    contribs = calendar["totalContributions"]

    day_list: list[tuple[date, int]] = []
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            n = int(day["contributionCount"])
            day_list.append((date.fromisoformat(day["date"]), n))

    current, longest = streaks(day_list)

    bytes_by_lang: dict[str, int] = defaultdict(int)
    for name in OWNED:
        langs = gh_json("api", f"repos/JustNak/{name}/languages")
        for lang, n in langs.items():
            bytes_by_lang[lang] += int(n)

    top = sorted(bytes_by_lang.items(), key=lambda kv: kv[1], reverse=True)[:6]

    for suffix, theme in (("dark", DARK), ("light", LIGHT)):
        (ASSETS / f"stats-{suffix}.svg").write_text(stats_svg(theme, commits, contribs, prs, repos), encoding="utf-8")
        (ASSETS / f"langs-{suffix}.svg").write_text(langs_svg(theme, top), encoding="utf-8")
        (ASSETS / f"streak-{suffix}.svg").write_text(streak_svg(theme, current, longest, contribs), encoding="utf-8")


if __name__ == "__main__":
    main()
