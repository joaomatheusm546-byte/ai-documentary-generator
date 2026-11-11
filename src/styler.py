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
    Renders the exact typography and visual signature of 'After the Crown'
    as an independent, transparent 1920x1080 overlay layer.
    Stays 100% stationary and anchored over moving footage without scaling.
    """
    if not (label_title or label_sub or citation or callout_red or callout_box):
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
    ], 52)
    font_sub = load_best_font([
        "georgiai.ttf", "timesi.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
    ], 32)
    font_cite = load_best_font([
        "georgia.ttf", "times.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    ], 28)
    font_banner = load_best_font([
        "georgiab.ttf", "timesbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    ], 36)
    font_box = load_best_font([
        "courbd.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    ], 32)

    # 1. Lower-Third White Serif Label (After the Crown Standard)
    if label_title:
        lx = 140
        ly = h - 210 if label_sub else h - 160
        
        # Soft dark gradient glow behind text for contrast
        odraw.text((lx + 3, ly + 3), label_title, fill=(0, 0, 0, 240), font=font_title)
        odraw.text((lx, ly), label_title, fill=(255, 255, 255, 255), font=font_title)
        
        if label_sub:
            sub_y = ly + 62
            odraw.text((lx + 2, sub_y + 2), label_sub, fill=(0, 0, 0, 220), font=font_sub)
            odraw.text((lx, sub_y), label_sub, fill=(225, 220, 210, 240), font=font_sub)

    # 2. Forensic Red Callout Banner
    if callout_red:
        banner_text = callout_red.upper()
        bbox = odraw.textbbox((0, 0), banner_text, font=font_banner)
        bw = bbox[2] - bbox[0] + 55
        bh = 64
        bx = (w - bw) // 2
        by = h - 160
        # Dark translucent plate with red border and red left accent bar
        odraw.rectangle([bx, by, bx + bw, by + bh], fill=(12, 12, 12, 235), outline=(190, 30, 30, 255), width=2)
        odraw.rectangle([bx, by, bx + 6, by + bh], fill=(220, 35, 35, 255))
        tx = bx + 30
        ty = by + (bh - (bbox[3] - bbox[1])) // 2 - 2
        odraw.text((tx, ty), banner_text, fill=(245, 240, 235, 255), font=font_banner)

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
