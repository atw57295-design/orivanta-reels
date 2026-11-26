import json, os, subprocess, sys
sys.path.insert(0, '/home/claude/orivanta'); import gfx
from edl import ARCH
P = json.load(open('/home/claude/orivanta/plan.json')); U = P['units']
SRC = "/home/claude/orivanta-reels/videos/cinematic_test/"
OUT = "/home/claude/orivanta/v6/units/"; os.makedirs(OUT, exist_ok=True)
FPS = 30
only = set(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else None
end_t = [u['t'] + u['dur'] for u in U]
for i, u in enumerate(U):
    if only is not None and i not in only: continue
    f0 = round(u['t'] * FPS); f1 = round(end_t[i] * FPS); N = f1 - f0
    out = f"{OUT}u{i:03d}.mp4"
    if os.path.exists(out) and only is None: continue
    if N <= 0: continue
    enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-an", "-frames:v", str(N), out]
    if u['type'] == 'C':
        pre = "crop=iw*0.97:ih*0.97," if u['key'] in ("MI",) else ""
        vf = f"{pre}scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,setsar=1"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(u['tin']), "-i", SRC + u['file'], "-vf", vf] + enc, check=True)
    elif u['type'] == 'A':
        img = ARCH.format(u['key'])
        fc = (f"[0]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,gblur=sigma=40,eq=brightness=-0.20:saturation=0.5[bg];"
              f"[0]scale=1680:880:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-40,"
              f"scale=2880:1620,zoompan=z='1+0.07*on/{N}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,"
              f"drawtext=fontfile=/usr/share/fonts/opentype/inter/Inter-SemiBold.otf:text='ARCHIVE':fontsize=30:fontcolor=0xD6AF5C:x=60:y=50,setsar=1")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "30", "-i", img, "-filter_complex", fc] + enc, check=True)
    else:
        gfx.render(u['kind'], u['args'], N / FPS, out, seed=i)
    print(i, u['type'], u.get('key', u.get('kind')), N, flush=True)
print("DONE")
