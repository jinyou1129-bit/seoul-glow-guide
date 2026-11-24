#!/usr/bin/env python3
"""Publish one short shopping checklist per day and refresh the archive pages.

Kept deliberately small: the generator only touches posts/*.html, articles.html,
the latest-guides block in index.html and sitemap.xml.
"""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from add_seo_meta import DEFAULT_IMAGE, head_tags, patch  # noqa: E402

BASE = 'https://jinyou1129-bit.github.io/seoul-glow-guide/'
TOPICS = [
    ('Hydrating serum', 'Check the texture and full ingredient list.'),
    ('Gentle cleanser', 'Compare size, texture and directions.'),
    ('Sunscreen', 'Check SPF, broad-spectrum labeling and directions on the package.'),
    ('Cleansing oil', 'Check directions and whether the format fits your routine.'),
    ('Moisturizer', 'Compare textures and ingredients.'),
    ('Toner', 'Compare fragrance and ingredient lists.'),
    ('Lip care', 'Check the ingredient list for known irritants.'),
    ('Sheet mask', 'Read instructions and ingredient list.'),
    ('Exfoliant', 'Follow instructions and avoid introducing too many new products at once.'),
    ('Ampoule', 'Compare ingredients, size and price.'),
]

NAV = ('<nav><a href="{p}index.html#guides">Guides</a><a href="{p}articles.html">All guides</a>'
       '<a href="{p}about.html">About</a><a href="{p}contact.html">Contact</a></nav>')
FOOT = ('<footer><div class="wrap"><p class="foot-links"><a href="{p}index.html">Home</a> · '
        '<a href="{p}articles.html">All guides</a> · <a href="{p}about.html">About</a> · '
        '<a href="{p}contact.html">Contact</a> · <a href="{p}privacy.html">Privacy Policy</a></p>'
        '<p>✿ Seoul Glow Guide · Independent traveler resource. Not affiliated with Olive Young. '
        'Information can change; confirm details with official sources.</p></div></footer>')


def render_post(day, heading, tip):
    rel = f'posts/{day.isoformat()}.html'
    title = f'{heading} | Seoul Glow Guide'
    description = (f'A Seoul shopping checklist for {heading.split(":")[0].lower()}: what to compare in store, '
                   'how to read the label and when to ask about a tax refund.')
    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
{head_tags(rel, title, description, DEFAULT_IMAGE)}
<link rel="stylesheet" href="../style.css?v=20261120c">
</head>
<body>
<header><div class="nav wrap"><a class="brand" href="../">✿ Seoul Glow Guide</a>{NAV.format(p='../')}</div></header>
<main class="wrap">
<article class="article">
<p class="eyebrow">AUTOMATED SHOPPING CHECKLIST · {day}</p>
<h1>{escape(heading)}</h1>
<p>This is a template-generated checklist, not a firsthand product review. Product availability, formulas and prices may change.</p>
<h2>In store</h2>
<p>{escape(tip)}</p>
<ol>
<li>Set a budget and compare price per unit.</li>
<li>Read the exact product label, ingredients and instructions. Ask staff if unsure.</li>
<li>Patch-test new products and stop using them if irritation occurs.</li>
<li>Bring your passport and ask staff about current tax-refund eligibility before paying.</li>
</ol>
<p>For current selection check <a href="https://global.oliveyoung.com/">Olive Young Global</a>. For tax rules consult <a href="https://www.customs.go.kr/english/main.do">Korea Customs Service</a>.</p>
<p><a href="../articles.html">All guides</a></p>
</article>
</main>
{FOOT.format(p='../')}
<script src="../engage.js" defer></script>
</body>
</html>
"""
    return rel, body


def render_archive(entries):
    title = 'All guides | Seoul Glow Guide'
    description = ('Every Seoul Glow Guide checklist in one place: Olive Young shopping, tax refund steps, '
                   'K-beauty picks and Korean shopping phrases for visitors.')
    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
{head_tags('articles.html', title, description, DEFAULT_IMAGE)}
<link rel="stylesheet" href="style.css?v=20261120c">
</head>
<body>
<header><div class="nav wrap"><a class="brand" href="./">✿ Seoul Glow Guide</a>{NAV.format(p='./')}</div></header>
<main class="wrap">
<article class="article">
<p class="eyebrow">THE ARCHIVE</p>
<h1>All guides</h1>
<p>Automated shopping checklists and editorial guides. Check the shelf label and ingredients before buying.</p>
<ul>
{''.join(f'<li><a href="posts/{name}">{title_text}</a> · {name[:-5]}</li>' for name, title_text in entries)}
</ul>
<p><a href="./index.html#guides">Back to the guides →</a></p>
</article>
</main>
{FOOT.format(p='./')}
<script src="./engage.js" defer></script>
</body>
</html>
"""
    return body


def main():
    day = datetime.now(timezone.utc).date()
    topic, tip = TOPICS[day.toordinal() % len(TOPICS)]
    heading = f'{topic}: a Seoul shopping checklist'
    posts = ROOT / 'posts'
    posts.mkdir(exist_ok=True)
    rel, body = render_post(day, heading, tip)
    target = ROOT / rel
    if not target.exists():
        target.write_text(patch(rel, body), encoding='utf-8')
        print('Published', rel)

    entries = []
    for path in sorted(posts.glob('*.html'), reverse=True):
        match = re.search(r'<h1>(.*?)</h1>', path.read_text(encoding='utf-8'))
        if match:
            entries.append((path.name, match.group(1)))
    (ROOT / 'articles.html').write_text(render_archive(entries), encoding='utf-8')

    index = ROOT / 'index.html'
    html = index.read_text(encoding='utf-8')
    start, end = '<!-- POSTS_START -->', '<!-- POSTS_END -->'
    if html.count(start) != 1 or html.count(end) != 1:
        raise ValueError('Missing unique post markers in index.html')
    latest = '<ul>' + ''.join(
        f'<li><a href="posts/{name}">{title_text}</a> · {name[:-5]}</li>' for name, title_text in entries[:5]
    ) + '</ul>'
    before, tail = html.split(start, 1)
    _, after = tail.split(end, 1)
    index.write_text(before + start + latest + end + after, encoding='utf-8')

    pages = ['', 'top-10-olive-young-skincare-must-buys.html', 'olive-young-tax-refund-and-shopping-guide.html',
             'korean-skincare-flashcards.html', 'articles.html', 'about.html', 'contact.html', 'privacy.html']
    pages += ['best-olive-young-korean-sunscreens-guide.html', 'best-olive-young-toner-pads-guide.html', 'kpop-idol-skincare-and-makeup-guide.html'] + ['posts/' + name for name, _ in entries]; lastmods = {u.findtext('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'): u.findtext('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod') for u in __import__('xml.etree.ElementTree', fromlist=['parse']).parse(ROOT / 'sitemap.xml').getroot() if u.findtext('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')}
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + ''.join(f'<url><loc>{BASE}{page}</loc><lastmod>{day.isoformat() if page in ("", "articles.html", rel) else lastmods.get(BASE + page, day.isoformat())}</lastmod></url>\n' for page in pages)
           + '</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(xml, encoding='utf-8')
    try:
        import add_engage
        add_engage.main()
    except Exception as exc:  # never fail the daily publish over the blocks
        print('engage blocks not refreshed:', exc)
    print('Archive, latest list and sitemap updated')


if __name__ == '__main__':
    main()
