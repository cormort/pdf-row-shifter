#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-check for the English financial-report fixtures (_fixtures/en/).

Verifies against manifest.json:
  1. every note_line and trap_row appears verbatim (whitespace-normalized)
     in the PDF's extracted text layer
  2. page count and paper size (612 x 792 pt)
  3. every page has full-width 天線/地線 vector rules (>= 90% page width)
  4. note_lines_per_page matches per-page note counts
  5. trap_rows sit in the table region (data rows, not notes)
  6. per-page extracted line counts printed for eyeballing data_row_count
"""
import json
import os
import re
import sys

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTLine, LTRect, LTTextBoxHorizontal, LTTextLineHorizontal

# pdfminer.six (>= 2026) with laparams=None yields LTTextBoxHorizontal for
# each text run; older versions yield LTTextLineHorizontal. Accept both.
_TEXT_TYPES = (LTTextBoxHorizontal, LTTextLineHorizontal)

HERE = os.path.dirname(os.path.abspath(__file__))
EN = os.path.join(HERE, "en")
MIN_RULE_LEN = 612 * 0.9  # 550.8 pt


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _collect(items, texts, rules):
    """Recursively gather text lines and full-width horizontal rules."""
    for it in items:
        if isinstance(it, LTTextLineHorizontal):
            texts.append(it)
        elif isinstance(it, LTTextBoxHorizontal):
            kids = list(it)
            if kids:
                _collect(kids, texts, rules)
            else:  # older pdfminer: box may be the leaf itself
                texts.append(it)
        elif isinstance(it, (LTLine, LTRect)):
            w = abs(it.x1 - it.x0)
            h = abs(it.y1 - it.y0)
            if w >= MIN_RULE_LEN and h < 2.0:  # full-width horizontal rule
                rules.append((it.y0 + it.y1) / 2.0)


def analyze(path):
    """Return per-page: text lines (obj), horizontal rule ys, page size."""
    pages = []
    for page in extract_pages(path, laparams=None):
        texts, rules = [], []
        _collect(page, texts, rules)
        pages.append({
            "w": page.width,
            "h": page.height,
            "texts": texts,
            "rules": sorted(rules),
        })
    return pages


def main():
    with open(os.path.join(EN, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)

    all_ok = True
    for fname in sorted(manifest):
        path = os.path.join(EN, fname)
        m = manifest[fname]
        pages = analyze(path)
        note_set = {norm(s) for s in m["note_lines"]}
        ok = True
        print("=" * 72)
        print(f"{fname}")

        # ---- 2. page count & paper size
        if len(pages) != m["pages"]:
            print(f"  [FAIL] pages: PDF has {len(pages)}, manifest says {m['pages']}")
            ok = False
        else:
            print(f"  [ OK ] pages: {len(pages)}")
        paper_ok = all(
            abs(p["w"] - m["paper"][0]) < 0.5 and abs(p["h"] - m["paper"][1]) < 0.5
            for p in pages
        )
        print(f"  [{' OK ' if paper_ok else 'FAIL'}] paper: "
              f"{m['paper'][0]}x{m['paper'][1]} pt "
              f"(PDF: {pages[0]['w']:.1f}x{pages[0]['h']:.1f})")
        ok = ok and paper_ok

        # ---- 3. 天地線 on every page (except intentional blank covers)
        cover = m.get("cover_pages", 0)
        rules_ok = True
        for i, p in enumerate(pages, 1):
            if i <= cover:
                if len(p["texts"]) == 0 and len(p["rules"]) == 0:
                    print(f"  [ OK ] page {i}: intentional blank cover "
                          f"(0 text, 0 rules)")
                else:
                    print(f"  [FAIL] page {i}: expected blank cover but found "
                          f"{len(p['texts'])} text, {len(p['rules'])} rules")
                    rules_ok = False
            elif len(p["rules"]) < 2:
                print(f"  [FAIL] page {i}: only {len(p['rules'])} full-width "
                      f"rule(s), need >= 2 (天線+地線)")
                rules_ok = False
            else:
                print(f"  [ OK ] page {i}: 天線/地線 y = {p['rules'][-1]:.0f} / "
                      f"{p['rules'][0]:.0f} (rule length 552 pt = 90.2%)")
        ok = ok and rules_ok

        # ---- 1 + 4. note lines: verbatim presence + per-page counts
        # table region for this PDF: between lowest and highest rule
        note_counts = []
        note_hits = {norm(s): False for s in m["note_lines"]}
        for i, p in enumerate(pages, 1):
            if len(p["rules"]) >= 2:
                top = p["rules"][-1]
                bot = p["rules"][0]
            else:
                top, bot = 748.0, 64.0
            count = 0
            for t in p["texts"]:
                n = norm(t.get_text())
                if n in note_hits:
                    note_hits[n] = True
                    count += 1
            note_counts.append(count)
        notes_ok = note_counts == m["note_lines_per_page"]
        print(f"  [{' OK ' if notes_ok else 'FAIL'}] note_lines_per_page: "
              f"manifest {m['note_lines_per_page']}, extracted {note_counts}")
        ok = ok and notes_ok
        missing = [s for s, hit in note_hits.items() if not hit]
        if missing:
            print(f"  [FAIL] note lines NOT found verbatim: {missing}")
            ok = False

        # ---- 1. trap rows: verbatim presence + must be in table region
        trap_ok = True
        for trap in m["trap_rows"]:
            target = norm(trap)
            found = False
            for p in pages:
                if len(p["rules"]) >= 2:
                    top, bot = p["rules"][-1], p["rules"][0]
                else:
                    top, bot = 748.0, 64.0
                for t in p["texts"]:
                    if norm(t.get_text()) == target and bot < t.y0 < top:
                        found = True
            if not found:
                print(f"  [FAIL] trap row not found as a table-region data row: {trap!r}")
                trap_ok = False
            else:
                print(f"  [ OK ] trap row (data row): {trap!r}")
        ok = ok and trap_ok

        # ---- 6. per-page extracted lines vs data_row_count
        total_rows = 0
        print("  per-page extracted text lines (raw | table-region data rows | notes):")
        for i, p in enumerate(pages, 1):
            if len(p["rules"]) >= 2:
                top, bot = p["rules"][-1], p["rules"][0]
            else:
                top, bot = 748.0, 64.0
            raw = len(p["texts"])
            rows = sum(
                1 for t in p["texts"]
                if t.x0 < 306 and bot < t.y0 < top
                and norm(t.get_text()) not in note_set
            )
            total_rows += rows
            ctag = "  (cover)" if i <= cover else ""
            print(f"    page {i}: {raw:3d} | {rows:3d} | {note_counts[i-1]}{ctag}")
        if total_rows == m["data_row_count"]:
            print(f"  [ OK ] data_row_count: {total_rows}")
        else:
            print(f"  [FAIL] data_row_count: extracted {total_rows}, "
                  f"manifest {m['data_row_count']}")
            ok = False

        all_ok = all_ok and ok

    print("=" * 72)
    print("OVERALL:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
