"""Qatar landmark scenes, drawn from code as SVG (1280x720), original illustrations.
Lower third is kept dark so the dock and tiles stay readable."""
import math, random, os, sys

W, H = 1280, 720
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def lg(i, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in
                [(st + (1,))[:3] for st in stops])
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(i, c, a=1.0):
    return (f'<radialGradient id="{i}"><stop offset="0" stop-color="{c}" stop-opacity="{a}"/>'
            f'<stop offset=".45" stop-color="{c}" stop-opacity="{a*0.3:.2f}"/>'
            f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')


BLUR = "".join(f'<filter id="b{n}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{n}"/></filter>'
               for n in (1, 2, 4, 8, 16, 30))


def stars(seed, n, ymax, op=0.8):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, ymax) ** 1.15 / ymax ** 0.15
        rad = r.choice([0.6, 0.8, 1.0, 1.3])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad}" fill="#fff" opacity="{r.uniform(.25, op):.2f}"/>')
    return "".join(out)


def crescent(cx, cy, r, color="#fff4d6"):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r*3}" fill="url(#moonglow)"/>'
            f'<mask id="cm"><rect width="{W}" height="{H}" fill="#fff"/><circle cx="{cx + r*0.45}" cy="{cy - r*0.2}" r="{r*0.9}" fill="#000"/></mask>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" mask="url(#cm)"/>')


def dunes(seed, base, amp, color, waves=2.2, step=8):
    r = random.Random(seed)
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    pts = []
    for x in range(-step, W + 2 * step, step):
        y = base - amp * (0.6 * math.sin(x / W * 6.28 * waves * 0.5 + ph[0])
                          + 0.3 * math.sin(x / W * 6.28 * waves + ph[1])
                          + 0.1 * math.sin(x / W * 6.28 * waves * 2.3 + ph[2]))
        pts.append(f"{x},{y:.1f}")
    return f'<path d="M{" L".join(pts)} L{W+2*step},{H} L{-step},{H} Z" fill="{color}"/>'


def palm(x, y, h, color="#05060c", s=1.0):
    """A date palm silhouette."""
    trunk = f'<path d="M{x},{y} Q{x+6*s},{y-h*0.5} {x+3*s},{y-h}" stroke="{color}" stroke-width="{5*s}" fill="none" stroke-linecap="round"/>'
    tx, ty = x + 3 * s, y - h
    fr = []
    for a in (-160, -130, -100, -70, -40, -15, 10, 200, 230):
        ang = math.radians(a)
        L = (34 + (a % 3) * 4) * s
        ex, ey = tx + math.cos(ang) * L, ty + math.sin(ang) * L * 0.55 + L * 0.35
        mx, my = tx + math.cos(ang) * L * 0.5, ty + math.sin(ang) * L * 0.6 - 6 * s
        fr.append(f'<path d="M{tx},{ty} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}" stroke="{color}" stroke-width="{3.2*s}" fill="none" stroke-linecap="round"/>')
    return trunk + "".join(fr)


def reflect(group_svg, horizon, op=0.35, blur=2):
    return (f'<g transform="translate(0,{2*horizon}) scale(1,-1)" opacity="{op}" filter="url(#b{blur})">{group_svg}</g>')


def water(horizon, top, bottom, seed=1, streaks=60, streak_color="#ffffff"):
    r = random.Random(seed)
    s = [f'<rect x="0" y="{horizon}" width="{W}" height="{H-horizon}" fill="url(#water)"/>']
    for _ in range(streaks):
        y = r.uniform(horizon + 4, H)
        w = r.uniform(20, 140) * (0.4 + (y - horizon) / (H - horizon))
        x = r.uniform(0, W)
        s.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="1.2" fill="{streak_color}" opacity="{r.uniform(.03,.10):.2f}"/>')
    return "".join(s)


def bottom_shade():
    return f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#shade)"/>'


def svg(defs, body):
    shade = lg("shade", [(0, "#000", 0), (0.42, "#000", 0), (0.62, "#000", 0.45), (1, "#000", 0.8)])
    moon = rg("moonglow", "#fff2c8", 0.35)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{BLUR}{shade}{moon}{defs}</defs>{body}{bottom_shade()}</svg>')


