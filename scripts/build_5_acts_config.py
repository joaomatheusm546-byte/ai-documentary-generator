import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import FFPROBE_BIN

MASTER_SCRIPT_PATH = ROOT_DIR / "assets" / "hitler_family_master_script.json"
AUDIO_DIR = ROOT_DIR / "assets" / "full_narration_audio"
SRC_DIR = ROOT_DIR / "remotion_app" / "src"

def get_audio_duration(p: Path) -> float:
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(p)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 4.2

def determine_archetype(s_id: int, b_id: int, narration: str, subject: str, query: str):
    narr_l = narration.lower()
    sub_l = subject.lower()
    q_l = query.lower()

    # 1. Family Tree points
    if (s_id == 1 and b_id == 4) or (s_id == 8 and b_id == 1):
        return {
            "layoutType": "family_tree",
            "treeData": {
                "title": "Origins of the Hitler Lineage",
                "subtitle": "Lower Austria // 1837 Paternity Mystery",
                "nodes": [
                    {"id": "maria", "name": "Maria Schicklgruber", "role": "Mother (1795-1847)", "x": 30, "y": 35, "image": "cutouts/maria_schicklgruber_cutout.png"},
                    {"id": "father", "name": "Unknown Father", "role": "Unrecorded in Register", "x": 70, "y": 35, "isQuestion": True},
                    {"id": "alois", "name": "Alois Schicklgruber", "role": "Son (1837-1903)", "x": 50, "y": 72, "image": "cutouts/alois_hitler_cutout.png"},
                ],
                "links": [
                    {"from": "maria", "to": "alois", "style": "solid", "color": "#b91c1c"},
                    {"from": "father", "to": "alois", "style": "dashed", "color": "#b45309"},
                ]
            }
        }
    
    if s_id == 40 and b_id == 3:
        return {
            "layoutType": "family_tree",
            "treeData": {
                "title": "The Long Island Bloodline Pact",
                "subtitle": "Extinction of the Direct Lineage // Present Day",
                "nodes": [
                    {"id": "adolf", "name": "Adolf Hitler", "role": "1889-1945 // No Offspring", "x": 25, "y": 35, "isDead": True},
                    {"id": "alois_jr", "name": "Alois Hitler Jr.", "role": "Half-Brother (1882-1956)", "x": 50, "y": 35, "isDead": True},
                    {"id": "william", "name": "William Patrick Stuart-Houston", "role": "Son (1911-1987)", "x": 50, "y": 62, "isDead": True},
                    {"id": "sons", "name": "The Three Sons", "role": "Pact of Silence // Extinction", "x": 75, "y": 62, "isQuestion": True},
                ],
                "links": [
                    {"from": "alois_jr", "to": "william", "style": "solid", "color": "#8b1e1e"},
                    {"from": "william", "to": "sons", "style": "solid", "color": "#8b1e1e"},
                ]
            }
        }

    # 2. Split Collage
    if any(k in narr_l for k in ["married", "legitimized", "inscribed", "interrogation", "engaged", "dossier", "confrontation"]) and b_id in [2, 3]:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": f"images/scene_{s_id:03d}_beat_02.jpg",
                "rightSubject": "cutouts/alois_hitler_cutout.png" if "alois" in narr_l else "cutouts/maria_schicklgruber_cutout.png",
                "highlightText": "CLASSIFIED FORENSIC DOSSIER"
            }
        }

    # 3. Document
    if any(k in narr_l or k in q_l for k in ["register", "parish", "book", "taufbuch", "certificate", "document", "records", "entry", "signature", "passport", "dossier", "file", "letter", "report", "deed"]):
        return {
            "layoutType": "document",
            "highlightText": "CONFIDENTIAL ARCHIVE"
        }

    # 4. Portrait Cutout
    if any(k in narr_l or k in sub_l for k in ["woman", "miller", "mother", "father", "sister", "paula", "alois", "maria", "portrait", "adolf", "johann", "brother", "geli", "william", "angela", "nepomuk"]):
        cutout_target = "cutouts/alois_hitler_cutout.png"
        if "maria" in narr_l or "maria" in sub_l:
            cutout_target = "cutouts/maria_schicklgruber_cutout.png"
        elif "hiedler" in narr_l or "hiedler" in sub_l:
            cutout_target = "cutouts/johann_georg_hiedler_cutout.png"
            
        return {
            "layoutType": "portrait",
            "subjectImage": cutout_target
        }

    # 5. Landscape
    return {
        "layoutType": "landscape"
    }

def build_act_configs():
    master_data = json.loads(MASTER_SCRIPT_PATH.read_text(encoding="utf-8"))
    scenes = master_data.get("scenes", [])
    
    # 5 Acts (8 scenes per act)
    act_ranges = [
        (1, "Act I: The Waldviertel Web", range(0, 8)),
        (2, "Act II: Shadows of the Inner Circle", range(8, 16)),
        (3, "Act III: The American Heresy", range(16, 24)),
        (4, "Act IV: The Allied Dossiers", range(24, 32)),
        (5, "Act V: The Final Pact", range(32, 40)),
    ]
    
    for act_num, act_title, sc_range in act_ranges:
        act_scenes = [scenes[i] for i in sc_range if i < len(scenes)]
        act_beats = []
        total_frames = 0
        
        for sc in act_scenes:
            s_id = sc.get("scene_id")
            for b in sc.get("beats", []):
                b_id = b.get("beat_id")
                narr = b.get("narration", "")
                sub = b.get("canonical_subject", "")
                q = b.get("search_query", "")
                
                audio_file = f"voice_s{s_id:03d}_b{b_id:02d}.mp3"
                audio_path = AUDIO_DIR / audio_file
                dur = get_audio_duration(audio_path)
                padded_dur = dur + 0.38
                frames = int(round(padded_dur * 30))
                total_frames += frames
                
                arch = determine_archetype(s_id, b_id, narr, sub, q)
                
                beat_entry = {
                    "id": f"s{s_id}_b{b_id}",
                    "durationInFrames": frames,
                    "layoutType": arch["layoutType"],
                    "bgImage": f"images/scene_{s_id:03d}_beat_{b_id:02d}.jpg",
                    "subjectImage": arch.get("subjectImage"),
                    "labelTitle": b.get("label_title") or sub[:25] or f"Scene {s_id}",
                    "labelSubtitle": b.get("label_subtitle") or f"Historical Archive // Folio {s_id*4 + b_id}",
                    "highlightText": arch.get("highlightText", "ARCHIVAL RECORD"),
                    "hasBoom": (b_id == 1 or b_id == 4),
                    "citation": f"[{act_num}, {s_id}] Sources in Description",
                    "audioSrc": f"audio/{audio_file}",
                }
                
                if "treeData" in arch:
                    beat_entry["treeData"] = arch["treeData"]
                if "splitData" in arch:
                    beat_entry["splitData"] = arch["splitData"]
                    
                act_beats.append(beat_entry)
                
        act_config = {
            "title": f"The Hitler Bloodline - {act_title}",
            "actNumber": act_num,
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "musicSrc": "audio/music.mp3",
            "beats": act_beats,
        }
        
        cfg_path = SRC_DIR / f"act_{act_num}_config.json"
        cfg_path.write_text(json.dumps(act_config, indent=2), encoding="utf-8")
        dur_sec = total_frames / 30
        print(f"Generated {cfg_path.name}: {len(act_beats)} beats | {total_frames} frames ({dur_sec:.1f}s = {dur_sec/60:.2f} min)")

if __name__ == "__main__":
    build_act_configs()
