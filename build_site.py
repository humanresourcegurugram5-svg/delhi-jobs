"""
build_site.py  —  generates docs/index.html and docs/archive.html
Called automatically by main.py after every post run.
GitHub Pages serves these files at:
  https://YOUR_USERNAME.github.io/delhi-jobs/
"""
import os
import json
import subprocess
from datetime import datetime
import pytz

DATA_DIR = "data"
DOCS_DIR = "docs"
IST      = pytz.timezone("Asia/Kolkata")

def load_json(path, default):
    if not os.path.exists(path): return default
    try:
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except: return default

def save_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w",encoding="utf-8") as f: f.write(content)

def now_ist():
    return datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")

# ── HTML helpers ──────────────────────────────────────────────────────────────

CSS = """
:root{--bg:#fdf6ee;--card:#fff8f0;--dark:#2c1f0e;--mid:#6b4f2e;
      --accent:#b49060;--border:#e8ddd0;--green:#15803d;--tag:#f0fdf4}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:var(--bg);color:var(--dark);min-height:100vh}
.header{text-align:center;padding:40px 20px 24px;border-bottom:1px solid var(--border)}
.header h1{font-size:26px;font-weight:800;letter-spacing:-0.5px}
.header p{font-size:13px;color:var(--accent);margin-top:6px}
.updated{display:inline-block;background:var(--tag);color:var(--green);
         font-size:11px;font-weight:600;padding:3px 12px;border-radius:20px;margin-top:10px}
.container{max-width:520px;margin:0 auto;padding:24px 16px}
.section-title{font-size:11px;font-weight:700;letter-spacing:2px;
               color:var(--accent);margin:24px 0 12px;text-transform:uppercase}
.job-card{background:var(--card);border:1px solid var(--border);
          border-radius:14px;padding:20px;margin-bottom:12px}
.job-card:hover{border-color:var(--accent)}
.job-title{font-size:18px;font-weight:800;color:var(--dark);
           line-height:1.2;margin-bottom:4px}
.job-company{font-size:13px;color:var(--mid);margin-bottom:12px}
.job-meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.meta-pill{font-size:11px;color:var(--accent);background:var(--bg);
           border:1px solid var(--border);padding:3px 10px;border-radius:20px}
.meta-pill.salary{background:#fef9c3;color:#854d0e;border-color:#fde68a}
.apply-btn{display:block;width:100%;padding:13px;background:var(--dark);
           color:var(--bg);text-align:center;border-radius:10px;
           text-decoration:none;font-size:13px;font-weight:700;
           letter-spacing:0.5px}
.apply-btn:hover{background:var(--mid)}
.no-link{background:#e8ddd0;color:var(--mid);cursor:default}
.archive-row{display:flex;justify-content:space-between;align-items:center;
             padding:10px 0;border-bottom:1px solid var(--border);
             font-size:13px;color:var(--dark)}
.archive-row:last-child{border-bottom:none}
.archive-date{font-size:11px;color:var(--accent);min-width:80px;text-align:right}
.archive-link{color:var(--dark);text-decoration:none;font-weight:500}
.archive-link:hover{color:var(--mid)}
.footer{text-align:center;padding:32px 16px;font-size:12px;color:var(--accent)}
.nav-btn{display:inline-block;margin:4px;padding:8px 18px;
         border-radius:20px;border:1px solid var(--border);
         background:transparent;color:var(--mid);font-size:12px;
         text-decoration:none;font-weight:500}
.nav-btn:hover{background:var(--border)}
"""

def job_card_html(job, show_apply=True):
    title   = job.get("title","Job Opening")
    company = job.get("company","")
    loc     = job.get("location","Delhi / Gurugram")
    salary  = job.get("salary","")
    exp     = job.get("experience","")
    link    = job.get("link","")
    sal_class = "salary" if salary else ""
    sal_text  = salary if salary else "Salary on application"
    apply_html = ""
    if show_apply:
        if link:
            apply_html = f'<a href="{link}" class="apply-btn" target="_blank" rel="noopener">Apply Now  →</a>'
        else:
            apply_html = '<span class="apply-btn no-link">Check company website</span>'
    return f"""
<div class="job-card">
  <div class="job-title">{title}</div>
  <div class="job-company">{company}</div>
  <div class="job-meta">
    <span class="meta-pill">📍 {loc}</span>
    <span class="meta-pill {sal_class}">💰 {sal_text}</span>
    {"<span class='meta-pill'>🕐 " + exp + "</span>" if exp else ""}
  </div>
  {apply_html}
</div>"""

def build_index(todays_jobs):
    now = now_ist()
    cards = "".join(job_card_html(j) for j in todays_jobs)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Fresh Delhi & Gurugram job alerts — updated daily">
<title>Delhi Gurugram Jobs — Today's Openings</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
  <h1>Delhi &amp; Gurugram Jobs</h1>
  <p>4 fresh jobs posted daily · Follow us on Instagram</p>
  <div class="updated">Updated {now}</div>