scenes = {}

# 1. Museum of Islamic Art at dusk ------------------------------------------------------------------
def mia():
    hz = 430
    defs = (lg("sky", [(0, "#0c0f2e"), (0.45, "#3b2a5c"), (0.75, "#c0607a"), (1, "#f0a36a")])
            + lg("water", [(0, "#4a3560"), (0.3, "#1c1838"), (1, "#05060f")])
            + rg("sun", "#ffc58a", 0.9)
            + lg("stone", [(0, "#efe2cf"), (1, "#b9a68e")], 1, 0))
    cx = 640
    b = []
    # stepped cubist volumes
    b.append(f'<rect x="{cx-170}" y="{hz-95}" width="340" height="95" fill="#2a2240"/>')
    b.append(f'<rect x="{cx-130}" y="{hz-175}" width="260" height="85" fill="#3a2f55"/>')
    b.append(f'<path d="M{cx-130},{hz-175} L{cx},{hz-200} L{cx+130},{hz-175} Z" fill="#43375f"/>')
    b.append(f'<rect x="{cx-75}" y="{hz-250}" width="150" height="80" fill="#4b3e69"/>')
    b.append(f'<path d="M{cx-75},{hz-250} L{cx-40},{hz-282} L{cx+40},{hz-282} L{cx+75},{hz-250} Z" fill="#54476f"/>')
    b.append(f'<rect x="{cx-30}" y="{hz-305}" width="60" height="26" fill="#5c4f78"/>')
    # the "eye" window under the dome
    b.append(f'<path d="M{cx-34},{hz-228} Q{cx},{hz-246} {cx+34},{hz-228} Q{cx},{hz-210} {cx-34},{hz-228} Z" fill="#ffcf8a" opacity=".9"/>')
    b.append(f'<path d="M{cx-34},{hz-228} Q{cx},{hz-246} {cx+34},{hz-228} Q{cx},{hz-210} {cx-34},{hz-228} Z" fill="#ffcf8a" filter="url(#b8)" opacity=".7"/>')
    # lit lower windows
    for i in range(-3, 4):
        b.append(f'<rect x="{cx+i*40-6}" y="{hz-40}" width="12" height="26" fill="#ffd9a0" opacity=".55"/>')
    # promenade & palms
    land = f'<rect x="0" y="{hz-6}" width="{W}" height="8" fill="#140f24"/>'
    palms = "".join(palm(x, hz - 4, 80 + (x % 37), "#0b0818", 0.9) for x in (110, 190, 260, 1010, 1090, 1170))
    building = "".join(b)
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
            + stars(11, 70, 230, 0.6)
            + f'<circle cx="980" cy="{hz-20}" r="220" fill="url(#sun)"/>'
            + water(hz, 0, 0, 3, 80, "#ffd0a0")
            + reflect(building + palms, hz, 0.35, 2)
            + building + land + palms)
    return svg(defs, body)
scenes["01-museum-islamic-art"] = mia

