import math
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from src.config import VIDEO_WIDTH, VIDEO_HEIGHT

logger = logging.getLogger("Styler")

def fit_to_16_9(img: Image.Image, target_size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT)) -> Image.Image:
    """
    Guarantees 100% full-bleed 16:9 widescreen frame (ZERO black bars, ZERO blurred pillarbox).
    Intelligently crops to keep faces/subjects centered in the upper/middle rule of thirds.
    """
    tw, th = target_size
    iw, ih = img.size
    aspect = iw / ih

    scale = max(tw / iw, th / ih)
    nw, nh = int(math.ceil(iw * scale)), int(math.ceil(ih * scale))
    res = img.resize((nw, nh), Image.Resampling.LANCZOS)
    
    left = (nw - tw) // 2
    # For vertical portraits (aspect < 1.0), anchor slightly higher (top 18-22%) so the head/face is perfectly framed
    if aspect < 1.0:
        top = int(max(0, min(nh - th, (nh - th) * 0.20)))
    else:
        top = (nh - th) // 2
        
    return res.crop((left, top, left + tw, top + th))

def apply_cinematic_vignette(img: Image.Image) -> Image.Image:
    """Adds a smooth dark radial vignette around the edges."""
    w, h = img.size
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    max_radius = math.hypot(w / 2, h / 2)
    for r in range(int(max_radius * 0.40), int(max_radius), 8):
        dist = max(0.0, (r - max_radius * 0.40) / (max_radius * 0.60))
        alpha = int((dist ** 1.9) * 200)
        vdraw.ellipse([w/2 - r, h/2 - r, w/2 + r, h/2 + r], outline=(0, 0, 0, min(240, alpha)), width=10)
    vignette = vignette.filter(ImageFilter.GaussianBlur(22))
    return Image.alpha_composite(img.convert("RGBA"), vignette).convert("RGB")

def prepare_cinematic_background(base_img: Image.Image) -> Image.Image:
    """
    Prepares the 100% full-bleed 16:9 background with unified
    After the Crown archival monochrome/sepia grading and film vignette.
    """
    frame = fit_to_16_9(base_img)
    
    # 1. Convert to rich monochrome
    gray = frame.convert("L")
    
    # 2. Add subtle vintage gelatin warmth (tint: R+3%, B-5%)
    r = gray.point(lambda p: min(255, int(p * 1.03)))
    g = gray
    b = gray.point(lambda p: max(0, int(p * 0.95)))
    tinted = Image.merge("RGB", (r, g, b))
    
    # 3. Enhance film contrast (crush pure blacks slightly, expand midtones)
    contrasted = ImageOps.autocontrast(tinted, cutoff=2)
    
    # 4. Cinematic vignette
    return apply_cinematic_vignette(contrasted)

def create_title_overlay_layer(
    label_title: Optional[str] = None,
    label_sub: Optional[str] = None,
    citation: Optional[str] = None,
    callout_red: Optional[str] = None,
    callout_box: Optional[str] = None,
    canvas_size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT)
) -> Optional[Image.Image]:
    """
    Renders the exact typography of 'After the Crown' as a transparent 1920x1080 overlay layer.
    Pure, elegant lower-third in ivory serif with soft blur drop-shadow.
    Zero red alert boxes or amateur PowerPoint banners.
    """
    if not (label_title or label_sub):
        return None

    w, h = canvas_size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    def load_best_font(candidates: list, size: int) -> ImageFont.ImageFont:
        for c in candidates:
            try:
                return ImageFont.truetype(c, size)
            except (IOError, OSError):
                continue
        return ImageFont.load_default()

    font_title = load_best_font([
        "georgiab.ttf", "timesbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    ], 42)
    font_sub = load_best_font([
        "georgiai.ttf", "timesi.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
    ], 26)

    # 1. Lower-Third Serif Label (After the Crown Standard)
    if label_title:
        lx = 120
        ly = h - 180 if label_sub else h - 140
        
        # Soft multi-pass drop shadow for maximum readability over any footage
        for dx, dy in [(1, 1), (2, 2), (2, 3), (3, 3)]:
            odraw.text((lx + dx, ly + dy), label_title, fill=(0, 0, 0, 180), font=font_title)
        odraw.text((lx, ly), label_title, fill=(245, 242, 235, 255), font=font_title)
        
        if label_sub:
            sub_y = ly + 52
            for dx, dy in [(1, 1), (2, 2)]:
                odraw.text((lx + dx, sub_y + dy), label_sub, fill=(0, 0, 0, 160), font=font_sub)
            odraw.text((lx, sub_y), label_sub, fill=(205, 200, 190, 235), font=font_sub)

    return overlay

def render_after_the_crown_frame(
    base_img: Image.Image,
    label_title: Optional[str] = None,
    label_sub: Optional[str] = None,
    citation: Optional[str] = None,
    callout_red: Optional[str] = None,
    callout_box: Optional[str] = None
) -> Image.Image:
    """
    Renders the combined composite frame (for static exports / previews).
    """
    frame = prepare_cinematic_background(base_img)
    overlay = create_title_overlay_layer(
        label_title=label_title,
        label_sub=label_sub,
        citation=citation,
        callout_red=callout_red,
        callout_box=callout_box
    )
    if overlay:
        return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
    return frame
