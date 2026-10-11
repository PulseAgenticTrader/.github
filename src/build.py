#!/usr/bin/env python3
"""Builds every image for the org profile.

    python3 src/build.py          # SVGs into profile/assets/ and brand/
    python3 src/build.py --png    # also the PNGs in brand/png/, through headless Chrome

All shapes and colours live here, so each image stays in one family.
"""
import math
import pathlib
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "profile" / "assets"
ICONS = ROOT / "brand" / "icons"
LOGO = ROOT / "brand" / "logo"
PNG = ROOT / "brand" / "png"

FONT = "ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"

# The palette is the repo banner's, so the org page and the repo read as one family.
THEMES = {
    "dark": dict(
        bg0="#0A0F1E", bg1="#121A2E", ink="#F1F5FB", muted="#9AA7BD", eyebrow="#5EEAD4",
        teal="#2DD4BF", indigo="#818CF8", dot="#FFFFFF", dot_op=0.075, edge="#FFFFFF",
        edge_top=0.16, edge_bot=0.05, halo_op=0.30, aura_op=0.13, comet="#F0FDFA",
        card0="#141D33", card1="#0D1426", card_edge="#FFFFFF", card_edge_op=0.10,
        chip="#FFFFFF", chip_op=0.07, arrow="#CBD5E1", shadow_op=0.0,
    ),
    "light": dict(
        bg0="#FBFCFE", bg1="#EDF1F8", ink="#0B1222", muted="#4A5568", eyebrow="#0F9488",
        teal="#0EA5A4", indigo="#6366F1", dot="#0B1222", dot_op=0.07, edge="#0B1222",
        edge_top=0.07, edge_bot=0.11, halo_op=0.16, aura_op=0.09, comet="#312E81",
        card0="#FFFFFF", card1="#F7F9FC", card_edge="#0B1222", card_edge_op=0.11,
        chip="#0B1222", chip_op=0.05, arrow="#334155", shadow_op=0.10,
    ),
}

# Accent pairs for the glyphs that sit on the dark tiles (the tiles look the same in both themes).
PULSE = ("#2DD4BF", "#818CF8")


def f(n):
    """Short number formatting for path data."""
    s = f"{n:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


# ---------------------------------------------------------------- shapes

def squircle(x, y, size, n=5.0, per_quadrant=56):
    """A superellipse, the continuous-corner shape app icons use."""
    r = size / 2
    cx, cy = x + r, y + r
    steps = per_quadrant * 4
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        pts.append((cx + r * math.copysign(abs(c) ** (2 / n), c),
                    cy + r * math.copysign(abs(s) ** (2 / n), s)))
    return "M" + "L".join(f"{f(px)} {f(py)}" for px, py in pts) + "Z"


SQ = squircle(0, 0, 1024)
SQ_RIM = squircle(3, 3, 1018)


def polyline(points):
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in points)


def length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def fraction_at(points, target):
    """How far along the polyline (0 to 1) the point `target` sits."""
    total, run = length(points), 0.0
    for a, b in zip(points, points[1:]):
        if b == target:
            return (run + math.dist(a, b)) / total
        run += math.dist(a, b)
    raise ValueError(target)


# ---------------------------------------------------------------- the wordmark