# 2. West Bay skyline at night ------------------------------------------------------------------------
def westbay():
    hz = 450
    r = random.Random(5)
    defs = (lg("sky", [(0, "#03040c"), (0.55, "#0d1430"), (0.9, "#24305e"), (1, "#3c3f6e")])
            + lg("water", [(0, "#151a3a"), (1, "#020309")])
            + lg("glass", [(0, "#3d6cc4"), (1, "#16224a")], 1, 0)
            + lg("glass2", [(0, "#1f9fb5"), (1, "#0a2a40")], 1, 0)
            + rg("cityglow", "#5d7bff", 0.5))
    b = []
    xs = 60
    while xs < W - 40:
        w = r.randint(36, 70)
        h = r.randint(90, 230)
        col = r.choice(["#121a36", "#15203f", "#0f1630", "#1a2448"])
        b.append(f'<rect x="{xs}" y="{hz-h}" width="{w}" height="{h}" fill="{col}"/>')
        for wy in range(hz - h + 8, hz - 6, 9):
            for wx in range(xs + 5, xs + w - 5, 8):
                if r.random() < 0.35:
                    b.append(f'<rect x="{wx}" y="{wy}" width="4" height="3" fill="#ffe2a8" opacity="{r.uniform(.3,.9):.2f}"/>')
        xs += w + r.randint(4, 18)
    # Doha Tower: cylinder with a domed tip and diagrid
    cx = 520
    b.append(f'<path d="M{cx-34},{hz} L{cx-34},{hz-300} Q{cx},{hz-380} {cx+34},{hz-300} L{cx+34},{hz} Z" fill="url(#glass)"/>')
    for k in range(0, 300, 18):
        b.append(f'<path d="M{cx-34},{hz-k} L{cx+34},{hz-k-18}" stroke="#9fc3ff" stroke-width=".7" opacity=".35"/>')
        b.append(f'<path d="M{cx+34},{hz-k} L{cx-34},{hz-k-18}" stroke="#9fc3ff" stroke-width=".7" opacity=".35"/>')
    b.append(f'<line x1="{cx}" y1="{hz-372}" x2="{cx}" y2="{hz-400}" stroke="#cfe0ff" stroke-width="2"/>')
    # Tornado tower: hyperboloid
    tx = 760
    pts_l = [(tx - 40 + 14 * math.sin(math.pi * k / 20), hz - k * 14) for k in range(21)]
    pts_r = [(tx + 40 - 14 * math.sin(math.pi * k / 20), hz - k * 14) for k in range(20, -1, -1)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts_l + pts_r) + " Z"
    b.append(f'<path d="{d}" fill="url(#glass2)"/>')
    for k in range(1, 20):
        y = hz - k * 14
        hw = 40 - 14 * math.sin(math.pi * k / 20)
        b.append(f'<line x1="{tx-hw:.1f}" y1="{y}" x2="{tx+hw:.1f}" y2="{y}" stroke="#7ff3ff" stroke-width=".8" opacity=".45"/>')
    # Burj style tall tower
    bx = 960
    b.append(f'<path d="M{bx-28},{hz} L{bx-22},{hz-330} L{bx},{hz-370} L{bx+22},{hz-330} L{bx+28},{hz} Z" fill="#1a2550"/>')
    b.append(f'<path d="M{bx},{hz-370} L{bx},{hz-20}" stroke="#ff8fd0" stroke-width="2" opacity=".6"/>')
    city = "".join(b)
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>' + stars(21, 120, 300, 0.7)
            + f'<ellipse cx="640" cy="{hz}" rx="700" ry="160" fill="url(#cityglow)"/>'
            + water(hz, 0, 0, 7, 120, "#9fc3ff")
            + reflect(city, hz, 0.4, 2) + city)
    return svg(defs, body)
scenes["02-west-bay-skyline"] = westbay

# 3. Aspire Torch -----------------------------------------------------------------------------------------
def torch():
    hz = 470
    defs = (lg("sky", [(0, "#02030a"), (0.6, "#101633"), (1, "#2b1f3d")])
            + lg("ground", [(0, "#0d0b18"), (1, "#020205")])
            + rg("flame", "#ff9a2e", 1) + rg("halo", "#ff6a1a", 0.35)
            + lg("tower", [(0, "#2a3256"), (0.5, "#4a5a8c"), (1, "#1b2140")], 1, 0))
    cx = 640
    t = []
    t.append(f'<path d="M{cx-26},{hz} C{cx-22},{hz-180} {cx-14},{hz-300} {cx-18},{hz-360} L{cx+18},{hz-360} C{cx+14},{hz-300} {cx+22},{hz-180} {cx+26},{hz} Z" fill="url(#tower)"/>')
    t.append(f'<ellipse cx="{cx}" cy="{hz-372}" rx="44" ry="12" fill="#3a466f"/>')
    t.append(f'<path d="M{cx-40},{hz-372} Q{cx},{hz-395} {cx+40},{hz-372}" fill="#556397"/>')
    flame = (f'<circle cx="{cx}" cy="{hz-410}" r="150" fill="url(#halo)"/>'
             f'<path d="M{cx-22},{hz-380} Q{cx-30},{hz-420} {cx-4},{hz-470} Q{cx+2},{hz-430} {cx+16},{hz-448} Q{cx+30},{hz-410} {cx+22},{hz-380} Z" fill="#ff8a1e"/>'
             f'<path d="M{cx-10},{hz-382} Q{cx-12},{hz-410} {cx},{hz-440} Q{cx+12},{hz-410} {cx+10},{hz-382} Z" fill="#ffe08a"/>'
             f'<circle cx="{cx}" cy="{hz-415}" r="40" fill="url(#flame)" filter="url(#b8)"/>')
    # stadium dome at the base
    dome = f'<path d="M{cx-330},{hz} Q{cx-150},{hz-120} {cx+40},{hz-70} Q{cx+250},{hz-40} {cx+380},{hz} Z" fill="#141a33"/>'
    ribs = "".join(f'<path d="M{cx-300+k*45},{hz} Q{cx-200+k*45},{hz-90} {cx-120+k*45},{hz-60}" stroke="#2f3b6a" stroke-width="1.2" fill="none"/>' for k in range(14))
    lights = "".join(f'<circle cx="{x}" cy="{hz-3}" r="1.6" fill="#ffd27a" opacity=".8"/>' for x in range(40, W, 22))
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>' + stars(31, 110, 330, 0.7)
            + "".join(t) + flame + dome + ribs
            + f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#ground)"/>' + lights)
    return svg(defs, body)
