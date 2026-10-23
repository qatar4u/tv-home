"""Qatar landmarks at night in gold and maroon, drawn from code as SVG (1280x800, 16:10 for tablets).
Original illustrations. The lower part stays dark so the dock and the tiles stay readable.

    python3 tools/qatar4u/qatar_night_gold.py out_dir
"""
import math, os, random, sys

W, H = 1280, 800
OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)

GOLD = "#e3b65c"
GOLD_LIGHT = "#ffe4a3"
GOLD_DEEP = "#9a6a24"
MAROON = "#5b0f26"
MAROON_DEEP = "#2a0612"
NIGHT = "#04040b"


def lg(i, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{st[0]}" stop-color="{st[1]}" stop-opacity="{st[2] if len(st) > 2 else 1}"/>'
                for st in stops)
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(i, c, a=1.0, mid=0.3):
    return (f'<radialGradient id="{i}"><stop offset="0" stop-color="{c}" stop-opacity="{a}"/>'
            f'<stop offset=".45" stop-color="{c}" stop-opacity="{a * mid:.3f}"/>'
            f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')


BLUR = "".join(f'<filter id="b{n}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{n}"/></filter>'
               for n in (1, 2, 3, 5, 8, 14, 24, 40))


def star8(cx, cy, r):
    """An eight-pointed star (khatam) outline."""
    pts = []
    for k in range(16):
        a = math.pi / 8 * k - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.62
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def pattern_defs():
    """A faint gold khatam lattice that fades out towards the horizon."""
    cell = 64
    tile = (f'<path d="{star8(cell / 2, cell / 2, 22)}" fill="none" stroke="{GOLD}" stroke-width=".8"/>'
            f'<path d="M0,{cell/2} L{cell/2-22},{cell/2} M{cell/2+22},{cell/2} L{cell},{cell/2} '
            f'M{cell/2},0 L{cell/2},{cell/2-22} M{cell/2},{cell/2+22} L{cell/2},{cell}" stroke="{GOLD}" stroke-width=".6"/>')
    return (f'<pattern id="khatam" width="{cell}" height="{cell}" patternUnits="userSpaceOnUse">{tile}</pattern>'
            + lg("patfade", [(0, "#fff", 1), (0.35, "#fff", 0.35), (0.6, "#fff", 0)])
            + f'<mask id="patmask"><rect width="{W}" height="{H}" fill="url(#patfade)"/></mask>')


def pattern(op=0.07):
    return f'<rect width="{W}" height="{H}" fill="url(#khatam)" opacity="{op}" mask="url(#patmask)"/>'


def stars(seed, n, ymax, op=0.85):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x = r.uniform(0, W)
        y = r.uniform(0, 1) ** 1.6 * ymax
        rad = r.choice([0.5, 0.7, 0.9, 1.1, 1.5])
        col = r.choice(["#ffffff", "#fff1cf", GOLD_LIGHT])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad}" fill="{col}" opacity="{r.uniform(.25, op):.2f}"/>')
    # a few sparkles
    for _ in range(max(2, n // 40)):
        x, y = r.uniform(40, W - 40), r.uniform(10, ymax * 0.7)
        s = r.uniform(4, 7)
        out.append(f'<path d="M{x:.0f},{y-s:.0f} L{x+0.8:.1f},{y:.0f} L{x:.0f},{y+s:.0f} L{x-0.8:.1f},{y:.0f} Z '
                   f'M{x-s:.0f},{y:.0f} L{x:.0f},{y+0.8:.1f} L{x+s:.0f},{y:.0f} L{x:.0f},{y-0.8:.1f} Z" fill="{GOLD_LIGHT}" opacity=".8"/>')
    return "".join(out)


def crescent(cx, cy, r, mid):
    """A crescent as one path: the moon's disc minus an offset disc (no masks, so every renderer agrees)."""
    ox, oy, r2 = cx + r * 0.42, cy - r * 0.22, r * 0.88
    d = math.hypot(ox - cx, oy - cy)
    a = (r * r - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(r * r - a * a, 0))
    ux, uy = (ox - cx) / d, (oy - cy) / d
    px, py = cx + a * ux, cy + a * uy
    p1 = (px + h * uy, py - h * ux)
    p2 = (px - h * uy, py + h * ux)
    path = (f"M{p1[0]:.2f},{p1[1]:.2f} A{r},{r} 0 1 0 {p2[0]:.2f},{p2[1]:.2f} "
            f"A{r2},{r2} 0 0 1 {p1[0]:.2f},{p1[1]:.2f} Z")
    return (f'<circle cx="{cx}" cy="{cy}" r="{r*5}" fill="url(#moonglow)"/>'
            f'<path d="{path}" fill="url(#moonfill)"/>')


def full_moon(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r*6}" fill="url(#moonglow)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#moonfill)"/>'
            f'<circle cx="{cx-r*0.3}" cy="{cy-r*0.2}" r="{r*0.18}" fill="#d9b878" opacity=".35"/>'
            f'<circle cx="{cx+r*0.25}" cy="{cy+r*0.3}" r="{r*0.12}" fill="#d9b878" opacity=".3"/>')


def dunes(seed, base, amp, color, waves=2.2, step=8, extra=""):
    r = random.Random(seed)
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    pts = []
    for x in range(-step, W + 2 * step, step):
        y = base - amp * (0.6 * math.sin(x / W * 6.28 * waves * 0.5 + ph[0])
                          + 0.3 * math.sin(x / W * 6.28 * waves + ph[1])
                          + 0.1 * math.sin(x / W * 6.28 * waves * 2.3 + ph[2]))
        pts.append(f"{x},{y:.1f}")
    return f'<path d="M{" L".join(pts)} L{W+2*step},{H} L{-step},{H} Z" fill="{color}" {extra}/>'


def ridge(seed, base, amp, waves=2.2, step=8, color=GOLD, op=0.5):
    """The moonlit crest line of a dune."""
    r = random.Random(seed)
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    pts = []
    for x in range(-step, W + 2 * step, step):
        y = base - amp * (0.6 * math.sin(x / W * 6.28 * waves * 0.5 + ph[0])
                          + 0.3 * math.sin(x / W * 6.28 * waves + ph[1])
                          + 0.1 * math.sin(x / W * 6.28 * waves * 2.3 + ph[2]))
        pts.append(f"{x},{y:.1f}")
    return f'<path d="M{" L".join(pts)}" stroke="{color}" stroke-width="1.4" fill="none" opacity="{op}"/>'


def palm(x, y, h, color="#07040a", s=1.0, rim=None):
    trunk = f'<path d="M{x},{y} Q{x+7*s},{y-h*0.5} {x+3*s},{y-h}" stroke="{color}" stroke-width="{5.5*s}" fill="none" stroke-linecap="round"/>'
    tx, ty = x + 3 * s, y - h
    fr = []
    for a in (-165, -140, -112, -85, -58, -32, -8, 14, 196, 222):
        ang = math.radians(a)
        L = (38 + (abs(a) % 4) * 5) * s
        ex, ey = tx + math.cos(ang) * L, ty + math.sin(ang) * L * 0.5 + L * 0.42
        mx, my = tx + math.cos(ang) * L * 0.5, ty + math.sin(ang) * L * 0.55 - 7 * s
        fr.append(f'<path d="M{tx},{ty} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}" stroke="{color}" stroke-width="{3.4*s}" fill="none" stroke-linecap="round"/>')
        if rim:
            fr.append(f'<path d="M{tx},{ty} Q{mx:.1f},{my-1.5:.1f} {ex:.1f},{ey-1:.1f}" stroke="{rim}" stroke-width=".7" fill="none" opacity=".45"/>')
    return trunk + "".join(fr)


def water(hz, seed, streaks=110, color=GOLD_LIGHT, bright_x=None):
    r = random.Random(seed)
    s = [f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#water)"/>']
    for _ in range(streaks):
        y = r.uniform(hz + 3, H)
        depth = (y - hz) / (H - hz)
        w = r.uniform(18, 150) * (0.35 + depth)
        if bright_x is not None and r.random() < 0.55:
            x = bright_x + r.gauss(0, 60 + 160 * depth) - w / 2
            op = r.uniform(.12, .34) * (1 - depth * 0.6)
        else:
            x = r.uniform(-50, W)
            op = r.uniform(.03, .10)
        s.append(f'<rect x="{x:.0f}" y="{y:.1f}" width="{w:.0f}" height="{1 + depth*1.6:.1f}" rx="1" fill="{color}" opacity="{op:.2f}"/>')
    return "".join(s)


def reflect(g, hz, op=0.38, blur=3):
    return f'<g transform="translate(0,{2*hz}) scale(1,-1)" opacity="{op}" filter="url(#b{blur})">{g}</g>'


def haze(cx, cy, rx, ry, op=0.55, gid="haze"):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{gid})" opacity="{op}"/>'


def svg(defs, body, pat=0.06):
    shade = lg("shade", [(0, "#000", 0), (0.5, "#000", 0), (0.66, "#000", 0.42), (0.84, "#000", 0.72), (1, "#000", 0.9)])
    vign = (f'<radialGradient id="vign" cx=".5" cy=".42" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>')
    common = (BLUR + shade + vign + pattern_defs()
              + rg("moonglow", "#ffe2a0", 0.28, 0.25)
              + f'<radialGradient id="moonfill" cx=".38" cy=".35"><stop offset="0" stop-color="#fff8e6"/><stop offset="1" stop-color="#f0cf86"/></radialGradient>'
              + rg("haze", "#c8406a", 0.6, 0.35)
              + rg("goldhaze", "#e9a948", 0.55, 0.3)
              + lg("goldv", [(0, GOLD_LIGHT), (0.5, GOLD), (1, GOLD_DEEP)])
              + lg("goldh", [(0, GOLD_DEEP), (0.5, GOLD_LIGHT), (1, GOLD_DEEP)], 1, 0))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{common}{defs}</defs>{body}{pattern(pat)}'
            f'<rect width="{W}" height="{H}" fill="url(#vign)"/><rect width="{W}" height="{H}" fill="url(#shade)"/></svg>')


def night_sky(top=NIGHT, mid="#0d0a1e", low="#3a0c22", horizon="#7a1e3a"):
    return lg("sky", [(0, top), (0.3, mid), (0.5, low), (0.64, horizon), (1, MAROON_DEEP)])


def sky_body(seed, n, ymax):
    return f'<rect width="{W}" height="{H}" fill="url(#sky)"/>' + stars(seed, n, ymax)


scenes = {}


# 1. Museum of Islamic Art ------------------------------------------------------------------------------
def mia():
    hz = 470
    cx = 640
    defs = (night_sky(horizon="#6a1a34")
            + lg("water", [(0, "#3a1426"), (0.25, "#160814"), (1, "#020104")])
            + lg("stone", [(0, "#f6e2bf"), (0.55, "#cfa970"), (1, "#7d5a2c")], 1, 0)
            + lg("stoneShadow", [(0, "#5a4322"), (1, "#2a1e10")], 1, 0))
    b = []
    # stepped volumes, lit from the front by gold floodlights
    vols = [(-200, 0, 400, 105), (-150, 105, 300, 92), (-88, 197, 176, 86), (-36, 283, 72, 30)]
    for dx, up, w, h in vols:
        y = hz - up - h
        b.append(f'<rect x="{cx+dx}" y="{y}" width="{w}" height="{h}" fill="url(#stone)"/>')
        b.append(f'<rect x="{cx+dx}" y="{y}" width="{w*0.18:.0f}" height="{h}" fill="url(#stoneShadow)" opacity=".75"/>')
        b.append(f'<rect x="{cx+dx}" y="{y}" width="{w}" height="2" fill="{GOLD_LIGHT}" opacity=".9"/>')
    # chamfered shoulders
    b.append(f'<path d="M{cx-150},{hz-197} L{cx},{hz-226} L{cx+150},{hz-197} Z" fill="#e8cf9d"/>')
    b.append(f'<path d="M{cx-88},{hz-283} L{cx-50},{hz-312} L{cx+50},{hz-312} L{cx+88},{hz-283} Z" fill="#f0d9a8"/>')
    # the eye window
    eye = f'M{cx-40},{hz-240} Q{cx},{hz-262} {cx+40},{hz-240} Q{cx},{hz-218} {cx-40},{hz-240} Z'
    b.append(f'<path d="{eye}" fill="{GOLD_LIGHT}" filter="url(#b8)" opacity=".9"/>')
    b.append(f'<path d="{eye}" fill="#fff3d0"/>')
    b.append(f'<path d="{eye}" fill="none" stroke="{GOLD_DEEP}" stroke-width="1.2"/>')
    # lit arcade
    for i in range(-4, 5):
        x = cx + i * 40
        b.append(f'<path d="M{x-8},{hz} L{x-8},{hz-34} Q{x},{hz-46} {x+8},{hz-34} L{x+8},{hz} Z" fill="{GOLD_LIGHT}" opacity=".85"/>')
    building = "".join(b)
    land = (f'<rect x="0" y="{hz-5}" width="{W}" height="7" fill="#0c0610"/>'
            + "".join(f'<circle cx="{x}" cy="{hz-6}" r="1.8" fill="{GOLD_LIGHT}"/>' for x in range(30, W, 34)))
    palms = "".join(palm(x, hz - 4, 92 + (x % 41), "#070309", 1.0, GOLD) for x in (90, 175, 250, 1030, 1110, 1195))
    body = (sky_body(11, 140, 300)
            + crescent(985, 120, 26, 1)
            + haze(cx, hz, 620, 150, 0.6)
            + haze(cx, hz - 140, 260, 200, 0.35, "goldhaze")
            + water(hz, 3, 140, GOLD_LIGHT, cx)
            + reflect(building + palms, hz, 0.42, 3)
            + building + land + palms)
    return svg(defs, body)
scenes["01-museum-islamic-art"] = mia


# 2. West Bay skyline ------------------------------------------------------------------------------------
def westbay():
    hz = 500
    r = random.Random(5)
    defs = (night_sky(mid="#0b0a22", low="#2e0b24", horizon="#6e1c3a")
            + lg("water", [(0, "#22101e"), (1, "#010103")])
            + lg("doha", [(0, "#7a5420"), (0.45, "#f1cc7c"), (0.6, "#e3b65c"), (1, "#5a3a12")], 1, 0)
            + lg("tornado", [(0, "#4a0b22"), (0.5, "#a3264d"), (1, "#3a0818")], 1, 0)
            + lg("spire", [(0, "#1c1530"), (0.5, "#3a2e58"), (1, "#141022")], 1, 0))
    b = []
    xs = 40
    while xs < W - 30:
        w = r.randint(38, 78)
        h = r.randint(100, 250)
        col = r.choice(["#120c1c", "#160f22", "#0e0a16", "#1a1226"])
        b.append(f'<rect x="{xs}" y="{hz-h}" width="{w}" height="{h}" fill="{col}"/>')
        b.append(f'<rect x="{xs}" y="{hz-h}" width="{w}" height="1.5" fill="{GOLD}" opacity=".55"/>')
        for wy in range(hz - h + 8, hz - 6, 9):
            for wx in range(xs + 5, xs + w - 5, 8):
                if r.random() < 0.33:
                    b.append(f'<rect x="{wx}" y="{wy}" width="4" height="3" fill="{r.choice([GOLD_LIGHT, "#ffd08a", "#fff0cf"])}" opacity="{r.uniform(.3,.95):.2f}"/>')
        xs += w + r.randint(3, 16)
    # Doha Tower in gold with diagrid
    cx = 470
    b.append(f'<path d="M{cx-38},{hz} L{cx-38},{hz-330} Q{cx},{hz-420} {cx+38},{hz-330} L{cx+38},{hz} Z" fill="url(#doha)"/>')
    for k in range(0, 330, 20):
        b.append(f'<path d="M{cx-38},{hz-k} L{cx+38},{hz-k-20} M{cx+38},{hz-k} L{cx-38},{hz-k-20}" stroke="#5a3a12" stroke-width=".9" opacity=".55"/>')
    b.append(f'<line x1="{cx}" y1="{hz-410}" x2="{cx}" y2="{hz-446}" stroke="{GOLD_LIGHT}" stroke-width="2"/>')
    b.append(f'<circle cx="{cx}" cy="{hz-446}" r="3" fill="#ff5a6a"/>')
    # Tornado Tower in maroon light
    tx = 760
    pts_l = [(tx - 44 + 16 * math.sin(math.pi * k / 22), hz - k * 14) for k in range(23)]
    pts_r = [(tx + 44 - 16 * math.sin(math.pi * k / 22), hz - k * 14) for k in range(22, -1, -1)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts_l + pts_r) + " Z"
    b.append(f'<path d="{d}" fill="url(#tornado)"/>')
    for k in range(1, 22):
        y = hz - k * 14
        hw = 44 - 16 * math.sin(math.pi * k / 22)
        b.append(f'<line x1="{tx-hw:.1f}" y1="{y}" x2="{tx+hw:.1f}" y2="{y}" stroke="{GOLD_LIGHT}" stroke-width=".9" opacity=".55"/>')
    # a tall spire tower with a gold seam
    bx = 980
    b.append(f'<path d="M{bx-30},{hz} L{bx-24},{hz-360} L{bx},{hz-404} L{bx+24},{hz-360} L{bx+30},{hz} Z" fill="url(#spire)"/>')
    b.append(f'<path d="M{bx},{hz-404} L{bx},{hz-10}" stroke="{GOLD}" stroke-width="2" opacity=".85"/>')
    city = "".join(b)
    body = (sky_body(21, 150, 330) + crescent(1150, 110, 22, 2)
            + haze(640, hz, 760, 190, 0.75)
            + haze(470, hz - 160, 200, 260, 0.35, "goldhaze")
            + water(hz, 7, 170, GOLD_LIGHT, 470)
            + reflect(city, hz, 0.45, 3) + city)
    return svg(defs, body)
scenes["02-west-bay-skyline"] = westbay


# 3. Lusail Stadium --------------------------------------------------------------------------------------
def lusail():
    hz = 500
    cx = 640
    defs = (night_sky(mid="#0b0814", low="#2a0a18", horizon="#4a1626")
            + lg("bowl", [(0, "#ffe6a8"), (0.35, "#e3b65c"), (0.75, "#9a6a24"), (1, "#4a300e")], 1, 0)
            + lg("ground", [(0, "#140a08"), (1, "#020101")]))
    b = [sky_body(81, 120, 260), haze(cx, hz - 120, 640, 300, 0.55, "goldhaze"), haze(cx, hz, 700, 120, 0.6)]
    for a in (-34, -16, 16, 34):
        b.append(f'<path d="M{cx+a*6},{hz-248} L{cx+a*16-34},0 L{cx+a*16+34},0 Z" fill="#fff1cc" opacity=".05"/>')
    b.append(f'<path d="M{cx-400},{hz-220} Q{cx},{hz-275} {cx+400},{hz-220} Q{cx+350},{hz-30} {cx+262},{hz} '
             f'L{cx-262},{hz} Q{cx-350},{hz-30} {cx-400},{hz-220} Z" fill="url(#bowl)"/>')
    for row in range(7):
        y = hz - 200 + row * 29
        hw = 380 - row * 17
        n = 24 - row
        for k in range(n):
            x = cx - hw + (2 * hw) * (k + 0.5) / n
            b.append(f'<path d="M{x-8:.1f},{y+20} L{x:.1f},{y+4} L{x+8:.1f},{y+20} Z" fill="#3a2006" opacity=".6"/>')
            if (k + row) % 5 == 0:
                b.append(f'<path d="M{x-8:.1f},{y+20} L{x:.1f},{y+4} L{x+8:.1f},{y+20} Z" fill="{GOLD_LIGHT}" opacity=".7"/>')
    b.append(f'<path d="M{cx-400},{hz-220} Q{cx},{hz-275} {cx+400},{hz-220} Q{cx},{hz-244} {cx-400},{hz-220} Z" fill="#fff6dc" opacity=".95"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#ground)"/>')
    b.append(f'<ellipse cx="{cx}" cy="{hz+8}" rx="440" ry="18" fill="{GOLD}" opacity=".3" filter="url(#b8)"/>')
    # fireworks
    r = random.Random(8)
    for fx, fy, fr, col in ((300, 150, 60, GOLD_LIGHT), (1000, 120, 70, "#ff7a9a"), (1120, 230, 40, GOLD_LIGHT)):
        for k in range(28):
            a = 2 * math.pi * k / 28
            L = fr * r.uniform(0.7, 1.0)
            b.append(f'<line x1="{fx+math.cos(a)*L*0.25:.1f}" y1="{fy+math.sin(a)*L*0.25:.1f}" x2="{fx+math.cos(a)*L:.1f}" y2="{fy+math.sin(a)*L:.1f}" stroke="{col}" stroke-width="1.1" opacity=".55" stroke-linecap="round"/>')
            b.append(f'<circle cx="{fx+math.cos(a)*L:.1f}" cy="{fy+math.sin(a)*L:.1f}" r="1.4" fill="{col}" opacity=".9"/>')
    return svg(defs, "".join(b))
scenes["03-lusail-stadium"] = lusail


# 4. Souq Waqif -----------------------------------------------------------------------------------------
def souq():
    hz = 520
    defs = (night_sky(mid="#0c0a1c", low="#2a0c1e", horizon="#4c1a2a")
            + lg("mud", [(0, "#c9965c"), (1, "#6e4a26")])
            + lg("mud2", [(0, "#a87646"), (1, "#4e3218")])
            + rg("lamp", "#ffbe5a", 0.95, 0.3)
            + lg("floor", [(0, "#2a170c"), (1, "#030201")]))
    b = [sky_body(41, 110, 280), crescent(1090, 110, 26, 4)]
    b.append(f'<rect x="900" y="{hz-350}" width="96" height="350" fill="url(#mud2)"/>')
    b.append(f'<rect x="888" y="{hz-366}" width="120" height="18" fill="#8a6036"/>')
    for k in range(3):
        b.append(f'<rect x="{910+k*27}" y="{hz-340}" width="16" height="84" fill="#1e1208"/>')
    b.append(f'<rect x="70" y="{hz-240}" width="1140" height="240" fill="url(#mud)"/>')
    b.append(f'<path d="M70,{hz-240} ' + " ".join(f"L{70+k*28},{hz-240-(9 if k%2 else 0)}" for k in range(42)) + f' L1210,{hz-240} Z" fill="#d4a670"/>')
    for k in range(0, 1140, 36):
        b.append(f'<line x1="{70+k}" y1="{hz-205}" x2="{70+k-9}" y2="{hz-198}" stroke="#3e2612" stroke-width="5" stroke-linecap="round"/>')
    for k in range(7):
        x = 140 + k * 152
        b.append(f'<circle cx="{x+46}" cy="{hz-110}" r="120" fill="url(#lamp)" opacity=".7"/>')
        b.append(f'<path d="M{x},{hz} L{x},{hz-114} Q{x+46},{hz-178} {x+92},{hz-114} L{x+92},{hz} Z" fill="#ffc06a" opacity=".9"/>')
        b.append(f'<path d="M{x+6},{hz} L{x+6},{hz-110} Q{x+46},{hz-166} {x+86},{hz-110} L{x+86},{hz} Z" fill="#3a2010" opacity=".5"/>')
        b.append(f'<line x1="{x+46}" y1="{hz-178}" x2="{x+46}" y2="{hz-144}" stroke="#1e1208" stroke-width="2"/>')
        b.append(f'<path d="M{x+38},{hz-144} L{x+54},{hz-144} L{x+57},{hz-124} L{x+46},{hz-118} L{x+35},{hz-124} Z" fill="{GOLD_LIGHT}"/>')
        b.append(f'<circle cx="{x+46}" cy="{hz-132}" r="16" fill="{GOLD_LIGHT}" filter="url(#b5)" opacity=".8"/>')
    for k in range(10):
        b.append(f'<rect x="{122+k*112}" y="{hz-222}" width="18" height="26" fill="#1e1208"/>')
        b.append(f'<rect x="{126+k*112}" y="{hz-218}" width="10" height="18" fill="{GOLD}" opacity=".35"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#floor)"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="40" fill="{GOLD}" opacity=".08" filter="url(#b8)"/>')
    return svg(defs, "".join(b))
scenes["04-souq-waqif"] = souq


# 5. National Museum of Qatar (desert rose discs) ---------------------------------------------------------
def nmoq():
    hz = 500
    defs = (night_sky(mid="#0c0a1e", low="#30102a", horizon="#6a2440")
            + lg("disc", [(0, "#f2d9a8"), (0.5, "#c79a5c"), (1, "#5e4020")], 1, 0)
            + lg("water", [(0, "#2a1222"), (1, "#020104")]))
    r = random.Random(12)
    discs = []
    specs = []
    for _ in range(26):
        x = r.uniform(300, 980)
        y = r.uniform(hz - 250, hz - 30)
        rx = r.uniform(60, 150)
        ry = rx * r.uniform(0.14, 0.24)
        rot = r.uniform(-40, 40)
        specs.append((y, x, rx, ry, rot))
    for y, x, rx, ry, rot in sorted(specs):
        discs.append(f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.0f})">'
                     f'<ellipse rx="{rx:.0f}" ry="{ry:.0f}" fill="url(#disc)"/>'
                     f'<ellipse rx="{rx:.0f}" ry="{ry:.0f}" fill="none" stroke="{GOLD_LIGHT}" stroke-width="1.2" opacity=".7"/>'
                     f'<ellipse cy="{ry*0.35:.1f}" rx="{rx*0.92:.0f}" ry="{ry*0.5:.1f}" fill="#2a1a0c" opacity=".35"/></g>')
    museum = "".join(discs)
    body = (sky_body(13, 140, 300) + crescent(220, 120, 24, 5)
            + haze(640, hz, 640, 170, 0.7) + haze(640, hz - 130, 380, 200, 0.3, "goldhaze")
            + water(hz, 14, 150, GOLD_LIGHT, 640)
            + reflect(museum, hz, 0.4, 3) + museum
            + f'<rect x="0" y="{hz-3}" width="{W}" height="5" fill="#0a0508"/>'
            + "".join(palm(x, hz - 2, 85 + (x % 23), "#070309", 0.9, GOLD) for x in (110, 190, 1090, 1180)))
    return svg(defs, body)
