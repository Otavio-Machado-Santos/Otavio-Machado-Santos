#!/usr/bin/env python3
"""Anima a revelação do retrato ASCII existente. Requer Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / "assets"
W, H = 1200, 430
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
PORTRAIT.thumbnail((385, 385), Image.Resampling.LANCZOS)
FONTS = {"name": font(57, bold=True), "role": font(26), "mono": font(19, mono=True)}


def frame(progress):
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)
    draw.line((421, 47, 421, 382), fill="#30363d", width=1)
    # Revelação em linhas: o retrato gerado permanece intacto.
    height = min(PORTRAIT.height, int(progress * PORTRAIT.height / 8) * 8)
    if height:
        visible = PORTRAIT.crop((0, 0, PORTRAIT.width, height))
        canvas.paste(visible, (18, 22), visible)
    if 0 < progress < 1:
        y = 22 + height
        draw.line((18, y, 403, y), fill=GREEN, width=1)
    draw.text((467, 51), "OTAVIO-MACHADO-SANTOS", font=FONTS["mono"], fill=GREEN)
    draw.text((463, 100), "Otávio Machado", font=FONTS["name"], fill=TEXT)
    draw.text((463, 164), "Santos", font=FONTS["name"], fill=TEXT)
    draw.text((467, 248), "Observabilidade · DevOps · AI Ops", font=FONTS["role"], fill=TEXT)
    draw.text((467, 294), "Infraestrutura, automação e IA.", font=FONTS["role"], fill=MUTED)
    draw.line((467, 345, 528, 345), fill=ORANGE, width=3)
    draw.text((467, 365), "Explore meu histórico e meus projetos ↓", font=FONTS["mono"], fill=MUTED)
    return canvas


if __name__ == "__main__":
    static = frame(1)
    static.save(ASSETS / "intro-ascii-static.png")
    frames = [frame(i / 31) for i in range(32)]
    frames.append(static)
    frames[0].save(ASSETS / "intro-ascii.gif", save_all=True, append_images=frames[1:],
                   duration=[125] * 32 + [3500], loop=0, optimize=True)
    print("Retrato: 4 s de construção e 3,5 s de pausa; 1200 × 430.")
