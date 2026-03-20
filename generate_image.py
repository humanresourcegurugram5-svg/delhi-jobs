import os
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz

WIDTH, HEIGHT = 1080, 1080

# ── System fonts pre-installed on GitHub Actions Ubuntu runners ──────────────
# No downloading needed — these are always available
FONT_PATHS = {
    "bold":    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "medium":  "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
    "regular": "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
    "light":   "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
    "serif":   "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf",
    "mono":    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    # Fallback if somehow missing
    "fallback":"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

IST = pytz.timezone("Asia/Kolkata")


def load_fonts():
    """Load Poppins system fonts at various sizes."""
    def F(key, size):
        path = FONT_PATHS.get(key, FONT_PATHS["fallback"])
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
        # Try fallback
        fb = FONT_PATHS["fallback"]
        if os.path.exists(fb):
            return ImageFont.truetype(fb, size)
        return ImageFont.load_default()

    return {
        "title_xl":  F("bold",    92),
        "title_lg":  F("bold",    76),
        "title_md":  F("bold",    60),
        "company":   F("medium",  48),
        "label":     F("regular", 34),
        "value":     F("bold",    38),
        "tag":       F("medium",  30),
        "small":     F("light",   28),
        "badge":     F("bold",    28),
        "mono":      F("mono",    32),
    }


def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=2):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)


def salary_text(job):
    s = job.get("salary", "")
    if s and s not in ("", "Competitive Salary"):
        return s
    return "Competitive Salary"


def exp_text(job):
    e = job.get("experience", "")
    if e and e not in ("", "Not specified"):
        return e
    return "Open to all"


def location_text(job):
    loc = job.get("location", "Delhi / Gurugram")
    if not loc or loc.strip() == "":
        return "Delhi / Gurugram"
    return loc


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 1 — Deep Purple Gradient
# ══════════════════════════════════════════════════════════════════════════════
def style_deep_purple(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#1a0533")
    draw = ImageDraw.Draw(img)

    # Gradient overlay via bands
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(26 + ratio * 30)
        g = int(5 + ratio * 10)
        b = int(51 + ratio * 40)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Decorative circles
    draw.ellipse([600, -200, 1200, 400], fill="#2d0a5e")
    draw.ellipse([-100, 700, 400, 1200], fill="#220845")

    # Top badge
    draw_rounded_rect(draw, [60, 60, 340, 115], 30, fill="#7c3aed")
    draw.text((200, 87), "DELHI JOBS", font=fonts["badge"], fill="white", anchor="mm")

    # Location pill
    loc = location_text(job)
    draw.text((WIDTH - 80, 87), f"📍 {loc}", font=fonts["small"], fill="#c4b5fd", anchor="rm")

    # Job title — big and centered
    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="white", anchor="mm")
        y_title += int(title_font.size * 1.2)

    # Company
    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#a78bfa", anchor="mm")

    # Divider
    draw.line([(80, 620), (WIDTH - 80, 620)], fill="#4c1d95", width=2)

    # Info row
    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#2d0a5e")
    # Salary
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#c4b5fd")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    # Experience
    draw.text((600, 675), "EXPERIENCE", font=fonts["label"], fill="#c4b5fd")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    # Apply button
    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#7c3aed")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="white", anchor="mm")

    # Hashtags
    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#7c3aed", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 2 — Electric Blue
# ══════════════════════════════════════════════════════════════════════════════
def style_electric_blue(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#0a0f2e")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 + ratio * 5)
        g = int(15 + ratio * 20)
        b = int(46 + ratio * 50)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Accent shapes
    draw.ellipse([700, -150, 1250, 400], fill="#0d1b4b")
    draw.polygon([(0, 900), (400, 700), (0, 700)], fill="#061030")

    # Neon accent bar
    draw.rectangle([0, 0, 8, HEIGHT], fill="#00d4ff")

    # Badge
    draw_rounded_rect(draw, [40, 55, 320, 110], 30, fill="#00d4ff")
    draw.text((180, 82), "HIRING NOW", font=fonts["badge"], fill="#0a0f2e", anchor="mm")

    loc = location_text(job)
    draw.text((WIDTH - 60, 82), f"📍 {loc}", font=fonts["small"], fill="#60a5fa", anchor="rm")

    # Title
    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="#ffffff", anchor="mm")
        y_title += int(title_font.size * 1.2)

    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#00d4ff", anchor="mm")

    draw.line([(60, 620), (WIDTH - 60, 620)], fill="#1e3a8a", width=2)

    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#0d1b4b")
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#60a5fa")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    draw.text((600, 675), "EXP", font=fonts["label"], fill="#60a5fa")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#00d4ff")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="#0a0f2e", anchor="mm")

    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#1d4ed8", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 3 — Forest Green
