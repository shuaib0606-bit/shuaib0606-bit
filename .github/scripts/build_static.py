"""Builds the hand-made animated graphics of the profile README (run once; output is committed).

    python .github/scripts/build_static.py   -> assets/{header,project,footer}-{dark,light}.svg, assets/terminal.svg
"""
import os
import random
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, 'assets')
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
NAME = 'Sindeed Shuaib Arpon'

TH = {
    'dark': dict(s1='#060a1c', s2='#14123a', s3='#2a1550', text='#f2f3ff', muted='#9aa0d6', a1='#7c5cff', a2='#ff8a3d', a3='#2ee6c5',
                 bld='#0e1233', bld2='#151a45', win='#ffd27a', card='#0b1030', stroke='#2a3170', chip='#161c48', node='#121842'),
    'light': dict(s1='#cfe9ff', s2='#eaf4ff', s3='#fff1e3', text='#151a33', muted='#56607f', a1='#5b3fd0', a2='#f26b1d', a3='#0aa58a',
                  bld='#c9d3ea', bld2='#b7c2de', win='#fff6cf', card='#ffffff', stroke='#d9def0', chip='#f1f3fb', node='#f6f7fd'),
}
REDUCED = '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'


def svg(w, h, body, style='', defs='', label=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f'<defs>{defs}</defs><style>{style}{REDUCED}</style>{body}</svg>')


