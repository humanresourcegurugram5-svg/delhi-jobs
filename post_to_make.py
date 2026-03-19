import os
import json
import time
import base64
import random
import requests
from datetime import datetime

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")
TWILIO_SID       = os.environ.get("TWILIO_SID", "")
TWILIO_TOKEN     = os.environ.get("TWILIO_TOKEN", "")
YOUR_WHATSAPP    = os.environ.get("YOUR_WHATSAPP", "")

CAPTION_TEMPLATES = [
    """{emoji} Job Alert!
{title} at {company}
Location: {location}
Salary: {salary}
Experience: {experience}

Apply now via link in bio!

{hashtags}""",

    """{emoji} New Opening!
{company} is hiring a {title}
{location} | {experience}
Salary: {salary}

Tap link in bio to apply!

{hashtags}""",

    """{emoji} Hiring Alert!
Role: {title}
Company: {company}
Location: {location}
Salary: {salary}

Apply via link in bio

{hashtags}""",

    """{emoji} Don't miss this!
{title} - {company}
{location} | {salary}
Experience needed: {experience}

Link in bio to apply now!

{hashtags}""",

    """{emoji} Great Opportunity!
{company} needs a {title}
Based in {location}
Package: {salary}

Apply now - link in bio!

{hashtags}""",
]

HASHTAG_POOLS = {
    "it": [
        "#DelhiJobs #GurugramJobs #TechJobs #ITJobs #SoftwareEngineer #Hiring #JobAlert #NCRJobs #DeveloperJobs #DataScience",
        "#GurugramJobs #DelhiJobs #SoftwareJobs #ITHiring #TechCareers #JobSearch #Naukri #PythonJobs #JavaJobs #DevOps",
        "#DelhiNCR #TechJobs #HiringNow #SoftwareDeveloper #ITJobs #GurugramHiring #JobOpening #FullStack #CloudJobs #AIJobs",
    ],
    "marketing": [
        "#DelhiJobs #GurugramJobs #MarketingJobs #DigitalMarketing #SalesJobs #ContentWriter #Hiring #NCRJobs #MarketingHiring",
        "#GurugramJobs #DelhiJobs #MarketingCareer #SocialMediaJobs #SEOJobs #BrandManager #JobAlert #HiringNow #ContentJobs",
    ],
    "finance": [
        "#DelhiJobs #GurugramJobs #FinanceJobs #BankingJobs #CAJobs #FintechJobs #Hiring #NCRJobs #AccountingJobs #AnalystJobs",
        "#GurugramJobs #DelhiJobs #FinanceCareers #BFSIJobs #CFO #InvestmentBanking #JobAlert #FinanceHiring #PayrollJobs",
    ],
    "hr": [
        "#DelhiJobs #GurugramJobs #HRJobs #HumanResources #TalentAcquisition #Recruiter #Hiring #NCRJobs #HRHiring #PeopleOps",
        "#GurugramJobs #DelhiJobs #HRCareer #AdminJobs #RecruiterLife #HRManager #JobAlert #HiringNow #PayrollJobs",
    ],
}

EMOJIS = ["", "", "", "", "", "", ""]

def get_caption(job, post_number):
    template = CAPTION_TEMPLATES[post_number % len(CAPTION_TEMPLATES)]
    category = job.get("category", "it")
    hashtag_list = HASHTAG_POOLS.get(category, HASHTAG_POOLS["it"])
    hashtags = hashtag_list[post_number % len(hashtag_list)]
    emoji = EMOJIS[post_number % len(EMOJIS)]

    return template.format(
        emoji=emoji,
        title=job.get("title", "Job Opening"),
        company=job.get("company", "Leading Company"),
        location=job.get("location", "Delhi / Gurugram"),
        salary=job.get("salary", "Competitive Salary"),
        experience=job.get("experience", "Open to all"),
        hashtags=hashtags,
    )

