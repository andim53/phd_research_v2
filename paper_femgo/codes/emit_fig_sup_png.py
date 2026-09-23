"""
emit_fig_sup_png.py — Fig S2 (Fig_sup) panel images from the VESTA renders.

Flattens the owner's VESTA-rendered ground-state PNGs (3x3 and 4x4) to white and
writes TWO separate high-DPI panel images, so the supplementary can place them
in adjacent table cells with (a)/(b) labels as text below each (no labels drawn
inside the images).

Input (owner's VESTA renders):
  analysis/fig_sup_vesta/fig_sup_3x3_gs1.png   (a, 3x3)
  analysis/fig_sup_vesta/fig_sup_4x4_gs1.png   (b, 4x4)

Output:
  analysis/figures/Fig_sup_a.png   (3x3 panel)
  analysis/figures/Fig_sup_b.png   (4x4 panel)

Environment: any python with Pillow.
"""
__version__ = "2.0.0"

import os
from PIL import Image

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', 'analysis', 'fig_sup_vesta')
FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', 'analysis', 'figures')

PANELS = [
    ('fig_sup_3x3_gs1.png', 'Fig_sup_a.png'),
    ('fig_sup_4x4_gs1.png', 'Fig_sup_b.png'),
]

# Target: each panel scaled so output is ~300 dpi at ~7.0 cm render height.
TARGET_HEIGHT = 1000   # px per panel (generous resolution for the print size)
OUT_DPI = 300


def flatten_white(filename):
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
    os.makedirs(FIG_DIR, exist_ok=True)
    made = 0
    for src, out in PANELS:
        src_path = os.path.join(SRC_DIR, src)
        if not os.path.exists(src_path):
            print(f'  MISSING {src}')
            continue
        img = flatten_white(src)
        out_path = os.path.join(FIG_DIR, out)
        img.save(out_path, dpi=(OUT_DPI, OUT_DPI))
        print(f'  -> {out_path} ({img.size[0]}x{img.size[1]} @ {OUT_DPI} dpi)')
        made += 1
    if not made:
        print('  no panels produced')


if __name__ == '__main__':
    main()
