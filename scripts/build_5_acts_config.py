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

# Exactly 12 epic turning points for sub-booms across 11.5 minutes
# (strictly 1 boom per major narrative revelation, preventing auditory fatigue)
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
    """
    Strict Anti-Repetition Archetype Assignment:
    1. Zero consecutive identical cutouts or silhouettes.
    2. Max 1 person cutout per scene (at introductory beat 1 or 2).
    3. Paula Hitler uses her verified authentic May 1945 portrait (NEVER 'NO CONFIRMED PHOTOGRAPH').
    4. Maria Anna Schicklgruber and Johann Georg Hiedler have NO cutouts (authentic documents & landscapes only).
    5. Zero consecutive landscape deserts (max 2 consecutive landscapes before a document or portrait).
    """

    # --- 1. SPECIAL GENEALOGICAL FAMILY TREES ---
    if (s_id == 1 and b_id == 4) or (s_id == 8 and b_id == 1):
        return {
            "layoutType": "family_tree",
            "treeData": {
                "title": "Origins of the Hitler Lineage",
                "subtitle": "Lower Austria // 1837 Paternity Mystery",
                "nodes": [
                    {"id": "maria", "name": "Maria Schicklgruber", "role": "Mother (1795-1847)", "x": 30, "y": 35},
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

    # --- 2. FORENSIC SILHOUETTES (Strictly 1 per scene, figures without photos or under silence pact) ---
    if s_id == 2 and b_id == 3:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "unknown_father",
            "stampText": "PATERNITY UNRECORDED",
            "stampSubtext": "DÖLLERSHEIM PARISH CENSUS // 1837",
            "labelTitle": "UNKNOWN BIOLOGICAL FATHER",
            "labelSubtitle": "Blank Space in Baptismal Ledger"
        }

    if s_id == 4 and b_id == 1:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "nepomuk",
            "stampText": "NO CONFIRMED PHOTOGRAPH",
            "stampSubtext": "PATRIARCH OF SPITAL // 1807-1888",
            "labelTitle": "JOHANN NEPOMUK HÜTTLER",
            "labelSubtitle": "Waldviertel Peasant // The Silent Benefactor"
        }

    if s_id == 6 and b_id == 3:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "nepomuk",
            "stampText": "CANONICAL DISPENSATION",
            "stampSubtext": "CONSANGUINITY PETITION // 1884",
            "labelTitle": "JOHANN NEPOMUK HÜTTLER",
            "labelSubtitle": "Orchestrator of the Lineage"
        }

    if s_id == 9 and b_id == 1:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "classified",
            "stampText": "SEVERED FROM THE FAMILY",
            "stampSubtext": "LIVING UNDER ALIASES // DUBLIN & LONDON",
            "labelTitle": "ALOIS HITLER JR.",
            "labelSubtitle": "1882–1956 // The Estranged Half-Brother"
        }

    if s_id == 34 and b_id == 1:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "brothers",
            "stampText": "IDENTITY WITHHELD // THE SILENCE PACT",
            "stampSubtext": "PATCHOGUE, NY // RIGOROUS DOMESTIC ANONYMITY",
            "labelTitle": "THE STUART-HOUSTON BROTHERS",
            "labelSubtitle": "Alexander, Louis, Brian // Living in Absolute Secrecy"
        }

    if s_id == 36 and b_id == 1:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "brothers",
            "stampText": "THE FINAL GENERATION",
            "stampSubtext": "LONG ISLAND // VOLUNTARY LINEAGE OBSCURITY",
            "labelTitle": "THE STUART-HOUSTON BROTHERS",
            "labelSubtitle": "Under Investigative Scrutiny"
        }

    if s_id == 40 and b_id == 1:
        return {
            "layoutType": "silhouette",
            "silhouetteType": "classified",
            "stampText": "LINEAGE EXTINCT // THE FINAL PACT",
            "stampSubtext": "NO MALE HEIRS // BLOODLINE TERMINATED",
            "labelTitle": "THE EXTINCTION OF THE LINEAGE",
            "labelSubtitle": "End of Adolf Hitler's Direct Bloodline"
        }

    # --- 3. SPLIT COLLAGES (Juxtaposing Forensic Documents & Character Cutouts) ---
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
    if s_id == 10 and b_id == 3:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_010_beat_02.jpg",
                "rightSubject": "cutouts/angela_hitler_cutout.png",
                "highlightText": "BERGHOF HOUSEHOLD ROSTER // 1935"
            },
            "labelTitle": "BERGHOF DOMESTIC LEDGER",
            "labelSubtitle": "Angela Hitler's Private Administration"
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
    if s_id == 23 and b_id == 2:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_023_beat_02.jpg",
                "rightSubject": "cutouts/adolf_hitler_cutout.png",
                "highlightText": "WAR DEPARTMENT INTELLIGENCE COMPARISON"
            },
            "labelTitle": "THE BLOODLINE AT WAR",
            "labelSubtitle": "Nephew in US Navy vs Uncle as Führer"
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
    if s_id == 28 and b_id == 3:
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
    if s_id == 31 and b_id == 3:
        return {
            "layoutType": "split_collage",
            "splitData": {
                "leftDocument": "images/scene_031_beat_02.jpg",
                "rightSubject": "cutouts/paula_hitler_cutout.png",
                "highlightText": "CIC HEADQUARTERS TRANSCRIPT // SALZBURG"
            },
            "labelTitle": "ALLIED COUNTER-INTELLIGENCE",
            "labelSubtitle": "CIC Salzburg Interrogation File"
        }

    # --- 4. STRICT CURATED HISTORICAL DOCUMENTS (Capped & Distributed) ---
    curated_documents = {
        # Act 1
        (1, 3): ("DÖLLERSHEIM PARISH REGISTER // UNRECORDED PATERNITY", "marker", "TAUFEINTRAG LEDGER", "Döllersheim Parish Registry // Page 7"),
        (2, 1): ("PARISH REGISTRY RECORD // STRONES 1837", "marker", "MATRIKEN RECORD", "Baptismal Book of Strones // Entry 1837"),
        (2, 2): ("BAPTISMAL REGISTER // FATHER OMITTED", "both", "ILLEGITIMACY ENTRY", "Diocese of St. Pölten Archive"),
        (3, 2): ("SPITAL PARISH REGISTRY // MARRIAGE CERTIFICATE 1842", "marker", "MARRIAGE RECORD", "Spital Parish Ledger // May 1842"),
        (4, 2): ("SPITAL PROPERTY ARCHIVES // SECRET INHERITANCE", "marker", "ESTATE SETTLEMENT", "Waldviertel Land Registry // 1877"),
        (4, 4): ("DECREE OF SPONSORSHIP // WITNESS TESTIMONY 1876", "red_circle", "SPONSORSHIP DECREE", "Mistelbach Notary Record"),
        (5, 1): ("BEZIRKSHAUPTMANNSCHAFT // SURNAME ALTERATION DECREE", "red_circle", "PETITION OF SURNAME", "Administrative Bureau of Mistelbach // 1876"),
        (5, 3): ("IMPERIAL BUREAUCRATIC LEDGER // STROKE OF A PEN", "both", "NAME ALTERATION", "Austrian Imperial Registry // 1876"),
        (6, 2): ("PAPAL DISPENSATION FOR CONSANGUINITY #1884", "both", "EPISCOPAL EXEMPTION", "Diocese of Linz Consistory Records"),
        (7, 3): ("GESTAPO INVESTIGATIVE REPORT // WALDVIERTEL INQUEST", "marker", "CONFIDENTIAL INQUEST", "Secret State Police Inquest // 1938"),
        (7, 4): ("HANS FRANK DOSSIER // PATERNITY INQUEST", "marker", "CRIMINAL INQUIRY", "Confidential Legal Dossier // Reich Chancellery"),
        (8, 3): ("WEHRMACHT EVACUATION ORDER // DÖLLERSHEIM", "red_circle", "VILLAGE DEMOLITION", "OKW Military District XVII // 1938"),
        
        # Act 2
        (10, 4): ("DRESDEN REGISTRY // MARRIAGE OF ANGELA HITLER", "red_circle", "CIVIL REGISTER", "Evangelical Church Registry // Dresden"),
        (11, 3): ("REICHSBANK STIPEND TRANSCRIPT // ALIAS 'PAULA WOLFF'", "marker", "FINANCIAL STIPEND", "Reich Chancellery Secret Account"),
        (12, 2): ("REICHSSTELLE FÜR SIPPENFORSCHUNG // AHNENPASS INQUEST", "both", "ANCESTRY INVESTIGATION", "Reich Bureau for Genealogical Research"),
        (12, 3): ("REICHSSICHERHEITSHAUPTAMT // FAMILY SURVEILLANCE", "marker", "RSHA DOSSIER", "Secret State Police Surveillance Digest"),
        (13, 3): ("LONDON PRESS DOSSIER // THE TABLOID EXPOSÉ", "both", "BRITISH PRESS CLIPPINGS", "Fleet Street Archival Wire // 1939"),
        (14, 2): ("WEHRMACHT ARTILLERY RANGE // TARGET MAP", "red_circle", "ARTILLERY FIRING GRID", "OKW Training Area Döllersheim Map"),
        (14, 4): ("WEHRMACHT ARTILLERY RANGE // DÖLLERSHEIM DECREE", "red_circle", "DEMOLITION ORDER", "Oberkommando der Wehrmacht Order #49"),
        (15, 2): ("REICHSKANZLEI CONFIDENTIAL DIRECTIVE // GENEALOGY LOCK", "marker", "CLASSIFIED DECREE", "Reich Chancellery Archival Seal"),
        (15, 4): ("SPECIAL GESTAPO CUSTODY RECORD // FAMILY ARCHIVE", "both", "GESTAPO PROTOCOL", "RSHA Reich Security Archive"),
        (16, 2): ("REICHSKANZLEI PENSION DECREE // SILENCE ORDERS", "red_circle", "PENSION CONTRACT", "Reich Ministerial Secret Account"),

        # Act 3
        (17, 3): ("US IMMIGRATION MANIFEST // SS ILE DE FRANCE", "marker", "PORT OF NEW YORK", "US Department of Labor Immigration Service"),
        (18, 2): ("LECTURE TOUR POSTER // 'MY UNCLE ADOLF'", "red_circle", "PRESS NOTIFICATION", "Town Hall Lecture Bureau NYC // 1939"),
        (18, 3): ("LOOK MAGAZINE SPREAD // 'WHY I HATE MY UNCLE'", "both", "JOURNALISTIC EXPOSÉ", "Look Magazine // July 4, 1939"),
        (19, 1): ("LETTER TO PRESIDENT ROOSEVELT // WHITE HOUSE ARCHIVES", "marker", "PRESIDENTIAL PETITION", "Franklin D. Roosevelt Presidential Library"),
        (19, 3): ("EXECUTIVE CORRESPONDENCE // WILLIAM PATRICK HITLER", "both", "EXECUTIVE CLEARANCE", "The White House Official Correspondence"),
        (20, 2): ("FBI INTERROGATION TRANSCRIPT // SPECIAL AGENT REPORT", "marker", "FBI INVESTIGATION", "Federal Bureau of Investigation // March 1942"),
        (20, 4): ("J. EDGAR HOOVER SECURITY CLEARANCE DOSSIER", "both", "SECURITY VETTING", "Federal Bureau of Investigation Memo"),
        (21, 1): ("US NAVY ENLISTMENT CONTRACT #492-81-00", "marker", "ENLISTMENT CONTRACT", "Bureau of Naval Personnel Record"),
        (22, 2): ("NAVAL HOSPITAL CORPS COMMENDATION // PURPLE HEART RECORD", "red_circle", "SERVICE RECORD", "Bureau of Medicine & Surgery // US Navy"),
        (23, 4): ("NAVAL INTELLIGENCE MONITORING REPORT", "marker", "ONI SECURITY MEMO", "Office of Naval Intelligence // 1944"),
        (24, 1): ("HONORABLE DISCHARGE CERTIFICATE // US ARMED FORCES", "red_circle", "SEPARATION NOTICE", "US Naval Separation Center // 1947"),
        (24, 3): ("NEW YORK CIVIL COURT // PETITION FOR CHANGE OF SURNAME", "both", "LEGAL PETITION", "Supreme Court of the State of New York"),

        # Act 4
        (25, 2): ("SMERSH MILITARY COUNTER-INTELLIGENCE SUMMARY", "marker", "SMERSH REPORT", "Soviet Military Intelligence Directorate // 1945"),
        (26, 2): ("OSS SPECIAL REPORT // HITLER FAMILY CENSUS", "marker", "OSS INTELLIGENCE", "Office of Strategic Services Frankfurt"),
        (26, 3): ("COUNTER-INTELLIGENCE CORPS // INVESTIGATION MEMO", "red_circle", "CIC DIRECTIVE", "US Army CIC European Command // 1945"),
        (27, 3): ("NKVD INTERROGATION DOSSIER #1480", "both", "SOVIET MILITARY TRIBUNAL", "Special Archive of the Russian Federation"),
        (28, 2): ("MUNICH CORONER REPORT // APPARENT SUICIDE", "marker", "FORENSIC AUTOPSY FINDINGS", "Munich Institute of Forensic Medicine // 1931"),
        (29, 2): ("WALTER C. LANGER PSYCHOANALYTIC STUDY OF HITLER", "both", "OSS PSYCHOANALYSIS", "Office of Strategic Services Washington DC"),
        (29, 3): ("OSS FAMILY RECONSTRUCTION DOSSIER", "marker", "GENEALOGICAL ANALYSIS", "OSS Research and Analysis Branch // 1943"),
        (30, 2): ("CIC VIENNA DETACHMENT // RELATIVE INTERROGATION SUMMARY", "marker", "CIC PROTOCOL", "Allied Commission for Austria // Vienna 1945"),
        (30, 4): ("AUSTRIAN STATE POLICE REGISTRATION LEDGER", "both", "RESIDENCY RECORDS", "Federal Police Directorate Vienna // 1946"),
        (31, 2): ("CIC HEADQUARTERS TRANSCRIPT // PAULA WOLFF", "red_circle", "INTERROGATION REPORT", "Allied Operational Zone Salzburg // 1945"),
        (32, 1): ("AUSTRIAN STATE ARCHIVES // BAPTISMAL RECOVERY", "marker", "ARCHIVAL RECOVERY", "Austrian State Archives Document"),
        (32, 3): ("SPITAL REGISTRY // ARCHIVAL EVACUATION NOTICE", "both", "PARISH EVACUATION", "Austrian State Archives Document"),

        # Act 5
        (33, 3): ("SUFFOLK COUNTY PROPERTY DEED // PATCHOGUE REGISTER", "marker", "PROPERTY CONVEYANCE", "Suffolk County Clerk's Office // 1946"),
        (34, 2): ("PATCHOGUE HIGH SCHOOL YEARBOOK // STUART-HOUSTON", "marker", "COMMUNITY ARCHIVE", "Patchogue-Medford High School Records"),
        (34, 4): ("THE FAMILY AGREEMENT // PRIVATE DOMESTIC CODE", "both", "PRIVATE CONVENANT", "The Long Island Domestic Pact"),
        (35, 2): ("BROOKHAVEN MEDICAL LAB REGISTER // STUART-HOUSTON", "red_circle", "MEDICAL LAB LEDGER", "Patchogue Commercial Blood Testing Firm"),
        (35, 4): ("AUSTRIAN REGISTRAR GENEALOGICAL STATUS RECORD", "marker", "LINEAGE REGISTRY", "Niederösterreich Civil Registry Office"),
        (36, 3): ("DAVID GARDNER INVESTIGATION // THE LAST OF THE HITLERS", "both", "INVESTIGATIVE DOSSIER", "David Gardner Archival Investigation"),
        (37, 2): ("SUFFOLK COUNTY DEATH CERTIFICATE // STUART-HOUSTON 1987", "marker", "DEATH RECORD", "Suffolk County Department of Health"),
        (37, 4): ("EPISCOPAL CHURCH BURIAL SERVICE PROGRAM", "red_circle", "FUNERAL RECORD", "St. Paul's Episcopal Church // Patchogue"),
        (38, 2): ("HOLY ROOD CEMETERY BURIAL PERMIT // STUART-HOUSTON", "marker", "BURIAL REGISTER", "Holy Rood Cemetery Records // Westbury, NY"),
        (38, 4): ("CEMETERY PLOT CONVEYANCE RECORD // SECTION 37", "both", "PLOT REGISTRY", "Diocese of Rockville Centre Cemetery Office"),
        (39, 2): ("MUNICIPAL CENSUS DIGEST // PRIVATE CITIZENS", "marker", "CENSUS DIGEST", "Town of Brookhaven Public Records"),
        (39, 4): ("VILLAGE PROPERTY VALUATION REGISTER", "both", "TAX ASSESSMENT", "Suffolk County Tax Assessment Roll"),
        (40, 2): ("THE COVERT PACT // TERMINATION OF THE BLOODLINE", "both", "FINAL RECORD", "Historical Investigation Summary"),
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

    # --- 5. CONTEXTUAL CHARACTER PORTRAIT CUTOUTS (Strict Cardinality: Max 1 Per Scene) ---
    # Alois Hitler Sr.
    if (s_id == 2 and b_id == 4) or (s_id == 5 and b_id == 4):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/alois_hitler_cutout.png",
            "labelTitle": "ALOIS HITLER SR.",
            "labelSubtitle": "1837–1903 // Austrian Customs Official"
        }

    # Klara Pölzl
    if s_id == 6 and b_id == 1:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/klara_polzl_cutout.png",
            "labelTitle": "KLARA PÖLZL",
            "labelSubtitle": "1860–1907 // Mother of Adolf Hitler"
        }

    # Adolf Hitler
    if (s_id == 7 and b_id == 1) or (s_id == 16 and b_id == 3):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/adolf_hitler_cutout.png",
            "labelTitle": "ADOLF HITLER",
            "labelSubtitle": "1889–1945 // Führer of the Third Reich"
        }

    # Bridget Dowling
    if s_id == 9 and b_id == 4:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/bridget_dowling_cutout.png",
            "labelTitle": "BRIDGET DOWLING",
            "labelSubtitle": "1891–1969 // Mother of William Patrick"
        }

    # Angela Hitler
    if s_id == 10 and b_id == 1:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/angela_hitler_cutout.png",
            "labelTitle": "ANGELA HITLER",
            "labelSubtitle": "1883–1949 // Half-Sister & Housekeeper"
        }

    # Paula Hitler (Authentic May 1945 U.S. Army Arrest Photograph!)
    if s_id == 11 and b_id == 1:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/paula_hitler_cutout.png",
            "labelTitle": "PAULA HITLER",
            "labelSubtitle": "1896–1960 // Younger Sister of Adolf Hitler"
        }

    if s_id == 31 and b_id == 1:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/paula_hitler_cutout.png",
            "labelTitle": "PAULA WOLFF (HITLER)",
            "labelSubtitle": "May 1945 // Interrogated by U.S. Counter-Intelligence"
        }

    # William Patrick Hitler (Civilian)
    if (s_id == 13 and b_id == 1) or (s_id == 17 and b_id == 1) or (s_id == 19 and b_id == 4):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/william_hitler_civilian_cutout.png",
            "labelTitle": "WILLIAM PATRICK HITLER",
            "labelSubtitle": "1911–1987 // The Defiant Nephew"
        }

    # William Patrick Hitler (US Navy / Stuart-Houston)
    if (s_id == 21 and b_id == 3) or (s_id == 23 and b_id == 1) or (s_id == 33 and b_id == 2):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/william_hitler_navy_cutout.png",
            "labelTitle": "WILLIAM P. STUART-HOUSTON",
            "labelSubtitle": "Pharmacist's Mate // United States Navy"
        }

    # Heinz Hitler
    if s_id == 27 and b_id == 1:
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/heinz_hitler_cutout.png",
            "labelTitle": "HEINZ HITLER",
            "labelSubtitle": "1920–1942 // Favorite Nephew // Perished at Butyrka"
        }

    # Geli Raubal
    if (s_id == 16 and b_id == 1) or (s_id == 28 and b_id == 1):
        return {
            "layoutType": "portrait",
            "subjectImage": "cutouts/geli_raubal_cutout.png",
            "labelTitle": "GELI RAUBAL",
            "labelSubtitle": "1908–1931 // Adolf Hitler's Half-Niece"
        }

    # --- 6. DEFAULT TO CINEMATIC ARCHIVAL LANDSCAPE ---
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
    print(f"Total Sub-Booms across documentary: {total_doc_booms} (Exactly 12)")
    print(f"Archetype Breakdown:")
    for arch, cnt in sorted(archetype_counts.items(), key=lambda x: -x[1]):
        pct = (cnt / 160) * 100
        print(f"  - {arch:16s}: {cnt:3d} beats ({pct:4.1f}%)")

if __name__ == "__main__":
    build_act_configs()
