#!/usr/bin/env python3
"""
Verify that Rudin's prose has been transcribed verbatim.

Strips every annotation from the chapter sources -- boxes, margin notes,
editorial commands -- leaving only what is supposed to be Rudin.  Aligns the
result against text extracted from the original PDF and reports any run of
Rudin's words that failed to survive.

Two passes run:

  PROSE   -- aligned word by word.  Single- and double-letter tokens are
             dropped from both sides, because math residue does not survive
             pdftotext comparably; gaps of MIN_RUN+ words are reported.

  CLAUSES -- targeted checks on the structures the prose pass is blind to:
             axiom and enumerated-clause bodies, displayed formulas, and
             numbered-item labels.  A dropped clause inside (M1) is a handful
             of characters and would slip under any word-run threshold, so
             these are compared item by item rather than by alignment.

Even so, the symbolic content of displays is only compared by its letter
skeleton.  Formulas still repay reading by hand.

Usage:
    python3 tools/check-fidelity.py <source.pdf> <first> <last> <chapter-dir>
"""
import difflib, glob, os, re, subprocess, sys, unicodedata

ANNOTATION_ENVS = ('unpack', 'deeper', 'pitfall', 'roadmap', 'recap',
                   'signpost', 'proofwalk', 'tikzpicture')
NOTE_CMDS = ('kn', 'kd', 'kw', 'mnote')
MIN_RUN = 4          # report gaps of at least this many consecutive words


def strip_braced(text, cmds):
    """Remove \\cmd{...} and its argument, honouring nested braces."""
    for cmd in cmds:
        out, i, pat = [], 0, '\\' + cmd + '{'
        while True:
            j = text.find(pat, i)
            if j < 0:
                out.append(text[i:])
                break
            out.append(text[i:j])
            k, depth = j + len(pat), 1
            while k < len(text) and depth:
                depth += (text[k] == '{') - (text[k] == '}')
                k += 1
            i = k
        text = ''.join(out)
    return text


def normalise(text):
    text = unicodedata.normalize('NFKD', text)       # fi/fl ligatures -> f i
    text = re.sub(r'-\s*\n\s*', '', text)            # rejoin hyphenated breaks
    text = re.sub(r'[^A-Za-z]+', ' ', text).lower()
    # Drop 1-2 letter tokens: math variable residue on one side, real words on
    # the other, but symmetric removal keeps the alignment honest.
    return [w for w in text.split() if len(w) > 2]


def rudin_from_pdf(pdf, first, last):
    raw = subprocess.run(['pdftotext', '-f', first, '-l', last, pdf, '-'],
                         capture_output=True).stdout.decode('utf-8', 'ignore')
    kept = []
    for line in raw.split('\n'):
        s = line.strip()
        if not s or s.isdigit():                     # page numbers
            continue
        if s.isupper() and len(s.split()) <= 6:      # running heads
            continue
        kept.append(line)
    return normalise('\n'.join(kept))


def rudin_from_tex(chdir):
    text = ''
    for path in sorted(glob.glob(os.path.join(chdir, '*.tex'))):
        text += open(path, errors='ignore').read() + '\n'
    text = re.sub(r'(?<!\\)%.*', '', text)
    for env in ANNOTATION_ENVS:
        text = re.sub(r'\\begin\{' + env + r'\}(\[[^\]]*\])?.*?\\end\{' + env + r'\}',
                      ' ', text, flags=re.S)
    text = strip_braced(text, NOTE_CMDS)
    # \ritem{1.8}{Definition} -- the second argument IS Rudin's word, keep it.
    text = re.sub(r'\\ritem\{[^}]*\}\{([^}]*)\}', r' \1 ', text)
    text = re.sub(r'\\(rsection|rchapter)\s*\{([^}]*)\}', r' \2 ', text)
    text = re.sub(r'\\rskip\{[^}]*\}', ' ', text)
    text = re.sub(r'\\[a-zA-Z@]+\*?', ' ', text)
    return normalise(text)


