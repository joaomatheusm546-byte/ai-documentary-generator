import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import FFPROBE_BIN

SCRIPT_PATH = ROOT / "assets" / "operation_myth_master_script.json"
CAND_DIR = ROOT / "assets" / "operation_myth_archive" / "candidates"
DOCS_DIR = ROOT / "assets" / "operation_myth_archive" / "documents"
GEN_DIR = ROOT / "assets" / "operation_myth_archive" / "generated"
PUBLIC_DIR = ROOT / "remotion_app" / "public"
MYTH_IMG_DIR = PUBLIC_DIR / "myth_images"
CUTOUTS_DIR = PUBLIC_DIR / "cutouts"
MYTH_AUDIO_DIR = ROOT / "assets" / "operation_myth_audio"
REMOTION_AUDIO_DIR = PUBLIC_DIR / "audio"
REMOTION_SRC_DIR = ROOT / "remotion_app" / "src"
AUDIT_OUT_DIR = ROOT / "assets" / "operation_myth_archive" / "storyboard_audit"

MYTH_IMG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)

# Clean up cutouts that showed cropped limbs / multi-person artifacts in visual audit
DEPRECATED_CUTOUTS = [
    "myth_zhukov_cutout.png",
    "myth_truman_cutout.png",
    "myth_hans_baur_cutout.png",
    "myth_charlier_cutout.png",
]

