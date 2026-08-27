"""Render profile header and DNS icons as PNGs."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = Path(r"C:\Windows\Fonts")

W, H = 1360, 340


def load(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def header(path: Path, name_fill: str, tag_fill: str, meta_fill: str, accent: str) -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    name_font = load("segoeuib.ttf", 64)
    tag_font = load("segoeui.ttf", 26)
    meta_font = load("segoeui.ttf", 18)

    name = "Socheat Rotanak"
    tag = "Windows software that stays on your machine"
    meta = "Phnom Penh   ·   AUPP   ·   Rust"

    def cx(text: str, font: ImageFont.FreeTypeFont) -> float:
        b = d.textbbox((0, 0), text, font=font)
        return (W - (b[2] - b[0])) / 2

    d.text((cx(name, name_font), 58), name, font=name_font, fill=name_fill)

    line_w, line_h = 64, 4
    lx = (W - line_w) / 2
    d.rounded_rectangle((lx, 148, lx + line_w, 148 + line_h), radius=2, fill=accent)

    d.text((cx(tag, tag_font), 176), tag, font=tag_font, fill=tag_fill)
    d.text((cx(meta, meta_font), 228), meta, font=meta_font, fill=meta_fill)
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


if __name__ == "__main__":
    main()
