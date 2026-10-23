#!/usr/bin/env python3
# ORIVANTA paper-cutout reel engine (1080x1920, stop-motion look)
# usage: python3 engine.py episodes/epNN.json videos/epNN.mp4 [--audio voice.mp3] [--logo logo.png] [--stills dir]
import sys, json, math, random, subprocess, re, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H, FPS, TICK = 1080, 1920, 30, 3
NAVY = (13, 23, 74); BLUE = (14, 77, 185); GOLD = (234, 178, 46); AMBER = (198, 116, 19)
CREAM = (243, 232, 207); WHITE = (252, 250, 243); INK = (20, 18, 43); MOON = (8, 14, 48)
BG = {"navy": NAVY, "blue": BLUE}
PAD = 24
BIC = Image.Resampling.BICUBIC

def find_font():
    for f in ["fonts/Poppins-ExtraBold.ttf", "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"]:
        if os.path.exists(f): return f
    try:
        import urllib.request
        os.makedirs("fonts", exist_ok=True)
        urllib.request.urlretrieve("https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-ExtraBold.ttf", "fonts/Poppins-ExtraBold.ttf")
        return "fonts/Poppins-ExtraBold.ttf"
    except Exception as e:
        print("font download failed:", e)
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(f): return f
    return None

FONT = find_font()
def font(sz): return ImageFont.truetype(FONT, sz) if FONT else ImageFont.load_default(size=sz)

def shade(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)

def torn_poly(pts, rng, jag=5, step=24):
    out = []; n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
        k = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for j in range(k):
            t = j / k
            out.append((x0 + (x1 - x0) * t + rng.uniform(-jag, jag), y0 + (y1 - y0) * t + rng.uniform(-jag, jag)))
    return out

def finish(mask, fill, rim=CREAM):
    inner = mask.filter(ImageFilter.MinFilter(7))
    img = Image.new("RGBA", mask.size, rim + (0,))
    img.paste(Image.new("RGBA", mask.size, rim + (255,)), (0, 0), mask)
    img.paste(Image.new("RGBA", mask.size, fill + (255,)), (0, 0), inner)
    return img

def layer_from_poly(pts, fill, rim=CREAM):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = min(xs) - PAD, min(ys) - PAD
    w, h = int(max(xs) - min(xs) + 2 * PAD), int(max(ys) - min(ys) + 2 * PAD)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    return finish(m, fill, rim)

def torn_circle(R, fill, rng, rim=CREAM):
    n = 56
    pts = [(R + (R + rng.uniform(-4, 4)) * math.cos(2 * math.pi * i / n),
            R + (R + rng.uniform(-4, 4)) * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return layer_from_poly(pts, fill, rim)

def star_layer(R, fill, rim=CREAM):
    pts = []
    for i in range(10):
        r = R if i % 2 == 0 else R * 0.42
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((R + r * math.cos(a), R + r * math.sin(a)))
    return layer_from_poly(pts, fill, rim)

def gear_layer(R, teeth, fill):
    size = int(2 * R * 1.1) + 2 * PAD; c = size / 2
    m = Image.new("L", (size, size), 0); d = ImageDraw.Draw(m); pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        r = R if i % 4 in (1, 2) else R * 0.82
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=255)
    d.ellipse((c - R * .35, c - R * .35, c + R * .35, c + R * .35), fill=0)
    return finish(m, fill)

def chip(text, sz, fill, ink, rng, padx=28):
    f = font(sz)
    l, t, r, b = f.getbbox(text)
    w, h = (r - l) + 2 * padx, int(sz * 1.32)
    lay = layer_from_poly(torn_poly([(0, 0), (w, 0), (w, h), (0, h)], rng, jag=3, step=18), fill)
    ImageDraw.Draw(lay).text((lay.width / 2, lay.height / 2 + sz * 0.04), text, font=f, fill=ink, anchor="mm")
    return lay

def comp(cv, im, x, y):
    X0, Y0 = max(0, x), max(0, y); X1, Y1 = min(cv.width, x + im.width), min(cv.height, y + im.height)
    if X0 >= X1 or Y0 >= Y1: return
    cv.alpha_composite(im.crop((X0 - x, Y0 - y, X1 - x, Y1 - y)), (X0, Y0))

def place(cv, im, cx, cy, ang=0, sc=1.0, sh=True):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), BIC)
    if ang: im = im.rotate(ang, resample=BIC, expand=True)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    if sh:
        a = im.getchannel("A").filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .45))
        s = Image.new("RGBA", im.size, (0, 0, 0, 0)); s.putalpha(a)
        comp(cv, s, x + 7, y + 12)
    comp(cv, im, x, y)

