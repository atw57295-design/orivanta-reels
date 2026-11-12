#!/usr/bin/env python3
"""
Documentary-style location/date/diagram insert cards, in the spirit of the
reference channels (Real Engineering, Wendover Productions, Kings and
Generals): bold title + date/subtitle + a simple line-art icon, on the
ORIVANTA brand's dark-navy/aged-gold palette, with the small new watermark
for consistency. These are brief cutaways spliced into the relevant scene's
video track (narration keeps playing underneath) to break up the all-video
rhythm with the data/diagram/location beats the reference study asked for.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/claude/orivanta_work"
OUT = f"{ROOT}/videos/cinematic_test/brand_cards/info"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720
NAVY_TOP = (14, 18, 30)
NAVY_BOT = (6, 8, 14)
GOLD = (196, 163, 92, 255)
IVORY = (235, 228, 210, 255)
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
WATERMARK = f"{ROOT}/brand/v2/orivanta_watermark_small.png"

def make_bg():
    bg = Image.new("RGB", (W, H), NAVY_BOT)
    px = bg.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(NAVY_TOP[0]*(1-t) + NAVY_BOT[0]*t)
        g = int(NAVY_TOP[1]*(1-t) + NAVY_BOT[1]*t)
        b = int(NAVY_TOP[2]*(1-t) + NAVY_BOT[2]*t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return bg.convert("RGBA")

def frame(img, margin=46):
    d = ImageDraw.Draw(img)
    d.rectangle([margin, margin, W-margin, H-margin], outline=GOLD, width=2)
    cl = 34
    for (cx, cy, dx, dy) in [(margin, margin, 1, 1), (W-margin, margin, -1, 1),
                              (margin, H-margin, 1, -1), (W-margin, H-margin, -1, -1)]:
        d.line([(cx-dx*cl, cy), (cx, cy)], fill=GOLD, width=4)
        d.line([(cx, cy-dy*cl), (cx, cy)], fill=GOLD, width=4)
    return img

def watermark_corner(img):
    wm = Image.open(WATERMARK).convert("RGBA")
    img.alpha_composite(wm, (W - wm.width - 30, 30))
    return img

def centered_text(d, y, text, font, fill, tracking=0):
    if tracking:
        w = sum(d.textlength(c, font=font) for c in text) + tracking*(len(text)-1)
        x = (W - w) / 2
        for c in text:
            d.text((x, y), c, font=font, fill=fill)
            x += d.textlength(c, font=font) + tracking
    else:
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        d.text(((W - w) / 2, y), text, font=font, fill=fill)

def draw_pin_icon(d, cx, cy, s, color=GOLD):
    d.ellipse([cx-s, cy-s*1.3, cx+s, cy+s*0.7], outline=color, width=5)
    d.polygon([(cx-s*0.5, cy+s*0.35), (cx+s*0.5, cy+s*0.35), (cx, cy+s*1.3)], outline=color)
    d.ellipse([cx-s*0.35, cy-s*0.65, cx+s*0.35, cy+s*0.05], fill=color)

def draw_factory_icon(d, cx, cy, s, color=GOLD):
    base_y = cy + s*0.5
    d.rectangle([cx-s, base_y-s*0.6, cx+s, base_y+s*0.1], outline=color, width=5)
    d.polygon([(cx-s*0.7, base_y-s*0.6), (cx-s*0.4, base_y-s*1.1), (cx-s*0.1, base_y-s*0.6)], outline=color, width=4)
    d.polygon([(cx+s*0.1, base_y-s*0.6), (cx+s*0.35, base_y-s*1.3), (cx+s*0.6, base_y-s*0.6)], outline=color, width=4)
    for sx in (cx-s*0.6, cx-s*0.2, cx+s*0.2, cx+s*0.6):
        d.rectangle([sx-14, base_y-s*0.4, sx+14, base_y-s*0.15], outline=color, width=3)

def location_card(title, subtitle, icon_fn, filename):
    img = make_bg()
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(FONT_BOLD, 76)
    f_sub = ImageFont.truetype(FONT_REG, 36)

    icon_fn(d, W//2, 250, 56)

    centered_text(d, 340, title, f_title, IVORY, tracking=6)
    centered_text(d, 430, subtitle, f_sub, GOLD)

    img = frame(img)
    img.convert("RGB").save(f"{OUT}/{filename}", quality=95)
    print("saved", filename)

def equation_card(filename):
    img = make_bg()
    d = ImageDraw.Draw(img)
    f_small_cap = ImageFont.truetype(FONT_BOLD, 34)
    f_eq = ImageFont.truetype(FONT_BOLD, 92)
    f_sub = ImageFont.truetype(FONT_REG, 32)

    centered_text(d, 180, "THE HABER PROCESS", f_small_cap, GOLD, tracking=8)

    eq = "N₂  +  3H₂    →    2NH₃"
    centered_text(d, 290, eq, f_eq, IVORY)

    centered_text(d, 430, "High pressure  ·  high temperature  ·  iron catalyst", f_sub, GOLD)

    img = frame(img)
    img.convert("RGB").save(f"{OUT}/{filename}", quality=95)
    print("saved", filename)

def main():
    location_card("PERU · CHILE · BOLIVIA", "The War of the Pacific, 1879–1884",
                   draw_pin_icon, "card_war_of_pacific.png")
    equation_card("card_haber_equation.png")
    location_card("OPPAU, GERMANY", "1913 — the first full-scale ammonia plant",
                   draw_factory_icon, "card_oppau.png")
    location_card("YPRES, BELGIUM", "April 1915", draw_pin_icon, "card_ypres.png")

if __name__ == "__main__":
    main()
