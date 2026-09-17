#!/usr/bin/env python3
"""Convert data/patch-notes/html/*.html to plain text for grep.

Usage: python3 tools/patch_notes_text.py [out_dir]   (default .cache/patch-notes-text, git ignored)

Writes one .txt per note with the same file name (NNN_date_title.txt), one paragraph per line,
so `grep -h -o "[^.]*Phrase[^.]*\\." .cache/patch-notes-text/*` returns whole sentences and the
file name prefix (NNN) is the manifest sequence number used in constants sources:
    data/patch-notes/html NNN (YYYY-MM-DD): <sentence>
Only rewrites files whose html is newer than the text.
"""
import html, os, re, sys
from html.parser import HTMLParser

SRC = os.path.join(os.path.dirname(__file__), '..', 'data', 'patch-notes', 'html')
BLOCK = {'p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'br', 'tr', 'td', 'th', 'ul', 'ol', 'section', 'article', 'blockquote'}


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        elif tag in BLOCK:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def convert(src_path):
    p = Text()
    p.feed(open(src_path, encoding='utf-8', errors='replace').read())
    text = ''.join(p.parts)
    lines = [re.sub(r'[ \t ]+', ' ', l).strip() for l in text.split('\n')]
    return '\n'.join(l for l in lines if l) + '\n'


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    n = 0
    for name in sorted(os.listdir(SRC)):
        if not name.endswith('.html'):
            continue
        src = os.path.join(SRC, name)
        dst = os.path.join(out_dir, name[:-5] + '.txt')
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        open(dst, 'w', encoding='utf-8').write(convert(src))
        n += 1
    print(f'{n} notes converted into {out_dir}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '.cache', 'patch-notes-text'))
