import json
import logging
import os
import re
import time
from typing import Dict, Any, List, Optional
import requests
from src.config import GEMINI_API_KEY

logger = logging.getLogger("Scriptwriter")

CANDIDATE_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-pro-latest"
]

def clean_json_response(raw_text: str) -> str:
    """Strips markdown backticks, removes trailing commas, and trims to valid JSON."""
    cleaned = re.sub(r'^```(?:json)?\s*', '', raw_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned).strip()
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r',\s*([\]}])', r'\1', cleaned)
    return cleaned

def call_gemini_json(prompt: str, temperature: float = 0.25, max_tokens: int = 4096) -> Dict[str, Any]:
    """
    Robust caller for Gemini API with multi-model failover and JSON parsing.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }
    headers = {"Content-Type": "application/json"}

    last_error = None
    for model in CANDIDATE_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(3):
            try:
                logger.info(f"Calling Gemini ({model}, attempt {attempt+1})...")
                r = requests.post(url, json=payload, headers=headers, timeout=40)
                if r.status_code == 200:
                    cand = r.json().get("candidates", [{}])[0]
                    raw_text = cand.get("content", {}).get("parts", [{}])[0].get("text", "")
                    clean_str = clean_json_response(raw_text)
                    return json.loads(clean_str)
                elif r.status_code in [429, 503]:
                    logger.warning(f"Model {model} returned HTTP {r.status_code}. Retrying with backoff...")
                    time.sleep(2 * (attempt + 1))
                else:
                    logger.warning(f"Model {model} returned HTTP {r.status_code}: {r.text[:120]}")
                    break
            except Exception as e:
                logger.warning(f"Gemini call exception with {model}: {e}")
                last_error = e
                time.sleep(2)

    raise RuntimeError(f"Failed to obtain valid JSON from Gemini API: {last_error}")

def generate_master_outline(topic: str, total_scenes: int, num_acts: int = 5) -> Dict[str, Any]:
    """
    Tier 1: Generates the Master Narrative Outline dividing the documentary into chronological Acts.
    """
    scenes_per_act = max(5, total_scenes // num_acts)
    remainder = total_scenes % num_acts

    prompt = f"""You are the senior researcher and director for 'After the Crown', a premier historical documentary channel.
Design a comprehensive {num_acts}-Act Master Narrative Outline for a long-form documentary about:
"{topic}"

Total scenes required across the documentary: {total_scenes} (~{total_scenes * 20 / 60:.1f} minutes).
Style: Serious, forensic, analytical, grounded in real declassified dossiers, primary sources, and authentic chronology.

JSON Schema:
{{
  "title": "Documentary Title",
  "premise": "Core investigative thesis in 2 sentences",
  "acts": [
    {{
      "act_number": 1,
      "act_title": "Title of Act (e.g. 'Act I: The Alpine Safehouse')",
      "time_and_place": "Location and date (e.g. 'June 1946, Berchtesgaden')",
      "synopsis": "What this specific chapter investigates and uncovers",
      "key_historical_figures_and_records": ["Figure 1", "Dossier 2"],
      "target_scenes": {scenes_per_act}
    }}
  ]
}}

Return ONLY valid JSON.
"""
    outline = call_gemini_json(prompt, temperature=0.20, max_tokens=3000)
    acts = outline.get("acts", [])
    if not acts:
        raise ValueError("Failed to generate narrative acts in outline!")

    # Distribute remainder scenes to later acts
    for i in range(remainder):
        acts[-(i+1)]["target_scenes"] = acts[-(i+1)].get("target_scenes", scenes_per_act) + 1

    return outline

def generate_act_scenes(
    topic: str,
    doc_title: str,
    act_info: Dict[str, Any],
    prev_context: str
) -> List[Dict[str, Any]]:
    """
    Tier 2: Generates granular 4-beat scenes for a single Act maintaining narrative flow.
    """
    act_num = act_info.get("act_number", 1)
    act_title = act_info.get("act_title", f"Act {act_num}")
    setting = act_info.get("time_and_place", "Postwar Europe")
    synopsis = act_info.get("synopsis", "")
    records = act_info.get("key_historical_figures_and_records", [])
    target_scenes = act_info.get("target_scenes", 10)

    prompt = f"""You are the script director for 'After the Crown'.
Generate the exact documentary script for {act_title} of "{doc_title}".

Context from previous chapters:
{prev_context if prev_context else 'Opening act of the investigation.'}

Act Details:
- Chapter: {act_title}
- Setting / Date: {setting}
- Chapter Focus: {synopsis}
- Key historical figures & archival dossiers: {', '.join(records) if records else 'Declassified files'}
- Required Scenes: Exactly {target_scenes} scenes.

Every scene MUST strictly follow the After the Crown multi-beat standard:
- label_title: Primary Name or Location (e.g. 'Berchtesgaden', 'Paula Hitler', 'Dossier C10')
- label_sub: Context or Date (e.g. 'Bavarian Alps // June 1946')
- citation: Source marker (e.g. '[1]' or '[2, 3]')
- callout_red: OPTIONAL short 2-4 word dramatic forensic callout in caps (or null)
- callout_box: OPTIONAL typewriter archive note in caps (or null)
- target_beats: 4
- beats: exactly 4 beats. Each beat MUST have:
    - narration: Concise, solemn narration sentence (~8-10 words, ~3.5 seconds).
    - search_query: Authentic historical photograph/document query (using real historical names, places, dates, archive terms).
- ken_burns_motion: One of 'slow_zoom_in', 'pan_left', 'slow_zoom_out', 'pan_right'

