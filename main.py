import os
import sys
import time
import shutil
import random
import subprocess
from datetime import datetime
import pytz

from fetch_jobs      import fetch_best_jobs
from generate_image  import generate_card
from post_to_make    import post_job, send_linktree_update, send_whatsapp_alert
from duplicate_check import filter_unique_jobs, mark_as_posted, clean_old_records, log_post

IST = pytz.timezone("Asia/Kolkata")

DAILY_MIX = ["it", "it", "marketing", "finance"]

# Your GitHub Pages base URL — update if your repo name changes
GITHUB_REPO     = os.environ.get("GITHUB_REPOSITORY", "humanresourcegurugram5-svg/delhi-jobs")
GITHUB_USERNAME = GITHUB_REPO.split("/")[0]
GITHUB_REPONAME = GITHUB_REPO.split("/")[1]
PAGES_BASE_URL  = f"https://{GITHUB_USERNAME}.github.io/{GITHUB_REPONAME}"

DOCS_IMAGES_DIR = "docs/images"


def get_post_slot():
    now  = datetime.now(IST)
    hour = now.hour
    if 11 <= hour < 14:
        return 0
    elif 14 <= hour < 17:
        return 1
    elif 17 <= hour < 20:
        return 2
    else:
        return 3


def commit_data():
    try:
        cmds = [
            ["git", "config", "user.email", "bot@delhigurugramjobs.com"],
            ["git", "config", "user.name",  "Delhi Jobs Bot"],
            ["git", "add", "data/"],
            ["git", "add", "docs/"],
            ["git", "commit", "-m",
             f"Site update {datetime.now(IST).strftime('%d %b %Y %H:%M IST')}"],
            ["git", "push"],
        ]
        for cmd in cmds:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 and "nothing to commit" not in result.stdout:
                print(f"Git note: {result.stderr[:100]}")
        print("Data + site committed to GitHub")
    except Exception as e:
        print(f"Git commit error: {e}")


def run():
    now_ist = datetime.now(IST)
    print(f"\n{'='*50}")
    print(f"Delhi Jobs Bot starting")
    print(f"IST time: {now_ist.strftime('%d %b %Y %H:%M:%S')}")
    print(f"{'='*50}\n")

    clean_old_records()

    slot     = get_post_slot()
    category = DAILY_MIX[slot % len(DAILY_MIX)]
    print(f"Post slot: {slot + 1}/4 | Category: {category}")

    # ── Fetch jobs ────────────────────────────────────────────────────────────
    print("\nFetching jobs...")
    raw_jobs = fetch_best_jobs(category, count=12)

    if not raw_jobs:
        msg = f"No jobs fetched at {now_ist.strftime('%H:%M IST')}!"
        print(msg)
        send_whatsapp_alert(f"Job bot alert: {msg}")
        sys.exit(1)

    print(f"Fetched {len(raw_jobs)} raw jobs")

    # ── Deduplicate ───────────────────────────────────────────────────────────
    print("\nFiltering duplicates...")
    unique_jobs = filter_unique_jobs(raw_jobs, needed=1)

    if not unique_jobs:
        print("All jobs are duplicates — using first from fetch")
        unique_jobs = raw_jobs[:1]

    job = unique_jobs[0]
    print(f"\nSelected job : {job['title']} @ {job['company']}")
    print(f"Score        : {job.get('_score', 'n/a')}")
    print(f"Salary       : {job.get('salary') or '(none — smart fallback will apply)'}")

    # ── Generate image ────────────────────────────────────────────────────────
    print("\nGenerating image...")
    image_path = generate_card(job, slot)   # saves to /tmp/job_post_{slot}.jpg

    # ── Copy image into docs/images/ for GitHub Pages ─────────────────────────
    os.makedirs(DOCS_IMAGES_DIR, exist_ok=True)
    img_filename   = f"job_post_{slot}.jpg"
    docs_img_path  = os.path.join(DOCS_IMAGES_DIR, img_filename)
    shutil.copy(image_path, docs_img_path)
    print(f"Image copied to {docs_img_path}")

    # Build the final public URL (will be live after Pages deploys)
    github_pages_url = f"{PAGES_BASE_URL}/images/{img_filename}"
    print(f"Target URL: {github_pages_url}")

    # ── Update website ────────────────────────────────────────────────────────
    print("\nUpdating website...")
    try:
        from build_site import update_site
        update_site([job])
        print("Website updated successfully")
    except Exception as e:
        print(f"Site build error (non-critical): {e}")

    # ── Commit FIRST so GitHub Pages starts deploying ─────────────────────────
    print("\nCommitting to GitHub...")
    commit_data()

    # ── Wait for GitHub Pages to go live ──────────────────────────────────────
    # Pages typically deploys in 60-90 seconds after push
    print("\nWaiting 90 seconds for GitHub Pages to deploy image...")
    time.sleep(90)
    print("Wait complete — image should be live now")

    # ── Post to Instagram via Make.com ────────────────────────────────────────
    print("\nPosting to Instagram...")
    success = post_job(job, github_pages_url, slot)   # pass URL directly

    if success:
        mark_as_posted(job)
        log_post(job, "success")
        print(f"\nPost {slot + 1} successful!")
    else:
        log_post(job, "failed", "make_or_upload_error")
        print(f"\nPost {slot + 1} failed — WhatsApp fallback sent")

    # ── Send Linktree/WhatsApp update on first post of day ────────────────────
    if slot == 0:
        all_jobs = unique_jobs[:4] if len(unique_jobs) >= 4 else unique_jobs
        send_linktree_update(all_jobs)
        print("Linktree update sent")

    # ── Cleanup temp image from /tmp ──────────────────────────────────────────
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            print("Temp image cleaned up")
    except Exception:
        pass

    print(f"\n{'='*50}")
    print(f"Bot run complete — {now_ist.strftime('%H:%M IST')}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()
