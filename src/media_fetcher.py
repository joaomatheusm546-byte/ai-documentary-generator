import os
import re
import time
import logging
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from PIL import Image, ImageOps, ImageFilter
from src.config import PEXELS_API_KEY, PIXABAY_API_KEY, EUROPEANA_API_KEY, TEMP_DIR, ASSETS_DIR

logger = logging.getLogger("MediaFetcher")

HEADERS = {
    "User-Agent": "HistoricalDocumentaryResearchBot/1.2 (https://github.com/joaomatheusm546-byte/ai-documentary-generator; contact@ai-documentaries.org)"
}

# Registry to guarantee ZERO repeated images across the documentary
USED_MEDIA_IDENTIFIERS: Set[str] = set()

def clean_query(query: str) -> str:
    """Strips punctuation and noise words for cleaner search."""
    cleaned = re.sub(r'["\':;,]', '', query).strip()
    return cleaned

def search_wikimedia_commons(query: str, min_width: int = 300, exclude_ids: Optional[Set[str]] = None) -> Optional[Dict[str, Any]]:
    """Searches Wikimedia Commons for high-resolution historical images."""
    clean_q = clean_query(query)
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": clean_q,
        "gsrnamespace": 6,
        "gsrlimit": 12,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "format": "json"
    }
    
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            return None
            
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        
        candidates = []
        for pid, page in pages.items():
            infos = page.get("imageinfo", [])
            if not infos:
                continue
            info = infos[0]
            mime = info.get("mime", "")
            width = info.get("width", 0)
            height = info.get("height", 0)
            title = page.get("title", "")
            
            clean_filename = title.replace("File:", "").replace(" ", "_")
            if exclude_ids and clean_filename in exclude_ids:
                continue
                
            if mime in ["image/jpeg", "image/png", "image/webp"] and width >= min_width:
                aspect = width / max(1, height)
                if 0.5 <= aspect <= 2.5:
                    file_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{clean_filename}?width=1920"
                    candidates.append({
                        "id": clean_filename,
                        "url": file_url,
                        "width": width,
                        "height": height,
                        "title": title,
                        "score": width * height
                    })

        if candidates:
            candidates.sort(key=lambda x: x["score"], reverse=True)
            return candidates[0]
            
    except Exception as e:
        logger.warning(f"Wikimedia search failed for '{query}': {e}")
        
    return None

def search_wikipedia_images(topic: str, exclude_ids: Optional[Set[str]] = None) -> Optional[Dict[str, Any]]:
    """Fetches verified encyclopedic images from Wikipedia articles related to topic."""
    clean_t = clean_query(topic)
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": clean_t,
        "gsrlimit": 3,
        "prop": "pageimages",
        "piprop": "original",
        "format": "json"
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=12)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for pid, p in pages.items():
                orig = p.get("original", {})
                img_url = orig.get("source")
                if img_url and img_url.lower().endswith(('.jpg', '.jpeg', '.png')):
                    clean_id = Path(img_url).name
                    if exclude_ids and clean_id in exclude_ids:
                        continue
                    return {
                        "id": clean_id,
                        "url": img_url,
                        "width": orig.get("width", 1200),
                        "height": orig.get("height", 800),
                        "title": p.get("title", topic)
                    }
    except Exception as e:
        logger.warning(f"Wikipedia search failed for '{topic}': {e}")
    return None

