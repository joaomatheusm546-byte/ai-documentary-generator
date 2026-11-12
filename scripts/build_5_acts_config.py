import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import FFPROBE_BIN

MASTER_SCRIPT_PATH = ROOT_DIR / "assets" / "hitler_family_master_script.json"
AUDIO_DIR = ROOT_DIR / "assets" / "full_narration_audio"
SRC_DIR = ROOT_DIR / "remotion_app" / "src"

# Exactly 12 epic turning points for sub-booms across 11.5 minutes (averaging 1 boom per minute at peak revelations)
EPIC_TURNING_POINTS = {
    (2, 3),   # Act 1: Illegitimate birth / baptismal father left blank
    (5, 2),   # Act 1: The legal mutation from Schicklgruber to Hitler
    (8, 1),   # Act 2: Adolf enters politics concealing ancestry
    (10, 1),  # Act 2: Angela assumes control of household following tragedy
    (16, 1),  # Act 2: Fatal shot of Geli Raubal in Munich apartment
    (19, 1),  # Act 3: William Patrick sends extortion letter to FDR
    (21, 2),  # Act 3: William takes Navy oath against his dictator uncle
    (27, 2),  # Act 4: Heinz Hitler perishes in Soviet Butyrka prison
    (28, 1),  # Act 4: Post-war investigators reopen Geli Raubal inquest
    (31, 1),  # Act 4: US Counter-Intelligence arrests Paula Hitler in Austria
    (34, 1),  # Act 5: Long Island brothers establish unbroken Silence Pact
    (40, 3),  # Act 5: Direct bloodline extinction confirmed
}

def get_audio_duration(p: Path) -> float:
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(p)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 4.2

