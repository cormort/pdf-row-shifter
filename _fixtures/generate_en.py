#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate English financial-report test fixtures for pdf-row-shifter.

Output (all under _fixtures/):
  en/A.pdf ... en/F.pdf   -- 6 text-layer US-Letter PDFs, each with full-width
                              top/bottom rules (天地線) on every page
  en/manifest.json        -- ground-truth answer file (verbatim strings)

Layout contract per page (612 x 792 pt):
  title baseline ........ 765   (above 天線)
  天線 (top rule) ........ 748   x=30..582 -> 552 pt = 90.2% of page width
  row 1 baseline ........ 736, rows step 20 pt (row_leading_pt = 20)
  label x=72, amount right-aligned at x=540
  地線 (bottom rule) ....  64   x=30..582
  notes below 地線 ...... 52, 42, 32 (9 pt)
  straddling note (C) ... 96    (above 地線, inside the table region)
"""
import json
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "en")
os.makedirs(OUT, exist_ok=True)

PAGE_W, PAGE_H = letter  # 612 x 792
ROW_LEAD = 20
RULE_X1, RULE_X2 = 30, 582          # 552 pt long
RULE_LEN = RULE_X2 - RULE_X1        # 552 / 612 = 90.2%
TOP_RULE_Y = 748
BOT_RULE_Y = 64
TITLE_Y = 765
FIRST_ROW_Y = 736
LABEL_X = 72
AMOUNT_RIGHT = 540
NOTE_Y0 = 52                        # first note baseline below 地線
NOTE_STEP = 10
INTABLE_NOTE_Y0 = 110               # G.pdf: notes above 地線 (last table rows)
STRADDLE_NOTE_Y = 96                # C.pdf: note first line above 地線
FONT = "Helvetica"
FONT_B = "Helvetica-Bold"


def _draw_page(c, title, rows, notes_below, notes_above=(), intable=(),
               page_number=None):
    """Draw one page. rows = [(label, amount), ...]; amount '' -> no number.
    intable: notes drawn INSIDE the table region (above 地線), as the last
    rows of the statement — the real 10-K convention (NVDA/FRUSG/Apple)."""
    c.setFont(FONT_B, 13)
    c.drawCentredString(PAGE_W / 2.0, TITLE_Y, title)
    c.setLineWidth(1)
    c.line(RULE_X1, TOP_RULE_Y, RULE_X2, TOP_RULE_Y)   # 天線
    c.line(RULE_X1, BOT_RULE_Y, RULE_X2, BOT_RULE_Y)   # 地線
    c.setFont(FONT, 10)
    y = FIRST_ROW_Y
    for label, amount in rows:
        c.drawString(LABEL_X, y, label)
        if amount:
            c.drawRightString(AMOUNT_RIGHT, y, amount)
        y -= ROW_LEAD
    c.setFont(FONT, 9)
    for i, s in enumerate(intable):                    # notes above 地線
        c.drawString(LABEL_X, INTABLE_NOTE_Y0 - i * NOTE_STEP, s)
    for s in notes_above:                              # straddling notes
        c.drawString(LABEL_X, STRADDLE_NOTE_Y, s)
    for i, s in enumerate(notes_below):                # notes under 地線
        c.drawString(LABEL_X, NOTE_Y0 - i * NOTE_STEP, s)
    if page_number is not None:
        c.setFont(FONT, 9)
        c.drawCentredString(PAGE_W / 2.0, 20, page_number)


def _build(spec, path):
    c = canvas.Canvas(path, pagesize=letter)
    for i, pg in enumerate(spec["pages"], 1):
        if pg.get("cover"):
            c.showPage()          # intentional blank cover (frame trap, like
            continue              # NVIDIA 10-K p1: 0 text, 0 rules)
        _draw_page(
            c,
            title=pg.get("title", spec["title"]),
            rows=pg["rows"],
            notes_below=pg.get("below", []),
            notes_above=pg.get("above", []),
            intable=pg.get("intable", []),
            page_number=pg.get("page_number"),
        )
        c.showPage()
    c.save()


A_NOTE = "See accompanying notes to consolidated financial statements."

# ---------------------------------------------------------------- A.pdf
A_P1 = [
    ("Revenues", "1,234,567"),
    ("Cost of revenues", "(987,654)"),
    ("Gross profit", "246,913"),
    ("Operating expenses:", ""),
    ("Selling, general and administrative", "123,456"),
    ("Research and development", "45,678"),
    ("Depreciation and amortization", "12,345"),
    ("Total operating expenses", "181,479"),
    ("Operating income (loss)", "65,434"),
    ("Interest income", "1,234"),
    ("Interest expense", "(5,678)"),
    ("Other income (expense), net", "(890)"),
    ("Notes payable to related parties", "2,345"),
    ("Note receivable, net of current portion", "4,567"),
    ("(Loss) income before income taxes", "(1,234)"),
    ("Provision for income taxes", "(2,345)"),
    ("Net income (loss)", "(12,345)"),
    ("Net loss attributable to noncontrolling interests", "123"),
    ("Net income attributable to the Company", "(12,222)"),
    ("Net income per share, basic", "(0.14)"),
    ("Net income per share, diluted", "(0.14)"),
    ("Weighted average shares outstanding, basic", "87,654,321"),
]
A_P2 = [
    ("Weighted average shares outstanding, diluted", "89,012,345"),
    ("Dividends declared per share", "0.25"),
    ("Revenue from product sales", "1,100,000"),
    ("Revenue from services", "134,567"),
    ("Total revenue", "1,234,567"),
    ("Cost of product sales", "(900,000)"),
    ("Cost of services", "(87,654)"),
    ("Total cost of sales", "(987,654)"),
    ("Gross margin, product", "18.2%"),
    ("Gross margin, services", "34.9%"),
    ("Total gross margin", "20.0%"),
    ("Selling expense", "(88,888)"),
    ("Marketing expense", "(34,567)"),
    ("General and administrative", "(45,678)"),
    ("Research and development, net", "(50,000)"),
    ("Total operating expenses", "(219,133)"),
    ("Operating margin", "6.5%"),
    ("Interest expense, net of capitalized interest", "(4,444)"),
    ("Foreign exchange gain (loss), net", "(333)"),
    ("Equity method investment income", "2,222"),
    ("Other income, net", "111"),
    ("Income before income taxes", "22,222"),
]
A_P3 = [
    ("Provision for income taxes", "(5,555)"),
    ("Net income", "16,667"),
    ("Net income attributable to noncontrolling interests", "(1,111)"),
    ("Net income attributable to the Company", "15,556"),
    ("Basic earnings per share", "0.18"),
    ("Diluted earnings per share", "0.17"),
    ("Basic weighted average shares", "87,654,321"),
    ("Diluted weighted average shares", "89,012,345"),
    ("Dividends declared", "0.25"),
    ("Comprehensive income, net of tax", "15,000"),
    ("Foreign currency translation adjustment", "(500)"),
    ("Unrealized gains on securities, net of tax", "300"),
    ("Pension liability adjustment, net of tax", "(200)"),
    ("Total comprehensive income", "14,600"),
    ("Comprehensive income attributable to the Company", "13,600"),
    ("Comprehensive income attributable to noncontrolling interests", "1,000"),
    ("Revenue, net", "1,234,567"),
    ("Costs and expenses, net", "(1,200,000)"),
    ("Other income (expense), net", "(1,234)"),
    ("Income (loss) from continuing operations", "33,333"),
    ("Income (loss) from discontinued operations, net of tax", "(2,222)"),
    ("Net income (loss)", "31,111"),
]

# ---------------------------------------------------------------- B.pdf
B_P1 = [
    ("Revenues", "1,234,567"),
    ("Cost of goods sold", "(876,543)"),
    ("Gross profit", "358,024"),
    ("Operating expenses", "(210,000)"),
    ("Operating income", "148,024"),
    ("Restructuring charges", "(1,105)"),
    ("Adjusted operating income", "149,129"),
    ("Other income, net", "3,456"),
    ("Pre-tax income", "152,585"),
    ("Income taxes", "(38,146)"),
    ("Net income", "114,439"),
    ("Adjusted EBITDA", "210,000"),
    ("Adjusted EBITDA margin", "17.0%"),
    ("Diluted EPS", "1.31"),
    ("Diluted shares outstanding", "87,654,321"),
    ("Free cash flow", "98,765"),
    ("Net debt", "250,000"),
    ("(2) Segment detail", "12,450"),
    ("Segment A revenue", "500,000"),
    ("Segment B revenue", "400,000"),
    ("Segment C revenue", "334,567"),
    ("Total segment revenue", "1,234,567"),
    ("Segment A operating income", "75,000"),
    ("Segment B operating income", "55,000"),
]
B_P2 = [
    ("Segment C operating income", "18,024"),
    ("Total segment operating income", "148,024"),
    ("Q1 2025 revenue", "280,000"),
    ("Q2 2025 revenue", "295,000"),
    ("Q3 2025 revenue", "310,000"),
    ("Q4 2025 revenue", "349,567"),
    ("FY2025 revenue", "1,234,567"),
    ("Q1 2026 revenue", "290,000"),
    ("Q2 2026 revenue", "305,000"),
    ("Q3 2026 revenue", "320,000"),
    ("Q4 2026 revenue", "330,000"),
    ("FY2026 revenue", "1,245,000"),
    ("Adjusted EPS, Q1 2026", "0.32"),
    ("Adjusted EPS, Q2 2026", "0.35"),
    ("Adjusted EPS, Q3 2026", "0.38"),
    ("Adjusted EPS, Q4 2026", "0.40"),
]

# ---------------------------------------------------------------- C.pdf
C_P1 = [
    ("Revenue", "1,234,567"),
    ("Cost of revenue", "(678,901)"),
    ("Gross profit", "555,666"),
    ("Gross margin", "45.0%"),
    ("Operating expenses", "(345,678)"),
    ("Research and development", "(123,456)"),
    ("Sales and marketing", "(150,000)"),
    ("General and administrative", "(72,222)"),
    ("Operating income", "209,988"),
    ("Operating margin", "17.0%"),
    ("Other income (expense), net", "(1,234)"),
    ("Interest expense, net", "(5,678)"),
    ("Pre-tax income", "203,076"),
    ("Income taxes", "(50,769)"),
    ("Net income", "152,307"),
    ("Net margin", "12.3%"),
    ("Diluted EPS", "1.74"),
    ("Adjusted EBITDA", "290,000"),
    ("Adjusted EBITDA margin", "23.5%"),
    ("Stock-based compensation", "(45,000)"),
    ("Depreciation and amortization", "(35,000)"),
    ("Working capital change", "(12,345)"),
    ("Capital expenditures", "(25,000)"),
    ("Free cash flow", "172,655"),
]
C_P2 = [
    ("Revenue growth, y/y", "15.2%"),
    ("Revenue growth, q/q", "4.1%"),
    ("Organic revenue growth", "12.8%"),
    ("Constant currency growth", "13.5%"),
    ("FX impact", "(0.7)%"),
    ("Customer count", "12,345"),
    ("ARPU", "88.50"),
    ("Net revenue retention", "115%"),
    ("Gross revenue retention", "92%"),
    ("Headcount", "5,678"),
    ("Cash and cash equivalents", "456,789"),
    ("Total debt", "(250,000)"),
    ("Net debt / Adjusted EBITDA", "0.9x"),
]

# ---------------------------------------------------------------- D.pdf
D_P1 = [
    ("Cash and cash equivalents", "123,456"),
    ("Short-term investments", "45,678"),
    ("Accounts receivable, net", "234,567"),
    ("Inventories", "156,789"),
    ("Prepaid expenses and other current assets", "23,456"),
    ("Total current assets", "583,946"),
    ("Property, plant and equipment, net", "345,678"),
    ("Operating lease right-of-use assets", "89,012"),
    ("Goodwill", "210,987"),
    ("Intangible assets, net", "54,321"),
    ("Deferred tax assets", "12,345"),
    ("Total non-current assets", "712,343"),
    ("Total assets", "1,296,289"),
    ("Accounts payable", "(98,765)"),
    ("Accrued expenses", "(67,890)"),
    ("Deferred revenue, current", "(34,567)"),
    ("Current portion of long-term debt", "(12,345)"),
    ("Notes payable", "(23,456)"),
    ("Total current liabilities", "(237,023)"),
    ("Long-term debt, net of current portion", "(456,789)"),
    ("Deferred revenue, non-current", "(11,111)"),
    ("Operating lease liabilities, non-current", "(76,543)"),
    ("Deferred tax liabilities", "(9,876)"),
    ("Total non-current liabilities", "(554,319)"),
    ("Total liabilities", "(791,342)"),
    ("Source of funds", "504,947"),
    ("Common stock", "1,000"),
    ("Additional paid-in capital", "300,000"),
    ("Retained earnings", "200,000"),
    ("Accumulated other comprehensive income", "3,947"),
    ("Total stockholders' equity", "504,947"),
    ("Total liabilities and equity", "1,296,289"),
]
D_P2 = [
    ("Note 12 - Commitments", "45,678"),
    ("Commitments and contingencies", "67,890"),
    ("Purchase obligations", "123,456"),
    ("Operating leases", "76,543"),
    ("Finance leases", "12,345"),
    ("Letters of credit", "5,678"),
    ("Guarantees", "4,567"),
    ("Total commitments", "290,179"),
    ("Contingencies", "9,999"),
    ("Subsequent events", "0"),
]

# ---------------------------------------------------------------- E.pdf
E_P1 = [
    ("Revenue*", "1,234,567"),
    ("Cost of revenue", "(876,543)"),
    ("Gross profit", "358,024"),
    ("Operating expenses", "(210,000)"),
    ("Operating income", "148,024"),
    ("Interest income", "1,234"),
    ("Interest expense", "(5,678)"),
    ("Other income (expense), net", "(890)"),
    ("Pre-tax income", "142,690"),
    ("Income tax expense", "(35,673)"),
    ("Net income", "107,017"),
    ("Adjusted net income", "112,000"),
    ("Adjusted diluted EPS", "1.28"),
    ("Free cash flow", "98,765"),
    ("Adjusted free cash flow", "103,000"),
    ("Net debt", "250,000"),
    ("Leverage ratio", "1.6x"),
    ("Book value per share", "12.34"),
    ("Return on equity", "14.2%"),
    ("Return on invested capital", "11.8%"),
    ("Dividend per share", "0.40"),
    ("Payout ratio", "31%"),
    ("Organic growth", "12.8%"),
    ("Same-store sales growth", "6.5%"),
]
E_P2 = [
    ("Revenue by geography: Domestic", "700,000"),
    ("Revenue by geography: International", "534,567"),
    ("Revenue by geography: EMEA", "250,000"),
    ("Revenue by geography: APAC", "284,567"),
    ("Total revenue by geography", "1,234,567"),
    ("Operating income by geography: Domestic", "95,000"),
    ("Operating income by geography: International", "53,024"),
    ("Operating income by geography: EMEA", "30,000"),
    ("Operating income by geography: APAC", "23,024"),
    ("Total operating income by geography", "148,024"),
    ("Capital expenditure: Domestic", "(15,000)"),
    ("Capital expenditure: International", "(10,000)"),
    ("Capital expenditure: EMEA", "(6,000)"),
    ("Capital expenditure: APAC", "(4,000)"),
    ("Total capital expenditure", "(35,000)"),
    ("Adjusted EBITDA reconciliation: Net income", "107,017"),
    ("Adjusted EBITDA reconciliation: D&A", "35,000"),
    ("Adjusted EBITDA reconciliation: Interest", "4,444"),
    ("Adjusted EBITDA reconciliation: Taxes", "35,673"),
    ("Adjusted EBITDA reconciliation: SBC", "27,866"),
    ("Adjusted EBITDA", "210,000"),
]

# ---------------------------------------------------------------- F.pdf
F_P1 = [
    ("Notes and loans payable", "45,678"),
    ("Current portion of long-term debt", "(12,345)"),
    ("Revolving credit facility", "100,000"),
    ("Term loan A", "75,000"),
    ("Term loan B", "125,000"),
    ("Senior notes due 2028", "200,000"),
    ("Senior notes due 2031", "150,000"),
    ("Convertible notes", "50,000"),
    ("Finance lease obligations", "12,345"),
    ("Total debt", "745,678"),
    ("Less: deferred financing costs, net", "(5,678)"),
    ("Total debt, net", "740,000"),
    ("Fair value of debt", "742,000"),
    ("Weighted average interest rate", "4.6%"),
    ("Debt issuance costs amortization", "1,234"),
    ("Interest expense, net", "(1,234)"),
    ("Interest income", "(456)"),
    ("Net interest expense", "(778)"),
    ("Debt-to-equity ratio", "0.9x"),
    ("Interest coverage ratio", "7.4x"),
    ("Fixed charge coverage ratio", "5.2x"),
    ("Debt service coverage ratio", "3.1x"),
    ("Cash interest payments", "(28,000)"),
    ("Non-cash interest expense", "(3,000)"),
]
F_P2 = [
    ("Short-term investments", "23,456"),
    ("Long-term investments", "45,678"),
    ("Equity method investments", "12,345"),
    ("Total investments", "81,479"),
    ("Unrealized gains (losses), net", "(1,105)"),
    ("Realized gains (losses), net", "2,345"),
    ("Investment income", "5,678"),
    ("Net investment income", "6,918"),
    ("Impairment losses", "(1,234)"),
    ("Other-than-temporary impairments", "(456)"),
    ("Total other income (expense), net", "5,228"),
    ("Commitments and contingencies", "0"),
    ("Off-balance sheet arrangements", "0"),
    ("Variable interest entities", "0"),
    ("Guarantees of third-party obligations", "0"),
    ("Environmental liabilities", "(1,000)"),
]

# ---------------------------------------------------------------- G.pdf
# Real-world footnote conventions (2026-08-31, from downloaded real PDFs):
#   - notes sit INSIDE the table region, above the 地線, as the last rows
#     (NVDA 10-K / FRUSG / Apple FY24 Q4 actual placement)
#   - styles: "See accompanying Notes..." (capital N, See-prefixed — the
#     tool's NOTE_RE misses it), numbered (1)(2), lettered (c), star (*)
#   - page 1 is a BLANK COVER (0 text, 0 rules) replicating the NVIDIA 10-K
#     p1 frame trap (getFrame finds nothing on page 1 -> whole doc fake table)
# Note strings are verbatim real ones where possible: NVDA 10-K p63 EPS
# footnotes, NVDA 10-K p51 boilerplate, FRUSG p70 star footnote, Apple FY24
# Q4 p4 "(c)" footnote (marker+text fused into one line; real doc has the
# marker in a separate column).
G_SEE = "See accompanying Notes to the Consolidated Financial Statements."
G_P1 = [
    ("Revenue", "130,497"),
    ("Cost of revenue", "(37,544)"),
    ("Gross profit", "92,953"),
    ("Research and development", "(12,987)"),
    ("Sales and marketing", "(6,771)"),
    ("General and administrative", "(3,410)"),
    ("Total operating expenses", "(23,168)"),
    ("Operating income", "69,785"),
    ("Interest and other income (expense), net", "3,259"),
    ("Income before income taxes", "73,044"),
    ("Provision for income taxes", "(10,567)"),
    ("Net income", "62,477"),
    ("Net income per share, basic", "2.50"),
    ("Net income per share, diluted", "2.44"),
    ("Weighted average shares used in per share computation, basic", "24,988"),
    ("Weighted average shares used in per share computation, diluted", "25,577"),
    ("Cash dividends declared per share", "0.02"),
    ("Other comprehensive income (loss), net of tax", "(243)"),
    ("Total comprehensive income", "62,234"),
]
G_P2 = [
    ("Cash and cash equivalents", "7,843"),
    ("Marketable securities", "24,740"),
    ("Accounts receivable, net", "16,236"),
    ("Inventories", "10,204"),
    ("Prepaid expenses and other current assets", "3,463"),
    ("Total current assets", "62,486"),
    ("Property and equipment, net", "5,211"),
    ("Operating lease assets", "4,092"),
    ("Goodwill", "4,583"),
    ("Intangible assets, net", "1,476"),
    ("Other long-term assets", "7,554"),
    ("Total assets", "85,402"),
    ("Accounts payable", "3,115"),
    ("Accrued and other current liabilities", "11,879"),
    ("Short-term debt", "0"),
    ("Notes payable", "1,250"),
    ("Total current liabilities", "16,244"),
    ("Long-term debt", "8,844"),
    ("Operating lease liabilities", "4,663"),
    ("Other long-term liabilities", "3,972"),
    ("Total liabilities", "33,723"),
    ("Total stockholders' equity", "51,679"),
    ("Total liabilities and stockholders' equity", "85,402"),
]
G_NOTES_P1 = [
    "(1) Net income divided by basic weighted average shares.",
    "(2) Net income divided by diluted weighted average shares.",
    "(c) Represents the per-share impact of the non-GAAP adjustments to net income.",
    G_SEE,
]
G_NOTES_P2 = [
    "* Certain amounts differ from prior year reported amounts due to a change "
    "in presentation (see Financial Statement Note 1.W).",
    G_SEE,
]

SPECS = [
    {
        "file": "A.pdf",
        "title": "CONSOLIDATED STATEMENTS OF OPERATIONS",
        "pages": [
            {"rows": A_P1, "below": [A_NOTE]},
            {"rows": A_P2, "below": [A_NOTE]},
            {"rows": A_P3, "below": [A_NOTE]},
        ],
        "note_lines": [A_NOTE, A_NOTE, A_NOTE],
        "trap_rows": [
            "Notes payable to related parties",
            "Note receivable, net of current portion",
            "(Loss) income before income taxes",
        ],
    },
    {
        "file": "B.pdf",
        "title": "XYZ RESEARCH - INDUSTRY UPDATE",
        "pages": [
            {"rows": B_P1, "below": []},
            {
                "rows": B_P2,
                "below": [
                    "(1) Includes restructuring charges of $12.4 million.",
                    "(2) Adjusted to exclude one-time items.",
                    "Source: Company filings, XYZ Research estimates.",
                ],
            },
        ],
        "note_lines": [
            "(1) Includes restructuring charges of $12.4 million.",
            "(2) Adjusted to exclude one-time items.",
            "Source: Company filings, XYZ Research estimates.",
        ],
        "trap_rows": ["(2) Segment detail"],
    },
    {
        "file": "C.pdf",
        "title": "Q2 FY2026 EARNINGS REVIEW",
        "pages": [
            {"rows": C_P1, "below": []},
            {
                "rows": C_P2,
                "above": ["Note: 1. Figures are unaudited and stated in thousands."],
                "below": [
                    "2. Comparatives have been restated to conform with current presentation.",
                    "* Excludes discontinued operations.",
                ],
            },
        ],
        "note_lines": [
            "Note: 1. Figures are unaudited and stated in thousands.",
            "2. Comparatives have been restated to conform with current presentation.",
            "* Excludes discontinued operations.",
        ],
        "trap_rows": [],
    },
    {
        "file": "D.pdf",
        "title": "BALANCE SHEET SUMMARY",
        "pages": [
            {"rows": D_P1, "below": [], "page_number": "Page 1"},
            {"rows": D_P2, "below": [], "page_number": "Page 2"},
        ],
        "note_lines": [],
        "trap_rows": [
            "Notes payable",
            "Source of funds",
            "Note 12 - Commitments",
        ],
    },
    {
        "file": "E.pdf",
        "title": "SUPPLEMENTARY FINANCIAL DATA",
        "pages": [
            {"rows": E_P1, "below": []},
            {
                "rows": E_P2,
                "below": [
                    "* Restated.",
                    "** Preliminary, subject to audit.",
                    "\u2020 Represents non-GAAP measure.",
                ],
            },
        ],
        "note_lines": [
            "* Restated.",
            "** Preliminary, subject to audit.",
            "\u2020 Represents non-GAAP measure.",
        ],
        "trap_rows": ["Revenue*"],
    },
    {
        "file": "F.pdf",
        "title": "NOTES TO CONSOLIDATED FINANCIAL STATEMENTS",
        "pages": [
            {"rows": F_P1, "below": []},
            {
                "rows": F_P2,
                "below": [
                    "(1) Amounts in thousands, except per share data.",
                    "See accompanying notes to consolidated financial statements.",
                ],
            },
        ],
        "note_lines": [
            "(1) Amounts in thousands, except per share data.",
            "See accompanying notes to consolidated financial statements.",
        ],
        "trap_rows": ["Notes and loans payable"],
    },
    {
        "file": "G.pdf",
        "title": "CONSOLIDATED STATEMENTS OF OPERATIONS",
        "pages": [
            {"cover": True},
            {"title": "CONSOLIDATED STATEMENTS OF OPERATIONS",
             "rows": G_P1, "intable": G_NOTES_P1},
            {"title": "CONSOLIDATED BALANCE SHEETS",
             "rows": G_P2, "intable": G_NOTES_P2},
        ],
        "note_lines": G_NOTES_P1 + G_NOTES_P2,
        "trap_rows": ["Notes payable"],
        "cover_pages": 1,
    },
]


def main():
    manifest = {}
    for spec in SPECS:
        path = os.path.join(OUT, spec["file"])
        _build(spec, path)
        per_page = [
            len(pg.get("above", [])) + len(pg.get("below", []))
            + len(pg.get("intable", []))
            for pg in spec["pages"]
        ]
        entry = {
            "paper": [PAGE_W, PAGE_H],
            "pages": len(spec["pages"]),
            "row_leading_pt": ROW_LEAD,
            "note_lines": spec["note_lines"],
            "note_lines_per_page": per_page,
            "data_row_count": sum(len(pg.get("rows", [])) for pg in spec["pages"]),
            "trap_rows": spec["trap_rows"],
        }
        if spec.get("cover_pages"):          # extension: intentional blank cover
            entry["cover_pages"] = spec["cover_pages"]
        manifest[spec["file"]] = entry
        print(f"wrote {spec['file']}: {len(spec['pages'])} pages, "
              f"{entry['data_row_count']} data rows, "
              f"notes per page {per_page}")
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote manifest.json")


if __name__ == "__main__":
    main()
