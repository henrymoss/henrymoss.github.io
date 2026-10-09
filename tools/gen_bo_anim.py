#!/usr/bin/env python3
"""The figure on the front page: a real Bayesian optimisation run, animated.

Not a cartoon — this fits an actual GP (RBF kernel, exact Cholesky inference)
and picks each next point by maximising expected improvement, then draws one
frame per iteration. The posterior band visibly collapses around the optimum.

Output is an animated SVG rather than a GIF or WebP, for one reason: a raster
animation always plays and cannot honour prefers-reduced-motion. Here the
frames are <g> elements flipped by CSS, so a visitor who has asked for less
movement is simply shown the converged final frame.

    python3 tools/gen_bo_anim.py

Writes images/bo-loop.svg. Safe to re-run; deterministic.
"""

import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVY = "#2d1e69"
BAND = "#cfc8ea"
TRUTH = "#a9a2cf"
ORANGE = "#f97b3d"
YELLOW = "#ffd23f"
WHITE = "#ffffff"

# --- plot geometry ------------------------------------------------------------
W, H = 760, 230
L, R, T, B = 26, 734, 24, 196
GRID = 80                 # posterior is evaluated on this many points
N_INIT, N_ITER = 2, 12    # starting designs, then this many EI steps

# --- the objective ------------------------------------------------------------
# A standard awkward 1-D test problem: several local optima, one global.
# Normalised to [-1, 1] so the prior variance below can be set against a known
# scale — otherwise the opening ±2σ band is several times the height of the
# plot box and simply spills off the top and bottom.


def _raw(x):
    return math.sin(18 * x) * (3 * x - 1.4)


_PEAK = max(abs(_raw(i / 400.0)) for i in range(401))


def f(x):
    return _raw(x) / _PEAK


# --- a small exact GP ---------------------------------------------------------
LS, SIG, NOISE = 0.055, 0.45, 1e-6

# Fixed symmetric y-range: the objective lives in [-1, 1] and a 2σ prior band
# reaches about ±1.34, so this holds the opening frame without squashing the
# converged one. Anything still outside is clipped to the plot box.
YLO, YHI = -1.85, 1.85


def kern(a, b):
    d = (a - b) / LS
    return SIG * math.exp(-0.5 * d * d)


def cholesky(A):
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                L[i][j] = math.sqrt(max(A[i][i] - s, 1e-12))
            else:
                L[i][j] = (A[i][j] - s) / L[j][j]
    return L


def solve(L, b):
    """Solve L Lᵀ x = b by forward then back substitution."""
    n = len(b)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
    return x


def posterior(xs, ys, grid):
    n = len(xs)
    K = [[kern(xs[i], xs[j]) + (NOISE if i == j else 0.0) for j in range(n)]
         for i in range(n)]
    L = cholesky(K)
    alpha = solve(L, ys)
    mean, sd = [], []
    for g in grid:
        ks = [kern(g, x) for x in xs]
        mean.append(sum(ks[i] * alpha[i] for i in range(n)))
        v = [0.0] * n                       # forward-solve L v = ks
        for i in range(n):
            v[i] = (ks[i] - sum(L[i][k] * v[k] for k in range(i))) / L[i][i]
        sd.append(math.sqrt(max(SIG - sum(t * t for t in v), 1e-12)))
    return mean, sd


