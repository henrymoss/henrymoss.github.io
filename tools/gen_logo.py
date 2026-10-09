#!/usr/bin/env python3
"""MADD identity.

The mark is the group's subject in one picture: a search hopping across a
space — four evaluations, each landing a little higher than the last — and
converging on the optimum, drawn as a target with a sparkle at its centre.

Writes:
  images/logo-header.svg  the trajectory, drawn light for the navy header bar,
                          and self-animating: it plays the search out once on
                          page load, then holds still
  images/favicon.svg      the sparkle on navy, legible at 16px

The header file carries its own <style>, so it animates inside a plain <img>
with no page CSS and no JavaScript, and holds still for anyone who has asked
for reduced motion.

    python3 tools/gen_logo.py

Safe to re-run; it overwrites in place.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVY = "#2d1e69"      # header bar, and the ground the light mark sits on
HALO = "#6052ab"      # outermost ring, a lifted indigo that reads on navy
PINK = "#de6fa1"
ORANGE = "#f97b3d"
YELLOW = "#ffd23f"
WHITE = "#ffffff"


def write(name, body, w, h, style="", bg=None):
    ground = f'<rect width="{w}" height="{h}" fill="{bg}"/>\n' if bg else ""
    css = f"<style>\n{style}\n</style>\n" if style else ""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img">\n{css}{ground}{body}\n</svg>\n'
    )
    path = os.path.join(ROOT, "images", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(svg)
    print("wrote images/" + name)


def _n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def sparkle(cx, cy, r, pinch=0.22):
    """A four-pointed star whose sides pull in towards the centre."""
    a = r * pinch
    p = lambda x, y: f"{_n(x)},{_n(y)}"
    return (
        f"M {p(cx, cy - r)} "
        f"C {p(cx + a, cy - a)} {p(cx + a, cy - a)} {p(cx + r, cy)} "
        f"C {p(cx + a, cy + a)} {p(cx + a, cy + a)} {p(cx, cy + r)} "
        f"C {p(cx - a, cy + a)} {p(cx - a, cy + a)} {p(cx - r, cy)} "
        f"C {p(cx - a, cy - a)} {p(cx - a, cy - a)} {p(cx, cy - r)} Z"
    )


def target(cx, cy, r, halo=HALO):
    """Concentric rings plus a sparkle, as [ring, ring, ring, stars].

    `r` is the outer ring's radius; everything else is a fraction of it, so the
    mark scales as one piece. Returned in pieces so the caller can tag each
    ring for the ripple.

    The two stars are wrapped in a <g> because the yellow one carries a
    rotate() attribute: a CSS transform on that same element would replace the
    attribute outright and snap it upright mid-animation. Animating the group
    leaves the inner rotation alone.
    """
    k = r / 30.0
    return [
        f'<circle cx="{cx}" cy="{cy}" r="{_n(r)}" fill="none" '
        f'stroke="{halo}" stroke-width="{_n(3.0 * k)}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{_n(22 * k)}" fill="none" '
        f'stroke="{PINK}" stroke-width="{_n(3.6 * k)}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{_n(14.5 * k)}" fill="none" '
        f'stroke="{ORANGE}" stroke-width="{_n(3.6 * k)}"/>',
        # yellow star on the diagonals, white-and-navy star upright on top —
        # together they read as an eight-pointed sparkle
        f'<g class="star">'
        f'<path d="{sparkle(cx, cy, 11.5 * k)}" fill="{YELLOW}" '
        f'transform="rotate(45 {cx} {cy})"/>'
        f'<path d="{sparkle(cx, cy, 8.5 * k)}" fill="{WHITE}" '
        f'stroke="{NAVY}" stroke-width="{_n(1.5 * k)}" stroke-linejoin="round"/>'
        f'</g>',
    ]


# ------------------------------------------------------------- header mark ---

# Four pegs, each hop landing a little higher than the last, then a final leap
# onto the target. Coordinates are in the 196x52 viewBox, sized so the whole
# lockup drops into a 64px header bar at about 40px tall.
PEGS = [(11, 41), (45, 37), (79, 33), (113, 29)]
TARGET_C, TARGET_R = (166, 25), 19
PEG_R = 5.0
LIFT = 26        # how far the control point sits above the lower peg

HEADER_STYLE = """
  .hop, .peg, .ring, .star { transform-box: fill-box; transform-origin: center; }

  /* One shot: the search plays out as the page loads, then the mark sits
     still. A header is on screen the whole time, so nothing loops here. */
  .hop { animation: maddFade .4s ease both; }
  .h0 { animation-delay: .06s } .h1 { animation-delay: .20s }
  .h2 { animation-delay: .34s } .h3 { animation-delay: .48s }

  .peg { animation: maddPop .4s cubic-bezier(.34,1.56,.64,1) both; }
  .p0 { animation-delay: .13s } .p1 { animation-delay: .27s }
  .p2 { animation-delay: .41s } .p3 { animation-delay: .55s }

  .ring { animation: maddRipple .5s ease-out both; }
  .r0 { animation-delay: .68s } .r1 { animation-delay: .77s }
  .r2 { animation-delay: .86s }

  .star { animation: maddPop .45s cubic-bezier(.34,1.56,.64,1) .96s both; }

  @keyframes maddFade { from { opacity: 0 } to { opacity: 1 } }
  @keyframes maddPop {
     0%   { opacity: 0; transform: scale(.2) }
     100% { opacity: 1; transform: scale(1) }
  }
  @keyframes maddRipple {
     0%   { opacity: 0; transform: scale(.45) }
     60%  { opacity: 1 }
     100% { opacity: 1; transform: scale(1) }
  }

  /* hold everything still for anyone who has asked for less movement */
  @media (prefers-reduced-motion: reduce) {
     .hop, .peg, .ring, .star {
        animation: none !important;
        opacity: 1 !important;
        transform: none !important;
     }
  }
"""


def header_mark():
    hops, pegs = [], []
    points = PEGS + [(TARGET_C[0] - TARGET_R - 4, TARGET_C[1] + 2)]
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        cx, cy = (x0 + x1) / 2, min(y0, y1) - LIFT
        hops.append(
            f'<path class="hop h{i}" d="M {x0},{y0} Q {_n(cx)},{_n(cy)} {x1},{y1}" '
            f'fill="none" stroke="{WHITE}" stroke-width="2.2" '
            f'stroke-dasharray="0.1 5.5" stroke-linecap="round"/>'
        )
    for i, (x, y) in enumerate(PEGS):
        pegs.append(
            f'<circle class="peg p{i}" cx="{x}" cy="{y}" r="{_n(PEG_R)}" '
            f'fill="{NAVY}" stroke="{WHITE}" stroke-width="2.4"/>'
        )

    rings = target(*TARGET_C, TARGET_R)
    rings = [r.replace("<circle", f'<circle class="ring r{i}"', 1)
             for i, r in enumerate(rings[:3])] + rings[3:]

    write("logo-header.svg", "\n".join(hops + pegs + rings), 196, 52,
          style=HEADER_STYLE)


# ----------------------------------------------------------------- favicon ---

def favicon():
    """At 16px the rings collapse into mush, so the favicon is the sparkle
    alone on navy — the one part of the mark that still reads that small."""
    body = "\n".join([
        f'<path d="{sparkle(32, 32, 22)}" fill="{YELLOW}" '
        f'transform="rotate(45 32 32)"/>',
        f'<path d="{sparkle(32, 32, 16)}" fill="{WHITE}"/>',
    ])
    write("favicon.svg", body, 64, 64, bg=NAVY)


if __name__ == "__main__":
    header_mark()
    favicon()
