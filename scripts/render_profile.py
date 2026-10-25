from __future__ import annotations

import base64
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BRAND = ASSETS / "brand"

FONT = "Segoe UI, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "Cascadia Code, SFMono-Regular, Consolas, Liberation Mono, monospace"

DARK = {
    "bg": "#12100e",
    "border": "#2d2721",
    "text": "#f2ede4",
    "muted": "#a79c8d",
    "faint": "#6f655c",
    "accent": "#e07a5f",
}

LIGHT = {
    "bg": "#fbf8f2",
    "border": "#e2d9cc",
    "text": "#1c1917",
    "muted": "#6b6258",
    "faint": "#9a9083",
    "accent": "#b4441f",
}


def svg(width: int, height: int, title: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">\n'
        f"  <title>{escape(title)}</title>\n"
        f"{body}\n"
        f"</svg>\n"
    )


def text(x: float, y: float, value: str, size: float, fill: str, *, weight: int = 400,
         family: str = FONT, anchor: str = "start", spacing: float | None = None) -> str:
    extra = f' text-anchor="{anchor}"' if anchor != "start" else ""
    if spacing is not None:
        extra += f' letter-spacing="{spacing}"'
    return (
        f'  <text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}"{extra}>{escape(value)}</text>'
    )


def data_uri(path: Path) -> str:
    mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def header(theme: dict) -> str:
    body = "\n".join([
        text(0, 18, "PORTFOLIO / 2026", 10, theme["faint"], family=MONO, spacing=1.6),
        text(860, 18, "PHNOM PENH · UTC+7", 10, theme["faint"], family=MONO, anchor="end", spacing=1.2),
        f'  <line x1="0" y1="34" x2="860" y2="34" stroke="{theme["border"]}" stroke-width="1"/>',
        f'  <text x="0" y="126" font-family="{FONT}" font-size="76" font-weight="800" '
        f'letter-spacing="-2.6" fill="{theme["text"]}">Socheat '
        f'<tspan fill="{theme["accent"]}">Rotanak</tspan></text>',
        text(0, 166, "Local-first Windows tools, built in Rust.", 22, theme["muted"]),
        f'  <line x1="0" y1="204" x2="860" y2="204" stroke="{theme["border"]}" stroke-width="1"/>',
        f'  <rect x="0" y="203" width="120" height="2" fill="{theme["accent"]}"/>',
        text(0, 236, "FOCUS", 10, theme["accent"], family=MONO, spacing=1.4),
        text(58, 236, "Local-first software", 13, theme["muted"]),
        text(262, 236, "STACK", 10, theme["accent"], family=MONO, spacing=1.4),
        text(320, 236, "Rust · GPUI · TypeScript", 13, theme["muted"]),
        text(548, 236, "STUDY", 10, theme["accent"], family=MONO, spacing=1.4),
        text(606, 236, "Cybersecurity & networking", 13, theme["muted"]),
    ])
    return svg(860, 252, "Socheat Rotanak — local-first Windows tools, built in Rust", body)


def featured_card(theme: dict, logo: Path) -> str:
    uri = data_uri(logo)
    body = "\n".join([
        f'  <defs><clipPath id="logo"><rect x="36" y="76" width="104" height="104" rx="18"/></clipPath></defs>',
        f'  <rect x="0.5" y="0.5" width="859" height="291" rx="10" fill="{theme["bg"]}" stroke="{theme["border"]}"/>',
        text(36, 46, "01", 11, theme["accent"], family=MONO, spacing=1.2),
        text(64, 46, "FEATURED", 9, theme["faint"], family=MONO, spacing=1.6),
        text(824, 48, "↗", 18, theme["muted"], anchor="end"),
        f'  <image x="36" y="76" width="104" height="104" href="{uri}" clip-path="url(#logo)" preserveAspectRatio="xMidYMid slice"/>',
        f'  <rect x="36.5" y="76.5" width="103" height="103" rx="18" fill="none" stroke="{theme["border"]}"/>',
        text(168, 116, "RusticDL", 40, theme["text"], weight=700, spacing=-0.8),
        text(168, 152, "A local-first HTTP(S) download manager with", 22, theme["muted"]),
        text(168, 180, "segmented transfers, resume, and a browser handoff.", 22, theme["muted"]),
        text(168, 224, "RUST  /  GPUI  /  WINDOWS · LINUX", 11, theme["faint"], family=MONO, spacing=1.1),
        f'  <line x1="36" y1="250" x2="824" y2="250" stroke="{theme["border"]}"/>',
        text(36, 274, "VIEW PROJECT", 9, theme["accent"], family=MONO, spacing=1.6),
        text(824, 274, "github.com/JustNak/RusticDL", 9, theme["faint"], family=MONO, anchor="end"),
    ])
    return svg(860, 292, "RusticDL — local-first download manager for Windows and Linux", body)


def small_card(theme: dict, logo: Path, index: str, title: str, lines: list[str], stack: str,
               url: str) -> str:
    uri = data_uri(logo)
    desc = "\n".join(
        text(28, 182 + i * 22, line, 15, theme["muted"]) for i, line in enumerate(lines)
    )
    body = "\n".join([
        f'  <defs><clipPath id="logo"><rect x="28" y="64" width="52" height="52" rx="11"/></clipPath></defs>',
        f'  <rect x="0.5" y="0.5" width="419" height="291" rx="10" fill="{theme["bg"]}" stroke="{theme["border"]}"/>',
        text(28, 40, index, 10, theme["accent"], family=MONO, spacing=1.2),
        text(392, 42, "↗", 16, theme["muted"], anchor="end"),
        f'  <image x="28" y="64" width="52" height="52" href="{uri}" clip-path="url(#logo)" preserveAspectRatio="xMidYMid slice"/>',
        f'  <rect x="28.5" y="64.5" width="51" height="51" rx="11" fill="none" stroke="{theme["border"]}"/>',
        text(28, 150, title, 26, theme["text"], weight=700, spacing=-0.4),
        desc,
        f'  <line x1="28" y1="246" x2="392" y2="246" stroke="{theme["border"]}"/>',
        text(28, 270, stack, 9, theme["faint"], family=MONO, spacing=1.0),
        text(392, 270, "VIEW PROJECT", 8, theme["accent"], family=MONO, anchor="end", spacing=1.2),
    ])
    return svg(420, 292, f"{title} — {url}", body)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    logos = {
        "rusticdl": BRAND / "rusticdl.png",
        "rusticgu": BRAND / "rusticgu.png",
        "dns": BRAND / "dns.svg",
    }
    for suffix, theme in (("dark", DARK), ("light", LIGHT)):
        (ASSETS / f"header-{suffix}.svg").write_text(header(theme), encoding="utf-8")
        (ASSETS / f"rusticdl-card-{suffix}.svg").write_text(
            featured_card(theme, logos["rusticdl"]), encoding="utf-8"
        )
        (ASSETS / f"rusticgu-card-{suffix}.svg").write_text(
            small_card(
                theme,
                logos["rusticgu"],
                "02",
                "RusticGU",
                ["Shrinks Steam libraries with transparent", "WOF compression, so games stay playable."],
                "RUST  /  GPUI  /  WINDOWS",
                "github.com/JustNak/RusticGU",
            ),
            encoding="utf-8",
        )
        (ASSETS / f"dns-card-{suffix}.svg").write_text(
            small_card(
                theme,
                logos["dns"],
                "03",
                "DNS Bench Pro",
                ["A DNS-over-HTTPS latency benchmark that", "runs entirely in your browser."],
                "JAVASCRIPT  /  DNS  /  PRIVACY",
                "github.com/JustNak/DNSBenchPro",
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