def wordmark(stroke="currentColor"):
    """Lowercase 'pulse', drawn as one monoline weight.

    Design units: x-height 100, baseline at y=0, stroke 22, so the letters
    are the same at every size and need no font.
    Outer box: x 0..502, y -140..40.
    """
    T, B, MID, R = -89, -11, -50, 39
    ASC, DESC = -129, 29
    p0, a, b, s, e0 = 11, 137, 263, 339, 413
    ec = e0 + R
    ex, ey = ec + R * math.cos(math.radians(40)), MID + R * math.sin(math.radians(40))
    d = [
        # p
        f"M{p0} {T}V{DESC}",
        f"M{p0} {MID}a{R} {R} 0 1 0 {2*R} 0a{R} {R} 0 1 0 {-2*R} 0",
        # u
        f"M{a} {T}V{MID}A{R} {R} 0 0 0 {a+2*R} {MID}",
        f"M{a+2*R} {T}V{B}",
        # l
        f"M{b} {ASC}V{B}",
        # s
        f"M{s+27} {-77}C{s+20} {-86} {s+10} {-89} {s-1} {-89}"
        f"C{s-17} {-89} {s-28} {-81} {s-28} {-69}"
        f"C{s-28} {-56} {s-15} {-53} {s} {-50}"
        f"C{s+15} {-47} {s+28} {-43} {s+28} {-30}"
        f"C{s+28} {-18} {s+17} {-11} {s+1} {-11}"
        f"C{s-11} {-11} {s-22} {-14} {s-29} {-23}",
        # e
        f"M{e0} {MID}H{e0+2*R}A{R} {R} 0 1 0 {f(ex)} {f(ey)}",
    ]
    return (f'<path d="{"".join(d)}" fill="none" stroke="{stroke}" stroke-width="22" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- tiles (the same in both themes)

def tile(p, glyph, accent, glow_at=(512, 420), glow_r=520):
    """A dark app-icon tile, 1024 units square, with a glyph on it."""
    return f'''<defs>
    <clipPath id="{p}clip"><path d="{SQ}"/></clipPath>
    <linearGradient id="{p}bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1B2649"/>
      <stop offset="0.55" stop-color="#0F1730"/>
      <stop offset="1" stop-color="#090D1B"/>
    </linearGradient>
    <radialGradient id="{p}glow" cx="{glow_at[0]}" cy="{glow_at[1]}" r="{glow_r}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.30"/>
      <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="{p}sheen" cx="512" cy="-120" r="760" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.13"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="{p}rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.26"/>
      <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.06"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.10"/>
    </linearGradient>
    <pattern id="{p}dots" width="64" height="64" patternUnits="userSpaceOnUse">
      <circle cx="32" cy="32" r="3.4" fill="#FFFFFF" fill-opacity="0.06"/>
    </pattern>
    <filter id="{p}blur" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="30"/>
    </filter>
  </defs>
  <g clip-path="url(#{p}clip)">
    <rect width="1024" height="1024" fill="url(#{p}bg)"/>
    <rect width="1024" height="1024" fill="url(#{p}dots)"/>
    <rect width="1024" height="1024" fill="url(#{p}glow)"/>
    <rect width="1024" height="1024" fill="url(#{p}sheen)"/>
    <g filter="url(#{p}blur)" opacity="0.75">{glyph}</g>
    {glyph}
  </g>
  <path d="{SQ_RIM}" fill="none" stroke="url(#{p}rim)" stroke-width="6"/>'''


def lin(id_, stops, x1, y1, x2, y2):
    def stop(o, c, a):
        op = "" if a is None else ' stop-opacity="%s"' % a
        return f'<stop offset="{o}" stop-color="{c}"{op}/>'
    s = "".join(stop(o, c, a) for o, c, a in stops)
    return (f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}">{s}</linearGradient>')


MARK_BEAT = [(170, 566), (336, 566), (390, 646), (462, 290), (604, 778), (672, 566), (854, 566)]
MARK_PEAK = (462, 290)


def pulse_glyph(p):
    g = lin(f"{p}beat", [(0, PULSE[0], 0.35), (0.22, PULSE[0], None), (0.78, PULSE[1], None),
                         (1, PULSE[1], 0.35)], 176, 0, 848, 0)
    px, py = MARK_PEAK
    return (f'<defs>{g}</defs>'
            f'<path d="{polyline(MARK_BEAT)}" fill="none" stroke="url(#{p}beat)" stroke-width="60" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{px}" cy="{py}" r="74" fill="none" stroke="{PULSE[1]}" stroke-opacity="0.45" stroke-width="12"/>'
            f'<circle cx="{px}" cy="{py}" r="40" fill="#E0E7FF"/>')


def evidence_glyph(p):
    g = lin(f"{p}g", [(0, PULSE[0], None), (1, PULSE[1], None)], 200, 200, 820, 820)
    return (f'<defs>{g}</defs>'
            f'<circle cx="452" cy="452" r="218" fill="none" stroke="url(#{p}g)" stroke-width="60"/>'
            f'<path d="M618 618L800 800" fill="none" stroke="url(#{p}g)" stroke-width="84" stroke-linecap="round"/>'
            f'<path d="M296 476H372L414 372L482 580L526 452H608" fill="none" stroke="#F1F5FB" '
            f'stroke-width="40" stroke-linecap="round" stroke-linejoin="round"/>')


def limits_glyph(p):
    g = lin(f"{p}g", [(0, PULSE[0], None), (1, PULSE[1], None)], 240, 180, 790, 860)
    return (f'<defs>{g}</defs>'
            f'<path d="M512 176L790 282V512C790 680 672 790 512 852C352 790 234 680 234 512V282Z" '
            f'fill="none" stroke="url(#{p}g)" stroke-width="60" stroke-linejoin="round"/>'
            f'<path d="M396 518L478 600L636 438" fill="none" stroke="#F1F5FB" stroke-width="56" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def code_glyph(p):
    g = lin(f"{p}g", [(0, PULSE[0], None), (1, PULSE[1], None)], 200, 300, 824, 720)
    st = f'fill="none" stroke="url(#{p}g)" stroke-width="64" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<defs>{g}</defs>'
            f'<path d="M372 334L206 512L372 690" {st}/>'
            f'<path d="M652 334L818 512L652 690" {st}/>'
            f'<path d="M568 296L456 728" fill="none" stroke="#F1F5FB" stroke-width="56" stroke-linecap="round"/>')


def nested(x, y, size, inner):
    return f'<svg x="{f(x)}" y="{f(y)}" width="{f(size)}" height="{f(size)}" viewBox="0 0 1024 1024">{inner}</svg>'


def standalone_tile(title, glyph_fn, accent, glow_at=(512, 420)):
    inner = tile("t", glyph_fn("t"), accent, glow_at)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024" '
            f'role="img" aria-label="{title}"><title>{title}</title>{inner}</svg>\n')


