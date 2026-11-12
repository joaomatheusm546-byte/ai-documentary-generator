import os
import json
import shutil
import asyncio
import subprocess
from pathlib import Path
from PIL import Image

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
        print(f"Warning: could not probe duration for {audio_path}: {e}, defaulting to 4.5s")
        return 4.5

async def synthesize_voice(text: str, output_path: Path, voice: str = "en-US-ChristopherNeural", rate: str = "-7%"):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"  Voice file exists: {output_path.name}")
        return
    print(f"  Synthesizing voice: '{text[:50]}...' -> {output_path.name}")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))

def create_cutout(src_image: Path, out_png: Path):
    out_png.parent.mkdir(parents=True, exist_ok=True)
    if out_png.exists() and out_png.stat().st_size > 1000:
        print(f"  Cutout exists: {out_png.name}")
        return
    print(f"  Generating transparent cutout for: {src_image.name} -> {out_png.name}")
    if remove is not None:
        inp = Image.open(src_image).convert("RGB")
        out = remove(inp)
        out.save(out_png, "PNG")
        print(f"  Successfully extracted cutout ({out_png.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"  Warning: rembg not installed, copying raw image as fallback")
        shutil.copy(src_image, out_png)

async def main():
    print("=== Step 1: Directory Setup ===")
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CUTOUTS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SRC_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy Music & SFX
    print("\n=== Step 1.1: Copying Soundtrack and Foley SFX ===")
    music_src = MUSIC_DIR / "dark_ambient_cello.mp3"
    if music_src.exists():
        shutil.copy(music_src, AUDIO_DIR / "music.mp3")
        print(f"  + Music: music.mp3")

    sfx_files = {
        "paper_slide.wav": "sfx_paper_slide.wav",
        "typewriter_stamp.wav": "sfx_typewriter_stamp.wav",
        "sub_boom.wav": "sfx_sub_boom.wav",
        "camera_shutter.wav": "sfx_camera_shutter.wav",
    }
    for orig, dest_name in sfx_files.items():
        src = SFX_DIR / orig
        if src.exists():
            shutil.copy(src, AUDIO_DIR / dest_name)
            print(f"  + Foley: {dest_name}")
        else:
            print(f"  ! Warning: SFX {orig} not found")

    # 2. Cutouts for Key Historical Subjects
    print("\n=== Step 2: Processing 2.5D Cutouts ===")
    portraits_map = {
        "maria_schicklgruber": ARCHIVE_DIR / "scene_001_beat_03.jpg",
        "alois_hitler": ARCHIVE_DIR / "scene_002_beat_04.jpg",
        "johann_georg_hiedler": ARCHIVE_DIR / "scene_003_beat_01.jpg",
    }
    for key, p_src in portraits_map.items():
        if p_src.exists():
            create_cutout(p_src, CUTOUTS_DIR / f"{key}_cutout.png")

    # 3. Copy Archival Images
    print("\n=== Step 3: Staging Archival Backgrounds & Documents ===")
    archival_files = [
        "scene_001_beat_01.jpg",
        "scene_001_beat_02.jpg",
        "scene_001_beat_03.jpg",
        "scene_001_beat_04.jpg",
        "scene_002_beat_01.jpg",
        "scene_002_beat_02.jpg",
        "scene_002_beat_03.jpg",
        "scene_002_beat_04.jpg",
        "scene_003_beat_01.jpg",
        "scene_003_beat_02.jpg",
        "scene_003_beat_03.jpg",
        "scene_003_beat_04.jpg",
    ]
    for af in archival_files:
        src = ARCHIVE_DIR / af
        if src.exists():
            shutil.copy(src, IMAGES_DIR / af)
            print(f"  Staged {af}")

    # 4. Beat Definitions (12 Beats with After the Crown Authentic Styling)
    beats_meta = [
        # Scene 1: Döllersheim Parish (June 1837)
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

        # Scene 2: The Question of Paternity (Lower Austria, 1837)
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

        # Scene 3: Johann Georg Hiedler (Spital, Austria, 1842)
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

    print("\n=== Step 4: Synthesizing Narration & Computing Timeline ===")
    final_beats = []
    total_frames = 0

    for i, b in enumerate(beats_meta, 1):
        voice_filename = f"voice_beat_{i:02d}.mp3"
        voice_out = AUDIO_DIR / voice_filename
        
        await synthesize_voice(b["narration"], voice_out)
        duration = get_audio_duration(voice_out)
        padded_duration = duration + 0.4
        frames = int(round(padded_duration * 30))
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
            "audioSrc": f"audio/{voice_filename}",
        })
        print(f"  Beat {i:02d}: {b['id']} -> {duration:.2f}s (+0.4s pad) = {frames} frames ({frames/30:.2f}s)")

    config = {
        "title": "The Hitler Bloodline: From the Secret Origins to the Extinction of the Lineage (Remotion Pilot V2)",
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "musicSrc": "audio/music.mp3",
        "beats": final_beats,
    }

    config_path = SRC_DIR / "pilot_config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"\nGenerated Remotion configuration: {config_path}")
    print(f"Total Beats: {len(final_beats)}")
    print(f"Total Frames: {total_frames} ({total_frames / 30:.2f}s = {total_frames / (30 * 60):.2f} min)")

if __name__ == "__main__":
    asyncio.run(main())
