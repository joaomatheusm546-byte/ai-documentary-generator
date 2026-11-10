import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import FFMPEG_BIN, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, TEMP_DIR, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VideoEngine")

def create_scene_video(
    image_path: Path,
    audio_path: Path,
    duration: float,
    output_path: Path,
    motion: str = "zoom_in"
) -> bool:
    """
    Renders a single scene with Ken Burns effect synchronized to exact audio duration.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = max(30, int(duration * VIDEO_FPS))
    
    # Calculate Ken Burns filter based on motion type
    # Scaling to 8000x... before zoompan gives jitter-free, ultra-smooth interpolation
    if motion == "zoom_out":
        zoom_expr = "if(lte(zoom,1.0),1.25,max(1.001,zoom-0.0012))"
        pan_x = "iw/2-(iw/zoom/2)"
        pan_y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        zoom_expr = "1.15"
        pan_x = f"max(0, (iw-iw/zoom) * (1 - on/{frames}))"
        pan_y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        zoom_expr = "1.15"
        pan_x = f"min(iw-iw/zoom, (iw-iw/zoom) * (on/{frames}))"
        pan_y = "ih/2-(ih/zoom/2)"
    else:  # default zoom_in
        zoom_expr = "min(zoom+0.0012, 1.25)"
        pan_x = "iw/2-(iw/zoom/2)"
        pan_y = "ih/2-(ih/zoom/2)"

    # FFmpeg filter complex:
    # 1. Scale input image to fill screen preserving aspect ratio
    # 2. zoompan for cinematic movement
    # 3. Format pix_fmt yuv420p for broad player compatibility
    # Scale to 3840 (4K intermediate) for super-smooth subpixel zoom without slowdown
    vf_filter = (
        f"scale=3840:-2,"
        f"zoompan=z='{zoom_expr}':x='{pan_x}':y='{pan_y}':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS},"
        f"format=yuv420p"
    )

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path)
    ]

    try:
        logger.info(f"Rendering scene video {output_path.name} ({duration:.2f}s, {motion})...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg scene render failed: {e.stderr}")
        return False

def concatenate_scenes(scene_videos: List[Path], final_output: Path, background_music: Optional[Path] = None) -> bool:
    """
    Concatenates all scene MP4 files into the final documentary, optionally mixing background music.
    """
    final_output.parent.mkdir(parents=True, exist_ok=True)
    concat_list_file = TEMP_DIR / "concat_list.txt"
    
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for v in scene_videos:
            f.write(f"file '{v.resolve().as_posix()}'\n")

    raw_concat = TEMP_DIR / "combined_raw.mp4"
    cmd_concat = [
        FFMPEG_BIN,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(raw_concat)
    ]

    try:
        logger.info("Concatenating scenes into continuous documentary timeline...")
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg concat failed: {e.stderr}")
        return False

    # If background music is provided, mix it with auto-ducking / low volume
    if background_music and background_music.exists():
        logger.info(f"Mixing background soundtrack '{background_music.name}'...")
        # Audio ducking: Narration at volume 1.0, music looped at 12% volume
        cmd_audio = [
            FFMPEG_BIN,
            "-y",
            "-i", str(raw_concat),
            "-stream_loop", "-1",
            "-i", str(background_music),
            "-filter_complex",
            "[0:a]volume=1.0[voice];[1:a]volume=0.12[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "256k",
            str(final_output)
        ]
        try:
            subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Audio mix failed: {e.stderr}. Using raw concat instead.")
            
    # If no music or mix failed, copy raw concat to final output
    import shutil
    shutil.copy(raw_concat, final_output)
    return True