# ------------------------------------------------------------------ header
def header(theme):
    t = TH[theme]
    W, H = 1000, 330
    rnd = random.Random(11)
    defs = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["s1"]}"/>'
            f'<stop offset=".65" stop-color="{t["s2"]}"/><stop offset="1" stop-color="{t["s3"]}"/></linearGradient>'
            f'<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1000" y2="0">'
            f'<stop offset="0" stop-color="{t["a1"]}"/><stop offset=".5" stop-color="{t["a2"]}"/><stop offset="1" stop-color="{t["a1"]}"/>'
            f'<animate attributeName="x1" values="-1000;0" dur="6s" repeatCount="indefinite"/>'
            f'<animate attributeName="x2" values="0;1000" dur="6s" repeatCount="indefinite"/></linearGradient>'
            f'<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>'
            f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    b = [f'<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="url(#sky)"/>']
    # aurora / glow blobs
    op = .55 if theme == 'dark' else .35
    b.append(f'<g filter="url(#blur)" opacity="{op}"><ellipse class="blob1" cx="250" cy="90" rx="220" ry="70" fill="{t["a1"]}"/>'
             f'<ellipse class="blob2" cx="760" cy="120" rx="200" ry="60" fill="{t["a2"]}"/>'
             f'<ellipse class="blob3" cx="520" cy="40" rx="160" ry="40" fill="{t["a3"]}"/></g>')
    if theme == 'dark':
        for _ in range(90):
            x, y, r = rnd.uniform(5, W - 5), rnd.uniform(5, 190), rnd.choice([.6, .8, 1, 1.4])
            b.append(f'<circle class="tw" style="animation-delay:{rnd.uniform(0, 5):.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff"/>')
        b.append('<line class="shoot" x1="0" y1="0" x2="90" y2="26" stroke="#fff" stroke-width="2" stroke-linecap="round"/>')
    else:
        b.append(f'<circle cx="880" cy="70" r="34" fill="#ffd27a"/><circle class="halo" cx="880" cy="70" r="54" fill="#ffd27a" opacity=".22"/>')
        for cx, cy, s in [(120, 70, 1.1), (420, 46, .8), (650, 90, .9)]:
            b.append(f'<g class="cloud" transform="translate({cx},{cy}) scale({s})" opacity=".9"><ellipse rx="40" ry="13" fill="#fff"/>'
                     f'<ellipse cx="20" cy="-9" rx="24" ry="15" fill="#fff"/><ellipse cx="-16" cy="-7" rx="18" ry="11" fill="#fff"/></g>')
    # skyline silhouette with windows
    x = 0
    while x < W:
        w = rnd.randint(34, 70)
        h = rnd.randint(22, 64)
        y = H - h
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{t["bld"] if rnd.random() < .5 else t["bld2"]}"/>')
        for wy in range(y + 10, H - 8, 12):
            for wx in range(x + 6, x + w - 8, 10):
                if rnd.random() < .33:
                    cls = ' class="win"' if rnd.random() < .25 else ''
                    d = f' style="animation-delay:{rnd.uniform(0, 6):.1f}s"' if cls else ''
                    b.append(f'<rect{cls}{d} x="{wx}" y="{wy}" width="4" height="6" fill="{t["win"]}" opacity="{.85 if theme == "dark" else .9}"/>')
        x += w + rnd.randint(2, 8)
    b.append('</g>')
    # name and subtitle
    b.append(f'<text class="rise" x="60" y="128" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="4" fill="{t["muted"]}">HI, I&#8217;M</text>')
    b.append(f'<text class="rise" style="animation-delay:.15s" x="56" y="186" font-family="{FONT}" font-size="58" font-weight="800" fill="url(#name)">{NAME}</text>')
    roles = ['Full-stack developer · Laravel × React',
             'CSE @ United International University',
             'Building UIU CampusConnect',
             'Turning campus chaos into one verified home']
    cw, fs, x0, y0 = 12.0, 20, 60, 226
    period = 4.0 * len(roles)
    for k, r in enumerate(roles):
        n = len(r)
        frames, times = [], []
        start = k * 4.0
        type_t, hold_t, erase_t = 1.4, 1.8, 0.6
        frames.append(0); times.append(0.0)
        if start > 0:
            frames.append(0); times.append(start)
        for c in range(1, n + 1):
            frames.append(c * cw + 2); times.append(start + type_t * c / n)
        frames.append(n * cw + 2); times.append(start + type_t + hold_t)
        for c in range(n - 1, -1, -1):
            frames.append(c * cw + 2); times.append(start + type_t + hold_t + erase_t * (n - c) / n)
        frames.append(0); times.append(period)
        kt = ';'.join(f'{v / period:.4f}' for v in times)
        vals = ';'.join(f'{v:.0f}' for v in frames)
        b.append(f'<clipPath id="c{k}"><rect x="{x0 - 1}" y="{y0 - 22}" height="30" width="0">'
                 f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="{period}s" repeatCount="indefinite" calcMode="discrete"/></rect></clipPath>')
        b.append(f'<text clip-path="url(#c{k})" x="{x0}" y="{y0}" font-family="{MONO}" font-size="{fs}" fill="{t["text"]}" textLength="{n * cw:.0f}" lengthAdjust="spacingAndGlyphs">{escape(r)}</text>')
        # cursor follows the same frames
        cvals = ';'.join(f'{x0 + v:.0f}' for v in frames)
        b.append(f'<rect class="cur" x="{x0}" y="{y0 - 18}" width="10" height="22" fill="{t["a2"]}" opacity="0">'
                 f'<animate attributeName="x" values="{cvals}" keyTimes="{kt}" dur="{period}s" repeatCount="indefinite" calcMode="discrete"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{start / period:.4f};{(start + 4.0) / period - 0.0001:.4f};{min(1, (start + 4.0) / period):.4f}" '
                 f'dur="{period}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    # chips
    chips = ['Laravel', 'React', 'MySQL', 'Three.js', 'Selenium']
    cx = 60
    for k, c in enumerate(chips):
        w = len(c) * 8.4 + 26
        b.append(f'<g class="rise" style="animation-delay:{.4 + k * .08:.2f}s"><rect x="{cx}" y="246" width="{w:.0f}" height="28" rx="14" '
                 f'fill="{t["card"]}" fill-opacity=".85" stroke="{t["a1"]}" stroke-opacity=".7"/>'
                 f'<text x="{cx + w / 2:.0f}" y="265" font-family="{FONT}" font-size="13" font-weight="600" fill="{t["text"]}" text-anchor="middle">{c}</text></g>')
        cx += w + 10
    style = """
.tw{animation:tw 4s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.9}50%{opacity:.15}}
.win{animation:win 5s ease-in-out infinite}@keyframes win{0%,100%{opacity:.9}50%{opacity:.1}}
.shoot{opacity:0;animation:shoot 9s linear infinite}
@keyframes shoot{0%,80%{opacity:0;transform:translate(560px,10px)}82%{opacity:1}94%{opacity:0;transform:translate(900px,110px)}100%{opacity:0}}
.blob1{animation:b1 14s ease-in-out infinite alternate}@keyframes b1{to{transform:translate(120px,30px)}}
.blob2{animation:b2 16s ease-in-out infinite alternate}@keyframes b2{to{transform:translate(-140px,20px)}}
.blob3{animation:b3 12s ease-in-out infinite alternate}@keyframes b3{to{transform:translate(60px,40px)}}
.cloud{animation:drift 40s linear infinite alternate}@keyframes drift{to{transform:translateX(60px)}}
.halo{animation:halo 4s ease-in-out infinite}@keyframes halo{50%{opacity:.08}}
.rise{animation:rise 1s cubic-bezier(.2,.8,.2,1) both}@keyframes rise{from{transform:translateY(14px)}to{transform:none}}
"""
    return svg(W, H, ''.join(b), style, defs, f'{NAME} — full-stack developer')


# ------------------------------------------------------------------ terminal
def terminal():
    W, H = 1000, 352
    lines = [('$ ', 'whoami', None),
             ('', None, 'Sindeed Shuaib Arpon · CSE undergrad at United International University, Dhaka'),
             ('$ ', 'cat now.md', None),
             ('', None, 'Building UIU CampusConnect, one verified home for a whole university'),
             ('$ ', 'git log --oneline | wc -l', None),
             ('', None, '223 commits since August 2026'),
             ('$ ', 'ls stack/', None),
             ('', None, 'laravel  php  mysql  react  inertia  tailwind  alpine  three.js  python  selenium'),
             ]
    b = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="#0b0f1e" stroke="#262c4f"/>',
         '<rect x=".5" y=".5" width="999" height="40" rx="16" fill="#121831"/><rect x=".5" y="24" width="999" height="17" fill="#121831"/>',
         '<circle cx="26" cy="21" r="6.5" fill="#ff5f57"/><circle cx="48" cy="21" r="6.5" fill="#febc2e"/><circle cx="70" cy="21" r="6.5" fill="#28c840"/>',
         f'<text x="500" y="26" font-family="{FONT}" font-size="13" fill="#7d84b5" text-anchor="middle">arpon@uiu — ~/campusconnect</text>']
    cw, y, t = 9.6, 76, 0.4
    for k, (prompt, cmd, out) in enumerate(lines):
        if cmd is not None:
            n = len(cmd)
            dur = 0.05 * n + 0.2
            b.append(f'<text class="ln" style="animation-delay:{t:.2f}s" x="28" y="{y}" font-family="{MONO}" font-size="16" fill="#2ee6c5">{escape(prompt.strip())}</text>')
            b.append(f'<clipPath id="t{k}"><rect x="44" y="{y - 16}" height="22" width="0">'
                     f'<animate attributeName="width" from="0" to="{n * cw + 4:.0f}" begin="{t + .2:.2f}s" dur="{dur:.2f}s" fill="freeze" calcMode="discrete" '
                     f'values="{";".join(str(int(c * cw + 2)) for c in range(n + 1))}"/></rect></clipPath>')
            b.append(f'<text clip-path="url(#t{k})" x="46" y="{y}" font-family="{MONO}" font-size="16" fill="#e8eaff" textLength="{n * cw:.0f}" lengthAdjust="spacingAndGlyphs">{escape(cmd)}</text>')
            t += dur + .45
        else:
            col = '#ffb47a' if out.startswith('223 ') else '#a9b0e0'
            b.append(f'<text class="ln" style="animation-delay:{t:.2f}s" x="46" y="{y}" font-family="{MONO}" font-size="15" fill="{col}">{escape(out)}</text>')
            t += .35
            y += 10
        y += 26
    b.append(f'<text class="ln" style="animation-delay:{t:.2f}s" x="28" y="{y}" font-family="{MONO}" font-size="16" fill="#2ee6c5">$</text>')
    b.append(f'<rect class="blink" style="animation-delay:{t:.2f}s" x="46" y="{y - 15}" width="10" height="19" fill="#e8eaff"/>')
    style = """
.ln{opacity:0;animation:ln .25s ease-out forwards}@keyframes ln{to{opacity:1}}
.blink{opacity:0;animation:blink 1s steps(1) infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}}
"""
    return svg(W, H, ''.join(b), style, '', 'Terminal: about Sindeed Shuaib Arpon')


# ------------------------------------------------------------------ featured project
def project(theme):
    t = TH[theme]
    W, H = 1000, 520
    defs = (f'<linearGradient id="pg" x1="0" x2="1"><stop offset="0" stop-color="{t["a1"]}"/><stop offset="1" stop-color="{t["a2"]}"/></linearGradient>'
            f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{t["muted"]}"/></marker>')
    b = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{t["card"]}" stroke="{t["stroke"]}"/>',
         f'<rect x="0" y="0" width="{W}" height="5" rx="2" fill="url(#pg)"/>']
    b.append(f'<text x="40" y="52" font-family="{FONT}" font-size="13" font-weight="700" letter-spacing="3" fill="{t["a2"]}">★ FEATURED PROJECT</text>')
    b.append(f'<text x="40" y="94" font-family="{FONT}" font-size="36" font-weight="800" fill="{t["text"]}">UIU CampusConnect</text>')
    b.append(f'<text x="40" y="126" font-family="{FONT}" font-size="16" fill="{t["muted"]}">Every trimester, UIU&#8217;s open credit system scatters students into new sections with new faces.</text>')
    b.append(f'<text x="40" y="148" font-family="{FONT}" font-size="16" fill="{t["muted"]}">CampusConnect gives the whole university one verified home: classes, people, notices and campus life.</text>')
    roles = [('Student', t['a1']), ('Faculty', t['a3']), ('Registrar', t['a2']), ('Admin', '#e5484d')]
    x = 40
    for k, (r, c) in enumerate(roles):
        w = len(r) * 8.2 + 34
        b.append(f'<g class="pop" style="animation-delay:{.2 + k * .1:.1f}s"><rect x="{x}" y="166" width="{w:.0f}" height="26" rx="13" fill="{t["chip"]}" stroke="{c}"/>'
                 f'<circle cx="{x + 14}" cy="179" r="4" fill="{c}"/><text x="{x + 24}" y="184" font-family="{FONT}" font-size="13" font-weight="600" fill="{t["text"]}">{r}</text></g>')
        x += w + 10
    # architecture diagram
    def node(x, y, w, h, title, sub, col):
        return (f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t["node"]}" stroke="{col}" stroke-width="1.5"/>'
                f'<text x="{x + w / 2}" y="{y + 26}" font-family="{FONT}" font-size="15" font-weight="700" fill="{t["text"]}" text-anchor="middle">{escape(title)}</text>'
                + ''.join(f'<text x="{x + w / 2}" y="{y + 46 + i * 17}" font-family="{FONT}" font-size="12" fill="{t["muted"]}" text-anchor="middle">{escape(s)}</text>' for i, s in enumerate(sub))
                + '</g>')
    b.append(node(40, 222, 230, 110, 'Browser', ['Blade + Alpine.js', 'React 19 via Inertia', 'Three.js 3D campus'], t['a1']))
    b.append(node(370, 222, 260, 110, 'Laravel 13 · PHP 8.3', ['routes → middleware → controllers', 'SocialRules · Notifier · GroupSync', 'Filament admin panel'], t['a2']))
    b.append(node(730, 222, 230, 110, 'MySQL', ['67 tables · 50 migrations', 'public + private file storage', ''], t['a3']))
    b.append(node(370, 372, 260, 76, 'Campus assistant (AI)', ['tools scoped to the signed-in user'], '#e5484d'))
    b.append(node(40, 372, 230, 76, 'Laravel Reverb', ['websocket class chat'], t['a1']))
    b.append(node(730, 372, 230, 76, 'LLM providers', ['Groq · OpenRouter · Gemini …'], t['a3']))
    paths = [('M270,262 L370,262', t['a1'], 0), ('M370,292 L270,292', t['a2'], 1.0),
             ('M630,262 L730,262', t['a2'], .5), ('M730,292 L630,292', t['a3'], 1.5),
             ('M155,332 L155,372', t['a1'], .8), ('M500,332 L500,372', '#e5484d', .3),
             ('M630,410 L730,410', '#e5484d', 1.2)]
    for d, c, beg in paths:
        b.append(f'<path d="{d}" stroke="{t["muted"]}" stroke-opacity=".5" stroke-width="1.6" stroke-dasharray="4 4" fill="none" marker-end="url(#ah)"/>')
        b.append(f'<circle r="4.5" fill="{c}"><animateMotion dur="2s" begin="{beg}s" repeatCount="indefinite" path="{d}"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" dur="2s" begin="{beg}s" repeatCount="indefinite"/></circle>')
    # stats row
    stats = [('157', 'routes'), ('67', 'tables'), ('59', 'models'), ('33', 'controllers'), ('14', 'features'), ('627/627', 'Selenium checks')]
    x = 40
    for k, (n, lab) in enumerate(stats):
        w = 135 if k < 5 else 230
        b.append(f'<g class="pop" style="animation-delay:{.5 + k * .1:.1f}s"><text x="{x}" y="490" font-family="{FONT}" font-size="26" font-weight="800" fill="url(#pg)">{n}</text>'
                 f'<text x="{x + len(n) * 15.5 + 8}" y="489" font-family="{FONT}" font-size="13" fill="{t["muted"]}">{lab}</text></g>')
        x += w
    style = """
.pop{animation:pop .7s cubic-bezier(.2,.8,.2,1) both}@keyframes pop{from{transform:translateY(10px)}to{transform:none}}
"""
    return svg(W, H, ''.join(b), style, defs, 'UIU CampusConnect architecture')