scenes["03-aspire-torch"] = torch

# 4. Souq Waqif at night ----------------------------------------------------------------------------
def souq():
    hz = 500
    defs = (lg("sky", [(0, "#050816"), (0.7, "#1a2246"), (1, "#3a3150")])
            + lg("mud", [(0, "#b98a58"), (1, "#7a5532")])
            + lg("mud2", [(0, "#9e7246"), (1, "#5e4026")])
            + rg("lamp", "#ffb24a", 0.9)
            + lg("floor", [(0, "#2a1d14"), (1, "#050302")]))
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(41, 90, 260, 0.6), crescent(1080, 120, 26)]
    # wind tower
    b.append(f'<rect x="900" y="{hz-330}" width="90" height="330" fill="url(#mud2)"/>')
    b.append(f'<rect x="890" y="{hz-345}" width="110" height="18" fill="#8a6440"/>')
    for k in range(3):
        b.append(f'<rect x="{908+k*26}" y="{hz-320}" width="16" height="80" fill="#2a1b10"/>')
    # main wall with protruding beams
    b.append(f'<rect x="80" y="{hz-230}" width="1120" height="230" fill="url(#mud)"/>')
    b.append(f'<path d="M80,{hz-230} ' + " ".join(f"L{80+k*28},{hz-230 - (8 if k%2 else 0)}" for k in range(41)) + f' L1200,{hz-230} Z" fill="#c49a68"/>')
    for k in range(0, 1120, 36):
        b.append(f'<line x1="{80+k}" y1="{hz-196}" x2="{80+k-8}" y2="{hz-190}" stroke="#4a3018" stroke-width="5" stroke-linecap="round"/>')
    # arches with warm light
    for k in range(7):
        x = 150 + k * 150
        b.append(f'<path d="M{x},{hz} L{x},{hz-110} Q{x+45},{hz-170} {x+90},{hz-110} L{x+90},{hz} Z" fill="#ffb565" opacity=".85"/>')
        b.append(f'<path d="M{x+6},{hz} L{x+6},{hz-108} Q{x+45},{hz-160} {x+84},{hz-108} L{x+84},{hz} Z" fill="#3a2414" opacity=".55"/>')
        b.append(f'<circle cx="{x+45}" cy="{hz-120}" r="70" fill="url(#lamp)"/>')
        b.append(f'<line x1="{x+45}" y1="{hz-170}" x2="{x+45}" y2="{hz-138}" stroke="#2a1b10" stroke-width="2"/>')
        b.append(f'<rect x="{x+38}" y="{hz-138}" width="14" height="20" rx="3" fill="#ffd27a"/>')
    # upper small windows
    for k in range(10):
        b.append(f'<rect x="{130+k*110}" y="{hz-212}" width="18" height="26" fill="#2a1b10"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#floor)"/>')
    return svg(defs, "".join(b))
scenes["04-souq-waqif"] = souq