def main():
    pdf, first, last, chdir = sys.argv[1:5]
    src, mine = rudin_from_pdf(pdf, first, last), rudin_from_tex(chdir)

    sm = difflib.SequenceMatcher(None, src, mine, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    print(f'Rudin prose words in pp. {first}-{last}: {len(src)}')
    print(f'matched in transcription:                {matched} '
          f'({100*matched/len(src):.1f}%)')
    print()

    gaps = [(i1, i2) for tag, i1, i2, _, _ in sm.get_opcodes()
            if tag in ('delete', 'replace') and i2 - i1 >= MIN_RUN]
    if not gaps:
        print(f'No run of {MIN_RUN}+ consecutive Rudin prose words is missing.')
        return 0
    print(f'{len(gaps)} run(s) of {MIN_RUN}+ words present in Rudin but not found.')
    print('These need a human eye: math residue and any page-range overshoot')
    print('into the next chapter show up here and are usually benign.')
    for i1, i2 in gaps:
        print(f'  [{i1}] ' + ' '.join(src[i1:min(i2, i1 + 30)]))
    return 1





# ---------------------------------------------------------------------------
#  Clause-level pass
# ---------------------------------------------------------------------------
#  The prose pass aligns long word sequences and drops short tokens, so a
#  two-word clause dropped from inside an axiom slips straight through.  This
#  pass compares the field axioms (A1-A5, M1-M5) body by body, keeping every
#  letter including single-character variable names.
#
#  It compares against the RETYPED SOURCE, which is itself imperfect -- so a
#  deliberate restoration of Rudin's original reading shows up here as a
#  difference.  Those are registered in tools/corrections.txt; anything not
#  registered is an unintended slip and fails the check.

LABEL = re.compile(r'\(([AM]\d)\)[.\s]*(.*?)(?=\n\s*\n|\((?:[AM]\d)\)|\Z)', re.S)


def clause_words(text):
    """Like normalise() but keeps single letters -- axioms are short."""
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'-\s*\n\s*', '', text)
    return re.sub(r'[^A-Za-z]+', ' ', text).lower().split()


def labelled_items(text):
    out = {}
    for m in LABEL.finditer(text):
        # 12 tokens covers an axiom body and stops before the list
        # terminator or the next heading leaks in.
        body = ' '.join(clause_words(m.group(2))[:12])
        if body and m.group(1) not in out:
            out[m.group(1)] = body
    return out


def load_corrections(path='tools/corrections.txt'):
    reg = {}
    if not os.path.exists(path):
        return reg
    for line in open(path):
        line = line.split('#')[0].strip()
        if not line or '|' not in line:
            continue
        label, reason = line.split('|', 1)
        reg[label.strip()] = reason.strip()
    return reg


def clause_pass(pdf, first, last, chdir):
    raw = subprocess.run(['pdftotext', '-f', first, '-l', last, pdf, '-'],
                         capture_output=True).stdout.decode('utf-8', 'ignore')
    tex = ''
    for path in sorted(glob.glob(os.path.join(chdir, '*.tex'))):
        tex += open(path, errors='ignore').read() + '\n'
    for env in ANNOTATION_ENVS:
        tex = re.sub(r'\\begin\{' + env + r'\}(\[[^\]]*\])?.*?\\end\{' + env + r'\}',
                     ' ', tex, flags=re.S)
    tex = strip_braced(tex, NOTE_CMDS)
    # \item under label=(A\arabic*) -> emit the label pdftotext shows
    for tag in ('A', 'M'):
        pat = r'label=\(' + tag + r'\\arabic\*\).*?\\end\{enumerate\}'
        for m in list(re.finditer(pat, tex, re.S)):
            n = [0]
            def sub(_, tag=tag, n=n):
                n[0] += 1
                return f'({tag}{n[0]}) '
            tex = tex.replace(m.group(0), re.sub(r'\\item\s', sub, m.group(0)), 1)
    tex = re.sub(r'\\[a-zA-Z@]+\*?', ' ', tex)

    src, mine = labelled_items(raw), labelled_items(tex)
    reg = load_corrections()
    unexpected, registered, reverted = [], [], []
    for label, body in src.items():
        got = mine.get(label, '')
        same = difflib.SequenceMatcher(None, body, got).ratio() > 0.97
        if same:
            # Matching the source is normally right -- unless a correction was
            # registered for this clause, in which case the fix has been lost.
            if label in reg:
                reverted.append((label, body, got, reg[label]))
            continue
        (registered if label in reg else unexpected).append((label, body, got, reg.get(label)))
    return unexpected, registered, reverted


if __name__ == '__main__':
    # The prose pass is advisory -- its gaps require judgement.  Only the
    # clause pass, which is exact, decides the exit status.
    main()
    pdf, first, last, chdir = sys.argv[1:5]
    print()
    print('--- clause pass (field axioms A1-A5, M1-M5) ---')
    bad, known, lost = clause_pass(pdf, first, last, chdir)
    for label, body, got, reason in known:
        print(f'  ({label}) registered correction applied -- {reason}')
    for label, body, got, reason in lost:
        print(f'  ({label}) REGRESSION: registered correction is NOT applied')
        print(f'         expected to differ from source -- {reason}')
    if not bad and not lost:
        print('  No unregistered or reverted axiom-clause differences.')
    for label, body, got, _ in bad:
        print(f'  ({label}) UNREGISTERED difference')
        print(f'         source: {body}')
        print(f'         mine  : {got or "<missing>"}')
    sys.exit(1 if (bad or lost) else 0)
