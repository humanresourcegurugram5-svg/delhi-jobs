import os
import json
import time
import random
import requests
import feedparser
from datetime import datetime

DATA_DIR = "data"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

CATEGORIES = {
    "it":         ["software engineer", "developer", "data analyst", "devops", "python", "java"],
    "marketing":  ["digital marketing", "marketing manager", "content writer", "seo", "sales"],
    "finance":    ["financial analyst", "chartered accountant", "finance manager", "banking"],
    "hr":         ["hr manager", "human resources", "talent acquisition", "recruiter"],
}

RSS_FEEDS = {
    "it": [
        "https://in.indeed.com/rss?q=software+engineer&l=Gurugram",
        "https://in.indeed.com/rss?q=developer&l=Delhi",
        "https://in.indeed.com/rss?q=software&l=Delhi+NCR",
        "https://in.indeed.com/rss?q=IT+jobs&l=Gurugram",
    ],
    "marketing": [
        "https://in.indeed.com/rss?q=marketing&l=Delhi+NCR",
        "https://in.indeed.com/rss?q=digital+marketing&l=Gurugram",
        "https://in.indeed.com/rss?q=sales&l=Delhi",
    ],
    "finance": [
        "https://in.indeed.com/rss?q=finance&l=Delhi+NCR",
        "https://in.indeed.com/rss?q=accounting&l=Gurugram",
    ],
    "hr": [
        "https://in.indeed.com/rss?q=HR&l=Delhi+NCR",
        "https://in.indeed.com/rss?q=human+resources&l=Delhi",
    ],
}

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
        "Referer": "https://www.google.com/",
        "DNT": "1",
    }

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

def track_api_usage(source):
    usage = load_json("api_usage.json", {})
    month = datetime.now().strftime("%Y-%m")
    if month not in usage:
        usage[month] = {"jsearch": 0, "adzuna": 0, "rss": 0}
    usage[month][source] += 1
    save_json("api_usage.json", usage)

def should_use_jsearch():
    usage = load_json("api_usage.json", {})
    month = datetime.now().strftime("%Y-%m")
    used = usage.get(month, {}).get("jsearch", 0)
    return used < 180

def fetch_jsearch(category):
    print("Trying JSearch API...")
    key = os.environ.get("JSEARCH_KEY", "")
    if not key:
        print("No JSearch key found")
        return []

    queries = CATEGORIES.get(category, ["jobs"])
    query = random.choice(queries)

    try:
        response = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers={
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            },
            params={
                "query": f"{query} in Delhi Gurugram India",
                "page": "1",
                "num_results": "10",
                "date_posted": "today",
                "country": "in",
            },
            timeout=15
        )
        track_api_usage("jsearch")

        if response.status_code != 200:
            print(f"JSearch returned {response.status_code}")
            return []

        raw_jobs = response.json().get("data", [])
        jobs = []
        for j in raw_jobs:
            city = str(j.get("job_city", "")).lower()
            state = str(j.get("job_state", "")).lower()
            location_str = city + " " + state
            ncr_keywords = ["delhi", "gurugram", "gurgaon", "noida", "ncr", "faridabad"]
            if not any(k in location_str for k in ncr_keywords):
                continue

            sal_min = j.get("job_salary_min")
            sal_max = j.get("job_salary_max")
            if sal_min and sal_max:
                min_l = round(sal_min / 100000, 1)
                max_l = round(sal_max / 100000, 1)
                salary = f"Rs.{min_l}L-{max_l}L/yr"
            else:
                salary = "Competitive Salary"

            exp_months = j.get("job_required_experience", {})
            if exp_months:
                exp_months = exp_months.get("required_experience_in_months", 0)
                exp_years = exp_months // 12 if exp_months else 0
                experience = f"{exp_years}+ yrs" if exp_years else "Open to all"
            else:
                experience = "Open to all"

            jobs.append({
                "title": j.get("job_title", "Job Opening"),
                "company": j.get("employer_name", "Leading Company"),
                "location": j.get("job_city", "Delhi / Gurugram"),
                "salary": salary,
                "experience": experience,
                "description": (j.get("job_description") or "")[:150],
                "link": j.get("job_apply_link", ""),
                "type": j.get("job_employment_type", "Full Time"),
                "source": "jsearch",
                "category": category,
            })

        print(f"JSearch: {len(jobs)} NCR jobs found")
        return jobs

    except Exception as e:
        print(f"JSearch error: {e}")
        return []

