import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from PIL import Image
from src.config import FFMPEG_BIN, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, TEMP_DIR, ASSETS_DIR
from src.styler import render_after_the_crown_frame

logger = logging.getLogger("VideoEngine")

DEFAULT_MUSIC = ASSETS_DIR / "music" / "dark_ambient_cello.mp3"

def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def render_clip(image_path: Path, duration: float, output_path: Path, motion: str = "slow_zoom_in") -> bool:
    """Renders a single scene clip with Ken Burns motion and cinema grading."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = max(30, int(duration * VIDEO_FPS))
    
    if motion == "slow_zoom_out":
        zoom_expr = "if(lte(zoom,1.0),1.15,max(1.001,zoom-0.0006))"
        pan_x = "iw/2-(iw/zoom/2)"
        pan_y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        zoom_expr = "1.10"
        pan_x = f"max(0, (iw-iw/zoom) * (1 - on/{frames}))"
        pan_y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        zoom_expr = "1.10"
        pan_x = f"min(iw-iw/zoom, (iw-iw/zoom) * (on/{frames}))"
        pan_y = "ih/2-(ih/zoom/2)"
    else:  # slow_zoom_in
        zoom_expr = "min(zoom+0.0006, 1.16)"
        pan_x = "iw/2-(iw/zoom/2)"
        pan_y = "ih/2-(ih/zoom/2)"

    vf_filter = (
        f"scale=3840:-2,"
        f"zoompan=z='{zoom_expr}':x='{pan_x}':y='{pan_y}':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS},"
        f"eq=contrast=1.14:brightness=-0.01:saturation=0.85,"
        f"vignette=PI/4.2,"
        f"noise=alls=5:allf=t+u,"
        f"format=yuv420p"
    )

    cmd = [
        FFMPEG_BIN, "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Render clip failed: {e.stderr}")
        return False

def create_scene_video(
    images: Union[Path, List[Path]],
    audio_path: Path,
    duration: float,
    output_path: Path,
    motion: str = "slow_zoom_in",
    label_title: Optional[str] = None,
    label_sub: Optional[str] = None,
    citation: Optional[str] = None,
    callout_red: Optional[str] = None,
    callout_box: Optional[str] = None
) -> bool:
    """
    Renders a scene video with After the Crown multi-beat cuts.
    If multiple images are provided, cuts between them every ~3.5 seconds
    with alternating Ken Burns motions under the continuous scene audio.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(images, (str, Path)):
        img_list = [Path(images)]
    else:
        img_list = [Path(p) for p in images if Path(p).exists()]

    if not img_list:
        logger.error("No valid images provided for scene rendering.")
        return False

    num_beats = len(img_list)
    sub_duration = duration / num_beats
    motion_cycle = ["slow_zoom_in", "pan_left", "slow_zoom_out", "pan_right"]

    sub_clips = []
    for idx, img_p in enumerate(img_list):
        beat_idx = idx + 1
        beat_motion = motion_cycle[idx % len(motion_cycle)] if num_beats > 1 else motion

        # Documentary lower-third typography appears on the first beat for ~3.5s
        cur_title = label_title if beat_idx == 1 else None
        cur_sub = label_sub if beat_idx == 1 else None
        
        # Callouts can appear on subsequent beats
        cur_red = callout_red if (beat_idx == 2 or (num_beats == 1 and callout_red)) else None
        cur_box = callout_box if (beat_idx == 2 or (num_beats == 1 and callout_box)) else None

        raw_img = Image.open(img_p)
        styled_frame = render_after_the_crown_frame(
            base_img=raw_img,
            label_title=cur_title,
            label_sub=cur_sub,
            citation=citation,
            callout_red=cur_red,
            callout_box=cur_box
        )
        
        sub_img_path = TEMP_DIR / f"{output_path.stem}_beat_{beat_idx}_styled.jpg"
        styled_frame.save(sub_img_path, "JPEG", quality=95)

        sub_clip_path = TEMP_DIR / f"{output_path.stem}_beat_{beat_idx}.mp4"
        if not render_clip(sub_img_path, sub_duration, sub_clip_path, motion=beat_motion):
            logger.error(f"Failed to render sub-clip {beat_idx} of scene {output_path.stem}")
            return False
        sub_clips.append(sub_clip_path)

    # Concatenate sub-clips
    if len(sub_clips) == 1:
        temp_vonly = sub_clips[0]
    else:
        concat_list_file = TEMP_DIR / f"{output_path.stem}_beats_concat.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for c in sub_clips:
                f.write(f"file '{c.resolve().as_posix()}'\n")

        temp_vonly = TEMP_DIR / f"{output_path.stem}_vonly.mp4"
        cmd_concat = [
            FFMPEG_BIN, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list_file),
            "-c", "copy",
            str(temp_vonly)
        ]
        try:
            subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to concat sub-clips: {e.stderr}")
            return False

    # Mux with scene voice
    cmd_mux = [
        FFMPEG_BIN, "-y",
        "-i", str(temp_vonly),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]
    try:
        subprocess.run(cmd_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to mux scene video: {e.stderr}")
        return False

def concatenate_scenes(
    scene_videos: List[Path],
    output_path: Path,
    background_music: Optional[Path] = None,
    script_scenes: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """Concatenates scene videos and mixes continuous background cello soundtrack with ducking."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    concat_txt = TEMP_DIR / "final_concat_list.txt"
    
    with open(concat_txt, "w", encoding="utf-8") as f:
        for v in scene_videos:
            f.write(f"file '{v.resolve().as_posix()}'\n")

    raw_combined = TEMP_DIR / "raw_combined.mp4"
    cmd_cat = [
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-c", "copy",
        str(raw_combined)
    ]
    subprocess.run(cmd_cat, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    bg_music = background_music or DEFAULT_MUSIC
    if bg_music and bg_music.exists():
        logger.info(f"Mixing continuous cello soundtrack: {bg_music.name} with ducking...")
        cmd_master = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_combined),
            "-stream_loop", "-1", "-i", str(bg_music),
            "-filter_complex",
            "[0:a]volume=1.0[voice];[1:a]volume=0.13[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path)
        ]
        subprocess.run(cmd_master, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        import shutil
        shutil.copy(raw_combined, output_path)

    # Generate clean SRT subtitle file
    if script_scenes:
        srt_path = output_path.with_suffix(".srt")
        curr_t = 0.0
        with open(srt_path, "w", encoding="utf-8") as sf:
            for idx, sc in enumerate(script_scenes, 1):
                dur = sc.get("duration", 5.0)
                end_t = curr_t + dur
                sf.write(f"{idx}\n")
                sf.write(f"{format_srt_time(curr_t)} --> {format_srt_time(end_t)}\n")
                sf.write(f"{sc.get('narration', '')}\n\n")
                curr_t = end_t
                
    return True