# ---------------------------------------------------------------- the banner

BEAT = [(540, 198), (722, 198), (750, 180), (776, 198), (810, 198), (832, 238), (864, 66),
        (898, 280), (926, 198), (968, 198), (1002, 170), (1042, 198), (1280, 198)]
PEAK = (864, 66)


def banner(theme):
    t = THEMES[theme]
    W, H = 1280, 360
    beat_d = polyline(BEAT)
    peak_f = fraction_at(BEAT, PEAK)
    cycle, travel = 4.6, 0.62           # seconds per beat, share of it the comet spends moving
    hit = travel * (100 * peak_f) / 112  # when the comet's head reaches the peak
    px, py = PEAK

    def comet(cls, dash, width, op):
        return (f'<path class="{cls}" d="{beat_d}" pathLength="100" fill="none" stroke="{t["comet"]}" '
                f'stroke-opacity="{op}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" '
                f'stroke-dasharray="{dash} 300" stroke-dashoffset="{dash}"/>')

    style = f'''
    .c1,.c2,.c3 {{ animation: run {cycle}s linear infinite; }}
    .c1 {{ animation-name: run1; }} .c2 {{ animation-name: run2; }} .c3 {{ animation-name: run3; }}
    @keyframes run1 {{ 0% {{ stroke-dashoffset: 16; }} {travel*100:.1f}% {{ stroke-dashoffset: -96; }} 100% {{ stroke-dashoffset: -96; }} }}
    @keyframes run2 {{ 0% {{ stroke-dashoffset: 7; }} {travel*100:.1f}% {{ stroke-dashoffset: -105; }} 100% {{ stroke-dashoffset: -105; }} }}
    @keyframes run3 {{ 0% {{ stroke-dashoffset: 1.6; }} {travel*100:.1f}% {{ stroke-dashoffset: -110.4; }} 100% {{ stroke-dashoffset: -110.4; }} }}
    .ring {{ transform-box: fill-box; transform-origin: center; animation: ring {cycle}s ease-out infinite; opacity: 0; }}
    @keyframes ring {{ 0%, {hit*100-0.1:.1f}% {{ transform: scale(1); opacity: 0; }}
      {hit*100:.1f}% {{ transform: scale(1); opacity: 0.85; }}
      {hit*100+22:.1f}% {{ transform: scale(3.4); opacity: 0; }} 100% {{ opacity: 0; }} }}
    .dot {{ transform-box: fill-box; transform-origin: center; animation: dot {cycle}s ease-out infinite; }}
    @keyframes dot {{ 0%, {hit*100-0.1:.1f}% {{ transform: scale(1); }} {hit*100+1.5:.1f}% {{ transform: scale(1.45); }}
      {hit*100+14:.1f}% {{ transform: scale(1); }} 100% {{ transform: scale(1); }} }}
    .comet {{ animation: fadecomet {cycle}s linear infinite; }}
    @keyframes fadecomet {{ 0% {{ opacity: 0; }} {travel*100*0.16:.1f}% {{ opacity: 1; }}
      {travel*100*0.80:.1f}% {{ opacity: 1; }} {travel*100:.1f}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .comet, .ring {{ display: none; }}
      .dot {{ animation: none; }}
    }}'''

    lockup_x, base_y, scale = 96, 212, 0.66
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">Pulse</title>
  <desc id="desc">Pulse: automated trading on the pump.fun launchpads. Evidence first. Hard limits. Only code trades.</desc>
  <style>{style}
  </style>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t["bg0"]}"/>
      <stop offset="1" stop-color="{t["bg1"]}"/>
    </linearGradient>
    {lin("beat", [(0, t["teal"], 0), (0.22, t["teal"], None), (0.62, t["indigo"], None), (1, t["indigo"], 0)], BEAT[0][0], 0, W, 0)}
    <radialGradient id="halo" cx="{px}" cy="{py}" r="190" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t["indigo"]}" stop-opacity="{t["halo_op"]}"/>
      <stop offset="1" stop-color="{t["indigo"]}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="aura" cx="1160" cy="400" r="360" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t["teal"]}" stop-opacity="{t["aura_op"]}"/>
      <stop offset="1" stop-color="{t["teal"]}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="fade" cx="900" cy="190" r="760" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="0.75" stop-color="#FFFFFF" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.15"/>
    </radialGradient>
    <mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="{t["dot"]}" fill-opacity="{t["dot_op"]}"/>
    </pattern>
    <linearGradient id="rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t["edge"]}" stop-opacity="{t["edge_top"]}"/>
      <stop offset="1" stop-color="{t["edge"]}" stop-opacity="{t["edge_bot"]}"/>
    </linearGradient>
    <filter id="glow" x="-10%" y="-60%" width="120%" height="220%">
      <feGaussianBlur stdDeviation="7"/>
    </filter>
    <filter id="soft" x="-10%" y="-60%" width="120%" height="220%">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridmask)"/>
    <rect width="{W}" height="{H}" fill="url(#aura)"/>
    <circle cx="{px}" cy="{py}" r="190" fill="url(#halo)"/>
    <path d="{beat_d}" fill="none" stroke="url(#beat)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity="0.35" filter="url(#glow)"/>
    <path d="{beat_d}" fill="none" stroke="url(#beat)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
    <g class="comet">
      <g filter="url(#soft)">{comet("c1", 16, 0.30, 6)}</g>
      {comet("c2", 7, 0.55, 4)}
      {comet("c3", 1.6, 1, 5)}
    </g>
    <circle class="ring" cx="{px}" cy="{py}" r="12" fill="none" stroke="{t["indigo"]}" stroke-width="2"/>
    <circle cx="{px}" cy="{py}" r="12" fill="none" stroke="{t["indigo"]}" stroke-opacity="0.35" stroke-width="2"/>
    <circle class="dot" cx="{px}" cy="{py}" r="6" fill="{t["indigo"]}"/>
  </g>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="23.5" fill="none" stroke="url(#rim)"/>
  <g font-family="{FONT}">
    <text x="{lockup_x}" y="104" fill="{t["eyebrow"]}" font-size="15" font-weight="700" letter-spacing="3.5">SOLANA · PUMP.FUN FAMILY</text>
    <text x="{lockup_x}" y="284" fill="{t["muted"]}" font-size="23" font-weight="500">Evidence first. Hard limits. Only code trades.</text>
  </g>
  <g transform="translate({lockup_x} {base_y}) scale({scale})" color="{t["ink"]}">{wordmark()}</g>
</svg>
'''



# ---------------------------------------------------------------- the Pulse tab icons, for the apps

# The mark's beat, redrawn per grid so it stays sharp when small. The peak dot is what tells it apart
# from a generic "activity" icon, so every size keeps it.
TAB = {
    24: dict(stroke=2, dot=2,
             beat=[(2, 13), (6, 13), (7.5, 15.5), (9.75, 4.75), (14.5, 20), (16.75, 13), (22, 13)]),
    16: dict(stroke=1.5, dot=1.6,
             beat=[(1.5, 8.75), (4, 8.75), (5, 10.5), (6.5, 3.25), (9.75, 13.5), (11.25, 8.75), (14.5, 8.75)]),
}
# The active icon: the beat cut out of a filled tile, the same tile as the mark.
TAB_ACTIVE = {24: dict(box=(2, 20), stroke=1.75, dot=1.55), 16: dict(box=(1, 14), stroke=1.4, dot=1.25)}
TAB_COLOR = ("#22C3B0", "#737BF5")  # mid tones, readable on light and dark


def peak_of(beat):
    return min(beat, key=lambda pt: pt[1])


def icon_head(size, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
            f'fill="none" role="img" aria-label="{label}"><title>{label}</title>')


def tab_icon(size):
    t = TAB[size]
    (px, py) = peak_of(t["beat"])
    return (icon_head(size, "Pulse")
            + f'<path d="{polyline(t["beat"])}" stroke="currentColor" stroke-width="{t["stroke"]}" '
              f'stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<circle cx="{f(px)}" cy="{f(py)}" r="{t["dot"]}" fill="currentColor"/></svg>\n')


def tab_icon_color(size):
    t = TAB[size]
    (px, py) = peak_of(t["beat"])
    x0, x1 = t["beat"][0][0], t["beat"][-1][0]
    g = lin(f"pulse-{size}-color", [(0, TAB_COLOR[0], None), (1, TAB_COLOR[1], None)], x0, 0, x1, 0)
    return (icon_head(size, "Pulse") + f"<defs>{g}</defs>"
            + f'<path d="{polyline(t["beat"])}" stroke="url(#pulse-{size}-color)" stroke-width="{t["stroke"]}" '
              f'stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<circle cx="{f(px)}" cy="{f(py)}" r="{t["dot"]}" fill="{TAB_COLOR[1]}"/></svg>\n')


def tab_icon_active(size):
    a = TAB_ACTIVE[size]
    o, box = a["box"]
    k = box / 1024
    beat = [(o + x * k, o + y * k) for x, y in MARK_BEAT]
    px, py = o + MARK_PEAK[0] * k, o + MARK_PEAK[1] * k
    mid = f"pulse-{size}-active-cut"
    return (icon_head(size, "Pulse")
            + f'<defs><mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{size}" height="{size}">'
              f'<rect width="{size}" height="{size}" fill="#fff"/>'
              f'<path d="{polyline(beat)}" stroke="#000" stroke-width="{a["stroke"]}" stroke-linecap="round" stroke-linejoin="round"/>'
              f'<circle cx="{f(px)}" cy="{f(py)}" r="{a["dot"]}" fill="#000"/></mask></defs>'
            + f'<path d="{squircle(o, o, box, per_quadrant=24)}" fill="currentColor" mask="url(#{mid})"/></svg>\n')


def wordmark_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="502" height="180" viewBox="0 -140 502 180" '
            'role="img" aria-label="Pulse"><title>Pulse</title>' + wordmark() + '</svg>\n')

# ---------------------------------------------------------------- small pieces

def divider():
    """A flat trace with one small beat in the middle. Mid-tone colours, so one file serves both themes."""
    W, H, y = 1280, 40, 22
    pts = [(0, y), (604, y), (616, y - 4), (626, y), (634, y), (640, y + 6), (648, y - 16),
           (657, y + 10), (664, y), (676, y), (686, y - 5), (698, y), (1280, y)]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="presentation">
  <defs>
    {lin("g", [(0, "#14B8A6", 0), (0.36, "#14B8A6", 0.7), (0.5, "#6366F1", 1), (0.64, "#6366F1", 0.7), (1, "#6366F1", 0)], 0, 0, W, 0)}
  </defs>
  <path d="{polyline(pts)}" fill="none" stroke="url(#g)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="648" cy="{y-16}" r="2.6" fill="#6366F1"/>
</svg>
'''


def lockup(theme):
    """The mark and the wordmark side by side, for anywhere the logo is needed."""
    t = THEMES[theme]
    W, H = 760, 240
    mark = nested(56, 42, 128, tile("m", pulse_glyph("m"), PULSE[1], (MARK_PEAK[0], 420)))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Pulse">
  <title>Pulse</title>
  {mark}
  <g transform="translate(224 150) scale(0.86)" color="{t["ink"]}">{wordmark()}</g>
</svg>
'''


def avatar():
    """Full-bleed square for the org avatar. GitHub rounds the corners itself."""
    inner = tile("a", pulse_glyph("a"), PULSE[1], (MARK_PEAK[0], 420))
    inner = inner.replace(f'<path d="{SQ}"/>', '<rect width="1024" height="1024"/>', 1)
    inner = inner.split(f'<path d="{SQ_RIM}"')[0]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024" '
            f'role="img" aria-label="Pulse"><title>Pulse</title>{inner}</svg>\n')


# ---------------------------------------------------------------- build

def write(name, text, where=ASSETS):
    where.mkdir(parents=True, exist_ok=True)
    (where / name).write_text(text)
    print(f"wrote {(where / name).relative_to(ROOT)}  ({len(text.encode()) / 1024:.1f} KB)")


def png(svg_path, out_path, w, h):
    """Headless Chrome writes the screenshot and then sometimes lingers, so stop it once the file lands."""
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        proc = subprocess.Popen([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                 f"--user-data-dir={profile}", "--force-device-scale-factor=1",
                                 f"--window-size={w},{h}", "--default-background-color=00000000",
                                 f"--screenshot={out_path}", svg_path.as_uri()],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(600):
                if out_path.exists() and out_path.stat().st_size:
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError(f"no screenshot for {svg_path.name}")
        finally:
            proc.terminate()
            proc.wait(timeout=15)
    print(f"wrote {out_path.relative_to(ROOT)}")


def main():
    # The org profile page
    for theme in THEMES:
        write(f"banner-{theme}.svg", banner(theme))
    write("logo.svg", standalone_tile("Pulse", pulse_glyph, PULSE[1], (MARK_PEAK[0], 420)))
    write("icon-evidence.svg", standalone_tile("Evidence first", evidence_glyph, PULSE[0]))
    write("icon-limits.svg", standalone_tile("Hard limits", limits_glyph, PULSE[1]))
    write("icon-code.svg", standalone_tile("Only code trades", code_glyph, PULSE[0]))
    write("divider.svg", divider())

    # The Pulse tab icons, for the apps
    for size in TAB:
        write(f"pulse-{size}.svg", tab_icon(size), ICONS)
        write(f"pulse-{size}-active.svg", tab_icon_active(size), ICONS)
        write(f"pulse-{size}-color.svg", tab_icon_color(size), ICONS)

    # The logo
    write("mark.svg", standalone_tile("Pulse", pulse_glyph, PULSE[1], (MARK_PEAK[0], 420)), LOGO)
    write("wordmark.svg", wordmark_svg(), LOGO)
    for theme in THEMES:
        write(f"lockup-{theme}.svg", lockup(theme), LOGO)
    write("avatar.svg", avatar(), LOGO)

    if "--png" in sys.argv:
        png(LOGO / "avatar.svg", PNG / "avatar-1024.png", 1024, 1024)
        png(LOGO / "mark.svg", PNG / "mark-1024.png", 1024, 1024)
        for theme in THEMES:
            png(LOGO / f"lockup-{theme}.svg", PNG / f"lockup-{theme}.png", 760, 240)


if __name__ == "__main__":
    main()