# Explicit curated mapping: (scene, beat_1based) -> spec dict
# Overrides layout/bg/subject where visual precision or portrait verification demands it.
VISUAL_MAP = {
    # ---------------- ACT I ----------------
    (1, 1): {"layout": "split_collage", "bg": "cand:potsdam_1945__001.jpg", "doc": "doc:doc_03_stalin_classified_order.jpg", "subj": "cut:myth_stalin_cutout.png"},
    (1, 2): {"layout": "landscape", "bg": "cand:lubyanka__030.jpg"},
    (1, 3): {"layout": "document", "bg": "gen:plate_maroon_box_1945.jpg", "subj": "doc:doc_01_autopsy_may1945.jpg", "hi": None},
    (1, 4): {"layout": "landscape", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg"},

    (2, 1): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__115.jpg"},
    (2, 2): {"layout": "landscape", "bg": "cand:w2_chancellery_ruins__050.jpg"},
    (2, 3): {"layout": "landscape", "bg": "cand:fuehrerbunker_1945__006.jpg"},
    (2, 4): {"layout": "landscape", "bg": "gen:plate_crater_1945.jpg"},

    (3, 1): {"layout": "landscape", "bg": "cand:linge_gunsche__018.jpg"},
    (3, 2): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__116.jpg"},
    (3, 3): {"layout": "document", "bg": "cand:w5_cat_battle_berlin__119.jpg", "subj": "cand:w2_berlin_map_1945__058.jpg", "hi": "REICH CHANCELLERY // SECTOR GRID", "hstyle": "red_circle"},
    (3, 4): {"layout": "landscape", "bg": "cand:w2_berlin_1945_streets__055.jpg"},

    (4, 1): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_01_autopsy_may1945.jpg", "hi": None},
    (4, 2): {"layout": "landscape", "bg": "cand:w3_reichstag_1945_ruins__077.jpg"},
    (4, 3): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__091.jpg"},
    (4, 4): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},

    (5, 1): {"layout": "landscape", "bg": "cand:w3_dental_xray_vintage__093.png"},
    (5, 2): {"layout": "silhouette", "bg": "cand:w5_cat_battle_berlin__117.jpg", "sil": "classified", "stxt": "SMERSH INTERPRETER", "ssub": "ELENA RZHEVSKAYA // ARCHIVE RESTRICTED"},
    (5, 3): {"layout": "landscape", "bg": "cand:w2_hugo_blaschke__071.jpg"},
    (5, 4): {"layout": "landscape", "bg": "cand:w3_german_pow_1945__086.jpg"},

    (6, 1): {"layout": "silhouette", "bg": "cand:w3_german_pow_1945__085.jpg", "sil": "classified", "stxt": "WITNESS TESTIMONY RECORDED", "ssub": "KÄTHE HEUSERMANN // CLINIC STAFF"},
    (6, 2): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__092.jpg"},
    (6, 3): {"layout": "landscape", "bg": "cand:nazi_surrender_berlin__049.jpg"},
    (6, 4): {"layout": "landscape", "bg": "cand:w3_dental_xray_vintage__094.png"},

    (7, 1): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__091.jpg"},
    (7, 2): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},
    (7, 3): {"layout": "landscape", "bg": "cand:w3_dental_xray_vintage__093.png"},
    (7, 4): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_02_dental_sketch_1945.jpg", "hi": None},

    (8, 1): {"layout": "landscape", "bg": "cand:w3_berlin_battle_bundesarchiv__076.jpg"},
    (8, 2): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__119.jpg"},
    (8, 3): {"layout": "landscape", "bg": "cand:w2_butyrka_prison__069.jpg"},
    (8, 4): {"layout": "document", "bg": "cand:w4_gulag_camp_1950__114.jpg", "subj": "doc:doc_03_stalin_classified_order.jpg", "hi": None},

    (9, 1): {"layout": "portrait", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg", "subj": "cut:myth_stalin_cutout.png"},
    (9, 2): {"layout": "document", "bg": "cand:lubyanka__030.jpg", "subj": "doc:doc_01_autopsy_may1945.jpg", "hi": None},
    (9, 3): {"layout": "landscape", "bg": "cand:kremlin_1945__032.jpg"},
    (9, 4): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__118.jpg"},

    # ---------------- ACT II ----------------
    (10, 1): {"layout": "landscape", "bg": "cand:zhukov_1945__009.jpg"},
    (10, 2): {"layout": "landscape", "bg": "cand:w3_berlin_battle_bundesarchiv__075.jpg"},
    (10, 3): {"layout": "document", "bg": "cand:hans_baur__022.jpg", "subj": "doc:doc_04_zhukov_june1945_news.jpg", "hi": None},
    (10, 4): {"layout": "landscape", "bg": "cand:w2_times_square_1945__073.jpg"},

    (11, 1): {"layout": "landscape", "bg": "cand:w2_potsdam_palace__064.jpg"},
    (11, 2): {"layout": "portrait", "bg": "cand:potsdam_1945__002.jpg", "subj": "cut:myth_stalin_cutout.png"},
    (11, 3): {"layout": "landscape", "bg": "cand:w3_truman_potsdam__087.jpg"},
    (11, 4): {"layout": "landscape", "bg": "cand:w3_truman_potsdam__088.jpg"},

    (12, 1): {"layout": "document", "bg": "cand:lubyanka__030.jpg", "subj": "cand:fbi_hq__042.jpg", "hi": None},
    (12, 2): {"layout": "document", "bg": "cand:w2_times_square_1945__073.jpg", "subj": "doc:doc_05_fbi_file_65_53615.jpg", "hi": None},
    (12, 3): {"layout": "landscape", "bg": "cand:u_boat_argentina__034.jpg"},
    (12, 4): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},

    (13, 1): {"layout": "landscape", "bg": "cand:kremlin_1945__032.jpg"},
    (13, 2): {"layout": "portrait", "bg": "cand:lubyanka__030.jpg", "subj": "cut:myth_beria_cutout.png"},
    (13, 3): {"layout": "landscape", "bg": "gen:plate_crater_1945.jpg"},
    (13, 4): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_06_operation_myth_1946_cover.jpg", "hi": None},

    (14, 1): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__120.jpg"},
    (14, 2): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__117.jpg"},
    (14, 3): {"layout": "document", "bg": "cand:w4_berlin_ruins_45_a__101.jpg", "subj": "doc:doc_14_magdeburg_route_map.jpg", "hi": None},
    (14, 4): {"layout": "landscape", "bg": "cand:w3_magdeburg_old__098.jpg"},

    (15, 1): {"layout": "document", "bg": "cand:lubyanka__030.jpg", "subj": "doc:doc_06_operation_myth_1946_cover.jpg", "hi": None},
    (15, 2): {"layout": "portrait", "bg": "cand:w2_butyrka_prison__069.jpg", "subj": "cut:myth_gunsche_cutout.png"},
    (15, 3): {"layout": "landscape", "bg": "cand:w2_bunker_ruins__053.jpg"},
    (15, 4): {"layout": "landscape", "bg": "gen:plate_bunker_stairs_1945.jpg"},

    (16, 1): {"layout": "document", "bg": "gen:plate_maroon_box_1945.jpg", "subj": "doc:doc_07_cranium_discrepancy_1946.jpg", "hi": None},
    (16, 2): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__091.jpg"},
    (16, 3): {"layout": "landscape", "bg": "cand:w2_walther_ppk__060.jpg"},
    (16, 4): {"layout": "document", "bg": "gen:plate_crater_1945.jpg", "subj": "cand:w2_chancellery_ruins__051.jpg", "hi": None},

    (17, 1): {"layout": "family_tree", "bg": "gen:plate_fsb_vault.jpg"},
    (17, 2): {"layout": "landscape", "bg": "cand:lubyanka__030.jpg"},
    (17, 3): {"layout": "landscape", "bg": "cand:w3_magdeburg_old__098.jpg"},
    (17, 4): {"layout": "landscape", "bg": "cand:w2_chancellery_ruins__050.jpg"},

    (18, 1): {"layout": "landscape", "bg": "cand:w2_berlin_1945_streets__055.jpg"},
    (18, 2): {"layout": "landscape", "bg": "cand:w3_german_pow_1945__085.jpg"},
    (18, 3): {"layout": "landscape", "bg": "cand:fuehrerbunker_1945__006.jpg"},
    (18, 4): {"layout": "landscape", "bg": "gen:plate_crater_1945.jpg"},

    # ---------------- ACT III ----------------
    (19, 1): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__119.jpg"},
    (19, 2): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__115.jpg"},
    (19, 3): {"layout": "document", "bg": "cand:w2_bunker_ruins__053.jpg", "subj": "doc:doc_07_cranium_discrepancy_1946.jpg", "hi": None},
    (19, 4): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__092.jpg"},

    (20, 1): {"layout": "landscape", "bg": "cand:w3_dental_xray_vintage__093.png"},
    (20, 2): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__091.jpg"},
    (20, 3): {"layout": "portrait", "bg": "gen:plate_crater_1945.jpg", "subj": "cut:myth_eva_braun_cutout.png"},
    (20, 4): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_07_cranium_discrepancy_1946.jpg", "hi": None},

    (21, 1): {"layout": "landscape", "bg": "gen:plate_bunker_stairs_1945.jpg"},
    (21, 2): {"layout": "landscape", "bg": "cand:w2_bunker_ruins__053.jpg"},
    (21, 3): {"layout": "document", "bg": "cand:fuehrerbunker_1945__006.jpg", "subj": "cand:w4_bunker_plan_clean__110.png", "hi": "BUNKER STUDY -> GARDEN EXIT", "hstyle": "red_circle"},
    (21, 4): {"layout": "landscape", "bg": "cand:linge_gunsche__018.jpg"},

    (22, 1): {"layout": "landscape", "bg": "cand:w2_butyrka_prison__069.jpg"},
    (22, 2): {"layout": "landscape", "bg": "cand:w2_rochus_misch__072.jpg"},
    (22, 3): {"layout": "landscape", "bg": "cand:w2_walther_ppk__061.jpg"},
    (22, 4): {"layout": "landscape", "bg": "cand:lubyanka__031.jpg"},

    (23, 1): {"layout": "document", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg", "subj": "doc:doc_08_dossier_462a_1949.jpg", "hi": None},
    (23, 2): {"layout": "portrait", "bg": "cand:lubyanka__030.jpg", "subj": "cut:myth_stalin_cutout.png"},
    (23, 3): {"layout": "landscape", "bg": "cand:stalin_1945__012.jpg"},
    (23, 4): {"layout": "landscape", "bg": "gen:plate_fsb_vault.jpg"},

    (24, 1): {"layout": "landscape", "bg": "cand:stalin_funeral__046.jpg"},
    (24, 2): {"layout": "landscape", "bg": "cand:stalin_funeral__047.jpg"},
    (24, 3): {"layout": "landscape", "bg": "cand:u_boat_argentina__034.jpg"},
    (24, 4): {"layout": "landscape", "bg": "cand:w3_magdeburg_old__098.jpg"},

    (25, 1): {"layout": "document", "bg": "gen:plate_magdeburg_tent_1970.jpg", "subj": "doc:doc_14_magdeburg_route_map.jpg", "hi": None},
    (25, 2): {"layout": "landscape", "bg": "cand:w4_berlin_ruins_45_a__101.jpg"},
    (25, 3): {"layout": "landscape", "bg": "cand:w2_hugo_blaschke__071.jpg"},
    (25, 4): {"layout": "landscape", "bg": "cand:lubyanka__030.jpg"},

    (26, 1): {"layout": "document", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg", "subj": "cand:bezymensky__025.jpg", "hi": "1968 SOVIET EDITION", "hstyle": "marker"},
    (26, 2): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_09_censor_redaction_1968.jpg", "hi": None},
    (26, 3): {"layout": "landscape", "bg": "cand:w2_walther_ppk__061.jpg"},
    (26, 4): {"layout": "landscape", "bg": "cand:lubyanka__031.jpg"},

    (27, 1): {"layout": "landscape", "bg": "cand:magdeburg__036.jpg"},
    (27, 2): {"layout": "portrait", "bg": "cand:lubyanka__030.jpg", "subj": "cut:myth_andropov_cutout.png"},
    (27, 3): {"layout": "document", "bg": "cand:w3_magdeburg_old__098.jpg", "subj": "cand:w3_magdeburg_old__097.jpg", "hi": None},
    (27, 4): {"layout": "landscape", "bg": "cand:andropov__026.jpg"},

    # ---------------- ACT IV ----------------
    (28, 1): {"layout": "document", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg", "subj": "doc:doc_10_andropov_memo_1970.jpg", "hi": None},
    (28, 2): {"layout": "portrait", "bg": "cand:lubyanka__031.jpg", "subj": "cut:myth_brezhnev_cutout.png"},
    (28, 3): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_11_kgb_destruction_1970.jpg", "hi": None},
    (28, 4): {"layout": "landscape", "bg": "gen:plate_magdeburg_tent_1970.jpg"},

    (29, 1): {"layout": "landscape", "bg": "cand:w3_magdeburg_old__098.jpg"},
    (29, 2): {"layout": "landscape", "bg": "gen:plate_magdeburg_tent_1970.jpg"},
    (29, 3): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_11_kgb_destruction_1970.jpg", "hi": None},
    (29, 4): {"layout": "document", "bg": "cand:w3_magdeburg_old__098.jpg", "subj": "doc:doc_14_magdeburg_route_map.jpg", "hi": None},

    (30, 1): {"layout": "landscape", "bg": "gen:plate_biederitz_dawn_1970.jpg"},
    (30, 2): {"layout": "landscape", "bg": "gen:plate_crater_1945.jpg"},
    (30, 3): {"layout": "landscape", "bg": "gen:plate_biederitz_dawn_1970.jpg"},
    (30, 4): {"layout": "document", "bg": "cand:lubyanka__030.jpg", "subj": "doc:doc_11_kgb_destruction_1970.jpg", "hi": None},

    (31, 1): {"layout": "landscape", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg"},
    (31, 2): {"layout": "family_tree", "bg": "gen:plate_fsb_vault.jpg"},
    (31, 3): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},
    (31, 4): {"layout": "landscape", "bg": "cand:lubyanka__030.jpg"},

    (32, 1): {"layout": "landscape", "bg": "gen:plate_fsb_vault.jpg"},
    (32, 2): {"layout": "document", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg", "subj": "doc:doc_11_kgb_destruction_1970.jpg", "hi": None},
    (32, 3): {"layout": "landscape", "bg": "cand:w3_dental_xray_vintage__093.png"},
    (32, 4): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},

    (33, 1): {"layout": "landscape", "bg": "cand:lubyanka__031.jpg"},
    (33, 2): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__091.jpg"},
    (33, 3): {"layout": "document", "bg": "cand:w3_human_skull_xray__092.jpg", "subj": "doc:doc_07_cranium_discrepancy_1946.jpg", "hi": None},
    (33, 4): {"layout": "landscape", "bg": "cand:dna_lab__045.jpg"},

    (34, 1): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__092.jpg"},
    (34, 2): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_07_cranium_discrepancy_1946.jpg", "hi": None},
    (34, 3): {"layout": "landscape", "bg": "cand:lubyanka__030.jpg"},
    (34, 4): {"layout": "landscape", "bg": "cand:dna_lab__045.jpg"},

    (35, 1): {"layout": "landscape", "bg": "gen:plate_fsb_vault.jpg"},
    (35, 2): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__091.jpg"},
    (35, 3): {"layout": "landscape", "bg": "cand:w2_bunker_ruins__053.jpg"},
    (35, 4): {"layout": "landscape", "bg": "cand:dna_lab__045.jpg"},

    (36, 1): {"layout": "landscape", "bg": "cand:dna_lab__044.jpg"},
    (36, 2): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "cand:w3_microscope_lab__096.jpg", "hi": None},
    (36, 3): {"layout": "landscape", "bg": "cand:dna_lab__045.jpg"},
    (36, 4): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__092.jpg"},

    # ---------------- ACT V ----------------
    (37, 1): {"layout": "document", "bg": "cand:dna_lab__044.jpg", "subj": "doc:doc_12_uconn_dna_2009.jpg", "hi": None},
    (37, 2): {"layout": "landscape", "bg": "cand:dna_lab__045.jpg"},
    (37, 3): {"layout": "landscape", "bg": "cand:w2_bunker_ruins__053.jpg"},
    (37, 4): {"layout": "document", "bg": "cand:stalin_1945__012.jpg", "subj": "doc:doc_04_zhukov_june1945_news.jpg", "hi": None},

    (38, 1): {"layout": "document", "bg": "cand:u_boat_argentina__034.jpg", "subj": "doc:doc_05_fbi_file_65_53615.jpg", "hi": None},
    (38, 2): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__119.jpg"},
    (38, 3): {"layout": "landscape", "bg": "gen:plate_crater_1945.jpg"},
    (38, 4): {"layout": "portrait", "bg": "cand:w2_bunker_ruins__053.jpg", "subj": "cut:myth_eva_braun_cutout.png"},

    (39, 1): {"layout": "landscape", "bg": "cand:lubyanka__030.jpg"},
    (39, 2): {"layout": "landscape", "bg": "gen:plate_fsb_vault.jpg"},
    (39, 3): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},
    (39, 4): {"layout": "landscape", "bg": "cand:lubyanka__031.jpg"},

    (40, 1): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "cand:charlier__041.jpg", "hi": None},
    (40, 2): {"layout": "document", "bg": "cand:dna_lab__045.jpg", "subj": "cand:w3_microscope_lab__096.jpg", "hi": None},
    (40, 3): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},
    (40, 4): {"layout": "document", "bg": "cand:lubyanka__030.jpg", "subj": "doc:doc_02_dental_sketch_1945.jpg", "hi": None},

    (41, 1): {"layout": "document", "bg": "cand:w3_dental_xray_vintage__093.png", "subj": "doc:doc_13_charlier_2018_study.jpg", "hi": None},
    (41, 2): {"layout": "landscape", "bg": "cand:w3_human_skull_xray__091.jpg"},
    (41, 3): {"layout": "landscape", "bg": "cand:w3_dental_xray_vintage__094.png"},
    (41, 4): {"layout": "portrait", "bg": "cand:w2_chancellery_ruins__050.jpg", "subj": "cut:myth_hitler_cutout.png"},

    (42, 1): {"layout": "landscape", "bg": "cand:w3_dental_xray_vintage__093.png"},
    (42, 2): {"layout": "document", "bg": "cand:dna_lab__044.jpg", "subj": "doc:doc_13_charlier_2018_study.jpg", "hi": None},
    (42, 3): {"layout": "landscape", "bg": "cand:w2_walther_ppk__060.jpg"},
    (42, 4): {"layout": "landscape", "bg": "gen:plate_bunker_stairs_1945.jpg"},

    (43, 1): {"layout": "landscape", "bg": "cand:w5_cat_battle_berlin__118.jpg"},
    (43, 2): {"layout": "landscape", "bg": "cand:w3_berlin_battle_bundesarchiv__076.jpg"},
    (43, 3): {"layout": "portrait", "bg": "cand:potsdam_1945__001.jpg", "subj": "cut:myth_stalin_cutout.png"},
    (43, 4): {"layout": "landscape", "bg": "gen:plate_biederitz_dawn_1970.jpg"},

    (44, 1): {"layout": "document", "bg": "gen:plate_magdeburg_tent_1970.jpg", "subj": "doc:doc_11_kgb_destruction_1970.jpg", "hi": None},
    (44, 2): {"layout": "landscape", "bg": "gen:plate_maroon_box_1945.jpg"},
    (44, 3): {"layout": "landscape", "bg": "cand:w3_reichstag_1945_ruins__077.jpg"},
    (44, 4): {"layout": "landscape", "bg": "cand:fuehrerbunker_1945__006.jpg"},

    (45, 1): {"layout": "document", "bg": "gen:plate_fsb_vault.jpg", "subj": "doc:doc_08_dossier_462a_1949.jpg", "hi": None},
    (45, 2): {"layout": "landscape", "bg": "cand:w3_moscow_kremlin_1940s__081.jpg"},
    (45, 3): {"layout": "landscape", "bg": "cand:lubyanka__030.jpg"},
    (45, 4): {"layout": "landscape", "bg": "gen:plate_fsb_vault.jpg"},
}


