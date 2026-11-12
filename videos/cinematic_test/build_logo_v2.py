#!/usr/bin/env python3
"""
ORIVANTA brand redesign -- a minimal, flat, cinematic-documentary-studio
mark: a thin compass/astrolabe ring in aged gold with a small North-star
accent, and a letter-spaced ivory serif wordmark beneath. Fully original
geometric design (no reuse of the old glossy 3D "O" mark). Built as clean
vector-style raster art (large canvas, downsampled) with a true alpha
channel so it drops onto any background -- dark cinematic plaque, small
corner watermark, or the opening/closing title card.
"""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = "/home/claude/orivanta_work/brand/v2"
os.makedirs(OUT, exist_ok=True)

GOLD = (196, 163, 92, 255)       # aged / antique gold
GOLD_SOFT = (196, 163, 92, 160)
IVORY = (235, 228, 210, 255)
NAVY = (8, 12, 22, 255)

SS = 4  # supersample factor for clean anti-aliased edges
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

def letter_spaced(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        w = draw.textlength(ch, font=font)
        x += w + tracking
    return x

def letter_spaced_width(draw, text, font, tracking):
    w = sum(draw.textlength(ch, font=font) for ch in text)
    return w + tracking * (len(text) - 1)

def draw_mark(size=1600):
    """The circular emblem alone (for the small watermark)."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = s // 2
    R = int(s * 0.46)

    # outer thin ring
    ring_w = max(2, int(s * 0.006))
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=GOLD, width=ring_w)
    R2 = int(R * 0.90)
    d.ellipse([cx-R2, cy-R2, cx+R2, cy+R2], outline=GOLD, width=max(1, ring_w//2))

    # the astrolabe-band "O": a thick open arc, gap at upper-right (~ -20 to 55 deg)
    band_r_out = int(R * 0.74)
    band_r_in = int(R * 0.52)
    gap_start, gap_end = -5, 22
    start_deg = gap_end
    end_deg = 360 + gap_start
    steps = 360
    pts_outer = []
    pts_inner = []
    for i in range(steps + 1):
        t = start_deg + (end_deg - start_deg) * i / steps
        a = math.radians(t)
        pts_outer.append((cx + band_r_out*math.cos(a), cy + band_r_out*math.sin(a)))
    for i in range(steps + 1):
        t = end_deg - (end_deg - start_deg) * i / steps
        a = math.radians(t)
        pts_inner.append((cx + band_r_in*math.cos(a), cy + band_r_in*math.sin(a)))
    d.polygon(pts_outer + pts_inner, fill=GOLD)

    # thin meridian line across the band's open circle (astrolabe feel)
    mer_w = max(1, int(s * 0.0035))
    d.line([(cx, cy-band_r_in), (cx, cy+band_r_in)], fill=GOLD_SOFT, width=mer_w)
    d.ellipse([cx-int(band_r_in*0.55), cy-band_r_in, cx+int(band_r_in*0.55), cy+band_r_in],
              outline=GOLD_SOFT, width=mer_w)

    # small four-point compass star at the gap (upper right), refined/geometric
    star_a = math.radians((gap_start + gap_end) / 2)
    star_r = (band_r_out + band_r_in) / 2 * 1.02
    sx = cx + star_r * math.cos(star_a)
    sy = cy + star_r * math.sin(star_a)
    sp = s * 0.028
    star_pts = [
        (sx, sy - sp), (sx + sp*0.24, sy - sp*0.24),
        (sx + sp, sy), (sx + sp*0.24, sy + sp*0.24),
        (sx, sy + sp), (sx - sp*0.24, sy + sp*0.24),
        (sx - sp, sy), (sx - sp*0.24, sy - sp*0.24),
    ]
    d.polygon(star_pts, fill=GOLD)

    # center pivot dot
    pr = int(s * 0.012)
    d.ellipse([cx-pr, cy-pr, cx+pr, cy+pr], fill=GOLD)

    img = img.resize((size, size), Image.LANCZOS)
    return img

def build_full_lockup(mark, canvas_w=1920, canvas_h=1080):
    """Emblem + letter-spaced wordmark, transparent background, for the
    opening/closing title card and general branded use."""
    s = canvas_w * SS, canvas_h * SS
    img = Image.new("RGBA", s, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = s[0] // 2

    mark_h = int(s[1] * 0.46)
    mark_big = mark.resize((mark_h, mark_h), Image.LANCZOS)
    mark_y = int(s[1] * 0.10)
    img.alpha_composite(mark_big, (cx - mark_h//2, mark_y))

    font_size = int(s[1] * 0.085)
    font = ImageFont.truetype(FONT_SERIF, font_size)
    tracking = int(font_size * 0.38)
    text = "ORIVANTA"
    tw = letter_spaced_width(d, text, font, tracking)
    ty = mark_y + mark_h + int(s[1] * 0.045)
    bbox = d.textbbox((0, 0), "O", font=font)
    letter_spaced(d, (cx - tw/2, ty), text, font, IVORY, tracking)

    # thin flanking rules either side of the wordmark
    rule_w = int(s[1] * 0.004)
    rule_len = int(s[0] * 0.07)
    rule_y = ty + (bbox[3]-bbox[1]) // 2
    d.line([(cx - tw/2 - int(s[0]*0.025) - rule_len, rule_y),
            (cx - tw/2 - int(s[0]*0.025), rule_y)], fill=GOLD, width=rule_w)
    d.line([(cx + tw/2 + int(s[0]*0.025), rule_y),
            (cx + tw/2 + int(s[0]*0.025) + rule_len, rule_y)], fill=GOLD, width=rule_w)

    img = img.resize((canvas_w, canvas_h), Image.LANCZOS)
    return img

def main():
    mark = draw_mark(1600)
    mark.save(f"{OUT}/orivanta_mark_transparent.png")
    print("saved orivanta_mark_transparent.png", mark.size)

    # small watermark size (persistent corner use)
    wm = mark.resize((130, 130), Image.LANCZOS)
    wm.save(f"{OUT}/orivanta_watermark_small.png")
    print("saved orivanta_watermark_small.png")

    lockup = build_full_lockup(mark, 1920, 1080)
    lockup.save(f"{OUT}/orivanta_lockup_transparent.png")
    print("saved orivanta_lockup_transparent.png", lockup.size)

    # preview composited on a dark navy background to check legibility
    bg = Image.new("RGBA", lockup.size, NAVY)
    bg.alpha_composite(lockup)
    bg.convert("RGB").save(f"{OUT}/preview_on_navy.png", quality=95)
    print("saved preview_on_navy.png")

    # small-size legibility preview (what it looks like as a watermark)
    small_preview = Image.new("RGBA", (400, 300), NAVY)
    wm_prev = mark.resize((90, 90), Image.LANCZOS)
    small_preview.alpha_composite(wm_prev, (20, 20))
    small_preview.convert("RGB").save(f"{OUT}/preview_small.png")
    print("saved preview_small.png")

if __name__ == "__main__":
    main()
