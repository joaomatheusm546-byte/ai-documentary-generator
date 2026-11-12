import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import FFPROBE_BIN

AUDIO_DIR = ROOT_DIR / "assets" / "pilot_voices"
SRC_DIR = ROOT_DIR / "remotion_app" / "src"
PUBLIC_AUDIO_DIR = ROOT_DIR / "remotion_app" / "public" / "audio"
PUBLIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

beats_meta = [
    {
        "id": "s1_b1",
        "narration": "In the remote Waldviertel region, peasant roots run deep.",
        "layoutType": "landscape",
        "bgImage": "images/scene_001_beat_01.jpg",
        "labelTitle": "Waldviertel Region",
        "labelSubtitle": "Lower Austria // 19th Century",
        "citation": "[1, 2] Sources in Description",
        "hasBoom": False,
    },
    {
        "id": "s1_b2",
        "narration": "Parish records document a birth shrouded in immediate secrecy.",
        "layoutType": "document",
        "bgImage": "images/scene_001_beat_02.jpg",
        "subjectImage": "images/scene_001_beat_04.jpg",
        "labelTitle": "Parish Baptismal Register",
        "labelSubtitle": "Döllersheim Registry // Folio 42",
        "highlightText": "CONFIDENTIAL BIRTH ENTRY",
        "citation": "[1, 2] Sources in Description",
        "hasBoom": False,
    },
    {
        "id": "s1_b3",
        "narration": "An unmarried peasant woman stands at the center of inquiry.",
        "layoutType": "portrait",
        "bgImage": "images/scene_001_beat_01.jpg",
        "subjectImage": "cutouts/maria_schicklgruber_cutout.png",
        "labelTitle": "Maria Anna Schicklgruber",
        "labelSubtitle": "the unmarried mother",
        "citation": "[1, 2] Sources in Description",
        "hasBoom": True,
    },
    {
        "id": "s1_b4",
        "narration": "This solitary entry initiates a decades-long biological mystery.",
        "layoutType": "document",
        "bgImage": "images/scene_001_beat_02.jpg",
        "subjectImage": "images/scene_001_beat_04.jpg",
        "labelTitle": "The Baptismal Entry",
        "labelSubtitle": "father left unrecorded",
        "highlightText": "FATHER UNRECORDED",
        "citation": "[1, 2] Sources in Description",
        "hasBoom": True,
    },
    {
        "id": "s2_b1",
        "narration": "Alois was born out of wedlock to forty-two-year-old Maria Schicklgruber.",
        "layoutType": "landscape",
        "bgImage": "images/scene_002_beat_01.jpg",
        "labelTitle": "Village of Stronnes",
        "labelSubtitle": "birthplace of Alois // 1837",
        "citation": "[2, 3] Sources in Description",
        "hasBoom": False,
    },
    {
        "id": "s2_b2",
        "narration": "The local priest inscribed the word 'illegitimate' in the parish register.",
        "layoutType": "document",
        "bgImage": "images/scene_002_beat_01.jpg",
        "subjectImage": "images/scene_002_beat_02.jpg",
        "labelTitle": "Canonical Register",
        "labelSubtitle": "inscribed as 'unehelich'",
        "highlightText": "UNEHELICH // ILLEGITIMATE",
        "citation": "[2, 3] Sources in Description",
        "hasBoom": True,
    },
    {
        "id": "s2_b3",
        "narration": "The father's name was left completely blank on the baptismal certificate.",
        "layoutType": "document",
        "bgImage": "images/scene_002_beat_01.jpg",
        "subjectImage": "images/scene_002_beat_03.jpg",
        "labelTitle": "Paternity Section",
        "labelSubtitle": "space left completely blank",
        "highlightText": "PATERNITY: UNVERIFIED",
        "citation": "[2, 3] Sources in Description",
        "hasBoom": True,
    },
    {
        "id": "s2_b4",
        "narration": "For nearly forty years, the boy bore his mother's surname alone.",
        "layoutType": "portrait",
        "bgImage": "images/scene_001_beat_01.jpg",
        "subjectImage": "cutouts/alois_hitler_cutout.png",
        "labelTitle": "Alois Schicklgruber",
        "labelSubtitle": "the illegitimate son",
        "citation": "[2, 3] Sources in Description",
        "hasBoom": True,
    },
    {
        "id": "s3_b1",
        "narration": "Years later, itinerant miller Johann Georg Hiedler married Maria.",
        "layoutType": "portrait",
        "bgImage": "images/scene_002_beat_01.jpg",
        "subjectImage": "cutouts/johann_georg_hiedler_cutout.png",
        "labelTitle": "Johann Georg Hiedler",
        "labelSubtitle": "the itinerant miller",
        "citation": "[3, 4] Sources in Description",
        "hasBoom": True,
    },
    {
        "id": "s3_b2",
        "narration": "He never legally legitimized young Alois during his lifetime.",
        "layoutType": "document",
        "bgImage": "images/scene_002_beat_01.jpg",
        "subjectImage": "images/scene_003_beat_02.jpg",
        "labelTitle": "Marriage Record 1842",
        "labelSubtitle": "no legitimation recorded",
        "highlightText": "NO LEGITIMATION RECORDED",
        "citation": "[3, 4] Sources in Description",
        "hasBoom": False,
    },
    {
        "id": "s3_b3",
        "narration": "Decades passed before formal claims of paternity emerged publicly.",
        "layoutType": "landscape",
        "bgImage": "images/scene_003_beat_03.jpg",
        "labelTitle": "Lower Austria Countryside",
        "labelSubtitle": "the mystery persists // 1842 - 1876",
        "citation": "[3, 4] Sources in Description",
        "hasBoom": False,
    },
    {
        "id": "s3_b4",
        "narration": "Historians remain divided on Hiedler's actual biological contribution.",
        "layoutType": "document",
        "bgImage": "images/scene_001_beat_01.jpg",
        "subjectImage": "images/scene_003_beat_04.jpg",
        "labelTitle": "Historical Verdict",
        "labelSubtitle": "biological paternity unproven",
        "highlightText": "BIOLOGICAL PATERNITY DISPUTED",
        "citation": "[3, 4] Sources in Description",
        "hasBoom": True,
    },
]

