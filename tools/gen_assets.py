#!/usr/bin/env python3
"""Generate the image assets that are not photographs: the square headshot
crop, and an initials card for any group member we have no photo of.

The logo lockups, the header mark and the favicon come from gen_logo.py —
don't generate them here too, or the two scripts will fight over the files.

    python3 tools/gen_assets.py

Safe to re-run; it overwrites in place.
"""

import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCENT = "#5245c8"   # MARS violet
PALE = "#e7e4f8"     # light violet wash


def write(path, body, w, h, bg="#ffffff"):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img">\n'
        f'<rect width="{w}" height="{h}" fill="{bg}"/>\n{body}\n</svg>\n'
    )
    with open(full, "w") as f:
        f.write(svg)
    print("wrote", path)


# ---------------------------------------------------------------- headshot ---

def headshot():
    """Square-crop the full-size portrait down to the 400px card the site uses.

    images/henry.jpeg is the master; images/henry-headshot.jpg is derived and
    safe to regenerate.
    """
    im = Image.open(os.path.join(ROOT, "images/henry.jpeg"))
    w, h = im.size
    top = 200  # puts the top of the head ~10% down the square
    im = im.crop((0, top, w, top + w)).resize((400, 400), Image.LANCZOS)
    im.save(os.path.join(ROOT, "images/henry-headshot.jpg"), quality=88, optimize=True)
    print("wrote images/henry-headshot.jpg")


# ------------------------------------------------------------ person cards ---

# Slug -> initials, for members whose `image` in _data/people.yml points at
# images/people/<slug>.svg because we have no photo of them. Everyone currently
# listed has a real photo, so this is empty; add an entry when that changes,
# and remove it again (deleting the stale .svg) once a photo arrives.
PEOPLE = {}


def people():
    for slug, initials in PEOPLE.items():
        body = (
            f'<rect width="300" height="300" fill="{PALE}"/>'
            f'<circle cx="150" cy="150" r="96" fill="{ACCENT}" opacity="0.5"/>'
            f'<text x="150" y="150" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="82" font-weight="bold" fill="#ffffff" '
            f'text-anchor="middle" dominant-baseline="central">{initials}</text>'
        )
        write(f"images/people/{slug}.svg", body, w=300, h=300, bg=PALE)


if __name__ == "__main__":
    headshot()
    people()