def fetch_adzuna(category):
    print("Trying Adzuna API...")
    app_id = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        print("No Adzuna keys found")
        return []

    queries = CATEGORIES.get(category, ["jobs"])
    query = random.choice(queries)

    try:
        response = requests.get(
            f"https://api.adzuna.com/v1/api/jobs/in/search/1",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": 10,
                "what": query,
                "where": "Delhi",
                "content-type": "application/json",
            },
            timeout=15
        )
        track_api_usage("adzuna")

        if response.status_code != 200:
            print(f"Adzuna returned {response.status_code}")
            return []

        raw_jobs = response.json().get("results", [])
        jobs = []
        for j in raw_jobs:
            location = j.get("location", {}).get("display_name", "Delhi / Gurugram")
            sal_min = j.get("salary_min")
            sal_max = j.get("salary_max")
            if sal_min and sal_max and sal_min > 10000:
                min_l = round(sal_min / 100000, 1)
                max_l = round(sal_max / 100000, 1)
                salary = f"Rs.{min_l}L-{max_l}L/yr"
            else:
                salary = "Competitive Salary"

            jobs.append({
                "title": j.get("title", "Job Opening"),
                "company": j.get("company", {}).get("display_name", "Leading Company"),
                "location": location,
                "salary": salary,
                "experience": "Open to all",
                "description": (j.get("description") or "")[:150],
                "link": j.get("redirect_url", ""),
                "type": "Full Time",
                "source": "adzuna",
                "category": category,
            })

        print(f"Adzuna: {len(jobs)} jobs found")
        return jobs

    except Exception as e:
        print(f"Adzuna error: {e}")
        return []

def fetch_rss(category):
    print("Trying RSS feeds...")
    feeds = RSS_FEEDS.get(category, RSS_FEEDS["it"])
    feed_url = random.choice(feeds)

    try:
        time.sleep(random.uniform(2, 5))
        feed = feedparser.parse(feed_url)
        track_api_usage("rss")
        jobs = []

        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")

            if not title or not link:
                continue

            jobs.append({
                "title": title,
                "company": "Leading Company",
                "location": "Delhi / Gurugram",
                "salary": "Competitive Salary",
                "experience": "Open to all",
                "description": summary[:150] if summary else "",
                "link": link,
                "type": "Full Time",
                "source": "rss",
                "category": category,
            })

        print(f"RSS: {len(jobs)} jobs found")
        return jobs

    except Exception as e:
        print(f"RSS error: {e}")
        return []

def fetch_from_job_bank(category):
    print("Checking Job Bank...")
    bank = load_json("job_bank.json", [])
    available = [j for j in bank if not j.get("posted") and j.get("category") == category]
    if not available:
        available = [j for j in bank if not j.get("posted")]
    print(f"Job Bank: {len(available)} available")
    return available[:10]

def get_filler_content(category):
    fillers = [
        {
            "title": "Top Skills Hiring in Delhi NCR",
            "company": "Delhi Gurugram Jobs",
            "location": "Delhi / Gurugram",
            "salary": "Multiple Openings",
            "experience": "All levels",
            "description": "Check our bio link for today's top job openings in Delhi and Gurugram.",
            "link": "",
            "type": "Career Tips",
            "source": "filler",
            "category": category,
        }
    ]
    return fillers

def is_link_alive(url):
    if not url:
        return False
    try:
        r = requests.head(url, timeout=5, allow_redirects=True, headers=get_headers())
        return r.status_code in [200, 301, 302, 303]
    except:
        return True

def fetch_best_jobs(category="it", count=4):
    print(f"\nFetching jobs for category: {category}")
    jobs = []

    if should_use_jsearch():
        jobs = fetch_jsearch(category)

    if len(jobs) < count:
        more = fetch_adzuna(category)
        jobs.extend(more)

    if len(jobs) < count:
        more = fetch_rss(category)
        jobs.extend(more)

    if len(jobs) < count:
        more = fetch_from_job_bank(category)
        jobs.extend(more)

    if len(jobs) == 0:
        jobs = get_filler_content(category)

    bank = load_json("job_bank.json", [])
    new_jobs = [j for j in jobs if j.get("source") not in ["filler"]]
    bank.extend(new_jobs)
    bank = bank[-300:]
    save_json("job_bank.json", bank)

    print(f"Total jobs fetched: {len(jobs)}")
    return jobs

if __name__ == "__main__":
    jobs = fetch_best_jobs("it", 4)
    for j in jobs[:2]:
        print(f"  {j['title']} @ {j['company']} — {j['salary']}")
