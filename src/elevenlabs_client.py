import os
import hashlib
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import requests

from src.config import ROOT_DIR, FFPROBE_BIN, FFMPEG_BIN
from src.lexicon import prepare_text_for_tts

logger = logging.getLogger(__name__)

# Defaults configured for After the Crown solemn documentary style
DEFAULT_ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George (British, solemn, storytelling)
DEFAULT_ELEVENLABS_MODEL_ID = "eleven_turbo_v2_5"      # 0.5x credit cost (cheapest high-quality)

# Persistent archival voice cache directory (ensures zero redundant credit spend)
VOICE_CACHE_DIR = ROOT_DIR / "assets" / "voice_cache" / "elevenlabs"
VOICE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Recommended settings for George in historical documentary
DEFAULT_VOICE_SETTINGS = {
    "stability": 0.55,          # Slightly lowered for expressive gravitas and human pacing
    "similarity_boost": 0.80,   # High voice fidelity
    "style": 0.15,              # Subtle dramatic flair
    "use_speaker_boost": True
}

def get_audio_duration(audio_path: Path) -> float:
    """Uses ffprobe to obtain exact audio duration in seconds."""
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
        logger.warning(f"ffprobe duration check failed: {e}. Defaulting to 4.5s.")
        return 4.5

def get_cache_key(text: str, voice_id: str, model_id: str, settings: Dict[str, Any]) -> str:
    """Computes a deterministic hash for the generation parameters."""
    normalized_text = " ".join(text.strip().split())
    raw_key = f"{voice_id}|{model_id}|{json.dumps(settings, sort_keys=True)}|{normalized_text}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:24]

def synthesize_with_elevenlabs(
    text: str,
    output_path: Path,
    voice_id: str = DEFAULT_ELEVENLABS_VOICE_ID,
    model_id: str = DEFAULT_ELEVENLABS_MODEL_ID,
    voice_settings: Optional[Dict[str, Any]] = None,
    apply_phonetics: bool = False, # ElevenLabs Multilingual/Turbo naturally handles German phonetics
    force_regenerate: bool = False,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesizes speech using ElevenLabs API with persistent disk caching.
    GUARANTEE: If the exact text has already been synthesized, reuses cached audio
    with ZERO API calls and ZERO credit consumption.
    """
    key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
    if not key:
        raise ValueError("ELEVENLABS_API_KEY not found in environment or arguments.")

    settings = voice_settings or DEFAULT_VOICE_SETTINGS
    clean_text = prepare_text_for_tts(text) if apply_phonetics else " ".join(text.strip().split())
    
    char_count = len(clean_text)
    cache_hash = get_cache_key(clean_text, voice_id, model_id, settings)
    cached_file = VOICE_CACHE_DIR / f"{cache_hash}.mp3"
    meta_file = VOICE_CACHE_DIR / f"{cache_hash}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Check Cache (Zero Credit Protection)
    if not force_regenerate and cached_file.exists() and cached_file.stat().st_size > 2000:
        shutil.copy(cached_file, output_path)
        dur = get_audio_duration(output_path)
        cost = 0
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                cost = meta.get("character_cost", 0)
            except Exception:
                pass
        print(f"  [CACHE HIT - 0 CREDITS] Reused {cached_file.name} for: '{clean_text[:40]}...' ({dur:.2f}s)")
        return {
            "audio_path": str(output_path),
            "duration": dur,
            "character_cost": 0,
            "cached": True,
            "characters": char_count,
            "voice_id": voice_id,
            "model_id": model_id
        }

    # 2. Make ElevenLabs API Request
    print(f"  [ELEVENLABS API CALL] Synthesizing ({char_count} chars): '{clean_text[:50]}...'")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": clean_text,
        "model_id": model_id,
        "voice_settings": settings
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        if response.status_code != 200:
            err_msg = f"ElevenLabs API error {response.status_code}: {response.text}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        billed_cost = int(response.headers.get("character-cost", char_count // 2 if "turbo" in model_id else char_count))
        
        # Save to persistent cache
        with open(cached_file, "wb") as f:
            f.write(response.content)

        # Save metadata
        meta = {
            "text": clean_text,
            "voice_id": voice_id,
            "model_id": model_id,
            "character_cost": billed_cost,
            "characters": char_count,
            "settings": settings
        }
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        # Copy to destination output path
        shutil.copy(cached_file, output_path)
        dur = get_audio_duration(output_path)

        print(f"  [SUCCESS] Billed {billed_cost} credits | Duration: {dur:.2f}s | Saved to {output_path.name}")
        return {
            "audio_path": str(output_path),
            "duration": dur,
            "character_cost": billed_cost,
            "cached": False,
            "characters": char_count,
            "voice_id": voice_id,
            "model_id": model_id
        }

    except Exception as e:
        logger.error(f"ElevenLabs synthesis failed: {e}")
        raise