def make_bg(color, seed):
    rng = random.Random(seed)
    im = Image.new("RGBA", (W, H), color + (255,)); d = ImageDraw.Draw(im)
    for lo, hi, f, drop in ((700, 1000, 1.18, (150, 380)), (1300, 1600, 0.78, (120, 300))):
        y = rng.randint(lo, hi)
        pts = torn_poly([(-40, y), (W + 40, y - rng.randint(*drop)), (W + 40, H + 40), (-40, H + 40)], rng, 6, 30)
        d.polygon([(x, yy + 14) for x, yy in pts], fill=shade(color, 0.55))
        d.polygon(pts, fill=shade(color, f))
    dc = shade(color, 1.35)
    for gx in range(14):
        for gy in range(10):
            r = 3 + 6 * (1 - gy / 10) * (0.4 + 0.6 * gx / 14)
            x, y = 640 + gx * 30, 130 + gy * 30
            d.ellipse((x - r, y - r, x + r, y + r), fill=dc)
    return im

def make_logo(path):
    if path and os.path.exists(path):
        im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(int)
        ys, xs = np.where(a.sum(2) < 740)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        s = max(x1 - x0, y1 - y0) + 1; cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        crop = im.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)).convert("RGBA")
    else:
        s = 560; crop = Image.new("RGBA", (s, s), NAVY + (255,)); d = ImageDraw.Draw(crop)
        d.ellipse((60, 40, 500, 480), outline=GOLD, width=70)
        d.ellipse((150, 120, 410, 400), outline=BLUE, width=26)
        f = font(60); d.text((s / 2, 500), "ORIVANTA", font=f, fill=GOLD, anchor="mm")
    mask = Image.new("L", crop.size, 0); ImageDraw.Draw(mask).ellipse((0, 0, crop.width - 1, crop.height - 1), fill=255)
    crop.putalpha(mask)
    return crop

def parse(text):
    words = []; key = False
    for tok in text.split():
        if tok.startswith("*"): key = True
        words.append((tok.strip("*"), key))
        if tok.endswith("*"): key = False
    return words

def build_scene(sc, i, logo):
    words = parse(sc["text"]); n = len(words)
    sz = 104 if n <= 5 else 88
    chips, ang = [], []
    for k, (w, key) in enumerate(words):
        r = random.Random(i * 100 + k)
        if key: fill, ink = GOLD, NAVY
        else: fill, ink = (CREAM, INK) if k % 2 == 0 else (WHITE, INK)
        chips.append(chip(w, sz, fill, ink, r)); ang.append(r.uniform(-2.6, 2.6))
    gap = 16; lh = int(sz * 1.32) + gap; lines = []; cur = []; cw = 0
    for k, c in enumerate(chips):
        w = c.width - 2 * PAD
        nw = cw + (gap if cur else 0) + w
        if cur and nw > 960: lines.append(cur); cur = []; nw = w
        cur.append(k); cw = nw
    lines.append(cur)
    pos = {}; y = 1130 - len(lines) * lh / 2 + lh / 2
    for ln in lines:
        ws = [chips[k].width - 2 * PAD for k in ln]; tot = sum(ws) + gap * (len(ln) - 1); x = W / 2 - tot / 2
        for k, w in zip(ln, ws): pos[k] = (x + w / 2, y); x += w + gap
        y += lh
    wts = [len(w) + 2 for w, _ in words]; tot = sum(wts); cum = 0; times = []
    for wt in wts: times.append(cum / tot); cum += wt
    mo = sc.get("motif") or ["logo"]
    kind, arg = mo[0], (str(mo[1]) if len(mo) > 1 else "")
    r = random.Random(7 + i); m = {}
    if kind == "number": m["num"] = chip(arg, 330 if len(arg) <= 5 else 230, GOLD, NAVY, r, padx=40)
    elif kind == "gear":
        m["g1"] = gear_layer(250, 14, AMBER); m["g2"] = gear_layer(120, 9, GOLD); m["g3"] = gear_layer(80, 7, CREAM)
    elif kind == "waves":
        m["sun"] = torn_circle(120, GOLD, r)
        for j, col in enumerate(((30, 100, 210), (14, 77, 185), (10, 50, 140))):
            m["w%d" % j] = layer_from_poly(torn_poly([(0, 0), (1300, 0), (1300, 170), (0, 170)], r, 5, 26), col)
    elif kind == "eclipse":
        m["sun"] = torn_circle(190, GOLD, r); m["moon"] = torn_circle(172, MOON, r)
        m["st"] = star_layer(34, GOLD)
    else:
        kind = "logo"
        m["logo"] = logo.resize((560, 560), Image.Resampling.LANCZOS); m["st"] = star_layer(40, GOLD)
    bgc = BG.get(sc.get("bg", "navy"), NAVY)
    return dict(words=words, chips=chips, ang=ang, pos=pos, times=times, kind=kind, m=m, bg=make_bg(bgc, 900 + i))

