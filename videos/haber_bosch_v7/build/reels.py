import json, subprocess, os, re, sys
sys.path.insert(0,'/home/claude/orivanta'); from numfix import fix
from PIL import Image, ImageDraw, ImageFont
O = "/home/claude/orivanta/v6/reels/"; os.makedirs(O, exist_ok=True)
V = "/home/claude/orivanta/v6/video_raw7.mp4"; AUD = "/home/claude/orivanta/v6/mix7.wav"
FD = "/usr/share/fonts/opentype/inter/"
LOGO = Image.open("/home/claude/orivanta/work/logo_v3_masked.png").convert("RGBA")
P = json.load(open("/home/claude/orivanta/plan.json")); S = P["sents"]; Wd = P["words"]
A1, B1 = 238.2, 7247 / 30; D1 = B1 - A1
def mp(t): return t if t <= A1 else t - D1
REELS = [  # id, first sentence, last sentence, hook
 ("R1", 0, 10, "BY SOME ESTIMATES, HALF YOUR BODY'S NITROGEN CAME FROM A MACHINE"),
 ("R2", 26, 34, "THE WAR THAT COST BOLIVIA ITS COASTLINE"),
 ("R3", 47, 52, "SHE MADE HISTORY IN 1900. THEN HER WORK WAS PUT ASIDE"),
 ("R4", 59, 64, "HIS NUMBERS WERE CALLED “VERY INACCURATE” IN PUBLIC"),
 ("R5", 71, 79, "2 JULY 1909: AMMONIA FROM THE AIR, DROP BY DROP"),
 ("R6", 88, 93, "HIS NAME IS ON THE PATENT. HISTORY FORGOT HIM"),
 ("R7", 110, 117, "THE STEEL TUBES BURST AFTER 80 HOURS"),
]
PLAT = {"youtube": "SUBSCRIBE · ORIVANTA", "tiktok": "FOLLOW @orivanta2", "instagram": "FOLLOW @orivanta.studio", "facebook": "FOLLOW ORIVANTA"}
GOLD = (232, 184, 109); IVORY = (242, 239, 230)
def F(n, s): return ImageFont.truetype(FD + n, s)
def wrap(d, txt, f, mw):
    out, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > mw and cur: out.append(cur); cur = w
        else: cur = t
    return out + [cur]
def layer_content(hook):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = LOGO.resize((120, 120), Image.LANCZOS); im.alpha_composite(lg, (480, 120))
    size = 80
    while True:
        f = F("InterDisplay-Black.otf", size); lines = wrap(d, hook, f, 940)
        if len(lines) <= 3 or size < 56: break
        size -= 6
    y = 610 - len(lines) * (size + 14)
    for l in lines:
        w = d.textlength(l, font=f); d.text(((1080 - w) / 2, y), l, font=f, fill=IVORY, stroke_width=4, stroke_fill=(0, 0, 0)); y += size + 14
    return im
def badge(txt):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = F("Inter-Bold.otf", 40)
    w = d.textlength(txt, font=f); x0 = (1080 - w) / 2 - 34
    d.rounded_rectangle([x0, 1430, x0 + w + 68, 1500], 35, fill=(11, 27, 40, 215), outline=GOLD, width=3)
    d.text((x0 + 34, 1442), txt, font=f, fill=GOLD); return im
def endcard(txt):
    im = Image.new("RGB", (1080, 1920), (11, 27, 40)).convert("RGBA"); d = ImageDraw.Draw(im)
    lg = LOGO.resize((420, 420), Image.LANCZOS); im.alpha_composite(lg, (330, 520))
    for i, (s, f, c) in enumerate([("FULL STORY", F("InterDisplay-Black.otf", 92), IVORY), ("ON ORIVANTA", F("InterDisplay-Black.otf", 92), GOLD)]):
        w = d.textlength(s, font=f); d.text(((1080 - w) / 2, 1010 + i * 110), s, font=f, fill=c)
    im.alpha_composite(badge(txt).crop((0, 0, 1080, 1920)), (0, -70)); return im
def ts(t):
    t = max(0, t); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
def subs(a, b, t0, path):
    # sentence chunks (<=42 chars per line, 2 lines) using word timings
    ev = []
    wi = 0
    for k, s in enumerate(S[:142]):
        n = len(s["text"].split()); ws = Wd[wi:wi + n]; wi += n
        if k < a or k > b: continue
        cur = []
        for j, w in enumerate(ws):
            cur.append(w); txt = " ".join(x[0] for x in cur)
            end = j == len(ws) - 1
            rest = " ".join(x[0] for x in ws[j + 1:])
            if not end and 0 < len(fix(rest)) < 24 and len(fix(txt)) + len(fix(rest)) < 74: continue
            if end or len(txt) > 52 or (re.search(r"[,:;—.?]$", w[0]) and len(txt) > 24):
                t1 = ws[j + 1][1] if not end else s["e"] + 0.3
                ev.append(f"Dialogue: 0,{ts(mp(cur[0][1]) - t0)},{ts(mp(t1) - t0)},Sub,,0,0,0,,{fix(txt.lstrip(chr(8212)+' '))}"); cur = []
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter SemiBold,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,4,1,8,90,90,1290,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(path, "w").write(head + "\n".join(ev) + "\n")
def run(c): subprocess.run(c, check=True)
import sys
ONLY = sys.argv[1:]
for rid, a, b, hook in [r for r in REELS if not ONLY or r[0] in ONLY]:
    t0 = 0.0 if a == 0 else mp(S[a]["s"] - 0.15); t1 = mp(S[b]["e"] + 0.55); dur = t1 - t0
    layer_content(hook).save(f"/tmp/{rid}_layer.png"); subs(a, b, t0, f"/tmp/{rid}.ass")
    base = f"/tmp/{rid}_base.mp4"
    fc = ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2,eq=brightness=-0.32[bg];"
          "[b]scale=1080:608[fg];[bg][fg]overlay=0:660[v1];[v1][1:v]overlay=0:0[v2];"
          f"[v2]ass=/tmp/{rid}.ass,fps=30,format=yuv420p[v]")
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", V, "-i", f"/tmp/{rid}_layer.png",
         "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", base])
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", AUD, "-af",
         f"afade=t=in:d=0.08,afade=t=out:st={dur - 0.35:.3f}:d=0.35", f"/tmp/{rid}_a.wav"])
    for pk, ptxt in PLAT.items():
        badge(ptxt).save(f"/tmp/badge_{pk}.png"); endcard(ptxt).convert("RGB").save(f"/tmp/end_{pk}.png")
        out = f"{O}ORIVANTA_{rid}_{pk}.mp4"
        fc = (f"[0:v][1:v]overlay=0:0[c];[2:v]scale=1080:1920,zoompan=z='1+0.03*on/90':d=1:s=1080x1920:fps=30,format=yuv420p,setsar=1[e];"
              f"[c]setsar=1[c2];[c2][e]concat=n=2:v=1:a=0[v];"
              f"[3:a]apad=pad_dur=3[a0];[a0]loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", base, "-i", f"/tmp/badge_{pk}.png", "-loop", "1", "-t", "3", "-framerate", "30", "-i", f"/tmp/end_{pk}.png",
             "-i", f"/tmp/{rid}_a.wav", "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    print(rid, round(dur + 3, 1), flush=True)
print("DONE")
