import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import FFMPEG_BIN, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, TEMP_DIR, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VideoEngine")

def render_clip(image_path: Path, duration: float, output_path: Path, motion: str = "slow_zoom_in") -> bool:
    """
    Renders a video clip from an image with After The Crown grading and Ken Burns motion.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = max(30, int(duration * VIDEO_FPS))
    
    if motion in ("slow_zoom_out", "zoom_out"):
        zoom_expr = "if(lte(zoom,1.0),1.18,max(1.001,zoom-0.0007))"
        pan_x = "iw/2-(iw/zoom/2)"
        pan_y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        zoom_expr = "1.12"
        pan_x = f"max(0, (iw-iw/zoom) * (1 - on/{frames}))"
        pan_y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        zoom_expr = "1.12"
        pan_x = f"min(iw-iw/zoom, (iw-iw/zoom) * (on/{frames}))"
        pan_y = "ih/2-(ih/zoom/2)"
    else:  # slow_zoom_in
        zoom_expr = "min(zoom+0.0007, 1.20)"
        pan_x = "iw/2-(iw/zoom/2)"
        pan_y = "ih/2-(ih/zoom/2)"

    vf_filter = (
        f"scale=3840:-2,"
        f"zoompan=z='{zoom_expr}':x='{pan_x}':y='{pan_y}':d={frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS},"
        f"eq=contrast=1.16:brightness=-0.02:saturation=0.82,"
        f"vignette=PI/3.6,"
        f"noise=alls=6:allf=t+u,"
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
    motion: str = "zoom_in",
    doc_path: Optional[Path] = None
) -> bool:
    """
    Renders an 'After the Crown' scene. If duration >= 10s and a document is provided,
    splits into a 2-shot sequence (Archival Photo -> Declassified Document) for dynamic pacing.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if doc_path and doc_path.exists() and duration >= 10.0:
        d1 = duration * 0.55
        d2 = duration - d1
        
        shot1 = TEMP_DIR / f"{output_path.stem}_s1.mp4"
        shot2 = TEMP_DIR / f"{output_path.stem}_s2.mp4"
        concat_txt = TEMP_DIR / f"{output_path.stem}_concat.txt"
        
        logger.info(f"Rendering 2-shot sequence: Archival Photo ({d1:.1f}s) + Declassified Doc ({d2:.1f}s)...")
        if render_clip(image_path, d1, shot1, motion="slow_zoom_in") and render_clip(doc_path, d2, shot2, motion="slow_zoom_out"):
            with open(concat_txt, "w", encoding="utf-8") as f:
                f.write(f"file '{shot1.resolve().as_posix()}'\n")
                f.write(f"file '{shot2.resolve().as_posix()}'\n")
                
            cmd = [
                FFMPEG_BIN, "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_txt),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-t", f"{duration:.3f}",
                "-shortest",
                str(output_path)
            ]
            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                return True
            except subprocess.CalledProcessError as e:
                logger.warning(f"2-shot concat failed: {e.stderr}. Falling back to single shot.")

    # Single-shot fallback
    shot_tmp = TEMP_DIR / f"{output_path.stem}_raw.mp4"
    if render_clip(image_path, duration, shot_tmp, motion=motion):
        cmd_mux = [
            FFMPEG_BIN, "-y",
            "-i", str(shot_tmp),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{duration:.3f}",
            "-shortest",
            str(output_path)
        ]
        try:
            subprocess.run(cmd_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio mux failed: {e.stderr}")
            return False
            
    return False

def concatenate_scenes(scene_videos: List[Path], final_output: Path, background_music: Optional[Path] = None) -> bool:
    """
    Concatenates all scenes into the continuous documentary timeline.
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
        logger.info("Concatenating scenes into final documentary timeline...")
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg concat failed: {e.stderr}")
        return False

    # If background music is provided, mix it with auto-ducking (10% under narration)
    if background_music and background_music.exists():
        logger.info(f"Mastering audio with atmospheric soundtrack '{background_music.name}'...")
        cmd_audio = [
            FFMPEG_BIN,
            "-y",
            "-i", str(raw_concat),
            "-stream_loop", "-1",
            "-i", str(background_music),
            "-filter_complex",
            "[0:a]volume=1.0[voice];[1:a]volume=0.10[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=3[aout]",
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
            logger.warning(f"Audio mix failed: {e.stderr}. Using raw concat.")
            
    import shutil
    shutil.copy(raw_concat, final_output)
    return True
