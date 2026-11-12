#!/usr/bin/env python3
import json, os
from faster_whisper import WhisperModel

ROOT = "/home/claude/orivanta_work/videos/cinematic_test"
os.chdir(ROOT)
os.makedirs("subtitles", exist_ok=True)

model = WhisperModel("small.en", device="cpu", compute_type="int8")

for i in range(1, 10):
    audio = f"narration_audio/scene{i}_narration.mp3"
    if not os.path.exists(audio):
        continue
    segments, info = model.transcribe(audio, word_timestamps=True, language="en", beam_size=5)
    words = []
    seg_list = []
    for seg in segments:
        seg_list.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
        for w in seg.word_timestamps if hasattr(seg, "word_timestamps") else (seg.words or []):
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    out = {"scene": i, "segments": seg_list, "words": words}
    with open(f"subtitles/scene{i}_transcript.json", "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"scene {i}: {len(seg_list)} segments, {len(words)} words")
