import json
from pathlib import Path

# Load master script and configs
master = json.loads(Path("assets/hitler_family_master_script.json").read_text(encoding="utf-8"))
scenes = {s["scene_id"]: s for s in master["scenes"]}

configs = {}
for a in range(1, 6):
    configs[a] = json.loads(Path(f"remotion_app/src/act_{a}_config.json").read_text(encoding="utf-8"))

print("=== DEEP FORENSIC BREAKDOWN ACROSS ALL 40 SCENES ===")

for a in range(1, 6):
    cfg = configs[a]
    print(f"\n=======================================================")
    print(f" ACT {a}: {cfg['title']}")
    print(f"=======================================================")
    
    # Track repetitions within the act
    seen_subjects = []
    seen_layouts = []
    
    for b in cfg["beats"]:
        b_id = b["id"]
        lt = b.get("layoutType")
        subj = b.get("subjectImage")
        silh = b.get("silhouetteType")
        bg = b.get("bgImage")
        lbl = b.get("labelTitle")
        
        # Check consecutive identical layout
        is_repetitive = False
        reasons = []
        
        if subj:
            if seen_subjects and seen_subjects[-1] == subj:
                reasons.append(f"CONSECUTIVE SAME CUTOUT: {subj}")
            seen_subjects.append(subj)
        else:
            seen_subjects.append(None)
            
        if silh:
            if len(seen_layouts) >= 1 and seen_layouts[-1] == ("silhouette", silh):
                reasons.append(f"CONSECUTIVE SAME SILHOUETTE: {silh}")
            seen_layouts.append(("silhouette", silh))
        else:
            seen_layouts.append((lt, None))
            
        # Check runs of landscape
        recent_layouts = [x[0] for x in seen_layouts[-4:]]
        if len(recent_layouts) == 4 and all(x == "landscape" for x in recent_layouts):
            reasons.append("4 CONSECUTIVE GENERIC LANDSCAPES")
            
        flag = " [!] FLAW: " + "; ".join(reasons) if reasons else ""
        print(f"  {b_id:<7} | {lt:<13} | subj: {str(subj):<35} | silh: {str(silh):<10}{flag}")
