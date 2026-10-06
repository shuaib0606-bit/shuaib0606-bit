"""Writes the "Tech I work with" section of README.md and its skill cards.

Each skill is one small card (assets/skills/<icon>-{dark,light}.svg). The cards sit side by side in
a centred paragraph, so they flow like words: two per row on a computer, one per row on a phone,
and every card is the same size.

Logos: the skill-icons set (github.com/tandpfun/skill-icons, MIT licence), taken from the Iconify
API and stored in skill_icons.json (coordinates rounded to 0.1). Icons with a separate light
version are stored as "<name>-light"; for the others the light version only swaps the tile colour.

    python .github/scripts/skills.py
"""
import json, os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'assets', 'skills')
ICONS = json.load(open(os.path.join(HERE, 'skill_icons.json')))
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"

GROUPS = [
    ('code', 'Languages', [
        ('PHP', 'php', 'Two full web apps: CampusConnect on Laravel and Gen-Z Gamers Pro in plain PHP'),
        ('JavaScript', 'javascript', 'Alpine.js components, React pages and a Three.js 3D scene'),
        ('Python', 'python', 'Selenium tests, Playwright screen recording and a Flask app'),
        ('Java', 'java', 'OOP coursework: a ride-sharing system, Swing GUIs, threads and exceptions'),
    ]),
    ('server', 'Back end and data', [
        ('Laravel', 'laravel', 'CampusConnect: 157 routes, 59 models, a Filament admin panel, Reverb chat'),
        ('MySQL', 'mysql', 'A 67-table schema built from 50 migrations, and a 42-table club platform'),
        ('SQLite', 'sqlite', 'Throwaway test databases for automated runs, and Flask app storage'),
        ('Flask', 'flask', 'Student Records: a create, read, update and delete app'),
    ]),
    ('window', 'Front end', [
        ('React', 'react', 'Network, clubs, events and admin pages, served through Inertia'),
        ('Alpine.js', 'alpinejs', 'Post composer, reactions and the floating messenger'),
        ('Tailwind CSS', 'tailwindcss', 'The CampusConnect design system, in light and dark themes'),
        ('Three.js', 'threejs', 'A 3D model of the UIU campus with a day and night cycle'),
        ('HTML', 'html', 'Blade templates and plain PHP views'),
        ('CSS', 'css', 'Glass panels, a cyber grid and motion for Gen-Z Gamers Pro'),
        ('Vite', 'vite', 'Asset builds, with Three.js split into its own chunk'),
        ('SVG', 'svg', 'The animated graphics on this page'),
    ]),
    ('shield', 'Testing and tools', [
        ('Selenium', 'selenium', '627 automated browser checks across four user roles, all passing'),
        ('Git', 'git', '224 commits of CampusConnect history, published on GitHub'),
        ('GitHub Actions', 'githubactions', 'Redraws the city on this profile every day'),
        ('Cloudflare', 'cloudflare', 'Turnstile bot checks on Gen-Z Gamers Pro'),
        ('VS Code', 'vscode', 'Everyday editor'),
        ('IntelliJ IDEA', 'idea', 'Java coursework'),
    ]),
]

# Card colours: CampusConnect's surfaces, ink and terracotta (same values as build_static.py).
C = {
    'dark': dict(card='#161619', edge='#292930', text='#f4f5f7', muted='#a6aab3', accent='#dc7a56', tile='#242938'),
    'light': dict(card='#ffffff', edge='#e6e1db', text='#1b1815', muted='#6b5f53', accent='#c15f3c', tile='#f4f2ed'),
}
W, H, M = 414, 96, 4          # image size and transparent margin (the gap between cards)
NAME_PX, DESC_PX = 18, 14
TEXT_X, TEXT_W = 90, 300      # description lines are wrapped to fit TEXT_W at Arial widths


