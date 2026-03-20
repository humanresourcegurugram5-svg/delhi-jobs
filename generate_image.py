import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import random

WIDTH, HEIGHT = 1080, 1080
FONTS_DIR = "fonts"

FONT_URLS = {
    "Bold.ttf":    "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/static/Montserrat-Bold.ttf",
    "Black.ttf":   "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/static/Montserrat-Black.ttf",
    "Regular.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/static/Montserrat-Regular.ttf",
    "Light.ttf":   "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/static/Montserrat-Light.ttf",
    "Serif.ttf":   "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/playfairdisplay/static/PlayfairDisplay-Bold.ttf",
    "SerifReg.ttf":"https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/playfairdisplay/static/PlayfairDisplay-Regular.ttf",
    "Mono.ttf":    "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/spacemono/SpaceMono-Regular.ttf",
    "MonoBold.ttf":"https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/spacemono/SpaceMono-Bold.ttf",
    "Noto.ttf":    "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosans/NotoSans-Regular.ttf",
}

TIER1 = ["google","microsoft","amazon","meta","apple","adobe","oracle",
         "salesforce","goldman sachs","mckinsey","bcg","bain","jpmorgan",
         "morgan stanley","deloitte","pwc","ey","kpmg","netflix","uber"]
TIER2 = ["tcs","infosys","wipro","hcl","cognizant","accenture","capgemini",
         "ibm","tech mahindra","hexaware","mphasis","mindtree","l&t infotech"]
STARTUPS = ["zomato","swiggy","flipkart","paytm","phonepe","razorpay","meesho",
            "nykaa","byju","unacademy","zepto","blinkit","ola","myntra","cars24",
            "urban company","policybazaar","groww","cred","lenskart","slice"]

SALARY_MAP = {
    "software engineer":        {"0-2":"Rs.5L-10L",  "2-5":"Rs.10L-20L", "5+":"Rs.20L-38L"},
    "senior software engineer": {"0-2":"Rs.10L-18L", "2-5":"Rs.18L-30L", "5+":"Rs.30L-50L"},
    "full stack developer":     {"0-2":"Rs.5L-12L",  "2-5":"Rs.12L-22L", "5+":"Rs.22L-40L"},
    "frontend developer":       {"0-2":"Rs.4L-10L",  "2-5":"Rs.10L-18L", "5+":"Rs.18L-32L"},
    "backend developer":        {"0-2":"Rs.5L-12L",  "2-5":"Rs.12L-22L", "5+":"Rs.22L-38L"},
    "data scientist":           {"0-2":"Rs.6L-14L",  "2-5":"Rs.14L-28L", "5+":"Rs.28L-50L"},
    "data analyst":             {"0-2":"Rs.4L-9L",   "2-5":"Rs.9L-18L",  "5+":"Rs.18L-32L"},
    "data engineer":            {"0-2":"Rs.6L-14L",  "2-5":"Rs.14L-26L", "5+":"Rs.26L-45L"},
    "devops engineer":          {"0-2":"Rs.6L-14L",  "2-5":"Rs.14L-26L", "5+":"Rs.26L-45L"},
    "cloud architect":          {"0-2":"Rs.12L-22L", "2-5":"Rs.22L-40L", "5+":"Rs.40L-70L"},
    "product manager":          {"0-2":"Rs.8L-18L",  "2-5":"Rs.18L-35L", "5+":"Rs.35L-65L"},
    "project manager":          {"0-2":"Rs.6L-14L",  "2-5":"Rs.14L-26L", "5+":"Rs.26L-45L"},
    "ux designer":              {"0-2":"Rs.5L-12L",  "2-5":"Rs.12L-22L", "5+":"Rs.22L-38L"},
    "ui designer":              {"0-2":"Rs.4L-10L",  "2-5":"Rs.10L-20L", "5+":"Rs.20L-35L"},
    "business analyst":         {"0-2":"Rs.5L-10L",  "2-5":"Rs.10L-20L", "5+":"Rs.20L-35L"},
    "digital marketing":        {"0-2":"Rs.3L-7L",   "2-5":"Rs.7L-15L",  "5+":"Rs.15L-28L"},
    "marketing manager":        {"0-2":"Rs.5L-10L",  "2-5":"Rs.10L-20L", "5+":"Rs.20L-38L"},
    "sales manager":            {"0-2":"Rs.4L-9L",   "2-5":"Rs.9L-18L",  "5+":"Rs.18L-32L"},
    "hr manager":               {"0-2":"Rs.4L-8L",   "2-5":"Rs.8L-16L",  "5+":"Rs.16L-28L"},
    "financial analyst":        {"0-2":"Rs.4L-10L",  "2-5":"Rs.10L-20L", "5+":"Rs.20L-38L"},
    "chartered accountant":     {"0-2":"Rs.6L-12L",  "2-5":"Rs.12L-22L", "5+":"Rs.22L-40L"},
    "operations manager":       {"0-2":"Rs.5L-12L",  "2-5":"Rs.12L-22L", "5+":"Rs.22L-40L"},
    "content writer":           {"0-2":"Rs.2L-5L",   "2-5":"Rs.5L-10L",  "5+":"Rs.10L-18L"},
    "java developer":           {"0-2":"Rs.4L-9L",   "2-5":"Rs.9L-18L",  "5+":"Rs.18L-32L"},
    "python developer":         {"0-2":"Rs.5L-11L",  "2-5":"Rs.11L-22L", "5+":"Rs.22L-40L"},
    "consultant":               {"0-2":"Rs.6L-14L",  "2-5":"Rs.14L-28L", "5+":"Rs.28L-55L"},
}