def get_duration(p: Path) -> float:
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(p)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())

def main():
    final_beats = []
    total_frames = 0
    print("=== Building Pilot Config with ElevenLabs George Voice ===")
    
    for i, b in enumerate(beats_meta, 1):
        filename = f"voice_beat_{i:02d}.mp3"
        src_audio = AUDIO_DIR / filename
        dest_audio = PUBLIC_AUDIO_DIR / filename
        
        if not src_audio.exists():
            raise FileNotFoundError(f"Missing audio: {src_audio}")
            
        shutil.copy(src_audio, dest_audio)
        dur = get_duration(src_audio)
        padded_dur = dur + 0.4
        frames = int(round(padded_dur * 30))
        total_frames += frames
        
        final_beats.append({
            "id": b["id"],
            "durationInFrames": frames,
            "layoutType": b["layoutType"],
            "bgImage": b["bgImage"],
            "subjectImage": b.get("subjectImage"),
            "labelTitle": b.get("labelTitle"),
            "labelSubtitle": b.get("labelSubtitle"),
            "highlightText": b.get("highlightText"),
            "hasBoom": b.get("hasBoom", False),
            "citation": b.get("citation"),
            "audioSrc": f"audio/{filename}",
        })
        print(f"Beat {i:02d}: {b['id']} -> {dur:.2f}s (+0.4s) = {frames} frames ({frames/30:.2f}s)")
        
    config = {
        "title": "The Hitler Bloodline: From the Secret Origins to the Extinction of the Lineage (Remotion Pilot V3 - ElevenLabs George)",
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "musicSrc": "audio/music.mp3",
        "beats": final_beats,
    }
    
    out_config = SRC_DIR / "pilot_config.json"
    out_config.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"\nWrote calibrated configuration: {out_config}")
    print(f"Total Beats: {len(final_beats)}")
    print(f"Total Frames: {total_frames} ({total_frames/30:.2f}s = {total_frames/1800:.2f} min)")

if __name__ == "__main__":
    main()