# ------------------------------------------------------------------ footer
def footer(theme):
    t = TH[theme]
    W, H = 1000, 140
    def wave(amp, y, ph):
        pts = ' '.join(f'{x},{y + amp * (1 if (x // 125 + ph) % 2 else -1)}' for x in range(-250, 1251, 125))
        d = f'M-250,{y} ' + ' '.join(f'Q{x - 62},{y + amp * (1 if (x // 125 + ph) % 2 else -1)} {x},{y}' for x in range(-125, 1376, 125)) + f' L1375,{H} L-250,{H} Z'
        return d
    b = [f'<path class="w1" d="{wave(14, 70, 0)}" fill="{t["a1"]}" opacity=".35"/>',
         f'<path class="w2" d="{wave(12, 84, 1)}" fill="{t["a2"]}" opacity=".35"/>',
         f'<path class="w3" d="{wave(10, 98, 0)}" fill="{t["a1"]}" opacity=".55"/>',
         f'<text x="500" y="44" font-family="{FONT}" font-size="15" font-weight="600" fill="{t["muted"]}" text-anchor="middle">thanks for stopping by ✦ every graphic here is hand-made SVG</text>']
    style = """
.w1{animation:w 9s ease-in-out infinite alternate}.w2{animation:w 7s ease-in-out infinite alternate-reverse}.w3{animation:w 11s ease-in-out infinite alternate}
@keyframes w{from{transform:translateX(0)}to{transform:translateX(125px)}}
"""
    return svg(W, H, ''.join(b), style, '', 'Footer')


def main():
    os.makedirs(A, exist_ok=True)
    for th in TH:
        open(os.path.join(A, f'header-{th}.svg'), 'w').write(header(th))
        open(os.path.join(A, f'project-{th}.svg'), 'w').write(project(th))
        open(os.path.join(A, f'footer-{th}.svg'), 'w').write(footer(th))
    open(os.path.join(A, 'terminal.svg'), 'w').write(terminal())
    print('ok')


if __name__ == '__main__':
    main()
