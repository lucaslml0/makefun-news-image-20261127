#!/usr/bin/env python3
"""Draw the 27 November 2026 world-news front page (1024x1024 PNG).

Everything is drawn with PIL primitives — no fetched images, no photos.
Stories verified via web search on 27 Nov 2026 (Reuters / AP / BBC /
Euronews round-ups). Deterministic: fixed palette, fixed layout, no
timestamps or randomness in the output.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (27, 42, 74)
NAVY_LT = (43, 63, 105)
GOLD = (212, 175, 55)
RED = (178, 34, 34)
BLUE = (30, 80, 160)
TEAL = (0, 110, 110)
GREY = (90, 90, 90)
RULE = (120, 110, 95)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, fill, max_w, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.25)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_eu_stars(draw, x, y, s):
    """EU circle of 12 gold stars on blue, split by a jagged crack."""
    cx, cy = x + s // 2, y + s // 2
    draw.ellipse([x, y, x + s, y + s], fill=(18, 48, 120))
    for k in range(12):
        ang = -math.pi / 2 + k * math.pi / 6
        sx = cx + int(0.36 * s * math.cos(ang))
        sy = cy + int(0.36 * s * math.sin(ang))
        star(draw, sx, sy, int(s * 0.055), GOLD)
    # jagged crack
    crack = [(x + 8, y + s * 0.18), (x + s * 0.35, y + s * 0.42),
             (x + s * 0.28, y + s * 0.55), (x + s * 0.62, y + s * 0.68),
             (x + s * 0.55, y + s * 0.82), (x + s * 0.95, y + s * 0.95)]
    draw.line(crack, fill=(255, 255, 255), width=7, joint="curve")
    draw.line(crack, fill=RED, width=3, joint="curve")


def draw_kyiv(draw, x, y, s):
    """Night skyline, missile arcs, explosion burst."""
    draw.rectangle([x, y, x + s, y + s], fill=(16, 22, 44))
    # skyline
    heights = [0.45, 0.65, 0.38, 0.72, 0.55, 0.62, 0.42]
    bw = s // 7
    for i, hf in enumerate(heights):
        bx = x + i * bw
        bh = int(s * hf)
        draw.rectangle([bx + 2, y + s - bh, bx + bw - 2, y + s], fill=(52, 66, 96))
        for wy in range(y + s - bh + 8, y + s - 4, 16):
            draw.rectangle([bx + 6, wy, bx + 10, wy + 6], fill=GOLD)
    # missile arcs
    draw.arc([x + 8, y + 6, x + s - 8, y + s * 0.75], 200, 330,
             fill=(255, 120, 40), width=5)
    draw.arc([x + s * 0.3, y - 6, x + s + 6, y + s * 0.6], 190, 320,
             fill=(255, 200, 60), width=4)
    # explosion burst
    ex, ey = x + int(s * 0.72), y + int(s * 0.30)
    star(draw, ex, ey, 26, (255, 210, 60))
    star(draw, ex, ey, 15, (255, 90, 30))


def draw_tanker(draw, x, y, s):
    """Tanker on waves with a spiked mine and flame."""
    draw.rectangle([x, y, x + s, y + s], fill=(200, 228, 240))
    # sea
    for i, yy in enumerate(range(y + int(s * 0.62), y + s, 14)):
        col = (20, 90, 140) if i % 2 == 0 else (30, 110, 165)
        draw.line([(x, yy), (x + s, yy)], fill=col, width=7)
    # hull
    draw.polygon([(x + 12, y + int(s * 0.55)), (x + s - 12, y + int(s * 0.55)),
                  (x + s - 26, y + int(s * 0.72)), (x + 26, y + int(s * 0.72))],
                 fill=(140, 30, 30))
    draw.rectangle([x + 28, y + int(s * 0.38), x + s - 28, y + int(s * 0.55)],
                   fill=(190, 60, 50))
    for i in range(4):
        cx0 = x + 34 + i * 30
        draw.rectangle([cx0, y + int(s * 0.30), cx0 + 24, y + int(s * 0.38)],
                       fill=(230, 200, 90))
    # bridge
    draw.rectangle([x + s - 52, y + int(s * 0.22), x + s - 30, y + int(s * 0.38)],
                   fill=(250, 250, 250))
    # spiked mine
    mx, my = x + int(s * 0.22), y + int(s * 0.22)
    for k in range(8):
        ang = k * math.pi / 4
        draw.line([(mx + 10 * math.cos(ang), my + 10 * math.sin(ang)),
                   (mx + 20 * math.cos(ang), my + 20 * math.sin(ang))],
                  fill=INK, width=3)
    draw.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=INK)
    # flame
    fx, fy = x + int(s * 0.80), y + int(s * 0.18)
    star(draw, fx, fy, 18, (255, 140, 0))
    star(draw, fx, fy, 10, (255, 220, 60))


def draw_scales(draw, x, y, s):
    """Scales of justice (ICC)."""
    draw.rectangle([x, y, x + s, y + s], fill=(232, 226, 208))
    cx = x + s // 2
    # post + base
    draw.rectangle([cx - 5, y + 22, cx + 5, y + s - 26], fill=INK)
    draw.rectangle([cx - 34, y + s - 26, cx + 34, y + s - 16], fill=INK)
    draw.ellipse([cx - 10, y + 12, cx + 10, y + 30], fill=GOLD)
    # beam
    draw.line([(cx - 58, y + 34), (cx + 58, y + 34)], fill=INK, width=6)
    for sgn in (-1, 1):
        px = cx + sgn * 58
        draw.line([(px, y + 34), (px - 22, y + 66)], fill=INK, width=3)
        draw.line([(px, y + 34), (px + 22, y + 66)], fill=INK, width=3)
        draw.line([(px, y + 34), (px, y + 66)], fill=INK, width=3)
        draw.pieslice([px - 22, y + 62, px + 22, y + 92], 0, 180, fill=GOLD)
        draw.line([(px - 22, y + 77), (px + 22, y + 77)], fill=INK, width=3)


def draw_storm(draw, x, y, s):
    """Storm cloud, lightning, small plane."""
    draw.rectangle([x, y, x + s, y + s], fill=(214, 222, 230))
    # cloud
    cx, cy = x + s // 2, y + int(s * 0.38)
    for dx, dy, r in [(-38, 6, 26), (-8, -14, 34), (26, 2, 30), (46, 14, 20)]:
        draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                     fill=(96, 104, 116))
    draw.rectangle([cx - 62, cy - 4, cx + 66, cy + 30], fill=(96, 104, 116))
    # lightning
    bolt = [(cx - 6, cy + 28), (cx + 12, cy + 28), (cx - 2, cy + 52),
            (cx + 14, cy + 52), (cx - 14, cy + 92), (cx - 2, cy + 58),
            (cx - 16, cy + 58)]
    draw.polygon(bolt, fill=(255, 205, 0))
    # plane
    px, py = x + int(s * 0.68), y + int(s * 0.78)
    draw.polygon([(px, py - 6), (px + 34, py), (px, py + 6), (px - 8, py)],
                 fill=NAVY)
    draw.polygon([(px + 4, py - 4), (px + 12, py - 16), (px + 18, py - 4)],
                 fill=NAVY)


def draw_virus(draw, x, y, s):
    """Spiked virus disc (Ebola)."""
    cx, cy = x + s // 2, y + s // 2
    for k in range(12):
        ang = k * math.pi / 6
        draw.line([(cx + 20 * math.cos(ang), cy + 20 * math.sin(ang)),
                   (cx + 34 * math.cos(ang), cy + 34 * math.sin(ang))],
                  fill=RED, width=4)
        draw.ellipse([cx + 34 * math.cos(ang) - 4, cy + 34 * math.sin(ang) - 4,
                      cx + 34 * math.cos(ang) + 4, cy + 34 * math.sin(ang) + 4],
                     fill=RED)
    draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(200, 60, 60))
    draw.ellipse([cx - 12, cy - 14, cx - 2, cy - 4], fill=(255, 150, 150))
    draw.ellipse([cx + 4, cy + 6, cx + 14, cy + 16], fill=(255, 150, 150))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28  # margin

    # outer frame
    d.rectangle([M - 8, M - 8, W - M + 8, H - M + 8], outline=INK, width=4)
    d.rectangle([M - 2, M - 2, W - M + 2, H - M + 2], outline=INK, width=1)

    # ---- masthead ----
    d.rectangle([M, M, W - M, M + 96], fill=NAVY)
    d.text((W // 2, M + 48), "THE WORLD TODAY",
           font=font(SERIF_B, 62), fill=(255, 255, 255), anchor="mm")
    y = M + 106
    d.text((W // 2, y + 16), "FRIDAY  ·  27 NOVEMBER 2026",
           font=font(SANS_B, 30), fill=INK, anchor="mm")
    y += 44
    d.line([(M, y), (W - M, y)], fill=INK, width=3)
    d.line([(M, y + 6), (W - M, y + 6)], fill=INK, width=1)

    # ---- lead story: EU deadlock ----
    y += 18
    lead_y = y
    d.text((M + 8, lead_y), "EU SUMMIT DEADLOCKS",
           font=font(SERIF_B, 44), fill=INK)
    d.text((M + 8, lead_y + 62), "No deal on €1.6tn budget or $49bn Ukraine loan",
           font=font(SANS_B, 26), fill=RED)
    cap = ("Brussels — after 12+ hours of talks, EU leaders fail to agree the "
           "bloc's 2028–34 budget or a new loan for Kyiv. France sets a "
           "year-end deadline; leaders meet again on 17–18 December.")
    draw_text_block(d, M + 8, lead_y + 104, cap, font(SANS, 21), INK, 600, 27)
    draw_eu_stars(d, W - M - 250, lead_y + 4, 236)
    d.text((W - M - 250, lead_y + 244), "Brussels, 26–27 Nov",
           font=font(SANS, 17), fill=GREY)

    y = lead_y + 262
    d.line([(M, y), (W - M, y)], fill=RULE, width=2)

    # ---- 2x2 story grid ----
    stories = [
        ("KYIV UNDER FIRE", draw_kyiv,
         "Russian missiles hit a Kyiv mall, wounding 7; Ukraine says it "
         "struck a Russian air base, damaging MiG-31 jets."),
        ("GULF ON EDGE", draw_tanker,
         "Iran says tankers hit mines near Hormuz; two Italian technicians "
         "killed by a drone strike in Kuwait."),
        ("DUTERTE TO FACE ICC", draw_scales,
         "Ex-president goes on trial on Monday over drug-war killings; "
         "families of victims seek justice in The Hague."),
        ("THANKSGIVING STORM", draw_storm,
         "Storm snarls US holiday travel and cuts power to 800,000+ as "
         "Black Friday shoppers head out."),
    ]
    grid_y = y + 14
    cell_w, cell_h = (W - 2 * M) // 2, 178
    for i, (head, art, body) in enumerate(stories):
        cx = M + (i % 2) * cell_w
        cy = grid_y + (i // 2) * cell_h
        art(d, cx + 6, cy + 6, 150)
        tx = cx + 168
        d.text((tx, cy + 8), head, font=font(SANS_B, 23), fill=INK)
        d.line([(tx, cy + 40), (cx + cell_w - 12, cy + 40)], fill=RULE, width=1)
        draw_text_block(d, tx, cy + 50, body, font(SANS, 18), (40, 40, 40),
                        cell_w - 182, 23)
        if i % 2 == 0:
            d.line([(cx + cell_w, cy + 4), (cx + cell_w, cy + cell_h - 8)],
                   fill=RULE, width=1)
    y = grid_y + 2 * cell_h + 6
    d.line([(M, y), (W - M, y)], fill=RULE, width=2)

    # ---- bottom strip: Ebola ----
    y += 12
    draw_virus(d, M + 8, y + 4, 84)
    d.text((M + 108, y + 4), "EBOLA IN CONGO: CASES PASS 12,000",
           font=font(SANS_B, 24), fill=INK)
    draw_text_block(d, M + 108, y + 38,
                    "Deaths near 6,000 as fighting in Ituri forces aid workers out.",
                    font(SANS, 19), (40, 40, 40), W - M - 108 - 8, 24)
    y += 100
    d.line([(M, y), (W - M, y)], fill=INK, width=3)

    # ---- footer ----
    y += 10
    d.text((W // 2, y + 12),
           "Sources: Reuters · AP · BBC · Euronews — reports of 27 November 2026",
           font=font(SANS, 16), fill=GREY, anchor="mm")
    d.text((W // 2, y + 34), "All stories verified from reports published 27 November 2026.",
           font=font(SANS, 15), fill=GREY, anchor="mm")

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
