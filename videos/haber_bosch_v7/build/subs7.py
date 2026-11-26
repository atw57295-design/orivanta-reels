import json, re, sys
sys.path.insert(0,'/home/claude/orivanta'); from numfix import fix
sys.path.insert(0, '/home/claude/orivanta'); from edl import OST
P = json.load(open('/home/claude/orivanta/plan.json')); S = P['sents']; Wd = P['words']; U = P['units']
A1,B1,A2=238.2,7247/30,21062/30
D1=B1-A1
def mp(t):
    if t<=A1: return t
    if t<B1: return A1
    return min(t-D1, A2-D1+0.0)
def ts(t):
    t=mp(t)
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
# map words to sentences in order
wi = 0; sw = []
for k, s in enumerate(S):
    n = len(s['text'].split()) if k < 142 else 0
    sw.append(Wd[wi:wi + n]); wi += n
def chunks(k):
    s = S[k]; words = sw[k]
    if not words or len(s['text']) <= 84: return [(s['s'], s['text'])]
    toks = [w[0] for w in words]; out = []; cur = []
    total = len(s['text']); target = total / max(2, round(total / 70))
    for j, w in enumerate(toks):
        cur.append(j); txt = " ".join(toks[c] for c in cur)
        if (re.search(r"[,:;—]$", w) or toks[min(j + 1, len(toks) - 1)] == "—") and len(txt) >= target * 0.6 and j < len(toks) - 2:
            out.append(cur); cur = []
        elif len(txt) > 84 and len(cur) > 1:
            last = cur.pop(); out.append(cur); cur = [last]
    if cur:
        if out and len(" ".join(toks[c] for c in cur)) < 18: out[-1] += cur
        else: out.append(cur)
    return [(words[c[0]][1], " ".join(toks[x] for x in c)) for c in out]
ev = []
DROP={53,142,143,144}
for k, s in enumerate(S):
    if k in DROP: continue
    nxt = S[k + 1]['s'] if k + 1 < len(S) else s['e'] + 0.8
    ch = chunks(k)
    for j, (t0, txt) in enumerate(ch):
        t1 = ch[j + 1][0] if j + 1 < len(ch) else min(s['e'] + 0.35, nxt - 0.02)
        txt = fix(txt.lstrip("\u2014 ").strip())
        ev.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Sub,,0,0,0,,{txt}")
# OST only over footage/archive
for k, txt in OST.items():
    if k in (53,142,143,144): continue
    s = S[k]; a, b = s['s'] - 0.05, max(s['e'] + 0.5, s['s'] + 2.5)
    if k + 1 < len(S): b = min(b, S[k + 1]['s'] + 1.5)
    for u in U:
        if u['type'] == 'G': continue
        x0, x1 = max(a, u['t']), min(b, u['t'] + u['dur'])
        if x1 - x0 >= 0.9:
            ev.append(f"Dialogue: 1,{ts(x0)},{ts(x1)},OST,,0,0,0,,{{\\fad(200,200)}}{txt}")
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter SemiBold,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,4,1,2,140,140,70,1
Style: OST,Inter Display Bold,54,&H0070D0F5,&H00FFFFFF,&H50000000,&H50000000,0,0,0,0,100,100,3,0,3,16,0,8,200,200,64,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open('/home/claude/orivanta/v6/v7.ass', 'w').write(head + "\n".join(ev) + "\n")
print(len(ev), "events")
mx = max((len(e.split(',,', 1)[1].split(',,')[-1]) for e in ev if ',Sub,' in e)); print("max sub chars", mx)
