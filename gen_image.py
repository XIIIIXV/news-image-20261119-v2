#!/usr/bin/env python3
"""Thursday 19 November 2026 — one-day front page for make.fun.

Builds a 1024x1024 PNG front page carrying 52 news stories, all dated
Thursday 19 November 2026.  Everything is drawn with PIL primitives
(rectangles, ellipses, polygons, lines); no photos, no network, no
randomness, so repeated runs produce identical bytes.

Usage:
    python3 gen_image.py            # writes entry.png next to this file
"""

import json
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(HERE), "stories-19nov.json")
TARGET = os.path.join(HERE, "entry.png")

CANVAS_W = 1024
CANVAS_H = 1024
MARGIN = 14
INNER = CANVAS_W - 2 * MARGIN  # 996

PAPER = (250, 244, 230)
INK = (18, 18, 18)
SOFT_INK = (70, 66, 60)
RED = (178, 34, 34)
DARK_RED = (139, 0, 0)
RULE = (120, 110, 95)
CARD_BG = (255, 252, 244)
CARD_EDGE = (190, 180, 160)
PANEL = (238, 232, 216)
SKY = (214, 228, 238)

REGION_PAINT = {
    "ASIA": (176, 138, 20),
    "EUROPE": (46, 111, 176),
    "AMERICAS": (178, 52, 40),
    "MIDDLE EAST": (204, 102, 20),
    "GLOBAL": (106, 76, 160),
    "AFRICA": (34, 139, 110),
    "OCEANIA": (32, 140, 164),
}

# Rough lon/lat for each card's story, used only to place its map pin.
PIN_LONLAT = {
    1: (115, 22), 2: (4, 52), 3: (30, 36), 4: (-74, 40),
    5: (47, 25), 6: (85, 18), 7: (-80, 26), 8: (127, 37),
    9: (10, 56), 10: (36, 45), 11: (90, 24), 12: (149, -35),
    13: (-74, 5), 14: (37, -1), 15: (-74, 41), 16: (-77, 39),
}

FONT_DIR = "/usr/share/fonts/truetype"


def pick_font(name, size):
    """Return a truetype font, falling back through known local families."""
    candidates = {
        "serif_b": ["liberation/LiberationSerif-Bold.ttf",
                    "dejavu/DejaVuSerif-Bold.ttf"],
        "serif": ["liberation/LiberationSerif-Regular.ttf",
                  "dejavu/DejaVuSerif.ttf"],
        "sans_b": ["liberation/LiberationSans-Bold.ttf",
                   "dejavu/DejaVuSans-Bold.ttf"],
        "sans": ["liberation/LiberationSans-Regular.ttf",
                 "dejavu/DejaVuSans.ttf"],
    }
    for rel in candidates[name]:
        path = os.path.join(FONT_DIR, rel)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


class TypeCase:
    """All fonts used on the page, sized once."""

    def __init__(self):
        self.masthead = pick_font("serif_b", 56)
        self.kicker = pick_font("sans_b", 11)
        self.strap = pick_font("serif", 15)
        self.big_num = pick_font("serif_b", 21)
        self.stat_lab = pick_font("sans", 9)
        self.strip = pick_font("sans_b", 11)
        self.strip_sm = pick_font("sans_b", 9)
        self.time = pick_font("sans_b", 9)
        self.time_txt = pick_font("sans", 9)
        self.tag = pick_font("sans_b", 8)
        self.head_l = pick_font("serif_b", 16)
        self.head_m = pick_font("serif_b", 13)
        self.head_s = pick_font("serif_b", 12)
        self.deck_l = pick_font("sans", 11)
        self.deck_m = pick_font("sans", 10)
        self.deck_s = pick_font("sans", 9)
        self.src = pick_font("sans", 8)
        self.sec = pick_font("sans_b", 13)
        self.also = pick_font("sans", 10)
        self.also_n = pick_font("sans_b", 10)
        self.num_big = pick_font("serif_b", 17)
        self.num_lab = pick_font("sans", 8)
        self.legend = pick_font("sans", 9)
        self.legend_b = pick_font("sans_b", 9)
        self.date_t = pick_font("sans_b", 12)
        self.date_b = pick_font("sans", 9)
        self.foot = pick_font("sans", 8)


