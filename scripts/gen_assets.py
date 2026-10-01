"""Generates the animated SVG assets for the profile README.
Run:  python scripts/gen_assets.py   -> writes ./assets/*.svg
"""
import os, random
from xml.sax.saxutils import escape

random.seed(7)
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

G = "#00ff41"; G2 = "#00b32d"; DIM = "#0f3d1f"; BG = "#010409"; TXT = "#c9d1d9"; MUT = "#5f7a66"
FONT = "'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono','Courier New',monospace"
CHARS = "アイウエオカキクケコサシスセソタチツテト0123456789ABCDEF<>/{}$#"


def save(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def discrete(points, total):
    """points: list of (t, v) -> keyTimes, values strings for calcMode=discrete."""
    pts = sorted(points, key=lambda p: p[0])
    kt, vs, last = [], [], -1
    for t, v in pts:
        k = round(t / total, 5)
        if k <= last:
            k = round(last + 0.00001, 5)
        if k >= 1:
            break
        kt.append(k); vs.append(v); last = k
    return ";".join(map(str, kt)), ";".join(f"{v:.1f}" for v in vs)


def matrix_rain(w, h, step=22, opacity=0.2):
    out = [f'<g opacity="{opacity}" font-family="{FONT}" font-size="15" fill="{G}">']
    for x in range(6, w, step):
        n = random.randint(10, 22)
        dur = random.uniform(7, 16)
        delay = -random.uniform(0, dur)
        chars = "".join(random.choice(CHARS) for _ in range(n))
        tsp = "".join(
            f'<tspan x="{x}" dy="18" fill-opacity="{0.25 + 0.75 * i / n:.2f}">{escape(c)}</tspan>'
            for i, c in enumerate(chars))
        out.append(
            f'<text>{tsp}<animateTransform attributeName="transform" type="translate" '
            f'from="0 {-n*18}" to="0 {h+20}" dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/></text>')
    out.append("</g>")
    return "".join(out)


def hud_corners(x, y, w, h, s=22, color=G, op=0.7):
    p = (f"M{x},{y+s} V{y} H{x+s} M{x+w-s},{y} H{x+w} V{y+s} "
         f"M{x+w},{y+h-s} V{y+h} H{x+w-s} M{x+s},{y+h} H{x} V{y+h-s}")
    return f'<path d="{p}" fill="none" stroke="{color}" stroke-width="2" opacity="{op}"/>'


# ═══════════════════════════════ HEADER ═══════════════════════════════
def header():
    W, H = 1200, 400
    roles = ["Computer Engineering Student", "Computer Vision // YOLO // Tracking",
             "Building AI Automation Pipelines", "Teknofest Air Defense Team",
             "Mobile & Cross-Platform Developer", "Physics + Math Enthusiast"]
    x0, ty, fs = 92, 290, 26
    cw = fs * 0.6
    t, segs = 0.0, []
    for r in roles:
        n = len(r)
        typ, hold, dele, gap = 0.065, 1.8, 0.025, 0.35
        pts = [(t + k * typ, k * cw) for k in range(1, n + 1)]
        t2 = t + n * typ + hold
        pts += [(t2 + k * dele, (n - k) * cw) for k in range(1, n + 1)]
        t = t2 + n * dele + gap
        segs.append((r, pts))
    T = t

    defs, body, cursor_pts = [], [], [(0, x0)]
    for i, (r, pts) in enumerate(segs):
        kt, vs = discrete([(0, 0)] + pts, T)
        defs.append(
            f'<clipPath id="tc{i}"><rect x="{x0}" y="{ty-30}" height="40" width="0">'
            f'<animate attributeName="width" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite" '
            f'keyTimes="{kt}" values="{vs}"/></rect></clipPath>')
        body.append(
            f'<text clip-path="url(#tc{i})" x="{x0}" y="{ty}" font-size="{fs}" fill="{TXT}" '
            f'textLength="{len(r)*cw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(r)}</text>')
        cursor_pts += [(tt, x0 + v) for tt, v in pts]
    kt, vs = discrete(cursor_pts, T)
    cursor = (f'<rect class="blink" y="{ty-22}" width="13" height="27" fill="{G}" x="{x0}">'
              f'<animate attributeName="x" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite" '
              f'keyTimes="{kt}" values="{vs}"/></rect>')

    # radar
    cx, cy, R = 990, 182, 128
    radar = [f'<g transform="translate({cx},{cy})">',
             f'<circle r="{R+18}" fill="url(#rglow)"/>']
    for rr in (R, R * .72, R * .45, R * .18):
        radar.append(f'<circle r="{rr:.0f}" fill="none" stroke="{G}" stroke-opacity=".28"/>')
    radar.append(f'<circle r="{R+10}" fill="none" stroke="{G}" stroke-opacity=".5" stroke-width="2" '
                 f'stroke-dasharray="2 9"><animateTransform attributeName="transform" type="rotate" '
                 f'from="0" to="-360" dur="40s" repeatCount="indefinite"/></circle>')
    radar.append(f'<path d="M{-R},0H{R}M0,{-R}V{R}" stroke="{G}" stroke-opacity=".22"/>')
    radar.append(
        f'<g><path d="M0,0 L{R},0 A{R},{R} 0 0,0 {R*0.5:.1f},{-R*0.866:.1f} Z" fill="url(#sweep)"/>'
        f'<line x1="0" y1="0" x2="{R}" y2="0" stroke="{G}" stroke-width="2" filter="url(#glow)"/>'
        f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" '
        f'repeatCount="indefinite"/></g>')
    for ang, dist, lab in [(35, .62, "TGT-01"), (150, .8, "TGT-02"), (255, .4, "TGT-03")]:
        import math
        bx = math.cos(math.radians(ang)) * R * dist; by = math.sin(math.radians(ang)) * R * dist
        b = ang / 360 * 4
        radar.append(
            f'<g transform="translate({bx:.1f},{by:.1f})" opacity="0">'
            f'<circle r="4.5" fill="{G}" filter="url(#glow)"/>'
            f'<circle r="5" fill="none" stroke="{G}"><animate attributeName="r" values="5;18" dur="4s" '
            f'begin="{b:.2f}s" repeatCount="indefinite" keyTimes="0;1"/></circle>'
            f'<path d="M-11,-6V-11H-6M6,-11H11V-6M11,6V11H6M-6,11H-11V6" fill="none" stroke="{G}" stroke-width="1.5"/>'
            f'<text x="15" y="-12" font-size="11" fill="{G}">{lab}</text>'
            f'<animate attributeName="opacity" values="1;.75;0;0" keyTimes="0;.35;.75;1" dur="4s" '
            f'begin="{b:.2f}s" repeatCount="indefinite"/></g>')
    radar.append("</g>")
    radar.append(hud_corners(cx - R - 28, cy - R - 28, 2 * R + 56, 2 * R + 56, 18, G, .45))
    radar.append(f'<text x="{cx}" y="{cy+R+44}" text-anchor="middle" font-size="11" fill="{MUT}" '
                 f'letter-spacing="3">RADAR // SCANNING SECTOR</text>')

    ticker = ("CV_ENGINE: ACTIVE  ▸  AUTOMATION_PIPELINE: RUNNING  ▸  TEKNOFEST_HSS: TRACKING  ▸  "
              "MODEL: YOLO  ▸  GPU: RTX 4060  ▸  UPTIME: 99.9%  ▸  COFFEE: LOW  ▸  ")
    tick_w = len(ticker) * 12 * 0.6

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<style>
.blink{{animation:bl 1s steps(1) infinite}} @keyframes bl{{50%{{opacity:0}}}}
.pulse{{animation:pu 1.6s ease-in-out infinite}} @keyframes pu{{50%{{opacity:.25}}}}
.gr{{animation:gr 5s infinite}} .gc{{animation:gc 5s infinite}}
@keyframes gr{{0%,86%,100%{{opacity:0;transform:translate(0,0)}}87%{{opacity:.85;transform:translate(-5px,2px)}}89%{{opacity:.85;transform:translate(4px,-2px)}}91%{{opacity:.7;transform:translate(-2px,0)}}92%{{opacity:0}}}}
@keyframes gc{{0%,86%,100%{{opacity:0;transform:translate(0,0)}}87%{{opacity:.85;transform:translate(5px,-1px)}}89%{{opacity:.85;transform:translate(-4px,2px)}}91%{{opacity:.7;transform:translate(2px,0)}}92%{{opacity:0}}}}
.slice{{animation:sl 5s infinite;opacity:0}} @keyframes sl{{0%,86%,93%,100%{{opacity:0}}87%,90%{{opacity:1}}}}
.scan{{animation:sc 6s linear infinite}} @keyframes sc{{from{{transform:translateY(-10px)}}to{{transform:translateY({H}px)}}}}
.fadein{{animation:fi 1.2s ease-out both}} @keyframes fi{{from{{opacity:0;transform:translateY(12px)}}}}
</style>
<defs>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{G}" stroke-opacity=".07"/></pattern>
<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#b6ffc9"/><stop offset="1" stop-color="{G}"/></linearGradient>
<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity=".95"/><stop offset=".6" stop-color="{BG}" stop-opacity=".7"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0" gradientTransform="rotate(-30)"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset="1" stop-color="{G}" stop-opacity=".45"/></linearGradient>
<radialGradient id="rglow"><stop offset="0" stop-color="{G}" stop-opacity=".12"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></radialGradient>
<linearGradient id="scanl" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset="1" stop-color="{G}" stop-opacity=".18"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glow2" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
{''.join(defs)}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
{matrix_rain(W, H)}
<rect width="760" height="{H}" fill="url(#fadeL)"/>
{''.join(radar)}

<g class="fadein">
<g transform="translate(92,92)">
<rect x="0" y="-19" width="232" height="28" rx="4" fill="{G}" fill-opacity=".08" stroke="{G}" stroke-opacity=".5"/>
<circle class="pulse" cx="16" cy="-5" r="5" fill="{G}" filter="url(#glow)"/>
<text x="30" y="0" font-size="13" fill="{G}" letter-spacing="2">SYSTEM ONLINE // TR</text>
</g>
<text x="{x0-4}" y="190" font-size="78" font-weight="800" fill="#ff2e63" class="gr" letter-spacing="1">EMIRHAN SIRMA</text>
<text x="{x0-4}" y="190" font-size="78" font-weight="800" fill="#00e5ff" class="gc" letter-spacing="1">EMIRHAN SIRMA</text>
<text x="{x0-4}" y="190" font-size="78" font-weight="800" fill="url(#name)" filter="url(#glow2)" letter-spacing="1">EMIRHAN SIRMA</text>
<rect class="slice" x="{x0-10}" y="152" width="640" height="6" fill="{G}" fill-opacity=".6"/>
<rect class="slice" x="{x0+60}" y="170" width="420" height="3" fill="#00e5ff" fill-opacity=".7"/>
<text x="{x0}" y="232" font-size="20" fill="{G}" letter-spacing="7">&lt;KURAGAN /&gt;</text>
<text x="{x0+250}" y="232" font-size="14" fill="{MUT}" letter-spacing="2">// computer engineer in the making</text>
<text x="{x0-26}" y="{ty}" font-size="{fs}" fill="{G}">&gt;</text>
{''.join(body)}
{cursor}
</g>

<g>
<rect y="{H-38}" width="{W}" height="38" fill="#000" fill-opacity=".85"/>
<line x1="0" x2="{W}" y1="{H-38}" y2="{H-38}" stroke="{G}" stroke-opacity=".35"/>
<g font-size="12" fill="{G}" letter-spacing="1" opacity=".85">
<text y="{H-14}" x="0">{escape(ticker*2)}<animateTransform attributeName="transform" type="translate" from="0 0" to="{-tick_w:.1f} 0" dur="28s" repeatCount="indefinite"/></text>
</g>
</g>
<rect class="scan" width="{W}" height="60" fill="url(#scanl)"/>
{hud_corners(14, 14, W-28, H-28, 26, G, .55)}
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{G}" stroke-opacity=".25"/>
</svg>'''
    save("header.svg", svg)


# ═══════════════════════════════ SECTION TITLES ═══════════════════════════════
def section(file, num, cmd, title):
    W, H = 1200, 74
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<style>
.blink{{animation:bl 1s steps(1) infinite}} @keyframes bl{{50%{{opacity:0}}}}
.ln{{animation:ln 1.6s cubic-bezier(.2,.8,.2,1) both .3s;transform-origin:left}} @keyframes ln{{from{{transform:scaleX(0)}}}}
.dot{{animation:dt 3s linear infinite}} @keyframes dt{{from{{transform:translateX(0)}}to{{transform:translateX({W-470}px)}}}}
.in{{animation:in .8s ease-out both}} @keyframes in{{from{{opacity:0;transform:translateX(-14px)}}}}
</style>
<defs><filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{G}" stop-opacity=".8"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></linearGradient></defs>
<g class="in">
<text x="4" y="30" font-size="13" fill="{MUT}" letter-spacing="2">[{num}]  kuragan@github:~$ {escape(cmd)}</text>
<text x="4" y="62" font-size="27" font-weight="700" fill="{G}" filter="url(#g)" letter-spacing="2">{escape(title)}</text>
<rect class="blink" x="{8 + len(title)*16.9:.0f}" y="40" width="14" height="26" fill="{G}"/>
</g>
<rect class="ln" x="{40 + len(title)*16.9:.0f}" y="52" width="{W - 60 - len(title)*16.9:.0f}" height="1.5" fill="url(#l)"/>
<circle class="dot" cx="{48 + len(title)*16.9:.0f}" cy="52.7" r="3" fill="{G}" filter="url(#g)"/>
</svg>'''
    save(file, svg)


# ═══════════════════════════════ NEOFETCH / ABOUT ═══════════════════════════════
def about():
    W, H = 1200, 600
    cmd = "neofetch --kuragan"
    info = [
        ("hdr", "kuragan@github"),
        ("sep", "─" * 34),
        ("OS", "Kuragan-OS // Engineer Edition"),
        ("Name", "Emirhan Sirma"),
        ("Host", "Atatürk University"),
        ("Major", "Computer Engineering (EN)"),
        ("Location", "Turkey"),
        ("Shell", "python3 · c++ · java · kotlin"),
        ("Focus", "Computer Vision · Automation · AI"),
        ("Running", "Teknofest HSS · AutoTube · CV-Annotate"),
        ("Interests", "Theoretical Physics · Math · Psychology"),
        ("GPU", "NVIDIA RTX 4060"),
        ("Motto", "\"Automate the boring. Build the impossible.\""),
    ]
    rx, ry, lh = 470, 150, 29
    lines = []
    for i, (k, v) in enumerate(info):
        d = 1.5 + i * 0.12
        y = ry + i * lh
        if k == "hdr":
            content = f'<tspan fill="{G}" font-weight="700">kuragan</tspan><tspan fill="{TXT}">@</tspan><tspan fill="{G}" font-weight="700">github</tspan>'
        elif k == "sep":
            content = f'<tspan fill="{DIM}">{v}</tspan>'
        else:
            content = (f'<tspan fill="{G}" font-weight="700">{escape(k)}</tspan><tspan fill="{MUT}">:</tspan>'
                       f'<tspan x="{rx+130}" fill="{TXT}">{escape(v)}</tspan>')
        lines.append(f'<text class="ln" style="animation-delay:{d:.2f}s" x="{rx}" y="{y}" font-size="17">{content}</text>')
    cy = ry + len(info) * lh + 6
    pal = ["#0d1117", "#ff2e63", G, "#ffcc00", "#2f81f7", "#bc8cff", "#00e5ff", "#c9d1d9"]
    blocks = "".join(f'<rect x="{rx + i*38}" y="{cy}" width="34" height="18" fill="{c}"/>' for i, c in enumerate(pal))
    d_blocks = 1.5 + len(info) * 0.12
    n = len(cmd)
    typing = "".join(f'<tspan>{escape(ch)}</tspan>' for ch in cmd)

    cx, cyl = 235, 330
    hexpts = " ".join(f"{cx + 95*__import__('math').cos(__import__('math').radians(a)):.1f},"
                      f"{cyl + 95*__import__('math').sin(__import__('math').radians(a)):.1f}" for a in range(30, 390, 60))
    prompt_y = H - 36

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<style>
.blink{{animation:bl 1s steps(1) infinite}} @keyframes bl{{50%{{opacity:0}}}}
.ln{{opacity:0;animation:ln .35s ease-out forwards}} @keyframes ln{{from{{opacity:0;transform:translateX(-10px)}}to{{opacity:1;transform:none}}}}
.type{{animation:ty .9s steps({n}) .4s both}} @keyframes ty{{from{{width:0}}to{{width:{n*10.2:.1f}px}}}}
.c1{{animation:r1 14s linear infinite;transform-origin:{cx}px {cyl}px}} @keyframes r1{{to{{transform:rotate(360deg)}}}}
.c2{{animation:r2 9s linear infinite;transform-origin:{cx}px {cyl}px}} @keyframes r2{{to{{transform:rotate(-360deg)}}}}
.hx{{animation:hx 2.4s ease-in-out infinite}} @keyframes hx{{50%{{stroke-opacity:.35}}}}
.logo{{opacity:0;animation:ln .8s ease-out 1.2s forwards}}
.scan{{animation:sc 5s linear infinite}} @keyframes sc{{from{{transform:translateY(40px)}}to{{transform:translateY({H}px)}}}}
.cur{{opacity:0;animation:ap 0s {d_blocks+.4:.2f}s forwards, bl 1s steps(1) {d_blocks+.4:.2f}s infinite}} @keyframes ap{{to{{opacity:1}}}}
</style>
<defs>
<clipPath id="tclip"><rect class="type" x="{40+19*10.2:.1f}" y="70" height="30" width="0"/></clipPath>
<filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="lg"><stop offset="0" stop-color="{G}" stop-opacity=".18"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></radialGradient>
<linearGradient id="scanl" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset="1" stop-color="{G}" stop-opacity=".07"/></linearGradient>
<clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="44" fill="#0b1410"/>
<line x1="0" x2="{W}" y1="44" y2="44" stroke="{DIM}"/>
<circle cx="26" cy="22" r="7" fill="#ff5f56"/><circle cx="50" cy="22" r="7" fill="#ffbd2e"/><circle cx="74" cy="22" r="7" fill="#27c93f"/>
<text x="{W/2}" y="27" text-anchor="middle" font-size="13" fill="{MUT}">kuragan@github: ~ — zsh — 120×36</text>

<text x="40" y="92" font-size="17"><tspan fill="{G}" font-weight="700">kuragan@github</tspan><tspan fill="{TXT}">:</tspan><tspan fill="#2f81f7">~</tspan><tspan fill="{TXT}">$ </tspan></text>
<text x="{40+19*10.2:.1f}" y="92" font-size="17" fill="{TXT}" clip-path="url(#tclip)" textLength="{n*10.2:.1f}" lengthAdjust="spacingAndGlyphs">{escape(cmd)}</text>

<g class="logo">
<circle cx="{cx}" cy="{cyl}" r="150" fill="url(#lg)"/>
<circle class="c1" cx="{cx}" cy="{cyl}" r="140" fill="none" stroke="{G}" stroke-opacity=".55" stroke-width="2" stroke-dasharray="4 10"/>
<circle class="c2" cx="{cx}" cy="{cyl}" r="122" fill="none" stroke="{G}" stroke-opacity=".8" stroke-width="3" stroke-dasharray="120 260" stroke-linecap="round"/>
<g class="c1"><circle cx="{cx+140}" cy="{cyl}" r="5" fill="{G}" filter="url(#g)"/></g>
<polygon class="hx" points="{hexpts}" fill="{G}" fill-opacity=".06" stroke="{G}" stroke-width="2.5" filter="url(#g)"/>
<text x="{cx}" y="{cyl+34}" text-anchor="middle" font-size="96" font-weight="800" fill="{G}" filter="url(#g)">K</text>
<text x="{cx}" y="{cyl+190}" text-anchor="middle" font-size="12" fill="{MUT}" letter-spacing="4">ID // KURAGAN</text>
</g>

{''.join(lines)}
<g class="ln" style="animation-delay:{d_blocks:.2f}s">{blocks}</g>

<text x="40" y="{prompt_y}" font-size="17"><tspan fill="{G}" font-weight="700">kuragan@github</tspan><tspan fill="{TXT}">:</tspan><tspan fill="#2f81f7">~</tspan><tspan fill="{TXT}">$ </tspan></text>
<rect class="cur" x="{40+19*10.2:.1f}" y="{prompt_y-16}" width="10" height="20" fill="{G}"/>
<rect class="scan" width="{W}" height="80" fill="url(#scanl)"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{G}" stroke-opacity=".3"/>
</svg>'''
    save("about.svg", svg)


# ═══════════════════════════════ PROJECTS ═══════════════════════════════
def projects():
    cards = [
        ("01", "air_defense_system", ["Real-time target detection, tracking and", "lock-on system built for Teknofest."], ["Python", "YOLO", "OpenCV"]),
        ("02", "autotube", ["Fully automated pipeline producing YouTube", "Shorts & long-form videos end-to-end."], ["Python", "LLM APIs", "FFmpeg"]),
        ("03", "cv_annotation_tool", ["Free & unlimited bbox / polygon labeling", "with built-in data augmentation."], ["Python", "OpenCV"]),
        ("04", "study_planner", ["Cross-platform planner for schedules, topics", "and resources — with an AI assistant."], ["Flutter", "Gemini API"]),
        ("05", "lecture_to_pdf", ["Records Turkish lectures and turns them", "into clean, readable PDF documents."], ["Mobile", "Speech-to-Text"]),
        ("06", "next_project.exe", ["Something new is compiling...", "stay tuned."], []),
    ]
    W, cw, ch, gap = 1200, 585, 210, 30
    H = 3 * ch + 2 * 22
    parts = []
    for i, (num, name, desc, tags) in enumerate(cards):
        x = (i % 2) * (cw + gap); y = (i // 2) * (ch + 22)
        d = i * 0.15
        last = num == "06"
        g = [f'<g class="card" style="animation-delay:{d:.2f}s" transform="translate({x},{y})">',
             f'<rect width="{cw}" height="{ch}" rx="12" fill="{BG}" stroke="{G}" stroke-opacity="{.18 if not last else .12}" '
             f'{"stroke-dasharray=\"6 6\"" if last else ""}/>',
             f'<rect width="4" height="{ch-40}" y="20" rx="2" fill="{G}" opacity="{.9 if not last else .3}"/>',
             # shimmer along top border
             f'<svg width="{cw-12}" x="6" height="3"><rect y="0" width="140" height="2" fill="url(#shim)"><animate attributeName="x" from="-140" to="{cw}" '
             f'dur="3.5s" begin="{d+i*0.4:.2f}s" repeatCount="indefinite"/></rect></svg>',
             f'<text x="30" y="40" font-size="13" fill="{MUT}" letter-spacing="2">[{num}]  ~/projects/</text>',
             f'<text x="30" y="74" font-size="24" font-weight="700" fill="{G if not last else MUT}" filter="url(#g)">{escape(name)}</text>']
        if not last:
            g.append(f'<g transform="translate({cw-142},22)"><rect width="118" height="26" rx="13" fill="{G}" fill-opacity=".08" '
                     f'stroke="{G}" stroke-opacity=".55"/><circle class="pulse" cx="17" cy="13" r="4.5" fill="{G}" filter="url(#g)"/>'
                     f'<text x="31" y="18" font-size="12" font-weight="700" fill="{G}" letter-spacing="1.5">BUILDING</text></g>')
        else:
            g.append(f'<g transform="translate({cw-60},40)"><circle r="13" fill="none" stroke="{DIM}" stroke-width="3"/>'
                     f'<circle r="13" fill="none" stroke="{G}" stroke-width="3" stroke-dasharray="20 62" stroke-linecap="round">'
                     f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="1s" repeatCount="indefinite"/></circle></g>')
        for j, line in enumerate(desc):
            g.append(f'<text x="30" y="{108 + j*24}" font-size="15.5" fill="{TXT if not last else MUT}" opacity=".9">{escape(line)}</text>')
        tx = 30
        for t in tags:
            w = len(t) * 7.8 + 22
            g.append(f'<rect x="{tx}" y="{ch-62}" width="{w:.0f}" height="24" rx="5" fill="{G}" fill-opacity=".06" stroke="{G}" stroke-opacity=".3"/>'
                     f'<text x="{tx + w/2:.1f}" y="{ch-45}" text-anchor="middle" font-size="13" fill="{G2}">{escape(t)}</text>')
            tx += w + 8
        # indeterminate progress bar
        bw = cw - 60
        g.append(f'<rect x="30" y="{ch-24}" width="{bw}" height="3" rx="1.5" fill="{DIM}"/>'
                 f'<svg x="30" y="{ch-26}" width="{bw}" height="7"><rect y="2" width="140" height="3" rx="1.5" fill="url(#bar)" filter="url(#g)">'
                 f'<animate attributeName="x" values="-140;{bw}" dur="{2.2 + (i%3)*0.4:.1f}s" begin="{d:.2f}s" repeatCount="indefinite"/></rect></svg>')
        g.append("</g>")
        parts.append("".join(g))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<style>
.card{{opacity:0;animation:ci .7s cubic-bezier(.2,.8,.2,1) forwards}} @keyframes ci{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1}}}}
.pulse{{animation:pu 1.4s ease-in-out infinite}} @keyframes pu{{50%{{opacity:.2}}}}
</style>
<defs>
<filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="shim" x1="0" x2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></linearGradient>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset="1" stop-color="{G}"/></linearGradient>
</defs>
{''.join(parts)}
</svg>'''
    save("projects.svg", svg)


# ═══════════════════════════════ FOOTER ═══════════════════════════════
def footer():
    W, H = 1200, 170
    # EKG path
    pts, x = [], 0
    path = f"M0,70"
    while x < W:
        path += f" H{x+70} L{x+82},58 L{x+94},70 L{x+104},70 L{x+114},22 L{x+126},112 L{x+138},70 L{x+150},70 L{x+166},62 L{x+182},70"
        x += 240
    msg = "> SESSION TERMINATED // THANKS FOR VISITING"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<style>
.ekg{{stroke-dasharray:2600;animation:ek 4s linear infinite}} @keyframes ek{{from{{stroke-dashoffset:2600}}to{{stroke-dashoffset:0}}}}
.blink{{animation:bl 1s steps(1) infinite}} @keyframes bl{{50%{{opacity:0}}}}
</style>
<defs>
<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".15" stop-color="{G}"/><stop offset=".85" stop-color="{G}"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></linearGradient>
<filter id="g" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<path d="{path}" fill="none" stroke="{G}" stroke-opacity=".12" stroke-width="2"/>
<path class="ekg" d="{path}" fill="none" stroke="url(#f)" stroke-width="2.5" filter="url(#g)"/>
<text x="{W/2}" y="148" text-anchor="middle" font-size="17" fill="{G}" letter-spacing="3">{escape(msg)}</text>
<rect class="blink" x="{W/2 + len(msg)*6.1 + 6:.0f}" y="133" width="10" height="19" fill="{G}"/>
</svg>'''
    save("footer.svg", svg)


header(); about(); projects(); footer()
section("sec-whoami.svg", "01", "neofetch", "WHOAMI")
section("sec-projects.svg", "02", "ls ./projects", "PROJECTS")
section("sec-stack.svg", "03", "cat arsenal.txt", "TECH_ARSENAL")
section("sec-activity.svg", "04", "git log --graph", "ACTIVITY")
section("sec-connect.svg", "05", "./connect.sh", "CONNECT")
print("ok:", sorted(os.listdir(OUT)))
