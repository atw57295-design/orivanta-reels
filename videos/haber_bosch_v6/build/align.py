import sherpa_onnx, soundfile as sf, numpy as np, json
M="/home/claude/models/sherpa-onnx-whisper-base.en/"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+"base.en-encoder.int8.onnx",decoder=M+"base.en-decoder.int8.onnx",tokens=M+"base.en-tokens.txt",num_threads=4)
a,sr=sf.read("/tmp/full16.wav",dtype="float32")
L=[l.split() for l in open("/tmp/sil.txt")]
segs=[];t=0.0
for k,v in L:
    v=float(v)
    if k=="S": segs.append((t,v))
    else: t=v
segs.append((t,len(a)/sr))
segs=[(s,e) for s,e in segs if e-s>0.15]
out=[]
for s,e in segs:
    st=rec.create_stream(); st.accept_waveform(sr,a[int(max(0,s-0.05)*sr):int((e+0.05)*sr)]); rec.decode_stream(st)
    out.append({"s":round(s,2),"e":round(e,2),"t":st.result.text.strip()})
json.dump(out,open("/home/claude/orivanta/segments.json","w"),indent=0)
print(len(out)); print("\n".join(f'{o["s"]:7.2f}-{o["e"]:7.2f} {o["t"]}' for o in out[:12]))