# 5. Al Zubarah Fort at sunset ---------------------------------------------------------------------
def zubarah():
    hz = 470
    defs = (lg("sky", [(0, "#1a1335"), (0.5, "#7a3b52"), (0.8, "#e07a4c"), (1, "#ffc176")])
            + rg("sun", "#ffd38a", 1)
            + lg("fort", [(0, "#d9a873"), (1, "#8f6238")])
            + lg("sand", [(0, "#6b4426"), (1, "#120a05")]))
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<circle cx="330" cy="{hz-40}" r="260" fill="url(#sun)" opacity=".75"/>',
         f'<circle cx="330" cy="{hz-40}" r="34" fill="#fff0c8"/>',
         dunes(5, hz + 6, 14, "#3a2416", 1.6)]
    fx, fw, fh = 470, 380, 120
    b.append(f'<rect x="{fx}" y="{hz-fh}" width="{fw}" height="{fh}" fill="url(#fort)"/>')
    for k in range(0, fw, 22):
        b.append(f'<rect x="{fx+k}" y="{hz-fh-10}" width="12" height="12" fill="#c8955f"/>')
    # corner towers (round and square)
    for tx, rd in ((fx - 22, True), (fx + fw - 30, True)):
        b.append(f'<rect x="{tx}" y="{hz-fh-50}" width="52" height="{fh+50}" fill="#c99560" rx="{20 if rd else 0}"/>')
        for k in range(0, 52, 13):
            b.append(f'<path d="M{tx+k},{hz-fh-50} l6,-12 l6,12 Z" fill="#b8854f"/>')
        for k in range(3):
            b.append(f'<rect x="{tx+22}" y="{hz-fh-30+k*40}" width="7" height="16" fill="#3c2412"/>')
    b.append(f'<path d="M{fx+fw/2-30},{hz} L{fx+fw/2-30},{hz-55} Q{fx+fw/2},{hz-82} {fx+fw/2+30},{hz-55} L{fx+fw/2+30},{hz} Z" fill="#3c2412"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#sand)"/>')
    b.append(dunes(9, hz + 70, 18, "#1f1309", 2.4))
    return svg(defs, "".join(b))
scenes["05-zubarah-fort"] = zubarah

# 6. Khor Al Adaid (Inland Sea) at sunrise ----------------------------------------------------------
def inland():
    hz = 440
    defs = (lg("sky", [(0, "#13234a"), (0.5, "#5a6aa0"), (0.85, "#f2b28a"), (1, "#ffd9a8")])
            + lg("water", [(0, "#3fb6b8"), (0.4, "#16606e"), (1, "#041a20")])
            + rg("sun", "#fff0c8", 0.95)
            + lg("d1", [(0, "#e3a466"), (1, "#7a4a24")]) + lg("d2", [(0, "#b8743c"), (1, "#3d2210")])
            + lg("d3", [(0, "#5a3416"), (1, "#0d0703")]))
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<circle cx="900" cy="{hz-30}" r="240" fill="url(#sun)"/>',
         f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#water)"/>',
         dunes(3, hz - 10, 60, "url(#d1)", 1.4),
         f'<path d="M0,{hz+40} C300,{hz+10} 600,{hz+80} 1280,{hz+30} L1280,{hz+60} C700,{hz+110} 300,{hz+40} 0,{hz+70} Z" fill="#46c4c4" opacity=".55"/>',
         dunes(8, hz + 120, 50, "url(#d2)", 1.8), dunes(13, hz + 200, 40, "url(#d3)", 2.6)]
    return svg(defs, "".join(b))
scenes["06-khor-al-adaid"] = inland

