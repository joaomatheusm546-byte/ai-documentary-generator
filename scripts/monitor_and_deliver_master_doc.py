import os
import sys
import time
import json
import re
import shutil
import requests
import subprocess
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from src.config import FFMPEG_BIN

RUN_ID = sys.argv[1] if len(sys.argv) > 1 else "43168251630"
OWNER = "joaomatheusm546-byte"
REPO = "ai-documentary-generator"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GDRIVE_FOLDER_ID = "1t6bjqb-waSCWgIkxTChNVwTrnr20TuUW"
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\matuc\.gemini\antigravity\brain\025ce8b1-1553-4f72-aadd-5f42cea3e88c")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def monitor_run():
    print(f"Monitoring Full Documentary 5-Acts Run {RUN_ID} on {OWNER}/{REPO}...")
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{RUN_ID}"
    
    start_time = time.time()
    while True:
        try:
            r = requests.get(url, headers=HEADERS)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                conclusion = data.get("conclusion")
                elapsed_min = (time.time() - start_time) / 60.0
                print(f"[{elapsed_min:.1f}m] Status: {status} | Conclusion: {conclusion}")
                
                if status == "completed":
                    if conclusion == "success":
                        print("\n=== MASTER DOCUMENTARY RUN COMPLETED SUCCESSFULLY! ===")
                        return True
                    else:
                        print(f"\n=== MASTER DOCUMENTARY RUN FAILED with conclusion: {conclusion} ===")
                        return False
            else:
                print(f"Warning: HTTP {r.status_code}")
        except Exception as e:
            print(f"Network error: {e}")
            
        time.sleep(30)

def download_and_deliver():
    tag = f"master-doc-{RUN_ID}"
    rel_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{tag}"
    print(f"Fetching release: {tag}...")
    
    r = requests.get(rel_url, headers=HEADERS)
    video_dest = OUTPUT_DIR / "master_hitler_bloodline_documentary.mp4"
    
    if r.status_code == 200:
        assets = r.json().get("assets", [])
        if assets:
            download_url = assets[0]["browser_download_url"]
            print(f"Downloading from release: {download_url}...")
            subprocess.run(["curl.exe", "-L", "-o", str(video_dest), download_url], check=True)
            
    # Fallback to run artifact
    if not video_dest.exists() or video_dest.stat().st_size < 100000:
        art_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{RUN_ID}/artifacts"
        r_art = requests.get(art_url, headers=HEADERS).json()
        artifacts = r_art.get("artifacts", [])
        if artifacts:
            down_art = artifacts[0]["archive_download_url"]
            print(f"Downloading run artifact from {down_art}...")
            r_redir = requests.get(down_art, headers=HEADERS, allow_redirects=False)
            blob_url = r_redir.headers.get("Location") or down_art
            zip_dest = OUTPUT_DIR / "artifact_master_doc.zip"
            subprocess.run(["curl.exe", "-L", "-o", str(zip_dest), blob_url], check=True)
            import zipfile
            with zipfile.ZipFile(zip_dest) as z:
                z.extractall(OUTPUT_DIR)
            for f in OUTPUT_DIR.rglob("*.mp4"):
                if "master" in f.name.lower() and f != video_dest:
                    shutil.copy(f, video_dest)
                    break

    size_mb = video_dest.stat().st_size / (1024 * 1024)
    print(f"Master Video Secured: {video_dest.name} ({size_mb:.2f} MB)")

    # Copy video to artifacts folder only if disk space allows
    try:
        free_bytes = shutil.disk_usage(str(ARTIFACT_DIR)).free
        if free_bytes > video_dest.stat().st_size * 2:
            shutil.copy(video_dest, ARTIFACT_DIR / "master_hitler_bloodline_documentary.mp4")
            print(f"Copied to artifact directory: {ARTIFACT_DIR / 'master_hitler_bloodline_documentary.mp4'}")
        else:
            print(f"Disk space tight ({free_bytes / (1024*1024):.1f} MB free). Preserving master solely in output/ to avoid disk exhaustion.")
    except Exception as e:
        print(f"Skipping duplicate copy to artifacts folder: {e}")

    # Extract 5 audit frames across the acts
    print("Extracting visual audit frames across 5 acts...")
    timestamps = [
        ("act1_waldviertel", 60),
        ("act2_munich_geli", 220),
        ("act3_william_us_navy", 380),
        ("act4_oss_interrogation", 520),
        ("act5_long_island_pact", 660)
    ]
    for label, sec in timestamps:
        out_jpg = ARTIFACT_DIR / f"master_frame_{label}.jpg"
        cmd = [
            FFMPEG_BIN, "-y", "-ss", str(sec), "-i", str(video_dest),
            "-vframes", "1", "-q:v", "2", str(out_jpg)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if out_jpg.exists():
            print(f"  Audit frame: {out_jpg.name}")

    # Upload to Google Drive via gdrive CLI
    print(f"Uploading to Google Drive folder 'Documentarios AI' ({GDRIVE_FOLDER_ID})...")
    cmd_upload = [
        "gdrive", "mutate", "upload",
        str(video_dest),
        "--parent", GDRIVE_FOLDER_ID
    ]
    res = subprocess.run(cmd_upload, capture_output=True, text=True, check=True, shell=True)
    print(res.stdout.strip())
    
    match = re.search(r'\(ID:\s*([^\)]+)\)', res.stdout)
    if match:
        file_id = match.group(1).strip()
        try:
            subprocess.run(["gdrive", "mutate", "share", file_id, "--role", "reader", "--type", "anyone"], check=True, shell=True)
        except Exception:
            pass
        res_url = subprocess.run(["gdrive", "readonly", "url", file_id], capture_output=True, text=True, check=True, shell=True)
        drive_url = res_url.stdout.strip()
        print(f"\n==========================================")
        print(f"MASTER DOCUMENTARY GOOGLE DRIVE URL: {drive_url}")
        print(f"GOOGLE DRIVE FILE ID: {file_id}")
        print(f"==========================================")

if __name__ == "__main__":
    if monitor_run():
        download_and_deliver()
