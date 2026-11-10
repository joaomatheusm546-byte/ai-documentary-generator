import argparse
import json
import logging
import sys
import time
from pathlib import Path
from src.config import OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, DEFAULT_VOICE
from src.scriptwriter import generate_documentary_script
from src.voice import synthesize_scene_audio
from src.media_fetcher import fetch_media_for_scene
from src.video_engine import create_scene_video, concatenate_scenes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DocumentaryEngine")

MUSIC_PATH = ASSETS_DIR / "music" / "dark_ambient_cello.mp3"

def build_documentary(
    topic: str,
    num_scenes: int = 8,
    voice: str = DEFAULT_VOICE,
    custom_title: str = None,
    preloaded_script: dict = None
) -> Path:
    start_time = time.time()
    logger.info("=" * 60)
    logger.info(f"STARTING 'AFTER THE CROWN' CLOUD PRODUCTION: '{topic}'")
    logger.info(f"Scenes: {num_scenes} | Voice: {voice}")
    logger.info("=" * 60)

    # 1. Scriptwriting
    logger.info("\n--- STEP 1: Research & Scriptwriting ---")
    if preloaded_script:
        logger.info("Using preloaded documentary script...")
        script = preloaded_script
    else:
        script = generate_documentary_script(topic=topic, num_scenes=num_scenes)

    title = custom_title or script.get("title", "Documentary")
    safe_slug = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip().replace(" ", "_")
    
    doc_output_dir = OUTPUT_DIR / safe_slug
    doc_output_dir.mkdir(parents=True, exist_ok=True)
    
    script_path = doc_output_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)
    logger.info(f"Script saved to {script_path}")

    scenes = script.get("scenes", [])
    if not scenes:
        raise ValueError("Script contains no scenes!")

    scene_videos = []
    
    # 2. Process Scenes
    logger.info("\n--- STEP 2: Archival Media Retrieval & Scene Rendering ---")
    for idx, sc in enumerate(scenes, start=1):
        scene_id = sc.get("scene_id", idx)
        narration = sc.get("narration", "")
        queries = sc.get("search_queries", [])
        motion = sc.get("ken_burns_motion", "slow_zoom_in")
        
        logger.info(f"\n[Scene {scene_id}/{len(scenes)}]")
        logger.info(f"Narration: \"{narration}\"")
        
        # A. Voice Synthesis
        voice_audio_path = TEMP_DIR / f"scene_{scene_id:03d}_voice.mp3"
        audio_meta = synthesize_scene_audio(narration, voice_audio_path, voice=voice)
        duration = audio_meta["duration"]
        sc["duration"] = duration
        logger.info(f"Voice synthesized: {duration:.2f}s")
        
        # B. Media Retrieval
        custom_asset = sc.get("image_path") or sc.get("asset_path")
        image_path = fetch_media_for_scene(scene_id, queries, topic_fallback=topic, custom_asset=custom_asset)
        logger.info(f"Archival media secured: {image_path.name}")
        
        # C. Render Scene with After the Crown Typography & Enquadramento
        scene_video_path = TEMP_DIR / f"scene_{scene_id:03d}_video.mp4"
        success = create_scene_video(
            image_path=image_path,
            audio_path=voice_audio_path,
            duration=duration,
            output_path=scene_video_path,
            motion=motion,
            label_title=sc.get("label_title"),
            label_sub=sc.get("label_sub"),
            citation=sc.get("citation", f"[{scene_id}]"),
            callout_red=sc.get("callout_red"),
            callout_box=sc.get("callout_box")
        )
        if success:
            scene_videos.append(scene_video_path)
        else:
            logger.error(f"Failed to render scene {scene_id}")

    if not scene_videos:
        raise RuntimeError("No scenes were rendered successfully.")

    # 3. Concatenate and Mix Soundtrack
    logger.info("\n--- STEP 3: Timeline Assembly & Soundtrack Mixing ---")
    final_video_path = doc_output_dir / f"{safe_slug}.mp4"
    concatenate_scenes(
        scene_videos=scene_videos,
        output_path=final_video_path,
        background_music=MUSIC_PATH,
        script_scenes=scenes
    )
    
    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"DOCUMENTARY PRODUCTION COMPLETED SUCCESSFULLY IN {elapsed:.1f}s!")
    logger.info(f"Master Video: {final_video_path} ({final_video_path.stat().st_size / (1024*1024):.2f} MB)")
    logger.info("=" * 60)
    
    return final_video_path

def main():
    parser = argparse.ArgumentParser(description="After the Crown AI Documentary Production Engine")
    parser.add_argument("--topic", type=str, required=True, help="Topic of the documentary")
    parser.add_argument("--scenes", type=int, default=8, help="Number of scenes to generate")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Edge-TTS voice identifier")
    parser.add_argument("--title", type=str, default=None, help="Custom title override")
    parser.add_argument("--script-json", type=str, default=None, help="Preloaded JSON script string")
    parser.add_argument("--script-file", type=str, default=None, help="Path to preloaded script JSON file")
    
    args = parser.parse_args()
    
    preloaded = None
    script_str = args.script_json or os.environ.get("SCRIPT_JSON_INPUT")
    script_file = args.script_file or os.environ.get("SCRIPT_FILE")

    if script_file and Path(script_file).exists():
        try:
            with open(script_file, "r", encoding="utf-8") as f:
                preloaded = json.load(f)
            logger.info(f"Loaded script from file: {script_file}")
        except Exception as e:
            logger.warning(f"Failed to read script file {script_file}: {e}")
    elif script_str:
        try:
            preloaded = json.loads(script_str)
            logger.info("Loaded script from script string input.")
        except Exception as e:
            logger.warning(f"Failed to parse script string: {e}")

    try:
        build_documentary(
            topic=args.topic,
            num_scenes=args.scenes,
            voice=args.voice,
            custom_title=args.title,
            preloaded_script=preloaded
        )
    except Exception as e:
        logger.exception(f"Fatal error during production: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
