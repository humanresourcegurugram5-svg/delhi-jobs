import os
import json
import re
from datetime import datetime

DATA_DIR = "data"

def load_json(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_job_id(job):
    title   = re.sub(r'[^a-z0-9]', '_', job.get("title", "").lower())
    company = re.sub(r'[^a-z0-9]', '_', job.get("company", "").lower())
    title   = re.sub(r'_+', '_', title).strip('_')[:30]
    company = re.sub(r'_+', '_', company).strip('_')[:20]
    return f"{company}__{title}"

def is_duplicate(job, days_threshold=14):
    posted = load_json("posted_jobs.json", {})
    job_id = create_job_id(job)

    if job_id not in posted:
        return False

    posted_on = datetime.fromisoformat(posted[job_id]["posted_on"])
    days_ago = (datetime.now() - posted_on).days

    if days_ago < days_threshold:
        print(f"Duplicate: {job['title']} posted {days_ago} days ago")
        return True

    print(f"Repost OK: {job['title']} last posted {days_ago} days ago")
    return False

def mark_as_posted(job):
    posted = load_json("posted_jobs.json", {})
    job_id = create_job_id(job)

    posted[job_id] = {
        "title":     job.get("title", ""),
        "company":   job.get("company", ""),
        "posted_on": datetime.now().isoformat(),
        "source":    job.get("source", "unknown"),
    }
    save_json("posted_jobs.json", posted)
    print(f"Marked as posted: {job['title']}")

def clean_old_records():
    posted = load_json("posted_jobs.json", {})
    now = datetime.now()
    cleaned = 0

    for job_id in list(posted.keys()):
        try:
            posted_on = datetime.fromisoformat(posted[job_id]["posted_on"])
            days_old = (now - posted_on).days
            if days_old > 30:
                del posted[job_id]
                cleaned += 1
        except:
            del posted[job_id]
            cleaned += 1

    save_json("posted_jobs.json", posted)
    if cleaned:
        print(f"Cleaned {cleaned} old records")

def filter_unique_jobs(jobs, needed=4):
    unique = []
    for job in jobs:
        if not is_duplicate(job):
            unique.append(job)
        if len(unique) >= needed * 3:
            break
    print(f"Unique jobs found: {len(unique)}")
    return unique

def log_post(job, status, error=None):
    log = load_json("post_log.json", [])
    log.append({
        "timestamp": datetime.now().isoformat(),
        "job_title": job.get("title", ""),
        "company":   job.get("company", ""),
        "status":    status,
        "error":     error or "none",
    })
    log = log[-500:]
    save_json("post_log.json", log)

if __name__ == "__main__":
    clean_old_records()
    print("Duplicate check module ready")
