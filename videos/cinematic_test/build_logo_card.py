#!/usr/bin/env python3
"""
Build brand assets for the intro / outro / watermark:
 1. Isolate the ORIVANTA logo mark from its flat light-gray background
    (flood-fill from the corners so we never touch the logo's own highlights),
    producing a clean RGBA cutout with NO cropping or distortion of the mark.
 2. Compose that cutout, uncropped and fit-contain, onto a clean cinematic
    dark background at 1280x720 -> "logo_card_1280x720.png" (used for both
    the intro and the redesigned, uncropped Scene 9 outro).
 3. Build a small persistent corner-watermark PNG from the existing circular
    watermark asset (already RGBA), resized without distortion.
"""
from PIL import Image, ImageDraw, ImageFilter
import collections

ROOT = "/home/claude/orivanta_work"
BRAND = f"{ROOT}/brand"
OUT = f"{ROOT}/videos/cinematic_test/brand_cards"
import os
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

def flood_fill_bg_mask(im, tol=55, sat_max=34):
    """Flood fill from all four corners over near-gray background pixels
    (8-connected, generous tolerance to also absorb the soft floor
    reflection/vignette), building an alpha mask that removes only the
    CONNECTED background region so interior highlights inside the logo
    itself (which never touch the outer background) are preserved."""
    im = im.convert("RGB")
    w, h = im.size
    px = im.load()
    visited = bytearray(w * h)
    mask = bytearray(w * h)  # 1 = background (to become transparent)

    def is_bg_like(c, seed):
        dr = abs(c[0]-seed[0]); dg = abs(c[1]-seed[1]); db = abs(c[2]-seed[2])
        maxc, minc = max(c), min(c)
        sat = maxc - minc
        return dr < tol and dg < tol and db < tol and sat < sat_max and minc > 95

    seeds = [(2,2), (w-3,2), (2,h-3), (w-3,h-3)]
    stack = []
    for sx, sy in seeds:
        seed_c = px[sx, sy]
        idx = sy*w+sx
        if not visited[idx]:
            stack.append((sx, sy, seed_c))

    neighbors = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    while stack:
        x, y, seed_c = stack.pop()
        idx = y*w+x
        if visited[idx]:
            continue
        c = px[x, y]
        if not is_bg_like(c, seed_c):
            continue
        visited[idx] = 1
        mask[idx] = 1
        for dx, dy in neighbors:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny*w+nx]:
                stack.append((nx, ny, seed_c))

    alpha = Image.frombytes("L", (w, h), bytes(0 if b else 255 for b in mask))
    # clean up tiny stray fringe pixels, then feather the edge
    alpha = alpha.filter(ImageFilter.MedianFilter(5))
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.5))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out

def make_background(w, h, top=(10, 13, 22), bottom=(2, 3, 6)):
    bg = Image.new("RGB", (w, h), bottom)
    px = bg.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0]*(1-t) + bottom[0]*t)
        g = int(top[1]*(1-t) + bottom[1]*t)
        b = int(top[2]*(1-t) + bottom[2]*t)
        for x in range(w):
            px[x, y] = (r, g, b)
    # subtle vignette
    vign = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vign)
    vd.ellipse([-w*0.3, -h*0.3, w*1.3, h*1.3], fill=60)
    vign = vign.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    bg = Image.composite(bg, dark, vign)
    return bg.convert("RGBA")

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=radius, fill=255)
    return m

def fit_contain_plaque(canvas, logo_rgb, max_frac_h=0.66):
    """Place the FULL, uncropped, undistorted logo square (scaled uniformly,
    never stretched) as a soft-edged plaque with a gentle drop shadow on the
    dark cinematic background -- avoids any lossy background chroma-keying
    while still looking deliberate and on-brand."""
    cw, ch = canvas.size
    lw, lh = logo_rgb.size  # square, e.g. 1600x1600
    target_h = int(ch * max_frac_h)
    scale = target_h / lh
    target_w = int(lw * scale)
    resized = logo_rgb.resize((target_w, target_h), Image.LANCZOS).convert("RGBA")

    radius = int(target_w * 0.06)
    mask = rounded_mask((target_w, target_h), radius)
    resized.putalpha(mask)

    x = (cw - target_w) // 2
    y = (ch - target_h) // 2

    # soft drop shadow
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    pad = int(target_w * 0.03)
    sd.rounded_rectangle(
        [x - pad, y - pad + 14, x + target_w + pad, y + target_h + pad + 14],
        radius=radius + pad, fill=(0, 0, 0, 160)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    canvas.alpha_composite(shadow)

    # faint glow behind the plaque for a premium feel
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([x - target_w*0.12, y - target_h*0.12, x + target_w*1.12, y + target_h*1.12],
               fill=(255, 205, 90, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    canvas.alpha_composite(glow)

    canvas.alpha_composite(resized, (x, y))
    return canvas

def main():
    logo = Image.open(f"{BRAND}/orivanta_logo_full.jpg").convert("RGB")

    card = make_background(W, H)
    card = fit_contain_plaque(card, logo, max_frac_h=0.66)
    card = card.convert("RGB")
    card.save(f"{OUT}/logo_card_1280x720.png", quality=95)
    print("saved logo_card_1280x720.png")

    # Persistent corner watermark: resize the existing RGBA watermark asset
    # (no distortion -- uniform scale) to a small, unobtrusive size.
    wm = Image.open(f"{BRAND}/orivanta_logo_watermark.png").convert("RGBA")
    target_w = 110
    scale = target_w / wm.width
    target_h = int(wm.height * scale)
    wm_small = wm.resize((target_w, target_h), Image.LANCZOS)
    wm_small.save(f"{OUT}/watermark_small.png")
    print("saved watermark_small.png", wm_small.size)

if __name__ == "__main__":
    main()
