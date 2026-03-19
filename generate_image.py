import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

WIDTH, HEIGHT = 1080, 1080
BG_COLOR     = "#fdf6ee"
TEXT_DARK    = "#2c1f0e"
TEXT_MID     = "#6b4f2e"
TEXT_LIGHT   = "#b49060"
BORDER_COLOR = "#e8ddd0"

FONTS_DIR = "fonts"

FONT_URLS = {
    "CormorantBold.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/"
        "cormorantgaramond/CormorantGaramond-SemiBold.ttf"
    ),
    "Montserrat.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/"
        "montserrat/static/Montserrat-Bold.ttf"
    ),
    "MontserratReg.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/"
        "montserrat/static/Montserrat-Regular.ttf"
    ),
    "NotoSans.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/"
        "notosans/NotoSans-Regular.ttf"
    ),
}

def setup_fonts():
    os.makedirs(FONTS_DIR, exist_ok=True)
    for name, url in FONT_URLS.items():
        path = os.path.join(FONTS_DIR, name)
        if not os.path.exists(path):
            print(f"Downloading font: {name}...")
            try:
                urllib.request.urlretrieve(url, path)
                print(f"Downloaded {name}")
            except Exception as e:
                print(f"Failed to download {name}: {e}")

def load_fonts():
    setup_fonts()
    fonts = {}
    try:
        fonts["title"]   = ImageFont.truetype(os.path.join(FONTS_DIR, "Cormorant.ttf"), 80)
        fonts["title_sm"]= ImageFont.truetype(os.path.join(FONTS_DIR, "Cormorant.ttf"), 62)
        fonts["bold"]    = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat.ttf"), 26)
        fonts["medium"]  = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat.ttf"), 22)
        fonts["small"]   = ImageFont.truetype(os.path.join(FONTS_DIR, "MontserratReg.ttf"), 19)
        fonts["tiny"]    = ImageFont.truetype(os.path.join(FONTS_DIR, "MontserratReg.ttf"), 16)
        fonts["salary"]  = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans.ttf"), 26)
        fonts["salary_sm"]= ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans.ttf"), 22)
    except Exception as e:
        print(f"Font load error: {e} — using default")
        default = ImageFont.load_default()
        for k in ["title","title_sm","bold","medium","small","tiny","salary","salary_sm"]:
            fonts[k] = default
    return fonts

def wrap_title(title, max_chars=22):
    words = title.split()
    if len(title) <= max_chars:
        return [title]
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = (current + " " + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:3]

def generate_card(job, post_number=0):
    fonts = load_fonts()

    img  = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rectangle([6, 6, WIDTH-6, HEIGHT-6], outline=BORDER_COLOR, width=2)
    draw.rectangle([14, 14, WIDTH-14, HEIGHT-14], outline=BORDER_COLOR, width=1)

    draw.ellipse([WIDTH-320, HEIGHT-320, WIDTH+80, HEIGHT+80],
                 outline="#e8ddd0", width=50)
    draw.ellipse([WIDTH-180, HEIGHT-420, WIDTH+20, HEIGHT-220],
                 outline="#f0e8d8", width=30)

    draw.text((72, 72), "DELHI  /  GURUGRAM",
              font=fonts["tiny"], fill=TEXT_LIGHT)

    badge_text = "HIRING NOW"
    badge_x = WIDTH - 72 - 160
    draw.rectangle([badge_x, 60, badge_x+160, 98],
                   outline=TEXT_DARK, width=1)
    draw.text((badge_x + 80, 79), badge_text,
              font=fonts["tiny"], fill=TEXT_DARK, anchor="mm")

    title = job.get("title", "Job Opening")
    title_lines = wrap_title(title)
    font_title = fonts["title"] if len(title) <= 22 else fonts["title_sm"]

    y_title = 380
    for line in title_lines:
        draw.text((72, y_title), line, font=font_title, fill=TEXT_DARK)
        y_title += 90 if font_title == fonts["title"] else 72

    company = job.get("company", "Leading Company")
    draw.text((72, y_title + 12), company,
              font=fonts["bold"], fill=TEXT_MID)

    job_type = job.get("type", "Full Time")
    draw.text((72, 340), f"{job_type}  ·  On-site",
              font=fonts["tiny"], fill=TEXT_LIGHT)

    divider_y = 770
    draw.line([(72, divider_y), (WIDTH-72, divider_y)],
              fill=BORDER_COLOR, width=1)

    salary = job.get("salary", "Competitive Salary")
    exp    = job.get("experience", "Open to all")

    draw.text((72, divider_y + 18), "SALARY",
              font=fonts["tiny"], fill=TEXT_LIGHT)
    draw.text((72, divider_y + 38), salary,
              font=fonts["salary_sm"], fill=TEXT_DARK)

    draw.text((430, divider_y + 18), "EXPERIENCE",
              font=fonts["tiny"], fill=TEXT_LIGHT)
    draw.text((430, divider_y + 38), exp,
              font=fonts["salary_sm"], fill=TEXT_DARK)

    draw.text((780, divider_y + 18), "APPLY",
              font=fonts["tiny"], fill=TEXT_LIGHT)
    draw.text((780, divider_y + 38), "Link in bio",
              font=fonts["tiny"], fill=TEXT_DARK)

    hashtag_pools = [
        "#DelhiJobs #GurugramJobs #Hiring #JobAlert #NCRJobs",
        "#DelhiJobs #TechJobs #GurugramHiring #JobSearch #ITJobs",
        "#GurugramJobs #DelhiNCR #HiringNow #JobVacancy #CareerGoals",
        "#NaukriAlert #DelhiJobs #JobOpening #GurugramJobs #Recruitment",
        "#JobsDelhi #GurugramHiring #CareerOpportunity #DelhiNCR #Hiring",
    ]
    hashtags = hashtag_pools[post_number % len(hashtag_pools)]
    draw.text((72, 960), hashtags, font=fonts["tiny"], fill=TEXT_LIGHT)

    draw.text((72, 1000), "@delhi_gurugram_jobs",
              font=fonts["tiny"], fill=BORDER_COLOR)

    output_path = f"post_{post_number}.jpg"
    img.save(output_path, "JPEG", quality=95, dpi=(72, 72))
    print(f"Image saved: {output_path} ({WIDTH}x{HEIGHT}px)")
    return output_path

if __name__ == "__main__":
    test_job = {
        "title":      "Senior Software Engineer",
        "company":    "Google India",
        "location":   "Gurugram, Haryana",
        "salary":     "Rs.30L-45L/yr",
        "experience": "5-8 yrs",
        "type":       "Full Time",
    }
    path = generate_card(test_job, 0)
    print(f"Test image generated: {path}")
