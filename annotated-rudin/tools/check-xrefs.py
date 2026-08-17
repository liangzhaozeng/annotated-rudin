#!/usr/bin/env python3
"""Resolve every cross-reference the companion makes into the annotated book.

Two kinds of citation are checked:

  S<c>.<n>   an appendix item -- must exist as \\sitem{S<c>.<n>} in appendix/
  <c>.<n>    one of Rudin's own numbered items -- must exist as
             \\ritem{<c>.<n>} in ch0<c>/  ... but only for chapters that are
             actually written.  Citations into unwritten chapters are
             reported as FORWARD, not as failures, since there is nothing to
             check them against yet.

Exit 0 when nothing is broken; 1 when a citation names something that should
exist and does not.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WRITTEN_CHAPTERS = {1, 2, 3, 4}          # chapters transcribed so far


def targets():
    """Every label the book currently defines."""
    s_items, r_items = set(), set()
    for f in (ROOT / 'appendix').glob('*.tex'):
        s_items |= set(re.findall(r'\\sitem\{(S\d+\.\d+)\}', f.read_text()))
    for d in sorted(ROOT.glob('ch0*')):
        for f in d.glob('*.tex'):
            r_items |= set(re.findall(r'\\ritem\{(\d+\.\d+)\}', f.read_text()))
    return s_items, r_items


def citations(src_dir):
    """Every citation the companion makes, with the file it appears in."""
    found = []
    for f in sorted(src_dir.glob('*.tex')):
        text = f.read_text()
        # strip our own theorem/example labels so they are not read as cites
        text = re.sub(r'\\ritem\{[TE]\d+\}\{[^}]*\}', '', text)
        # strip figure bodies -- TikZ coordinates look exactly like citations
        text = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',
                      '', text, flags=re.S)
        for m in re.finditer(r'\bS(\d+)\.(\d+)\b', text):
            found.append((f.name, 'S', f'S{m.group(1)}.{m.group(2)}'))
        for m in re.finditer(r'(?<![\w.])(\d{1,2})\.(\d{1,2})(?![\d.])', text):
            found.append((f.name, 'R', f'{m.group(1)}.{m.group(2)}'))
    return found


def main():
    src = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'companion')
    s_items, r_items = targets()
    print(f'book defines {len(s_items)} appendix items, '
          f'{len(r_items)} Rudin items')

    broken, forward, ok = [], set(), 0
    for fname, kind, label in citations(src):
        if kind == 'S':
            if label in s_items:
                ok += 1
            else:
                broken.append((fname, label, 'no such appendix item'))
        else:
            chapter = int(label.split('.')[0])
            if chapter not in WRITTEN_CHAPTERS:
                forward.add(label)
            elif label in r_items:
                ok += 1
            else:
                broken.append((fname, label, f'not found in ch0{chapter}/'))

    print(f'resolved {ok} citation(s) against written chapters')
    if forward:
        print(f'{len(forward)} forward reference(s) into unwritten chapters '
              f'(not checkable): {", ".join(sorted(forward))}')
    if broken:
        print(f'\nBROKEN ({len(broken)}):')
        for fname, label, why in broken:
            print(f'  {fname}: {label} -- {why}')
        return 1
    print('\nNo broken cross-references.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