def upload_image_to_imgbb(image_path):
    imgbb_key = os.environ.get("IMGBB_KEY", "")
    if not imgbb_key:
        print("No IMGBB_KEY — trying alternative upload")
        return upload_image_to_github(image_path)

    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": imgbb_key,
                "image": image_data,
                "expiration": 86400,
            },
            timeout=30
        )

        if response.status_code == 200:
            url = response.json()["data"]["url"]
            print(f"Image uploaded to imgbb: {url}")
            return url
        else:
            print(f"imgbb upload failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"imgbb error: {e}")
        return None

def upload_image_to_github(image_path):
    github_token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    if not github_token or not repo:
        print("No GitHub token for image upload")
        return None

    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        filename = f"images/post_{int(time.time())}.jpg"
        url = f"https://api.github.com/repos/{repo}/contents/{filename}"

        response = requests.put(
            url,
            headers={
                "Authorization": f"token {github_token}",
                "Content-Type": "application/json",
            },
            json={
                "message": f"Add post image {filename}",
                "content": image_data,
            },
            timeout=30
        )

        if response.status_code in [200, 201]:
            raw_url = f"https://raw.githubusercontent.com/{repo}/main/{filename}"
            print(f"Image uploaded to GitHub: {raw_url}")
            return raw_url
        else:
            print(f"GitHub upload failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"GitHub upload error: {e}")
        return None

def send_to_make(image_url, caption):
    if not MAKE_WEBHOOK_URL:
        print("No Make webhook URL")
        return False

    try:
        payload = {
            "image_url": image_url,
            "caption": caption,
            "timestamp": datetime.now().isoformat(),
        }

        response = requests.post(
            MAKE_WEBHOOK_URL,
            json=payload,
            timeout=30
        )

        if response.status_code in [200, 201, 202]:
            print("Sent to Make.com successfully!")
            return True
        else:
            print(f"Make.com returned: {response.status_code}")
            return False

    except Exception as e:
        print(f"Make.com error: {e}")
        return False

def send_whatsapp_alert(message, image_path=None):
    if not TWILIO_SID or not TWILIO_TOKEN or not YOUR_WHATSAPP:
        print("Twilio not configured — skipping WhatsApp")
        return False

    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)

        client.messages.create(
            from_="whatsapp:+14155238886",
            to=f"whatsapp:{YOUR_WHATSAPP}",
            body=message
        )
        print(f"WhatsApp alert sent to {YOUR_WHATSAPP}")
        return True

    except Exception as e:
        print(f"WhatsApp error: {e}")
        return False

def post_job(job, image_path, post_number):
    caption = get_caption(job, post_number)
    print(f"\nPosting: {job['title']} @ {job['company']}")

    image_url = upload_image_to_imgbb(image_path)

    if not image_url:
        print("Image upload failed — sending to WhatsApp")
        alert = (
            f"Image upload failed for post {post_number + 1}\n\n"
            f"Job: {job['title']} at {job['company']}\n"
            f"Please post manually.\n\n"
            f"Caption:\n{caption[:500]}"
        )
        send_whatsapp_alert(alert)
        return False

    success = send_to_make(image_url, caption)

    if not success:
        print("Make.com failed — sending to WhatsApp as fallback")
        alert = (
            f"Make.com failed for post {post_number + 1}\n\n"
            f"Job: {job['title']} at {job['company']}\n"
            f"Image URL: {image_url}\n\n"
            f"Caption:\n{caption[:500]}"
        )
        send_whatsapp_alert(alert)
        return False

    print(f"Post {post_number + 1} sent successfully!")
    return True

def send_linktree_update(jobs):
    if not YOUR_WHATSAPP:
        return

    message = "Today's jobs ready! Update your Linktree:\n\n"
    for i, job in enumerate(jobs, 1):
        link = job.get("link", "N/A")
        message += f"{i}. {job['title']}\n"
        message += f"   {job['company']} - {job['location']}\n"
        message += f"   {link}\n\n"
    message += "Open linktr.ee and update the 4 links!"

    send_whatsapp_alert(message)
    print("Linktree update sent to WhatsApp")

if __name__ == "__main__":
    print("post_to_make.py loaded successfully")