def load_stories():
    with open(SOURCE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def wrap(draw, text, font, width):
    """Greedy word wrap using real pixel widths."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, text, font, x, y, width, fill, spacing=1):
    lines = wrap(draw, text, font, width)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + spacing
    return y


def fit_lines(draw, text, font, width, max_lines):
    """Wrap text and clip to max_lines, adding an ellipsis if clipped."""
    lines = wrap(draw, text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "…", font=font) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


def paint_motif(draw, box, kind):
    """Flat vector illustration inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2

    def person(px, py, suit, skin=(232, 190, 150)):
        draw.ellipse([px - 7, py - 16, px + 7, py - 2], fill=skin)
        draw.polygon([(px - 12, py + 16), (px + 12, py + 16),
                      (px + 9, py - 2), (px - 9, py - 2)], fill=suit)

    if kind == "summit":
        draw.rectangle(box, fill=(126, 164, 196))
        draw.rectangle([x0, y1 - 14, x1, y1], fill=(96, 64, 32))
        for i, (flag, suit) in enumerate(
                [((178, 34, 34), (30, 30, 30)),
                 ((204, 0, 0), (20, 60, 120)),
                 ((40, 90, 160), (90, 30, 30))]):
            px = x0 + 45 + i * 75
            person(px, y1 - 30, suit)
            draw.line([px + 12, y1 - 52, px + 12, y1 - 22], fill=INK, width=2)
            draw.polygon([(px + 12, y1 - 52), (px + 34, y1 - 46),
                          (px + 12, y1 - 40)], fill=flag)
        draw.text((x0 + 6, y0 + 4), "APEC 2026 · SHENZHEN",
                  font=pick_font("sans_b", 9), fill=(255, 255, 255))
    elif kind == "court":
        draw.rectangle(box, fill=(222, 210, 186))
        draw.rectangle([x0 + 30, y0 + 8, x1 - 30, y0 + 16], fill=(139, 69, 19))
        for i in range(4):
            px = x0 + 42 + i * 52
            draw.rectangle([px, y0 + 16, px + 12, y1 - 10], fill=(245, 240, 225))
        draw.rectangle([x0 + 24, y1 - 12, x1 - 24, y1 - 4], fill=(139, 69, 19))
        draw.ellipse([cx - 26, y0 + 26, cx + 26, y0 + 44], outline=RED, width=3)
        draw.text((cx - 12, y0 + 27), "9–6", font=pick_font("sans_b", 13),
                  fill=RED)
    elif kind == "cop":
        draw.rectangle(box, fill=(30, 90, 90))
        draw.ellipse([x0 + 18, y0 + 6, x0 + 78, y0 + 66], fill=(60, 140, 180))
        draw.ellipse([x0 + 34, y0 + 22, x0 + 56, y0 + 36], fill=(80, 180, 120))
        draw.ellipse([x0 + 48, y0 + 38, x0 + 66, y0 + 50], fill=(80, 180, 120))
        draw.ellipse([x1 - 52, y0 + 14, x1 - 30, y0 + 60], fill=(220, 60, 50))
        draw.ellipse([x1 - 47, y0 + 20, x1 - 35, y0 + 54], fill=(255, 255, 255))
        draw.text((x1 - 58, y0 + 26), "COP31", font=pick_font("sans_b", 11),
                  fill=(255, 255, 255))
        draw.text((x0 + 96, y1 - 20), "DRAFT DEAL",
                  font=pick_font("sans_b", 10), fill=(255, 220, 120))
    elif kind == "chart":
        draw.rectangle(box, fill=(16, 60, 48))
        scale = (h - 18) / 62.0
        bars = [int(v * scale) for v in (22, 34, 28, 44, 52, 62)]
        for i, bh in enumerate(bars):
            bx = x0 + 14 + i * 36
            col = (60, 180, 120) if i < 5 else (120, 220, 140)
            draw.rectangle([bx, y1 - 8 - bh, bx + 24, y1 - 8], fill=col)
        pts = [(x0 + 14 + i * 36 + 12, y1 - 14 - bh) for i, bh in enumerate(bars)]
        draw.line(pts, fill=(255, 220, 80), width=3)
        draw.text((x0 + 8, y0 + 4), "$83", font=pick_font("serif_b", 20),
                  fill=(255, 255, 255))
        draw.text((x1 - 34, y0 + 6), "IPO", font=pick_font("sans_b", 11),
                  fill=(255, 220, 80))
    elif kind == "riyadh":
        draw.rectangle(box, fill=(20, 30, 60))
        draw.polygon([(cx - 16, y1), (cx - 10, y0 + 12), (cx + 10, y0 + 12),
                      (cx + 16, y1)], fill=(150, 170, 200))
        for j in range(5):
            yy = y0 + 16 + j * 9
            draw.line([cx - 11, yy, cx + 11, yy], fill=(220, 220, 220), width=1)
        draw.line([x1 - 70, y0 + 8, cx + 4, y0 + 26], fill=(255, 180, 60),
                  width=2)
        draw.polygon([(x1 - 78, y0 + 4), (x1 - 62, y0 + 8),
                      (x1 - 78, y0 + 12)], fill=(255, 120, 40))
        draw.text((x0 + 6, y0 + 4), "RIYADH", font=pick_font("sans_b", 9),
                  fill=(255, 255, 255))
    elif kind == "cyclone":
        draw.rectangle(box, fill=(180, 210, 225))
        rmax = min(26, min(w, h) // 2 - 2)
        for r in range(rmax, 4, -6):
            draw.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300,
                     fill=(255, 255, 255), width=4)
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
        draw.text((x0 + 6, y0 + 4), "AKVAN", font=pick_font("sans_b", 10),
                  fill=(20, 60, 90))
    elif kind == "gta":
        draw.rectangle(box, fill=(40, 20, 70))
        r = min(22, h // 2 - 6)
        draw.ellipse([cx - r, y0 + 6, cx + r, y0 + 6 + 2 * r],
                     fill=(255, 120, 90))
        draw.rectangle([x0, y1 - 22, x1, y1], fill=(20, 20, 40))
        vfont = pick_font("serif_b", max(12, 2 * r - 6))
        vtxt = "VI"
        vw = draw.textlength(vtxt, font=vfont)
        draw.text((cx - vw / 2, y0 + 6 + r - vfont.size // 2), vtxt,
                  font=vfont, fill=(255, 255, 255))
        for px in (x0 + 22, x1 - 22):
            draw.line([px, y1 - 22, px, y1 - 44], fill=(60, 40, 20), width=3)
            draw.arc([px - 12, y1 - 56, px + 12, y1 - 32], 180, 360,
                     fill=(40, 160, 80), width=3)
    elif kind == "gavel":
        draw.rectangle(box, fill=(230, 220, 200))
        draw.line([x0 + 30, y0 + 40, x1 - 40, y0 + 14], fill=(120, 80, 40),
                  width=6)
        draw.rectangle([x1 - 62, y0 + 2, x1 - 18, y0 + 22], fill=(90, 55, 20))
        draw.rectangle([x0 + 18, y1 - 14, x0 + 74, y1 - 6], fill=(90, 55, 20))
        draw.text((x0 + 80, y1 - 15), "OVERTURNED",
                  font=pick_font("sans_b", 9), fill=RED)
    elif kind == "greenland":
        draw.rectangle(box, fill=(190, 220, 235))
        draw.polygon([(x0, y1), (x0 + 60, y0 + 20), (x0 + 120, y1)],
                     fill=(255, 255, 255))
        draw.polygon([(x0 + 90, y1), (x0 + 150, y0 + 8), (x1, y1)],
                     fill=(230, 240, 245))
        draw.rectangle([x1 - 58, y0 + 8, x1 - 10, y0 + 30], fill=(255, 255, 255))
        draw.ellipse([x1 - 50, y0 + 12, x1 - 18, y0 + 26], fill=RED)
        draw.text((x0 + 8, y0 + 6), "109–0", font=pick_font("sans_b", 13),
                  fill=(20, 60, 90))
    elif kind == "bridge":
        draw.rectangle(box, fill=(170, 200, 225))
        draw.rectangle([x0, y1 - 26, x1, y1 - 18], fill=(90, 90, 90))
        draw.arc([x0 + 30, y0 + 8, x1 - 30, y1 + 6], 180, 360,
                 fill=(60, 60, 60), width=5)
        for sx, sy in ((cx - 8, y0 + 14), (cx + 14, y0 + 22), (cx - 22, y0 + 26)):
            draw.line([sx - 6, sy, sx + 6, sy], fill=(255, 160, 0), width=3)
            draw.line([sx, sy - 6, sx, sy + 6], fill=(255, 160, 0), width=3)
        draw.text((x0 + 6, y0 + 4), "KERCH", font=pick_font("sans_b", 9),
                  fill=(20, 40, 60))
    elif kind == "fire":
        draw.rectangle(box, fill=(60, 30, 20))
        draw.polygon([(x0 + 30, y1 - 18), (x0 + 90, y1 - 18),
                      (x0 + 60, y0 + 22)], fill=(160, 90, 40))
        draw.polygon([(cx - 16, y1 - 8), (cx - 4, y0 + 18), (cx + 8, y1 - 8)],
                     fill=(255, 140, 0))
        draw.polygon([(cx - 8, y1 - 8), (cx, y0 + 30), (cx + 8, y1 - 8)],
                     fill=(255, 220, 0))
        draw.text((x0 + 6, y0 + 4), "DHAKA", font=pick_font("sans_b", 9),
                  fill=(255, 255, 255))
    elif kind == "jobs":
        draw.rectangle(box, fill=(240, 235, 220))
        scale = (h - 20) / 44.0
        bars = [int(v * scale) for v in (18, 26, 34, 30, 44)]
        for i, bh in enumerate(bars):
            bx = x0 + 16 + i * 38
            draw.rectangle([bx, y1 - 10 - bh, bx + 22, y1 - 10],
                           fill=(178, 52, 40) if i == 4 else (90, 110, 140))
        draw.line([x0 + 12, y1 - 8 - bars[-1] - 4, x1 - 16, y1 - 16],
                  fill=RED, width=3)
        draw.polygon([(x1 - 16, y1 - 16), (x1 - 30, y1 - 18),
                      (x1 - 22, y1 - 6)], fill=RED)
        tag = "4.9%"
        tfont = pick_font("serif_b", 15)
        draw.text((x1 - 8 - draw.textlength(tag, font=tfont), y0 + 3), tag,
                  font=tfont, fill=RED)
    elif kind == "march":
        draw.rectangle(box, fill=(220, 215, 200))
        for i, suit in enumerate([(40, 80, 140), (160, 40, 40), (40, 120, 60)]):
            person(x0 + 45 + i * 70, y1 - 22, suit)
            draw.rectangle([x0 + 28 + i * 70, y0 + 8, x0 + 62 + i * 70, y0 + 22],
                           fill=(255, 255, 255), outline=INK)
        draw.text((x0 + 34, y0 + 10), "STRIKE", font=pick_font("sans_b", 8),
                  fill=INK)
    elif kind == "runner":
        draw.rectangle(box, fill=(200, 120, 60))
        draw.rectangle([x0, y1 - 20, x1, y1 - 12], fill=(178, 52, 40))
        for i in range(5):
            draw.line([x0 + 20 + i * 40, y1 - 20, x0 + 20 + i * 40, y1 - 12],
                      fill=(255, 255, 255), width=2)
        draw.ellipse([cx - 6, y0 + 16, cx + 6, y0 + 28], fill=(90, 50, 30))
        draw.line([cx, y0 + 28, cx + 10, y1 - 12], fill=(20, 20, 20), width=4)
        draw.line([cx, y0 + 44, cx - 12, y1 - 22], fill=(20, 20, 20), width=4)
        draw.line([cx, y0 + 44, cx + 14, y1 - 24], fill=(20, 20, 20), width=4)
        draw.text((x1 - 62, y0 + 6), "3 YEARS", font=pick_font("sans_b", 10),
                  fill=(255, 255, 255))
        draw.text((x1 - 62, y0 + 20), "BANNED", font=pick_font("sans_b", 10),
                  fill=(255, 255, 255))
    elif kind == "painting":
        draw.rectangle(box, fill=(120, 90, 50))
        draw.rectangle([x0 + 14, y0 + 8, x1 - 14, y1 - 8], fill=(250, 240, 210),
                       outline=(220, 180, 60), width=4)
        for i in range(3):
            px = x0 + 44 + i * 60
            draw.line([px, y1 - 16, px, y0 + 30], fill=(40, 120, 40), width=3)
            draw.ellipse([px - 12, y0 + 14, px + 12, y0 + 38], fill=(255, 200, 0))
            draw.ellipse([px - 4, y0 + 22, px + 4, y0 + 30], fill=(120, 60, 0))
        draw.text((x0 + 8, y1 - 18), "$190.4m", font=pick_font("sans_b", 11),
                  fill=(255, 255, 255))
    elif kind == "senate":
        draw.rectangle(box, fill=(30, 40, 80))
        draw.rectangle([x0 + 40, y1 - 12, x1 - 40, y1 - 4],
                       fill=(230, 225, 210))
        draw.arc([cx - 24, y0 + 2, cx + 24, y0 + 22], 180, 360,
                 fill=(230, 225, 210), width=8)
        for i in range(4):
            px = x0 + 52 + i * 36
            draw.rectangle([px, y0 + 14, px + 8, y1 - 12],
                           fill=(200, 195, 180))
        draw.text((x0 + 8, y0 + 4), "51–48", font=pick_font("sans_b", 13),
                  fill=(255, 255, 255))
    else:
        draw.rectangle(box, fill=SKY)
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=RED)


def paint_card(draw, fonts, card, x, y, w, h, size):
    """One story card: flat illustration on top, text below.

    Text is budgeted against the card's real height: the headline is
    trimmed first, then the deck, so nothing ever draws past the
    bottom edge or over the source line.
    """
    draw.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=CARD_EDGE)
    region = card["region"]
    paint = REGION_PAINT.get(region, (100, 100, 100))
    if size == "large":
        ill_h, hf, df, max_head, max_deck = 48, fonts.head_l, fonts.deck_m, 3, 3
    elif size == "medium":
        ill_h, hf, df, max_head, max_deck = 40, fonts.head_m, fonts.deck_s, 2, 2
    else:
        ill_h, hf, df, max_head, max_deck = 34, fonts.head_s, fonts.deck_s, 2, 2
    paint_motif(draw, (x + 1, y + 1, x + w - 1, y + ill_h), card["ill"])
    draw.rectangle([x, y + ill_h, x + w, y + ill_h + 2], fill=paint)
    ty = y + ill_h + 6
    tag = "%d · %s · %s" % (card["n"], region, card["field"])
    draw.text((x + 6, ty), tag, font=fonts.tag, fill=paint)
    ty += 12
    src = card["src"].strip()
    bottom = y + h - 14 if src else y + h - 4
    head_lines = fit_lines(draw, card["head"], hf, w - 12, max_head)
    # Reserve at least one deck line; trim the headline if it must give way.
    while (len(head_lines) > 1 and
           ty + len(head_lines) * (hf.size + 1) + (df.size + 1) > bottom):
        head_lines = head_lines[:-1]
        head_lines[-1] = head_lines[-1].rstrip() + "…"
    for line in head_lines:
        draw.text((x + 6, ty), line, font=hf, fill=INK)
        ty += hf.size + 1
    ty += 1
    deck_room = max(0, (bottom - ty) // (df.size + 1))
    deck_lines = fit_lines(draw, card["deck"], df, w - 12,
                           min(max_deck, deck_room))
    for line in deck_lines:
        draw.text((x + 6, ty), line, font=df, fill=SOFT_INK)
        ty += df.size + 1
    if src:
        draw.text((x + 6, y + h - 13), src, font=fonts.src, fill=(130, 120, 105))


def paint_masthead(draw, fonts, data):
    draw.text((MARGIN, 6), "THE WORLD IN ONE DAY", font=fonts.kicker, fill=RED)
    right = "52 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY"
    draw.text((CANVAS_W - MARGIN - draw.textlength(right, font=fonts.kicker),
               6), right, font=fonts.kicker, fill=SOFT_INK)
    title = "Thursday 19 November 2026"
    tw = draw.textlength(title, font=fonts.masthead)
    draw.text(((CANVAS_W - tw) / 2, 22), title, font=fonts.masthead, fill=INK)
    strap = ("Trump, Xi and Putin share one table · The World Court finds "
             "genocide in Myanmar · COP31's draft drops fossil fuels")
    sw = draw.textlength(strap, font=fonts.strap)
    draw.text(((CANVAS_W - sw) / 2, 84), strap, font=fonts.strap, fill=RED)
    draw.line([MARGIN, 104, CANVAS_W - MARGIN, 104], fill=INK, width=2)


def paint_stats(draw, fonts, data):
    y0, y1 = 108, 146
    cell = INNER / 6.0
    for i, (num, lab) in enumerate(data["STATS"]):
        x = MARGIN + i * cell
        if i:
            draw.line([x, y0 + 4, x, y1 - 4], fill=RULE, width=1)
        nw = draw.textlength(num, font=fonts.big_num)
        draw.text((x + (cell - nw) / 2, y0 + 2), num, font=fonts.big_num,
                  fill=INK)
        for j, line in enumerate(wrap(draw, lab, fonts.stat_lab, cell - 10)):
            lw = draw.textlength(line, font=fonts.stat_lab)
            draw.text((x + (cell - lw) / 2, y0 + 26 + j * 11), line,
                      font=fonts.stat_lab, fill=SOFT_INK)
    draw.line([MARGIN, y1, CANVAS_W - MARGIN, y1], fill=RULE, width=1)


def paint_strips(draw, fonts, data):
    # Region strip: colour-coded, counts in white.
    y0, h = 150, 18
    total = sum(c for _, c in data["REGIONS"])
    x = MARGIN
    for name, count in data["REGIONS"]:
        w = INNER * count / total
        draw.rectangle([x, y0, x + w, y0 + h],
                       fill=REGION_PAINT[name])
        label = "%s %d" % (name, count)
        lw = draw.textlength(label, font=fonts.strip_sm)
        draw.text((x + (w - lw) / 2, y0 + 3), label, font=fonts.strip_sm,
                  fill=(255, 255, 255))
        x += w
    # Field strip: dark slate, name + count.
    y0 = 170
    cell = INNER / len(data["FIELDS"])
    draw.rectangle([MARGIN, y0, CANVAS_W - MARGIN, y0 + h], fill=(48, 48, 56))
    for i, (name, _label, count) in enumerate(data["FIELDS"]):
        x = MARGIN + i * cell
        label = "%s %d" % (name, count)
        lw = draw.textlength(label, font=fonts.strip_sm)
        draw.text((x + (cell - lw) / 2, y0 + 3), label, font=fonts.strip_sm,
                  fill=(235, 230, 220))
        if i:
            draw.line([x, y0 + 3, x, y0 + h - 3], fill=(120, 120, 130), width=1)


def paint_timeline(draw, fonts, data):
    y0, y1 = 194, 232
    draw.text((MARGIN, y0 + 2), "THE DAY\nIN UTC", font=fonts.strip_sm, fill=RED)
    x = MARGIN + 62
    cell = (CANVAS_W - MARGIN - x) / len(data["TIMELINE"])
    for i, (when, what) in enumerate(data["TIMELINE"]):
        cx = x + i * cell
        if i % 2 == 0:
            draw.rectangle([cx, y0, cx + cell, y1], fill=(242, 236, 222))
        draw.text((cx + 4, y0 + 3), when, font=fonts.time, fill=RED)
        yy = y0 + 15
        for line in fit_lines(draw, what, fonts.time_txt, cell - 8, 3):
            draw.text((cx + 4, yy), line, font=fonts.time_txt, fill=INK)
            yy += 11
        if i:
            draw.line([cx, y0 + 3, cx, y1 - 3], fill=RULE, width=1)
    draw.line([MARGIN, y1, CANVAS_W - MARGIN, y1], fill=INK, width=1)


def paint_cards(draw, fonts, data):
    cards = data["CARDS"]
    gap = 6
    # 4 large
    lw = (INNER - 3 * gap) // 4
    for i, card in enumerate(cards[0:4]):
        paint_card(draw, fonts, card, MARGIN + i * (lw + gap), 238, lw, 148,
                   "large")
    # 6 medium
    mw = (INNER - 5 * gap) // 6
    for i, card in enumerate(cards[4:10]):
        paint_card(draw, fonts, card, MARGIN + i * (mw + gap), 392, mw, 118,
                   "medium")
    # 6 small
    for i, card in enumerate(cards[10:16]):
        paint_card(draw, fonts, card, MARGIN + i * (mw + gap), 516, mw, 108,
                   "small")


def paint_world_map(draw, fonts, data):
    x0, y0, x1, y1 = MARGIN, 652, MARGIN + 308, 796
    draw.rectangle([x0, y0, x1, y1], fill=(232, 238, 242),
                   outline=CARD_EDGE)
    # Stylised continents as flat grey-blue blobs (no real coastline data).
    blobs = [
        [(x0 + 18, y0 + 42), (x0 + 52, y0 + 26), (x0 + 96, y0 + 34),
         (x0 + 104, y0 + 58), (x0 + 70, y0 + 78), (x0 + 30, y0 + 66)],
        [(x0 + 118, y0 + 30), (x0 + 150, y0 + 22), (x0 + 178, y0 + 34),
         (x0 + 168, y0 + 62), (x0 + 132, y0 + 58)],
        [(x0 + 186, y0 + 40), (x0 + 224, y0 + 30), (x0 + 268, y0 + 44),
         (x0 + 258, y0 + 76), (x0 + 214, y0 + 84), (x0 + 192, y0 + 62)],
        [(x0 + 128, y0 + 84), (x0 + 160, y0 + 78), (x0 + 176, y0 + 100),
         (x0 + 158, y0 + 122), (x0 + 134, y0 + 104)],
        [(x0 + 238, y0 + 108), (x0 + 272, y0 + 104), (x0 + 282, y0 + 124),
         (x0 + 256, y0 + 132)],
    ]
    for blob in blobs:
        draw.polygon(blob, fill=(150, 168, 182))
    draw.text((x0 + 6, y0 + 4), "WORLD MAP — PINS 1–16",
              font=fonts.tag, fill=SOFT_INK)
    mw, mh = x1 - x0, y1 - y0
    for card in data["CARDS"]:
        lon, lat = PIN_LONLAT[card["n"]]
        px = x0 + (lon + 180) / 360.0 * mw
        py = y0 + (90 - lat) / 180.0 * mh
        paint = REGION_PAINT.get(card["region"], (100, 100, 100))
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=paint,
                     outline=(255, 255, 255), width=2)
        num = str(card["n"])
        nw = draw.textlength(num, font=fonts.tag)
        draw.text((px - nw / 2, py - 5), num, font=fonts.tag,
                  fill=(255, 255, 255))


def paint_also(draw, fonts, data):
    x0 = MARGIN + 322
    col_w = (CANVAS_W - MARGIN - x0 - 12) // 2
    items = data["ALSO"]
    half = (len(items) + 1) // 2
    small = pick_font("sans", 9)
    small_n = pick_font("sans_b", 9)
    for col in range(2):
        cx = x0 + col * (col_w + 12)
        for row, item in enumerate(items[col * half:(col + 1) * half]):
            n, _region, _field, text = item
            y = 652 + row * 10
            draw.text((cx, y), "%d" % n, font=small_n, fill=RED)
            font = small
            draw.text((cx + 20, y), text, font=font, fill=INK)


def paint_how_sure(draw, fonts):
    x0, y0, x1, y1 = MARGIN, 802, MARGIN + 308, 856
    draw.rectangle([x0, y0, x1, y1], fill=PANEL, outline=CARD_EDGE)
    draw.text((x0 + 8, y0 + 5), "HOW SURE", font=fonts.legend_b, fill=INK)
    rows = [
        ("● CONFIRMED", "— on the record: officials, filings, results."),
        ("● CLAIM", "— one side's account, not independently verified."),
        ("● SOURCES", "— monitors or unnamed sources, via a news agency."),
    ]
    yy = y0 + 20
    for head, tail in rows:
        draw.text((x0 + 8, yy), head, font=fonts.legend_b, fill=INK)
        draw.text((x0 + 96, yy), tail, font=fonts.legend, fill=SOFT_INK)
        yy += 11


def paint_numbers(draw, fonts, data):
    y0 = 858
    draw.text((MARGIN, y0), "THE DAY IN NUMBERS", font=fonts.sec, fill=INK)
    draw.line([MARGIN + 168, y0 + 8, CANVAS_W - MARGIN, y0 + 8], fill=RED,
              width=1)
    y0 = 876
    cell = INNER / 6.0
    draw.rectangle([MARGIN, y0, CANVAS_W - MARGIN, y0 + 40], fill=PANEL)
    for i, (num, lab) in enumerate(data["NUMBERS"]):
        x = MARGIN + i * cell
        if i:
            draw.line([x, y0 + 5, x, y0 + 35], fill=RULE, width=1)
        nw = draw.textlength(num, font=fonts.num_big)
        draw.text((x + (cell - nw) / 2, y0 + 3), num, font=fonts.num_big,
                  fill=DARK_RED)
        for j, line in enumerate(wrap(draw, lab, fonts.num_lab, cell - 10)):
            lw = draw.textlength(line, font=fonts.num_lab)
            draw.text((x + (cell - lw) / 2, y0 + 23 + j * 10), line,
                      font=fonts.num_lab, fill=SOFT_INK)


def paint_date_check(draw, fonts):
    x0, y0, x1, y1 = MARGIN, 924, CANVAS_W - MARGIN, 986
    draw.rectangle([x0, y0, x1, y1], outline=RED, width=2)
    draw.rectangle([x0, y0, x0 + 108, y1], fill=RED)
    draw.text((x0 + 10, y0 + 20), "DATE\nCHECK", font=fonts.date_t,
              fill=(255, 255, 255))
    tx = x0 + 120
    lines = [
        "Every story on this page happened, or was first reported, on "
        "Thursday, 19 November 2026.",
        "Left out as other days' news: 18 Nov — Xi's $5.8bn clean-energy "
        "loan plan; riots, airstrikes and a volcano warning from earlier in "
        "the week; 20 Nov — COP31's draft due, Kerch bridge attack latest, "
        "Colombia Q3 GDP.",
        "Checked against the day's wires before printing. No story here is "
        "from 18 or 20 November.",
    ]
    yy = y0 + 6
    for line in lines:
        yy = draw_wrapped(draw, line, fonts.date_b, tx, yy, x1 - tx - 10, INK)
        yy += 2


def paint_footer(draw, fonts):
    draw.text((MARGIN, 994),
              "Claims are attributed, not stated as fact · Pictures are "
              "original, drawn in code · Sources: Reuters, AP, AFP, BBC, "
              "Al Jazeera, UN News, Euronews, ABC, RNZ, Xinhua, Nature",
              font=fonts.foot, fill=(130, 120, 105))
    note = "2026-11-19"
    draw.text((CANVAS_W - MARGIN - draw.textlength(note, font=fonts.foot),
               994), note, font=fonts.foot, fill=(130, 120, 105))


def build_page():
    data = load_stories()
    fonts = TypeCase()
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    draw = ImageDraw.Draw(canvas)
    paint_masthead(draw, fonts, data)
    paint_stats(draw, fonts, data)
    paint_strips(draw, fonts, data)
    paint_timeline(draw, fonts, data)
    paint_cards(draw, fonts, data)
    draw.text((MARGIN, 630), "WHERE IT HAPPENED",
              font=fonts.sec, fill=INK)
    draw.text((MARGIN + 322, 630), "ALSO ON THURSDAY 19 NOVEMBER — "
              "36 MORE STORIES", font=fonts.sec, fill=INK)
    draw.line([MARGIN, 646, CANVAS_W - MARGIN, 646], fill=RED, width=1)
    paint_world_map(draw, fonts, data)
    paint_also(draw, fonts, data)
    paint_how_sure(draw, fonts)
    paint_numbers(draw, fonts, data)
    paint_date_check(draw, fonts)
    paint_footer(draw, fonts)
    return canvas


def main():
    page = build_page()
    page.save(TARGET, format="PNG")
    size = os.path.getsize(TARGET)
    print("wrote %s (%d bytes, %dx%d)" % (TARGET, size, CANVAS_W, CANVAS_H))


if __name__ == "__main__":
    main()