# 7. Dhows on the Corniche ---------------------------------------------------------------------------
def dhows():
    hz = 450
    defs = (lg("sky", [(0, "#03050f"), (0.6, "#14204a"), (1, "#2c3d73")])
            + lg("water", [(0, "#1c2a5a"), (1, "#02040b")])
            + lg("sail", [(0, "#f2e3c4"), (1, "#bfa77f")], 1, 0))

    def dhow(x, y, s):
        hull = f'<path d="M{x-120*s},{y-20*s} Q{x-140*s},{y-34*s} {x-150*s},{y-50*s} L{x+130*s},{y-30*s} Q{x+110*s},{y} {x-80*s},{y} Z" fill="#2a1a10"/>'
        mast = f'<line x1="{x}" y1="{y-30*s}" x2="{x+10*s}" y2="{y-230*s}" stroke="#1a100a" stroke-width="{3*s}"/>'
        yard = f'<line x1="{x-120*s}" y1="{y-60*s}" x2="{x+90*s}" y2="{y-250*s}" stroke="#1a100a" stroke-width="{2.5*s}"/>'
        sail = f'<path d="M{x-118*s},{y-62*s} L{x+88*s},{y-248*s} Q{x+70*s},{y-120*s} {x+20*s},{y-44*s} Z" fill="url(#sail)" opacity=".95"/>'
        lights = "".join(f'<circle cx="{x+k*s}" cy="{y-24*s}" r="{2*s}" fill="#ffd27a"/>' for k in range(-90, 110, 30))
        return hull + sail + mast + yard + lights
    sky = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>' + stars(71, 140, 330, 0.8) + crescent(1040, 110, 30))
    r = random.Random(4)
    city = "".join(f'<rect x="{x}" y="{hz-r.randint(20,70)}" width="{r.randint(10,26)}" height="80" fill="#0b1230"/>' for x in range(0, W, 24))
    boats = dhow(420, hz + 10, 1.0) + dhow(860, hz - 6, 0.6)
    body = (sky + city + water(hz, 0, 0, 9, 110, "#c9d6ff") + reflect(boats, hz + 10, 0.3, 2) + boats)
    return svg(defs, body)
scenes["07-corniche-dhows"] = dhows

# 8. Lusail Stadium -----------------------------------------------------------------------------------
def lusail():
    hz = 470
    defs = (lg("sky", [(0, "#02030a"), (0.6, "#0f1024"), (1, "#2a1d10")])
            + lg("gold", [(0, "#ffe2a0"), (0.5, "#d9a24a"), (1, "#7a4e18")], 1, 0)
            + rg("glow", "#ffb84a", 0.55)
            + lg("ground", [(0, "#120c06"), (1, "#020101")]))
    cx = 640
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(81, 100, 260, 0.6),
         f'<ellipse cx="{cx}" cy="{hz-90}" rx="560" ry="260" fill="url(#glow)"/>']
    bowl = (f'<path d="M{cx-380},{hz-210} Q{cx},{hz-260} {cx+380},{hz-210} Q{cx+330},{hz-30} {cx+250},{hz} '
            f'L{cx-250},{hz} Q{cx-330},{hz-30} {cx-380},{hz-210} Z" fill="url(#gold)"/>')
    b.append(bowl)
    # lattice of triangular openings
    for row in range(6):
        y = hz - 190 + row * 32
        hw = 360 - row * 18
        n = 22 - row
        for k in range(n):
            x = cx - hw + (2 * hw) * (k + 0.5) / n
            b.append(f'<path d="M{x-9:.1f},{y+22} L{x:.1f},{y+4} L{x+9:.1f},{y+22} Z" fill="#3a2408" opacity=".55"/>')
    b.append(f'<path d="M{cx-380},{hz-210} Q{cx},{hz-260} {cx+380},{hz-210} Q{cx},{hz-232} {cx-380},{hz-210} Z" fill="#fff1c8" opacity=".9"/>')
    # floodlight beams
    for a in (-30, -12, 12, 30):
        b.append(f'<path d="M{cx+a*6},{hz-230} L{cx+a*14-30},0 L{cx+a*14+30},0 Z" fill="#fff3d0" opacity=".05"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#ground)"/>')
    b.append(f'<ellipse cx="{cx}" cy="{hz+8}" rx="420" ry="16" fill="#ffb84a" opacity=".25" filter="url(#b8)"/>')
    return svg(defs, "".join(b))
scenes["08-lusail-stadium"] = lusail

