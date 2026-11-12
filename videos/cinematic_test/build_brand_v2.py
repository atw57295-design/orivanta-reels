#!/usr/bin/env python3
"""
Rebuild the intro, outro and CTA-badge using the new ORIVANTA mark
(build_logo_v2.py), replacing the old glossy 3D logo everywhere.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = "/home/claude/orivanta_work"
BRAND2 = f"{ROOT}/brand/v2"
OUT = f"{ROOT}/videos/cinematic_test/brand_cards"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

def make_background(w, h, top=(14, 18, 30), bottom=(4, 5, 9)):
    bg = Image.new("RGB", (w, h), bottom)
    px = bg.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0]*(1-t) + bottom[0]*t)
        g = int(top[1]*(1-t) + bottom[1]*t)
        b = int(top[2]*(1-t) + bottom[2]*t)
        for x in range(w):
            px[x, y] = (r, g, b)
    vign = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vign)
    vd.ellipse([-w*0.3, -h*0.3, w*1.3, h*1.3], fill=55)
    vign = vign.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    bg = Image.composite(bg, dark, vign)
    return bg.convert("RGBA")

def main():
    lockup = Image.open(f"{BRAND2}/orivanta_lockup_transparent.png").convert("RGBA")

    # --- intro / outro title card: lockup centered on brand dark gradient ---
    card = make_background(W, H)
    lh = int(H * 0.62)
    scale = lh / lockup.height
    lw = int(lockup.width * scale)
    lockup_r = lockup.resize((lw, lh), Image.LANCZOS)
    card.alpha_composite(lockup_r, ((W - lw)//2, (H - lh)//2))
    card.convert("RGB").save(f"{OUT}/logo_card_1280x720.png", quality=95)
    print("saved logo_card_1280x720.png")

    # --- watermark already built by build_logo_v2.py; just copy/resize ---
    wm = Image.open(f"{BRAND2}/orivanta_watermark_small.png").convert("RGBA")
    wm.save(f"{OUT}/watermark_small.png")
    print("saved watermark_small.png", wm.size)

if __name__ == "__main__":
    main()
