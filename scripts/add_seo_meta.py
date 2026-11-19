#!/usr/bin/env python3
"""Add description, Open Graph, Twitter Card and self-canonical tags to Glow pages.

python3 scripts/add_seo_meta.py        # patch every page in place
Imported by scripts/generate_post.py for newly generated posts.
"""
from html import escape as esc
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://jinyou1129-bit.github.io/seoul-glow-guide/'
SITE = 'Seoul Glow Guide'

U = 'https://images.unsplash.com/{}?auto=format&fit=crop&w=1200&h=630&q=80'
IMG_SKINCARE = U.format('photo-1556229010-6c3f2c9ca5f8')
IMG_PRODUCTS = U.format('photo-1611930022073-b7a4ba5fcccd')
IMG_SHELF = U.format('photo-1598440947619-2c35fc9aa908')
IMG_FLASHCARDS = U.format('photo-1556228720-195a672e8a03')

DESCRIPTIONS = {
    'index.html': 'A practical K-beauty and Olive Young guide for Seoul visitors: what to buy, how tax refunds work and Korean phrases to show store staff.',
    'articles.html': 'Every Seoul Glow Guide checklist in one place: Olive Young shopping, tax refund steps, K-beauty picks and Korean shopping phrases for visitors.',
    'korean-skincare-flashcards.html': 'Korean phrases to show store staff in Seoul: skin type, fragrance-free, ingredient checks, sunscreen and tax refund questions.',
    'olive-young-tax-refund-and-shopping-guide.html': 'How to shop Olive Young as a visitor: passport, tax refund questions, minimum purchase amounts and a simple in-store shopping formula.',
    'top-10-olive-young-skincare-must-buys.html': 'A practical shortlist of ten K-beauty skincare picks for Olive Young shoppers in Seoul, with Korean product names to show staff.',
    'about.html': 'Who writes Seoul Glow Guide, what the site covers, how it is funded and how to report a correction.',
    'contact.html': 'Send Seoul Glow Guide a question, a correction or a partnership idea by form or email.',
    'privacy.html': 'How Seoul Glow Guide handles contact form data, cookies, third-party advertising and affiliate links.',
    'posts/2026-11-19.html': 'A Seoul shopping checklist for ampoules: what to compare in store, how to read the label and when to ask about a tax refund.',
}

IMAGES = {
    'index.html': IMG_SKINCARE,
    'articles.html': IMG_PRODUCTS,
    'korean-skincare-flashcards.html': IMG_FLASHCARDS,
    'olive-young-tax-refund-and-shopping-guide.html': IMG_SHELF,
    'top-10-olive-young-skincare-must-buys.html': IMG_PRODUCTS,
    'about.html': IMG_SHELF,
    'contact.html': IMG_PRODUCTS,
    'privacy.html': IMG_PRODUCTS,
    'posts/2026-11-19.html': IMG_PRODUCTS,
}
DEFAULT_IMAGE = IMG_PRODUCTS

# Pages that are not guides (website) rather than articles.
NON_ARTICLE = {'index.html', 'about.html', 'contact.html', 'privacy.html', 'articles.html'}

REMOVE = [
    re.compile(r'<link[^>]+rel=[\"\']canonical[\"\'][^>]*>', re.I),
    re.compile(r'<meta[^>]+property=[\"\']og:[^\"\']*[\"\'][^>]*>', re.I),
    re.compile(r'<meta[^>]+name=[\"\']twitter:[^\"\']*[\"\'][^>]*>', re.I),
]


def url_for(rel_name: str) -> str:
    """rel_name is the path inside the site, e.g. 'index.html' or 'posts/2026-11-19.html'."""
    if rel_name == 'index.html':
        return BASE
    return BASE + rel_name


def head_tags(rel_name: str, title: str, description: str, image: str) -> str:
    url = url_for(rel_name)
    og_type = 'website' if rel_name in NON_ARTICLE else 'article'
    image_attr = image.replace('&', '&amp;')
    tags = [
        f'<link rel="canonical" href="{esc(url, quote=True)}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{esc(SITE, quote=True)}">',
        '<meta property="og:locale" content="en_US">',
        f'<meta property="og:title" content="{esc(title, quote=True)}">',
        f'<meta property="og:description" content="{esc(description, quote=True)}">',
        f'<meta property="og:url" content="{esc(url, quote=True)}">',
        f'<meta property="og:image" content="{image_attr}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(title, quote=True)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title, quote=True)}">',
        f'<meta name="twitter:description" content="{esc(description, quote=True)}">',
        f'<meta name="twitter:image" content="{image_attr}">',
    ]
    return ''.join(tags)


def patch(rel_name: str, html: str) -> str:
    """Return html with head tags (and a missing description) inserted."""
    head_end = html.find('</head>')
    if head_end == -1:
        return html
    head, rest = html[:head_end], html[head_end:]
    name = rel_name.split('/')[-1]

    title_m = re.search(r'<title>(.*?)</title>', head, re.S)
    title = title_m.group(1).strip() if title_m else SITE

    desc_m = re.search(r'<meta[^>]+name=[\"\']description[\"\'][^>]*>', head, re.I)
    if desc_m:
        value = re.search(r'content=[\"\']([^\"\']*)[\"\']', desc_m.group(0))
        description = value.group(1) if value else (DESCRIPTIONS.get(rel_name) or DESCRIPTIONS.get(name, ''))
    else:
        description = DESCRIPTIONS.get(rel_name) or DESCRIPTIONS.get(name)
        if not description:
            print('no description for', rel_name)
            return html
        head = head.rstrip() + f'<meta name="description" content="{esc(description, quote=True)}">'

    for pattern in REMOVE:
        head = pattern.sub('', head)
    head = head.rstrip() + head_tags(rel_name, title, description, IMAGES.get(rel_name) or IMAGES.get(name) or DEFAULT_IMAGE)
    return head + rest


def main() -> None:
    pages = sorted(ROOT.glob('*.html')) + sorted((ROOT / 'posts').glob('*.html'))
    changed = 0
    for path in pages:
        rel = path.relative_to(ROOT).as_posix()
        if rel == 'top-k-beauty-products.html':
            continue  # redirect stub
        html = path.read_text(encoding='utf-8')
        new = patch(rel, html)
        if new != html:
            path.write_text(new, encoding='utf-8')
            changed += 1
    print(f'seo meta written to {changed} pages')


if __name__ == '__main__':
    main()
