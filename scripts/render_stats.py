from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

from render_profile import DARK as DARK_BASE
from render_profile import LIGHT as LIGHT_BASE
from render_profile import MONO, text, svg

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

DARK = {
    **DARK_BASE,
    "line": "#24201b",
    "ramp": ["#e07a5f", "#d98e72", "#c9a08b", "#b8a18f", "#99897a", "#776b60"],
}
LIGHT = {
    **LIGHT_BASE,
    "line": "#efe6d9",
    "ramp": ["#b4441f", "#cc6a44", "#dc8e6d", "#e4b29a", "#cdb8a4", "#a99a88"],
}


def gh(*args: str) -> str:
    return subprocess.check_output(["gh", *args], text=True)


def gh_json(*args: str):
    return json.loads(gh(*args))


def fmt(n: int) -> str:
    return f"{n:,}"


def streaks(days: list[tuple[date, int]]) -> tuple[int, int]:
    longest = run = 0
    today = date.today()
    for day, count in days:
        if count > 0:
            run += 1
            longest = max(longest, run)
        elif day < today:
            run = 0
    current = run
    if days and days[-1][0] < today and days[-1][1] == 0:
        current = 0
    return current, longest


def weekly_bars(theme: dict, weekly: list[int]) -> str:
    x0, x1 = 28, 392
    base, top = 232, 150
    peak = max(weekly) or 1
    slot = (x1 - x0) / len(weekly)
    width = max(3.0, slot * 0.68)
    grid = "\n".join(
        f'  <line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{theme["line"]}" stroke-width="1"/>'
        for y in (170, 200, 232)
    )
    bars = []
    for i, value in enumerate(weekly):
        x = x0 + i * slot + (slot - width) / 2
        if value == 0:
            bars.append(
                f'  <rect x="{x:.1f}" y="{base - 2}" width="{width:.1f}" height="2" '
                f'fill="{theme["faint"]}" fill-opacity="0.45"/>'
            )
            continue
        height = max(3.0, (base - top) * (value / peak) ** 0.5)
        opacity = 1 if value == peak else 0.35
        bars.append(
            f'  <rect x="{x:.1f}" y="{base - height:.1f}" width="{width:.1f}" height="{height:.1f}" '
            f'fill="{theme["accent"]}" fill-opacity="{opacity}"/>'
        )
    return "\n".join([grid, *bars])


def activity_svg(theme: dict, contribs: int, commits: int, prs: int, repos: int,
                 weekly: list[int]) -> str:
    body = "\n".join([
        f'  <rect x="0.5" y="0.5" width="419" height="311" rx="10" fill="{theme["bg"]}" stroke="{theme["border"]}"/>',
        text(28, 36, "ACTIVITY", 10, theme["accent"], family=MONO, spacing=1.6),
        text(392, 36, "LAST 12 MONTHS", 9, theme["faint"], family=MONO, anchor="end", spacing=1.3),
        text(28, 104, fmt(contribs), 50, theme["text"], weight=700, spacing=-1.5),
        text(28, 126, "CONTRIBUTIONS", 10, theme["faint"], family=MONO, spacing=1.5),
        weekly_bars(theme, weekly),
        text(28, 278, fmt(commits), 18, theme["text"], weight=700),
        text(28, 294, "COMMITS", 9, theme["faint"], family=MONO, spacing=1.3),
        text(156, 278, fmt(prs), 18, theme["text"], weight=700),
        text(156, 294, "PULL REQUESTS", 9, theme["faint"], family=MONO, spacing=1.3),
        text(286, 278, fmt(repos), 18, theme["text"], weight=700),
        text(286, 294, "REPOSITORIES", 9, theme["faint"], family=MONO, spacing=1.3),
    ])
    return svg(420, 312, "GitHub activity for JustNak", body)


def languages_svg(theme: dict, langs: list[tuple[str, int]], current: int, longest: int) -> str:
    total = sum(n for _, n in langs) or 1
    bar_x, bar_y, bar_w, bar_h, gap = 28, 58, 364, 12, 2
    inner = bar_w - gap * (len(langs) - 1)
    segments = []
    cursor = bar_x
    for i, (_, n) in enumerate(langs):
        width = max(5.0, inner * n / total)
        segments.append(
            f'  <rect x="{cursor:.1f}" y="{bar_y}" width="{width:.1f}" height="{bar_h}" '
            f'rx="3" fill="{theme["ramp"][i % len(theme["ramp"])]}"/>'
        )
        cursor += width + gap
    rows = []
    for i, (name, n) in enumerate(langs):
        y = 102 + i * 34
        rows.append(
            f'  <circle cx="30" cy="{y - 4}" r="3.6" fill="{theme["ramp"][i % len(theme["ramp"])]}"/>'
        )
        rows.append(text(42, y, name, 14, theme["text"]))
        rows.append(text(392, y, f"{n / total * 100:.1f}%", 10.5, theme["muted"], family=MONO, anchor="end"))
    body = "\n".join([
        f'  <rect x="0.5" y="0.5" width="419" height="311" rx="10" fill="{theme["bg"]}" stroke="{theme["border"]}"/>',
        text(28, 36, "LANGUAGES", 10, theme["accent"], family=MONO, spacing=1.6),
        text(392, 36, "BY BYTES", 9, theme["faint"], family=MONO, anchor="end", spacing=1.3),
        *segments,
        *rows,
        f'  <line x1="28" y1="284" x2="392" y2="284" stroke="{theme["line"]}"/>',
        text(28, 300, f"CURRENT STREAK {current} DAYS  ·  LONGEST {longest}", 9, theme["faint"],
             family=MONO, spacing=1.1),
    ])
    return svg(420, 312, "Top languages and contribution streak for JustNak", body)


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
        'query=query { user(login: "JustNak") { pullRequests { totalCount } repositories(ownerAffiliations: OWNER, isFork: false) { totalCount } contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }',
    )["data"]["user"]

    prs = payload["pullRequests"]["totalCount"]
    repos = payload["repositories"]["totalCount"]
    calendar = payload["contributionsCollection"]["contributionCalendar"]
    contribs = calendar["totalContributions"]

    day_list: list[tuple[date, int]] = []
    weekly: list[int] = []
    for week in calendar["weeks"]:
        week_total = 0
        for day in week["contributionDays"]:
            n = int(day["contributionCount"])
            week_total += n
            day_list.append((date.fromisoformat(day["date"]), n))
        weekly.append(week_total)

    current, longest = streaks(day_list)

    bytes_by_lang: dict[str, int] = defaultdict(int)
    for name in OWNED:
        langs = gh_json("api", f"repos/JustNak/{name}/languages")
        for lang, n in langs.items():
            bytes_by_lang[lang] += int(n)

    ranked = sorted(bytes_by_lang.items(), key=lambda kv: kv[1], reverse=True)
    top = ranked[:4]
    if len(ranked) > 4:
        top.append(("Other", sum(n for _, n in ranked[4:])))

    for suffix, theme in (("dark", DARK), ("light", LIGHT)):
        (ASSETS / f"activity-{suffix}.svg").write_text(
            activity_svg(theme, contribs, commits, prs, repos, weekly), encoding="utf-8"
        )
        (ASSETS / f"languages-{suffix}.svg").write_text(
            languages_svg(theme, top, current, longest), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