JSON Schema:
{{
  "act_number": {act_num},
  "scenes": [
    {{
      "label_title": "Location or Person",
      "label_sub": "Context and Date",
      "citation": "[1]",
      "callout_red": null,
      "callout_box": null,
      "target_beats": 4,
      "ken_burns_motion": "slow_zoom_in",
      "beats": [
        {{
          "beat_id": 1,
          "narration": "First concise sentence (~8-10 words).",
          "search_query": "Authentic historical photograph query"
        }},
        {{
          "beat_id": 2,
          "narration": "Second sentence introducing document or person.",
          "search_query": "Historical document or portrait query"
        }},
        {{
          "beat_id": 3,
          "narration": "Third sentence detailing the investigative finding.",
          "search_query": "Historical archive photograph query"
        }},
        {{
          "beat_id": 4,
          "narration": "Fourth sentence concluding the scene beat.",
          "search_query": "Historical evidence or aftermath query"
        }}
      ]
    }}
  ]
}}

Return ONLY valid JSON.
"""
    res = call_gemini_json(prompt, temperature=0.25, max_tokens=4000)
    scenes = res.get("scenes", [])
    if not scenes:
        logger.warning(f"No scenes returned for Act {act_num}. Retrying...")
        time.sleep(2)
        res = call_gemini_json(prompt, temperature=0.35, max_tokens=4000)
        scenes = res.get("scenes", [])
    return scenes

def generate_documentary_script(topic: str, num_scenes: int = 8) -> Dict[str, Any]:
    """
    Master documentary script generation pipeline:
    - If num_scenes <= 12: Uses single-pass focused script generation.
    - If num_scenes > 12: Automatically activates the Multi-Act Chapter Architecture (for 10-30 min long-form productions).
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    logger.info(f"Generating documentary script for '{topic}' ({num_scenes} scenes requested)...")

    # Mode A: Short format (<= 12 scenes, ~3 to 5 minutes)
    if num_scenes <= 12:
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
      "narration": "Measured documentary narration sentence for this scene.",
      "label_title": "Primary Name or Location (e.g. 'Berchtesgaden')",
      "label_sub": "Context or Date (e.g. 'Bavarian Alps // June 1946')",
      "citation": "[1]",
      "callout_red": null,
      "callout_box": null,
      "target_beats": 4,
      "ken_burns_motion": "slow_zoom_in",
      "beats": [
        {{
          "beat_id": 1,
          "narration": "First concise sentence (~8-10 words, ~3.5 seconds).",
          "search_query": "Historical photo query 1"
        }},
        {{
          "beat_id": 2,
          "narration": "Second sentence introducing person or document.",
          "search_query": "Historical photo query 2"
        }},
        {{
          "beat_id": 3,
          "narration": "Third sentence providing historical context.",
          "search_query": "Historical photo query 3"
        }},
        {{
          "beat_id": 4,
          "narration": "Fourth sentence concluding the scene beat.",
          "search_query": "Historical photo query 4"
        }}
      ]
    }}
  ]
}}

Return ONLY valid JSON.
"""
        script = call_gemini_json(prompt, temperature=0.25, max_tokens=4000)
        # Validate scenes
        scenes = script.get("scenes", [])
        for idx, sc in enumerate(scenes, 1):
            sc["scene_id"] = idx
            if not sc.get("narration") and sc.get("beats"):
                sc["narration"] = " ".join(b.get("narration", "") for b in sc["beats"])
        return script

    # Mode B: Long-form multi-act pipeline (> 12 scenes, 10 to 30+ minutes)
    num_acts = 5 if num_scenes >= 40 else (4 if num_scenes >= 24 else 3)
    logger.info(f"Activating Multi-Act Architecture: {num_scenes} scenes split across {num_acts} narrative Acts...")

    outline = generate_master_outline(topic, total_scenes=num_scenes, num_acts=num_acts)
    doc_title = outline.get("title", f"Documentary: {topic}")
    acts = outline.get("acts", [])

    all_scenes: List[Dict[str, Any]] = []
    prev_context = f"Investigation topic: {topic}. Premise: {outline.get('premise', '')}"

    for act_idx, act in enumerate(acts, 1):
        logger.info(f"Writing Act {act_idx}/{len(acts)}: '{act.get('act_title')}' ({act.get('target_scenes')} scenes)...")
        act_scenes = generate_act_scenes(
            topic=topic,
            doc_title=doc_title,
            act_info=act,
            prev_context=prev_context
        )
        all_scenes.extend(act_scenes)

        # Update running context
        prev_context = (
            f"Previous Act ({act.get('act_title')}): {act.get('synopsis')} "
            f"Finished scenes covering {act.get('time_and_place')}."
        )

    # Re-index all scenes sequentially (1 to N)
    for idx, sc in enumerate(all_scenes, 1):
        sc["scene_id"] = idx
        if not sc.get("target_beats"):
            sc["target_beats"] = len(sc.get("beats", [])) or 4
        if not sc.get("narration") and sc.get("beats"):
            sc["narration"] = " ".join(b.get("narration", "") for b in sc["beats"])
        if not sc.get("ken_burns_motion"):
            motions = ["slow_zoom_in", "pan_left", "slow_zoom_out", "pan_right"]
            sc["ken_burns_motion"] = motions[(idx - 1) % len(motions)]

    master_script = {
        "title": doc_title,
        "topic": topic,
        "premise": outline.get("premise"),
        "total_acts": len(acts),
        "total_scenes": len(all_scenes),
        "acts_outline": acts,
        "scenes": all_scenes
    }

    logger.info(f"Master long-form documentary script created: {len(all_scenes)} scenes ({len(all_scenes)*4} visual cuts) across {len(acts)} Acts.")
    return master_script
