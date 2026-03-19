import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1080
BG           = "#fdf6ee"
DARK         = "#2c1f0e"
MID          = "#6b4f2e"
LIGHT        = "#b49060"
BORDER       = "#e8ddd0"
FONTS_DIR    = "fonts"

FONT_URLS = {
    "Playfair.ttf": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf",
    "Lato.ttf":     "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Bold.ttf",
    "LatoReg.ttf":  "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf",
}

def setup_fonts():
    os.makedirs(FONTS_DIR, exist_ok=True)
    for name, url in FONT_URLS.items():
        path = os.path.join(FONTS_DIR, name)
        if not os.path.exists(path):
            print(f"Downloading {name}...")
            try:
                urllib.request.urlretrieve(url, path)
                print(f"OK: {name}")
            except Exception as e:
                print(f"FAILED {name}: {e}")

def get_font(name, size):
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def cx(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return (WIDTH - (bb[2] - bb[0])) // 2

def wrap(text, max_chars):
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines[:3]

def generate_card(job, post_number=0):
    setup_fonts()

    f_title_xl = get_font("Playfair.ttf", 180)
    f_title_lg = get_font("Playfair.ttf", 150)
    f_title_md = get_font("Playfair.ttf", 115)
    f_company  = get_font("Lato.ttf",     42)
    f_label    = get_font("LatoReg.ttf",  28)
    f_value    = get_font("Lato.ttf",     36)
    f_tag      = get_font("Lato.ttf",     26)
    f_small    = get_font("LatoReg.ttf",  26)

    img  = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Borders
    draw.rectangle([8,8,WIDTH-8,HEIGHT-8], outline=BORDER, width=4)
    draw.rectangle([22,22,WIDTH-22,HEIGHT-22], outline="#f0e8d8", width=1)

    # Decorative circles
    draw.ellipse([WIDTH-320,HEIGHT-320,WIDTH+80,HEIGHT+80], outline="#e8ddd0", width=55)
    draw.ellipse([WIDTH-180,HEIGHT-440,WIDTH+40,HEIGHT-240], outline="#f0e8da", width=30)

    # Top: location
    draw.text((70, 72), "DELHI  /  GURUGRAM", font=f_tag, fill=LIGHT)

    # Top: badge
    bw = 230
    bx = WIDTH - 70 - bw
    draw.rectangle([bx, 58, bx+bw, 108], outline=DARK, width=2)
    draw.text((bx + bw//2, 83), "HIRING NOW", font=f_tag, fill=DARK, anchor="mm")

    # Thin divider
    draw.line([(70,125),(WIDTH-70,125)], fill=BORDER, width=1)

    # Job type
    jtype = job.get("type", "Full Time")
    draw.text((70, 150), f"{jtype}  ·  On-site", font=f_label, fill=LIGHT)

    # Pick title font based on length
    title = job.get("title", "Job Opening")
    if len(title) > 38:
        title = title[:36] + "..."

    if len(title) <= 12:
        ft, mc, lh = f_title_xl, 12, 195
    elif len(title) <= 20:
        ft, mc, lh = f_title_lg, 18, 165
    else:
        ft, mc, lh = f_title_md, 26, 128

    lines = wrap(title, mc)
    total_h = len(lines) * lh
    y = (HEIGHT // 2) - (total_h // 2) - 80

    for line in lines:
        x = cx(draw, line, ft)
        draw.text((x, y), line, font=ft, fill=DARK)
        y += lh

    # Company — centered
    company = job.get("company", "Leading Company")
    if len(company) > 28:
        company = company[:26] + "..."
    draw.text((cx(draw, company, f_company), y + 24), company, font=f_company, fill=MID)

    # Bottom divider
    dy = HEIGHT - 280
    draw.line([(70, dy),(WIDTH-70, dy)], fill=BORDER, width=2)

    salary = job.get("salary", "Competitive Salary")
    exp    = job.get("experience", "Open to all")

    draw.text((70,  dy+24), "SALARY",     font=f_label, fill=LIGHT)
    draw.text((70,  dy+58), salary,        font=f_value, fill=DARK)
    draw.text((430, dy+24), "EXPERIENCE", font=f_label, fill=LIGHT)
    draw.text((430, dy+58), exp,           font=f_value, fill=DARK)
    draw.text((820, dy+24), "APPLY",      font=f_label, fill=LIGHT)
    draw.text((820, dy+58), "Link in bio", font=f_value, fill=DARK)

    pools = [
        "#DelhiJobs #GurugramJobs #Hiring #JobAlert #NCRJobs",
        "#DelhiJobs #TechJobs #GurugramHiring #JobSearch #ITJobs",
        "#GurugramJobs #DelhiNCR #HiringNow #JobVacancy #CareerGoals",
        "#NaukriAlert #DelhiJobs #JobOpening #GurugramJobs #Recruitment",
        "#JobsDelhi #GurugramHiring #CareerOpportunity #DelhiNCR #Hiring",
    ]
    draw.text((70, HEIGHT-118), pools[post_number % len(pools)], font=f_small, fill=LIGHT)
    draw.text((70, HEIGHT-76),  "@delhi_gurugram_jobs", font=f_small, fill=BORDER)

    out = f"post_{post_number}.jpg"
    img.save(out, "JPEG", quality=95, dpi=(72,72))
    print(f"Saved: {out}")
    return out

if __name__ == "__main__":
    generate_card({
        "title": "Senior Software Engineer",
        "company": "Google India",
        "salary": "Rs.30L-45L/yr",
        "experience": "5-8 yrs",
        "type": "Full Time",
    }, 0)
