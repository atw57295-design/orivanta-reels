#!/usr/bin/env python3
"""
Build per-scene SRT subtitles synced proportionally to narration audio duration.
Splits each scene's script into readable caption chunks (~8-11 words, breaking
on punctuation where possible) and times each chunk proportionally to its
character count within the scene's actual narration duration.
"""
import json, os, re, subprocess

ROOT = "/home/claude/orivanta_work/videos/cinematic_test"
os.chdir(ROOT)
os.makedirs("subtitles", exist_ok=True)

with open("narration_script.json") as f:
    SCRIPT = json.load(f)

def dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True
    )
    return float(out.stdout.strip())

def split_into_chunks(text, max_words=11):
    # Split on sentence-ending punctuation and em-dashes first, then re-chunk by word count
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks = []
    for sent in sentences:
        words = sent.split()
        if len(words) <= max_words:
            chunks.append(sent.strip())
        else:
            # split on commas / em-dashes if possible, else hard split by word count
            parts = re.split(r'(?<=[,;—])\s+', sent)
            buf = []
            for part in parts:
                buf_words = " ".join(buf).split()
                part_words = part.split()
                if len(buf_words) + len(part_words) <= max_words or not buf:
                    buf.append(part)
                else:
                    chunks.append(" ".join(buf).strip())
                    buf = [part]
            if buf:
                chunks.append(" ".join(buf).strip())
    # final pass: hard-wrap any chunk still too long
    final = []
    for c in chunks:
        words = c.split()
        if len(words) <= max_words + 3:
            final.append(c)
        else:
            for i in range(0, len(words), max_words):
                final.append(" ".join(words[i:i+max_words]))
    return [c for c in final if c.strip()]

def srt_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def build_scene_srt(scene_id, text, audio_path, lead_in=0.15, tail_pad=0.3):
    total_dur = dur(audio_path)
    usable = max(0.1, total_dur - lead_in - tail_pad)
    chunks = split_into_chunks(text)
    total_chars = sum(len(c) for c in chunks)
    t = lead_in
    entries = []
    for i, c in enumerate(chunks, 1):
        frac = len(c) / total_chars
        seg_dur = max(1.0, usable * frac)
        start = t
        end = min(total_dur - 0.05, t + seg_dur)
        entries.append((start, end, c))
        t = end
    return entries

def write_srt(entries, path, index_offset=0):
    with open(path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(entries, 1 + index_offset):
            f.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n\n")

def main():
    all_entries_global = []  # for a combined full-film SRT, filled in later by assembly script with offsets
    for i in range(1, 9):  # scenes 1-8 (scene 9's CTA line is new, handled separately)
        audio = f"narration_audio/scene{i}_narration.mp3"
        text = SCRIPT[str(i)]
        entries = build_scene_srt(i, text, audio)
        write_srt(entries, f"subtitles/scene{i}.srt")
        print(f"scene {i}: {len(entries)} caption lines, duration {dur(audio):.1f}s")
    # scene 9 (closing reflection line, before the new CTA)
    entries9 = build_scene_srt(9, SCRIPT["9"], "narration_audio/scene9_narration.mp3")
    write_srt(entries9, "subtitles/scene9.srt")
    print(f"scene 9: {len(entries9)} caption lines")

if __name__ == "__main__":
    main()
