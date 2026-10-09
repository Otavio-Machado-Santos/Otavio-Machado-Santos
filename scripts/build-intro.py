#!/usr/bin/env python3
"""Anima a revelação do retrato ASCII existente. Requer Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / "assets"
W, H = 500, 560
BG, TEXT, MUTED, GREEN, ORANGE = "#0d1117", "#e6edf3", "#8b949e", "#39d353", "#f46800"


def font(size, bold=False, mono=False):
    names = (["/System/Library/Fonts/Menlo.ttc", "DejaVuSansMono.ttf"] if mono else
             (["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "DejaVuSans-Bold.ttf"] if bold else
              ["/System/Library/Fonts/Supplemental/Arial.ttf", "DejaVuSans.ttf"]))
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise RuntimeError("Instale Arial ou DejaVu Sans para gerar o cabeçalho.")


PORTRAIT = Image.open(ASSETS / "portrait-ascii.png").convert("RGBA")
PORTRAIT.thumbnail((460, 460), Image.Resampling.LANCZOS)
FONTS = {"name": font(26, bold=True), "mono": font(17, mono=True)}


def frame(progress):
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((1, 1, W-2, H-2), radius=14, outline="#30363d")
    # Revelação em linhas: o retrato gerado permanece intacto.
    height = min(PORTRAIT.height, int(progress * PORTRAIT.height / 8) * 8)
    if height:
        visible = PORTRAIT.crop((0, 0, PORTRAIT.width, height))
        canvas.paste(visible, ((W-PORTRAIT.width)//2, 62), visible)
    if 0 < progress < 1:
        y = 62 + height
        draw.line((20, y, 479, y), fill=GREEN, width=1)
    draw.text((28, 23), "otavio@github ~ $ whoami", font=FONTS["mono"], fill=GREEN)
    draw.text((28, 516), "Otavio Machado", font=FONTS["name"], fill=TEXT)
    draw.line((432, 541, 472, 541), fill=ORANGE, width=3)
    return canvas


if __name__ == "__main__":
    static = frame(1)
    static.save(ASSETS / "portrait-terminal-static.png")
    frames = [frame(i / 31) for i in range(32)]
    frames.append(static)
    frames[0].save(ASSETS / "portrait-terminal.gif", save_all=True, append_images=frames[1:],
                   duration=[125] * 32 + [3500], loop=0, optimize=True)
    print("Retrato: 4 s de construção e 3,5 s de pausa; 500 × 560.")
