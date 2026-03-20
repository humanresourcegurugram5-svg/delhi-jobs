import os
import re
import json
import time
import random
import requests
import feedparser
from datetime import datetime, timedelta
import pytz

# ── Constants ─────────────────────────────────────────────────────────────────

DATA_DIR  = "data"
BANK_FILE = os.path.join(DATA_DIR, "job_bank.json")
USED_FILE = os.path.join(DATA_DIR, "posted_jobs.json")
LOG_FILE  = os.path.join(DATA_DIR, "api_usage.json")

IST = pytz.timezone("Asia/Kolkata")

# ── Tier lists ────────────────────────────────────────────────────────────────

TIER1_COMPANIES = [
    "google","microsoft","amazon","meta","apple","adobe","oracle","salesforce",
    "goldman sachs","mckinsey","bcg","bain","jpmorgan","morgan stanley",
    "deloitte","pwc","ey","kpmg","netflix","uber","airbnb","linkedin",
    "twitter","stripe","atlassian","servicenow","workday","snowflake",
]
TIER2_COMPANIES = [
    "tcs","infosys","wipro","hcl","cognizant","accenture","capgemini",
    "ibm","tech mahindra","hexaware","mphasis","mindtree","l&t infotech",
    "persistent","mphasis","birlasoft","niit tech",
]
KNOWN_STARTUPS = [
    "zomato","swiggy","flipkart","paytm","phonepe","razorpay","meesho",
    "nykaa","byju","unacademy","zepto","blinkit","ola","myntra","cars24",
    "urban company","policybazaar","groww","cred","lenskart","slice",
    "sharechat","dreamll","freshworks","zoho","browserstack","postman",
]

GARBAGE_SALARY = [
    "","none","null","na","n/a","not disclosed","not mentioned",
    "not specified","as per industry","best in industry","negotiable",
    "hike on ctc","competitive","as per company norms","will be discussed",
    "-","tbd","to be discussed","undisclosed",
]

# ── Job scoring ───────────────────────────────────────────────────────────────
# Higher score = better quality job. We want to post the best ones first.
#
# Score breakdown:
#   40 pts  — real salary is disclosed
#   30 pts  — Tier 1 company (Google, Microsoft, McKinsey…)
#   20 pts  — Tier 2 company (TCS, Infosys, Wipro…)  
#   15 pts  — Known startup (Zomato, Razorpay, PhonePe…)
#   10 pts  — has a clear experience range
#    5 pts  — has job description
#    5 pts  — posted today or yesterday (freshness bonus)
#
# So best possible score = 40+30+10+5+5 = 90
# Minimum acceptable score = 10 (at least experience mentioned)
# We reject anything below MIN_SCORE

MIN_SCORE = 10   # jobs below this are skipped entirely
IDEAL_SCORE = 40 # jobs at/above this go straight to front of queue

def score_job(job):
    score = 0
    company = str(job.get("company","")).lower()
    salary  = str(job.get("salary","")).lower().strip()
    exp     = str(job.get("experience","")).lower().strip()
    desc    = str(job.get("description","")).strip()
    posted  = job.get("posted_date","")

    # Salary — biggest signal
    has_real_salary = (
        salary and
        salary not in GARBAGE_SALARY and
        len(salary) > 3 and
        any(c.isdigit() for c in salary)
    )
    if has_real_salary:
        score += 40

    # Company tier
    for t in TIER1_COMPANIES:
        if t in company:
            score += 30
            break
    else:
        for t in KNOWN_STARTUPS:
            if t in company:
                score += 15
                break
        else:
            for t in TIER2_COMPANIES:
                if t in company:
                    score += 20
                    break

    # Experience mentioned
    if exp and exp not in ["","none","not specified","open"]:
        score += 10

    # Has description
    if desc and len(desc) > 30:
        score += 5

    # Freshness — posted today or yesterday
    if posted:
        try:
            if isinstance(posted, str):
                posted_dt = datetime.fromisoformat(posted.replace("Z",""))
            else:
                posted_dt = posted
            age_days = (datetime.now() - posted_dt).days
            if age_days <= 1:
                score += 5
        except:
            pass

    return score

def priority_label(score):
    if score >= 70: return "IDEAL"
    if score >= 40: return "GOOD"
    if score >= MIN_SCORE: return "OK"
    return "SKIP"

# ── Data helpers ──────────────────────────────────────────────────────────────

def load_json(path, default):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(path):
        return default
    try:
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_job_id(job):
    title   = re.sub(r"[^a-z0-9]","_", job.get("title","").lower())[:30]
    company = re.sub(r"[^a-z0-9]","_", job.get("company","").lower())[:20]
    return f"{company}__{title}"

