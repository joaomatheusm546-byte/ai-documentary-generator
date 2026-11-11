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

def prepare_cinematic_background(base_img: Image.Image) -> Image.Image:
    """Prepares the clean 16:9 pillarboxed/cropped image with cinematic vignette for Ken Burns."""
    frame = fit_to_16_9(base_img)
    return apply_cinematic_vignette(frame)

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

    # 1. Top-Right Citation
    if citation:
        cite_text = citation if "Source" in citation else f"{citation} Source in Description"
        bbox = odraw.textbbox((0, 0), cite_text, font=font_cite)
        cite_w = bbox[2] - bbox[0]
        cx = w - cite_w - 70
        cy = 50
        odraw.text((cx + 2, cy + 2), cite_text, fill=(0, 0, 0, 180), font=font_cite)
        odraw.text((cx, cy), cite_text, fill=(235, 230, 220, 240), font=font_cite)

    # 2. Lower-Third White Serif Label
    if label_title:
        lx = 140
        ly = h - 210 if label_sub else h - 160
        odraw.text((lx + 3, ly + 3), label_title, fill=(0, 0, 0, 220), font=font_title)
        odraw.text((lx, ly), label_title, fill=(255, 255, 255, 255), font=font_title)
        
        if label_sub:
            sub_y = ly + 62
            odraw.text((lx + 2, sub_y + 2), label_sub, fill=(0, 0, 0, 200), font=font_sub)
            odraw.text((lx, sub_y), label_sub, fill=(225, 220, 210, 235), font=font_sub)

    # 3. Red Highlight Forensic Callout (Etapa 2)
    if callout_red:
        banner_text = callout_red.upper()
        bbox = odraw.textbbox((0, 0), banner_text, font=font_banner)
        bw = bbox[2] - bbox[0] + 55
        bh = 64
        bx = (w - bw) // 2
        by = h - 160
        # Dark translucent plate with red border and red left accent bar
        odraw.rectangle([bx, by, bx + bw, by + bh], fill=(12, 12, 12, 225), outline=(190, 30, 30, 240), width=2)
        odraw.rectangle([bx, by, bx + 6, by + bh], fill=(220, 35, 35, 255))
        tx = bx + 30
        ty = by + (bh - (bbox[3] - bbox[1])) // 2 - 2
        odraw.text((tx, ty), banner_text, fill=(245, 240, 235, 255), font=font_banner)

    # 4. Black Typewriter Box Callout (Etapa 2)
    if callout_box:
        box_text = callout_box.upper()
        bbox = odraw.textbbox((0, 0), box_text, font=font_box)
        bw = bbox[2] - bbox[0] + 50
        bh = 60
        bx = w - bw - 70
        by = 105
        odraw.rectangle([bx, by, bx + bw, by + bh], fill=(12, 12, 12, 225), outline=(75, 75, 75, 200), width=2)
        tx = bx + 25
        ty = by + (bh - (bbox[3] - bbox[1])) // 2 - 2
        odraw.text((tx, ty), box_text, fill=(240, 235, 225, 250), font=font_box)

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
