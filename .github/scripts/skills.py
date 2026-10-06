"""Writes the "Tech I work with" section of README.md.

Logos are the skill-icons set, served by the Iconify API (checked: every name below exists there).
Each entry: (name, icon, has dark/light versions, what I have done with it)."""
import os, re

I = 'https://api.iconify.design/skill-icons/'
GROUPS = [
    ('code', 'Languages', [
        ('PHP', 'php', True, 'Two full web apps: CampusConnect on Laravel and Gen-Z Gamers Pro in plain PHP'),
        ('JavaScript', 'javascript', False, 'Alpine.js components, React pages and a Three.js 3D scene'),
        ('Python', 'python', True, 'Selenium tests, Playwright screen recording and a Flask app'),
        ('Java', 'java', True, 'OOP coursework: a ride-sharing system, Swing GUIs, threads and exceptions'),
    ]),
    ('server', 'Back end and data', [
        ('Laravel', 'laravel', True, 'CampusConnect: 157 routes, 59 models, a Filament admin panel and live chat with Reverb'),
        ('MySQL', 'mysql', True, 'A 67-table schema built from 50 migrations, and a 42-table club platform'),
        ('SQLite', 'sqlite', False, 'Throwaway test databases for automated runs, and Flask app storage'),
        ('Flask', 'flask', True, 'Student Records: a create, read, update and delete app'),
    ]),
    ('window', 'Front end', [
        ('React', 'react', True, 'Network, clubs, events and admin pages, served through Inertia'),
        ('Alpine.js', 'alpinejs', True, 'Post composer, reactions and the floating messenger'),
        ('Tailwind CSS', 'tailwindcss', True, 'The CampusConnect design system, in light and dark themes'),
        ('Three.js', 'threejs', True, 'A 3D model of the UIU campus with a day and night cycle'),
        ('HTML', 'html', False, 'Blade templates and plain PHP views'),
        ('CSS', 'css', False, 'Glass panels, a cyber grid and motion for Gen-Z Gamers Pro'),
        ('Vite', 'vite', True, 'Asset builds, with Three.js split into its own chunk'),
        ('SVG', 'svg', True, 'The animated graphics on this page'),
    ]),
    ('shield', 'Testing and tools', [
        ('Selenium', 'selenium', False, '627 automated browser checks across four user roles, all passing'),
        ('Git', 'git', False, '223 commits of CampusConnect history'),
        ('GitHub Actions', 'githubactions', True, 'Redraws the city on this profile every day'),
        ('Cloudflare', 'cloudflare', True, 'Turnstile bot checks on Gen-Z Gamers Pro'),
        ('VS Code', 'vscode', True, 'Everyday editor'),
        ('IntelliJ IDEA', 'idea', True, 'Java coursework'),
    ]),
]


def pic(name, ic, variants):
    if variants:
        return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{I}{ic}-dark.svg">'
                f'<img src="{I}{ic}-light.svg" width="40" height="40" alt="{name}"></picture>')
    return f'<img src="{I}{ic}.svg" width="40" height="40" alt="{name}">'


def section():
    out = ['## <img src="assets/icons/stack.svg" width="26" height="26" align="top"> Tech I work with', '']
    for icn, title, items in GROUPS:
        out += [f'### <img src="assets/icons/{icn}.svg" width="22" height="22" align="top"> {title}', '', '<table>']
        for k in range(0, len(items), 2):
            row = ['  <tr>']
            for name, ic, var, what in items[k:k + 2]:
                row.append(f'    <td width="64" align="center">{pic(name, ic, var)}</td>')
                row.append(f'    <td><b>{name}</b><br><sub>{what}</sub></td>')
            out.append('\n'.join(row + ['  </tr>']))
        out += ['</table>', '']
    return '\n'.join(out)


if __name__ == '__main__':
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'README.md')
    s = open(p).read()
    a = s.index('## <img src="assets/icons/stack.svg"')
    b = s.index('## <img src="assets/icons/city.svg"')
    open(p, 'w').write(s[:a] + section() + '\n' + s[b:])
    print('skills:', sum(len(g[2]) for g in GROUPS))
