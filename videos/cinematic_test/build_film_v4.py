#!/usr/bin/env python3
"""
v4 editing pass, per the user's final-corrections brief:
 - No ping-pong/reverse looping ("back-and-forth") of short video clips.
   Each real video clip now plays forward exactly once.
 - Remaining scene time is filled with the scene's own existing reference
   STILL image (already generated, zero new credits) under a varied
   Ken-Burns move (push-in / drift-left / drift-right / pull-out), cycled
   so consecutive fills in the same scene don't repeat the same motion --
   this is the "historical stills + camera movement" look of the
   reference channels, and avoids any one long static hold.
 - Documentary info-card cutaways (scenes 2, 3, 5, 7) are kept, but moved
   so they never land on a video clip (always after it) and never overlap
   the scene's emphasis-text window.
 - No intro logo card: the film now opens directly on scene 1 (hook-first).
   Branding = persistent corner watermark from frame 1, full logo kept
   only at the close (per the user's "no logo intro, add branding later").
 - Subtitles, emphasis text, watermark, audio mix: unchanged from v3.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import build_film_v2 as v2

ROOT = "/home/claude/orivanta_work/videos/cinematic_test"
os.chdir(ROOT)
BUILD = "scene_builds_v4"
os.makedirs(BUILD, exist_ok=True)

run = v2.run
dur = v2.dur
esc_drawtext = v2.esc_drawtext
WATERMARK = v2.WATERMARK
W, H = v2.W, v2.H
INFO_CARDS = v2.INFO_CARDS

STILLS = {
    1: ["scene1_industrial_opening.png", "scene1b_wheat_field.png"],
    2: ["scene2_guano_port.png"],
    3: ["scene2_laboratory.png"],
    4: ["scene3_fritz_haber.png"],
    5: ["scene5_factory_interior.png"],
    6: ["scene6_munitions_factory.png"],
    7: ["scene7_ypres_gas_attack.png"],
    8: ["scene8_legacy_farmland.png"],
}

PRESETS = [
    dict(z0=1.00, z1=1.14, xd=0.00, yd=0.00),
    dict(z0=1.10, z1=1.22, xd=-0.11, yd=0.03),
    dict(z0=1.05, z1=1.17, xd=0.11, yd=-0.03),
    dict(z0=1.16, z1=1.02, xd=0.00, yd=0.05),
]

# scenes 1-8 with: ordered real video clips, and (for 2/3/5/7) a card insert
# placed strictly AFTER all of that scene's video clips, clear of the
# emphasis window. Emphasis + music/sfx are unchanged from v2/v3.
SCENES = {
    1: {"clips": ["scene1a_industrial_opening_veo.mp4", "scene1b_wheat_kling.mp4"],
        "music": "music_sfx_audio/music_first_signal_cue.wav", "sfx": None,
        "emphasis": [(9.829, 11.296, "A FACTORY")], "insert": None},
    2: {"clips": ["scene2_guano_port_veo.mp4"],
        "music": "music_sfx_audio/music_first_signal_cue.wav", "sfx": None,
        "emphasis": [(20.375, 23.858, "A WAR")],
        "insert": (23.9, 4.0, f"{INFO_CARDS}/card_war_of_pacific.png")},
    3: {"clips": ["scene3_lab_kling.mp4"],
        "music": "music_sfx_audio/music_first_signal_cue.wav",
        "sfx": "music_sfx_audio/sfx_laboratory_ambience.wav",
        "emphasis": [(14.279, 15.279, "...AND FAILED.")],
        "insert": (20.6, 5.3, f"{INFO_CARDS}/card_haber_equation.png")},
    4: {"clips": ["scene4_breakthrough_kling.mp4"],
        "music": "music_sfx_audio/music_breakthrough_cue.wav", "sfx": None,
        "emphasis": [(12.102, 14.239, "THE BREAKTHROUGH")], "insert": None},
    5: {"clips": ["scene5_clip1_aerial.mp4", "scene5_factory_interior_veo.mp4",
                  "scene5_clip2_interior.mp4", "scene5_clip4_gauge.mp4",
                  "scene5_clip3_loading.mp4", "scene5_clip5_dusk.mp4"],
        "clips_after": [],
        "music": "music_sfx_audio/music_breakthrough_cue.wav",
        "sfx": "music_sfx_audio/sfx_factory_ambience_1913.wav",
        "emphasis": [(50.259, 52.717, "A RAW MATERIAL")],
        "insert": (44.8, 5.0, f"{INFO_CARDS}/card_oppau.png")},
    6: {"clips": ["scene6_munitions_kling.mp4"],
        "music": "music_sfx_audio/music_moral_shadow_cue.wav",
        "sfx": "music_sfx_audio/sfx_factory_ambience_1913.wav",
        "emphasis": [(12.210, 15.867, "EXPLOSIVES")], "insert": None},
    7: {"clips": ["scene7_clip1_trench.mp4", "scene7_clip2_gascloud.mp4"],
        "clips_after": ["scene7_clip3_gasmasks.mp4", "scene7_ypres_kling.mp4"],
        "music": "music_sfx_audio/music_moral_shadow_cue.wav",
        "sfx": "music_sfx_audio/sfx_wwi_trench_ambience.wav",
        "emphasis": [(6.937, 12.303, "CHEMICAL WEAPONS")],
        "insert": (13.0, 4.0, f"{INFO_CARDS}/card_ypres.png")},
    8: {"clips": ["scene8_legacy_farmland_veo.mp4"],
        "music": "music_sfx_audio/music_legacy_cue.wav", "sfx": None,
        "emphasis": [(11.921, 15.622, "HALF OF YOU")], "insert": None},
}

def kenburns_clip(still_path, duration, preset_idx, out_path, fps=30, y_bias=0.0, x_bias=0.0, preset_override=None):
    n = max(1, round(duration * fps))
    p = preset_override if preset_override else PRESETS[preset_idx % len(PRESETS)]
    zexpr = f"{p['z0']}+{p['z1']-p['z0']}*on/{n}"
    xexpr = f"(iw/2-(iw/zoom/2))+{x_bias}*iw+{p['xd']}*iw*(on/{n})"
    yexpr = f"(ih/2-(ih/zoom/2))+{y_bias}*ih+{p['yd']}*ih*(on/{n})"
    vf = (f"scale=1920:1920:force_original_aspect_ratio=increase,"
          f"zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d=1:s={W}x{H}:fps={fps},"
          f"format=yuv420p")
    run(["ffmpeg", "-y", "-loop", "1", "-i", still_path, "-t", f"{duration:.3f}",
         "-vf", vf, "-r", str(fps), "-an", out_path])

def video_forward_clip(clip_path, out_path, fps=30):
    run(["ffmpeg", "-y", "-i", clip_path,
         "-vf", f"scale={W}:{H},format=yuv420p", "-r", str(fps), "-an", out_path])

def concat_segments(paths, out_path):
    txt = out_path.replace(".mp4", "_list.txt")
    with open(txt, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", out_path])
    os.remove(txt)

def build_scene_video_v4(scene_id, cfg, target_dur):
    clips = cfg["clips"]
    stills = STILLS[scene_id]
    insert = cfg.get("insert")
    preset_i = scene_id  # vary starting preset per scene too

    segments = []
    if scene_id == 1:
        # two clips, each followed by its own still fill, no card
        v_durs = [dur(c) for c in clips]
        total_fixed = sum(v_durs)
        remainder = target_dur - total_fixed
        fill0 = remainder * (v_durs[0] / total_fixed)
        fill1 = remainder - fill0
        p0 = f"{BUILD}/s1_v0.mp4"; video_forward_clip(clips[0], p0)
        segments.append(p0)
        if fill0 > 0.2:
            # y_bias keeps the crop on the smokestacks/skyline (stronger hook
            # visual, and clear of a small artifact low in this particular frame)
            p = f"{BUILD}/s1_f0.mp4"; kenburns_clip(
                stills[0], fill0, preset_i, p, y_bias=-0.30,
                preset_override=dict(z0=1.32, z1=1.42, xd=0.0, yd=0.0))
            segments.append(p); preset_i += 1
        p1 = f"{BUILD}/s1_v1.mp4"; video_forward_clip(clips[1], p1)
        segments.append(p1)
        if fill1 > 0.2:
            p = f"{BUILD}/s1_f1.mp4"; kenburns_clip(stills[1], fill1, preset_i, p)
            segments.append(p); preset_i += 1
        out = f"{BUILD}/scene{scene_id}_video.mp4"
        concat_segments(segments, out)
        return out

    # scenes 2-8: one or more real clips in sequence, optionally capped to fit
    # before an info-card insert (trimming the last clip if the real footage
    # runs long, rather than letting it push the card out of narration sync),
    # plus an optional second real-clip group that plays after the card.
    cap = insert[0] if insert else target_dur
    segments = []
    v_d = 0.0
    for ci, clip in enumerate(clips):
        cdur = dur(clip)
        remaining_cap = cap - v_d
        if remaining_cap <= 0.2:
            break
        p = f"{BUILD}/s{scene_id}_v{ci}.mp4"
        if cdur <= remaining_cap + 0.05:
            video_forward_clip(clip, p)
            v_d += cdur
        else:
            run(["ffmpeg", "-y", "-i", clip, "-t", f"{remaining_cap:.3f}",
                 "-vf", f"scale={W}:{H},format=yuv420p", "-r", "30", "-an", p])
            v_d += remaining_cap
        segments.append(p)

    def add_fill(fill_dur, nonlocal_preset):
        if fill_dur <= 0.2:
            return nonlocal_preset
        MAXSEG = 12.0
        n_sub = max(1, round(fill_dur / MAXSEG))
        each = fill_dur / n_sub
        for i in range(n_sub):
            p = f"{BUILD}/s{scene_id}_f{nonlocal_preset}.mp4"
            kenburns_clip(stills[0], each, nonlocal_preset, p)
            segments.append(p)
            nonlocal_preset += 1
        return nonlocal_preset

    if insert:
        ins_start, ins_dur, card_png = insert
        fill_before = ins_start - v_d
        preset_i = add_fill(fill_before, preset_i)
        card_clip = f"{BUILD}/s{scene_id}_card.mp4"
        run(["ffmpeg", "-y", "-loop", "1", "-i", card_png, "-t", f"{ins_dur:.3f}",
             "-vf", f"fade=t=in:st=0:d=0.35,fade=t=out:st={ins_dur-0.4:.3f}:d=0.4,format=yuv420p",
             "-r", "30", card_clip])
        segments.append(card_clip)

        after_clips = cfg.get("clips_after") or []
        after_cap = target_dur - ins_start - ins_dur
        a_d = 0.0
        for ci, clip in enumerate(after_clips):
            cdur = dur(clip)
            remaining_cap = after_cap - a_d
            if remaining_cap <= 0.2:
                break
            p = f"{BUILD}/s{scene_id}_a{ci}.mp4"
            if cdur <= remaining_cap + 0.05:
                video_forward_clip(clip, p)
                a_d += cdur
            else:
                run(["ffmpeg", "-y", "-i", clip, "-t", f"{remaining_cap:.3f}",
                     "-vf", f"scale={W}:{H},format=yuv420p", "-r", "30", "-an", p])
                a_d += remaining_cap
            segments.append(p)

        fill_after = after_cap - a_d
        preset_i = add_fill(fill_after, preset_i)
    else:
        fill_after = target_dur - v_d
        preset_i = add_fill(fill_after, preset_i)

    out = f"{BUILD}/scene{scene_id}_video.mp4"
    concat_segments(segments, out)
    return out

def build_scene(scene_id, cfg):
    narration = f"narration_audio/scene{scene_id}_narration.mp3"
    target_dur = dur(narration)
    print(f"-- scene {scene_id}: target {target_dur:.2f}s")

    video = build_scene_video_v4(scene_id, cfg, target_dur)

    srt_path = os.path.abspath(f"subtitles/scene{scene_id}.srt")
    style = ("FontName=Liberation Sans,FontSize=15,PrimaryColour=&H00FFFFFF,"
              "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
              "Alignment=2,MarginV=40")
    import shlex
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

    watermarked = f"{BUILD}/scene{scene_id}_wm.mp4"
    run(["ffmpeg", "-y", "-i", subbed, "-i", WATERMARK,
         "-filter_complex", "[1:v]colorchannelmixer=aa=0.55[wm];[0:v][wm]overlay=W-w-22:22",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", watermarked])

    inputs = ["-i", watermarked, "-i", narration]
    idx = 2
    music_idx = sfx_idx = None
    if cfg["music"]:
        inputs += ["-stream_loop", "-1", "-i", cfg["music"]]; music_idx = idx; idx += 1
    if cfg["sfx"]:
        inputs += ["-stream_loop", "-1", "-i", cfg["sfx"]]; sfx_idx = idx; idx += 1
    mix_labels = ["[1:a]volume=1.0[n]"]
    amix_inputs = ["[n]"]
    if music_idx is not None:
        mix_labels.append(f"[{music_idx}:a]atrim=0:{target_dur:.3f},asetpts=PTS-STARTPTS,volume=0.14[m]")
        amix_inputs.append("[m]")
    if sfx_idx is not None:
        mix_labels.append(f"[{sfx_idx}:a]atrim=0:{target_dur:.3f},asetpts=PTS-STARTPTS,volume=0.10[s]")
        amix_inputs.append("[s]")
    mix_labels.append("".join(amix_inputs) + f"amix=inputs={len(amix_inputs)}:duration=first:dropout_transition=2[a]")
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

if __name__ == "__main__":
    main()
