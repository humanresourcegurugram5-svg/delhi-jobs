import re

ABBREVIATIONS = {
    "sr.": "Senior", "sr ": "Senior ", "jr.": "Junior", "jr ": "Junior ",
    "mgr": "Manager", "eng": "Engineer", "engg": "Engineer",
    "dev": "Developer", "asst.": "Assistant", "asst ": "Assistant ",
    "exec.": "Executive", "exec ": "Executive ", "mktg": "Marketing",
    "ops": "Operations", "mgmt": "Management", "bd": "Business Development",
    "qa": "Quality Assurance", "tech": "Technical",
}

REMOVE_WORDS = [
    "urgent", "urgently", "immediate", "immediately", "hiring",
    "requirement", "required", "opening", "vacancy", "opportunity",
    "wfh", "work from home", "fresher", "freshers", "wanted",
    "needed", "apply now", "walk-in", "walkin",
]

SALARY_GARBAGE = [
    "not disclosed", "na", "", "not mentioned", "best in industry",
    "not specified", "-", "negotiable", "as per industry",
    "hike on ctc", "not available", "n/a", "undisclosed",
]

COMPANY_SUFFIXES = [
    "pvt ltd", "pvt. ltd.", "private limited", "limited", "ltd",
    "ltd.", "llp", "india pvt", "technologies pvt", "solutions pvt",
    "services pvt", "& co.", "& co",
]

def clean_job_title(raw_title):
    if not raw_title:
        return "Job Opening"

    title = raw_title

    title = re.sub(
        r'\(?\d+[-+]?\d*\s*(yr|yrs|year|years|exp|experience)\)?',
        "", title, flags=re.IGNORECASE
    )
    title = re.sub(r'@\s*\w+', "", title)
    if " - " in title:
        title = title.split(" - ")[0]
    title = re.sub(r'\([^)]*\)', "", title)
    title = re.sub(r'\[[^\]]*\]', "", title)
    title = re.sub(r'[!@#$%^&*+=|<>?]', "", title)

    title_lower = title.lower()
    for abbr, full in ABBREVIATIONS.items():
        title_lower = title_lower.replace(abbr, full.lower())

    words = title_lower.split()
    words = [w for w in words if w.lower() not in REMOVE_WORDS]
    title = " ".join(words)

    title = title.strip().title()

    if len(title) > 40:
        title = title[:37] + "..."

    if len(title.strip()) < 3:
        return "Job Opening"

    return title

def clean_company_name(raw_company):
    if not raw_company:
        return "Leading Company"

    company = raw_company.strip()

    company_lower = company.lower()
    for suffix in COMPANY_SUFFIXES:
        company_lower = company_lower.replace(suffix, "").strip()

    company = company_lower.strip().title()

    if len(company) > 30:
        company = company[:27] + "..."

    if len(company.strip()) < 2:
        return "Leading Company"

    return company

def clean_salary(raw_salary):
    if not raw_salary:
        return "Competitive Salary"

    salary = str(raw_salary).strip()

    if salary.lower() in SALARY_GARBAGE:
        return "Competitive Salary"

    if len(salary) < 2:
        return "Competitive Salary"

    return salary

def clean_location(raw_location):
    if not raw_location:
        return "Delhi / Gurugram"

    location = str(raw_location).strip()
    loc_lower = location.lower()

    if "gurugram" in loc_lower or "gurgaon" in loc_lower:
        return "Gurugram, Haryana"
    if "noida" in loc_lower:
        return "Noida, UP"
    if "delhi" in loc_lower:
        return "New Delhi"
    if "ncr" in loc_lower or "faridabad" in loc_lower or "ghaziabad" in loc_lower:
        return "Delhi NCR"

    return "Delhi / Gurugram"

def clean_description(raw_desc):
    if not raw_desc:
        return ""
    text = re.sub(r'<[^>]+>', '', str(raw_desc))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = ' '.join(text.split())
    if len(text) > 150:
        text = text[:147] + "..."
    return text.strip()

def clean_experience(raw_exp):
    if not raw_exp:
        return "Open to all"
    exp = str(raw_exp).strip()
    if len(exp) < 2:
        return "Open to all"
    if len(exp) > 20:
        exp = exp[:20]
    return exp

def prepare_job(job):
    return {
        "title":       clean_job_title(job.get("title")),
        "company":     clean_company_name(job.get("company")),
        "location":    clean_location(job.get("location")),
        "salary":      clean_salary(job.get("salary")),
        "experience":  clean_experience(job.get("experience")),
        "description": clean_description(job.get("description")),
        "link":        job.get("link", ""),
        "type":        job.get("type", "Full Time"),
        "source":      job.get("source", "unknown"),
        "category":    job.get("category", "it"),
    }

if __name__ == "__main__":
    test_job = {
        "title": "URGENT!!! Sr.Soft.Eng Java 3-5yr MNC Gurgaon!!!",
        "company": "Tata Consultancy Services Pvt Ltd",
        "location": "Gurgaon, Haryana",
        "salary": "Not Disclosed",
        "experience": "3-5 years",
    }
    cleaned = prepare_job(test_job)
    print("Before:", test_job["title"])
    print("After: ", cleaned["title"])
    print("Company:", cleaned["company"])
    print("Salary:", cleaned["salary"])
