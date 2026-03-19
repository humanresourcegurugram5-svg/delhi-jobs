import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1080
BG_COLOR     = "#fdf6ee"
TEXT_DARK    = "#2c1f0e"
TEXT_MID     = "#6b4f2e"
TEXT_LIGHT   = "#b49060"
BORDER_COLOR = "#e8ddd0"
FONTS_DIR    = "fonts"

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
        fonts["title_lg"]   = ImageFont.truetype(os.path.join(FONTS_DIR, "CormorantBold.ttf"), 120)
        fonts["title_md"]   = ImageFont.truetype(os.path.join(FONTS_DIR, "CormorantBold.ttf"), 95)
        fonts["title_sm"]   = ImageFont.truetype(os.path.join(FONTS_DIR, "CormorantBold.ttf"), 75)
        fonts["company"]    = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat.ttf"), 34)
        fonts["label"]      = ImageFont.truetype(os.path.join(FONTS_DIR, "MontserratReg.ttf"), 24)
        fonts["value"]      = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans.ttf"), 32)
        fonts["tag"]        = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat.ttf"), 22)
        fonts["hashtag"]    = ImageFont.truetype(os.path.join(FONTS_DIR, "MontserratReg.ttf"), 23)
        fonts["watermark"]  = ImageFont.truetype(os.path.join(FONTS_DIR, "MontserratReg.ttf"), 21)
    except Exception as e:
        print(f"Font load error: {e} - using default")
        default = ImageFont.load_default()
        for k in ["title_lg","title_md","title_sm","company","label","value","tag","hashtag","watermark"]:
            fonts[k] = default
    return fonts

def get_title_font(fonts, title):
    if len(title) <= 14:
        return fonts["title_lg"]
    elif len(title) <= 22:
        return fonts["title_md"]
    else:
        return fonts["title_sm"]

def wrap_text(title, max_chars):
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

def centered_x(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return (WIDTH - (bbox[2] - bbox[0])) // 2

def generate_card(job, post_number=0):
    fonts = load_fonts()
    img  = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rectangle([8, 8, WIDTH-8, HEIGHT-8], outline=BORDER_COLOR, width=3)
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline="#f0e8d8", width=1)
    draw.ellipse([WIDTH-300, HEIGHT-300, WIDTH+70, HEIGHT+70], outline="#e8ddd0", width=50)
    draw.ellipse([WIDTH-170, HEIGHT-430, WIDTH+30, HEIGHT-230], outline="#f0e8da", width=28)

    draw.text((65, 68), "DELHI  /  GURUGRAM", font=fonts["tag"], fill=TEXT_LIGHT)

    badge_w = 210
    bx = WIDTH - 65 - badge_w
    draw.rectangle([bx, 55, bx + badge_w, 100], outline=TEXT_DARK, width=2)
    draw.text((bx + badge_w // 2, 77), "HIRING NOW", font=fonts["tag"], fill=TEXT_DARK, anchor="mm")

    draw.line([(65, 120), (WIDTH-65, 120)], fill=BORDER_COLOR, width=1)
    job_type = job.get("type", "Full Time")
    draw.text((65, 145), f"{job_type}  .  On-site", font=fonts["label"], fill=TEXT_LIGHT)

    title = job.get("title", "Job Opening")
    if len(title) > 38:
        title = title[:36] + "..."

    font_title = get_title_font(fonts, title)
    max_chars  = 14 if font_title == fonts["title_lg"] else 20 if font_title == fonts["title_md"] else 28
    lines      = wrap_text(title, max_chars)
    line_h     = 130 if font_title == fonts["title_lg"] else 108 if font_title == fonts["title_md"] else 88

    total_h = len(lines) * line_h
    y = (HEIGHT // 2) - (total_h // 2) - 70

    for line in lines:
        x = centered_x(draw, line, font_title)
        draw.text((x, y), line, font=font_title, fill=TEXT_DARK)
        y += line_h

    company = job.get("company", "Leading Company")
    if len(company) > 30:
        company = company[:28] + "..."
    cx = centered_x(draw, company, fonts["company"])
    draw.text((cx, y + 18), company, font=fonts["company"], fill=TEXT_MID)

    div_y = HEIGHT - 270
    draw.line([(65, div_y), (WIDTH-65, div_y)], fill=BORDER_COLOR, width=2)

    salary = job.get("salary", "Competitive Salary")
    exp    = job.get("experience", "Open to all")

    draw.text((65,  div_y + 22), "SALARY",      font=fonts["label"], fill=TEXT_LIGHT)
    draw.text((65,  div_y + 52), salary,         font=fonts["value"], fill=TEXT_DARK)
    draw.text((430, div_y + 22), "EXPERIENCE",  font=fonts["label"], fill=TEXT_LIGHT)
    draw.text((430, div_y + 52), exp,            font=fonts["value"], fill=TEXT_DARK)
    draw.text((820, div_y + 22), "APPLY",        font=fonts["label"], fill=TEXT_LIGHT)
    draw.text((820, div_y + 52), "Link in bio",  font=fonts["value"], fill=TEXT_DARK)

    pools = [
        "#DelhiJobs #GurugramJobs #Hiring #JobAlert #NCRJobs",
        "#DelhiJobs #TechJobs #GurugramHiring #JobSearch #ITJobs",
        "#GurugramJobs #DelhiNCR #HiringNow #JobVacancy #CareerGoals",
        "#NaukriAlert #DelhiJobs #JobOpening #GurugramJobs #Recruitment",
        "#JobsDelhi #GurugramHiring #CareerOpportunity #DelhiNCR #Hiring",
    ]
    draw.text((65, HEIGHT - 115), pools[post_number % len(pools)], font=fonts["hashtag"], fill=TEXT_LIGHT)
    draw.text((65, HEIGHT - 75), "@delhi_gurugram_jobs", font=fonts["watermark"], fill=BORDER_COLOR)

    out = f"post_{post_number}.jpg"
    img.save(out, "JPEG", quality=95, dpi=(72, 72))
    print(f"Image saved: {out}")
    return out

if __name__ == "__main__":
    test_job = {
        "title": "Senior Software Engineer",
        "company": "Google India",
        "salary": "Rs.30L-45L/yr",
        "experience": "5-8 yrs",
        "type": "Full Time",
    }
    generate_card(test_job, 0)
