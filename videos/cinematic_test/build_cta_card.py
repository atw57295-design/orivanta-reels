#!/usr/bin/env python3
"""
Build the closing Subscribe + Follow call-to-action overlay graphic.
Original design (a red rounded button + bell icon + bold "SUBSCRIBE" text,
plus plain-text follow labels for Instagram/TikTok) -- no reproduction of
any platform's official logo/wordmark/trademarked icon.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
OUT = "/home/claude/orivanta_work/videos/cinematic_test/brand_cards"

def font(path, size):
    return ImageFont.truetype(path, size)

def draw_bell(d, cx, cy, s, color=(255, 255, 255, 255)):
    # simple bell glyph
    d.pieslice([cx-s, cy-s, cx+s, cy+s*0.5], 180, 360, fill=color)
    d.rectangle([cx-s, cy-s*0.25, cx+s, cy+s*0.5], fill=color)
    d.polygon([(cx-s*1.15, cy+s*0.5), (cx+s*1.15, cy+s*0.5), (cx+s*0.9, cy+s*0.75), (cx-s*0.9, cy+s*0.75)], fill=color)
    d.ellipse([cx-s*0.22, cy+s*0.75, cx+s*0.22, cy+s*1.15], fill=color)

def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = W // 2

    # --- Small ORIVANTA circle logo up top, uncropped/undistorted ---
    logo = Image.open("/home/claude/orivanta_work/brand/v2/orivanta_watermark_small.png").convert("RGBA")
    logo_h = 96
    scale = logo_h / logo.height
    logo_w = int(logo.width * scale)
    logo_small = logo.resize((logo_w, logo_h), Image.LANCZOS)
    img.alpha_composite(logo_small, (cx - logo_w // 2, 36))

    # --- Subscribe button ---
    btn_w, btn_h = 420, 110
    bx0 = cx - btn_w // 2
    by0 = 150 + 60
    bx1 = bx0 + btn_w
    by1 = by0 + btn_h
    # soft glow behind button
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([bx0-20, by0-20, bx1+20, by1+20], radius=btn_h//2+20, fill=(224, 32, 32, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow)

    d.rounded_rectangle([bx0, by0, bx1, by1], radius=btn_h//2, fill=(214, 28, 28, 255))
    draw_bell(d, bx0 + 78, by0 + btn_h//2, 20)
    f_btn = font(FONT_BOLD, 52)
    txt = "SUBSCRIBE"
    bbox = d.textbbox((0, 0), txt, font=f_btn)
    tw = bbox[2] - bbox[0]
    d.text((bx0 + 78 + 46, by0 + btn_h//2 - (bbox[3]-bbox[1])//2 - bbox[1]), txt, font=f_btn, fill=(255, 255, 255, 255))

    # --- "ORIVANTA on YouTube" caption above button ---
    f_small = font(FONT_BOLD, 34)
    cap = "ORIVANTA on YouTube"
    bbox = d.textbbox((0, 0), cap, font=f_small)
    cw = bbox[2] - bbox[0]
    d.text((cx - cw//2, by0 - 62), cap, font=f_small, fill=(255, 255, 255, 235))

    # --- Follow line below button ---
    f_follow_label = font(FONT_BOLD, 30)
    f_follow_names = font(FONT_BOLD, 34)
    fy = by1 + 56
    line1 = "Follow ORIVANTA"
    bbox = d.textbbox((0, 0), line1, font=f_follow_label)
    lw = bbox[2] - bbox[0]
    d.text((cx - lw//2, fy), line1, font=f_follow_label, fill=(255, 255, 255, 210))

    line2 = "Instagram   •   TikTok"
    bbox = d.textbbox((0, 0), line2, font=f_follow_names)
    lw2 = bbox[2] - bbox[0]
    d.text((cx - lw2//2, fy + 46), line2, font=f_follow_names, fill=(255, 205, 90, 255))

    img.save(f"{OUT}/cta_overlay.png")
    print("saved cta_overlay.png", img.size)

if __name__ == "__main__":
    main()