def is_duplicate(job_id):
    posted = load_json(USED_FILE, {})
    if job_id not in posted:
        return False
    posted_on = datetime.fromisoformat(posted[job_id]["posted_on"])
    return (datetime.now() - posted_on).days < 14

def mark_posted(job):
    posted = load_json(USED_FILE, {})
    jid = make_job_id(job)
    posted[jid] = {
        "title":     job.get("title",""),
        "company":   job.get("company",""),
        "posted_on": datetime.now().isoformat(),
        "score":     job.get("_score", 0),
    }
    # keep only last 500 entries
    if len(posted) > 500:
        oldest = sorted(posted, key=lambda k: posted[k]["posted_on"])[:100]
        for k in oldest: del posted[k]
    save_json(USED_FILE, posted)

def clean_old_records():
    posted = load_json(USED_FILE, {})
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    cleaned = {k:v for k,v in posted.items() if v.get("posted_on","") > cutoff}
    save_json(USED_FILE, cleaned)
    print(f"Cleaned posted_jobs — kept {len(cleaned)} records")

def track_api(source):
    usage = load_json(LOG_FILE, {})
    month = datetime.now().strftime("%Y-%m")
    usage.setdefault(month, {"jsearch":0,"adzuna":0,"rss":0,"bank":0})
    usage[month][source] = usage[month].get(source,0) + 1
    save_json(LOG_FILE, usage)

def jsearch_quota_ok():
    usage = load_json(LOG_FILE, {})
    month = datetime.now().strftime("%Y-%m")
    used  = usage.get(month,{}).get("jsearch",0)
    return used < 175   # keep 25 calls as buffer

# ── Data cleaning ─────────────────────────────────────────────────────────────

REMOVE_TITLE_WORDS = [
    "urgent","urgently","immediate","immediately","hiring","requirement",
    "required","opening","vacancy","opportunity","wfh","work from home",
    "wanted","needed","apply now","fresher","freshers",
]
ABBR = {
    "sr.":"Senior","sr ":"Senior ","jr.":"Junior","jr ":"Junior ",
    "mgr":"Manager","eng":"Engineer","engg":"Engineer","dev":"Developer",
    "asst.":"Assistant","exec.":"Executive","mktg":"Marketing",
    "ops":"Operations","tech":"Technical","bd":"Business Development",
    "qa":"Quality Assurance",
}

def clean_title(raw):
    if not raw: return "Job Opening"
    t = raw
    t = re.sub(r"\(?\d+[-+]?\d*\s*(yr|yrs|year|years|exp|experience)\)?","",t,flags=re.I)
    t = re.sub(r"@\s*\w+","",t)
    if " - " in t: t = t.split(" - ")[0]
    t = re.sub(r"\([^)]*\)","",t)
    t = re.sub(r"\[[^\]]*\]","",t)
    t = re.sub(r"[!@#$%^&*+=|<>?]","",t)
    tl = t.lower()
    for ab,full in ABBR.items():
        tl = tl.replace(ab, full.lower())
    words = [w for w in tl.split() if w.lower() not in REMOVE_TITLE_WORDS]
    t = " ".join(words).strip().title()
    if len(t) > 40: t = t[:37]+"..."
    return t or "Job Opening"

def clean_company(raw):
    if not raw: return "Leading Company"
    c = raw
    suffixes = ["pvt ltd","pvt. ltd.","private limited","limited","ltd.",
                "ltd","llp","india pvt","technologies pvt","solutions pvt"]
    cl = c.lower()
    for s in suffixes: cl = cl.replace(s,"").strip()
    c = cl.strip().title()
    if len(c) > 32: c = c[:29]+"..."
    return c or "Leading Company"

def clean_location(raw):
    if not raw: return "Delhi / Gurugram"
    rl = raw.lower()
    if any(x in rl for x in ["gurugram","gurgaon"]): return "Gurugram, Haryana"
    if "noida" in rl:  return "Noida, UP"
    if "delhi" in rl:  return "New Delhi"
    if "ncr"   in rl:  return "Delhi NCR"
    if "faridabad" in rl: return "Faridabad"
    if "ghaziabad" in rl: return "Ghaziabad"
    return "Delhi / Gurugram"

def clean_experience(raw):
    if not raw: return "Open to all"
    e = str(raw).strip()
    m = re.search(r"(\d+)\s*[-–to]+\s*(\d+)", e)
    if m: return f"{m.group(1)}–{m.group(2)} yrs"
    m2 = re.search(r"(\d+)\+", e)
    if m2: return f"{m2.group(1)}+ yrs"
    m3 = re.search(r"(\d+)", e)
    if m3: return f"{m3.group(1)}+ yrs"
    return "Open to all"