# 9. Katara: amphitheatre and pigeon towers -----------------------------------------------------------
def katara():
    hz = 480
    defs = (lg("sky", [(0, "#0e1636"), (0.55, "#3c3d78"), (0.85, "#d0809a"), (1, "#f2b48a")])
            + lg("stone", [(0, "#f0dcc0"), (1, "#a88a68")])
            + lg("ground", [(0, "#2b2030"), (1, "#05030a")]))
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(91, 60, 200, 0.5), crescent(200, 120, 22)]
    # pigeon towers
    for x, h in ((880, 210), (980, 260), (1080, 190)):
        b.append(f'<path d="M{x-34},{hz} L{x-16},{hz-h} Q{x},{hz-h-24} {x+16},{hz-h} L{x+34},{hz} Z" fill="url(#stone)"/>')
        for row in range(int(h / 26)):
            y = hz - 20 - row * 24
            for k in (-1, 0, 1):
                b.append(f'<circle cx="{x+k*10*(1-row*0.07):.1f}" cy="{y}" r="2.6" fill="#5a4030"/>')
            b.append(f'<line x1="{x-30+row*1.6:.1f}" y1="{y+8}" x2="{x+30-row*1.6:.1f}" y2="{y+8}" stroke="#7a5e44" stroke-width="2"/>')
    # amphitheatre arcade
    ax = 160
    b.append(f'<rect x="{ax}" y="{hz-150}" width="560" height="150" fill="url(#stone)"/>')
    for row, (y0, hgt, n) in enumerate(((hz - 140, 60, 9), (hz - 70, 66, 9))):
        for k in range(n):
            x = ax + 20 + k * 60
            b.append(f'<path d="M{x},{y0+hgt} L{x},{y0+22} Q{x+20},{y0} {x+40},{y0+22} L{x+40},{y0+hgt} Z" fill="#3b2a26"/>')
            b.append(f'<path d="M{x+4},{y0+hgt} L{x+4},{y0+26} Q{x+20},{y0+8} {x+36},{y0+26} L{x+36},{y0+hgt} Z" fill="#ffb87a" opacity=".35"/>')
    b.append(f'<rect x="{ax-10}" y="{hz-158}" width="580" height="10" fill="#f6e6cc"/>')
    b.append(f'<rect x="0" y="{hz}" width="{W}" height="{H-hz}" fill="url(#ground)"/>')
    b.append("".join(palm(x, hz + 2, 90, "#0a0712", 0.9) for x in (60, 780, 1200)))
    return svg(defs, "".join(b))
scenes["09-katara"] = katara

# 10. Dukhan coast at sunset with camels ----------------------------------------------------------------
def dukhan():
    hz = 430
    defs = (lg("sky", [(0, "#160d2c"), (0.45, "#6a2d5a"), (0.75, "#e4684a"), (1, "#ffbe6a")])
            + lg("water", [(0, "#d27a5a"), (0.25, "#6a3050"), (1, "#0b0612")])
            + rg("sun", "#ffe2a0", 1)
            + lg("beach", [(0, "#5a3020"), (1, "#0a0503")]))

    def camel(x, y, s, flip=False):
        sc = -s if flip else s
        return (f'<g transform="translate({x},{y}) scale({sc},{s})" fill="#140a08">'
                '<path d="M-40,0 L-36,-34 Q-38,-50 -26,-56 Q-14,-72 0,-58 Q10,-70 22,-56 Q30,-50 32,-40 L48,-62 Q54,-74 64,-70 '
                'L70,-66 L64,-62 L56,-58 L40,-30 L36,0 L31,0 L30,-26 L-24,-26 L-28,0 L-33,0 L-34,-26 L-36,0 Z"/></g>')
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<circle cx="640" cy="{hz}" r="300" fill="url(#sun)" opacity=".8"/>',
         f'<circle cx="640" cy="{hz-6}" r="42" fill="#fff4d6"/>',
         water(hz, 0, 0, 13, 90, "#ffd9a0"),
         f'<rect x="600" y="{hz+4}" width="80" height="140" fill="#ffd9a0" opacity=".25" filter="url(#b8)"/>',
         dunes(17, hz + 120, 26, "url(#beach)", 1.2)]
    b.append(camel(330, hz + 108, 1.15) + camel(430, hz + 112, 0.95) + camel(250, hz + 114, 0.8))
    return svg(defs, "".join(b))
scenes["10-dukhan-coast"] = dukhan

for name, fn in scenes.items():
    open(os.path.join(OUT, name + ".svg"), "w").write(fn())
print(len(scenes), "scenes")
