import os
import json
import shutil
import asyncio
import subprocess
from pathlib import Path

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    from rembg import remove
except ImportError:
    remove = None

ROOT_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = ROOT_DIR / "assets" / "hitler_family_archive"
MUSIC_DIR = ROOT_DIR / "assets" / "music"
SFX_DIR = ROOT_DIR / "assets" / "sfx"
MASTER_SCRIPT_PATH = ROOT_DIR / "assets" / "hitler_family_master_script.json"

REMOTION_DIR = ROOT_DIR / "remotion_app"
PUBLIC_DIR = REMOTION_DIR / "public"
IMAGES_DIR = PUBLIC_DIR / "images"
CUTOUTS_DIR = PUBLIC_DIR / "cutouts"
AUDIO_DIR = PUBLIC_DIR / "audio"
SRC_DIR = REMOTION_DIR / "src"

FFPROBE_BIN = shutil.which("ffprobe") or "ffprobe"

def get_audio_duration(audio_path: Path) -> float:
    try:
        cmd = [
            FFPROBE_BIN,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception as e:
        return 4.5

async def synthesize_voice(text: str, output_path: Path, voice: str = "en-US-ChristopherNeural", rate: str = "-7%"):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 1000:
        return
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))

def determine_layout_archetype(scene_idx: int, beat_idx: int, scene_data: dict, beat_data: dict) -> dict:
    """
    Intelligently routes each beat to the most engaging visual archetype:
    - 'family_tree'
    - 'split_collage'
    - 'portrait'
    - 'document'
    - 'landscape'
    """
    narration = beat_data.get("narration", "").lower()
    subject = beat_data.get("canonical_subject", "").lower()
    query = beat_data.get("search_query", "").lower()

    # 1. Family Tree Trigger Points (Scenes 1.4, 8.1, 40.3)
    if scene_idx == 0 and beat_idx == 3:
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
    
    if scene_idx == 39 and beat_idx == 2:
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

    # 2. Split Collage Trigger Points (when document links directly to an individual)
    if any(k in narration for k in ["married", "legitimized", "inscribed", "interrogation", "engaged", "dossier"]) and beat_idx in [1, 2]:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": f"images/scene_{scene_idx+1:03d}_beat_02.jpg",
                "rightSubject": f"cutouts/alois_hitler_cutout.png" if "alois" in narration else "cutouts/maria_schicklgruber_cutout.png",
                "highlightText": "CLASSIFIED ARCHIVE"
            }
        }

    # 3. Document Trigger Points
    if any(k in narration or k in query for k in ["register", "parish", "book", "taufbuch", "certificate", "document", "records", "entry", "signature", "passport", "dossier"]):
        return {
            "layoutType": "document",
            "highlightText": "CONFIDENTIAL RECORD"
        }

    # 4. Portrait Trigger Points
    if any(k in narration or k in subject for k in ["woman", "miller", "mother", "father", "sister", "paula", "alois", "maria", "portrait", "adolf", "johann", "brother"]):
        return {
            "layoutType": "portrait"
        }

    # 5. Fallback: Establishing Landscape
    return {
        "layoutType": "landscape"
    }