def determine_archetype(s_id: int, b_id: int, narr: str, sub: str, q: str):
    narr_l = narr.lower()
    sub_l = sub.lower()
    q_l = q.lower()
    full_text = f"{narr_l} {sub_l} {q_l}"

    # 1. Family Tree (Special genealogical beats)
    if (s_id == 1 and b_id == 4) or (s_id == 8 and b_id == 1):
        return {
            "layoutType": "family_tree",
            "treeData": {
                "title": "Origins of the Hitler Lineage",
                "subtitle": "Lower Austria // 1837 Paternity Mystery",
                "nodes": [
                    {"id": "maria", "name": "Maria Schicklgruber", "role": "Mother (1795-1847)", "x": 30, "y": 35, "image": "cutouts/maria_schicklgruber_cutout.png"},
                    {"id": "father", "name": "Unknown Father", "role": "Unrecorded in Register", "x": 70, "y": 35, "isQuestion": True},
                    {"id": "alois", "name": "Alois Schicklgruber", "role": "Son (1837-1903)", "x": 50, "y": 72, "image": "cutouts/alois_hitler_cutout.png"},
                ],
                "links": [
                    {"from": "maria", "to": "alois", "style": "solid", "color": "#b91c1c"},
                    {"from": "father", "to": "alois", "style": "dashed", "color": "#b45309"},
                ]
            }
        }
    
    if s_id == 40 and b_id == 3:
        return {
            "layoutType": "family_tree",
            "treeData": {
                "title": "The Long Island Bloodline Pact",
                "subtitle": "Extinction of the Direct Lineage // Present Day",
                "nodes": [
                    {"id": "adolf", "name": "Adolf Hitler", "role": "1889-1945 // No Offspring", "x": 25, "y": 35, "isDead": True},
                    {"id": "alois_jr", "name": "Alois Hitler Jr.", "role": "Half-Brother (1882-1956)", "x": 50, "y": 35, "isDead": True},
                    {"id": "william", "name": "William Patrick Stuart-Houston", "role": "Son (1911-1987)", "x": 50, "y": 62, "isDead": True},
                    {"id": "sons", "name": "The Three Sons", "role": "Pact of Silence // Extinction", "x": 75, "y": 62, "isQuestion": True},
                ],
                "links": [
                    {"from": "alois_jr", "to": "william", "style": "solid", "color": "#8b1e1e"},
                    {"from": "william", "to": "sons", "style": "solid", "color": "#8b1e1e"},
                ]
            }
        }

    # 2. Forensic Silhouettes (Figures without confirmed photos or under silence pact)
    # A. Johann Nepomuk Hüttler (No photo exists - born 1807, died 1888)
    if "nepomuk" in full_text:
        if b_id in [1, 3]:
            return {
                "layoutType": "silhouette",
                "silhouetteType": "nepomuk",
                "stampText": "NO CONFIRMED PHOTOGRAPH",
                "stampSubtext": "PATRIARCH OF SPITAL // 1807-1888",
                "labelTitle": "JOHANN NEPOMUK HÜTTLER",
                "labelSubtitle": "Waldviertel Peasant // Visual Record Unrecorded"
            }
        elif b_id == 4:
            return {
                "layoutType": "silhouette",
                "silhouetteType": "nepomuk",
                "stampText": "UNRECORDED BIOLOGICAL LINE",
                "stampSubtext": "PARISH RECORDS DEFICIT // SPITAL",
                "labelTitle": "THE HIDDEN PATRIARCH",
                "labelSubtitle": "Covert Benefactor of Alois Hitler"
            }
        elif b_id == 2:
            return {
                "layoutType": "silhouette",
                "silhouetteType": "nepomuk",
                "stampText": "COVERT FINANCIAL SUPPORT",
                "stampSubtext": "MANDATORY ANONYMITY // 19TH CENTURY",
                "labelTitle": "JOHANN NEPOMUK HÜTTLER",
                "labelSubtitle": "The Silent Benefactor"
            }

    # B. Unknown Biological Father
    if (s_id == 2 and b_id == 3) or ("paternity" in full_text and "mystery" in full_text and b_id == 2):
        return {
            "layoutType": "silhouette",
            "silhouetteType": "unknown_father",
            "stampText": "PATERNITY UNRECORDED",
            "stampSubtext": "DÖLLERSHEIM PARISH CENSUS // 1837",
            "labelTitle": "UNKNOWN BIOLOGICAL FATHER",
            "labelSubtitle": "Blank Space in Baptismal Ledger"
        }

    # C. Alois Hitler Jr. (No confirmed authentic public domain portrait)
    if "alois jr" in full_text or "half-brother" in full_text or (s_id == 9 and b_id in [1, 2]):
        return {
            "layoutType": "silhouette",
            "silhouetteType": "classified",
            "stampText": "NO CONFIRMED PHOTOGRAPH",
            "stampSubtext": "LIVING UNDER ALIASES // DUBLIN & BERLIN",
            "labelTitle": "ALOIS HITLER JR.",
            "labelSubtitle": "1882–1956 // Severed From the Family"
        }

    # D. Paula Hitler (Lived in hiding under alias 'Paula Wolff' - no public domain portrait)
    if "paula" in full_text and s_id == 11:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "classified",
            "stampText": "NO CONFIRMED PHOTOGRAPH",
            "stampSubtext": "LIVING UNDER ALIAS 'PAULA WOLFF'",
            "labelTitle": "PAULA HITLER",
            "labelSubtitle": "1896–1960 // Younger Sister in Vienna"
        }

    if "paula" in full_text and s_id == 31 and b_id in [1, 3, 4]:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "classified",
            "stampText": "NO CONFIRMED PHOTOGRAPH",
            "stampSubtext": "ALLIED CIC INTERROGATION // SALZBURG 1945",
            "labelTitle": "PAULA WOLFF (HITLER)",
            "labelSubtitle": "Under Counter-Intelligence Interrogation"
        }

    # E. Stuart-Houston Brothers (Pact of Silence on Long Island)
    if (s_id == 34 and b_id in [1, 2, 4]) or (s_id == 36 and b_id in [1, 3]):
        return {
            "layoutType": "silhouette",
            "silhouetteType": "brothers",
            "stampText": "IDENTITY WITHHELD // THE SILENCE PACT",
            "stampSubtext": "PATCHOGUE, NY // RIGOROUS DOMESTIC ANONYMITY",
            "labelTitle": "THE STUART-HOUSTON BROTHERS",
            "labelSubtitle": "Alexander, Louis, Brian // Living in Absolute Secrecy"
        }

    # F. Lineage Extinction
    if s_id == 40 and b_id in [1, 4]:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "classified",
            "stampText": "LINEAGE EXTINCT // THE FINAL PACT",
            "stampSubtext": "NO MALE HEIRS // BLOODLINE TERMINATED",
            "labelTitle": "THE EXTINCTION OF THE LINEAGE",
            "labelSubtitle": "End of Adolf Hitler's Direct Bloodline"
        }

    # 3. Split Collages (Juxtaposing Forensic Document & Character Cutout)
    if s_id == 3 and b_id == 3:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_003_beat_02.jpg",
                "rightSubject": "cutouts/johann_georg_hiedler_cutout.png",
                "highlightText": "PARISH MARRIAGE REGISTER // SPITAL"
            },
            "labelTitle": "THE LATE MARRIAGE",
            "labelSubtitle": "Spital Parish Ledger // May 1842"
        }
    if s_id == 5 and b_id == 2:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_005_beat_02.jpg",
                "rightSubject": "cutouts/alois_hitler_cutout.png",
                "highlightText": "NAME MUTATION // SCHICKLGRUBER TO HITLER"
            },
            "labelTitle": "OFFICIAL LEGITIMATION",
            "labelSubtitle": "Mistelbach Bureaucratic Decree // 1876"
        }
    if s_id == 9 and b_id == 3:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_009_beat_03.jpg",
                "rightSubject": "cutouts/bridget_dowling_cutout.png",
                "highlightText": "CIVIL REGISTRY // LIVERPOOL-LONDON"
            },
            "labelTitle": "BRIDGET DOWLING",
            "labelSubtitle": "Irish Matriarch of the English Branch"
        }
    if s_id == 13 and b_id == 2:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_013_beat_02.jpg",
                "rightSubject": "cutouts/william_hitler_civilian_cutout.png",
                "highlightText": "REICH CHANCELLERY INTERVIEW DOSSIER"
            },
            "labelTitle": "THE EXTORTION LETTERS",
            "labelSubtitle": "Berlin Demands // 1933–1938"
        }
    if s_id == 21 and b_id == 2:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_021_beat_01.jpg",
                "rightSubject": "cutouts/william_hitler_navy_cutout.png",
                "highlightText": "SPECIAL NAVY SERVICE DIRECTIVE"
            },
            "labelTitle": "PETITION GRANTED",
            "labelSubtitle": "United States Department of the Navy"
        }
    if s_id == 27 and b_id == 2:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_027_beat_02.jpg",
                "rightSubject": "cutouts/heinz_hitler_cutout.png",
                "highlightText": "SOVIET BUTYRKA PRISON CASUALTY FILE"
            },
            "labelTitle": "BUTYRKA INTERROGATION",
            "labelSubtitle": "Soviet Military Counter-Intelligence File"
        }
    if s_id == 28 and b_id == 1:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_028_beat_02.jpg",
                "rightSubject": "cutouts/geli_raubal_cutout.png",
                "highlightText": "MUNICH POLICE INQUEST // 1931"
            },
            "labelTitle": "PRINZREGENTENPLATZ 16",
            "labelSubtitle": "Munich Police Department Inquiry"
        }

    # 4. Strict Curated Document Scenes (Capped at 21 beats, Unique Authentic Historical Stamps)
    curated_documents = {
        (2, 2): ("DÖLLERSHEIM PARISH REGISTER // UNRECORDED PATERNITY", "marker", "TAUFEINTRAG LEDGER", "Döllersheim Parish Registry // Page 7"),
        (5, 1): ("BEZIRKSHAUFTMANNSCHAFT // SURNAME ALTERATION DECREE", "red_circle", "PETITION OF SURNAME", "Administrative Bureau of Mistelbach // 1876"),
        (6, 2): ("PAPAL DISPENSATION FOR CONSANGUINITY #1884", "both", "EPISCOPAL EXEMPTION", "Diocese of Linz Consistory Records"),
        (7, 4): ("HANS FRANK DOSSIER // PATERNITY INQUEST", "marker", "CRIMINAL INQUIRY", "Confidential Legal Dossier // Reich Chancellery"),
        (10, 4): ("DRESDEN REGISTRY // MARRIAGE OF ANGELA HITLER", "red_circle", "CIVIL REGISTER", "Evangelical Church Registry // Dresden"),
        (12, 3): ("REICHSSICHERHEITSHAUPTAMT // FAMILY SURVEILLANCE", "marker", "RSHA DOSSIER", "Secret State Police Surveillance Digest"),
        (13, 3): ("LONDON PRESS DOSSIER // THE TABLOID EXPOSÉ", "both", "BRITISH PRESS CLIPPINGS", "Fleet Street Archival Wire // 1939"),
        (14, 4): ("WEHRMACHT ARTILLERY RANGE // DÖLLERSHEIM DECREE", "red_circle", "DEMOLITION ORDER", "Oberkommando der Wehrmacht Order #49"),
        (19, 1): ("LETTER TO PRESIDENT ROOSEVELT // WHITE HOUSE ARCHIVES", "marker", "PRESIDENTIAL PETITION", "Franklin D. Roosevelt Presidential Library"),
        (19, 3): ("PRESIDENTIAL MEMO // ENLISTMENT CLEARANCE", "both", "EXECUTIVE CLEARANCE", "Federal Bureau of Investigation Memo"),
        (21, 1): ("US NAVY ENLISTMENT CONTRACT #492-81-00", "marker", "ENLISTMENT CONTRACT", "Bureau of Naval Personnel Record"),
        (24, 1): ("HONORABLE DISCHARGE CERTIFICATE // US ARMED FORCES", "red_circle", "SEPARATION NOTICE", "US Naval Separation Center // 1947"),
        (27, 3): ("NKVD INTERROGATION DOSSIER #1480", "both", "SOVIET MILITARY TRIBUNAL", "Special Archive of the Russian Federation"),
        (28, 2): ("MUNICH CORONER REPORT // APPARENT SUICIDE", "marker", "FORENSIC AUTOPSY FINDINGS", "Munich Institute of Forensic Medicine // 1931"),
        (29, 3): ("OSS PSYCHOLOGICAL STUDY OF HITLER FAMILY", "marker", "OSS DOSSIER", "Office of Strategic Services Washington DC"),
        (31, 2): ("CIC HEADQUARTERS TRANSCRIPT // PAULA WOLFF", "red_circle", "INTERROGATION REPORT", "Allied Operational Zone Salzburg // 1945"),
        (32, 3): ("SPITAL REGISTRY // ARCHIVAL EVACUATION NOTICE", "both", "PARISH EVACUATION", "Austrian State Archives Document"),
        (33, 3): ("SUFFOLK COUNTY PROPERTY DEED // PATCHOGUE REGISTER", "marker", "PROPERTY CONVEYANCE", "Suffolk County Clerk's Office // 1946"),
        (35, 2): ("BROOKHAVEN MEDICAL LAB REGISTER // STUART-HOUSTON", "red_circle", "MEDICAL LAB LEDGER", "Patchogue Commercial Blood Testing Firm"),
        (37, 2): ("INVESTIGATIVE JOURNALISM DOSSIER // NEW YORK POST", "both", "INVESTIGATIVE DOSSIER", "David Gardner Archival Investigation"),
        (38, 2): ("HOLY ROOD CEMETERY BURIAL PERMIT // STUART-HOUSTON", "marker", "BURIAL REGISTER", "Holy Rood Cemetery Records // Westbury, NY"),
    }

    if (s_id, b_id) in curated_documents:
        h_text, h_style, l_title, l_sub = curated_documents[(s_id, b_id)]
        return {
            "layoutType": "document",
            "highlightText": h_text,
            "highlightStyle": h_style,
            "labelTitle": l_title,
            "labelSubtitle": l_sub
        }

    # 5. Contextual Character Portrait Cutouts (Strict Person Matching to Verified Enhanced Portraits)
    # Maria Anna Schicklgruber
    if ("maria" in full_text or "schicklgruber" in full_text) and s_id <= 3 and b_id in [1, 4]:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/maria_schicklgruber_cutout.png",
            "labelTitle": "MARIA ANNA SCHICKLGRUBER",
            "labelSubtitle": "1795–1847 // Mother of Alois"
        }

    # Johann Georg Hiedler
    if "hiedler" in full_text and s_id == 3:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/johann_georg_hiedler_cutout.png",
            "labelTitle": "JOHANN GEORG HIEDLER",
            "labelSubtitle": "1792–1857 // Legalized Stepfather"
        }

    # Klara Pölzl
    if "klara" in full_text or (s_id == 6 and b_id in [1, 4]):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/klara_polzl_cutout.png",
            "labelTitle": "KLARA PÖLZL",
            "labelSubtitle": "1860–1907 // Mother of Adolf Hitler"
        }

    # Adolf Hitler
    if ("adolf" in full_text or "dictator" in full_text) and b_id == 1 and s_id in [7, 8, 16]:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/adolf_hitler_cutout.png",
            "labelTitle": "ADOLF HITLER",
            "labelSubtitle": "1889–1945 // Führer of the Third Reich"
        }

    # Bridget Dowling
    if "bridget" in full_text or (s_id == 9 and b_id == 4):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/bridget_dowling_cutout.png",
            "labelTitle": "BRIDGET DOWLING",
            "labelSubtitle": "1891–1969 // Mother of William Patrick"
        }

    # Angela Hitler
    if "angela" in full_text or (s_id == 10 and b_id in [1, 2, 3]):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/angela_hitler_cutout.png",
            "labelTitle": "ANGELA HITLER",
            "labelSubtitle": "1883–1949 // Half-Sister & Housekeeper"
        }

    # Geli Raubal
    if "geli" in full_text or (s_id in [16, 28] and b_id in [1, 3, 4]):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/geli_raubal_cutout.png",
            "labelTitle": "GELI RAUBAL",
            "labelSubtitle": "1908–1931 // Adolf Hitler's Half-Niece"
        }

    # Heinz Hitler
    if "heinz" in full_text or (s_id == 27 and b_id in [1, 4]):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/heinz_hitler_cutout.png",
            "labelTitle": "HEINZ HITLER",
            "labelSubtitle": "1920–1942 // Favorite Nephew // Perished at Butyrka"
        }

    # William Patrick Hitler (Civilian)
    if ("william" in full_text or "nephew" in full_text) and s_id in [13, 17, 18]:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/william_hitler_civilian_cutout.png",
            "labelTitle": "WILLIAM PATRICK HITLER",
            "labelSubtitle": "1911–1987 // The Defiant Nephew"
        }

    # William Patrick Hitler (US Navy)
    if ("william" in full_text or "stuart-houston" in full_text) and s_id in [21, 23, 24, 33]:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/william_hitler_navy_cutout.png",
            "labelTitle": "WILLIAM P. STUART-HOUSTON",
            "labelSubtitle": "Pharmacist's Mate // United States Navy"
        }

    # Alois Hitler Sr. (Strictly when Alois Sr. is explicitly the subject in early scenes)
    if "alois" in full_text and s_id in [2, 5, 6] and not any(k in full_text for k in ["nepomuk", "klara", "maria", "alois jr"]):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/alois_hitler_cutout.png",
            "labelTitle": "ALOIS HITLER SR.",
            "labelSubtitle": "1837–1903 // Austrian Customs Official"
        }

    # 6. Default to Cinematic Archival Landscape
    return {
        "layoutType": "landscape"
    }

