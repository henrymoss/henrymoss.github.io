#!/usr/bin/env python3
"""MAADLAB logo.

The mark is the group's subject in one glyph: a belief about an unknown
function (the lime curve with its uncertainty band) and the single point we
choose to measure next (the violet dot). Geometry and palette follow the MARS
identity — lime #d1f43d, violet #6472e2, navy #1a1a34, steel #8ab0c9.

Writes:
  images/logo.svg        horizontal lockup, light text — for the navy header
  images/logo-dark.svg   horizontal lockup, dark text — for white backgrounds
  images/logo-mark.svg   square mark only
  images/favicon.svg     square mark, favicon-sized
"""

import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIME = "#d1f43d"
VIOLET = "#6472e2"
NAVY = "#1a1a34"
STEEL = "#8ab0c9"


def curve_points(x0, x1, cy, amp, n=90):
    """A two-humped posterior mean; the higher hump is where we sample."""
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + t * (x1 - x0)
        y = cy - amp * (0.42 * math.sin(t * 2.6 * math.pi - 0.7)
                        + 0.72 * math.exp(-((t - 0.70) / 0.17) ** 2))
        pts.append((x, y))
    return pts


def path(pts):
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def band(pts, fn):
    up = [(x, y - fn(i / (len(pts) - 1))) for i, (x, y) in enumerate(pts)]
    lo = [(x, y + fn(i / (len(pts) - 1))) for i, (x, y) in enumerate(reversed(pts))]
    return path(up) + " L " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in lo) + " Z"


def mark(size=64, bg=NAVY, rounded=True):
    """The square mark."""
    s = size / 64.0
    pad = 11 * s
    pts = curve_points(pad, size - pad, size * 0.54, 16 * s)
    width = lambda t: (3.0 + 5.0 * abs(math.sin(t * 3.0))) * s
    peak = pts[int(0.70 * (len(pts) - 1))]
    r = (12 * s) if rounded else 0
    out = [f'<rect width="{size}" height="{size}" rx="{r:.1f}" fill="{bg}"/>',
           f'<path d="{band(pts, width)}" fill="{STEEL}" opacity="0.40"/>',
           f'<path d="{path(pts)}" fill="none" stroke="{LIME}" '
           f'stroke-width="{4.4 * s:.2f}" stroke-linecap="round" stroke-linejoin="round"/>',
           # the point we choose to measure next
           f'<circle cx="{peak[0]:.2f}" cy="{peak[1]:.2f}" r="{7.6 * s:.2f}" fill="{bg}"/>',
           f'<circle cx="{peak[0]:.2f}" cy="{peak[1]:.2f}" r="{6.0 * s:.2f}" fill="{VIOLET}"/>']
    return "\n".join(out)


def write(name, body, w, h):
    p = os.path.join(ROOT, "images", name)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'width="{w}" height="{h}" role="img">\n{body}\n</svg>\n')
    open(p, "w").write(svg)
    print("wrote images/" + name)


def lockup(text_fill, sub_fill, bg=None, w=460, h=96):
    m = 64
    body = []
    if bg:
        body.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')
    body.append(f'<g transform="translate(6,{(h - m) / 2:.0f})">{mark(m)}</g>')
    body.append(
        f'<text x="{6 + m + 16}" y="{h / 2 + 2:.0f}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="34" font-weight="bold" letter-spacing="1.5" fill="{text_fill}">MAADLAB</text>')
    body.append(
        f'<text x="{6 + m + 18}" y="{h / 2 + 24:.0f}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11.5" font-weight="bold" letter-spacing="1.35" fill="{sub_fill}">'
        f'MATHEMATICAL AI FOR DECISION &amp; DISCOVERY</text>')
    return "\n".join(body)


if __name__ == "__main__":
    write("logo.svg", lockup("#ffffff", LIME), 460, 96)
    write("logo-dark.svg", lockup(NAVY, VIOLET), 460, 96)
    write("logo-mark.svg", mark(64), 64, 64)
    write("favicon.svg", mark(64, rounded=False), 64, 64)
