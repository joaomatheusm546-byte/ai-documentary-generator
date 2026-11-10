import json
import logging
import os
import re
import time
from typing import Dict, Any, List
import requests
from src.config import GEMINI_API_KEY

logger = logging.getLogger("Scriptwriter")

def generate_documentary_script(topic: str, num_scenes: int = 8) -> Dict[str, Any]:
    """
    Generates a broadcast-quality historical documentary script replicating 'After the Crown'.
    Features archival citations, authentic names, locations, and clean lower-third titles.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    prompt = f"""You are the senior researcher and director for 'After the Crown', a premier historical documentary channel on YouTube.
Create a deeply researched, serious, cinematic documentary script about: "{topic}".

The tone must be:
- Sober, measured, analytical, and respectful (like BBC / PBS / After the Crown).
- Grounded in real historical facts, dates, declassified intelligence reports, and primary archive evidence.
- Written for a calm, authoritative male narrator speaking in measured documentary cadence.

Produce exactly {num_scenes} scenes in valid JSON format.

JSON Schema:
{{
  "title": "Documentary Title",
  "topic": "{topic}",
  "scenes": [
    {{
      "scene_id": 1,
      "narration": "Measured documentary narration sentence(s) for this scene (~14 seconds of speech).",
      "label_title": "Primary Name or Location (e.g. 'Berchtesgaden' or 'Paula Hitler')",
      "label_sub": "Context or Date (e.g. 'Bavarian Alps' or 'May 1945 // Allied Advance')",
      "citation": "[1]",
      "callout_red": "OPTIONAL short 2-4 word dramatic callout in caps (or null)",
      "callout_box": "OPTIONAL typewriter archive note in caps (or null)",
      "target_beats": 4,
      "search_queries": [
        "Historical photo query 1 (establishing shot / primary entity, seconds 0-3.5)",
        "Historical photo query 2 (action / secondary entity / declassified document, seconds 3.5-7.0)",
        "Historical photo query 3 (archival context / location, seconds 7.0-10.5)",
        "Historical photo query 4 (evidence / atmospheric detail, seconds 10.5-14.0)"
      ],
      "ken_burns_motion": "slow_zoom_in"
    }}
  ]
}}

Return ONLY the raw JSON object. Do not include markdown codeblocks or explanation.
"""

    models = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-pro-latest", "gemini-3-flash-preview"]
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096}
    }
    headers = {"Content-Type": "application/json"}

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(2):
            try:
                logger.info(f"Generating script using model {model} (attempt {attempt+1})...")
                r = requests.post(url, json=payload, headers=headers, timeout=35)
                if r.status_code == 200:
                    raw_text = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    clean_json = re.sub(r'^```json\s*', '', raw_text.strip())
                    clean_json = re.sub(r'```$', '', clean_json).strip()
                    return json.loads(clean_json)
                elif r.status_code in [429, 503]:
                    logger.warning(f"Model {model} returned status {r.status_code}, retrying in 3s...")
                    time.sleep(3)
                else:
                    logger.warning(f"Model {model} returned status {r.status_code}")
                    break
            except Exception as e:
                logger.warning(f"Attempt failed with model {model}: {e}")
                time.sleep(2)

    raise RuntimeError("Failed to generate documentary script from Gemini API.")