def search_europeana(query: str, exclude_ids: Optional[Set[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Searches Europeana (European cultural heritage, museums, declassified national archives).
    """
    if not EUROPEANA_API_KEY:
        return None
    clean_q = clean_query(query)
    url = "https://api.europeana.eu/record/v2/search.json"
    params = {
        "wskey": EUROPEANA_API_KEY,
        "query": clean_q,
        "rows": 8,
        "qf": "TYPE:IMAGE"
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=12)
        if r.status_code == 200:
            items = r.json().get("items", [])
            for it in items:
                guid = it.get("guid") or (it.get("id") and it.get("id")[0])
                if exclude_ids and guid in exclude_ids:
                    continue
                img_url = None
                if it.get("edmPreview"):
                    img_url = it["edmPreview"][0]
                elif it.get("edmIsShownBy"):
                    img_url = it["edmIsShownBy"][0]
                if img_url:
                    return {
                        "id": guid or img_url,
                        "url": img_url,
                        "title": it.get("title", [clean_q])[0]
                    }
    except Exception as e:
        logger.warning(f"Europeana search error for '{query}': {e}")
    return None

def search_pixabay(query: str, exclude_ids: Optional[Set[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Searches Pixabay for high-res authentic atmospheric photographs.
    """
    if not PIXABAY_API_KEY:
        return None
    clean_q = clean_query(query)
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": clean_q,
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": 6,
        "safesearch": "true"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            hits = r.json().get("hits", [])
            for h in hits:
                h_id = f"pixabay_{h.get('id')}"
                if exclude_ids and h_id in exclude_ids:
                    continue
                img_url = h.get("largeImageURL") or h.get("webformatURL")
                if img_url:
                    return {
                        "id": h_id,
                        "url": img_url,
                        "title": h.get("tags", clean_q)
                    }
    except Exception as e:
        logger.warning(f"Pixabay search error for '{query}': {e}")
    return None

def search_pexels(query: str, exclude_ids: Optional[Set[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Searches Pexels for high-res atmospheric cinematic landscape / location photographs.
    """
    if not PEXELS_API_KEY:
        return None
    clean_q = clean_query(query)
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": clean_q,
        "per_page": 6,
        "orientation": "landscape"
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for p in photos:
                p_id = f"pexels_{p.get('id')}"
                if exclude_ids and p_id in exclude_ids:
                    continue
                src = p.get("src", {})
                img_url = src.get("large2x") or src.get("large") or src.get("original")
                if img_url:
                    return {
                        "id": p_id,
                        "url": img_url,
                        "title": p.get("alt", clean_q)
                    }
    except Exception as e:
        logger.warning(f"Pexels search error for '{query}': {e}")
    return None

def generate_flux_historical_fallback(prompt: str, dest_path: Path) -> bool:
    """
    Generates an authentic historical archive photograph using Flux
    strictly calibrated for 1930s-1940s 35mm film grain and museum look.
    Never produces anime, CGI or digital faces.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    clean_p = clean_query(prompt)
    historical_prompt = (
        f"Authentic historical black and white archive photograph 1945, "
        f"vintage 35mm Leica film grain, raw documentary photography, "
        f"museum archival record, monochrome gelatin silver print, {clean_p}, "
        f"authentic period attire, natural documentary lighting, no digital smoothing, "
        f"no CGI, no 3D render, no watermark"
    )
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(historical_prompt)}?width=1280&height=720&model=flux&nologo=true"
    logger.info(f"Generating archival fallback with Flux: '{clean_p}'...")
    
    for attempt in range(2):
        try:
            r = requests.get(url, timeout=35)
            if r.status_code == 200 and len(r.content) > 15000:
                with open(dest_path, "wb") as f:
                    f.write(r.content)
                # Verify and post-process to ensure pure archival tone
                with Image.open(dest_path) as img:
                    img = img.convert("L").convert("RGB") # Authentic monochrome
                    img = ImageOps.autocontrast(img, cutoff=1)
                    img.save(dest_path, "JPEG", quality=95)
                logger.info(f"Archival Flux generation secured: {dest_path.name}")
                return True
        except Exception as e:
            logger.warning(f"Flux attempt {attempt+1} failed: {e}")
            time.sleep(2)
            
    return False

def download_file(url: str, dest_path: Path) -> bool:
    """Downloads and verifies an image file."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=HEADERS, stream=True, timeout=25, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 10000:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            with Image.open(dest_path) as img:
                img.verify()
            return True
    except Exception as e:
        logger.warning(f"Download failed for {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()
    return False

def fetch_single_visual_beat(
    scene_id: int,
    beat_idx: int,
    query: str,
    topic_fallback: str = "",
    custom_file: Optional[Path] = None
) -> Path:
    """Fetches a unique archival image for a specific sub-beat in a scene."""
    target_file = TEMP_DIR / f"scene_{scene_id:03d}_beat_{beat_idx:02d}.jpg"
    target_file.parent.mkdir(parents=True, exist_ok=True)

    # 0. Pre-bundled asset check
    if custom_file and custom_file.exists() and custom_file.stat().st_size > 5000:
        import shutil
        shutil.copy(custom_file, target_file)
        USED_MEDIA_IDENTIFIERS.add(custom_file.name)
        logger.info(f"[Scene {scene_id} Beat {beat_idx}] Using bundled asset: {custom_file.name}")
        return target_file

    # 1. Direct URL or Wikimedia File: filename
    if query.startswith("http://") or query.startswith("https://"):
        if download_file(query, target_file):
            USED_MEDIA_IDENTIFIERS.add(query)
            return target_file

    if query.startswith("File:") or query.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        clean_fn = query.replace("File:", "").strip().replace(" ", "_")
        if clean_fn not in USED_MEDIA_IDENTIFIERS:
            direct_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{clean_fn}?width=1920"
            if download_file(direct_url, target_file):
                USED_MEDIA_IDENTIFIERS.add(clean_fn)
                logger.info(f"[Scene {scene_id} Beat {beat_idx}] Downloaded direct Wikimedia file: {clean_fn}")
                return target_file

    # 2. Europeana Cultural Heritage & National Archives Search
    media_euro = search_europeana(query, exclude_ids=USED_MEDIA_IDENTIFIERS)
    if media_euro and download_file(media_euro["url"], target_file):
        USED_MEDIA_IDENTIFIERS.add(media_euro["id"])
        logger.info(f"[Scene {scene_id} Beat {beat_idx}] Found Europeana museum archive: {media_euro.get('title')}")
        return target_file

    # 3. Wikimedia Commons Primary Search
    media = search_wikimedia_commons(query, exclude_ids=USED_MEDIA_IDENTIFIERS)
    if media and download_file(media["url"], target_file):
        USED_MEDIA_IDENTIFIERS.add(media["id"])
        logger.info(f"[Scene {scene_id} Beat {beat_idx}] Found Wikimedia archive: {media.get('title')}")
        return target_file

    # 4. Wikipedia Encyclopedic Media
    media_wiki = search_wikipedia_images(query, exclude_ids=USED_MEDIA_IDENTIFIERS)
    if media_wiki and download_file(media_wiki["url"], target_file):
        USED_MEDIA_IDENTIFIERS.add(media_wiki["id"])
        logger.info(f"[Scene {scene_id} Beat {beat_idx}] Found Wikipedia historical asset: {media_wiki.get('title')}")
        return target_file

    # 5. Relaxed query search (Europeana & Wikimedia)
    simplified = re.sub(r'\b(vintage|antique|engraving|illustration|painting|photo|drawing|archives|diagram)\b', '', query, flags=re.IGNORECASE).strip()
    if simplified and simplified != query:
        media_rel_euro = search_europeana(simplified, exclude_ids=USED_MEDIA_IDENTIFIERS)
        if media_rel_euro and download_file(media_rel_euro["url"], target_file):
            USED_MEDIA_IDENTIFIERS.add(media_rel_euro["id"])
            logger.info(f"[Scene {scene_id} Beat {beat_idx}] Found via relaxed Europeana query: {simplified}")
            return target_file

        media_rel = search_wikimedia_commons(simplified, min_width=300, exclude_ids=USED_MEDIA_IDENTIFIERS)
        if media_rel and download_file(media_rel["url"], target_file):
            USED_MEDIA_IDENTIFIERS.add(media_rel["id"])
            logger.info(f"[Scene {scene_id} Beat {beat_idx}] Found via relaxed query: {simplified}")
            return target_file

    # 6. Topic fallback search
    if topic_fallback:
        media_top = search_wikimedia_commons(f"{topic_fallback} historical archive", min_width=300, exclude_ids=USED_MEDIA_IDENTIFIERS)
        if media_top and download_file(media_top["url"], target_file):
            USED_MEDIA_IDENTIFIERS.add(media_top["id"])
            return target_file

    # 6. High-Fidelity Flux AI Archival Fallback (matches exact 1930s-1940s film look)
    logger.info(f"[Scene {scene_id} Beat {beat_idx}] No open archive found. Activating Flux 35mm archive generator...")
    if generate_flux_historical_fallback(query, target_file):
        USED_MEDIA_IDENTIFIERS.add(f"flux_{scene_id}_{beat_idx}")
        return target_file

    # 7. As absolute last resort, create an authentic historical dossier card placeholder - NEVER duplicate another scene's image
    logger.warning(f"[Scene {scene_id} Beat {beat_idx}] Fallback: generating archival record card to avoid repetition.")
    try:
        from PIL import ImageDraw
        card = Image.new("RGB", (1920, 1080), color=(18, 18, 18))
        draw = ImageDraw.Draw(card)
        draw.rectangle([(80, 80), (1840, 1000)], outline=(60, 60, 60), width=2)
        draw.text((120, 140), "NATIONAL ARCHIVES AND RECORDS ADMINISTRATION", fill=(140, 140, 140))
        draw.text((120, 180), f"HISTORICAL RECORD // DOSSIER {scene_id:03d}-{beat_idx:02d}", fill=(200, 50, 50))
        draw.text((120, 240), f"SUBJECT: {query.upper()[:80]}", fill=(210, 210, 210))
        card.save(target_file, "JPEG", quality=90)
        USED_MEDIA_IDENTIFIERS.add(f"record_card_{scene_id}_{beat_idx}")
        return target_file
    except Exception as e:
        logger.error(f"Failed to generate archival card: {e}")

    return target_file

    return target_file

def fetch_media_for_scene(
    scene_id: int,
    search_queries: List[str],
    topic_fallback: str = "",
    custom_asset: Optional[str] = None,
    target_beats: int = 4
) -> List[Path]:
    """
    Fetches multiple distinct archival images for a scene to ensure
    15-20 cuts per minute (corte a cada ~3.5 segundos).
    """
    logger.info(f"\n[Scene {scene_id}] Securing {target_beats} archival visual beats...")
    
    # Expand queries if fewer than target_beats
    queries = list(search_queries)
    if len(queries) < target_beats:
        # Generate complementary historical angles
        extras = [
            f"{topic_fallback} declassified records document",
            f"{topic_fallback} military headquarters 1945",
            f"{topic_fallback} archival location photograph",
            f"{topic_fallback} historical evidence portrait"
        ]
        for ex in extras:
            if len(queries) >= target_beats:
                break
            if ex not in queries:
                queries.append(ex)

    scene_images: List[Path] = []
    for beat_idx in range(1, target_beats + 1):
        q = queries[(beat_idx - 1) % len(queries)]
        
        # Priority 1: Dedicated beat asset in hitler_family_archive (e.g. scene_001_beat_02.jpg)
        beat_asset = ASSETS_DIR / "hitler_family_archive" / f"scene_{scene_id:03d}_beat_{beat_idx:02d}.jpg"
        c_file = None
        if beat_asset.exists() and beat_asset.stat().st_size > 3000:
            c_file = beat_asset
        elif beat_idx == 1 and custom_asset and Path(custom_asset).exists():
            c_file = Path(custom_asset)
        elif beat_idx == 1:
            scene_asset = ASSETS_DIR / "hitler_family_archive" / f"scene_{scene_id:03d}.jpg"
            if scene_asset.exists() and scene_asset.stat().st_size > 3000:
                c_file = scene_asset

        img_p = fetch_single_visual_beat(
            scene_id=scene_id,
            beat_idx=beat_idx,
            query=q,
            topic_fallback=topic_fallback,
            custom_file=c_file
        )
        if img_p.exists() and img_p.stat().st_size > 5000:
            scene_images.append(img_p)

    logger.info(f"[Scene {scene_id}] Completed: {len(scene_images)} distinct archival assets ready.")
    return scene_images
