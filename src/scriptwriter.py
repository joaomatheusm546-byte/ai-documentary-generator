import json
import time
import logging
import requests
from typing import Dict, Any, List
from src.config import GEMINI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Scriptwriter")

AFTER_THE_CROWN_SYSTEM_PROMPT = """You are the master director and lead investigative writer for high-end historical deep-dive documentaries, in the exact storytelling standard of the renowned YouTube channel 'After the Crown' (@afterthecrown-j6q).

YOUR SIGNATURE FORMULA:
1. HUMAN COLLATERAL DAMAGE: Focus intensely on the forgotten survivors, exiled monarchs, daughters of fallen tyrants, secret mistresses, imperial eunuchs, or siblings caught in the aftermath of historical catastrophes.
2. FORENSIC EVIDENCE & PRIMARY SOURCES: Build each scene around real historical documents, declassified intelligence files, interrogation transcripts, secret diaries, autopsy reports, and obscure trial testimonies.
3. ATMOSPHERIC & HAUNTING PROSE: The narration must be somber, eloquent, investigative, and deeply human. Avoid hype; use dignified, evocative English with dramatic gravitas.
4. NARRATIVE ARCS:
   - Scene 1 (The Ruin / The Arrest): Establish the immediate aftermath of the regime's collapse and the protagonist's quiet capture or displacement.
   - Middle Scenes (The Interrogation & Exile): Forensic investigation into aliases, secret pensions, asylum life, poverty, or political surveillance.
   - Climax Scene (The Final Isolation): Their final years, forgotten burial, or desperate petition to claim their identity/estate.
   - Final Scene (The Historical Verdict): The lingering moral question—were they an innocent hostage of their bloodline, or a complicit bystander?

FOR EVERY SCENE, PROVIDE:
1. "narration": Spoken script (50-70 words per scene), written in the gripping 'After the Crown' style.
2. "visual_type": "archival_photo" or "declassified_document" or "historical_portrait".
3. "search_queries": 4 precise, highly specific search terms targeting public domain historical archives, museum collections, and Wikimedia Commons. Focus on mugshots, original interrogation memos, black and white portraits, signed treaties, or burial places.
4. "mood": "somber_investigation", "tragic_ruin", "haunting_suspense", "melancholy_exile".
5. "ken_burns_motion": "slow_zoom_in", "slow_zoom_out", "pan_left", "pan_right".

FORMAT REQUIREMENT:
Output strictly valid JSON matching this schema:
{
  "title": "Documentary Title",
  "summary": "Forensic logline of the investigation",
  "recommended_music_mood": "somber historical cello dark piano atmospheric drone",
  "scenes": [
    {
      "scene_id": 1,
      "narration": "...",
      "visual_type": "...",
      "search_queries": ["...", "...", "..."],
      "mood": "...",
      "ken_burns_motion": "slow_zoom_in"
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
    Generates an 'After the Crown' style documentary script using the Gemini API with automatic model failover.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

    prompt = f"""Write an investigative documentary script in the exact standard of 'After the Crown' on the topic: "{topic}".
It must have exactly {num_scenes} sequential scenes telling the complete, tragic, and forensic post-collapse story.
Ensure the search queries target authentic declassified records, archival photographs, and historical portraits."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": AFTER_THE_CROWN_SYSTEM_PROMPT}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.65
        }
    }

    last_error = None
    for model in CANDIDATE_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(2):
            try:
                logger.info(f"Attempting script generation with model '{model}' (attempt {attempt + 1})...")
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
                
                if response.status_code == 200:
                    result_json = response.json()
                    raw_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                    script_data = json.loads(raw_text)
                    logger.info(f"Successfully generated 'After the Crown' script with '{model}': {script_data.get('title')}")
                    return script_data
                
                if response.status_code in (503, 429):
                    logger.warning(f"Model '{model}' busy (status {response.status_code}). Retrying...")
                    time.sleep(2)
                    continue
                else:
                    break

            except Exception as e:
                last_error = e
                time.sleep(1)

    raise RuntimeError(f"All candidate models failed to generate script. Last error: {last_error}")