def draw_motif(cv, S, t, dur):
    k, m, cy = S["kind"], S["m"], 560
    pop = 1 + 0.25 * max(0, 1 - t / 0.3) ** 2
    if k == "number":
        place(cv, m["num"], W / 2, cy, -4 + 1.5 * math.sin(t * 3), pop)
    elif k == "gear":
        place(cv, m["g1"], W / 2 - 110, cy, t * 22, pop)
        place(cv, m["g2"], W / 2 + 215, cy + 175, -t * 40, pop)
        place(cv, m["g3"], W / 2 - 330, cy - 215, -t * 55, pop)
    elif k == "waves":
        place(cv, m["sun"], W / 2 + 230, cy - 180, 0, pop)
        for j, yy in enumerate((cy + 20, cy + 110, cy + 200)):
            place(cv, m["w%d" % j], W / 2 + 25 * math.sin(t * 2 + j * 1.7), yy + 9 * math.sin(t * 2.6 + j), 0, 1)
    elif k == "eclipse":
        p = min(1.0, t / max(dur, .1) * 1.25)
        place(cv, m["sun"], W / 2, cy, t * 6, pop)
        place(cv, m["moon"], W / 2 - 360 * (1 - p), cy + 10, 0, 1)
        for j, (dx, dy) in enumerate(((-380, -230), (360, -250), (-400, 200), (390, 215), (0, -330))):
            place(cv, m["st"], W / 2 + dx, cy + dy, (t * 90 + j * 30) % 360, 0.7 + 0.3 * math.sin(t * 5 + j))
    else:
        place(cv, m["logo"], W / 2, cy, 3 * math.sin(t * 3), pop)
        for j, (dx, dy) in enumerate(((-340, -300), (350, -280), (-360, 280), (370, 300))):
            place(cv, m["st"], W / 2 + dx, cy + dy, (t * 80 + j * 40) % 360, 0.8 + 0.3 * math.sin(t * 5 + j))

def est(sc): return max(2.4, len(sc["text"].split()) * 0.40 + 0.5)

def retime(audio, durs):
    out = subprocess.run(["ffmpeg", "-i", audio, "-af", "silencedetect=noise=-32dB:d=0.28", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    hh, mm, ss = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    total = int(hh) * 3600 + int(mm) * 60 + float(ss)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    cuts = [(s + e) / 2 for s, e in zip(st, en) if s > 0.3 and e < total - 0.1]
    n = len(durs)
    if len(cuts) == n - 1:
        b = [0] + cuts + [total]; print("retimed from audio silences")
        return [b[i + 1] - b[i] for i in range(n)]
    k = total / sum(durs); print("silence count mismatch (%d vs %d): scaled estimates" % (len(cuts), n - 1))
    return [d * k for d in durs]

def main():
    a = sys.argv[1:]
    ep, out = a[0], a[1]
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    logo = make_logo(opt("--logo") or "logo.png"); badge = logo.resize((120, 120), Image.Resampling.LANCZOS)
    scenes = json.load(open(ep))["scenes"]
    durs = [est(s) for s in scenes]; audio = opt("--audio")
    if audio: durs = retime(audio, durs)
    starts = [sum(durs[:i]) for i in range(len(durs))]; total = sum(durs)
    S = [build_scene(s, i, logo) for i, s in enumerate(scenes)]

    def frame(tick):
        t = tick / 10.0
        i = max(j for j in range(len(durs)) if starts[j] <= t + 1e-6)
        lt = t - starts[i]; sc = S[i]
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        if i > 0 and lt < 0.4:
            cv.alpha_composite(S[i - 1]["bg"])
            p = (lt + 0.1) / 0.4; r = random.Random(i); top = H * (1 - p)
            pts = torn_poly([(-30, top), (W + 30, top - 60), (W + 30, H + 30), (-30, H + 30)], r, 8, 28)
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
            cv.paste(sc["bg"], (0, 0), m)
        else:
            cv.alpha_composite(sc["bg"])
        draw_motif(cv, sc, lt, durs[i])
        for k in range(len(sc["words"])):
            tk = 0.15 + sc["times"][k] * durs[i] * 0.78
            if lt >= tk:
                age = lt - tk; r = random.Random(tick * 31 + k)
                pop = 1 + 0.28 * max(0, 1 - age / 0.25) ** 2
                x, y = sc["pos"][k]
                place(cv, sc["chips"][k], x + r.uniform(-2, 2), y + r.uniform(-2, 2), sc["ang"][k] + r.uniform(-.6, .6), pop)
        place(cv, badge, 110, 190, 0, 1)
        arr = np.asarray(cv.convert("RGB")).astype(np.int16)
        arr += np.random.default_rng(tick).normal(0, 3, (H, W, 1)).astype(np.int16)
        return np.clip(arr, 0, 255).astype(np.uint8)

    still_dir = opt("--stills")
    if still_dir:
        os.makedirs(still_dir, exist_ok=True)
        for i in range(len(durs)):
            Image.fromarray(frame(int((starts[i] + durs[i] * 0.85) * 10))).save(os.path.join(still_dir, "scene%02d.png" % (i + 1)))
        print("stills saved; total %.1fs" % total); return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-"]
    if audio: cmd += ["-i", audio]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-preset", "veryfast"]
    if audio: cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += [out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for tk in range(int(math.ceil(total * 10))):
        b = frame(tk).tobytes()
        for _ in range(TICK): p.stdin.write(b)
    p.stdin.close(); p.wait(); print("done %.1fs -> %s" % (total, out))

if __name__ == "__main__":
    main()