def norm_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def norm_pdf(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def expected_improvement(mu, sd, best):
    """Classic EI — the acquisition that picks where to measure next."""
    out = []
    for m, s in zip(mu, sd):
        if s < 1e-9:
            out.append(0.0)
            continue
        z = (m - best) / s
        out.append((m - best) * norm_cdf(z) + s * norm_pdf(z))
    return out


# --- drawing ------------------------------------------------------------------

def run():
    grid = [i / (GRID - 1.0) for i in range(GRID)]
    truth = [f(g) for g in grid]
    lo, hi = YLO, YHI

    px = lambda x: L + x * (R - L)                      # noqa: E731
    py = lambda v: B - (v - lo) / (hi - lo) * (B - T)   # noqa: E731
    n = lambda v: f"{v:.1f}"                            # noqa: E731

    # deterministic starting design, then pure EI
    xs = [0.08, 0.62]
    ys = [f(x) for x in xs]

    frames = []
    for step in range(N_ITER + 1):
        mu, sd = posterior(xs, ys, grid)
        best = max(ys)
        ei = expected_improvement(mu, sd, best)
        nxt = grid[max(range(GRID), key=lambda i: ei[i])]

        upper = " ".join(f"{n(px(g))},{n(py(m + 2 * s))}"
                         for g, m, s in zip(grid, mu, sd))
        lower = " ".join(f"{n(px(g))},{n(py(m - 2 * s))}"
                         for g, m, s in reversed(list(zip(grid, mu, sd))))
        meanline = " ".join(f"{n(px(g))},{n(py(m))}" for g, m in zip(grid, mu))

        dots = "".join(
            f'<circle cx="{n(px(x))}" cy="{n(py(y))}" r="4.2" fill="{ORANGE}" '
            f'stroke="{WHITE}" stroke-width="1.6"/>'
            for x, y in zip(xs, ys))

        # mark where EI says to measure next, and the best point so far
        bi = ys.index(best)
        marker = (
            f'<line x1="{n(px(nxt))}" y1="{n(T)}" x2="{n(px(nxt))}" y2="{n(B)}" '
            f'stroke="{ORANGE}" stroke-width="1.4" stroke-dasharray="3 4" '
            f'opacity=".75"/>'
            if step < N_ITER else "")
        star = (f'<circle cx="{n(px(xs[bi]))}" cy="{n(py(ys[bi]))}" r="7.5" '
                f'fill="none" stroke="{YELLOW}" stroke-width="3"/>')

        frames.append(
            f'<g class="f f{step}" clip-path="url(#plot)">'
            f'<polygon points="{upper} {lower}" fill="{BAND}" opacity=".62"/>'
            f'{marker}'
            f'<polyline points="{meanline}" fill="none" stroke="{NAVY}" '
            f'stroke-width="2.4" stroke-linejoin="round"/>'
            f'{star}{dots}'
            f'</g>')

        if step < N_ITER:
            xs.append(nxt)
            ys.append(f(nxt))

    truth_line = " ".join(f"{n(px(g))},{n(py(t))}" for g, t in zip(grid, truth))
    base = (f'<polyline points="{truth_line}" fill="none" stroke="{TRUTH}" '
            f'stroke-width="1.8" stroke-dasharray="5 5"/>')

    total = len(frames)
    cycle = 9.0
    win = 100.0 / total
    # Positive delays, so each frame waits its turn and the run plays forwards.
    # A negative delay would start every frame partway through its own cycle,
    # which makes later frames reach their visible window sooner — i.e. the
    # whole animation runs backwards.
    delays = "\n".join(
        f"  .f{i} {{ animation-delay: {cycle * i / total:.2f}s }}"
        for i in range(total))

    style = f"""
  .f {{ opacity: 0; animation: boFlip {cycle}s linear infinite; }}
{delays}
  @keyframes boFlip {{
     0%, {win - 0.001:.3f}% {{ opacity: 1 }}
     {win:.3f}%, 100%       {{ opacity: 0 }}
  }}
  /* A raster animation could not do this: anyone who has asked for less
     movement simply gets the converged final frame. */
  @media (prefers-reduced-motion: reduce) {{
     .f {{ animation: none; opacity: 0 }}
     .f{total - 1} {{ opacity: 1 }}
  }}
"""
    clip = (f'<clipPath id="plot"><rect x="{L - 10}" y="{T - 16}" '
            f'width="{R - L + 20}" height="{B - T + 30}"/></clipPath>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img">\n'
           f'<style>{style}</style>\n<defs>{clip}</defs>\n{base}\n'
           + "\n".join(frames) + "\n</svg>\n")

    out = os.path.join(ROOT, "images", "bo-loop.svg")
    with open(out, "w") as fh:
        fh.write(svg)
    print("wrote images/bo-loop.svg  (%d frames, %d KB, %d evaluations)"
          % (total, os.path.getsize(out) // 1024, len(xs)))


if __name__ == "__main__":
    run()