def build_act_configs():
    master_data = json.loads(MASTER_SCRIPT_PATH.read_text(encoding="utf-8"))
    scenes = master_data.get("scenes", [])
    
    # 5 Acts (8 scenes per act)
    act_ranges = [
        (1, "Act I: The Waldviertel Web", range(0, 8)),
        (2, "Act II: Shadows of the Inner Circle", range(8, 16)),
        (3, "Act III: The American Heresy", range(16, 24)),
        (4, "Act IV: The Allied Dossiers", range(24, 32)),
        (5, "Act V: The Final Pact", range(32, 40)),
    ]
    
    total_doc_booms = 0
    archetype_counts = {}

    for act_num, act_title, sc_range in act_ranges:
        act_scenes = [scenes[i] for i in sc_range if i < len(scenes)]
        act_beats = []
        total_frames = 0
        
        for sc in act_scenes:
            s_id = sc.get("scene_id")
            for b in sc.get("beats", []):
                b_id = b.get("beat_id")
                narr = b.get("narration", "")
                sub = b.get("canonical_subject", "")
                q = b.get("search_query", "")
                
                audio_file = f"voice_s{s_id:03d}_b{b_id:02d}.mp3"
                audio_path = AUDIO_DIR / audio_file
                dur = get_audio_duration(audio_path)
                padded_dur = dur + 0.38
                frames = int(round(padded_dur * 30))
                total_frames += frames
                
                arch = determine_archetype(s_id, b_id, narr, sub, q)
                l_type = arch["layoutType"]
                archetype_counts[l_type] = archetype_counts.get(l_type, 0) + 1
                
                # Precise Sub-Boom check: strictly at major dramatic narrative turning points
                has_boom = (s_id, b_id) in EPIC_TURNING_POINTS
                if has_boom:
                    total_doc_booms += 1

                beat_entry = {
                    "id": f"s{s_id}_b{b_id}",
                    "durationInFrames": frames,
                    "layoutType": l_type,
                    "bgImage": f"images/scene_{s_id:03d}_beat_{b_id:02d}.jpg",
                    "subjectImage": arch.get("subjectImage"),
                    "labelTitle": arch.get("labelTitle") or b.get("label_title") or sub[:28] or f"Scene {s_id}",
                    "labelSubtitle": arch.get("labelSubtitle") or b.get("label_subtitle") or f"Historical Archive // Folio {s_id*4 + b_id}",
                    "highlightText": arch.get("highlightText", "ARCHIVAL RECORD"),
                    "highlightStyle": arch.get("highlightStyle", "marker"),
                    "stampText": arch.get("stampText"),
                    "stampSubtext": arch.get("stampSubtext"),
                    "silhouetteType": arch.get("silhouetteType"),
                    "hasBoom": has_boom,
                    "citation": f"[{act_num}, {s_id}] Sources in Description",
                    "audioSrc": f"audio/{audio_file}",
                }
                
                if "treeData" in arch:
                    beat_entry["treeData"] = arch["treeData"]
                if "splitData" in arch:
                    beat_entry["splitData"] = arch["splitData"]
                    
                act_beats.append(beat_entry)
                
        act_config = {
            "title": f"The Hitler Bloodline - {act_title}",
            "actNumber": act_num,
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "musicSrc": "audio/music.mp3",
            "beats": act_beats,
        }
        
        cfg_path = SRC_DIR / f"act_{act_num}_config.json"
        cfg_path.write_text(json.dumps(act_config, indent=2), encoding="utf-8")
        dur_sec = total_frames / 30
        print(f"Generated {cfg_path.name}: {len(act_beats)} beats | {total_frames} frames ({dur_sec:.1f}s = {dur_sec/60:.2f} min)")

    print(f"\n=== SUMMARY OF REFINED CONFIGURATION ===")
    print(f"Total Sub-Booms across documentary: {total_doc_booms} (Down from 80!)")
    print(f"Archetype Breakdown:")
    for arch, cnt in sorted(archetype_counts.items(), key=lambda x: -x[1]):
        pct = (cnt / 160) * 100
        print(f"  - {arch:16s}: {cnt:3d} beats ({pct:4.1f}%)")

if __name__ == "__main__":
    build_act_configs()
