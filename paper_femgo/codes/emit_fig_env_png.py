"""
emit_fig_env_png.py — Fig S1 (Fig_env) panel images from the VESTA renders.

Crops the owner's VESTA-rendered top/side views to their opaque content, flattens
to white, and writes TWO separate 300-dpi panel images so the supplementary can
place them in a line-less two-column table with (a)/(b) labels as text below.

Input (owner's VESTA renders):
  analysis/fig_env_vesta/fig_env_top.png    (a, top view)
  analysis/fig_env_vesta/fig_env_side.png   (b, side view)

Output (tracked in git):
  analysis/figures/Fig_env_a.png
  analysis/figures/Fig_env_b.png

Environment: any python with Pillow + numpy.
"""
__version__ = "1.0.0"

import os
import numpy as np
from PIL import Image

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', 'analysis', 'fig_env_vesta')
FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', 'analysis', 'figures')

PANELS = [
    ('fig_env_top.png', 'Fig_env_a.png'),
    ('fig_env_side.png', 'Fig_env_b.png'),
]

# Panels are placed at 3.5 cm in the tex; size generously for 300 dpi print.
TARGET_HEIGHT = 600   # px per panel (~300 dpi at ~5 cm)
OUT_DPI = 300


def crop_flatten_white(filename, target_height):
    """Crop to opaque content, flatten RGBA to white, upscale to target height."""
    with Image.open(os.path.join(SRC_DIR, filename)).convert('RGBA') as im:
        a = np.array(im)
        mask = a[..., 3] > 10
        if mask.any():
            ys, xs = np.where(mask)
            box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
            im = im.crop(box)
        # flatten to white
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        rgb = bg.convert('RGB')
    w, h = rgb.size
    scale = target_height / max(h, 1)
    new_w = max(1, int(round(w * scale)))
    return rgb.resize((new_w, target_height), Image.LANCZOS)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    made = 0
    for src, out in PANELS:
        src_path = os.path.join(SRC_DIR, src)
        if not os.path.exists(src_path):
            print(f'  MISSING {src}')
            continue
        img = crop_flatten_white(src, TARGET_HEIGHT)
        out_path = os.path.join(FIG_DIR, out)
        img.save(out_path, dpi=(OUT_DPI, OUT_DPI))
        print(f'  -> {out_path} ({img.size[0]}x{img.size[1]} @ {OUT_DPI} dpi)')
        made += 1
    if not made:
        print('  no panels produced')


if __name__ == '__main__':
    main()
