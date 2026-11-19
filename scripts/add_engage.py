#!/usr/bin/env python3
"""Insert the stay-on-site blocks into Seoul Glow Guide pages.

python3 scripts/add_engage.py
Idempotent: everything between the engage markers is rebuilt on every run.
"""
from html import escape as esc
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

# ordered guide pages used for "Read next" and prev/next (slug, label)
GUIDES = [
    ('top-10-olive-young-skincare-must-buys.html', 'Product edit'),
    ('olive-young-tax-refund-and-shopping-guide.html', 'Shop smarter'),
    ('korean-skincare-flashcards.html', 'Show to staff'),
    ('articles.html', 'Archive'),
]
SKIP = {'index.html', 'about.html', 'contact.html', 'privacy.html', 'top-k-beauty-products.html'}
START, END = '<!-- engage:start -->', '<!-- engage:end -->'


def text_of(html, pattern, default=''):
    m = re.search(pattern, html, re.S)
    return m.group(1).strip() if m else default


def short(text, limit=92):
    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) <= limit else text[:limit - 1].rsplit(' ', 1)[0] + '…'


def prefix_of(rel: str) -> str:
    return '../' if rel.startswith('posts/') else './'


def main() -> None:
    pages = {}
    for rel in [r for r, _ in GUIDES] + [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'posts').glob('*.html'))]:
        path = ROOT / rel
        if not path.exists():
            continue
        html = path.read_text(encoding='utf-8')
        title = re.sub(r'\s*[|\-]\s*Seoul Glow Guide\s*$', '', text_of(html, r'<title>(.*?)</title>'))
        pages[rel] = {
            'label': dict(GUIDES).get(rel, 'Checklist'),
            'title': title,
            'desc': text_of(html, r'<meta name="description" content="([^"]*)"'),
        }
    order = [r for r, _ in pages.items() if r.startswith('posts/') is False]
    order += [r for r in pages if r.startswith('posts/')]
    order = [r for r in order if r in pages]

    changed = 0
    for rel in order:
        path = ROOT / rel
        html = path.read_text(encoding='utf-8')
        body = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', html, flags=re.S)
        p = prefix_of(rel)
        idx = order.index(rel)
        picks = [r for r in order if r != rel][:3]
        if not picks:
            continue

        items = ''.join(
            '<li><a href="{p}{slug}"><span class="rn-tag">{label}</span>'
            '<strong>{title}</strong><small>{desc}</small></a></li>'.format(
                p=p, slug=s, label=esc(pages[s]['label']), title=esc(pages[s]['title']),
                desc=esc(short(pages[s]['desc']))) for s in picks)

        prev_rel = order[idx - 1] if idx > 0 else order[-1]
        next_rel = order[idx + 1] if idx + 1 < len(order) else order[0]
        nav = ('<nav class="post-nav" aria-label="Guide navigation">'
               f'<a class="prev" href="{p}{prev_rel}"><small>Previous</small>{esc(pages[prev_rel]["title"])}</a>'
               f'<a class="next" href="{p}{next_rel}"><small>Next</small>{esc(pages[next_rel]["title"])}</a></nav>')

        block = ''.join([
            START,
            '<section class="read-next" id="read-next" aria-labelledby="read-next-title">',
            '<p class="eyebrow">KEEP READING</p>',
            '<h2 id="read-next-title">Read next</h2>',
            f'<ul class="read-next-list">{items}</ul></section>',
            nav,
            END,
        ])

        if '</article>' not in body:
            print('no </article>, skipped', rel)
            continue
        body = body.replace('</article>', block + '</article>', 1)

        if rel in dict(GUIDES) or rel.startswith('posts/'):
            save_row = ('<div class="save-row"><button class="save-btn" type="button" aria-pressed="false" '
                        f'data-save-href="{p}{rel}" '
                        f'data-save-title="{esc(pages[rel]["title"], quote=True)}">'
                        '☆ Save this guide</button><span class="save-note">Kept in this browser only.</span></div>')
        else:
            save_row = ''

        body = re.sub(r'<div class="save-row">.*?</div>', '', body, count=1, flags=re.S)
        h1 = re.search(r'</h1>', body)
        if save_row and h1:
            body = body[:h1.end()] + save_row + body[h1.end():]

        if body != html:
            path.write_text(body, encoding='utf-8')
            changed += 1
    print(f'engage blocks written to {changed} pages')


if __name__ == '__main__':
    main()
