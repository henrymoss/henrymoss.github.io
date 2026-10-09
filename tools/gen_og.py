#!/usr/bin/env python3
"""Open Graph card — the picture Slack, LinkedIn, Bluesky and the rest show
when someone shares a link to the site.

It has to be a raster image: essentially no OG consumer renders SVG, so this
redraws the MADD lockup with Pillow rather than reusing images/logo-header.svg.

Everything is drawn at SUPERSAMPLE times final size and scaled down at the end,
because Pillow's ellipse and polygon are not antialiased and look ragged at 1:1.

    python3 tools/gen_og.py

Writes images/og-card.png (1200x630, the size every platform expects).
Safe to re-run; it overwrites in place.
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 1200, 630
SS = 3                       # supersample factor

NAVY = "#2d1e69"
LAVENDER = "#f1eefc"
HALO = "#d9d5ec"
PINK = "#de6fa1"
ORANGE = "#f97b3d"
YELLOW = "#ffd23f"
WHITE = "#ffffff"
GREY = "#6f6a93"

LATO = "/usr/share/fonts/truetype/lato/Lato-%s.ttf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"


def font(weight, size):
    """Lato where it is installed, DejaVu where it is not."""
    for path in (LATO % weight, FALLBACK % ("-Bold" if weight != "Regular" else "")):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ----------------------------------------------------------------- geometry ---

def qbezier(p0, p1, p2, n):
    """Points along a quadratic Bezier, used for the dotted hops."""
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def cbezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return out


def sparkle_points(cx, cy, r, pinch=0.22, rot=0.0):
    """The four-pointed star, as a polygon sampled off its curved sides."""
    import math
    a = r * pinch
    tips = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    ctrl = [(cx + a, cy - a), (cx + a, cy + a), (cx - a, cy + a), (cx - a, cy - a)]
    pts = []
    for i in range(4):
        c = ctrl[i]
        pts += cbezier(tips[i], c, c, tips[(i + 1) % 4], 14)[:-1]
    if rot:
        s, co = math.sin(rot), math.cos(rot)
        pts = [(cx + (x - cx) * co - (y - cy) * s,
                cy + (x - cx) * s + (y - cy) * co) for x, y in pts]
    return pts


def ring(d, cx, cy, r, colour, width):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=int(width))


def dot(d, x, y, r, colour):
    d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def spaced(d, xy, text, fnt, fill, tracking):
    """Draw text with extra space between characters."""
    x, y = xy
    bb = fnt.getbbox(text)
    y -= bb[1]
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking
    return x


def ink(fnt, text):
    """Width and height of the marks a string actually makes, ignoring the
    font's own padding — so blocks can be stacked by eye rather than by em."""
    x0, y0, x1, y1 = fnt.getbbox(text)
    return x1 - x0, y1 - y0


def fit(text, weight, target_w):
    """Largest size at which `text` still fits inside target_w."""
    lo, hi, best = 10, 900, 10
    while lo <= hi:
        mid = (lo + hi) // 2
        if ink(font(weight, mid), text)[0] <= target_w:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best


def text_at(d, x, top, text, fnt, fill):
    """Draw so the ink's left and top edges land exactly on (x, top)."""
    x0, y0, x1, y1 = fnt.getbbox(text)
    d.text((x - x0, top - y0), text, font=fnt, fill=fill)
    return x1 - x0


# -------------------------------------------------------------------- card ---

MARGIN = 96
TAGLINE = "Mathematical AI for Decision and Discovery"


def build():
    im = Image.new("RGB", (W * SS, H * SS), LAVENDER)
    d = ImageDraw.Draw(im)
    s = lambda v: v * SS      # noqa: E731 — scale a design-space value

    # The tagline sets the measure: the wordmark is sized to match its width,
    # so the two stack as one block instead of leaving the right side empty.
    tag_f = font("Bold", int(s(44)))
    block_w = ink(tag_f, TAGLINE)[0]
    madd_f = font("Black", fit("MADD", "Black", block_w))
    madd_w, madd_h = ink(madd_f, "MADD")

    madd_top = s(268)
    tag_top = madd_top + madd_h + s(46)
    lanc_top = tag_top + ink(tag_f, TAGLINE)[1] + s(30)

    # --- the search: four pegs, each landing higher, then onto the target ---
    # The target sits just past the end of the wordmark and keeps a right
    # margin a little wider than the left, as it does in the printed lockup.
    # The pegs then space themselves back from wherever it landed.
    target_r = s(80)
    tx = s(W - 137) - target_r
    ty = s(168)

    first, last = s(118), tx - target_r - s(12)
    step = (last - first) / 4.0
    pegs = [(first + step * i, s(250 - 14 * i)) for i in range(4)]
    points = pegs + [(last, s(198))]
    peg_r, lift = s(15), step * 0.46

    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        ctrl = ((x0 + x1) / 2, min(y0, y1) - lift)
        # walk the curve and lay a round dot down every few samples
        for j, (x, y) in enumerate(qbezier((x0, y0), ctrl, (x1, y1), 150)):
            if j % 8 == 0:
                dot(d, x, y, s(3.4), NAVY)

    for x, y in pegs:
        d.ellipse([x - peg_r, y - peg_r, x + peg_r, y + peg_r],
                  fill=WHITE, outline=NAVY, width=int(s(6)))

    k = target_r / 30.0
    ring(d, tx, ty, target_r, HALO, 3.0 * k)
    ring(d, tx, ty, 22 * k, PINK, 3.6 * k)
    ring(d, tx, ty, 14.5 * k, ORANGE, 3.6 * k)
    d.polygon(sparkle_points(tx, ty, 12.5 * k, rot=0.7853981634), fill=YELLOW)
    d.polygon(sparkle_points(tx, ty, 9.0 * k), fill=WHITE, outline=NAVY,
              width=int(1.6 * k))

    # --- wordmark, tagline, institution -------------------------------------
    text_at(d, s(MARGIN), madd_top, "MADD", madd_f, NAVY)
    text_at(d, s(MARGIN) + s(4), tag_top, TAGLINE, tag_f, NAVY)
    spaced(d, (s(MARGIN) + s(6), lanc_top), "LANCASTER UNIVERSITY",
           font("Medium", int(s(22))), GREY, s(4.4))

    im = im.resize((W, H), Image.LANCZOS)
    out = os.path.join(ROOT, "images", "og-card.png")
    im.save(out, optimize=True)
    print("wrote images/og-card.png  (%dx%d, %d KB)"
          % (W, H, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    build()
