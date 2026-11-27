from __future__ import annotations

import base64
import io
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BRAND = ASSETS / "brand"

FONT = "system-ui, 'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'Cascadia Code', SFMono-Regular, Consolas, 'Liberation Mono', monospace"

# One accent (rust). "faint" is tuned to at least 4.5:1 on the card paper.
DARK = {
    "bg": "#12100e",
    "border": "#2d2721",
    "text": "#f2ede4",
    "muted": "#a79c8d",
    "faint": "#8a7f72",
    "accent": "#e07a5f",
    "tile": "#26211c",
    "tile_edge": "#3d352d",
    "glyph": "#f2ede4",
}

LIGHT = {
    "bg": "#fbf8f2",
    "border": "#e2d9cc",
    "text": "#1c1917",
    "muted": "#6b6258",
    "faint": "#776d61",
    "accent": "#b4441f",
    "tile": "#1c1917",
    "tile_edge": "#1c1917",
    "glyph": "#fbf8f2",
}

# Card geometry. Pairs are (860 - 16) / 2 = 422 wide; each pair SVG carries
# half the 16px gutter as transparent padding, so two 430px images sit flush
# with no whitespace between them and line up with the 860px cards.
FULL = 860
HALF = 422
GUTTER = 16
PAIR = HALF + GUTTER // 2
SMALL_H = 248


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
        f'  <text x="{x}" y="{y}" font-family="{escape(family)}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}"{extra}>{escape(value)}</text>'
    )


def card(x: float, w: float, h: float, theme: dict) -> str:
    return (
        f'  <rect x="{x + 0.5}" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" '
        f'fill="{theme["bg"]}" stroke="{theme["border"]}"/>'
    )


def glyph_png(src: Path, bg: tuple[int, int, int], color: str, size: int) -> str:
    """Flatten a brand logo to a one-colour glyph: tile pixels become transparent,
    everything else becomes `color`. Returns a data URI at `size` px."""
    im = Image.open(src).convert("RGB")
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    out = Image.new("RGBA", im.size)
    src_px, out_px = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            p = src_px[x, y]
            d = max(abs(p[0] - bg[0]), abs(p[1] - bg[1]), abs(p[2] - bg[2]))
            a = max(0, min(255, int((d - 12) * 255 / 60)))
            out_px[x, y] = (r, g, b, a)
    out = out.resize((size, size), Image.LANCZOS)
    alpha = out.getchannel("A")
    # One colour plus alpha: store as a 16-level paletted PNG to keep the SVG small.
    pal = Image.new("P", (size, size))
    levels = [round(i * 255 / 15) for i in range(16)]
    pal.putdata([min(15, round(v / 17)) for v in alpha.tobytes()])
    pal.putpalette([r, g, b] * 16)
    buf = io.BytesIO()
    pal.save(buf, format="PNG", optimize=True, transparency=bytes(levels))
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def tile(x: float, y: float, size: float, radius: float, theme: dict) -> str:
    return (
        f'  <rect x="{x + 0.5}" y="{y + 0.5}" width="{size - 1}" height="{size - 1}" rx="{radius}" '
        f'fill="{theme["tile"]}" stroke="{theme["tile_edge"]}"/>'
    )


def logo_image(x: float, y: float, size: float, uri: str) -> str:
    return f'  <image x="{x}" y="{y}" width="{size}" height="{size}" href="{uri}"/>'


def dns_mark(x: float, y: float, size: float, theme: dict) -> str:
    """The DNS Bench Pro chart mark (64-unit grid) on the shared ink tile."""
    s = size / 64
    return "\n".join([
        tile(x, y, size, round(size * 0.21), theme),
        f'  <g transform="translate({x} {y}) scale({s:.4f})">',
        f'    <rect x="12" y="44" width="40" height="3" fill="{theme["glyph"]}"/>',
        f'    <rect x="12" y="44" width="19" height="3" fill="{theme["accent"]}"/>',
        f'    <rect x="28" y="14" width="3" height="33" fill="{theme["accent"]}"/>',
        "  </g>",
    ])