def resolve_src(ref: str) -> Path:
    kind, name = ref.split(":", 1)
    if kind == "cand":
        return CAND_DIR / name
    if kind == "doc":
        return DOCS_DIR / name
    if kind == "gen":
        return GEN_DIR / name
    if kind == "cut":
        return CUTOUTS_DIR / name
    raise ValueError(f"Unknown ref kind: {ref}")


def stage_to_public(ref: str) -> str:
    """Copy verified file into remotion_app/public/myth_images (or cutout path) and return relative public path."""
    kind, name = ref.split(":", 1)
    if kind == "cut":
        p = CUTOUTS_DIR / name
        if not p.exists():
            raise FileNotFoundError(f"Cutout missing: {p}")
        return f"cutouts/{name}"

    src = resolve_src(ref)
    if not src.exists():
        raise FileNotFoundError(f"Visual asset missing: {src}")

    dest = MYTH_IMG_DIR / name
    if not dest.exists() or dest.stat().st_size != src.stat().st_size:
        shutil.copy2(src, dest)
    return f"myth_images/{name}"


def prepare_visuals():
    # Remove deprecated cutouts
    for dep in DEPRECATED_CUTOUTS:
        p = CUTOUTS_DIR / dep
        if p.exists():
            p.unlink()
            print(f"[REMOVED DEPRECATED CUTOUT] {dep}")

    script = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    assert len(script["scenes"]) == 45, "Expected 45 scenes"

    flat_entries = []
    prev_primary = None
    consecutive_repeats = 0

    for sc in script["scenes"]:
        s_num = sc["scene"]
        for b_idx, b in enumerate(sc["beats"], 1):
            m = VISUAL_MAP.get((s_num, b_idx))
            if not m:
                raise KeyError(f"Missing VISUAL_MAP entry for (scene={s_num}, beat={b_idx})")

            bg_rel = stage_to_public(m["bg"])
            subj_rel = stage_to_public(m["subj"]) if "subj" in m and m["subj"] else None
            doc_rel = stage_to_public(m["doc"]) if "doc" in m and m["doc"] else None

            primary_key = doc_rel or subj_rel or bg_rel
            if primary_key == prev_primary:
                consecutive_repeats += 1
                print(f"[WARN CONSECUTIVE REPEAT] S{s_num:02d}B{b_idx}: {primary_key}")
            prev_primary = primary_key

            flat_entries.append({
                "id": f"s{s_num:02d}_b{b_idx}",
                "scene": s_num,
                "act": sc["act"],
                "beat": b_idx,
                "layout": m["layout"],
                "bg_path": resolve_src(m["bg"]),
                "subj_path": resolve_src(m["subj"]) if "subj" in m and m["subj"] else None,
                "doc_path": resolve_src(m["doc"]) if "doc" in m and m["doc"] else None,
                "label": b.get("label_title"),
                "sfx": b.get("sfx"),
                "impact": b.get("impact_text"),
            })

    print(f"Verified all {len(flat_entries)} beats! Consecutive exact primary repeats = {consecutive_repeats}")

    # Render 5 storyboard audit contact sheets (36 panels each = 180 panels total)
    cols, rows = 6, 6
    cell_w, cell_h = 320, 210
    for act_idx in range(5):
        chunk = flat_entries[act_idx * 36 : (act_idx + 1) * 36]
        sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (16, 17, 21))
        draw = ImageDraw.Draw(sheet)
        for idx, item in enumerate(chunk):
            cx = (idx % cols) * cell_w
            cy = (idx // cols) * cell_h
            # Preview primary visual
            preview_p = item["doc_path"] or item["subj_path"] or item["bg_path"]
            im = Image.open(preview_p).convert("RGBA")
            im.thumbnail((cell_w - 14, cell_h - 38), Image.LANCZOS)
            bg_thumb = Image.new("RGB", im.size, (26, 28, 34))
            bg_thumb.paste(im, (0, 0), im)
            px = cx + (cell_w - im.width) // 2
            py = cy + 32 + (cell_h - 38 - im.height) // 2
            sheet.paste(bg_thumb, (px, py))

            tag = f"{item['id']} [{item['layout'][:4].upper()}] {preview_p.stem[:20]}"
            draw.text((cx + 6, cy + 6), tag, fill=(240, 210, 120))
            if item["sfx"] != "none":
                draw.text((cx + 6, cy + 18), f"SFX:{item['sfx']} IMP:{item['impact'] or '-'}", fill=(130, 220, 170))

        out_cs = AUDIT_OUT_DIR / f"pre_render_audit_act{act_idx + 1}.jpg"
        sheet.save(out_cs, quality=90)
        print(f"[STORYBOARD SHEET] {out_cs}")


def get_audio_duration(p: Path) -> float:
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(p),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())


