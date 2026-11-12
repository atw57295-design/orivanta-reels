#!/usr/bin/env python3
"""
Haber-Bosch documentary — final assembly.
Builds each scene as video(looped to narration length)+mixed audio(narration+music+sfx),
then concatenates all scenes into one complete film.
"""
import subprocess, os, sys, json

ROOT = "/home/claude/orivanta_work/videos/cinematic_test"
os.chdir(ROOT)
OUT_DIR = os.path.join(ROOT, "scene_builds")
os.makedirs(OUT_DIR, exist_ok=True)

W, H, FPS = 1280, 720, 24

def dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True
    )
    return float(out.stdout.strip())

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(cmd))
        print(r.stderr[-4000:])
        raise SystemExit(1)

# scene -> (video sources list [concat in order, looped to fill duration], narration, music cue, sfx or None, music_vol, sfx_vol)
SCENES = [
    {
        "id": 1, "name": "hook",
        "videos": ["scene1a_industrial_opening_veo.mp4", "scene1b_motion_proof.mp4"],
        "narration": "narration_audio/scene1_narration.mp3",
        "music": "music_sfx_audio/music_first_signal_cue.wav", "sfx": None,
    },
    {
        "id": 2, "name": "problem",
        "videos": ["scene2_guano_port_motion.mp4"],
        "narration": "narration_audio/scene2_narration.mp3",
        "music": "music_sfx_audio/music_first_signal_cue.wav", "sfx": None,
    },
    {
        "id": 3, "name": "challenge",
        "videos": ["scene2_motion_proof.mp4"],
        "narration": "narration_audio/scene3_narration.mp3",
        "music": "music_sfx_audio/music_first_signal_cue.wav",
        "sfx": "music_sfx_audio/sfx_laboratory_ambience.wav",
    },
    {
        "id": 4, "name": "breakthrough",
        "videos": ["scene4_motion_proof.mp4"],
        "narration": "narration_audio/scene4_narration.mp3",
        "music": "music_sfx_audio/music_breakthrough_cue.wav", "sfx": None,
    },
    {
        "id": 5, "name": "scaling_up",
        "videos": ["scene5_factory_interior_veo.mp4"],
        "narration": "narration_audio/scene5_narration.mp3",
        "music": "music_sfx_audio/music_breakthrough_cue.wav",
        "sfx": "music_sfx_audio/sfx_factory_ambience_1913.wav",
    },
    {
        "id": 6, "name": "turn",
        "videos": ["scene6_munitions_factory_motion.mp4"],
        "narration": "narration_audio/scene6_narration.mp3",
        "music": "music_sfx_audio/music_moral_shadow_cue.wav",
        "sfx": "music_sfx_audio/sfx_factory_ambience_1913.wav",
    },
    {
        "id": 7, "name": "moral_shadow",
        "videos": ["scene7_ypres_gas_attack_motion.mp4"],
        "narration": "narration_audio/scene7_narration.mp3",
        "music": "music_sfx_audio/music_moral_shadow_cue.wav",
        "sfx": "music_sfx_audio/sfx_wwi_trench_ambience.wav",
    },
    {
        "id": 8, "name": "legacy",
        "videos": ["scene8_legacy_farmland_veo.mp4"],
        "narration": "narration_audio/scene8_narration.mp3",
        "music": "music_sfx_audio/music_legacy_cue.wav", "sfx": None,
    },
]

def build_scene_video(scene):
    """Loop/concat the scene's source videos to (at least) narration length, scale/pad to WxH."""
    target_dur = dur(scene["narration"]) + 0.5  # small pad
    vids = scene["videos"]
    out_silent = os.path.join(OUT_DIR, f"s{scene['id']}_video.mp4")

    if len(vids) == 1:
        src = vids[0]
        src_dur = dur(src)
        loops = max(0, int(target_dur // src_dur))  # -stream_loop N means play N+1 times
        cmd = [
            "ffmpeg", "-y", "-stream_loop", str(loops), "-i", src,
            "-t", str(target_dur),
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}",
            "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            out_silent,
        ]
        run(cmd)
    else:
        # concat multiple distinct clips back-to-back, then loop the whole sequence if still short
        normed = []
        for i, v in enumerate(vids):
            nv = os.path.join(OUT_DIR, f"s{scene['id']}_part{i}.mp4")
            run([
                "ffmpeg", "-y", "-i", v,
                "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}",
                "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                nv,
            ])
            normed.append(nv)
        concat_list = os.path.join(OUT_DIR, f"s{scene['id']}_concat.txt")
        with open(concat_list, "w") as f:
            for nv in normed:
                f.write(f"file '{os.path.abspath(nv)}'\n")
        concat_once = os.path.join(OUT_DIR, f"s{scene['id']}_concat_once.mp4")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", concat_once])
        once_dur = dur(concat_once)
        loops = max(0, int(target_dur // once_dur))
        run([
            "ffmpeg", "-y", "-stream_loop", str(loops), "-i", concat_once,
            "-t", str(target_dur),
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            out_silent,
        ])
    return out_silent, target_dur

def build_scene_audio(scene, target_dur):
    narration = scene["narration"]
    music = scene["music"]
    sfx = scene.get("sfx")
    out_audio = os.path.join(OUT_DIR, f"s{scene['id']}_audio.m4a")

    inputs = ["-i", narration]
    music_dur = dur(music)
    music_loops = max(0, int(target_dur // music_dur) + 1)
    inputs += ["-stream_loop", str(music_loops), "-i", music]

    filter_parts = []
    # narration: full volume, pad to target_dur with silence if shorter
    filter_parts.append(f"[0:a]apad=whole_dur={target_dur},atrim=0:{target_dur},volume=1.0[narr]")
    filter_parts.append(f"[1:a]atrim=0:{target_dur},volume=0.14[mus]")
    mix_inputs = "[narr][mus]"
    n_mix = 2

    if sfx:
        sfx_dur = dur(sfx)
        sfx_loops = max(0, int(target_dur // sfx_dur) + 1)
        inputs += ["-stream_loop", str(sfx_loops), "-i", sfx]
        filter_parts.append(f"[2:a]atrim=0:{target_dur},volume=0.10[sfxa]")
        mix_inputs += "[sfxa]"
        n_mix = 3

    filter_parts.append(f"{mix_inputs}amix=inputs={n_mix}:duration=first:dropout_transition=0,volume=1.6[aout]")
    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[aout]", "-c:a", "aac", "-b:a", "192k",
        out_audio,
    ]
    run(cmd)
    return out_audio

def mux_scene(scene, video_path, audio_path, target_dur):
    out_final = os.path.join(OUT_DIR, f"scene{scene['id']}_{scene['name']}_final.mp4")
    run([
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-t", str(target_dur),
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_final,
    ])
    return out_final

def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    finals = []
    for scene in SCENES:
        if only and str(scene["id"]) not in only:
            continue
        missing = [v for v in scene["videos"] if not os.path.exists(v)]
        if missing:
            print(f"SKIP scene {scene['id']}: missing source video(s) {missing}")
            continue
        print(f"=== Building scene {scene['id']} ({scene['name']}) ===")
        video_path, target_dur = build_scene_video(scene)
        audio_path = build_scene_audio(scene, target_dur)
        final = mux_scene(scene, video_path, audio_path, target_dur)
        finals.append(final)
        print(f"  -> {final} ({target_dur:.1f}s)")
    print("DONE. Built:", finals)

if __name__ == "__main__":
    main()