scenes["05-national-museum"] = nmoq


# 6. Katara: amphitheatre and pigeon towers --------------------------------------------------------------
def katara():
    hz = 520
    defs = (night_sky(mid="#0d0b22", low="#2c0f2a", horizon="#5a1c38")
            + lg("stone", [(0, "#f5e2c2"), (0.6, "#c9a272"), (1, "#7a5a36")])
            + lg("ground", [(0, "#22121a"), (1, "#030104")])
            + lg("uplight", [(0, GOLD, 0), (1, GOLD, 0.5)]))
    b = [sky_body(91, 120, 260), full_moon(220, 130, 30)]
    for x, h in ((880, 230), (990, 285), (1100, 205)):
        b.append(f'<path d="M{x-60},{hz} L{x-20},{hz-h-40} L{x+20},{hz-h-40} L{x+60},{hz} Z" fill="url(#uplight)" opacity=".5"/>')
        b.append(f'<path d="M{x-36},{hz} L{x-17},{hz-h} Q{x},{hz-h-26} {x+17},{hz-h} L{x+36},{hz} Z" fill="url(#stone)"/>')
        for row in range(int(h / 26)):
            y = hz - 22 - row * 25
            for k in (-1, 0, 1):
                b.append(f'<circle cx="{x+k*10*(1-row*0.07):.1f}" cy="{y}" r="2.6" fill="#4a3220"/>')
            b.append(f'<line x1="{x-32+row*1.6:.1f}" y1="{y+9}" x2="{x+32-row*1.6:.1f}" y2="{y+9}" stroke="#7a5a3a" stroke-width="2"/>')
    ax = 150
    b.append(f'<rect x="{ax}" y="{hz-160}" width="580" height="160" fill="url(#stone)"/>')
    for (y0, hgt, n) in ((hz - 150, 64, 9), (hz - 76, 70, 9)):
        for k in range(n):
            x = ax + 22 + k * 62
            b.append(f'<path d="M{x},{y0+hgt} L{x},{y0+24} Q{x+20},{y0} {x+40},{y0+24} L{x+40},{y0+hgt} Z" fill="#2e1a16"/>')
            b.append(f'<path d="M{x+4},{y0+hgt} L{x+4},{y0+28} Q{x+20},{y0+8} {x+36},{y0+28} L{x+36},{y0+hgt} Z" fill="{GOLD_LIGHT}" opacity=".55"/>')
    b.append(f'<rect x="{ax-10}" y="{hz-168}" width="600" height="10" fill="#fbecd2"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#ground)"/>')
    b.append("".join(palm(x, hz + 2, 96, "#070309", 0.95, GOLD) for x in (60, 790, 1210)))
    return svg(defs, "".join(b))