async def generate_full_documentary_config(max_scenes: int = 40):
    print(f"=== Generating Full Documentary Configuration (Up to {max_scenes} Scenes) ===")
    
    if not MASTER_SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Master script not found: {MASTER_SCRIPT_PATH}")
    
    master_data = json.loads(MASTER_SCRIPT_PATH.read_text(encoding="utf-8"))
    scenes = master_data.get("scenes", [])[:max_scenes]
    
    total_beats = []
    total_frames = 0
    current_frame = 0
    
    # 4 Musical Acts Definition
    # Act 1: Scenes 1-10 (Origens secretas no Waldviertel e o mistério de Alois)
    # Act 2: Scenes 11-20 (A infância de Adolf, Klara Pölzl e a ascensão em Viena)
    # Act 3: Scenes 21-30 (O Terceiro Reich, a família nas sombras e Geli Raubal)
    # Act 4: Scenes 31-40 (1945, Paula interrogada, o pós-guerra e a extinção em Long Island)
    soundtrack_acts = []
    act_milestones = [0, 10, 20, 30, 40]
    act_names = [
        "Act I: The Illegitimate Origins (1837–1914)",
        "Act II: Shadow of the Dictator (1914–1939)",
        "Act III: The Secret Dynasty & Fall (1939–1945)",
        "Act IV: The Pact of Extinction (1945–Present)",
    ]

    for s_idx, sc in enumerate(scenes):
        scene_id = sc.get("scene_id", s_idx + 1)
        label_title = sc.get("label_title", f"Scene {scene_id}")
        label_sub = sc.get("label_sub", "")
        citation = sc.get("citation", f"[{scene_id}] Sources in Description")
        
        beats = sc.get("beats", [])
        for b_idx, b in enumerate(beats):
            beat_id = f"s{scene_id:02d}_b{b_idx+1}"
            narration = b.get("narration", "")
            
            # Synthesize or verify voice audio
            voice_filename = f"voice_{beat_id}.mp3"
            voice_path = AUDIO_DIR / voice_filename
            await synthesize_voice(narration, voice_path)
            
            duration = get_audio_duration(voice_path)
            padded_duration = duration + 0.4
            frames = int(round(padded_duration * 30))
            
            # Image mapping
            bg_image_name = f"images/scene_{scene_id:03d}_beat_{b_idx+1:02d}.jpg"
            
            # Intelligent Layout Router
            archetype = determine_layout_archetype(s_idx, b_idx, sc, b)
            
            beat_entry = {
                "id": beat_id,
                "durationInFrames": frames,
                "layoutType": archetype["layoutType"],
                "bgImage": bg_image_name,
                "labelTitle": label_title if b_idx == 0 else None,
                "labelSubtitle": label_sub if b_idx == 0 else None,
                "citation": citation,
                "hasBoom": b_idx == 0 or archetype["layoutType"] in ("family_tree", "split_collage"),
                "audioSrc": f"audio/{voice_filename}",
            }
            
            if "treeData" in archetype:
                beat_entry["treeData"] = archetype["treeData"]
            if "splitData" in archetype:
                beat_entry["splitData"] = archetype["splitData"]
            if "highlightText" in archetype:
                beat_entry["highlightText"] = archetype["highlightText"]
                
            total_beats.append(beat_entry)
            current_frame += frames

    # Create Soundtrack Acts with calculated frame windows
    frames_per_scene = current_frame / len(scenes)
    for act_idx in range(len(act_names)):
        start_sc = act_milestones[act_idx]
        end_sc = min(act_milestones[act_idx + 1], len(scenes))
        if start_sc >= len(scenes):
            break
        
        act_start_frame = int(round(start_sc * frames_per_scene))
        act_end_frame = int(round(end_sc * frames_per_scene))
        act_duration = act_end_frame - act_start_frame
        
        soundtrack_acts.append({
            "actId": f"act_{act_idx+1}",
            "name": act_names[act_idx],
            "src": "audio/music.mp3", # In production, each act can point to distinct act_1.mp3, act_2.mp3
            "startFrame": act_start_frame,
            "durationInFrames": act_duration,
        })

    config = {
        "title": "The Hitler Bloodline: From the Secret Origins to the Extinction of the Lineage",
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "musicSrc": "audio/music.mp3",
        "soundtrackActs": soundtrack_acts,
        "beats": total_beats,
    }

    out_json = SRC_DIR / "full_documentary_config.json"
    out_json.write_text(json.dumps(config, indent=2), encoding="utf-8")
    
    print(f"\nGenerated full documentary config: {out_json}")
    print(f"Total Scenes: {len(scenes)}")
    print(f"Total Beats: {len(total_beats)}")
    print(f"Total Duration: {current_frame / 30:.1f}s ({current_frame / (30 * 60):.2f} minutes)")
    print(f"Soundtrack Acts: {len(soundtrack_acts)}")

if __name__ == "__main__":
    asyncio.run(generate_full_documentary_config(max_scenes=40))
