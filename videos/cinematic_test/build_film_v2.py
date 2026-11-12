#!/usr/bin/env python3
"""
Full rebuild of the Haber-Bosch documentary per the user's 9 corrections:
real HD video throughout (no frame extraction), burned-in English subtitles,
synced on-screen emphasis phrases, persistent uncropped logo watermark,
an uncropped logo intro + outro, and a Subscribe/Follow CTA ending.
Reuses all existing narration, music and SFX (requirement #8).
"""
import json, os, subprocess, shlex

ROOT = "/home/claude/orivanta_work/videos/cinematic_test"
os.chdir(ROOT)
BUILD = "scene_builds_v2"
os.makedirs(BUILD, exist_ok=True)

W, H = 1280, 720
WATERMARK = "brand_cards/watermark_small.png"
INFO_CARDS = "brand_cards/info"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(shlex.quote(c) for c in cmd))
        print(r.stderr[-4000:])
        raise SystemExit(1)
    return r

def dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())

def esc_drawtext(text):
    return text.replace("\\", "\\\\\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")

# ---------------------------------------------------------------------------
# Scene definitions
# ---------------------------------------------------------------------------
SCENES = {
    1: {
        "clips": ["scene1a_industrial_opening_veo.mp4", "scene1b_wheat_kling.mp4"],
        "music": "music_sfx_audio/music_first_signal_cue.wav",
        "sfx": None,
        "emphasis": [(9.829, 11.296, "A FACTORY")],
        "insert": None,
    },
    2: {
        "clips": ["scene2_guano_port_veo.mp4"],
        "music": "music_sfx_audio/music_first_signal_cue.wav",
        "sfx": None,
        "emphasis": [(20.375, 23.858, "A WAR")],
        "insert": (23.9, 4.0, f"{INFO_CARDS}/card_war_of_pacific.png"),
    },
    3: {
        "clips": ["scene3_lab_kling.mp4"],
        "music": "music_sfx_audio/music_first_signal_cue.wav",
        "sfx": "music_sfx_audio/sfx_laboratory_ambience.wav",
        "emphasis": [(14.279, 15.279, "...AND FAILED.")],
        "insert": (20.6, 5.3, f"{INFO_CARDS}/card_haber_equation.png"),
    },
    4: {
        "clips": ["scene4_breakthrough_kling.mp4"],
        "music": "music_sfx_audio/music_breakthrough_cue.wav",
        "sfx": None,
        "emphasis": [(12.102, 14.239, "THE BREAKTHROUGH")],
        "insert": None,
    },
    5: {
        "clips": ["scene5_factory_interior_veo.mp4"],
        "music": "music_sfx_audio/music_breakthrough_cue.wav",
        "sfx": "music_sfx_audio/sfx_factory_ambience_1913.wav",
        "emphasis": [(50.259, 52.717, "A RAW MATERIAL")],
        "insert": (44.8, 5.0, f"{INFO_CARDS}/card_oppau.png"),
    },
    6: {
        "clips": ["scene6_munitions_kling.mp4"],
        "music": "music_sfx_audio/music_moral_shadow_cue.wav",
        "sfx": "music_sfx_audio/sfx_factory_ambience_1913.wav",
        "emphasis": [(12.210, 15.867, "EXPLOSIVES")],
        "insert": None,
    },
    7: {
        "clips": ["scene7_ypres_kling.mp4"],
        "music": "music_sfx_audio/music_moral_shadow_cue.wav",
        "sfx": "music_sfx_audio/sfx_wwi_trench_ambience.wav",
        "emphasis": [(6.937, 12.303, "CHEMICAL WEAPONS")],
        "insert": (3.9, 4.0, f"{INFO_CARDS}/card_ypres.png"),
    },
    8: {
        "clips": ["scene8_legacy_farmland_veo.mp4"],
        "music": "music_sfx_audio/music_legacy_cue.wav",
        "sfx": None,
        "emphasis": [(11.921, 15.622, "HALF OF YOU")],
        "insert": None,
    },
}

def make_palindrome(src, out):
    """Forward + reversed (seamless ping-pong) so looping a short clip to a
    long scene duration doesn't produce a hard jump-cut every few seconds."""
    rev = out.replace(".mp4", "_rev.mp4")
    run(["ffmpeg", "-y", "-i", src, "-vf", "reverse", "-an", rev])
    concat_txt = out.replace(".mp4", "_concat.txt")
    with open(concat_txt, "w") as f:
        f.write(f"file '{os.path.abspath(src)}'\n")
        f.write(f"file '{os.path.abspath(rev)}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", out])
    os.remove(rev)
    os.remove(concat_txt)

def build_scene_video(scene_id, clips, target_dur):
    """Loop/concat the scene's clip(s) (as seamless palindromes) to exactly
    cover target_dur, scaled uniformly to 1280x720 with a slow cinematic
    drift zoom to add motion and help disguise loop seams."""
    segs = []
    per_clip = target_dur / len(clips)
    for i, clip in enumerate(clips):
        pal = f"{BUILD}/scene{scene_id}_pal{i}.mp4"
        make_palindrome(clip, pal)
        pal_dur = dur(pal)
        looped = f"{BUILD}/scene{scene_id}_loop{i}.mp4"
        n_frames_zoom = int(per_clip * 30)
        run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", pal, "-t", f"{per_clip:.3f}",
             "-vf", (f"scale={W}:{H},"
                     f"zoompan=z='min(zoom+0.0007,1.12)':d=1:s={W}x{H}:fps=30,"
                     f"format=yuv420p"),
             "-r", "30", "-an", looped])
        segs.append(looped)
    if len(segs) == 1:
        return segs[0]
    concat_txt = f"{BUILD}/scene{scene_id}_segs.txt"
    with open(concat_txt, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    out = f"{BUILD}/scene{scene_id}_video.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", out])
    return out

