"""ORIVANTA v6 motion graphics: every frame animated (drifting light, grain, kinetic text)."""
import numpy as np, subprocess, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
FD = "/usr/share/fonts/opentype/inter/"
GOLD = (214, 175, 92); GOLD2 = (240, 210, 140); WHITE = (244, 240, 230); DIM = (170, 160, 140)
WM = "/home/claude/orivanta/work/logo_v3_masked.png"

_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name, size)
    return _fc[k]

def ease(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3

class BG:
    def __init__(self, seed, tint=(1.0, 0.82, 0.55), dark=False):
        rng = np.random.default_rng(seed)
        bw, bh = W // 4 + 200, H // 4 + 120
        yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
        f = np.zeros((bh, bw), np.float32)
        for _ in range(7):
            cx, cy = rng.uniform(0, bw), rng.uniform(0, bh); r = rng.uniform(60, 160)
            f += rng.uniform(.3, 1) * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
        f = f / f.max() * (0.20 if dark else 0.30) + 0.035
        rgb = np.stack([f * t for t in tint], -1)
        self.big = np.array(Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).resize((bw * 4, bh * 4), Image.BICUBIC)).astype(np.float32)
        self.grain = [rng.normal(0, 7, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        self.vig = (1 - 0.55 * (((X - W / 2) / (W / 2)) ** 2 + ((Y - H / 2) / (H / 2)) ** 2) / 2)[..., None]
        self.dx, self.dy = rng.uniform(-1, 1), rng.uniform(-1, 1)
    def frame(self, t, n):
        ox = int(400 + 380 * math.sin(t * 0.09 + self.dx * 3)); oy = int(240 + 220 * math.cos(t * 0.07 + self.dy * 3))
        a = self.big[oy:oy + H, ox:ox + W] * (0.93 + 0.07 * math.sin(t * 1.7))
        g = self.grain[n % 6]; g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
        return Image.fromarray(np.clip(a * self.vig + g, 0, 255).astype(np.uint8))

def ctext(d, y, txt, font, fill, alpha=1.0, spacing=0, cx=W // 2):
    if spacing:
        widths = [d.textlength(c, font=font) + spacing for c in txt]; tw = sum(widths) - spacing; x = cx - tw / 2
        for c, w in zip(txt, widths):
            d.text((x, y), c, font=font, fill=fill + (int(255 * alpha),)); x += w
    else:
        tw = d.textlength(txt, font=font); d.text((cx - tw / 2, y), txt, font=font, fill=fill + (int(255 * alpha),))

def wrap(d, txt, font, maxw):
    out, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > maxw and cur: out.append(cur); cur = w
        else: cur = t
    if cur: out.append(cur)
    return out

def fit(d, txt, name, size, maxw):
    while size > 40 and d.textlength(txt, font=F(name, size)) > maxw: size -= 6
    return F(name, size)

# ---------------- kinds ----------------
def k_big(d, t, dur, a, ov):
    head, sub = a[0], (a[1] if len(a) > 1 else "")
    p = ease(t / 0.7); out = 1 - ease((t - (dur - 0.45)) / 0.45)
    al = p * out
    fh = fit(d, head, "InterDisplay-Bold.otf", 132, 1650)
    lines = wrap(d, head, fh, 1650)
    y0 = 400 - 70 * (len(lines) - 1) - (30 if sub else 0) + int(30 * (1 - p))
    for i, l in enumerate(lines): ctext(d, y0 + i * 150, l, fh, WHITE, al, spacing=int(4 + 3 * t / dur))
    ly = y0 + len(lines) * 150 + 20; lw = int(520 * ease((t - 0.3) / 0.9))
    d.rectangle([W // 2 - lw // 2, ly, W // 2 + lw // 2, ly + 4], fill=GOLD + (int(255 * out),))
    if sub:
        fs = F("Inter-Medium.otf", 50); sl = wrap(d, sub, fs, 1500)
        for i, l in enumerate(sl): ctext(d, ly + 40 + i * 66, l, fs, GOLD2, ease((t - 0.5) / 0.6) * out)

def k_count(d, t, dur, a, ov):
    target, suffix, sub = a[0], a[1], (a[2] if len(a) > 2 else "")
    out = 1 - ease((t - (dur - 0.45)) / 0.45); v = target * ease(t / 1.6)
    s = (f"{int(round(v)):,}" if target >= 1000 else f"{int(round(v))}") + suffix
    if a and len(a) > 3: s = a[3] + s
    ctext(d, 260 + int(20 * (1 - ease(t / .5))), s, F("InterDisplay-Black.otf", 300), GOLD2, ease(t / .4) * out)
    if sub:
        fs = F("Inter-SemiBold.otf", 58)
        for i, l in enumerate(wrap(d, sub.upper(), fs, 1500)): ctext(d, 640 + i * 76, l, fs, WHITE, ease((t - .6) / .6) * out, spacing=3)

def k_title(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.5)) / 0.5)
    ctext(d, 360, a[0], F("InterDisplay-Black.otf", 170), GOLD2, ease(t / 1.0) * out, spacing=int(10 + 14 * ease(t / dur)))
    if len(a) > 1: ctext(d, 580, a[1], F("Inter-Medium.otf", 52), WHITE, ease((t - .6) / .6) * out, spacing=6)
    if ov.get("logo"):
        lg = ov["logo"]; al = ease((t - 0.9) / .6) * out
        im = lg.copy(); im.putalpha(im.getchannel("A").point(lambda x: int(x * al)))
        ov["base"].alpha_composite(im, (W // 2 - im.width // 2, 680))

def k_date(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45)
    n = int(len(a[0]) * ease(t / 0.9))
    ctext(d, 380, a[0][:n], F("InterDisplay-ExtraBold.otf", 120 if len(a[0]) < 22 else 92), GOLD2, out, spacing=6)
    d.rectangle([W // 2 - 300, 545, W // 2 + 300, 548], fill=GOLD + (int(255 * out * ease((t - .4) / .5)),))
    if len(a) > 1:
        fs = F("Inter-Medium.otf", 54)
        for i, l in enumerate(wrap(d, a[1], fs, 1500)): ctext(d, 590 + i * 70, l, fs, WHITE, ease((t - .8) / .6) * out)

def k_card(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45); p = ease(t / .8)
    x = 220 + int(-60 * (1 - p))
    d.rectangle([x - 40, 360, x - 30, 700], fill=GOLD + (int(255 * p * out),))
    fh = fit(d, a[0], "InterDisplay-Bold.otf", 120, 1500)
    d.text((x, 380), a[0], font=fh, fill=WHITE + (int(255 * p * out),))
    if len(a) > 1:
        fs = F("Inter-Medium.otf", 52)
        for i, l in enumerate(wrap(d, a[1], fs, 1450)):
            d.text((x, 545 + i * 68), l, font=fs, fill=GOLD2 + (int(255 * ease((t - .5) / .6) * out),))
    if len(a) > 2 and a[2] == "fade":  # name fades away at end
        pass

def k_doc(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45); p = ease(t / .7)
    bx0, by0, bx1, by1 = 460, 230 + int(40 * (1 - p)), 1460, 790 + int(40 * (1 - p))
    d.rectangle([bx0, by0, bx1, by1], fill=(236, 224, 196, int(235 * p * out)), outline=GOLD + (int(255 * p * out),), width=4)
    ctext(d, by0 + 70, a[0], fit(d, a[0], "InterDisplay-Bold.otf", 76, 900), (40, 30, 20), p * out, spacing=3)
    d.rectangle([W // 2 - 250, by0 + 175, W // 2 + 250, by0 + 178], fill=(120, 90, 50, int(255 * p * out)))
    fs = F("Inter-Medium.otf", 48)
    txt = a[1]; n = int(len(txt) * ease((t - .6) / 1.4))
    for i, l in enumerate(wrap(d, txt[:n], fs, 860)): ctext(d, by0 + 230 + i * 64, l, fs, (50, 40, 30), out)

def k_mol(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45); mode = a[0]
    sep = 150
    if mode == "break":
        flash = max(0, 1 - abs(t - 1.2) / 0.25)
        if flash > 0: d.rectangle([0, 0, W, H], fill=(255, 250, 230, int(120 * flash)))
        sep = 150 + 420 * ease((t - 1.2) / 1.2)
        if 1.0 < t < 1.6:  # lightning bolt
            pts = [(W // 2 + 40, 60)]; random.seed(int(t * 30))
            for k in range(1, 9): pts.append((W // 2 + random.randint(-70, 70), 60 + k * 45))
            d.line(pts, fill=(255, 250, 220, 255), width=8)
    jit = 6 * math.sin(t * 22) if mode != "break" else 0
    cy = 470
    for s in (-1, 1):
        cx = W // 2 + s * (sep / 2 + 90) + s * jit
        d.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], fill=(60, 90, 160, int(230 * out)), outline=GOLD2 + (int(255 * out),), width=5)
        ctext(d, cy - 70, "N", F("InterDisplay-Bold.otf", 120), WHITE, out, cx=int(cx))
    if mode != "break" or t < 1.2:
        for k in (-26, 0, 26):
            d.line([W // 2 - sep / 2 - 0 + jit, cy + k, W // 2 + sep / 2 - jit, cy + k], fill=GOLD2 + (int(255 * out),), width=9)
    if len(a) > 1:
        fs = F("Inter-SemiBold.otf", 60)
        for i, l in enumerate(wrap(d, a[1], fs, 1600)): ctext(d, 680 + i * 78, l, fs, WHITE, ease((t - .5) / .6) * out, spacing=3)

def k_equil(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45)
    parts = [("N₂", WHITE), (" + ", DIM), ("3H₂", WHITE), ("  →  ", GOLD), ("2NH₃", GOLD2)]
    f = F("InterDisplay-Bold.otf", 150); tot = sum(d.textlength(p, font=f) for p, _ in parts); x = W / 2 - tot / 2
    for k, (p, c) in enumerate(parts):
        al = ease((t - 0.35 * k) / .5) * out; d.text((x, 360), p, font=f, fill=c + (int(255 * al),)); x += d.textlength(p, font=f)
    labels = a if a else ["NITROGEN + HYDROGEN → AMMONIA"]
    fs = F("Inter-SemiBold.otf", 54)
    for i, l in enumerate(labels): ctext(d, 620 + i * 74, l, fs, WHITE if i == 0 else GOLD2, ease((t - 1.6 - .5 * i) / .6) * out, spacing=3)

def k_thermo(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45); hot = a[0] == "hot"
    x0, y0, y1 = 520, 220, 820
    d.rounded_rectangle([x0 - 34, y0, x0 + 34, y1], 34, outline=WHITE + (int(255 * out),), width=6)
    lvl = ease(t / 1.6); h = (0.15 + 0.7 * lvl) if hot else (0.85 - 0.7 * lvl)
    col = (220, 90, 50) if hot else (80, 150, 230)
    d.rounded_rectangle([x0 - 22, y1 - 12 - (y1 - y0 - 24) * h, x0 + 22, y1 - 12], 22, fill=col + (int(255 * out),))
    fh = F("InterDisplay-Bold.otf", 104)
    d.text((700, 300), "HEAT IT" if hot else "COOL IT", font=fh, fill=col + (int(255 * ease(t / .6) * out),))
    fs = F("Inter-SemiBold.otf", 56)
    for i, l in enumerate(a[1:]):
        d.text((700, 470 + i * 90), l, font=fs, fill=WHITE + (int(255 * ease((t - .7 - .8 * i) / .6) * out),))

def k_coast(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45)
    # schematic, not to scale: coastline as a gently wavy vertical line
    pts = [(780 + 40 * math.sin(y / 120), y) for y in range(120, 1000, 20)]
    n = int(len(pts) * ease(t / 1.2));
    if n > 1: d.line(pts[:n], fill=GOLD2 + (int(255 * out),), width=6)
    if len(a) < 2: ctext(d, 60, "PACIFIC OCEAN", F("Inter-Medium.otf", 40), DIM, out, cx=430)
    for i, (lab, sub, y) in enumerate(a[0]):
        al = ease((t - .8 - .6 * i) / .5) * out
        d.ellipse([800 - 14, y - 14, 800 + 14, y + 14], fill=GOLD + (int(255 * al),))
        d.text((860, y - 46), lab, font=F("InterDisplay-Bold.otf", 76), fill=WHITE + (int(255 * al),))
        if sub: d.text((862, y + 40), sub, font=F("Inter-Medium.otf", 42), fill=GOLD2 + (int(255 * al),))
    d.text((60, 1000), "Schematic — not to scale", font=F("Inter-Regular.otf", 30), fill=DIM + (int(200 * out),))

def k_reactor(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45); mode = a[0]
    x0, x1, yt, yb = 260, 1660, 330, 690
    # outer jacket
    d.rectangle([x0, yt - 60, x1, yt], fill=(110, 110, 118, int(255 * out))); d.rectangle([x0, yb, x1, yb + 60], fill=(110, 110, 118, int(255 * out)))
    if mode == "lining":
        d.rectangle([x0, yt, x1, yt + 22], fill=(200, 200, 205, int(255 * out))); d.rectangle([x0, yb - 22, x1, yb], fill=(200, 200, 205, int(255 * out)))
        for x in range(x0 + 60, x1, 140):
            d.rectangle([x, yt - 60, x + 16, yt], fill=(20, 18, 15, int(255 * out))); d.rectangle([x, yb, x + 16, yb + 60], fill=(20, 18, 15, int(255 * out)))
    random.seed(7)
    for k in range(70):
        sp = random.uniform(80, 220); xx = (random.uniform(0, x1 - x0) + sp * t) % (x1 - x0) + x0
        yy = random.uniform(yt + 30, yb - 30)
        if mode == "lining" and k % 9 == 0:
            # escape through a hole
            hx = x0 + 60 + 140 * (k % 10) + 8; ph = (t * 0.6 + k * 0.13) % 1.0
            xx, yy = hx, (yt - 30 - 160 * ph) if k % 2 else (yb + 30 + 160 * ph)
        d.ellipse([xx - 9, yy - 9, xx + 9, yy + 9], fill=(120, 200, 255, int(230 * out)))
    if mode == "carbon":
        for k in range(30):
            ph = (t * 0.5 + k / 30) % 1.0; xx = x0 + 40 + (k * 47) % (x1 - x0 - 80)
            yy = yt - 40 + 120 * ph if k % 2 else yb + 40 - 120 * ph
            d.ellipse([xx - 8, yy - 8, xx + 8, yy + 8], fill=(30, 30, 30, int(255 * out)), outline=(230, 230, 230, int(200 * out)))
    if mode == "brittle":
        random.seed(3); cr = ease((t - 1.0) / 2.0)
        for k in range(6):
            x = random.randint(x0 + 100, x1 - 100); y = yt - 60 if k % 2 else yb
            pts = [(x, y + (0 if k % 2 else 60))]
            for j in range(5): pts.append((pts[-1][0] + random.randint(-30, 30), pts[-1][1] + (12 if k % 2 else -12)))
            if cr > 0: d.line(pts[:max(2, int(6 * cr))], fill=(250, 240, 220, int(255 * out)), width=4)
    ctext(d, 110, a[1], fit(d, a[1], "InterDisplay-Bold.otf", 84, 1700), WHITE, ease(t / .6) * out, spacing=3)
    if len(a) > 2:
        fs = F("Inter-SemiBold.otf", 50)
        for i, l in enumerate(wrap(d, a[2], fs, 1600)): ctext(d, 800 + i * 64, l, fs, GOLD2, ease((t - .8) / .6) * out)
    d.text((1580, 1010), "Schematic", font=F("Inter-Regular.otf", 30), fill=DIM + (int(200 * out),))

def k_list(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45)
    ctext(d, 200, a[0], fit(d, a[0], "InterDisplay-Bold.otf", 110, 1700), WHITE, ease(t / .6) * out, spacing=4)
    step = max(0.5, min(1.2, (dur - 2.0) / max(1, len(a) - 1)))
    for i, item in enumerate(a[1:]):
        al = ease((t - .8 - step * i) / .5) * out
        ctext(d, 420 + i * 120, item, F("Inter-SemiBold.otf", 72), GOLD2, al, spacing=3)

def k_swap(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45)
    f = F("InterDisplay-Black.otf", 140); m = dur * 0.45
    if t < m: ctext(d, 420, a[0], f, WHITE, ease(t / .5) * (1 - ease((t - m + .4) / .4)), spacing=6)
    else: ctext(d, 420, a[1], f, GOLD2, ease((t - m) / .5) * out, spacing=6)

def k_split(d, t, dur, a, ov):
    out = 1 - ease((t - (dur - 0.45)) / 0.45)
    for i, (h, s) in enumerate(a):
        cx = W // 4 + i * W // 2; al = ease((t - .6 * i) / .6) * out
        ctext(d, 400, h, F("InterDisplay-Bold.otf", 96), WHITE, al, cx=cx)
        ctext(d, 540, s, F("Inter-SemiBold.otf", 64), GOLD2, al, cx=cx, spacing=4)
    d.rectangle([W // 2 - 2, 330, W // 2 + 2, 700], fill=GOLD + (int(255 * out),))

def k_end(d, t, dur, a, ov):
    lg = ov["logo"]; al = ease(t / .7)
    im = lg.copy(); im.putalpha(im.getchannel("A").point(lambda x: int(x * al)))
    ov["base"].alpha_composite(im, (W // 2 - im.width // 2, 50))
    ctext(d, 370, "THE PRICE OF PROGRESS", F("Inter-SemiBold.otf", 44), GOLD2, ease((t - .4) / .6), spacing=10)
    for (x, y, w, h) in [(250, 460, 760, 428), (1230, 510, 330, 330)]:
        d.rounded_rectangle([x, y, x + w, y + h], 18, outline=GOLD + (int(200 * ease((t - .6) / .6)),), width=4)
    ctext(d, 960, "Sources in the description", F("Inter-Medium.otf", 40), DIM, ease((t - 1) / .6))

KINDS = dict(big=k_big, count=k_count, title=k_title, date=k_date, card=k_card, doc=k_doc, mol=k_mol, equil=k_equil,
             thermo=k_thermo, coast=k_coast, reactor=k_reactor, list=k_list, swap=k_swap, split=k_split, end=k_end)

def render(kind, args, dur, out, seed=0):
    bg = BG(seed, dark=(kind in ("reactor", "mol")))
    logo = None
    if kind in ("title", "end"):
        sz = 300 if kind == "end" else 190
        lg = Image.open(WM).convert("RGBA"); logo = lg.resize((sz, sz), Image.LANCZOS)
    N = int(round(dur * FPS))
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(N):
        t = n / FPS
        base = bg.frame(t, n).convert("RGBA")
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        ov = {"base": base, "logo": logo}
        KINDS[kind](d, t, dur, args, ov)
        base.alpha_composite(lay)
        p.stdin.write(base.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