def _metric():
    """Arial-compatible advance widths (Liberation Sans), to wrap lines without a browser."""
    from fontTools.ttLib import TTFont
    f = TTFont('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
    cmap, hmtx, upm = f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm
    return lambda s, px: sum(hmtx[cmap.get(ord(c), '.notdef')][0] for c in s) * px / upm


def wrap(text, px, width, measure):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if measure(t, px) * 1.06 <= width:   # 6% spare for wider system fonts
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def icon(ic, theme):
    if theme == 'light' and ic + '-light' in ICONS:
        return ICONS[ic + '-light']
    body = ICONS[ic]
    return body.replace('fill="#242938" rx="60"', f'fill="{C["light"]["tile"]}" rx="60"') if theme == 'light' else body


def card(name, ic, what, theme, measure):
    c = C[theme]
    lines = wrap(what, DESC_PX, TEXT_W, measure)
    assert len(lines) <= 2, (name, lines)
    y0 = 42 if len(lines) == 2 else 51           # centre the text block in the card
    t = [f'<text x="{TEXT_X}" y="{y0}" font-family="{FONT}" font-size="{NAME_PX}" font-weight="700" fill="{c["text"]}">{escape(name)}</text>']
    for k, ln in enumerate(lines):
        t.append(f'<text x="{TEXT_X}" y="{y0 + 22 + k * 19}" font-family="{FONT}" font-size="{DESC_PX}" fill="{c["muted"]}">{escape(ln)}</text>')
    s = 48 / 256
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(name)}: {escape(what)}">'
            f'<rect x="{M + .5}" y="{M + .5}" width="{W - 2 * M - 1}" height="{H - 2 * M - 1}" rx="14" fill="{c["card"]}" stroke="{c["edge"]}"/>'
            f'<rect x="{M + .5}" y="{M + 20}" width="3" height="{H - 2 * M - 40}" rx="1.5" fill="{c["accent"]}"/>'
            f'<g transform="translate(24 {H / 2 - 24}) scale({s})">{icon(ic, theme)}</g>'
            + ''.join(t) + '</svg>')


def card_mobile(name, ic, what, theme, measure):
    """Phone version: the same card, with the description under the logo and larger type, so it is
    readable when the card is shrunk to the width of a phone."""
    c = C[theme]
    lines = wrap(what, 18, W - 48, measure)
    h = 88 + 24 * len(lines) + 12
    t = [f'<text x="86" y="56" font-family="{FONT}" font-size="23" font-weight="700" fill="{c["text"]}">{escape(name)}</text>']
    for k, ln in enumerate(lines):
        t.append(f'<text x="26" y="{102 + k * 24}" font-family="{FONT}" font-size="18" fill="{c["muted"]}">{escape(ln)}</text>')
    s = 46 / 256
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(name)}: {escape(what)}">'
            f'<rect x="{M + .5}" y="{M + .5}" width="{W - 2 * M - 1}" height="{h - 2 * M - 1}" rx="16" fill="{c["card"]}" stroke="{c["edge"]}"/>'
            f'<rect x="{M + .5}" y="24" width="4" height="{h - 48}" rx="2" fill="{c["accent"]}"/>'
            f'<g transform="translate(26 20) scale({s:.4f})">{icon(ic, theme)}</g>'
            + ''.join(t) + '</svg>')


def build():
    os.makedirs(OUT, exist_ok=True)
    measure = _metric()
    for _, _, items in GROUPS:
        for name, ic, what in items:
            for theme in ('dark', 'light'):
                with open(os.path.join(OUT, f'{ic}-{theme}.svg'), 'w') as f:
                    f.write(card(name, ic, what, theme, measure))
                with open(os.path.join(OUT, f'{ic}-mobile-{theme}.svg'), 'w') as f:
                    f.write(card_mobile(name, ic, what, theme, measure))


PHONE = '(max-width: 700px)'   # below this window width the phone versions are shown


def sources(base):
    """<source> tags for the phone and dark versions of an image; the <img> after them is the light one."""
    return (f'<source media="{PHONE} and (prefers-color-scheme: dark)" srcset="{base}-mobile-dark.svg">'
            f'<source media="{PHONE}" srcset="{base}-mobile-light.svg">'
            f'<source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg">')


def section():
    out = ['## <img src="assets/icons/stack.svg" width="26" height="26" align="top"> Tech I work with', '']
    for icn, title, items in GROUPS:
        out += [f'### <img src="assets/icons/{icn}.svg" width="22" height="22" align="top"> {title}', '']
        cards = ''.join(
            f'<picture>{sources(f"assets/skills/{ic}")}'
            f'<img src="assets/skills/{ic}-light.svg" width="{W}" alt="{escape(name)}: {escape(what)}"></picture>'
            for name, ic, what in items)
        out += ['<p align="center">' + cards + '</p>', '']
    return '\n'.join(out)


if __name__ == '__main__':
    build()
    p = os.path.join(ROOT, 'README.md')
    s = open(p).read()
    a = s.index('## <img src="assets/icons/stack.svg"')
    b = s.index('## <img src="assets/icons/city.svg"')
    open(p, 'w').write(s[:a] + section() + '\n' + s[b:])
    print('skills:', sum(len(g[2]) for g in GROUPS))
