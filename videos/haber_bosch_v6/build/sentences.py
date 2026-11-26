import json,re,difflib
segs=json.load(open("/home/claude/orivanta/segments.json"))
script=" ".join(open(f"/home/claude/orivanta-reels/audio/haber_bosch_part1_steven/tts_0{i}.txt").read().replace("\n"," ") for i in range(8))
script=re.sub(r"\s+"," ",script).strip()
norm=lambda w:re.sub(r"[^a-z0-9]","",w.lower())
sw=script.split(); swn=[norm(w) for w in sw]
ww=[];wseg=[]
for i,s in enumerate(segs):
    for w in s["t"].split(): ww.append(norm(w)); wseg.append(i)
sm=difflib.SequenceMatcher(None,swn,ww,autojunk=False)
s2w=[None]*len(sw)
for a,b,n in sm.get_matching_blocks():
    for k in range(n): s2w[a+k]=b+k
# time per script word: interpolate within segments
segof=[None]*len(sw)
for i,j in enumerate(s2w):
    if j is not None: segof[i]=wseg[j]
# fill gaps forward/back
last=0
for i in range(len(sw)):
    if segof[i] is None: segof[i]=last
    else: last=segof[i]
# word timing: within a segment, distribute by chars
from collections import defaultdict
bys=defaultdict(list)
for i,s in enumerate(segof): bys[s].append(i)
wt=[None]*len(sw)
for s,idx in bys.items():
    st,en=segs[s]["s"],segs[s]["e"]; tot=sum(len(sw[i])+1 for i in idx); acc=0
    for i in idx:
        a=st+(en-st)*acc/tot; acc+=len(sw[i])+1; b=st+(en-st)*acc/tot; wt[i]=(a,b)
# sentences
sents=[];cur=[]
for i,w in enumerate(sw):
    cur.append(i)
    if re.search(r"[.?!]$",w) and not re.search(r"\.\.\.$",w) or i==len(sw)-1:
        sents.append(cur);cur=[]
S=[{"i":k,"s":round(wt[c[0]][0],2),"e":round(wt[c[-1]][1],2),"text":" ".join(sw[j] for j in c)} for k,c in enumerate(sents)]
json.dump({"words":[[sw[i],round(wt[i][0],2),round(wt[i][1],2)] for i in range(len(sw))],"sents":S},open("/home/claude/orivanta/timeline.json","w"))
for x in S: print(f'{x["i"]:3d} {x["s"]:6.1f}-{x["e"]:6.1f} {x["text"][:70]}')
