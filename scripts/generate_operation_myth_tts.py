import sys
import time
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / ".env")

from src.elevenlabs_client import synthesize_with_elevenlabs

MASTER_SCRIPT_PATH = ROOT_DIR / "assets" / "operation_myth_master_script.json"
AUDIO_DIR = ROOT_DIR / "assets" / "operation_myth_audio"
REMOTION_AUDIO_DIR = ROOT_DIR / "remotion_app" / "public" / "audio"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
REMOTION_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not MASTER_SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Missing master script: {MASTER_SCRIPT_PATH}")

    data = json.loads(MASTER_SCRIPT_PATH.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    assert len(scenes) == 45, f"Expected 45 scenes, got {len(scenes)}"

    print("=== Synthesizing Operation Myth Narration (45 Scenes / 180 Beats) ===")
    print("Voice: George (JBFqnCBsd6RMkjVDRZzb) | Model: eleven_turbo_v2_5")

    total_characters = 0
    total_billed_credits = 0
    total_cached = 0
    total_generated = 0
    start_time = time.time()

    for scene in scenes:
        s_num = scene["scene"]
        beats = scene.get("beats", [])
        print(f"\n--- Scene {s_num:02d}/45 (Act {scene['act']}): {scene.get('title', 'Scene')} ({len(beats)} beats) ---")

        for b_idx, beat in enumerate(beats, 1):
            text = beat.get("narration", "").strip()
            if not text:
                raise ValueError(f"Empty narration at S{s_num:02d}B{b_idx}")

            filename = f"myth_s{s_num:03d}_b{b_idx:02d}.mp3"
            dest_path = AUDIO_DIR / filename
            remotion_path = REMOTION_AUDIO_DIR / filename

            # Skip API/cache lookup if already staged in operation_myth_audio
            if dest_path.exists() and dest_path.stat().st_size > 2000:
                if not remotion_path.exists() or remotion_path.stat().st_size != dest_path.stat().st_size:
                    shutil.copy2(dest_path, remotion_path)
                total_cached += 1
                total_characters += len(text)
                print(f"  [LOCAL] {filename} | {len(text)}c")
                continue

            res = synthesize_with_elevenlabs(
                text=text,
                output_path=dest_path,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_turbo_v2_5",
            )
            shutil.copy2(dest_path, remotion_path)

            billed = res.get("character_cost", 0)
            dur = res.get("duration", 0)
            chars = res.get("characters", len(text))
            cached = res.get("cached", False)

            total_characters += chars
            total_billed_credits += billed

            if cached:
                total_cached += 1
                status = "CACHE"
            else:
                total_generated += 1
                status = "BILLED"
                time.sleep(0.15)

            print(f"  [{status}] {filename} | {dur:.2f}s | {chars}c | {billed} cred | '{text[:40]}...'")

    elapsed = time.time() - start_time
    print("\n" + "=" * 56)
    print(f"OPERATION MYTH NARRATION COMPLETE in {elapsed:.1f}s")
    print(f"Total Beats Processed: {total_cached + total_generated} / 180")
    print(f"Cached/Local (0 Credits): {total_cached}")
    print(f"Freshly Generated: {total_generated}")
    print(f"Total Characters: {total_characters}")
    print(f"Total Credits Billed: {total_billed_credits}")
    print("=" * 56)


if __name__ == "__main__":
    main()
