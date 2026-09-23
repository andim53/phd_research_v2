"""
emit_fig_sup_png.py — composite Fig S2 (Fig_sup) from the two VESTA renders.

Combines the owner's VESTA-rendered ground-state PNGs (3x3 and 4x4) into the
single side-by-side Fig_sup figure used by paper2's supplementary, with (a)/(b)
panel labels, upscaled to high-DPI white output.

Input (owner's VESTA renders):
  analysis/fig_sup_vesta/fig_sup_3x3_gs1.png   (a, 3x3)
  analysis/fig_sup_vesta/fig_sup_4x4_gs1.png   (b, 4x4)

Output:
  analysis/figures/Fig_sup.png

Environment: any python with Pillow.
"""
__version__ = "1.0.0"

import os
from PIL import Image, ImageDraw, ImageFont

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', 'analysis', 'fig_sup_vesta')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'analysis', 'figures', 'Fig_sup.png')

PANELS = [
    ('fig_sup_3x3_gs1.png', 'a'),
    ('fig_sup_4x4_gs1.png', 'b'),
]

# Target: each panel scaled so output is ~300 dpi at ~8.5 cm render height.
TARGET_HEIGHT = 1000   # px per panel (generous resolution for the print size)
LABEL_PAD = 24         # px whitespace above each panel for the (a)/(b) label
OUT_DPI = 300


def load_composited(filename):
    """Load a VESTA RGBA PNG, flatten to white, upscale to TARGET_HEIGHT."""
    with Image.open(os.path.join(SRC_DIR, filename)) as im:
        im = im.convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        rgb = bg.convert('RGB')
    w, h = rgb.size
    scale = TARGET_HEIGHT / max(h, 1)
    new_w = max(1, int(round(w * scale)))
    return rgb.resize((new_w, TARGET_HEIGHT), Image.LANCZOS)


def main():
    flat = [(fn, tag) for fn, tag in PANELS
            if os.path.exists(os.path.join(SRC_DIR, fn))]
    if not flat:
        print('  no source panels found in', SRC_DIR)
        return

    panels = [load_composited(fn) for fn, _ in flat]
    panel_w = max(p.width for p in panels)
    panel_h = max(p.height for p in panels)
    total_w = panel_w * len(panels)
    total_h = LABEL_PAD + panel_h

    canvas = Image.new('RGB', (total_w, total_h), 'white')
    draw = ImageDraw.Draw(canvas)
    for i, ((fn, tag), p) in enumerate(zip(flat, panels)):
        x = i * panel_w
        canvas.paste(p, (x, LABEL_PAD))
        # (a) / (b) label, left of each panel, above its top edge is too tight,
        # so place it just inside the top-left of the panel.
        try:
            font = ImageFont.truetype('DejaVuSans-Bold.ttf', 72)
        except Exception:
            font = ImageFont.load_default()
        draw.text((x + 12, LABEL_PAD + 12), f'({tag})', fill=(0, 0, 0), font=font)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    canvas.save(OUT, dpi=(OUT_DPI, OUT_DPI))
    print(f'  -> {OUT} ({canvas.size[0]}x{canvas.size[1]} @ {OUT_DPI} dpi)')


if __name__ == '__main__':
    main()