scenes["06-katara"] = katara


# 7. Dhows and the Pearl Monument on the Corniche ----------------------------------------------------------
def dhows():
    hz = 490
    defs = (night_sky(mid="#0b0a20", low="#24102a", horizon="#521a36")
            + lg("water", [(0, "#24122a"), (1, "#010103")])
            + lg("sail", [(0, "#fbe9c4"), (1, "#caa36a")], 1, 0)
            + lg("shell", [(0, "#f6dca6"), (1, "#8a6230")], 1, 0)
            + f'<radialGradient id="pearl" cx=".35" cy=".35"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d9c9b0"/></radialGradient>')

    def dhow(x, y, s):
        hull = f'<path d="M{x-125*s},{y-20*s} Q{x-145*s},{y-34*s} {x-156*s},{y-52*s} L{x+136*s},{y-30*s} Q{x+115*s},{y} {x-84*s},{y} Z" fill="#1e1008"/>'
        trim = f'<path d="M{x-150*s},{y-48*s} L{x+132*s},{y-28*s}" stroke="{GOLD}" stroke-width="{1.4*s}" opacity=".8"/>'
        mast = f'<line x1="{x}" y1="{y-30*s}" x2="{x+10*s}" y2="{y-240*s}" stroke="#140a04" stroke-width="{3*s}"/>'
        yard = f'<line x1="{x-125*s}" y1="{y-62*s}" x2="{x+95*s}" y2="{y-260*s}" stroke="#140a04" stroke-width="{2.5*s}"/>'
        sail = f'<path d="M{x-122*s},{y-64*s} L{x+92*s},{y-258*s} Q{x+74*s},{y-124*s} {x+22*s},{y-46*s} Z" fill="url(#sail)" opacity=".96"/>'
        bulbs = "".join(f'<circle cx="{x-122*s+(214*s)*t:.1f}" cy="{y-64*s-(194*s)*t + 18*s*math.sin(math.pi*t):.1f}" r="{1.8*s:.1f}" fill="{GOLD_LIGHT}"/>' for t in [i / 14 for i in range(15)])
        deck = "".join(f'<circle cx="{x+k*s}" cy="{y-24*s}" r="{2.2*s}" fill="{GOLD_LIGHT}"/>' for k in range(-96, 116, 24))
        return hull + trim + sail + mast + yard + bulbs + deck
    r = random.Random(4)
    city = "".join(f'<rect x="{x}" y="{hz-r.randint(24,80)}" width="{r.randint(10,26)}" height="90" fill="#0c0814"/>' for x in range(0, W, 24))
    citylights = "".join(f'<rect x="{r.uniform(0,W):.0f}" y="{hz-r.uniform(10,70):.0f}" width="2" height="2" fill="{GOLD_LIGHT}" opacity="{r.uniform(.4,.9):.2f}"/>' for _ in range(160))
    # pearl monument on the promenade
    px, py = 1010, hz - 4
    shell = (f'<path d="M{px-70},{py-18} Q{px-80},{py-110} {px},{py-130} Q{px+80},{py-110} {px+70},{py-18} Q{px},{py-50} {px-70},{py-18} Z" fill="url(#shell)"/>'
             + "".join(f'<path d="M{px},{py-34} L{px+math.cos(math.radians(a))*74:.1f},{py-34-math.sin(math.radians(a))*92:.1f}" stroke="#7a5426" stroke-width="1.2" opacity=".6"/>' for a in range(30, 160, 16))
             + f'<path d="M{px-72},{py-14} Q{px},{py+8} {px+72},{py-14} L{px+58},{py} L{px-58},{py} Z" fill="#a8783a"/>'
             + f'<circle cx="{px}" cy="{py-30}" r="22" fill="#fff6e0" filter="url(#b8)" opacity=".7"/>'
             + f'<circle cx="{px}" cy="{py-30}" r="15" fill="url(#pearl)"/>'
             + f'<rect x="{px-90}" y="{py}" width="180" height="10" fill="#1c1208"/>')
    boats = dhow(400, hz + 12, 1.0) + dhow(760, hz - 4, 0.6)
    body = (sky_body(71, 160, 340) + crescent(1120, 100, 24, 7)
            + haze(640, hz, 760, 130, 0.65)
            + city + citylights + water(hz, 9, 170, GOLD_LIGHT, 420)
            + reflect(boats + shell, hz + 10, 0.36, 3) + shell + boats)
    return svg(defs, body)
