#!/usr/bin/env python3
"""The featured-research figure: a GP flow, after Figure 2 of "Conditioning
Gaussian Processes on Almost Anything".

White noise at t = 1 flows into samples from a GP predictive distribution at
t = 0, with the conditioning observations (red) fixed throughout.

This is the paper's own construction, not an impression of it. Equation (7)
gives the marginals in closed form,

    f_t = alpha(t) f_0 + sqrt(1 - alpha^2(t)) z,     z ~ N(0, I)

so holding one posterior draw f_0 and one noise draw z fixed and sweeping
alpha produces sample paths that are continuous in t — which is what makes the
lines morph rather than flicker. The shaded band is the marginal of
A(t) = alpha^2 K + (1 - alpha^2) I, likewise in closed form. Only a single
Cholesky is needed for the whole animation.

Output is an animated SVG for the same reason as the BO figure: a raster
animation cannot honour prefers-reduced-motion.

    python3 tools/gen_flow_anim.py

Writes images/gp-flow.svg. Deterministic; safe to re-run.
"""

import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVY = "#2d1e69"
BAND = "#cfc8ea"
DOT = "#d6212b"
PATHS = ["#5245c8", "#de6fa1", "#f97b3d", "#2d1e69", "#8ab0c9",
         "#6052ab", "#c4567f", "#e0a33d", "#5b8fa8"]

W, H = 760, 250
L, R, T, B = 26, 734, 20, 214
# GRID, N_PATH and FRAMES all multiply into the file size — every frame spells
# out every point of every path — so these are a balance, not free dials. A
# shorter lengthscale needs a finer grid to render its wiggles cleanly, which
# is why GRID moves whenever LS does.
GRID = 74                  # function is drawn on this many points
N_PATH = 8                 # sample trajectories
FRAMES = 42
YLO, YHI = -3.0, 3.0

LS, SIG, NOISE = 0.07, 1.0, 2e-3

# Observations only on the left. The right of the plot stays unconditioned, so
# the final frame shows both halves of the story at once: paths pinned to the
# data on one side, fanning out to the prior on the other.
OBS_X = [0.10, 0.27, 0.46]


def truth(x):
    return 1.5 * math.sin(5.2 * x) * math.exp(-0.7 * x)


# --- small exact GP (same machinery as gen_bo_anim.py) ------------------------

def kern(a, b):
    d = (a - b) / LS
    return SIG * math.exp(-0.5 * d * d)


def cholesky(A):
    n = len(A)
    Lm = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(Lm[i][k] * Lm[j][k] for k in range(j))
            if i == j:
                Lm[i][j] = math.sqrt(max(A[i][i] - s, 1e-12))
            else:
                Lm[i][j] = (A[i][j] - s) / Lm[j][j]
    return Lm


def solve(Lm, b):
    n = len(b)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(Lm[i][k] * y[k] for k in range(i))) / Lm[i][i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - sum(Lm[k][i] * x[k] for k in range(i + 1, n))) / Lm[i][i]
    return x


def posterior(xs, ys, grid):
    """Predictive mean and full covariance on the grid."""
    n = len(xs)
    K = [[kern(xs[i], xs[j]) + (NOISE if i == j else 0.0) for j in range(n)]
         for i in range(n)]
    Lk = cholesky(K)
    alpha = solve(Lk, ys)

    mean = [sum(kern(g, xs[i]) * alpha[i] for i in range(n)) for g in grid]

    # K_post = K_** - Ks^T K^-1 Ks, built column by column
    V = []
    for g in grid:
        ks = [kern(g, x) for x in xs]
        v = [0.0] * n
        for i in range(n):
            v[i] = (ks[i] - sum(Lk[i][k] * v[k] for k in range(i))) / Lk[i][i]
        V.append(v)
    m = len(grid)
    cov = [[kern(grid[i], grid[j]) - sum(V[i][k] * V[j][k] for k in range(n))
            + (1e-7 if i == j else 0.0) for j in range(m)] for i in range(m)]
    return mean, cov