def header(theme: dict) -> str:
    body = "\n".join([
        f'  <text x="0" y="84" font-family="{escape(FONT)}" font-size="76" font-weight="800" '
        f'letter-spacing="-2.6" fill="{theme["text"]}">Socheat '
        f'<tspan fill="{theme["accent"]}">Rotanak</tspan></text>',
        text(2, 128, "Local-first tools, built in Rust.", 22, theme["muted"]),
        f'  <line x1="0" y1="160" x2="{FULL}" y2="160" stroke="{theme["border"]}" stroke-width="1"/>',
        f'  <rect x="0" y="159" width="120" height="2" fill="{theme["accent"]}"/>',
    ])
    return svg(FULL, 168, "Socheat Rotanak: local-first tools, built in Rust", body)


def featured_card(theme: dict, glyph: str) -> str:
    h = 248
    body = "\n".join([
        card(0, FULL, h, theme),
        text(36, 46, "FEATURED", 11, theme["faint"], family=MONO, spacing=1.6),
        text(816, 50, "↗", 18, theme["muted"], anchor="end"),
        tile(36, 72, 104, 18, theme),
        logo_image(36, 72, 104, glyph),
        text(168, 110, "RusticDL", 40, theme["text"], weight=700, spacing=-0.8),
        text(168, 146, "A local-first HTTP(S) download manager with", 22, theme["muted"]),
        text(168, 174, "segmented transfers, resume, and a browser handoff.", 22, theme["muted"]),
        text(168, 214, "RUST  /  GPUI  /  WINDOWS · LINUX", 11, theme["faint"], family=MONO, spacing=1.1),
    ])
    return svg(FULL, h, "RusticDL: local-first download manager for Windows and Linux", body)


def small_card(theme: dict, side: str, mark: str, title: str, lines: list[str], stack: str,
               alt: str, note: str | None = None) -> str:
    ox = 0 if side == "left" else GUTTER // 2
    x0, x1 = ox + 28, ox + HALF - 32
    desc = "\n".join(
        text(x0, 154 + i * 22, line, 15, theme["muted"]) for i, line in enumerate(lines)
    )
    parts = [
        card(ox, HALF, SMALL_H, theme),
        text(x1, 46, "↗", 16, theme["muted"], anchor="end"),
        mark,
        text(x0, 122, title, 26, theme["text"], weight=700, spacing=-0.4),
        desc,
        text(x0, 220, stack, 11, theme["faint"], family=MONO, spacing=1.0),
    ]
    if note:
        parts.append(text(x1, 220, note, 11, theme["accent"], family=MONO, anchor="end"))
    return svg(PAIR, SMALL_H, alt, "\n".join(parts))


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for suffix, theme in (("dark", DARK), ("light", LIGHT)):
        dl = glyph_png(BRAND / "rusticdl.png", (23, 23, 23), theme["glyph"], 208)
        gu = glyph_png(BRAND / "rusticgu.png", (7, 22, 28), theme["glyph"], 104)
        (ASSETS / f"header-{suffix}.svg").write_text(header(theme), encoding="utf-8")
        (ASSETS / f"rusticdl-card-{suffix}.svg").write_text(featured_card(theme, dl), encoding="utf-8")
        gx = 28
        (ASSETS / f"rusticgu-card-{suffix}.svg").write_text(
            small_card(
                theme, "left",
                "\n".join([tile(gx, 28, 52, 11, theme), logo_image(gx, 28, 52, gu)]),
                "RusticGU",
                ["Shrinks Steam libraries with transparent", "WOF compression, so games stay playable."],
                "RUST  /  GPUI  /  WINDOWS",
                "RusticGU: Steam library compression for Windows",
            ),
            encoding="utf-8",
        )
        dx = GUTTER // 2 + 28
        (ASSETS / f"dns-card-{suffix}.svg").write_text(
            small_card(
                theme, "right",
                dns_mark(dx, 28, 52, theme),
                "DNS Bench Pro",
                ["A DNS-over-HTTPS latency benchmark that", "runs entirely in your browser."],
                "JAVASCRIPT  /  DNS",
                "DNS Bench Pro: DNS-over-HTTPS latency benchmark in the browser",
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
