"""Builds the live graphics on the profile README from GitHub data.

    python .github/scripts/build_profile.py                  # in GitHub Actions (uses GITHUB_TOKEN)
    python .github/scripts/build_profile.py --from-json x.json  # offline, from saved data

Writes assets/generated/{skyline,stats}-{dark,light}.svg:
- skyline: the last year of contributions drawn as an isometric campus at night (or by day),
  one building per day, taller for busier days, with lit windows.
- stats: contributions this year, current and longest streak, busiest day, and top languages.
Only the Python standard library is used.
"""
import datetime as dt
import json
import math
import os
import sys
import urllib.request
from html import escape

LOGIN = os.environ.get('PROFILE_LOGIN', 'shuaib0606-bit')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'assets', 'generated')
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# CampusConnect's own colours: terracotta primary ramp, app surfaces, and the landing scene's night/day sky.
THEMES = {
    'dark': dict(bg1='#080d20', bg2='#1e2d55', text='#f4f5f7', muted='#a6aab3', empty='#1e1e23', emptyL='#161619',
                 emptyR='#101014', ground='#101014', accent='#eda183', accent2='#c15f3c', window='#ffd9a8',
                 card='#161619', stroke='#292930', levels=['#5b2a1c', '#8a3d26', '#c15f3c', '#dc7a56', '#eda183']),
    'light': dict(bg1='#8fb8e6', bg2='#fbfaf8', text='#1b1815', muted='#7a6d60', empty='#efece9', emptyL='#ded8d2',
                  emptyR='#c2b8ae', ground='#fbfaf8', accent='#dc7a56', accent2='#a84c2e', window='#fffdf8',
                  card='#ffffff', stroke='#efece9', levels=['#f5c7b3', '#eda183', '#dc7a56', '#c15f3c', '#8a3d26']),
}
# Languages are drawn in the project's palette rather than GitHub's default colours.
LANG_COLORS = {'PHP': '#c15f3c', 'JavaScript': '#eda183', 'Blade': '#8a3d26', 'Python': '#5b8fd6',
               'CSS': '#8bb254', 'Shell': '#b48aa8', 'TypeScript': '#2f6fc4', 'HTML': '#dc7a56'}
EXTRA = ['#9c8f82', '#4c7a33', '#96708c', '#f5c7b3']

