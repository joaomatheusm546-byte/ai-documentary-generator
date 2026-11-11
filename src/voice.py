import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import edge_tts
from src.config import FFMPEG_BIN, FFPROBE_BIN, DEFAULT_VOICE, TEMP_DIR
from src.lexicon import prepare_text_for_tts

logger = logging.getLogger(__name__)

# Recommended documentary voices (Microsoft Neural)
DOCUMENTARY_VOICES = {
    "christopher": "en-US-ChristopherNeural",  # Authoritative, serious, deep forensic tone
    "ryan": "en-GB-RyanNeural",                # British, somber, documentary narrator
    "brian": "en-US-BrianNeural",              # British, sophisticated, historical
    "eric": "en-US-EricNeural",                # Engaging, cinematic
    "sonia": "en-GB-SoniaNeural"               # Refined historical female narrator
}

async def generate_scene_voice(
    text: str,
    output_path: Path,
    voice: str = DEFAULT_VOICE,
    rate: str = "-7%" # Calibrated slower cadence for 'After the Crown' solemn gravitas
) -> Dict[str, Any]:
    """
    Synthesizes speech using Edge-TTS and returns metadata including exact duration.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Apply phonetic calibration for canonical documentary entities
    calibrated_text = prepare_text_for_tts(text)
    
    # Generate MP3
    communicate = edge_tts.Communicate(calibrated_text, voice, rate=rate)
    await communicate.save(str(output_path))
    
    # Get exact duration via ffprobe
    duration = get_audio_duration(output_path)
    
    word_count = len(text.split())
    
    return {
        "audio_path": str(output_path),
        "duration": duration,
        "word_count": word_count,
        "voice": voice
    }

def get_audio_duration(audio_path: Path) -> float:
    """
    Uses ffprobe to obtain exact audio duration in seconds.
    """
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception as e:
        logger.warning(f"ffprobe duration check failed: {e}. Falling back to 5.0s default estimate.")
        return 5.0

def synthesize_scene_audio(text: str, output_path: Path, voice: str = DEFAULT_VOICE) -> Dict[str, Any]:
    """
    Synchronous wrapper for generate_scene_voice.
    """
    return asyncio.run(generate_scene_voice(text, output_path, voice))

def synthesize_beat_audio(
    text: str,
    output_path: Path,
    voice: str = DEFAULT_VOICE,
    pause_after: float = 0.45
) -> Dict[str, Any]:
    """
    Synthesizes speech for an individual sentence beat and shapes the pause naturally.
    Detects where the speech actually ends and ensures zero truncation of trailing syllables.
    Appends a subtle fade-out in pure silence to eliminate any abrupt cuts or pops.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = output_path.with_name(f"{output_path.stem}_raw.mp3")
    meta = asyncio.run(generate_scene_voice(text, raw_path, voice=voice))
    raw_dur = meta["duration"]

    try:
        # Run silencedetect to find where speech actually finishes (-60dB noise threshold)
        cmd_sil = [
            FFMPEG_BIN, "-i", str(raw_path),
            "-af", "silencedetect=noise=-60dB:d=0.2",
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd_sil, stderr=subprocess.PIPE, text=True, check=True)
        sil_starts = []
        for line in res.stderr.splitlines():
            if "silence_start:" in line:
                try:
                    val = float(line.split("silence_start:")[1].strip())
                    sil_starts.append(val)
                except ValueError:
                    pass

        # If trailing silence detected towards the end
        if sil_starts and sil_starts[-1] > 0.8:
            speech_end = sil_starts[-1]
        else:
            speech_end = raw_dur

        target_dur = speech_end + pause_after

        if target_dur < raw_dur:
            fade_st = max(0.0, target_dur - 0.05)
            af = f"atrim=0:{target_dur:.3f},afade=t=out:st={fade_st:.3f}:d=0.05"
            cmd_process = [
                FFMPEG_BIN, "-y",
                "-i", str(raw_path),
                "-af", af,
                "-c:a", "libmp3lame", "-q:a", "2",
                str(output_path)
            ]
            subprocess.run(cmd_process, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        else:
            pad_needed = max(0.0, target_dur - raw_dur)
            af = f"apad=pad_dur={pad_needed:.3f}" if pad_needed > 0 else "anull"
            cmd_process = [
                FFMPEG_BIN, "-y",
                "-i", str(raw_path),
                "-af", af,
                "-c:a", "libmp3lame", "-q:a", "2",
                str(output_path)
            ]
            subprocess.run(cmd_process, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if raw_path.exists():
            raw_path.unlink()

        final_dur = get_audio_duration(output_path)
        meta["duration"] = final_dur
        meta["audio_path"] = str(output_path)
        return meta

    except Exception as e:
        logger.warning(f"Safe audio shaping failed: {e}. Falling back to raw audio.")
        if raw_path.exists():
            import shutil
            shutil.move(str(raw_path), str(output_path))
        return meta

def concatenate_beat_audios(beat_audio_paths: List[Path], output_path: Path) -> float:
    """
    Concatenates individual beat audio files into a single seamless scene audio track.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    list_file = output_path.with_name(f"{output_path.stem}_concat_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for p in beat_audio_paths:
            posix_p = p.resolve().as_posix()
            f.write(f"file '{posix_p}'\n")
            
    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c:a", "libmp3lame",
        "-q:a", "2",
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if list_file.exists():
        list_file.unlink()
    return get_audio_duration(output_path)

