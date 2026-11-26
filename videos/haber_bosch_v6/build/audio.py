import numpy as np, soundfile as sf, subprocess, json
SR = 48000; M = "/home/claude/orivanta-reels/videos/cinematic_test/music_sfx_audio/"
NARR = "/home/claude/orivanta-reels/audio/haber_bosch_part1_steven/Steven_Part1_full_narration.mp3"
TOTAL = 724.0
def load(p):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", p, "-ar", str(SR), "-ac", "1", "/tmp/_a.wav"], check=True)
    a, _ = sf.read("/tmp/_a.wav", dtype="float32"); return a
def loop(a, n, xf=1.5):
    x = int(xf * SR); out = np.zeros(n + len(a), np.float32); pos = 0
    fin = np.linspace(0, 1, x, dtype=np.float32)
    while pos < n:
        seg = a.copy()
        if pos > 0: seg[:x] *= fin
        seg[-x:] *= fin[::-1]
        out[pos:pos + len(seg)] += seg; pos += len(a) - x
    return out[:n]
narr = load(NARR)
cues = {k: load(M + f"music_{k}_cue.wav") for k in ("first_signal", "breakthrough", "moral_shadow", "legacy")}
for k in cues: cues[k] /= (np.abs(cues[k]).max() + 1e-6)
SECT = [(0, 24.5, "moral_shadow"), (24.5, 181, "first_signal"), (181, 453, "breakthrough"), (453, 636, "first_signal"),
        (636, 668.5, "legacy"), (668.5, 711.8, "moral_shadow"), (711.8, TOTAL, "legacy")]
N = int(TOTAL * SR); mus = np.zeros(N, np.float32); xf = int(2 * SR)
for a, b, k in SECT:
    s0 = max(0, int(a * SR) - xf // 2); s1 = min(N, int(b * SR) + xf // 2); seg = loop(cues[k], s1 - s0)
    r = np.linspace(0, 1, xf, dtype=np.float32); seg[:xf] *= r; seg[-xf:] *= r[::-1]
    mus[s0:s1] += seg
# ducking envelope from narration
env = np.zeros(N, np.float32); nv = np.zeros(N, np.float32); nv[:len(narr)] = narr[:N]
win = int(0.05 * SR); rms = np.sqrt(np.convolve(nv ** 2, np.ones(win) / win, mode="same"))
speech = (rms > 0.01).astype(np.float32)
sm = int(0.4 * SR); speech = np.convolve(speech, np.ones(sm) / sm, mode="same")
gain = 0.16 - 0.10 * np.clip(speech, 0, 1)   # ~-16 dB bed, ~-24 dB under voice
gain[int(711.8 * SR):] = 0.30
mus *= gain
# ambience under footage units
P = json.load(open("/home/claude/orivanta/plan.json"))
fac = load(M + "sfx_factory_ambience_1913.wav"); war = load(M + "sfx_wwi_trench_ambience.wav")
fac /= np.abs(fac).max(); war /= np.abs(war).max()
FAC = {"FI", "VA", "IN", "AE", "DU", "F1", "GA", "BK", "LO", "ST", "SH", "MU", "CT"}; WAR = {"GC", "GM", "YP"}
amb = np.zeros(N, np.float32)
for u in P["units"]:
    if u["type"] != "C": continue
    src = fac if u["key"] in FAC else war if u["key"] in WAR else None
    if src is None: continue
    s0 = int(u["t"] * SR); n = int(u["dur"] * SR); seg = loop(src, n, 0.5)
    f = min(int(0.25 * SR), n // 2); r = np.linspace(0, 1, f, dtype=np.float32); seg[:f] *= r; seg[n - f:] *= r[::-1]
    amb[s0:s0 + n] += seg * 0.07
mix = nv * 1.0 + mus + amb
mix /= max(1.0, np.abs(mix).max() / 0.95)
sf.write("/home/claude/orivanta/v6/mix.wav", np.stack([mix, mix], 1), SR)
print("ok", len(mix) / SR)