QUERY = """query($login:String!){ user(login:$login){ createdAt followers{totalCount}
  repositories(ownerAffiliations:OWNER, isFork:false, first:100){ totalCount nodes{ name stargazerCount
    languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } } }
  contributionsCollection{ restrictedContributionsCount
    contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""


def fetch(token):
    req = urllib.request.Request('https://api.github.com/graphql',
                                 data=json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode(),
                                 headers={'Authorization': f'bearer {token}', 'User-Agent': 'profile-builder'})
    raw = json.load(urllib.request.urlopen(req, timeout=30))
    if raw.get('errors'):
        raise SystemExit('GitHub API error: ' + json.dumps(raw['errors'])[:400])
    u = raw['data']['user']
    days = [d for w in u['contributionsCollection']['contributionCalendar']['weeks'] for d in w['contributionDays']]
    langs = {}
    for r in u['repositories']['nodes']:
        for e in r['languages']['edges']:
            n = e['node']['name']
            langs.setdefault(n, [0, e['node']['color'] or '#888888'])[0] += e['size']
    return {
        'days': [[d['date'], d['contributionCount']] for d in days],
        'repos': u['repositories']['totalCount'],
        'stars': sum(r['stargazerCount'] for r in u['repositories']['nodes']),
        'followers': u['followers']['totalCount'],
        'languages': langs,
    }


def seed_languages():
    """Language mix of the main project, used while its repository is private (the API can't see it)."""
    p = os.path.join(HERE, 'seed_languages.json')
    return json.load(open(p)) if os.path.exists(p) else {}


# ------------------------------------------------------------------ numbers
def summarize(data):
    days = sorted(data['days'])
    counts = [c for _, c in days]
    total = sum(counts)
    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    cur = 0
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not started yet does not break the streak
        i -= 1
    while i >= 0 and counts[i] > 0:
        cur += 1
        i -= 1
    best = max(days, key=lambda d: d[1]) if days else ['', 0]
    active = sum(1 for c in counts if c > 0)
    return dict(total=total, longest=longest, current=cur, best=best, active=active)


def shade(hexcol, f):
    h = hexcol.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


def level(c, mx):
    if c <= 0:
        return -1
    q = math.log1p(c) / math.log1p(max(mx, 1))
    return min(4, int(q * 4.999))


# ------------------------------------------------------------------ skyline
def skyline(data, theme):
    t = THEMES[theme]
    days = sorted(data['days'])[-371:]
    first = dt.date.fromisoformat(days[0][0])
    pad = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cells = [None] * pad + days
    W, H = 1000, 430
    WX, WY, DX, DY = 15.4, 3.3, -8.5, 7.2  # screen step for one week, and for one day
    mx = max([c for _, c in days] + [1])
    weeks = (len(cells) + 6) // 7
    ox = (W - (weeks * WX + 7 * DX)) / 2 - 7 * DX * 0.15
    oy = 150
    parts = []
    parts.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#sky)"/>')
    if theme == 'dark':
        import random
        rnd = random.Random(7)
        for k in range(70):
            x, y, r = rnd.uniform(10, W - 10), rnd.uniform(8, 150), rnd.choice([0.6, 0.8, 1, 1.3])
            parts.append(f'<circle class="tw" style="animation-delay:{rnd.uniform(0, 4):.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff"/>')
        parts.append('<circle cx="905" cy="62" r="22" fill="#fff6d9"/><circle cx="914" cy="56" r="20" fill="url(#sky)" opacity=".9"/>')
        parts.append('<line class="shoot" x1="0" y1="0" x2="70" y2="22" stroke="url(#shoot)" stroke-width="2" stroke-linecap="round"/>')
    else:
        parts.append('<circle cx="905" cy="62" r="26" fill="#fff2d6"/><circle cx="905" cy="62" r="40" fill="#fff2d6" opacity=".35"/>')
        for cx, cy, sc in [(140, 60, 1), (330, 40, .7), (700, 70, .85)]:
            parts.append(f'<g class="cloud" opacity=".85" transform="translate({cx},{cy}) scale({sc})"><ellipse cx="0" cy="0" rx="34" ry="12" fill="#fff"/>'
                         f'<ellipse cx="18" cy="-8" rx="20" ry="13" fill="#fff"/><ellipse cx="-14" cy="-6" rx="16" ry="10" fill="#fff"/></g>')

    def P(i, j):
        return ox + i * WX + j * DX, oy + i * WY + j * DY

    def poly(pts, fill, cls=''):
        return f'<polygon{cls} points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}"/>'

    plate = [P(-0.5, -0.5), P(weeks + 0.5, -0.5), P(weeks + 0.5, 7.5), P(-0.5, 7.5)]
    parts.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in plate)}" fill="{t["ground"]}" stroke="{t["stroke"]}"/>')
    g0 = 0.12  # gap between buildings, in tiles
    order = sorted(((i, j) for i in range(weeks) for j in range(7) if i * 7 + j < len(cells) and cells[i * 7 + j]),
                   key=lambda q: (q[0] * WY + q[1] * DY, q[0]))
    for i, j in order:
        date, c = cells[i * 7 + j]
        lv = level(c, mx)
        h = 1.5 if lv < 0 else 10 + (lv + 1) * 10 + min(40, c * 2.2)
        A, B, C, D = P(i + g0, j + g0), P(i + 1 - g0, j + g0), P(i + 1 - g0, j + 1 - g0), P(i + g0, j + 1 - g0)
        up = lambda q: (q[0], q[1] - h)
        top = [up(A), up(B), up(C), up(D)]
        front = [up(D), up(C), C, D]       # faces the viewer (day edge)
        side = [up(A), up(D), D, A]        # left side
        if lv < 0:
            parts.append(poly(side, t['emptyL']) + poly(front, t['emptyR']) + poly(top, t['empty']))
            continue
        col = t['levels'][lv]
        g = [f'<g class="bld" style="animation-delay:{0.25 + (i / weeks) * 1.6:.2f}s"><title>{escape(date)}: {c} contribution{"s" if c != 1 else ""}</title>',
             poly(side, shade(col, 0.62)), poly(front, shade(col, 0.82)), poly(top, col)]
        rows = int((h - 8) // 7.5)
        for r in range(rows):
            v0 = h - 6 - r * 7.5
            for k in (0.28, 0.72):
                if ((i * 7 + j + r * 3 + int(k * 10)) % 3) == 0:
                    continue
                pts = []
                for (u, v) in ((k - 0.13, v0), (k + 0.13, v0), (k + 0.13, v0 - 3.2), (k - 0.13, v0 - 3.2)):
                    pts.append((D[0] + u * (C[0] - D[0]), D[1] + u * (C[1] - D[1]) - v))
                g.append(poly(pts, t['window'], ' class="win"' if (i + r + j) % 5 == 0 else ''))
        g.append('</g>')
        parts.append(''.join(g))
    s = summarize(data)
    first_d = dt.date.fromisoformat(days[0][0]).strftime('%b %Y')
    last_d = dt.date.fromisoformat(days[-1][0]).strftime('%b %Y')
    parts.append(f'<text x="34" y="44" font-family="{FONT}" font-size="20" font-weight="700" fill="{t["text"]}">My year in commits</text>')
    parts.append(f'<text x="34" y="68" font-family="{FONT}" font-size="13" fill="{t["muted"]}">one building per day · taller = busier · {first_d} – {last_d}</text>')
    parts.append(f'<text x="34" y="{H - 26}" font-family="{MONO}" font-size="13" fill="{t["muted"]}">{s["total"]} contributions · {s["active"]} active days · longest streak {s["longest"]} days</text>')
    # legend
    lx = W - 220
    parts.append(f'<text x="{lx - 40}" y="{H - 26}" font-family="{FONT}" font-size="12" fill="{t["muted"]}" text-anchor="end">less</text>')
    for k, col in enumerate([t['empty']] + t['levels']):
        parts.append(f'<rect x="{lx - 30 + k * 18}" y="{H - 38}" width="13" height="13" rx="3" fill="{col}"/>')
    parts.append(f'<text x="{lx - 30 + 6 * 18 + 4}" y="{H - 26}" font-family="{FONT}" font-size="12" fill="{t["muted"]}">more</text>')
    style = """
  .bld{animation:rise 1s cubic-bezier(.2,.8,.2,1) both}
  @keyframes rise{from{transform:translateY(34px)}to{transform:none}}
  .win{animation:flick 3.2s ease-in-out infinite}
  @keyframes flick{0%,100%{opacity:.95}50%{opacity:.15}}
  .tw{animation:tw 3.5s ease-in-out infinite}
  @keyframes tw{0%,100%{opacity:.9}50%{opacity:.2}}
  .shoot{animation:shoot 7s linear infinite;opacity:0}
  @keyframes shoot{0%,78%{opacity:0;transform:translate(120px,20px)}80%{opacity:1}92%{opacity:0;transform:translate(560px,160px)}100%{opacity:0}}
  .cloud{animation:drift 30s linear infinite alternate}
  @keyframes drift{from{transform:translateX(-20px)}to{transform:translateX(40px)}}
  @media (prefers-reduced-motion:reduce){*{animation:none!important}}"""
    sky = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
           '<linearGradient id="shoot" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Contributions over the last year drawn as a city">'
            f'<defs>{sky}</defs><style>{style}</style>' + ''.join(parts) + '</svg>')