# ══════════════════════════════════════════════════════════════════════════════
def style_forest_green(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#052e16")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(5 + ratio * 10)
        g = int(46 + ratio * 30)
        b = int(22 + ratio * 20)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    draw.ellipse([650, -100, 1180, 430], fill="#064e3b")
    draw.ellipse([-80, 750, 350, 1180], fill="#022c22")

    draw.rectangle([0, 0, 8, HEIGHT], fill="#4ade80")

    draw_rounded_rect(draw, [40, 55, 320, 110], 30, fill="#16a34a")
    draw.text((180, 82), "NEW OPENING", font=fonts["badge"], fill="white", anchor="mm")

    loc = location_text(job)
    draw.text((WIDTH - 60, 82), f"📍 {loc}", font=fonts["small"], fill="#86efac", anchor="rm")

    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="white", anchor="mm")
        y_title += int(title_font.size * 1.2)

    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#4ade80", anchor="mm")

    draw.line([(60, 620), (WIDTH - 60, 620)], fill="#064e3b", width=2)
    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#022c22")
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#86efac")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    draw.text((600, 675), "EXP", font=fonts["label"], fill="#86efac")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#16a34a")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="white", anchor="mm")

    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#16a34a", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 4 — Crimson Red
# ══════════════════════════════════════════════════════════════════════════════
def style_crimson(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#1a0000")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(26 + ratio * 50)
        g = int(0 + ratio * 5)
        b = int(0 + ratio * 5)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    draw.ellipse([620, -120, 1200, 460], fill="#450a0a")
    draw.rectangle([0, 0, 8, HEIGHT], fill="#ef4444")

    draw_rounded_rect(draw, [40, 55, 300, 110], 30, fill="#dc2626")
    draw.text((170, 82), "URGENT HIRE", font=fonts["badge"], fill="white", anchor="mm")

    loc = location_text(job)
    draw.text((WIDTH - 60, 82), f"📍 {loc}", font=fonts["small"], fill="#fca5a5", anchor="rm")

    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="white", anchor="mm")
        y_title += int(title_font.size * 1.2)

    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#f87171", anchor="mm")

    draw.line([(60, 620), (WIDTH - 60, 620)], fill="#450a0a", width=2)
    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#2d0000")
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#fca5a5")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    draw.text((600, 675), "EXP", font=fonts["label"], fill="#fca5a5")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#dc2626")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="white", anchor="mm")

    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#dc2626", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 5 — Midnight Gold
# ══════════════════════════════════════════════════════════════════════════════
def style_midnight_gold(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#0f0a00")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(15 + ratio * 20)
        g = int(10 + ratio * 15)
        b = int(0)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    draw.ellipse([600, -150, 1200, 450], fill="#1a1100")
    draw.rectangle([0, 0, 8, HEIGHT], fill="#f59e0b")

    draw_rounded_rect(draw, [40, 55, 280, 110], 30, fill="#b45309")
    draw.text((160, 82), "TOP ROLE", font=fonts["badge"], fill="white", anchor="mm")

    loc = location_text(job)
    draw.text((WIDTH - 60, 82), f"📍 {loc}", font=fonts["small"], fill="#fcd34d", anchor="rm")

    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="#fbbf24", anchor="mm")
        y_title += int(title_font.size * 1.2)

    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#fcd34d", anchor="mm")

    draw.line([(60, 620), (WIDTH - 60, 620)], fill="#78350f", width=2)
    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#1a1100")
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#fcd34d")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    draw.text((600, 675), "EXP", font=fonts["label"], fill="#fcd34d")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#b45309")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="white", anchor="mm")

    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#b45309", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 6 — Slate Corporate
# ══════════════════════════════════════════════════════════════════════════════
def style_slate(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#0f172a")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(15 + ratio * 15)
        g = int(23 + ratio * 20)
        b = int(42 + ratio * 30)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    draw.ellipse([650, -100, 1200, 450], fill="#1e293b")
    draw.rectangle([0, 0, 8, HEIGHT], fill="#38bdf8")

    draw_rounded_rect(draw, [40, 55, 300, 110], 30, fill="#0369a1")
    draw.text((170, 82), "JOB ALERT", font=fonts["badge"], fill="white", anchor="mm")

    loc = location_text(job)
    draw.text((WIDTH - 60, 82), f"📍 {loc}", font=fonts["small"], fill="#7dd3fc", anchor="rm")

    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="white", anchor="mm")
        y_title += int(title_font.size * 1.2)

    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#38bdf8", anchor="mm")

    draw.line([(60, 620), (WIDTH - 60, 620)], fill="#1e293b", width=2)
    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#0f172a")
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#7dd3fc")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    draw.text((600, 675), "EXP", font=fonts["label"], fill="#7dd3fc")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#0369a1")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="white", anchor="mm")

    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#0369a1", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 7 — Orange Fire
