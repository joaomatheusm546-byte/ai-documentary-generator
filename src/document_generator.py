import math
from pathlib import Path
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_declassified_document(
    quote_text: str,
    header_agency: str = "COUNTER-INTELLIGENCE CORPS // SPECIAL INVESTIGATION",
    dossier_no: str = "CASE FILE #45-BERCHTESGADEN",
    stamp_text: str = "DECLASSIFIED",
    output_path: Optional[Path] = None,
    size: Tuple[int, int] = (1920, 1080)
) -> Image.Image:
    """
    Generates a high-resolution, cinema-grade 'After the Crown' declassified archival document.
    Includes aged paper texture, agency letterhead, typewriter body text, and official stamp.
    """
    width, height = size
    # Base aged paper tone
    doc = Image.new("RGBA", (width, height), (232, 222, 204, 255))
    draw = ImageDraw.Draw(doc)

    # 1. Subtle Paper Grain / Fiber Noise
    import random
    noise = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    noise_draw = ImageDraw.Draw(noise)
    for _ in range(25000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        gray = random.randint(180, 220)
        noise_draw.point((x, y), fill=(gray, gray, gray, 18))
    doc = Image.alpha_composite(doc, noise)
    draw = ImageDraw.Draw(doc)

    # 2. Outer Border / Case Margins
    margin = 120
    draw.rectangle([margin, margin, width - margin, height - margin], outline=(140, 128, 110, 180), width=2)
    draw.line([margin, margin + 80, width - margin, margin + 80], fill=(140, 128, 110, 180), width=2)

    # Load system or default font
    try:
        font_header = ImageFont.truetype("cour.ttf", 26)
        font_sub = ImageFont.truetype("cour.ttf", 18)
        font_body = ImageFont.truetype("courbd.ttf", 36)
        font_stamp = ImageFont.truetype("arialbd.ttf", 52)
    except IOError:
        font_header = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_stamp = ImageFont.load_default()

    # 3. Header Text
    draw.text((margin + 30, margin + 25), header_agency.upper(), fill=(60, 52, 44, 255), font=font_header)
    draw.text((width - margin - 380, margin + 28), dossier_no.upper(), fill=(90, 80, 70, 255), font=font_sub)

    # 4. Official Red Rubber Stamp (Angled)
    stamp_img = Image.new("RGBA", (500, 140), (0, 0, 0, 0))
    stamp_draw = ImageDraw.Draw(stamp_img)
    stamp_draw.rectangle([10, 10, 480, 120], outline=(180, 35, 30, 220), width=6)
    stamp_draw.text((35, 32), stamp_text.upper(), fill=(180, 35, 30, 230), font=font_stamp)
    
    # Rotate stamp slightly
    rotated_stamp = stamp_img.rotate(14, expand=True, resample=Image.BICUBIC)
    doc.paste(rotated_stamp, (width - margin - 460, margin + 110), rotated_stamp)

    # 5. Typewritten Forensic Text (Wrapped)
    # Break quote_text into lines of ~50 chars
    words = quote_text.split()
    lines = []
    curr = []
    for w in words:
        if len(" ".join(curr + [w])) <= 52:
            curr.append(w)
        else:
            lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))

    start_y = margin + 220
    line_height = 54
    
    # Draw typewriter text with subtle character offsets (organic typewriter imperfection)
    for idx, line in enumerate(lines):
        line_y = start_y + (idx * line_height)
        
        # Draw translucent amber highlighter on key lines (lines 1 & 2 for documentary effect)
        if idx in (1, 2) and len(line) > 10:
            highlight_width = min(len(line) * 22, width - (margin * 2) - 100)
            draw.rectangle(
                [margin + 45, line_y - 4, margin + 45 + highlight_width, line_y + 40],
                fill=(245, 215, 60, 110) # Translucent amber marker
            )

        draw.text((margin + 50, line_y), line, fill=(35, 30, 25, 240), font=font_body)

    # 6. Apply Subtle Edge Burn / Vignette
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.convert("RGB").save(output_path, "JPEG", quality=95)
        
    return doc

if __name__ == "__main__":
    from src.config import TEMP_DIR
    out = TEMP_DIR / "sample_declassified_doc.jpg"
    create_declassified_document(
        quote_text='"Subject was interrogated at Berchtesgaden regarding personal correspondence with the Reich Chancellery. Subject insisted she had no knowledge of executive camp operations."',
        output_path=out
    )
    print("Sample document created at:", out)