# ------------------------------------------------------------------ stats card
def stats(data, theme, langs):
    t = THEMES[theme]
    s = summarize(data)
    W, H = 1000, 230
    best = s['best']
    best_txt = dt.date.fromisoformat(best[0]).strftime('%d %b %Y') if best[0] else '—'
    tiles = [(str(s['total']), 'contributions', 'last 12 months'),
             (str(s['current']), 'day streak', 'current'),
             (str(s['longest']), 'day streak', 'longest'),
             (str(best[1]), 'in one day', best_txt)]
    p = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{t["card"]}" stroke="{t["stroke"]}"/>']
    for k, (big, lab, sub) in enumerate(tiles):
        x = 30 + k * 140
        p.append(f'<g class="fade" style="animation-delay:{0.15 * k:.2f}s">'
                 f'<text x="{x}" y="92" font-family="{FONT}" font-size="44" font-weight="800" fill="url(#g{theme})">{escape(big)}</text>'
                 f'<text x="{x}" y="120" font-family="{FONT}" font-size="14" font-weight="600" fill="{t["text"]}">{escape(lab)}</text>'
                 f'<text x="{x}" y="140" font-family="{FONT}" font-size="12" fill="{t["muted"]}">{escape(sub)}</text></g>')
    p.append(f'<text x="30" y="46" font-family="{FONT}" font-size="15" font-weight="700" fill="{t["muted"]}" letter-spacing="2">IN NUMBERS</text>')
    p.append(f'<text x="30" y="196" font-family="{MONO}" font-size="12" fill="{t["muted"]}">{data["repos"]} repositor{"y" if data["repos"] == 1 else "ies"} · {data["stars"]} star{"" if data["stars"] == 1 else "s"} · {data["followers"]} follower{"" if data["followers"] == 1 else "s"} · refreshed {dt.date.today():%d %b %Y}</text>')
    # language donut
    items = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    tot = sum(v[0] for _, v in items) or 1
    cx, cy, r = 690, 128, 58
    circ = 2 * math.pi * r
    off = 0
    p.append(f'<text x="600" y="46" font-family="{FONT}" font-size="15" font-weight="700" fill="{t["muted"]}" letter-spacing="2">LANGUAGES</text>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["empty"]}" stroke-width="18"/>')
    for k, (name, (size, color)) in enumerate(items):
        color = LANG_COLORS.get(name, EXTRA[k % len(EXTRA)])
        frac = size / tot
        L = frac * circ
        p.append(f'<circle class="arc" style="animation-delay:{0.2 + 0.15 * k:.2f}s;--L:{L:.1f}" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
                 f'stroke-width="18" stroke-dasharray="{L:.1f} {circ:.1f}" stroke-dashoffset="{-off:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        off += L
        y = 64 + k * 24
        p.append(f'<g class="fade" style="animation-delay:{0.3 + 0.12 * k:.2f}s"><rect x="790" y="{y}" width="12" height="12" rx="3" fill="{color}"/>'
                 f'<text x="810" y="{y + 11}" font-family="{FONT}" font-size="13" fill="{t["text"]}">{escape(name)}</text>'
                 f'<text x="970" y="{y + 11}" font-family="{MONO}" font-size="12" fill="{t["muted"]}" text-anchor="end">{frac * 100:.1f}%</text></g>')
    style = """
  .fade{animation:fade .9s ease-out both}
  @keyframes fade{from{transform:translateY(10px)}to{transform:none}}
  .arc{animation:draw 1.2s ease-out both}
  @keyframes draw{from{stroke-dasharray:0 1000}}
  @media (prefers-reduced-motion:reduce){*{animation:none!important}}"""
    grad = f'<linearGradient id="g{theme}" x1="0" x2="1"><stop offset="0" stop-color="{t["accent2"]}"/><stop offset="1" stop-color="{t["accent"]}"/></linearGradient>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub statistics">'
            f'<defs>{grad}</defs><style>{style}</style>' + ''.join(p) + '</svg>')


def main():
    if '--from-json' in sys.argv:
        data = json.load(open(sys.argv[sys.argv.index('--from-json') + 1]))
    else:
        token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if not token:
            raise SystemExit('set GITHUB_TOKEN')
        data = fetch(token)
    # Commits made in the private CampusConnect repository (from its Git history). GitHub only counts them
    # once the repository is public or private contributions are shown, so they are used as a floor.
    sc = os.path.join(HERE, 'seed_calendar.json')
    if os.path.exists(sc):
        seed = json.load(open(sc))
        data['days'] = [[d, max(c, seed.get(d, 0))] for d, c in data['days']]
    langs = data.get('languages') or {}
    seed = seed_languages()
    for k, v in seed.items():  # the private project's mix is added on top of what the API can see
        if k in langs:
            langs[k][0] = max(langs[k][0], v[0])
        else:
            langs[k] = list(v)
    os.makedirs(OUT, exist_ok=True)
    for th in THEMES:
        open(os.path.join(OUT, f'skyline-{th}.svg'), 'w').write(skyline(data, th))
        open(os.path.join(OUT, f'stats-{th}.svg'), 'w').write(stats(data, th, langs))
    print('total', summarize(data))


if __name__ == '__main__':
    main()
