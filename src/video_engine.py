import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
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
    image_path: Path,
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
    """Styles the archival image with After the Crown graphics and renders the scene."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Apply typography & enquadramento
    raw_img = Image.open(image_path)
    styled_frame = render_after_the_crown_frame(
        base_img=raw_img,
        label_title=label_title,
        label_sub=label_sub,
        citation=citation,
        callout_red=callout_red,
        callout_box=callout_box
    )
    
    styled_img_path = TEMP_DIR / f"{output_path.stem}_styled.jpg"
    styled_frame.save(styled_img_path, "JPEG", quality=95)
    
    # 2. Render motion clip
    temp_clip_video = TEMP_DIR / f"{output_path.stem}_vonly.mp4"
    if not render_clip(styled_img_path, duration, temp_clip_video, motion=motion):
        return False
        
    # 3. Mux with scene voice
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(temp_clip_video),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
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
