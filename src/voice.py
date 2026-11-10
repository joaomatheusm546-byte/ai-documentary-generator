import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import edge_tts
from src.config import FFMPEG_BIN, FFPROBE_BIN, DEFAULT_VOICE, TEMP_DIR

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
    
    # Generate MP3
    communicate = edge_tts.Communicate(text, voice, rate=rate)
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