def run():
    rng = random.Random(11)
    grid = [i / (GRID - 1.0) for i in range(GRID)]
    ys = [truth(x) for x in OBS_X]

    mean, cov = posterior(OBS_X, ys, grid)
    Lp = cholesky(cov)                      # the only m x m Cholesky needed
    sd0 = [math.sqrt(max(cov[i][i], 0.0)) for i in range(GRID)]

    # one posterior draw and one white-noise draw per trajectory, held fixed
    # across every frame so the paths deform continuously
    f0, zs = [], []
    for _ in range(N_PATH):
        u = [rng.gauss(0, 1) for _ in range(GRID)]
        f0.append([mean[i] + sum(Lp[i][k] * u[k] for k in range(i + 1))
                   for i in range(GRID)])
        zs.append([rng.gauss(0, 1) for _ in range(GRID)])

    px = lambda x: L + x * (R - L)                        # noqa: E731
    py = lambda v: B - (v - YLO) / (YHI - YLO) * (B - T)  # noqa: E731
    nf = lambda v: f"{v:.1f}"                             # noqa: E731

    frames = []
    for s in range(FRAMES):
        # step so the noise amplitude falls linearly — equal visual change
        noise_amp = 1.0 - s / (FRAMES - 1.0)
        a = math.sqrt(max(1.0 - noise_amp * noise_amp, 0.0))

        band_sd = [math.sqrt(a * a * v * v + (1 - a * a)) for v in sd0]
        up = " ".join(f"{nf(px(g))},{nf(py(a * mu + 2 * sdv))}"
                      for g, mu, sdv in zip(grid, mean, band_sd))
        dn = " ".join(f"{nf(px(g))},{nf(py(a * mu - 2 * sdv))}"
                      for g, mu, sdv in reversed(list(zip(grid, mean, band_sd))))

        lines = []
        for k in range(N_PATH):
            pts = " ".join(
                f"{nf(px(g))},{nf(py(a * f0[k][i] + noise_amp * zs[k][i]))}"
                for i, g in enumerate(grid))
            lines.append(f'<polyline points="{pts}" fill="none" '
                         f'stroke="{PATHS[k % len(PATHS)]}" stroke-width="1.3" '
                         f'opacity=".8"/>')

        # the observations stay put; the flow is what moves
        dots = "".join(
            f'<circle cx="{nf(px(x))}" cy="{nf(py(y))}" r="4" fill="{DOT}"/>'
            for x, y in zip(OBS_X, ys))

        # Time readout along the bottom. t = 0 is white noise, t = 1 the GP —
        # the flow-matching direction. The paper runs its own t the other way
        # (t = 1 initial, t = 0 final); flip `tv` below to match it.
        tv = s / (FRAMES - 1.0)
        x0 = L + 64
        meter = (
            f'<text x="{L}" y="243" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="12" fill="{NAVY}">t = {tv:.2f}</text>'
            f'<line x1="{x0}" y1="239" x2="{R}" y2="239" stroke="{BAND}" '
            f'stroke-width="3" stroke-linecap="round"/>'
            f'<line x1="{x0}" y1="239" x2="{x0 + tv * (R - x0):.1f}" y2="239" '
            f'stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>')

        # the plot clips, the readout below it must not
        cls = "f hold" if s == FRAMES - 1 else "f"
        frames.append(
            f'<g class="{cls} f{s}">'
            f'<g clip-path="url(#plot)">'
            f'<polygon points="{up} {dn}" fill="{BAND}" opacity=".55"/>'
            + "".join(lines) + dots + "</g>" + meter + "</g>")

    # The last frame — the converged GP — is held four times as long as the
    # rest, so the figure settles instead of snapping straight back to noise.
    cycle = 5.0
    hold = 0.22
    step = cycle * (1 - hold) / (FRAMES - 1)

    # Each frame stays lit for TWICE its slot, so consecutive frames overlap.
    # Frames sit in document order, so a later one simply paints over its
    # predecessor and the overlap is invisible — but it removes any chance of a
    # gap between one frame going dark and the next lighting up. Those gaps are
    # what showed as white flashes: at ~95ms per frame, rounding the delays to
    # hundredths of a second was enough to leave slivers with nothing on screen.
    # Delays are also emitted at four decimal places now rather than two.
    win = 2 * step
    delays = "\n".join(f"  .f{i} {{ animation-delay: {step * i:.4f}s }}"
                       for i in range(FRAMES))

    style = f"""
  .f {{ opacity: 0; animation: gpFlip {cycle}s linear infinite; }}
  .hold {{ animation-name: gpHold; }}
{delays}
  @keyframes gpFlip {{
     0%, {win / cycle * 100 - 0.001:.3f}% {{ opacity: 1 }}
     {win / cycle * 100:.3f}%, 100%      {{ opacity: 0 }}
  }}
  @keyframes gpHold {{
     0%, {hold * 100 - 0.001:.3f}% {{ opacity: 1 }}
     {hold * 100:.3f}%, 100%       {{ opacity: 0 }}
  }}
  @media (prefers-reduced-motion: reduce) {{
     .f {{ animation: none; opacity: 0 }}
     .f{FRAMES - 1} {{ opacity: 1 }}
  }}
"""
    clip = (f'<clipPath id="plot"><rect x="{L - 10}" y="{T - 10}" '
            f'width="{R - L + 20}" height="{B - T + 20}"/></clipPath>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img">\n<style>{style}</style>\n'
           f'<defs>{clip}</defs>\n' + "\n".join(frames) + "\n</svg>\n")

    out = os.path.join(ROOT, "images", "gp-flow.svg")
    with open(out, "w") as fh:
        fh.write(svg)
    print("wrote images/gp-flow.svg  (%d frames, %d paths, %d KB)"
          % (FRAMES, N_PATH, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    run()
