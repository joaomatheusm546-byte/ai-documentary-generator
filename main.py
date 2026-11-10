import argparse
import json
import logging
import sys
import time
from pathlib import Path
from src.config import OUTPUT_DIR, TEMP_DIR, MUSIC_DIR, DEFAULT_VOICE
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

def build_documentary(topic: str, num_scenes: int = 5, voice: str = DEFAULT_VOICE, custom_title: str = None) -> Path:
    start_time = time.time()
    logger.info("=" * 60)
    logger.info(f"STARTING DOCUMENTARY PRODUCTION: '{topic}'")
    logger.info(f"Scenes requested: {num_scenes} | Voice: {voice}")
    logger.info("=" * 60)

    # 1. Script Generation
    logger.info("\n--- STEP 1: Researching & Scriptwriting ---")
    script = generate_documentary_script(topic=topic, num_scenes=num_scenes)
    title = custom_title or script.get("title", "Documentary")
    safe_slug = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip().replace(" ", "_")
    
    doc_output_dir = OUTPUT_DIR / safe_slug
    doc_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save script JSON
    script_path = doc_output_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)
    logger.info(f"Script saved to {script_path}")

    scenes = script.get("scenes", [])
    if not scenes:
        raise ValueError("Script contains no scenes!")

    scene_videos = []
    
    # 2. Process each scene
    logger.info("\n--- STEP 2: Synthesizing Voice & Acquiring Archival Media ---")
    for idx, sc in enumerate(scenes, start=1):
        scene_id = sc.get("scene_id", idx)
        narration = sc.get("narration", "")
        queries = sc.get("search_queries", [])
        motion = sc.get("ken_burns_motion", "zoom_in")
        
        logger.info(f"\n[Scene {scene_id}/{len(scenes)}]")
        logger.info(f"Narration: \"{narration}\"")
        
        # A. Voice Synthesis
        voice_audio_path = TEMP_DIR / f"scene_{scene_id:03d}_voice.mp3"
        audio_meta = synthesize_scene_audio(narration, voice_audio_path, voice=voice)
        duration = audio_meta["duration"]
        logger.info(f"Voice synthesized: {duration:.2f}s ({audio_meta['word_count']} words)")
        
        # B. Media Retrieval
        image_path = fetch_media_for_scene(scene_id, queries, topic_fallback=topic)
        logger.info(f"Media secured: {image_path.name}")
        
        # C. Scene Video Rendering
        scene_video_path = TEMP_DIR / f"scene_{scene_id:03d}_video.mp4"
        success = create_scene_video(
            image_path=image_path,
            audio_path=voice_audio_path,
            duration=duration,
            output_path=scene_video_path,
            motion=motion
        )
        if success:
            scene_videos.append(scene_video_path)
        else:
            logger.error(f"Failed to render scene {scene_id}")

    if not scene_videos:
        raise RuntimeError("No scenes were rendered successfully.")

    # 3. Concatenation & Audio Mastering
    logger.info("\n--- STEP 3: Timeline Assembly & Mastering ---")
    final_video_path = doc_output_dir / f"{safe_slug}.mp4"
    
    # Look for ambient music if available
    bg_music = None
    music_files = list(MUSIC_DIR.glob("*.mp3")) + list(MUSIC_DIR.glob("*.wav"))
    if music_files:
        bg_music = music_files[0]
        logger.info(f"Found background music track: {bg_music.name}")

    concatenate_scenes(scene_videos, final_video_path, background_music=bg_music)
    
    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info(f"DOCUMENTARY PRODUCTION COMPLETE!")
    logger.info(f"Output Video: {final_video_path}")
    logger.info(f"Total production time: {elapsed:.1f}s")
    logger.info("=" * 60)
    
    return final_video_path

def main():
    parser = argparse.ArgumentParser(description="Automated AI Documentary Production Engine")
    parser.add_argument("--topic", type=str, required=True, help="Topic of the documentary")
    parser.add_argument("--scenes", type=int, default=3, help="Number of scenes to generate")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Edge-TTS voice identifier")
    parser.add_argument("--title", type=str, default=None, help="Custom title override")
    
    args = parser.parse_args()
    try:
        build_documentary(
            topic=args.topic,
            num_scenes=args.scenes,
            voice=args.voice,
            custom_title=args.title
        )
    except Exception as e:
        logger.exception(f"Fatal error during production: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
