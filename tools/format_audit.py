#!/usr/bin/env python3
"""Measure a compiled thesis PDF against the Temple Graduate School formatting rules.

Usage: python tools/format_audit.py main.pdf [first_page last_page]
Checks every page for: content (text, images, table rules, page number) inside the
1.5" left / 1" top, right, bottom margins; page-number position, size and sequence; text
smaller than 10 pt; non-black text; numbered headings stranded at the bottom of a page;
fonts that are not embedded or not Type 1 (including fonts inside included PDF figures);
and encryption.  Prints a summary and writes <name>_audit.json next to the PDF.
Requires: pip install pdfplumber pypdf

This is a self-check, not an official approval: the Graduate School format review decides."""
import sys, re, json, collections, statistics
import pdfplumber
from pypdf import PdfReader

IN = 72.0
LEFT, RIGHT, TOP, BOTTOM = 1.5 * IN, 1.0 * IN, 1.0 * IN, 1.0 * IN
TOL = 0.5  # pt

def roman_val(s):
    vals = dict(i=1, v=5, x=10, l=50, c=100); t = 0
    for a, b in zip(s, s[1:] + ' '):
        t += -vals[a] if vals.get(b, 0) > vals[a] else vals[a]
    return t

def main(pdf, first=1, last=None):
    rep = collections.defaultdict(list)
    pages_info = []
    with pdfplumber.open(pdf) as P:
        n = len(P.pages); last = last or n
        for pno in range(first, last + 1):
            pg = P.pages[pno - 1]
            W, H = float(pg.width), float(pg.height)
            rot = pg.rotation if hasattr(pg, 'rotation') else 0
            land = W > H
            # content boxes
            boxes = []
            chars = [c for c in pg.chars if c['text'].strip()]
            for c in chars: boxes.append((c['x0'], c['top'], c['x1'], c['bottom'], 'text'))
            for im in pg.images: boxes.append((im['x0'], im['top'], im['x1'], im['bottom'], 'image'))
            for r in pg.rects + pg.lines + pg.curves:
                if (r['x1'] - r['x0']) > 0.1 or (r['bottom'] - r['top']) > 0.1:
                    boxes.append((r['x0'], r['top'], r['x1'], r['bottom'], 'rule'))
            if not boxes:
                pages_info.append(dict(page=pno, empty=True)); rep['blank_pages'].append(pno); continue
            # physical margins: for landscape (rotated) pages the binding edge is the physical left,
            # which appears as the top of the rotated view.
            if land:
                l, t_, r_, b_ = TOP, LEFT, BOTTOM, RIGHT   # (left, top, right, bottom) in rotated view
            else:
                l, t_, r_, b_ = LEFT, TOP, RIGHT, BOTTOM
            x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
            x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
            viol = []
            for b in boxes:
                if b[0] < l - TOL: viol.append(('left', round((l - b[0]) / IN, 3), b[4]))
                if b[2] > W - r_ + TOL: viol.append(('right', round((b[2] - (W - r_)) / IN, 3), b[4]))
                if b[1] < t_ - TOL: viol.append(('top', round((t_ - b[1]) / IN, 3), b[4]))
                if b[3] > H - b_ + TOL: viol.append(('bottom', round((b[3] - (H - b_)) / IN, 3), b[4]))
            if viol:
                worst = {}
                for side, amt, kind in viol:
                    k = (side, kind); worst[k] = max(worst.get(k, 0), amt)
                rep['margin_violations'].append((pno, {f'{s}/{k}': v for (s, k), v in worst.items()}))
            # page number: lowest line of text
            words = pg.extract_words(keep_blank_chars=False, use_text_flow=True, extra_attrs=['size', 'fontname'])
            lines = collections.OrderedDict()
            for w in words:
                key = round(w['bottom'])
                lines.setdefault(key, []).append(w)
            ys = sorted(lines)
            num = None
            if ys:
                lastline = ' '.join(w['text'] for w in sorted(lines[ys[-1]], key=lambda w: w['x0']))
                if re.fullmatch(r'[ivxlc]+|\d+', lastline.strip()) and (not land):
                    lw = lines[ys[-1]]; cx = (lw[0]['x0'] + lw[-1]['x1']) / 2
                    num = lastline.strip()
                    if abs(cx - (LEFT + (W - RIGHT)) / 2) > 3: rep['page_number_not_centred'].append((pno, round(cx, 1)))
                    if lw[0]['size'] < 9.9: rep['page_number_small'].append(pno)
            pages_info.append(dict(page=pno, num=num, land=land, box=[round(v / IN, 3) for v in (x0, y0, W - x1, H - y1)]))
            # fonts / sizes / colour
            for c in chars:
                col = c.get('non_stroking_color')
                if col not in (None, 0, (0,), [0], (0, 0, 0), [0, 0, 0], (0, 0, 0, 1), [0, 0, 0, 1]) and not (isinstance(col, (list, tuple)) and all(abs(v) < 1e-3 for v in col[:3]) ):
                    rep['non_black_text'].append((pno, str(col), c['text'])); break
            small = [c for c in chars if c['size'] < 9.9]
            if small:
                # superscript citations / exponents are expected; report only runs of >= 4 small chars on a baseline
                runs = collections.Counter(round(c['bottom']) for c in small)
                big = [k for k, v in runs.items() if v >= 6]
                if big:
                    sample = ''.join(c['text'] for c in small if round(c['bottom']) == big[0])[:60]
                    rep['small_text_lines'].append((pno, round(min(c['size'] for c in small), 1), sample))
            # heading stranded at page bottom (line above page number)
            if len(ys) >= 2 and num:
                prev = sorted(lines[ys[-2]], key=lambda w: w['x0'])
                txt = ' '.join(w['text'] for w in prev)
                if re.match(r'^\d+(\.\d+)+\s+\S', txt) and 'Bold' in prev[0]['fontname'] or ('Medi' in prev[0]['fontname'] and re.match(r'^[A-Z]?\d*(\.\d+)+\s', txt)):
                    rep['heading_at_page_bottom'].append((pno, txt[:70]))
    # page-number sequence
    seq = [(p['page'], p.get('num')) for p in pages_info if not p.get('empty')]
    first_arabic = next((pg for pg, n_ in seq if n_ and n_.isdigit()), None)
    prev = None
    for pg, n_ in seq:
        if n_ is None: continue
        v = int(n_) if n_.isdigit() else roman_val(n_)
        expected_from_pdf = None
        if n_.isdigit(): expected_from_pdf = pg - first_arabic + 1
        else: expected_from_pdf = pg
        if v != expected_from_pdf: rep['page_number_sequence'].append((pg, n_, expected_from_pdf))
    missing = [pg for pg, n_ in seq if n_ is None and pg > 1 and not dict((p['page'], p.get('land')) for p in pages_info).get(pg)]
    rep['pages_without_visible_number'] = missing
    # PDF-level
    R = PdfReader(pdf)
    rep['encrypted'] = R.is_encrypted
    # fonts: the Handbook requires embedded PostScript Type 1 fonts.  Type 3 (bitmap, e.g. from
    # matplotlib's default PDF output) and TrueType fonts -- usually inside figures -- are flagged.
    bad_fonts = {}
    def check_fonts(res, pno, seen):
        if res is None: return
        res = res.get_object()
        fd = res.get('/Font')
        if fd is not None:
            for key, ref in fd.get_object().items():
                f = ref.get_object()
                if id(f) in seen: continue
                seen.add(id(f))
                sub = str(f.get('/Subtype')); name = str(f.get('/BaseFont', f.get('/Name', key)))
                fonts_to_check = [f]
                if sub == '/Type0':
                    fonts_to_check = [d.get_object() for d in f.get('/DescendantFonts', [])]
                for g in fonts_to_check:
                    gsub = str(g.get('/Subtype')); desc = g.get('/FontDescriptor')
                    desc = desc.get_object() if desc is not None else None
                    if gsub == '/Type3':
                        problem = 'Type 3 (bitmap) font'
                    elif desc is None or not any(k in desc for k in ('/FontFile', '/FontFile2', '/FontFile3')):
                        problem = 'not embedded'
                    elif '/FontFile2' in desc or gsub in ('/TrueType', '/CIDFontType2'):
                        problem = 'TrueType, not Type 1'
                    else:
                        continue
                    bad_fonts.setdefault((name, problem), []).append(pno)
        xo = res.get('/XObject')
        if xo is not None:
            for _, ref in xo.get_object().items():
                x = ref.get_object()
                if x.get('/Subtype') == '/Form' and id(x) not in seen:
                    seen.add(id(x)); check_fonts(x.get('/Resources'), pno, seen)
    for i, page in enumerate(R.pages, 1):
        check_fonts(page.get('/Resources'), i, set())
    rep['font_problems'] = [(name, problem, sorted(set(p))[:10]) for (name, problem), p in bad_fonts.items()]
    out = dict(pages=len(seq), first_arabic_pdf_page=first_arabic, report=rep, pages_info=pages_info)
    json.dump(out, open(pdf.rsplit('.', 1)[0] + '_audit.json', 'w'), indent=1, default=str)
    # summary
    print('pages audited:', len(seq), '| Chapter 1 starts on PDF page', first_arabic)
    checks = ['margin_violations', 'page_number_sequence', 'pages_without_visible_number',
              'page_number_not_centred', 'page_number_small', 'small_text_lines', 'non_black_text',
              'heading_at_page_bottom', 'font_problems', 'blank_pages']
    for k in checks + [k for k in rep if k not in checks and k != 'encrypted']:
        v = rep.get(k, [])
        print(f'{"OK   " if not v else "CHECK"} {k}: {len(v)}', v[:12] if v else '')
    print(f'{"CHECK" if rep["encrypted"] else "OK   "} encrypted: {rep["encrypted"]}')

if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], *(int(x) for x in a[1:3]))