HIKE_OPTIONS = ["30-50% hike expected","25-40% hike on CTC","Up to 40% hike","30-45% hike offered"]

def get_company_tier(company):
    c = company.lower()
    for t in TIER1:
        if t in c: return "tier1"
    for t in STARTUPS:
        if t in c: return "startup"
    for t in TIER2:
        if t in c: return "tier2"
    return "unknown"

def get_exp_bracket(experience):
    if not experience: return "2-5"
    e = str(experience).lower()
    nums = [int(x) for x in e.split() if x.isdigit()]
    if not nums: return "2-5"
    n = nums[0]
    if n <= 2: return "0-2"
    if n <= 5: return "2-5"
    return "5+"

def smart_salary(salary, title, company, experience):
    garbage = ["not disclosed","na","not mentioned","best in industry","not specified","-","negotiable","as per industry","","none"]
    raw = str(salary).strip().lower() if salary else ""
    has_real = raw and raw not in garbage and len(raw) > 3
    if has_real: return str(salary).strip(), "real"
    tier = get_company_tier(company)
    title_lower = title.lower()
    exp_b = get_exp_bracket(experience)
    if tier == "tier1": return "Best in Industry", "premium"
    for key, ranges in SALARY_MAP.items():
        if key in title_lower: return ranges.get(exp_b, "Competitive Salary"), "estimated"
    if tier == "startup": return random.choice(HIKE_OPTIONS), "hike"
    if tier == "tier2": return "Competitive Salary", "market"
    return "Competitive Salary", "fallback"

def salary_label(salary_type):
    return {"real":"SALARY","estimated":"EST. SALARY","premium":"COMPENSATION","hike":"SALARY HIKE","market":"MARKET RATE","fallback":"SALARY"}.get(salary_type, "SALARY")

def setup_fonts():
    os.makedirs(FONTS_DIR, exist_ok=True)
    for name, url in FONT_URLS.items():
        path = os.path.join(FONTS_DIR, name)
        if not os.path.exists(path):
            print(f"Downloading font {name}...")
            try:
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"Font download failed {name}: {e}")

def load_fonts():
    setup_fonts()
    def f(name, size):
        path = os.path.join(FONTS_DIR, name)
        try: return ImageFont.truetype(path, size)
        except: return ImageFont.load_default()
    return {
        "black_xl": f("Black.ttf",130), "black_lg": f("Black.ttf",100),
        "black_md": f("Black.ttf",76),  "black_sm": f("Black.ttf",56),
        "bold_xl":  f("Bold.ttf",100),  "bold_lg":  f("Bold.ttf",76),
        "bold_md":  f("Bold.ttf",56),   "bold_sm":  f("Bold.ttf",38),
        "bold_xs":  f("Bold.ttf",28),   "bold_xxs": f("Bold.ttf",22),
        "reg_md":   f("Regular.ttf",38),"reg_sm":   f("Regular.ttf",28),
        "reg_xs":   f("Regular.ttf",22),"light_md": f("Light.ttf",38),
        "light_sm": f("Light.ttf",28),  "serif_xl": f("Serif.ttf",120),
        "serif_lg": f("Serif.ttf",96),  "serif_md": f("Serif.ttf",72),
        "serif_sm": f("SerifReg.ttf",50),"mono_md":  f("Mono.ttf",34),
        "mono_sm":  f("Mono.ttf",26),   "mono_xs":  f("Mono.ttf",20),
        "mono_bold":f("MonoBold.ttf",34),"noto_md":  f("Noto.ttf",38),
        "noto_sm":  f("Noto.ttf",28),
    }

def centered_x(draw, text, font, width):
    try:
        bbox = draw.textbbox((0,0), text, font=font)
        return (width - (bbox[2] - bbox[0])) // 2
    except: return width // 4

def wrap_title(title, max_chars=16):
    words = title.split()
    if len(title) <= max_chars: return [title]
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars: current = (current + " " + w).strip()
        else:
            if current: lines.append(current)
            current = w
    if current: lines.append(current)
    return lines[:3]

def truncate(text, maxlen=28):
    if not text: return ""
    return text[:maxlen-3] + "..." if len(text) > maxlen else text

def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

def today_str():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d %b %Y")

