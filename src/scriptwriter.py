import json
import time
import logging
import requests
from typing import Dict, Any, List
from src.config import GEMINI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Scriptwriter")

SYSTEM_PROMPT = """You are an elite historical and scientific documentary director and scriptwriter (in the style of Ken Burns, BBC, and National Geographic).
Your goal is to write captivating, accurate, and deeply immersive documentary scripts in English.

For every scene, you MUST provide:
1. "narration": The spoken voiceover text. It must be eloquent, engaging, and paced like a real narrator.
2. "visual_type": "archive_image" or "stock_video".
3. "search_queries": A list of 3-4 precise English search terms to find authentic archival footage, historical paintings, artifacts, or footage in public domain archives (Wikimedia Commons, Internet Archive, Pexels).
   IMPORTANT: Be very specific for archives (e.g. "Library of Alexandria painting engraving", "Ancient papyrus scroll Alexandria", "Ptolemy I Soter coin bust").
4. "mood": Emotional tone ("mysterious", "dramatic", "melancholy", "epic", "triumphant").
5. "ken_burns_motion": Suggested camera move for still images ("zoom_in", "zoom_out", "pan_left", "pan_right").

Format your entire response as a valid JSON object matching this structure:
{
  "title": "Documentary Title",
  "summary": "Brief 2-sentence summary",
  "recommended_music_mood": "cinematic orchestral ambient suspense",
  "scenes": [
    {
      "scene_id": 1,
      "narration": "...",
      "visual_type": "archive_image",
      "search_queries": ["...", "..."],
      "mood": "...",
      "ken_burns_motion": "zoom_in"
    }
  ]
}
"""

CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest"
]

def generate_documentary_script(topic: str, num_scenes: int = 5) -> Dict[str, Any]:
    """
    Generates a structured documentary script using the Gemini API with automatic model failover.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

    prompt = f"""Write an exceptional documentary script on the topic: "{topic}".
It must have exactly {num_scenes} distinct scenes that tell a complete, gripping narrative from prologue to climax and conclusion.
Ensure the search queries are highly specific so we can retrieve authentic public domain images/historical art for each scene."""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": SYSTEM_PROMPT}
            ]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }

    last_error = None

    for model in CANDIDATE_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(2):
            try:
                logger.info(f"Attempting script generation with model '{model}' (attempt {attempt + 1})...")
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=40)
                
                if response.status_code == 200:
                    result_json = response.json()
                    raw_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                    script_data = json.loads(raw_text)
                    logger.info(f"Successfully generated script with '{model}': {script_data.get('title')}")
                    return script_data
                
                if response.status_code in (503, 429):
                    logger.warning(f"Model '{model}' busy (status {response.status_code}). Backing off...")
                    time.sleep(2)
                    continue
                else:
                    logger.warning(f"Model '{model}' returned HTTP {response.status_code}: {response.text[:200]}")
                    break

            except Exception as e:
                last_error = e
                logger.warning(f"Error querying '{model}': {e}")
                time.sleep(1)

    raise RuntimeError(f"All candidate models failed to generate script. Last error: {last_error}")
