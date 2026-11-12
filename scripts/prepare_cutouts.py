import os
import shutil
from pathlib import Path
from PIL import Image

try:
    from rembg import remove
except ImportError:
    remove = None

ROOT_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = ROOT_DIR / "assets" / "hitler_family_archive"
CUTOUTS_DIR = ROOT_DIR / "remotion_app" / "public" / "cutouts"
CUTOUTS_DIR.mkdir(parents=True, exist_ok=True)

portraits_map = {
    "maria_schicklgruber_cutout.png": "scene_001_beat_03.jpg",
    "alois_hitler_cutout.png": "scene_002_beat_04.jpg",
    "johann_georg_hiedler_cutout.png": "scene_003_beat_01.jpg",
    "klara_polzl_cutout.png": "scene_006_beat_02.jpg",
    "adolf_hitler_cutout.png": "scene_008_beat_04.jpg",
    "geli_raubal_cutout.png": "scene_016_beat_01.jpg",
    "william_hitler_cutout.png": "scene_021_beat_02.jpg",
    "paula_hitler_cutout.png": "scene_031_beat_01.jpg",
}

def main():
    print(f"=== Generating 2.5D Cutouts for Documentary (rembg available: {remove is not None}) ===")
    for cutout_name, src_name in portraits_map.items():
        src_path = ARCHIVE_DIR / src_name
        dest_path = CUTOUTS_DIR / cutout_name
        
        if dest_path.exists() and dest_path.stat().st_size > 2000:
            print(f"  [EXISTS] {cutout_name}")
            continue
            
        if not src_path.exists():
            print(f"  [WARN] Source image not found: {src_name}")
            continue
            
        if remove is not None:
            try:
                print(f"  [REMBG] Extracting subject from {src_name} -> {cutout_name}...")
                inp = Image.open(src_path).convert("RGB")
                out = remove(inp)
                out.save(dest_path, "PNG")
                print(f"  [SUCCESS] Created {cutout_name} ({dest_path.stat().st_size / 1024:.1f} KB)")
            except Exception as e:
                print(f"  [ERROR] rembg failed for {src_name}: {e}. Copying raw image as fallback.")
                shutil.copy(src_path, dest_path)
        else:
            print(f"  [FALLBACK] rembg not available, copying {src_name} as fallback cutout")
            shutil.copy(src_path, dest_path)

if __name__ == "__main__":
    main()