# ══════════════════════════════════════════════════════════════════════════════
def style_orange_fire(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#1c0700")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(28 + ratio * 60)
        g = int(7 + ratio * 20)
        b = 0
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    draw.ellipse([600, -120, 1180, 460], fill="#431407")
    draw.rectangle([0, 0, 8, HEIGHT], fill="#f97316")

    draw_rounded_rect(draw, [40, 55, 300, 110], 30, fill="#ea580c")
    draw.text((170, 82), "HOT JOB", font=fonts["badge"], fill="white", anchor="mm")

    loc = location_text(job)
    draw.text((WIDTH - 60, 82), f"📍 {loc}", font=fonts["small"], fill="#fed7aa", anchor="rm")

    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="white", anchor="mm")
        y_title += int(title_font.size * 1.2)

    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#fb923c", anchor="mm")

    draw.line([(60, 620), (WIDTH - 60, 620)], fill="#431407", width=2)
    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#1c0700")
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#fed7aa")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    draw.text((600, 675), "EXP", font=fonts["label"], fill="#fed7aa")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#ea580c")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="white", anchor="mm")

    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#ea580c", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE 8 — Teal Minimal
# ══════════════════════════════════════════════════════════════════════════════
def style_teal(job, fonts, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#042f2e")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(4 + ratio * 10)
        g = int(47 + ratio * 30)
        b = int(46 + ratio * 30)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    draw.ellipse([630, -100, 1180, 450], fill="#134e4a")
    draw.rectangle([0, 0, 8, HEIGHT], fill="#2dd4bf")

    draw_rounded_rect(draw, [40, 55, 280, 110], 30, fill="#0f766e")
    draw.text((160, 82), "APPLY NOW", font=fonts["badge"], fill="white", anchor="mm")

    loc = location_text(job)
    draw.text((WIDTH - 60, 82), f"📍 {loc}", font=fonts["small"], fill="#99f6e4", anchor="rm")

    title = job.get("title", "Job Opening")
    title_font = fonts["title_xl"] if len(title) <= 25 else fonts["title_lg"] if len(title) <= 40 else fonts["title_md"]
    lines = wrap_text(draw, title.upper(), title_font, WIDTH - 120)
    y_title = 200
    for line in lines[:3]:
        draw.text((WIDTH // 2, y_title), line, font=title_font, fill="white", anchor="mm")
        y_title += int(title_font.size * 1.2)

    company = job.get("company", "")
    draw.text((WIDTH // 2, y_title + 30), f"@ {company}", font=fonts["company"], fill="#2dd4bf", anchor="mm")

    draw.line([(60, 620), (WIDTH - 60, 620)], fill="#134e4a", width=2)
    draw_rounded_rect(draw, [60, 640, WIDTH - 60, 780], 20, fill="#042f2e")
    draw.text((120, 675), "SALARY", font=fonts["label"], fill="#99f6e4")
    draw.text((120, 715), salary_text(job), font=fonts["value"], fill="white")
    draw.text((600, 675), "EXP", font=fonts["label"], fill="#99f6e4")
    draw.text((600, 715), exp_text(job), font=fonts["value"], fill="white")

    draw_rounded_rect(draw, [60, 820, WIDTH - 60, 920], 30, fill="#0f766e")
    draw.text((WIDTH // 2, 870), "APPLY NOW — LINK IN BIO", font=fonts["value"], fill="white", anchor="mm")

    draw.text((WIDTH // 2, 970), "#DelhiJobs #GurugramJobs #Hiring", font=fonts["small"], fill="#0f766e", anchor="mm")

    img.save(output, quality=95)
    return output


# ══════════════════════════════════════════════════════════════════════════════
#  DISPATCHER
# ══════════════════════════════════════════════════════════════════════════════
ALL_STYLES = [
    style_deep_purple,
    style_electric_blue,
    style_forest_green,
    style_crimson,
    style_midnight_gold,
    style_slate,
    style_orange_fire,
    style_teal,
]


def generate_card(job, slot=0):
    fonts = load_fonts()
    output = f"/tmp/job_post_{slot}.jpg"

    # Pick style based on day + slot for variety
    day_of_year = datetime.now(IST).timetuple().tm_yday
    style_idx = (day_of_year * 4 + slot) % len(ALL_STYLES)
    style_fn = ALL_STYLES[style_idx]
    style_name = style_fn.__name__

    print(f"Using style: {style_name}")
    return style_fn(job, fonts, output)


# ── Local test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_job = {
        "title": "Senior Software Engineer",
        "company": "TechCorp India",
        "location": "Gurugram",
        "salary": "₹18-25 LPA",
        "experience": "3-5 years",
    }
    for i, style_fn in enumerate(ALL_STYLES):
        fonts = load_fonts()
        out = f"/tmp/test_style_{i}.jpg"
        style_fn(test_job, fonts, out)
        print(f"Saved: {out}")
