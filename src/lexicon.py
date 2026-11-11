"""
Historical Lexicon & Phonetic Calibration Module
Ensures 100% canonical naming and precise pronunciation for English neural voices
(specifically en-US-ChristopherNeural) across German, Austrian, and historical entities.
"""

from typing import Dict

# Canonical historical names (Grammar & Historical Accuracy)
CANONICAL_ENTITIES: Dict[str, str] = {
    "Hammitzer": "Hammitzsch",
    "Martin Hammitzer": "Martin Hammitzsch",
    "Jelly": "Geli",
    "Robel": "Raubal",
    "Jelly Robel": "Geli Raubal",
}

# Phonetic substitutions specifically tuned for en-US-ChristopherNeural
# to prevent neural mispronunciations or automated subtitle mis-transcriptions
PHONETIC_TTS_REPLACEMENTS: Dict[str, str] = {
    # Names
    "Geli Raubal": "Gay-lee Row-bahl",
    "Raubal": "Row-bahl",
    "Geli": "Gay-lee",
    "Alois": "Ah-lo-iss",
    "Pölzl": "Pel-tsel",
    "Klara Pölzl": "Klara Pel-tsel",
    "Hammitzsch": "Hahm-itch",
    "Schicklgruber": "Shick-el-groo-ber",
    "Hiedler": "Heed-ler",
    "Hüttler": "Hoot-ler",
    
    # Austrian / German locations
    "Waldviertel": "Vald-feer-tel",
    "Braunau am Inn": "Brow-now ahm Inn",
    "Döllersheim": "Derr-lers-hime",
    "Strones": "Stro-ness",
    "Spital": "Shpee-tahl",
    "Leonding": "Lay-on-ding",
    "Berchtesgaden": "Bare-khtes-gah-den",
    "Obersalzberg": "Oh-ber-zaalts-berg",
    "Berghof": "Bare-khof",
    "Napola": "Nah-POH-lah",
}

def sanitize_canonical_text(text: str) -> str:
    """Corrects historical spelling and typographical errors in the canonical text."""
    sanitized = text
    for wrong, canonical in CANONICAL_ENTITIES.items():
        sanitized = sanitized.replace(wrong, canonical)
    return sanitized

def prepare_text_for_tts(text: str) -> str:
    """
    Prepares text for Edge-TTS neural voice:
    1. Corrects historical spelling.
    2. Applies phonetic respelling so the English neural voice pronounces
       German/Austrian names with natural, broadcast-grade clarity.
    """
    clean = sanitize_canonical_text(text)
    for canonical, phonetic in PHONETIC_TTS_REPLACEMENTS.items():
        clean = clean.replace(canonical, phonetic)
    return clean
