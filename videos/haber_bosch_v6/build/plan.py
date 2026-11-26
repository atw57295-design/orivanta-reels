import json, sys
sys.path.insert(0, '/home/claude/orivanta'); from edl import *
TL = json.load(open('/home/claude/orivanta/timeline.json'))
S = TL['sents']; WORDS = TL['words']
S += [{"i":142,"s":702.17,"e":702.93,"text":"In Part 2:"},{"i":143,"s":703.41,"e":706.46,"text":"how the process that fed the world kept an army fighting —"},
      {"i":144,"s":707.12,"e":711.28,"text":"and why Fritz Haber was standing behind a cloud of poison gas at Ypres."}]
AUD = 711.68
ptr = {k: v[1] for k, v in CLIPS.items()}
units = []; warn = []
for gi, (si, us) in enumerate(GROUPS):
    t0 = 0.0 if gi == 0 else S[si]['s'] - 0.12
    t1 = AUD + 0.3 if gi == len(GROUPS) - 1 else S[GROUPS[gi + 1][0]]['s'] - 0.12
    T = t1 - t0
    na = sum(1 for u in us if u[0] == 'A'); ng = sum(1 for u in us if u[0] == 'G'); clips = [u for u in us if u[0] == 'C']
    def wfill(av, tot):
        res = {k: 0.0 for k in av}; left = tot; ks = sorted(av, key=lambda k: av[k])
        for i, k in enumerate(ks):
            share = left / (len(ks) - i); res[k] = min(av[k], share); left -= res[k]
        return res
    avail0 = {u[1]: max(0, min(u[2], CLIPS[u[1]][2] - ptr[u[1]])) for u in clips}
    if ng: ad = min(3.3, T / max(1, len(us))) if na else 0
    else: ad = min(3.6, max(T / len(us), (T - sum(avail0.values())) / max(1, na))) if na else 0
    R = T - na * ad
    avail = {u[1]: max(0, min(u[2], CLIPS[u[1]][2] - ptr[u[1]])) for u in clips}
    if ng:
        gmin = 3.6 if ng == 1 else 3.2
        cl = max(0.0, R - gmin * ng); s0 = sum(avail.values()) or 1
        cd = wfill(avail, cl)
        cd = {k: min(v, 9.0) for k, v in cd.items()}
        gd = (R - sum(cd.values())) / ng
        if gd < 2.2 and clips:
            red = (2.2 - gd) * ng; s = sum(cd.values())
            cd = {k: v - red * v / s for k, v in cd.items()}; gd = 2.2
    else:
        if clips:
            s = sum(avail.values())
            if s < R - 0.05: warn.append(f"group {si}: need {R:.1f}s clips have {s:.1f}s")
            # split R proportionally to availability
            cd = wfill(avail, R)
            short = R - sum(cd.values()); gd = 0
        else: cd = {}; gd = R
    t = t0
    for u in us:
        if u[0] == 'A': d = ad
        elif u[0] == 'G': d = gd
        else: d = cd[u[1]]
        if u[0] == 'C':
            units.append(dict(type='C', key=u[1], file=CLIPS[u[1]][0], tin=round(ptr[u[1]], 3), dur=round(d, 3), t=round(t, 3)))
            ptr[u[1]] += d
        elif u[0] == 'A': units.append(dict(type='A', key=u[1], dur=round(d, 3), t=round(t, 3)))
        else: units.append(dict(type='G', kind=u[1], args=u[2], dur=round(d, 3), t=round(t, 3)))
        t += d
    if abs(t - t1) > 0.05: warn.append(f"group {si}: filled {t - t0:.2f} of {T:.2f}")
json.dump(dict(units=units, sents=S, words=WORDS), open('/home/claude/orivanta/plan.json', 'w'), ensure_ascii=False, indent=0)
tot = {k: 0 for k in 'CAG'}
for u in units: tot[u['type']] += u['dur']
print("units", len(units), {k: round(v, 1) for k, v in tot.items()})
print("long graphics:", [(u['t'], u['kind'], round(u['dur'], 1)) for u in units if u['type'] == 'G' and u['dur'] > 8])
print("short:", [(u['t'], u.get('key', u.get('kind')), u['dur']) for u in units if u['dur'] < 1.2])
print("\n".join(warn))
print("clip use:", {k: round(ptr[k] - CLIPS[k][1], 1) for k in CLIPS})
