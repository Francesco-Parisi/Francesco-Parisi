#!/usr/bin/env python3
"""Genera assets/languages.svg: analizzatore di spettro animato dei linguaggi usati nei repository pubblici.

Uso:
  python scripts/lang_spectrum.py                 # dati reali dall'API GitHub (GH_USER, GITHUB_TOKEN opzionale)
  python scripts/lang_spectrum.py --sample        # anteprima con dati di esempio
Variabili: GH_USER (default Francesco-Parisi), EXCLUDE (linguaggi da escludere, separati da virgola),
           TOP (numero di barre, default 8), OUT (default assets/languages.svg).
"""
import json, os, sys, datetime, urllib.request
from html import escape

USER = os.environ.get('GH_USER', 'Francesco-Parisi')
EXCLUDE = {s.strip().lower() for s in os.environ.get('EXCLUDE', '').split(',') if s.strip()}
TOP = int(os.environ.get('TOP', '8'))
OUT = os.environ.get('OUT', 'assets/languages.svg')

BG = '#05070a'; SURF = '#0b1017'; LINE = '#17222e'; LINE2 = '#213040'
TXT = '#e6edf3'; TXT2 = '#b6c2cf'; MUT = '#8796a8'; CY = '#4cc2ff'; AMB = '#ffb454'; GRN = '#4cd18a'
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def api(path):
    req = urllib.request.Request(f'https://api.github.com{path}', headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'lang-spectrum'})
    tok = os.environ.get('GITHUB_TOKEN')
    if tok:
        req.add_header('Authorization', f'Bearer {tok}')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    totals, page = {}, 1
    while True:
        repos = api(f'/users/{USER}/repos?per_page=100&type=owner&page={page}')
        if not repos:
            break
        for r in repos:
            if r.get('fork'):
                continue
            for lang, b in api(f"/repos/{USER}/{r['name']}/languages").items():
                if lang.lower() not in EXCLUDE:
                    totals[lang] = totals.get(lang, 0) + b
        page += 1
    return totals


SAMPLE = {'Python': 38, 'C': 17, 'C#': 13, 'JavaScript': 11, 'Java': 8, 'HTML': 6, 'CSS': 4, 'Shell': 3}