</div>
<div class="container">
  <div class="section-title">Today's Openings</div>
  {cards if cards else '<p style="color:var(--accent);font-size:13px">New jobs posting soon — check back shortly!</p>'}
  <div style="text-align:center;margin-top:20px">
    <a href="archive.html" class="nav-btn">📁 View All Past Jobs</a>
    <a href="https://instagram.com/delhi_gurugram_jobs" class="nav-btn" target="_blank">📸 Follow on Instagram</a>
  </div>
</div>
<div class="footer">
  @delhi_gurugram_jobs · Jobs updated daily · Links may expire after 30–60 days
</div>
</body>
</html>"""
    return html

def build_archive(all_jobs):
    now = now_ist()
    # Group by date
    by_date = {}
    for j in reversed(all_jobs):   # newest first
        d = j.get("posted_on_site", j.get("_fetched_date", ""))[:10]
        if not d:
            d = datetime.now().strftime("%Y-%m-%d")
        by_date.setdefault(d, []).append(j)

    rows_html = ""
    for date_str in sorted(by_date.keys(), reverse=True)[:60]:  # last 60 days
        try:
            dt = datetime.fromisoformat(date_str)
            display_date = dt.strftime("%d %b")
        except:
            display_date = date_str
        for j in by_date[date_str][:8]:   # max 8 per day
            title   = j.get("title","")
            company = j.get("company","")
            link    = j.get("link","")
            label   = f"{title} @ {company}" if company else title
            link_tag = (f'<a href="{link}" class="archive-link" target="_blank" rel="noopener">{label}</a>'
                        if link else f'<span class="archive-link">{label}</span>')
            rows_html += f"""
<div class="archive-row">
  {link_tag}
  <span class="archive-date">{display_date}</span>
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Delhi Gurugram Jobs — Archive</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
  <h1>Job Archive</h1>
  <p>All past openings — Delhi &amp; Gurugram</p>
  <div class="updated">Last updated {now}</div>
</div>
<div class="container">
  <div class="section-title">Past Openings</div>
  {rows_html if rows_html else '<p style="color:var(--accent);font-size:13px">Archive builds up as jobs are posted daily.</p>'}
  <div style="text-align:center;margin-top:20px">
    <a href="index.html" class="nav-btn">← Today's Jobs</a>
    <a href="https://instagram.com/delhi_gurugram_jobs" class="nav-btn" target="_blank">📸 Instagram</a>
  </div>
</div>
<div class="footer">
  @delhi_gurugram_jobs · Note: job links may expire after 30–60 days
</div>
</body>
</html>"""
    return html

# ── Archive data store ────────────────────────────────────────────────────────

ARCHIVE_DATA = os.path.join(DATA_DIR, "archive_jobs.json")

def add_to_archive(jobs):
    archive = load_json(ARCHIVE_DATA, [])
    today   = datetime.now().strftime("%Y-%m-%d")
    for j in jobs:
        j2 = dict(j)
        j2["posted_on_site"] = today
        archive.append(j2)
    archive = archive[-1000:]   # keep last 1000 jobs
    save_file(ARCHIVE_DATA, json.dumps(archive, indent=2, ensure_ascii=False))
    return archive

# ── Git push ──────────────────────────────────────────────────────────────────

def push_to_github():
    cmds = [
        ["git","config","user.email","bot@delhigurugramjobs.com"],
        ["git","config","user.name","Delhi Jobs Bot"],
        ["git","add","docs/"],
        ["git","add","data/"],
        ["git","commit","-m",f"Site update {datetime.now().strftime('%d %b %Y %H:%M')}"],
        ["git","push"],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 and "nothing to commit" not in r.stdout + r.stderr:
            print(f"Git note: {r.stderr[:120]}")
    print("GitHub Pages updated!")

# ── Main entry ────────────────────────────────────────────────────────────────

def update_site(todays_jobs):
    """Call this from main.py after posting. Pass the list of today's job dicts."""
    # Add to rolling archive
    archive = add_to_archive(todays_jobs)
    # Build pages
    index_html   = build_index(todays_jobs)
    archive_html = build_archive(archive)
    # Save
    save_file(os.path.join(DOCS_DIR, "index.html"),   index_html)
    save_file(os.path.join(DOCS_DIR, "archive.html"), archive_html)
    print(f"Site built — index ({len(todays_jobs)} jobs) + archive ({len(archive)} total)")
    # Push to GitHub
    push_to_github()

# ── Test ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_jobs = [
        {"title":"Senior Software Engineer","company":"Google India",
         "location":"Gurugram","salary":"Rs.30L-Rs.45L/yr",
         "experience":"5-8 yrs","link":"https://careers.google.com"},
        {"title":"Product Manager","company":"Razorpay",
         "location":"Gurugram","salary":"",
         "experience":"3-6 yrs","link":"https://razorpay.com/jobs"},
    ]
    os.makedirs("docs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    update_site(test_jobs)
    print("Test complete — check docs/index.html")
