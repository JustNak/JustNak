"""Render profile header, DNS icons, and project cards."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = Path(r"C:\Windows\Fonts")

HEADER_W, HEADER_H = 1360, 340
CARD_W, CARD_H = 420, 500
LOGO_SIZE = 148
RADIUS = 28


def load(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def hex_to_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    v = value.lstrip("#")
    r, g, b = int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    return (r, g, b, alpha)


def center_x(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> float:
    box = draw.textbbox((0, 0), text, font=font)
    return (width - (box[2] - box[0])) / 2


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def round_image(img: Image.Image, radius: int) -> Image.Image:
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.size[0], img.size[1]), radius=radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0))
    out.putalpha(mask)
    return out


def header(path: Path, name_fill: str, tag_fill: str, meta_fill: str, accent: str) -> None:
    img = Image.new("RGBA", (HEADER_W, HEADER_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    name_font = load("segoeuib.ttf", 64)
    tag_font = load("segoeui.ttf", 26)
    meta_font = load("segoeui.ttf", 18)

    name = "Socheat Rotanak"
    tag = "Windows software that stays on your machine"
    meta = "Phnom Penh   ·   AUPP   ·   Rust"

    d.text((center_x(d, name, name_font, HEADER_W), 58), name, font=name_font, fill=name_fill)

    line_w, line_h = 64, 4
    lx = (HEADER_W - line_w) / 2
    d.rounded_rectangle((lx, 148, lx + line_w, 148 + line_h), radius=2, fill=accent)

    d.text((center_x(d, tag, tag_font, HEADER_W), 176), tag, font=tag_font, fill=tag_fill)
    d.text((center_x(d, meta, meta_font, HEADER_W), 228), meta, font=meta_font, fill=meta_fill)
    img.save(path, "PNG")


def dns_icon(path: Path, bg: str, ring: str, core: str) -> None:
    size = 256
    img = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2 + 4

    d.ellipse((40, 40, 216, 216), outline=ring, width=12)
    d.ellipse((78, 40, 178, 216), outline=ring, width=8)
    d.arc((40, 92, 216, 164), start=0, end=360, fill=ring, width=8)
    d.line((40, 128, 216, 128), fill=ring, width=8)
    d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=core)

    img.save(path, "PNG")


def project_card(
    path: Path,
    logo_path: Path,
    title: str,
    blurb: str,
    tags: str,
    bg: str,
    border: str,
    title_fill: str,
    body_fill: str,
    tag_fill: str,
    accent: str,
) -> None:
    img = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1, 1, CARD_W - 2, CARD_H - 2), radius=RADIUS, fill=bg, outline=border, width=2)

    logo = Image.open(logo_path).convert("RGBA").resize((LOGO_SIZE, LOGO_SIZE), Image.Resampling.LANCZOS)
    logo = round_image(logo, 28)
    lx = (CARD_W - LOGO_SIZE) // 2
    img.paste(logo, (lx, 48), logo)

    title_font = load("segoeuib.ttf", 28)
    body_font = load("segoeui.ttf", 20)
    tag_font = load("segoeui.ttf", 16)

    y = 48 + LOGO_SIZE + 28
    d.text((center_x(d, title, title_font, CARD_W), y), title, font=title_font, fill=title_fill)

    accent_w = 40
    ay = y + 46
    d.rounded_rectangle(
        ((CARD_W - accent_w) / 2, ay, (CARD_W + accent_w) / 2, ay + 3),
        radius=2,
        fill=accent,
    )

    y = ay + 22
    for line in wrap_text(d, blurb, body_font, CARD_W - 64):
        d.text((center_x(d, line, body_font, CARD_W), y), line, font=body_font, fill=body_fill)
        y += 28

    d.text((center_x(d, tags, tag_font, CARD_W), CARD_H - 56), tags, font=tag_font, fill=tag_fill)
    img.save(path, "PNG")


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    header(
        ASSETS / "header-dark.png",
        name_fill="#f0f6fc",
        tag_fill="#9aa4b2",
        meta_fill="#6e7681",
        accent="#2dd4bf",
    )
    header(
        ASSETS / "header-light.png",
        name_fill="#1f2328",
        tag_fill="#656d76",
        meta_fill="#8b949e",
        accent="#0d9488",
    )
    dns_icon(
        ASSETS / "dns-dark.png",
        bg="#111111",
        ring="#5eead4",
        core="#f0f6fc",
    )
    dns_icon(
        ASSETS / "dns-light.png",
        bg="#f3f4f6",
        ring="#0f766e",
        core="#111111",
    )

    projects = [
        (
            "rusticdl",
            ASSETS / "rusticdl.png",
            ASSETS / "rusticdl-light.png",
            "RusticDL",
            "Local-first HTTP(S) download manager for Windows",
            "Rust  ·  GPUI  ·  Windows",
        ),
        (
            "rusticgu",
            ASSETS / "rusticgu.png",
            ASSETS / "rusticgu-light.png",
            "RusticGU",
            "Compact a Steam library with transparent WOF compression",
            "Rust  ·  GPUI  ·  Steam",
        ),
        (
            "dns",
            ASSETS / "dns-dark.png",
            ASSETS / "dns-light.png",
            "DNS Bench Pro",
            "DoH latency from your network, measured in the browser",
            "JavaScript  ·  DNS  ·  Privacy",
        ),
    ]

    dark = dict(
        bg="#161b22",
        border="#30363d",
        title_fill="#f0f6fc",
        body_fill="#9aa4b2",
        tag_fill="#6e7681",
        accent="#2dd4bf",
    )
    light = dict(
        bg="#ffffff",
        border="#d0d7de",
        title_fill="#1f2328",
        body_fill="#656d76",
        tag_fill="#8b949e",
        accent="#0d9488",
    )

    for slug, logo_dark, logo_light, title, blurb, tags in projects:
        project_card(ASSETS / f"{slug}-card-dark.png", logo_dark, title, blurb, tags, **dark)
        project_card(ASSETS / f"{slug}-card-light.png", logo_light, title, blurb, tags, **light)


if __name__ == "__main__":
    main()