scenes["07-corniche-dhows"] = dhows


# 8. Aspire Torch ------------------------------------------------------------------------------------------
def torch():
    hz = 510
    cx = 640
    defs = (night_sky(mid="#0b0818", low="#260a1c", horizon="#4a1424")
            + lg("ground", [(0, "#100810"), (1, "#020103")])
            + rg("flame", "#ff9a2e", 1) + rg("halo", "#ff8a2a", 0.4, 0.25)
            + lg("tower", [(0, "#5a3a18"), (0.5, "#e8c27a"), (1, "#4a2e10")], 1, 0))
    t = [f'<path d="M{cx-28},{hz} C{cx-24},{hz-190} {cx-15},{hz-320} {cx-19},{hz-384} L{cx+19},{hz-384} C{cx+15},{hz-320} {cx+24},{hz-190} {cx+28},{hz} Z" fill="url(#tower)"/>']
    for k in range(1, 16):
        y = hz - k * 24
        t.append(f'<line x1="{cx-26+k*0.5:.1f}" y1="{y}" x2="{cx+26-k*0.5:.1f}" y2="{y}" stroke="#5a3a18" stroke-width=".8" opacity=".6"/>')
    t.append(f'<ellipse cx="{cx}" cy="{hz-396}" rx="48" ry="13" fill="#7a5426"/>')
    t.append(f'<path d="M{cx-44},{hz-396} Q{cx},{hz-420} {cx+44},{hz-396}" fill="{GOLD}"/>')
    flame = (f'<circle cx="{cx}" cy="{hz-440}" r="190" fill="url(#halo)"/>'
             f'<path d="M{cx-24},{hz-404} Q{cx-34},{hz-450} {cx-4},{hz-506} Q{cx+2},{hz-460} {cx+18},{hz-480} Q{cx+34},{hz-438} {cx+24},{hz-404} Z" fill="#ff8a1e"/>'
             f'<path d="M{cx-11},{hz-406} Q{cx-13},{hz-438} {cx},{hz-472} Q{cx+13},{hz-438} {cx+11},{hz-406} Z" fill="#ffe7a0"/>'
             f'<circle cx="{cx}" cy="{hz-442}" r="44" fill="url(#flame)" filter="url(#b8)"/>')
    dome = f'<path d="M{cx-350},{hz} Q{cx-160},{hz-130} {cx+40},{hz-76} Q{cx+260},{hz-44} {cx+400},{hz} Z" fill="#1a0f18"/>'
    ribs = "".join(f'<path d="M{cx-320+k*46},{hz} Q{cx-214+k*46},{hz-96} {cx-128+k*46},{hz-64}" stroke="{GOLD}" stroke-width="1" fill="none" opacity=".35"/>' for k in range(15))
    lights = "".join(f'<circle cx="{x}" cy="{hz-3}" r="1.7" fill="{GOLD_LIGHT}" opacity=".85"/>' for x in range(30, W, 24))
    body = (sky_body(31, 130, 300) + haze(cx, hz, 640, 120, 0.6)
            + "".join(t) + flame + dome + ribs
            + f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#ground)"/>' + lights)
    return svg(defs, body)
scenes["08-aspire-torch"] = torch


# 9. Al Zubarah Fort under the full moon ----------------------------------------------------------------
def zubarah():
    hz = 510
    defs = (night_sky(mid="#0d0c22", low="#241430", horizon="#4a2236")
            + lg("fort", [(0, "#e9c08a"), (1, "#8a5e30")])
            + lg("sand", [(0, "#4a2e18"), (1, "#080403")])
            + lg("flood", [(0, GOLD, 0), (1, GOLD, 0.35)]))
    b = [sky_body(51, 170, 330), full_moon(320, 150, 40),
         dunes(5, hz + 6, 16, "#2a1a10", 1.6)]
    fx, fw, fh = 480, 400, 128
    b.append(f'<path d="M{fx-80},{hz} L{fx+40},{hz-fh-80} L{fx+fw-40},{hz-fh-80} L{fx+fw+80},{hz} Z" fill="url(#flood)" opacity=".45"/>')
    b.append(f'<rect x="{fx}" y="{hz-fh}" width="{fw}" height="{fh}" fill="url(#fort)"/>')
    for k in range(0, fw, 22):
        b.append(f'<rect x="{fx+k}" y="{hz-fh-11}" width="12" height="12" fill="#d6a46a"/>')
    for tx in (fx - 24, fx + fw - 30):
        b.append(f'<rect x="{tx}" y="{hz-fh-56}" width="54" height="{fh+56}" fill="#d8a56c" rx="20"/>')
        for k in range(0, 54, 13):
            b.append(f'<path d="M{tx+k},{hz-fh-56} l6,-13 l6,13 Z" fill="#c08a52"/>')
        for k in range(3):
            b.append(f'<rect x="{tx+23}" y="{hz-fh-34+k*42}" width="7" height="16" fill="#2e1a0a"/>')
            b.append(f'<rect x="{tx+24}" y="{hz-fh-32+k*42}" width="5" height="10" fill="{GOLD_LIGHT}" opacity=".6"/>')
    g = fx + fw / 2
    b.append(f'<path d="M{g-32},{hz} L{g-32},{hz-58} Q{g},{hz-88} {g+32},{hz-58} L{g+32},{hz} Z" fill="#2e1a0a"/>')
    b.append(f'<path d="M{g-26},{hz} L{g-26},{hz-56} Q{g},{hz-80} {g+26},{hz-56} L{g+26},{hz} Z" fill="{GOLD_LIGHT}" opacity=".5"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#sand)"/>')
    b.append(dunes(9, hz + 80, 20, "#140b06", 2.4))
    b.append(ridge(9, hz + 80, 20, 2.4, op=0.35))
    return svg(defs, "".join(b))
scenes["09-zubarah-fort"] = zubarah


# 10. Khor Al Adaid: desert night with the Milky Way --------------------------------------------------------
def inland():
    hz = 470
    defs = (night_sky(top="#03030a", mid="#0b0b22", low="#22102a", horizon="#3e1a34")
            + lg("water", [(0, "#1c1a36"), (1, "#020206")])
            + lg("d1", [(0, "#6a4424"), (1, "#22140a")]) + lg("d2", [(0, "#3e2614"), (1, "#0a0604")])
            + lg("d3", [(0, "#1c100a"), (1, "#020101")])
            + rg("fire", "#ffb04a", 0.9, 0.3)
            + f'<linearGradient id="milky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c9b8ff" stop-opacity="0"/>'
              f'<stop offset=".5" stop-color="#f2e2c8" stop-opacity=".22"/><stop offset="1" stop-color="#c9b8ff" stop-opacity="0"/></linearGradient>')
    r = random.Random(77)
    milky = [f'<path d="M-100,60 C300,120 700,260 1400,420 L1400,520 C700,360 300,220 -100,170 Z" fill="url(#milky)" filter="url(#b24)"/>']
    for _ in range(420):
        t = r.uniform(0, 1)
        x = -100 + 1500 * t
        y = 60 + 360 * t ** 1.2 + r.gauss(0, 34) + 50
        milky.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.choice([.4,.5,.7])}" fill="#fff" opacity="{r.uniform(.2,.8):.2f}"/>')
    b = [sky_body(61, 200, 400), "".join(milky), crescent(1080, 90, 18, 10),
         f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#water)"/>',
         water(hz, 15, 60, GOLD_LIGHT, 1080),
         dunes(3, hz - 6, 64, "url(#d1)", 1.4), ridge(3, hz - 6, 64, 1.4, op=0.55),
         dunes(8, hz + 130, 52, "url(#d2)", 1.8), ridge(8, hz + 130, 52, 1.8, op=0.4),
         f'<circle cx="420" cy="{hz+124}" r="90" fill="url(#fire)"/>',
         f'<path d="M412,{hz+128} Q414,{hz+108} 420,{hz+98} Q426,{hz+110} 428,{hz+128} Z" fill="#ffd27a"/>',
         dunes(13, hz + 220, 40, "url(#d3)", 2.6)]
    # a small Bedouin tent by the fire
    b.insert(-1, f'<path d="M470,{hz+132} L520,{hz+96} L590,{hz+104} L620,{hz+134} Z" fill="#0e0806"/>'
                 f'<path d="M470,{hz+132} L520,{hz+96} L590,{hz+104} L620,{hz+134}" stroke="{GOLD}" stroke-width="1" fill="none" opacity=".5"/>')
    return svg(defs, "".join(b), pat=0.04)
scenes["10-khor-al-adaid"] = inland


if __name__ == "__main__":
    for name, fn in scenes.items():
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(fn())
    print(len(scenes), "scenes")