def splice_info_card(scene_id, video, target_dur, insert_cfg):
    """Cut away from the looping scene footage to a brief documentary-style
    info card (map / date / diagram), then back -- narration keeps playing
    underneath unaffected since only the visual track is spliced."""
    start, ins_dur, card_png = insert_cfg
    end = start + ins_dur
    before = f"{BUILD}/scene{scene_id}_pre.mp4"
    after = f"{BUILD}/scene{scene_id}_post.mp4"
    card_clip = f"{BUILD}/scene{scene_id}_card.mp4"

    run(["ffmpeg", "-y", "-i", video, "-t", f"{start:.3f}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", before])
    run(["ffmpeg", "-y", "-ss", f"{end:.3f}", "-i", video,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", after])
    run(["ffmpeg", "-y", "-loop", "1", "-i", card_png, "-t", f"{ins_dur:.3f}",
         "-vf", f"fade=t=in:st=0:d=0.35,fade=t=out:st={ins_dur-0.4:.3f}:d=0.4,format=yuv420p",
         "-r", "30", card_clip])

    concat_txt = f"{BUILD}/scene{scene_id}_splice.txt"
    with open(concat_txt, "w") as f:
        for p in [before, card_clip, after]:
            f.write(f"file '{os.path.abspath(p)}'\n")
    spliced = f"{BUILD}/scene{scene_id}_spliced.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", spliced])
    return spliced

def build_scene(scene_id, cfg):
    narration = f"narration_audio/scene{scene_id}_narration.mp3"
    target_dur = dur(narration)
    print(f"-- scene {scene_id}: target {target_dur:.2f}s")

    video = build_scene_video(scene_id, cfg["clips"], target_dur)
    if cfg.get("insert"):
        video = splice_info_card(scene_id, video, target_dur, cfg["insert"])
        print(f"   spliced info card at {cfg['insert'][0]}s")

    # --- subtitles + emphasis text + watermark, all in one filter pass ---
    srt_path = os.path.abspath(f"subtitles/scene{scene_id}.srt")
    style = ("FontName=Liberation Sans,FontSize=15,PrimaryColour=&H00FFFFFF,"
              "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
              "Alignment=2,MarginV=40")
    vf_parts = [f"subtitles={shlex.quote(srt_path)}:force_style='{style}'"]

    for (st, en, text) in cfg["emphasis"]:
        t = esc_drawtext(text)
        alpha_expr = (f"if(lt(t,{st}+0.15),(t-{st})/0.15,"
                       f"if(gt(t,{en}-0.15),({en}-t)/0.15,1))")
        vf_parts.append(
            "drawtext=fontfile=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:"
            f"text='{t}':fontcolor=0xFFCD5A:fontsize=56:"
            "x=(w-text_w)/2:y=h*0.18:"
            "bordercolor=black@0.9:borderw=4:"
            f"alpha='{alpha_expr}':enable='between(t,{st},{en})'"
        )

    subbed = f"{BUILD}/scene{scene_id}_sub.mp4"
    run(["ffmpeg", "-y", "-i", video, "-vf", ",".join(vf_parts),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", subbed])

    # persistent corner watermark
    watermarked = f"{BUILD}/scene{scene_id}_wm.mp4"
    run(["ffmpeg", "-y", "-i", subbed, "-i", WATERMARK,
         "-filter_complex",
         f"[1:v]colorchannelmixer=aa=0.55[wm];[0:v][wm]overlay=W-w-22:22",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", watermarked])

    # --- audio mix: narration + music (+ optional sfx) ---
    inputs = ["-i", watermarked, "-i", narration]
    filter_inputs = []
    idx = 2
    music_idx = None
    sfx_idx = None
    if cfg["music"]:
        inputs += ["-stream_loop", "-1", "-i", cfg["music"]]
        music_idx = idx
        idx += 1
    if cfg["sfx"]:
        inputs += ["-stream_loop", "-1", "-i", cfg["sfx"]]
        sfx_idx = idx
        idx += 1

    mix_labels = ["[1:a]volume=1.0[n]"]
    amix_inputs = ["[n]"]
    if music_idx is not None:
        mix_labels.append(f"[{music_idx}:a]atrim=0:{target_dur:.3f},asetpts=PTS-STARTPTS,volume=0.14[m]")
        amix_inputs.append("[m]")
    if sfx_idx is not None:
        mix_labels.append(f"[{sfx_idx}:a]atrim=0:{target_dur:.3f},asetpts=PTS-STARTPTS,volume=0.10[s]")
        amix_inputs.append("[s]")
    n_inputs = len(amix_inputs)
    mix_labels.append("".join(amix_inputs) + f"amix=inputs={n_inputs}:duration=first:dropout_transition=2[a]")
    filter_complex = ";".join(mix_labels)

    final = f"{BUILD}/scene{scene_id}_final.mp4"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", filter_complex,
         "-map", "0:v", "-map", "[a]", "-t", f"{target_dur:.3f}",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", final])
    print(f"   done -> {final} ({dur(final):.2f}s)")
    return final

def main():
    finals = []
    for sid in range(1, 9):
        finals.append(build_scene(sid, SCENES[sid]))
    with open(f"{BUILD}/manifest.json", "w") as f:
        json.dump(finals, f, indent=2)
    print("All scene 1-8 builds complete.")

if __name__ == "__main__":
    main()