def clean_salary(raw):
    if not raw: return ""
    s = str(raw).strip().lower()
    if s in GARBAGE_SALARY: return ""
    if len(s) < 4: return ""
    if not any(c.isdigit() for c in s): return ""
    return str(raw).strip()

def prepare_job(raw):
    return {
        "title":       clean_title(raw.get("title","")),
        "company":     clean_company(raw.get("company","") or raw.get("employer_name","")),
        "location":    clean_location(raw.get("location","") or raw.get("job_city","")),
        "salary":      clean_salary(raw.get("salary","") or raw.get("job_salary_min","")),
        "experience":  clean_experience(raw.get("experience","") or raw.get("required_experience","")),
        "description": str(raw.get("description",""))[:200].strip(),
        "link":        raw.get("link","") or raw.get("job_apply_link",""),
        "posted_date": raw.get("posted_date",""),
        "category":    raw.get("category","IT"),
        "source":      raw.get("source","unknown"),
    }

# ── Fetchers ──────────────────────────────────────────────────────────────────

HEADERS = [
    {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
    {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
    {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"},
]

def rand_headers():
    h = random.choice(HEADERS).copy()
    h["Accept-Language"] = "en-IN,en;q=0.9"
    h["Referer"] = "https://www.google.com/"
    return h

def fetch_jsearch(category, location="Delhi Gurugram"):
    key = os.environ.get("JSEARCH_KEY","")
    if not key or not jsearch_quota_ok():
        print("JSearch skipped — no key or quota low")
        return []
    queries = {
        "it":         f"software engineer developer {location}",
        "marketing":  f"marketing manager digital marketing {location}",
        "finance":    f"financial analyst chartered accountant {location}",
        "hr":         f"HR manager talent acquisition {location}",
    }
    q = queries.get(category, f"jobs {location}")
    try:
        r = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers={"X-RapidAPI-Key":key,"X-RapidAPI-Host":"jsearch.p.rapidapi.com"},
            params={"query":q,"page":"1","num_results":"15","date_posted":"today","country":"in"},
            timeout=12,
        )
        track_api("jsearch")
        if r.status_code != 200: return []
        jobs = r.json().get("data",[])
        out  = []
        for j in jobs:
            city = str(j.get("job_city","")).lower()
            if not any(x in city for x in ["delhi","gurugram","gurgaon","noida","ncr","faridabad"]):
                continue
            sal_min = j.get("job_salary_min")
            sal_max = j.get("job_salary_max")
            salary  = ""
            if sal_min and sal_max:
                mn = round(sal_min/100000,1)
                mx = round(sal_max/100000,1)
                salary = f"Rs.{mn}L-Rs.{mx}L/yr"
            exp_months = (j.get("job_required_experience") or {}).get("required_experience_in_months",0)
            out.append({
                "title":       j.get("job_title",""),
                "company":     j.get("employer_name",""),
                "location":    j.get("job_city",""),
                "salary":      salary,
                "experience":  f"{exp_months//12}+ yrs" if exp_months else "",
                "description": j.get("job_description","")[:200],
                "link":        j.get("job_apply_link",""),
                "posted_date": j.get("job_posted_at_datetime_utc",""),
                "category":    category,
                "source":      "jsearch",
            })
        print(f"JSearch: {len(out)} NCR jobs")
        return out
    except Exception as e:
        print(f"JSearch error: {e}")
        return []

def fetch_adzuna(category, location="delhi"):
    app_id  = os.environ.get("ADZUNA_APP_ID","")
    app_key = os.environ.get("ADZUNA_APP_KEY","")
    if not app_id or not app_key:
        print("Adzuna skipped — no credentials")
        return []
    cats = {
        "it":"it-jobs","marketing":"marketing-jobs",
        "finance":"accounting-finance-jobs","hr":"hr-jobs",
    }
    cat_slug = cats.get(category,"it-jobs")
    try:
        r = requests.get(
            f"https://api.adzuna.com/v1/api/jobs/in/search/1",
            params={
                "app_id":app_id,"app_key":app_key,
                "what":category,"where":location,
                "results_per_page":15,"sort_by":"date",
                "max_days_old":3,
            },
            timeout=12,
        )
        track_api("adzuna")
        if r.status_code != 200: return []
        results = r.json().get("results",[])
        out = []
        for j in results:
            loc = str(j.get("location",{}).get("display_name","")).lower()
            if not any(x in loc for x in ["delhi","gurugram","gurgaon","noida","ncr"]):
                continue
            sal_min = j.get("salary_min")
            sal_max = j.get("salary_max")
            salary  = ""
            if sal_min and sal_max:
                mn = round(sal_min/100000,1)
                mx = round(sal_max/100000,1)
                salary = f"Rs.{mn}L-Rs.{mx}L/yr"
            out.append({
                "title":       j.get("title",""),
                "company":     j.get("company",{}).get("display_name",""),
                "location":    j.get("location",{}).get("display_name",""),
                "salary":      salary,
                "experience":  "",
                "description": j.get("description","")[:200],
                "link":        j.get("redirect_url",""),
                "posted_date": j.get("created",""),
                "category":    category,
                "source":      "adzuna",
            })
        print(f"Adzuna: {len(out)} NCR jobs")
        return out
    except Exception as e:
        print(f"Adzuna error: {e}")
        return []

RSS_FEEDS = {
    "it": [
        "https://in.indeed.com/rss?q=software+engineer&l=Gurugram&sort=date",
        "https://in.indeed.com/rss?q=developer&l=Delhi+NCR&sort=date",
        "https://in.indeed.com/rss?q=IT+jobs&l=Noida&sort=date",
        "https://www.shine.com/rss/it-jobs-delhi-ncr.xml",
    ],
    "marketing": [
        "https://in.indeed.com/rss?q=marketing+manager&l=Delhi+NCR&sort=date",
        "https://in.indeed.com/rss?q=digital+marketing&l=Gurugram&sort=date",
        "https://www.shine.com/rss/marketing-jobs-delhi.xml",
    ],
    "finance": [
        "https://in.indeed.com/rss?q=financial+analyst&l=Delhi+NCR&sort=date",
        "https://in.indeed.com/rss?q=chartered+accountant&l=Gurugram&sort=date",
    ],
    "hr": [
        "https://in.indeed.com/rss?q=HR+manager&l=Delhi+NCR&sort=date",
        "https://in.indeed.com/rss?q=talent+acquisition&l=Gurugram&sort=date",
    ],
}

def fetch_rss(category):
    feeds = RSS_FEEDS.get(category, RSS_FEEDS["it"])
    url   = random.choice(feeds)
    try:
        time.sleep(random.uniform(2,5))
        feed = feedparser.parse(url, request_headers=rand_headers())
        track_api("rss")
        out = []
        for e in feed.entries:
            company = ""
            for field in ["author","publisher","dc_publisher"]:
                if hasattr(e, field) and getattr(e,field):
                    company = getattr(e,field)
                    break
            out.append({
                "title":       e.get("title",""),
                "company":     company,
                "location":    "Delhi / Gurugram",
                "salary":      "",
                "experience":  "",
                "description": re.sub(r"<[^>]+>","",e.get("summary",""))[:200],
                "link":        e.get("link",""),
                "posted_date": e.get("published",""),
                "category":    category,
                "source":      "rss",
            })
        print(f"RSS ({url[:50]}...): {len(out)} jobs")
        return out
    except Exception as e:
        print(f"RSS error: {e}")
        return []

def fetch_job_bank(category, exclude_ids):
    bank = load_json(BANK_FILE, [])
    out  = [j for j in bank
            if j.get("category") == category
            and make_job_id(j) not in exclude_ids]
    print(f"Job bank: {len(out)} {category} jobs available")
    return out

FILLER_JOBS = [
    {"title":"Software Engineer","company":"Leading IT Company","location":"Delhi NCR",
     "salary":"","experience":"2-5 yrs","description":"Multiple openings for software engineers in Delhi NCR. Apply via link in bio.","link":"","category":"it","source":"filler"},
    {"title":"Marketing Manager","company":"Top Consumer Brand","location":"Gurugram",
     "salary":"","experience":"3-6 yrs","description":"Marketing leadership role at a top brand in Gurugram.","link":"","category":"marketing","source":"filler"},
    {"title":"Financial Analyst","company":"Leading BFSI Firm","location":"Delhi",
     "salary":"","experience":"2-4 yrs","description":"Finance role at a leading BFSI firm in Delhi.","link":"","category":"finance","source":"filler"},
    {"title":"HR Manager","company":"Fast Growing Startup","location":"Gurugram",
     "salary":"","experience":"4-7 yrs","description":"People operations role at a fast-growing startup in Gurugram.","link":"","category":"hr","source":"filler"},
]

# ── Main: fetch best jobs ─────────────────────────────────────────────────────
#
# Priority order for selection:
#   1. Jobs with real salary from a known big company  (score 70+)
#   2. Jobs with real salary from any company          (score 40+)
#   3. Jobs from known big companies (no salary)       (score 30+)
#   4. Jobs from known startups (no salary)            (score 15+)
#   5. Any job with experience info                    (score 10+)
#   6. Job bank (previously saved jobs)
#   7. Filler content (last resort)

def fetch_best_jobs(category="it", count=1):
    clean_old_records()
    posted_ids = set(load_json(USED_FILE, {}).keys())
    all_raw = []

    # --- Level 1: JSearch (best quality)
    print("\n--- Trying JSearch ---")
    raw = fetch_jsearch(category)
    all_raw.extend(raw)

    # --- Level 2: Adzuna
    print("\n--- Trying Adzuna ---")
    raw = fetch_adzuna(category)
    all_raw.extend(raw)

    # --- Level 3: RSS
    print("\n--- Trying RSS ---")
    raw = fetch_rss(category)
    all_raw.extend(raw)

    print(f"\nTotal raw fetched: {len(all_raw)}")

    # Clean and score all jobs
    cleaned = []
    for raw_job in all_raw:
        j   = prepare_job(raw_job)
        jid = make_job_id(j)
        if not j["title"] or j["title"] == "Job Opening": continue
        if is_duplicate(jid): continue
        s = score_job(j)
        if s < MIN_SCORE:
            print(f"  SKIP (score {s}): {j['title']} @ {j['company']}")
            continue
        j["_score"] = s
        j["_id"]    = jid
        cleaned.append(j)

    # Deduplicate by id
    seen = set()
    unique = []
    for j in cleaned:
        if j["_id"] not in seen:
            seen.add(j["_id"])
            unique.append(j)

    # Sort by score descending — best jobs first
    unique.sort(key=lambda x: x["_score"], reverse=True)

    print(f"\nScored & ranked {len(unique)} unique jobs:")
    for j in unique[:10]:
        print(f"  [{j['_score']:3d}] {priority_label(j['_score']):6s} | "
              f"{'SAL' if j['salary'] else '   '} | "
              f"{j['title'][:30]:30s} @ {j['company'][:20]}")

    # Save all scored jobs to bank for future fallback
    bank = load_json(BANK_FILE, [])
    new_ids = {j["_id"] for j in unique}
    bank = [b for b in bank if make_job_id(b) not in new_ids]
    bank.extend(unique)
    bank = bank[-400:]   # keep last 400
    save_json(BANK_FILE, bank)

    # Return top `count` jobs
    if len(unique) >= count:
        selected = unique[:count]
        print(f"\nSelected {count} job(s) — top score: {selected[0]['_score']}")
        return selected

    # Not enough from live APIs — top up from bank
    print(f"\nOnly {len(unique)} live jobs — checking bank for top-ups...")
    bank_jobs = fetch_job_bank(category, {j["_id"] for j in unique} | posted_ids)
    bank_jobs.sort(key=lambda x: x.get("_score",0), reverse=True)
    combined = unique + bank_jobs
    if len(combined) >= count:
        return combined[:count]

    # Absolute last resort — filler
    print("Using filler content")
    fillers = [f for f in FILLER_JOBS if f["category"] == category]
    combined.extend(fillers)
    return combined[:count]


def filter_unique_jobs(jobs, needed=1):
    """Filter duplicates from a pre-fetched list. Used by main.py."""
    posted_ids = set(load_json(USED_FILE, {}).keys())
    unique = []
    for j in jobs:
        jid = make_job_id(j)
        if jid not in posted_ids:
            unique.append(j)
        if len(unique) == needed:
            break
    return unique


def log_post(job, status, error=None):
    path = os.path.join(DATA_DIR, "post_log.json")
    log  = load_json(path, [])
    log.append({
        "timestamp": datetime.now().isoformat(),
        "title":     job.get("title",""),
        "company":   job.get("company",""),
        "score":     job.get("_score",0),
        "status":    status,
        "error":     error or "",
    })
    log = log[-500:]
    save_json(path, log)


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    jobs = fetch_best_jobs("it", count=1)
    if jobs:
        j = jobs[0]
        print(f"\nBest job found:")
        print(f"  Title:    {j['title']}")
        print(f"  Company:  {j['company']}")
        print(f"  Salary:   {j['salary'] or '(none — will use smart fallback)'}")
        print(f"  Score:    {j.get('_score',0)}")
        print(f"  Priority: {priority_label(j.get('_score',0))}")