def build_configs():
    script = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    act_names = {
        1: "Act I: The Burned Pit & The Dentist's Clue",
        2: "Act II: The Potsdam Deception",
        3: "Act III: Operation Myth (1946–1970)",
        4: "Act IV: Operation Archive & The Ashes",
        5: "Act V: The Skull Shock & 2018 Verdict",
    }

    acts_data = {i: [] for i in range(1, 6)}
    total_frames_all = 0
    layout_counts = {}
    sfx_counts = {}

    for sc in script["scenes"]:
        s_num = sc["scene"]
        act_num = sc["act"]
        for b_idx, b in enumerate(sc["beats"], 1):
            m = VISUAL_MAP[(s_num, b_idx)]
            audio_name = f"myth_s{s_num:03d}_b{b_idx:02d}.mp3"
            src_audio = MYTH_AUDIO_DIR / audio_name
            pub_audio = REMOTION_AUDIO_DIR / audio_name
            if not src_audio.exists():
                raise FileNotFoundError(f"Missing narration audio: {src_audio}. Run generate_operation_myth_tts.py first!")
            if not pub_audio.exists() or pub_audio.stat().st_size != src_audio.stat().st_size:
                shutil.copy2(src_audio, pub_audio)

            dur = get_audio_duration(src_audio)
            frames = int(round((dur + 0.34) * 30))

            ltype = m["layout"]
            layout_counts[ltype] = layout_counts.get(ltype, 0) + 1
            sfx_p = b.get("sfx", "none")
            sfx_counts[sfx_p] = sfx_counts.get(sfx_p, 0) + 1

            entry = {
                "id": f"s{s_num}_b{b_idx}",
                "durationInFrames": frames,
                "layoutType": ltype,
                "bgImage": stage_to_public(m["bg"]),
                "subjectImage": stage_to_public(m["subj"]) if "subj" in m and m["subj"] else None,
                "labelTitle": b.get("label_title"),
                "labelSubtitle": b.get("label_subtitle"),
                "highlightText": m.get("hi"),
                "highlightStyle": m.get("hstyle", "marker"),
                "stampText": m.get("stxt"),
                "stampSubtext": m.get("ssub"),
                "silhouetteType": m.get("sil"),
                "impactText": b.get("impact_text"),
                "impactFrame": 16,
                "hasBoom": (sfx_p == "boom"),
                "sfxPreset": sfx_p,
                "citation": f"[Act {act_num}, File {s_num:02d}] Archival Citations in Description",
                "audioSrc": f"audio/{audio_name}",
            }
            if ltype == "split_collage":
                entry["splitData"] = {
                    "leftDocument": stage_to_public(m["doc"]),
                    "rightSubject": stage_to_public(m["subj"]),
                    "highlightText": None,
                }
            if ltype == "family_tree" and b.get("tree_data"):
                entry["treeData"] = b["tree_data"]

            acts_data[act_num].append(entry)

    for act_num in range(1, 6):
        beats = acts_data[act_num]
        act_frames = sum(x["durationInFrames"] for x in beats)
        total_frames_all += act_frames
        cfg = {
            "title": f"Operation Myth - {act_names[act_num]}",
            "actNumber": act_num,
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "disableAutoSfx": True,
            "musicSrc": f"audio/myth_act{act_num}_music.mp3",
            "soundtrackActs": [
                {
                    "actId": f"myth_act_{act_num}",
                    "name": act_names[act_num],
                    "src": f"audio/myth_act{act_num}_music.mp3",
                    "startFrame": 0,
                    "durationInFrames": act_frames,
                }
            ],
            "beats": beats,
        }
        out_cfg = REMOTION_SRC_DIR / f"act_{act_num}_config.json"
        out_cfg.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[CONFIG SAVED] {out_cfg.name}: {len(beats)} beats | {act_frames} frames ({act_frames/30/60:.2f} min)")

    print(f"\nTOTAL DOCUMENTARY DURATION: {total_frames_all} frames = {total_frames_all/30/60:.2f} min")
    print(f"Layouts: {layout_counts}")
    print(f"SFX Presets: {sfx_counts}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare-visuals", action="store_true")
    ap.add_argument("--build-configs", action="store_true")
    args = ap.parse_args()
    if args.prepare_visuals:
        prepare_visuals()
    if args.build_configs:
        build_configs()
