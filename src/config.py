import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EUROPEANA_API_KEY = os.getenv("EUROPEANA_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

# Directory paths
TEMP_DIR = ROOT_DIR / "temp"
OUTPUT_DIR = ROOT_DIR / "output"
ASSETS_DIR = ROOT_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# Detect FFmpeg binary
def get_ffmpeg_path():
    # 1. Environment variable
    if os.getenv("FFMPEG_PATH"):
        return os.getenv("FFMPEG_PATH")
    # 2. PATH
    path_which = shutil.which("ffmpeg")
    if path_which:
        return path_which
    # 3. Known Windows path fallback
    win_custom = Path("C:/Users/matuc/AppData/Local/Programs/FFmpeg/ffmpeg-9.0.2-essentials_build/bin/ffmpeg.exe")
    if win_custom.exists():
        return str(win_custom)
    return "ffmpeg"

def get_ffprobe_path():
    if os.getenv("FFPROBE_PATH"):
        return os.getenv("FFPROBE_PATH")
    path_which = shutil.which("ffprobe")
    if path_which:
        return path_which
    win_custom = Path("C:/Users/matuc/AppData/Local/Programs/FFmpeg/ffmpeg-9.0.2-essentials_build/bin/ffprobe.exe")
    if win_custom.exists():
        return str(win_custom)
    return "ffprobe"

FFMPEG_BIN = get_ffmpeg_path()
FFPROBE_BIN = get_ffprobe_path()

# Video output settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
DEFAULT_VOICE = "en-US-ChristopherNeural"  # Authoritative, calm documentary voice

# ElevenLabs Production Voice Config
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")  # George (British BBC documentary narrator)
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")     # 0.5x credit cost (cheapest high-quality)
USE_ELEVENLABS = bool(ELEVENLABS_API_KEY)

