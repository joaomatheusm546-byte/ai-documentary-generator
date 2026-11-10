import os
import re
import logging
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image
from src.config import PEXELS_API_KEY, TEMP_DIR

logger = logging.getLogger("MediaFetcher")

HEADERS = {
    "User-Agent": "HistoricalDocumentaryResearchBot/1.1 (https://github.com/joaomatheusm546-byte/ai-documentary-generator; contact@ai-documentaries.org)"
}

def clean_query(query: str) -> str:
    return re.sub(r'["\':;,]', '', query).strip()

def search_wikimedia_commons(query: str, min_width: int = 1000) -> Optional[Dict[str, Any]]:
    """Searches Wikimedia Commons for high-resolution historical images."""
    clean_q = clean_query(query)
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": clean_q,
        "gsrnamespace": 6,
        "gsrlimit": 10,
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
            
            if mime in ["image/jpeg", "image/png", "image/webp"] and width >= min_width:
                aspect = width / max(1, height)
                if 0.5 <= aspect <= 2.5:
                    clean_filename = title.replace("File:", "").replace(" ", "_")
                    file_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{clean_filename}?width=1920"
                    candidates.append({
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

def download_file(url: str, dest_path: Path) -> bool:
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

def fetch_media_for_scene(scene_id: int, search_queries: List[str], topic_fallback: str = "") -> Path:
    target_file = TEMP_DIR / f"scene_{scene_id:03d}_visual.jpg"
    
    # 1. Exact queries
    for q in search_queries:
        logger.info(f"[Scene {scene_id}] Searching Wikimedia for: '{q}'...")
        media = search_wikimedia_commons(q)
        if media and download_file(media["url"], target_file):
            logger.info(f"[Scene {scene_id}] Found archival media: {media.get('title')}")
            return target_file

    # 2. Relaxed queries
    for q in search_queries:
        simplified = re.sub(r'\b(vintage|antique|engraving|illustration|painting|photo|drawing|archives|diagram)\b', '', q, flags=re.IGNORECASE).strip()
        if simplified and simplified != q:
            media = search_wikimedia_commons(simplified, min_width=800)
            if media and download_file(media["url"], target_file):
                logger.info(f"[Scene {scene_id}] Found via relaxed query: {simplified}")
                return target_file

    # 3. Topic fallback
    if topic_fallback:
        media = search_wikimedia_commons(topic_fallback, min_width=800)
        if media and download_file(media["url"], target_file):
            logger.info(f"[Scene {scene_id}] Found via topic fallback: {topic_fallback}")
            return target_file

    # 4. If all else fails, use another existing valid image from temp
    existing = list(TEMP_DIR.glob("scene_*_visual.jpg"))
    for ext_img in existing:
        if ext_img.exists() and ext_img.stat().st_size > 15000 and ext_img != target_file:
            import shutil
            shutil.copy(ext_img, target_file)
            logger.info(f"[Scene {scene_id}] Reusing archival asset from scene pool: {ext_img.name}")
            return target_file

    # 5. Last resort: high quality architectural/historical Wikimedia lead
    media = search_wikimedia_commons("Historical archive document museum", min_width=800)
    if media and download_file(media["url"], target_file):
        return target_file

    return target_file