def style_dark_bold(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#0d0d0d")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 12], fill="#ff6b35")
    draw_rounded_rect(draw, [72, 60, 330, 120], 6, fill="#ff6b35")
    draw.text((90, 90), "URGENT HIRE", font=fonts["bold_xs"], fill="#ffffff")
    lines = wrap_title(job["title"], 16)
    y = 180
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#ffffff")
        y += 140
    draw.text((72, y+10), "@ " + truncate(job["company"], 28), font=fonts["bold_md"], fill="#ff6b35")
    draw.text((72, y+80), truncate(job.get("location","Delhi / Gurugram"), 30), font=fonts["reg_sm"], fill="#888888")
    draw_rounded_rect(draw, [72, 820, WIDTH-72, 960], 20, fill="#1a1a1a")
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((110, 845), slabel, font=fonts["bold_xxs"], fill="#666666")
    draw.text((110, 875), sal, font=fonts["noto_md"], fill="#ffd700")
    draw.line([(520, 840), (520, 955)], fill="#333333", width=3)
    draw.text((560, 845), "EXP", font=fonts["bold_xxs"], fill="#666666")
    draw.text((560, 875), truncate(job.get("experience","Open"), 12), font=fonts["bold_sm"], fill="#ffffff")
    draw.line([(820, 840), (820, 955)], fill="#333333", width=3)
    draw_rounded_rect(draw, [840, 855, WIDTH-80, 945], 10, fill="#ff6b35")
    draw.text((880, 900), "APPLY", font=fonts["bold_xs"], fill="#ffffff", anchor="lm")
    draw.text((72, 985), "@delhi_gurugram_jobs", font=fonts["mono_xs"], fill="#333333")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_split_layout(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 260, HEIGHT], fill="#1a3c5e")
    draw.text((40, 80), "IT", font=fonts["bold_lg"], fill="#ffffff22")
    draw.text((40, 300), "TECH", font=fonts["bold_lg"], fill="#ffffff11")
    draw.line([(40, 500), (220, 500)], fill="#ffffff33", width=2)
    company_short = truncate(job["company"], 6).upper()
    draw.text((130, 600), company_short, font=fonts["bold_md"], fill="#7eb9ff", anchor="mm")
    cat = job.get("category","IT").upper()
    draw.text((300, 72), cat + "  |  GURUGRAM", font=fonts["bold_xxs"], fill="#999999")
    lines = wrap_title(job["title"], 16)
    y = 160
    for line in lines:
        draw.text((300, y), line, font=fonts["black_lg"], fill="#1a1a1a")
        y += 130
    draw.rectangle([300, y+20, 340, y+26], fill="#1a3c5e")
    draw.text((300, y+50), truncate(job["company"], 30), font=fonts["bold_sm"], fill="#1a3c5e")
    skills = job.get("skills", ["Leadership","Strategy","Analytics"])
    if isinstance(skills, str): skills = [s.strip() for s in skills.split(",")]
    tx, ty = 300, y + 140
    for sk in skills[:4]:
        draw_rounded_rect(draw, [tx, ty, tx+len(sk)*16+20, ty+46], 6, fill="#f0f4ff", outline="#1a3c5e", width=2)
        draw.text((tx+10, ty+23), sk, font=fonts["bold_xxs"], fill="#1a3c5e", anchor="lm")
        tx += len(sk)*16+36
        if tx > 900: tx, ty = 300, ty+60
    draw.line([(300, 900), (WIDTH-60, 900)], fill="#eeeeee", width=2)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((300, 920), slabel, font=fonts["bold_xxs"], fill="#999999")
    draw.text((300, 952), sal, font=fonts["noto_md"], fill="#1a3c5e")
    draw_rounded_rect(draw, [820, 910, WIDTH-60, 990], 10, fill="#1a3c5e")
    draw.text((900, 950), "Apply", font=fonts["bold_xs"], fill="#ffffff", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_minimal_line(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#fafafa")
    draw = ImageDraw.Draw(img)
    draw.text((72, 72), "NO. {:02d}".format(random.randint(1,99)), font=fonts["mono_xs"], fill="#999999")
    draw.text((WIDTH-72, 72), today_str(), font=fonts["mono_xs"], fill="#999999", anchor="ra")
    draw.line([(72, 130), (WIDTH-72, 130)], fill="#e0e0e0", width=2)
    draw.text((72, 160), job.get("category","GENERAL").upper(), font=fonts["bold_xxs"], fill="#999999")
    lines = wrap_title(job["title"], 18)
    y = 220
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#111111")
        y += 150
    draw.line([(72, y+20), (WIDTH-72, y+20)], fill="#e0e0e0", width=2)
    draw.text((72, y+50), "COMPANY", font=fonts["bold_xxs"], fill="#bbbbbb")
    draw.text((400, y+50), "LOCATION", font=fonts["bold_xxs"], fill="#bbbbbb")
    draw.text((72, y+85), truncate(job["company"], 20), font=fonts["bold_sm"], fill="#333333")
    draw.text((400, y+85), truncate(job.get("location","Delhi NCR"), 16), font=fonts["bold_sm"], fill="#333333")
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((72, y+170), slabel, font=fonts["bold_xxs"], fill="#bbbbbb")
    draw.text((400, y+170), "EXPERIENCE", font=fonts["bold_xxs"], fill="#bbbbbb")
    draw.text((72, y+205), sal, font=fonts["noto_md"], fill="#333333")
    draw.text((400, y+205), truncate(job.get("experience","Open"), 14), font=fonts["bold_sm"], fill="#333333")
    draw.line([(72, HEIGHT-120), (WIDTH-72, HEIGHT-120)], fill="#e0e0e0", width=2)
    draw.text((72, HEIGHT-88), "@delhi_gurugram_jobs", font=fonts["mono_xs"], fill="#999999")
    draw.text((WIDTH-72, HEIGHT-88), "LINK IN BIO", font=fonts["mono_xs"], fill="#111111", anchor="ra")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_color_block(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#2d1b69")
    draw = ImageDraw.Draw(img)
    draw.ellipse([WIDTH-360, -180, WIDTH+180, 360], fill="#3d2b79")
    draw.ellipse([-180, HEIGHT-300, 240, HEIGHT+180], fill="#4d3b89")
    draw_rounded_rect(draw, [72, 72, 340, 130], 30, fill="#7c3aed")
    draw.text((206, 101), "HR & ADMIN", font=fonts["bold_xxs"], fill="#ddd6fe", anchor="mm")
    lines = wrap_title(job["title"], 16)
    y = 200
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#ffffff")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#a78bfa")
    draw_rounded_rect(draw, [72, 820, WIDTH-72, 960], 20, fill="#ffffff1a", outline="#ffffff26", width=2)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((110, 845), slabel, font=fonts["bold_xxs"], fill="#a78bfa")
    draw.text((110, 878), sal, font=fonts["noto_md"], fill="#ffffff")
    draw.line([(600, 840), (600, 955)], fill="#ffffff22", width=2)
    draw.text((640, 845), "EXP", font=fonts["bold_xxs"], fill="#a78bfa")
    draw.text((640, 878), truncate(job.get("experience","Open"),12), font=fonts["bold_sm"], fill="#ffffff")
    draw_rounded_rect(draw, [72, 975, WIDTH-72, 1050], 14, fill="#7c3aed")
    draw.text((WIDTH//2, 1012), "APPLY NOW  -  LINK IN BIO", font=fonts["bold_xs"], fill="#ffffff", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_midnight_gold(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#0c0c0c")
    draw = ImageDraw.Draw(img)
    draw.line([(80, 60), (WIDTH-80, 60)], fill="#c9a84c", width=3)
    draw.line([(80, HEIGHT-60), (WIDTH-80, HEIGHT-60)], fill="#c9a84c", width=3)
    draw.text((WIDTH//2, 110), "* PREMIUM OPENING *", font=fonts["bold_xxs"], fill="#c9a84c", anchor="mm")
    lines = wrap_title(job["title"], 18)
    y = 240
    for line in lines:
        draw.text((WIDTH//2, y), line, font=fonts["serif_lg"], fill="#ffffff", anchor="mm")
        y += 130
    draw.text((WIDTH//2, y+30), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#c9a84c", anchor="mm")
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw_rounded_rect(draw, [200, y+140, 880, y+300], 14, outline="#c9a84c44", width=2)
    draw.text((340, y+170), slabel, font=fonts["bold_xxs"], fill="#666666", anchor="mm")
    draw.text((340, y+220), sal, font=fonts["noto_md"], fill="#c9a84c", anchor="mm")
    draw.line([(540, y+155), (540, y+285)], fill="#333333", width=2)
    draw.text((700, y+170), "EXP", font=fonts["bold_xxs"], fill="#666666", anchor="mm")
    draw.text((700, y+220), truncate(job.get("experience","Open"),12), font=fonts["bold_sm"], fill="#ffffff", anchor="mm")
    draw.text((WIDTH//2, HEIGHT-90), "APPLY  -  LINK IN BIO", font=fonts["bold_xxs"], fill="#666666", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_blueprint(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#0a2240")
    draw = ImageDraw.Draw(img)
    for x in range(0, WIDTH, 80): draw.line([(x,0),(x,HEIGHT)], fill="#ffffff08", width=1)
    for y in range(0, HEIGHT, 80): draw.line([(0,y),(WIDTH,y)], fill="#ffffff08", width=1)
    draw_rounded_rect(draw, [40, 40, WIDTH-40, HEIGHT-40], 8, outline="#64a0ff33", width=2)
    draw.text((72, 80), "SYS.JOB_ID: 2026-{:04d}".format(random.randint(1,9999)), font=fonts["mono_xs"], fill="#5b9bd5")
    lines = wrap_title(job["title"], 16)
    y = 180
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#e8f4ff")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["mono_md"], fill="#5b9bd5")
    draw.text((72, y+70), truncate(job.get("location","Delhi NCR"), 24), font=fonts["mono_xs"], fill="#3a6a9a")
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw_rounded_rect(draw, [72, y+140, WIDTH-72, y+280], 8, outline="#64a0ff33", width=2)
    draw.text((100, y+165), slabel + ":", font=fonts["mono_xs"], fill="#5b9bd5")
    draw.text((100, y+205), sal, font=fonts["noto_md"], fill="#e8f4ff")
    draw.text((600, y+165), "EXP:", font=fonts["mono_xs"], fill="#5b9bd5")
    draw.text((600, y+205), truncate(job.get("experience","Open"),14), font=fonts["mono_bold"], fill="#e8f4ff")
    draw.text((72, HEIGHT-80), "-> APPLY  |  LINK IN BIO", font=fonts["mono_sm"], fill="#5b9bd5")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_typewriter(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#fafaf5")
    draw = ImageDraw.Draw(img)
    draw.text((72, 72), "--- job_post_{:03d}.txt ---".format(random.randint(1,999)), font=fonts["mono_xs"], fill="#999999")
    draw.line([(72, 120), (WIDTH-72, 120)], fill="#dddddd", width=2)
    draw.text((72, 150), "TITLE:", font=fonts["mono_sm"], fill="#666666")
    lines = wrap_title(job["title"], 18)
    y = 210
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#111111")
        y += 140
    draw.text((72, y+10), "COMPANY:", font=fonts["mono_sm"], fill="#666666")
    draw.text((72, y+60), truncate(job["company"], 28), font=fonts["mono_bold"], fill="#111111")
    draw.text((72, y+130), "LOCATION:", font=fonts["mono_sm"], fill="#666666")
    draw.text((72, y+180), truncate(job.get("location","Delhi NCR"), 24), font=fonts["mono_sm"], fill="#111111")
    draw.line([(72, y+240), (WIDTH-72, y+240)], fill="#dddddd", width=2)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((72, y+270), slabel + ":", font=fonts["mono_sm"], fill="#666666")
    draw.text((72, y+320), sal, font=fonts["noto_md"], fill="#111111")
    draw.text((580, y+270), "EXP:", font=fonts["mono_sm"], fill="#666666")
    draw.text((580, y+320), truncate(job.get("experience","Open"),14), font=fonts["mono_bold"], fill="#111111")
    draw.line([(72, HEIGHT-130), (WIDTH-72, HEIGHT-130)], fill="#dddddd", width=2)
    draw.text((72, HEIGHT-100), "HOW TO APPLY:", font=fonts["mono_sm"], fill="#666666")
    draw.text((72, HEIGHT-60), "Link in bio ->", font=fonts["mono_bold"], fill="#111111")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_neon_night(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#0a0a0f")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 8], fill="#00ff88")
    draw.text((72, 80), "> LIVE  |  HIRING NOW", font=fonts["mono_sm"], fill="#00ff88")
    lines = wrap_title(job["title"], 16)
    y = 180
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#ffffff")
        y += 140
    draw.text((72, y+10), "@ " + truncate(job["company"], 26), font=fonts["bold_sm"], fill="#00ff88")
    draw.text((72, y+80), truncate(job.get("location","Delhi NCR"), 28), font=fonts["mono_xs"], fill="#444444")
    draw_rounded_rect(draw, [72, y+140, WIDTH-72, y+300], 16, fill="#ffffff0a", outline="#00ff8833", width=2)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((110, y+165), slabel, font=fonts["bold_xxs"], fill="#666666")
    draw.text((110, y+200), sal, font=fonts["noto_md"], fill="#00ff88")
    draw.line([(580, y+155), (580, y+285)], fill="#ffffff11", width=2)
    draw.text((620, y+165), "EXP", font=fonts["bold_xxs"], fill="#666666")
    draw.text((620, y+200), truncate(job.get("experience","Open"),12), font=fonts["bold_sm"], fill="#ffffff")
    draw_rounded_rect(draw, [72, y+320, WIDTH-72, y+420], 14, fill="#00ff88")
    draw.text((WIDTH//2, y+370), "APPLY  -  LINK IN BIO", font=fonts["bold_sm"], fill="#000000", anchor="mm")
    draw.text((72, HEIGHT-60), "@delhi_gurugram_jobs", font=fonts["mono_xs"], fill="#333333")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_red_alert(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 420], fill="#dc2626")
    draw.text((72, 80), "URGENT REQUIREMENT", font=fonts["bold_xxs"], fill="#ffffff99")
    lines = wrap_title(job["title"], 16)
    y = 150
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#ffffff")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#ffffff99")
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw_rounded_rect(draw, [72, 490, 520, 650], 14, fill="#fef2f2")
    draw.text((296, 530), slabel, font=fonts["bold_xxs"], fill="#dc2626", anchor="mm")
    draw.text((296, 575), sal, font=fonts["noto_md"], fill="#1a0000", anchor="mm")
    draw_rounded_rect(draw, [540, 490, WIDTH-72, 650], 14, fill="#fef2f2")
    draw.text((760, 530), "EXP", font=fonts["bold_xxs"], fill="#dc2626", anchor="mm")
    draw.text((760, 575), truncate(job.get("experience","Open"),12), font=fonts["bold_sm"], fill="#1a0000", anchor="mm")
    draw_rounded_rect(draw, [72, 680, WIDTH-72, 800], 14, fill="#dc2626")
    draw.text((WIDTH//2, 740), "APPLY NOW  -  LINK IN BIO", font=fonts["bold_sm"], fill="#ffffff", anchor="mm")
    draw.text((72, 840), truncate(job.get("location","Delhi NCR"), 28), font=fonts["reg_sm"], fill="#999999")
    draw.text((72, 890), "@delhi_gurugram_jobs", font=fonts["reg_xs"], fill="#cccccc")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_teal_modern(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#e6faf5")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 14], fill="#0d9488")
    draw_rounded_rect(draw, [72, 60, 280, 118], 30, fill="#0d9488")
    draw.text((176, 89), "NEW", font=fonts["bold_sm"], fill="#ffffff", anchor="mm")
    lines = wrap_title(job["title"], 18)
    y = 180
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#0f2825")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#0d9488")
    draw.text((72, y+80), truncate(job.get("location","Delhi NCR"), 28), font=fonts["reg_sm"], fill="#5e9e96")
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw_rounded_rect(draw, [72, y+150, WIDTH-72, y+310], 16, fill="#ffffff", outline="#b2e8df", width=3)
    draw.text((110, y+175), slabel, font=fonts["bold_xxs"], fill="#0d9488")
    draw.text((110, y+210), sal, font=fonts["noto_md"], fill="#0f2825")
    draw.line([(580, y+165), (580, y+295)], fill="#b2e8df", width=2)
    draw.text((620, y+175), "EXP", font=fonts["bold_xxs"], fill="#0d9488")
    draw.text((620, y+210), truncate(job.get("experience","Open"),14), font=fonts["bold_sm"], fill="#0f2825")
    draw.text((WIDTH//2, HEIGHT-80), "APPLY  |  LINK IN BIO", font=fonts["bold_xs"], fill="#0d9488", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_saffron(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#fff8f0")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 16], fill="#ff6600")
    draw.rectangle([0, 16, WIDTH, 28], fill="#ff9900")
    draw.rectangle([0, 28, WIDTH, 40], fill="#ffcc00")
    draw_rounded_rect(draw, [WIDTH-260, 68, WIDTH-60, 126], 6, fill="#ff6600")
    draw.text((WIDTH-160, 97), "HIRING", font=fonts["bold_sm"], fill="#ffffff", anchor="mm")
    draw.text((72, 80), truncate(job.get("location","Gurugram"), 22).upper() + "  |  FULL TIME", font=fonts["bold_xxs"], fill="#cc5500")
    lines = wrap_title(job["title"], 18)
    y = 180
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#1a0a00")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#cc5500")
    draw.line([(72, y+90), (WIDTH-72, y+90)], fill="#ffcc0066", width=3)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((72, y+120), slabel, font=fonts["bold_xxs"], fill="#cc5500")
    draw.text((72, y+158), sal, font=fonts["noto_md"], fill="#1a0a00")
    draw.text((560, y+120), "EXP", font=fonts["bold_xxs"], fill="#cc5500")
    draw.text((560, y+158), truncate(job.get("experience","Open"),14), font=fonts["bold_sm"], fill="#1a0a00")
    draw.text((WIDTH-72, HEIGHT-72), "Bio link ->", font=fonts["bold_xs"], fill="#cc5500", anchor="ra")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_newspaper(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#f8f4ee")
    draw = ImageDraw.Draw(img)
    draw.line([(72, 80), (WIDTH-72, 80)], fill="#111111", width=6)
    draw.line([(72, 96), (WIDTH-72, 96)], fill="#111111", width=6)
    draw.text((WIDTH//2, 140), "DELHI NCR EMPLOYMENT GAZETTE", font=fonts["bold_xxs"], fill="#111111", anchor="mm")
    draw.text((WIDTH//2, 185), today_str().upper() + "  -  HIRING EDITION", font=fonts["mono_xs"], fill="#888888", anchor="mm")
    draw.line([(72, 220), (WIDTH-72, 220)], fill="#111111", width=3)
    lines = wrap_title(job["title"], 18)
    y = 290
    for line in lines:
        cx = centered_x(draw, line, fonts["serif_xl"], WIDTH)
        draw.text((cx, y), line, font=fonts["serif_xl"], fill="#111111")
        y += 150
    draw.line([(72, y+20), (WIDTH-72, y+20)], fill="#111111", width=2)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((72, y+60), "COMPANY", font=fonts["bold_xxs"], fill="#555555")
    draw.text((500, y+60), slabel, font=fonts["bold_xxs"], fill="#555555")
    draw.text((72, y+100), truncate(job["company"],22), font=fonts["bold_sm"], fill="#111111")
    draw.text((500, y+100), sal, font=fonts["noto_md"], fill="#111111")
    draw.text((72, y+180), "EXPERIENCE", font=fonts["bold_xxs"], fill="#555555")
    draw.text((500, y+180), "HOW TO APPLY", font=fonts["bold_xxs"], fill="#555555")
    draw.text((72, y+220), truncate(job.get("experience","Open"),18), font=fonts["bold_sm"], fill="#111111")
    draw.text((500, y+220), "Link in bio", font=fonts["bold_sm"], fill="#111111")
    draw.line([(72, HEIGHT-100), (WIDTH-72, HEIGHT-100)], fill="#111111", width=2)
    draw.text((WIDTH//2, HEIGHT-60), "@delhi_gurugram_jobs", font=fonts["mono_xs"], fill="#aaaaaa", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_forest_green(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#0d2818")
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, [72, 72, 200, 200], 16, outline="#4ade80", width=4)
    draw.rectangle([100, 100, 172, 172], fill="#4ade80")
    draw.text((72, 240), "REMOTE-FRIENDLY  |  IT & TECH", font=fonts["bold_xxs"], fill="#4ade80")
    lines = wrap_title(job["title"], 16)
    y = 310
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#ffffff")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#86efac")
    draw.text((72, y+80), truncate(job.get("location","Delhi NCR"), 28), font=fonts["reg_sm"], fill="#4ade8066")
    draw.line([(72, y+150), (WIDTH-72, y+150)], fill="#ffffff11", width=2)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((72, y+180), slabel, font=fonts["bold_xxs"], fill="#4ade8088")
    draw.text((72, y+220), sal, font=fonts["noto_md"], fill="#4ade80")
    draw.text((580, y+180), "EXP", font=fonts["bold_xxs"], fill="#4ade8088")
    draw.text((580, y+220), truncate(job.get("experience","Open"),14), font=fonts["bold_sm"], fill="#ffffff")
    draw_rounded_rect(draw, [72, y+300, WIDTH-72, y+400], 14, fill="#4ade80")
    draw.text((WIDTH//2, y+350), "APPLY  -  LINK IN BIO", font=fonts["bold_sm"], fill="#0d2818", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_carbon_dark(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#18181b")
    draw = ImageDraw.Draw(img)
    draw_rounded_rect(draw, [WIDTH-190, 60, WIDTH-60, 190], 50, outline="#3f3f46", width=3)
    initials = "".join(w[0].upper() for w in job["company"].split()[:2])
    draw.text((WIDTH-125, 125), initials, font=fonts["bold_sm"], fill="#71717a", anchor="mm")
    draw.text((72, 80), "ROLE  |  2026", font=fonts["mono_xs"], fill="#52525b")
    lines = wrap_title(job["title"], 16)
    y = 200
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#fafafa")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#a1a1aa")
    draw.line([(72, y+90), (WIDTH-72, y+90)], fill="#27272a", width=3)
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw_rounded_rect(draw, [72, y+120, 520, y+270], 12, fill="#27272a")
    draw.text((296, y+145), slabel, font=fonts["bold_xxs"], fill="#71717a", anchor="mm")
    draw.text((296, y+200), sal, font=fonts["noto_md"], fill="#fafafa", anchor="mm")
    draw_rounded_rect(draw, [540, y+120, WIDTH-72, y+270], 12, fill="#27272a")
    draw.text((760, y+145), "EXP", font=fonts["bold_xxs"], fill="#71717a", anchor="mm")
    draw.text((760, y+200), truncate(job.get("experience","Open"),12), font=fonts["bold_sm"], fill="#fafafa", anchor="mm")
    draw_rounded_rect(draw, [72, y+300, WIDTH-72, y+420], 12, fill="#3f3f46")
    draw.text((WIDTH//2, y+360), "APPLY  -  LINK IN BIO", font=fonts["bold_xs"], fill="#fafafa", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_lavender(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#f5f3ff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 16, HEIGHT], fill="#7c3aed")
    draw_rounded_rect(draw, [72, 68, 380, 126], 30, fill="#ede9fe")
    draw.text((226, 97), "HR & TALENT", font=fonts["bold_xs"], fill="#5b21b6", anchor="mm")
    draw.text((WIDTH-72, 97), today_str(), font=fonts["reg_xs"], fill="#a78bfa", anchor="ra")
    lines = wrap_title(job["title"], 18)
    y = 200
    for line in lines:
        draw.text((72, y), line, font=fonts["black_xl"], fill="#1e0050")
        y += 140
    draw.text((72, y+10), truncate(job["company"], 28), font=fonts["bold_sm"], fill="#7c3aed")
    draw.text((72, y+80), truncate(job.get("location","Delhi NCR"), 28), font=fonts["reg_sm"], fill="#a78bfa")
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw_rounded_rect(draw, [72, y+150, WIDTH-72, y+310], 16, fill="#ede9fe")
    draw.text((110, y+175), slabel, font=fonts["bold_xxs"], fill="#7c3aed")
    draw.text((110, y+210), sal, font=fonts["noto_md"], fill="#1e0050")
    draw.line([(580, y+162), (580, y+296)], fill="#c4b5fd", width=2)
    draw.text((620, y+175), "EXP", font=fonts["bold_xxs"], fill="#7c3aed")
    draw.text((620, y+210), truncate(job.get("experience","Open"),14), font=fonts["bold_sm"], fill="#1e0050")
    draw_rounded_rect(draw, [72, y+330, WIDTH-72, y+430], 14, fill="#7c3aed")
    draw.text((WIDTH//2, y+380), "APPLY  -  LINK IN BIO", font=fonts["bold_sm"], fill="#ffffff", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

def style_retro_stamp(job, fonts, output):
    img  = Image.new("RGB", (WIDTH, HEIGHT), "#f5f0e8")
    draw = ImageDraw.Draw(img)
    seg = 40
    for x in range(72, WIDTH-72, seg*2):
        draw.line([(x, 72), (x+seg, 72)], fill="#2c1f0e", width=4)
        draw.line([(x, HEIGHT-72), (x+seg, HEIGHT-72)], fill="#2c1f0e", width=4)
    for y in range(72, HEIGHT-72, seg*2):
        draw.line([(72, y), (72, y+seg)], fill="#2c1f0e", width=4)
        draw.line([(WIDTH-72, y), (WIDTH-72, y+seg)], fill="#2c1f0e", width=4)
    draw.text((WIDTH//2, 160), "* JOB OPENING *", font=fonts["bold_xs"], fill="#2c1f0e", anchor="mm")
    draw.text((WIDTH//2, 230), truncate(job["company"], 26), font=fonts["serif_sm"], fill="#8b6914", anchor="mm")
    lines = wrap_title(job["title"], 18)
    y = 330
    for line in lines:
        cx = centered_x(draw, line, fonts["serif_xl"], WIDTH)
        draw.text((cx, y), line, font=fonts["serif_xl"], fill="#2c1f0e")
        y += 150
    sal, stype = smart_salary(job.get("salary"), job.get("title",""), job.get("company",""), job.get("experience",""))
    slabel = salary_label(stype)
    draw.text((300, y+70), slabel, font=fonts["bold_xxs"], fill="#8b6914", anchor="mm")
    draw.text((700, y+70), "CITY", font=fonts["bold_xxs"], fill="#8b6914", anchor="mm")
    draw.text((300, y+115), sal, font=fonts["noto_md"], fill="#2c1f0e", anchor="mm")
    draw.text((700, y+115), truncate(job.get("location","Gurugram"),14), font=fonts["bold_sm"], fill="#2c1f0e", anchor="mm")
    draw.text((WIDTH//2, y+200), "APPLY  |  LINK IN BIO", font=fonts["bold_xxs"], fill="#8b6914", anchor="mm")
    draw.text((WIDTH//2, HEIGHT-100), "@delhi_gurugram_jobs", font=fonts["mono_xs"], fill="#b49060", anchor="mm")
    img.save(output, "JPEG", quality=95, dpi=(72,72))
    return output

ALL_STYLES = [
    style_dark_bold,
    style_split_layout,
    style_minimal_line,
    style_color_block,
    style_midnight_gold,
    style_blueprint,
    style_typewriter,
    style_neon_night,
    style_red_alert,
    style_teal_modern,
    style_saffron,
    style_newspaper,
    style_forest_green,
    style_carbon_dark,
    style_lavender,
    style_retro_stamp,
]

def pick_style(slot):
    ist = pytz.timezone("Asia/Kolkata")
    day = datetime.now(ist).weekday()
    idx = (day * 4 + slot) % len(ALL_STYLES)
    return ALL_STYLES[idx]

def generate_card(job, slot=0):
    fonts = load_fonts()
    output = f"post_slot{slot}_{datetime.now().strftime('%H%M%S')}.jpg"
    style_fn = pick_style(slot)
    print(f"Using style: {style_fn.__name__}")
    try:
        return style_fn(job, fonts, output)
    except Exception as e:
        print(f"Style {style_fn.__name__} failed: {e} — using dark bold")
        return style_dark_bold(job, fonts, output)

if __name__ == "__main__":
    test_job = {
        "title": "Senior Software Engineer",
        "company": "Google India",
        "location": "Gurugram, Haryana",
        "salary": "",
        "experience": "4-8 yrs",
        "category": "IT",
        "skills": ["Python", "Cloud", "APIs"],
    }
    for slot in range(4):
        path = generate_card(test_job, slot)
        print(f"Slot {slot} -> {path}")
