import math
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.config import VIDEO_WIDTH, VIDEO_HEIGHT

logger = logging.getLogger("Styler")

def fit_to_16_9(img: Image.Image, target_size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT)) -> Image.Image:
    """
    Fits any aspect ratio into a cinematic 16:9 frame:
    - If near 16:9 (aspect >= 1.5), crops to fill.
    - If vertical or 4:3, creates a blurred, darkened background pillarbox (After the Crown standard).
    """
    tw, th = target_size
    iw, ih = img.size
    aspect = iw / ih

    if 1.5 <= aspect <= 1.9:
        scale = max(tw / iw, th / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        res = img.resize((nw, nh), Image.Resampling.LANCZOS)
        left = (nw - tw) // 2
        top = (nh - th) // 2
        return res.crop((left, top, left + tw, top + th))

    # Blurred pillarbox background
    bg_scale = max(tw / iw, th / ih)
    bg = img.resize((int(iw * bg_scale), int(ih * bg_scale)), Image.Resampling.LANCZOS)
    bg_left = (bg.width - tw) // 2
    bg_top = (bg.height - th) // 2
    bg = bg.crop((bg_left, bg_top, bg_left + tw, bg_top + th))
    bg = bg.filter(ImageFilter.GaussianBlur(35))
    bg = bg.point(lambda p: int(p * 0.40)) # Darken background

    fg_scale = th / ih
    fg_w, fg_h = int(iw * fg_scale), th
    fg = img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)

    paste_x = (tw - fg_w) // 2
    bg.paste(fg, (paste_x, 0))
    return bg

def apply_cinematic_vignette(img: Image.Image) -> Image.Image:
    """Adds a smooth dark radial vignette around the edges."""
    w, h = img.size
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    max_radius = math.hypot(w / 2, h / 2)
    for r in range(int(max_radius * 0.45), int(max_radius), 8):
        dist = max(0.0, (r - max_radius * 0.45) / (max_radius * 0.55))
        alpha = int((dist ** 1.8) * 180)
        vdraw.ellipse([w/2 - r, h/2 - r, w/2 + r, h/2 + r], outline=(0, 0, 0, min(235, alpha)), width=10)
    vignette = vignette.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(img.convert("RGBA"), vignette).convert("RGB")

def render_after_the_crown_frame(
    base_img: Image.Image,
    label_title: Optional[str] = None,
    label_sub: Optional[str] = None,
    citation: Optional[str] = None,
    callout_red: Optional[str] = None,
    callout_box: Optional[str] = None
) -> Image.Image:
    """
    Renders the exact typography and visual signature of 'After the Crown':
    1. 16:9 framing with subtle dark vignette.
    2. Lower-third text: white serif font with soft dark drop shadow.
    3. Top-right citation: '[1] Source in Description'.
    4. Optional red highlight banner ('SIX MARKS A DAY') or black callout box ('ONE SMALL SUITCASE').
    """
    frame = fit_to_16_9(base_img)
    frame = apply_cinematic_vignette(frame)
    w, h = frame.size
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Load system or fallback fonts
    try:
        font_title = ImageFont.truetype("georgiab.ttf", 52)
        font_sub = ImageFont.truetype("georgiai.ttf", 32)
        font_cite = ImageFont.truetype("georgia.ttf", 28)
        font_banner = ImageFont.truetype("georgiab.ttf", 36)
        font_box = ImageFont.truetype("courbd.ttf", 32)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_cite = ImageFont.load_default()
        font_banner = ImageFont.load_default()
        font_box = ImageFont.load_default()

    # 1. Top-Right Citation
    if citation:
        cite_text = citation if "Source" in citation else f"{citation} Source in Description"
        bbox = odraw.textbbox((0, 0), cite_text, font=font_cite)
        cite_w = bbox[2] - bbox[0]
        cx = w - cite_w - 70
        cy = 50
        # Shadow
        odraw.text((cx + 2, cy + 2), cite_text, fill=(0, 0, 0, 180), font=font_cite)
        odraw.text((cx, cy), cite_text, fill=(235, 230, 220, 240), font=font_cite)

    # 2. Lower-Third White Serif Label (After the Crown Frame 5)
    if label_title:
        lx = 140
        ly = h - 210 if label_sub else h - 160
        # Title Shadow & Text
        odraw.text((lx + 3, ly + 3), label_title, fill=(0, 0, 0, 210), font=font_title)
        odraw.text((lx, ly), label_title, fill=(255, 255, 255, 255), font=font_title)
        
        if label_sub:
            sub_y = ly + 62
            odraw.text((lx + 2, sub_y + 2), label_sub, fill=(0, 0, 0, 190), font=font_sub)
            odraw.text((lx, sub_y), label_sub, fill=(225, 220, 210, 235), font=font_sub)

    # 3. Red Banner Callout (After the Crown Frame 20: "SIX MARKS A DAY")
    if callout_red:
        banner_text = callout_red.upper()
        bbox = odraw.textbbox((0, 0), banner_text, font=font_banner)
        bw = bbox[2] - bbox[0] + 60
        bh = 70
        bx = (w - bw) // 2
        by = h - 160
        # Red rectangle
        odraw.rectangle([bx, by, bx + bw, by + bh], fill=(160, 25, 25, 235))
        # Text centered
        tx = bx + 30
        ty = by + 14
        odraw.text((tx, ty), banner_text, fill=(255, 255, 255, 255), font=font_banner)

    # 4. Black Typewriter Box Callout (After the Crown Frame 25: "ONE SMALL SUITCASE")
    if callout_box:
        box_text = callout_box.upper()
        bbox = odraw.textbbox((0, 0), box_text, font=font_box)
        bw = bbox[2] - bbox[0] + 50
        bh = 65
        bx = w - bw - 70
        by = 105
        # Black rectangle
        odraw.rectangle([bx, by, bx + bw, by + bh], fill=(15, 15, 15, 235), outline=(50, 50, 50, 200), width=2)
        # Typewriter text centered
        tx = bx + 25
        ty = by + 14
        odraw.text((tx, ty), box_text, fill=(245, 240, 230, 250), font=font_box)

    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