def build(totals, sample=False):
    tot = sum(totals.values()) or 1
    langs = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP]
    shares = [(n, v * 100 / tot) for n, v in langs]
    n = len(shares)

    W, H = 1000, 400
    px0, px1, ptop, pbot = 86, 964, 96, 288          # area del grafico
    ROWS, BH, GAP = 16, 9, 3                          # blocchi LED per colonna
    axis_max = max(10, -(-int(shares[0][1] + 0.999) // 10) * 10) if shares else 10
    slot = (px1 - px0) / max(n, 1)
    bw = min(66, slot * 0.58)
    date = datetime.date.today().isoformat()

    o = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Most used languages</title>
<desc id="d">Animated spectrum of the languages used in public repositories: ''' + ', '.join(f'{escape(l)} {p:.1f}%' for l, p in shares) + f'''.</desc>
<style>
  .on {{ animation: lit .35s ease var(--t) backwards; }}
  .tip {{ animation: lit .35s ease var(--t) backwards, flick var(--f) ease-in-out calc(var(--t) + .4s) infinite; }}
  .peak {{ animation: drop .5s cubic-bezier(.2,.8,.3,1) var(--t) backwards, hover var(--f) ease-in-out calc(var(--t) + .5s) infinite; }}
  .fade {{ animation: lit .5s ease var(--t) backwards; }}
  .sweep {{ animation: sweep 5.5s linear 2.4s infinite; }}
  .seg {{ animation: grow .9s cubic-bezier(.5,0,.2,1) var(--t) backwards; transform-box: fill-box; transform-origin: left; }}
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes lit {{ from {{ opacity: .08; }} }}
  @keyframes flick {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
  @keyframes drop {{ from {{ opacity: 0; transform: translateY(-30px); }} }}
  @keyframes hover {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
  @keyframes sweep {{ from {{ transform: translateX(0); }} 70%,100% {{ transform: translateX({px1 - px0 + 40}px); }} }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<defs>
  <linearGradient id="led" x1="0" y1="{pbot}" x2="0" y2="{ptop}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{GRN}"/><stop offset=".55" stop-color="{CY}"/><stop offset="1" stop-color="#9fe0ff"/>
  </linearGradient>
  <linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset="1" stop-color="{CY}" stop-opacity=".22"/></linearGradient>
  <clipPath id="plot"><rect x="{px0}" y="{ptop - 14}" width="{px1 - px0}" height="{pbot - ptop + 14}"/></clipPath>
</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{SURF}" stroke="{LINE2}"/>
<path d="M1 44H{W - 1}" stroke="{LINE}"/>
<circle cx="26" cy="22" r="6" fill="#ff5f57"/><circle cx="46" cy="22" r="6" fill="#febc2e"/><circle cx="66" cy="22" r="6" fill="#28c840"/>
<text x="{W / 2}" y="27" font-family="{MONO}" font-size="12" fill="{MUT}" text-anchor="middle">fp@osint: ~/repos — lang --spectrum</text>
<g font-family="{MONO}">
<text x="28" y="72" font-size="14"><tspan fill="{CY}">fp</tspan><tspan fill="{MUT}">@</tspan><tspan fill="{CY}">osint</tspan><tspan fill="{MUT}"> ~/repos </tspan><tspan fill="{TXT2}">$ </tspan><tspan fill="{TXT}">lang --spectrum --top {n}</tspan></text>
<rect class="cur" x="{28 + (len('fp@osint ~/repos $ lang --spectrum --top ') + len(str(n))) * 8.4 + 4:.1f}" y="59" width="8" height="16" fill="{CY}"/>''']

    # griglia e asse
    for k in range(0, 5):
        v = axis_max * k / 4
        y = pbot - (pbot - ptop) * k / 4
        o.append(f'<path d="M{px0} {y:.1f}H{px1}" stroke="{LINE}" stroke-dasharray="{"" if k == 0 else "2 6"}"/>'
                 f'<text x="{px0 - 12}" y="{y + 4:.1f}" font-size="11" fill="{MUT}" text-anchor="end">{v:.0f}%</text>')

    # colonne LED
    for i, (lang, pct) in enumerate(shares):
        cx = px0 + slot * (i + .5)
        x = cx - bw / 2
        lit = max(1, round(pct / axis_max * ROWS))
        f = 1.6 + (i * 0.37) % 1.3
        g = [f'<g style="--f:{f:.2f}s">']
        for r in range(ROWS):
            y = pbot - (r + 1) * (BH + GAP) + GAP
            if r < lit:
                t = 0.5 + i * 0.09 + r * 0.045
                cls = 'tip' if r >= lit - 2 and lit > 2 else 'on'
                g.append(f'<rect class="{cls}" style="--t:{t:.2f}s" x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{BH}" rx="2" fill="url(#led)"/>')
            else:
                g.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{BH}" rx="2" fill="{CY}" fill-opacity=".06"/>')
        top = pbot - lit * (BH + GAP) + GAP
        tp = 0.5 + i * 0.09 + lit * 0.045
        g.append(f'<g class="peak" style="--t:{tp:.2f}s"><rect x="{x:.1f}" y="{top - 9}" width="{bw:.1f}" height="3" rx="1.5" fill="{AMB}"/>'
                 f'<text x="{cx:.1f}" y="{top - 16}" font-size="12" fill="{TXT}" text-anchor="middle">{pct:.1f}%</text></g>')
        g.append(f'<text class="fade" style="--t:{0.3 + i * 0.09:.2f}s" x="{cx:.1f}" y="{pbot + 22}" font-size="12.5" fill="{TXT2}" text-anchor="middle">{escape(lang.lower())}</text>')
        g.append('</g>')
        o += g

    # linea di scansione
    o.append(f'<g clip-path="url(#plot)"><g class="sweep"><rect x="{px0 - 40}" y="{ptop - 34}" width="40" height="{pbot - ptop + 34}" fill="url(#sw)"/>'
             f'<path d="M{px0} {ptop - 34}V{pbot}" stroke="{CY}" stroke-opacity=".6"/></g></g>')

    # barra di composizione
    sy, sx, sw_ = 336, px0, px1 - px0
    o.append(f'<text x="28" y="{sy + 8}" font-size="11" fill="{MUT}">mix</text>')
    acc = 0.0; t0 = 1.6
    shades = [CY, GRN, AMB, '#ff7a93', '#a78bfa', '#7dd3fc', '#86efac', '#fcd34d']
    rest = 100 - sum(p for _, p in shares)
    parts = shares + ([('other', rest)] if rest > 0.05 else [])
    for j, (lang, pct) in enumerate(parts):
        w = sw_ * pct / 100
        col = shades[j % len(shades)] if lang != 'other' else LINE2
        o.append(f'<rect class="seg" style="--t:{t0 + j * 0.12:.2f}s" x="{sx + acc:.1f}" y="{sy}" width="{max(w - 2, 1):.1f}" height="10" rx="2" fill="{col}"/>')
        acc += w
    src = 'sample data · preview' if sample else f'source: github api · public repos · updated {date}'
    o.append(f'<text x="{px1}" y="{sy + 36}" font-size="11" fill="{MUT}" text-anchor="end">{src}</text>')
    o.append('</g>\n</svg>\n')
    return '\n'.join(o)


if __name__ == '__main__':
    sample = '--sample' in sys.argv
    data = SAMPLE if sample else fetch()
    os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
    open(OUT, 'w').write(build(data, sample))
    print(f'wrote {OUT} ({len(data)} languages)')
