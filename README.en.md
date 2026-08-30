# PDF Row Repagination

*[中文說明](README.md)*

Adjust where a PDF table's page breaks fall, straight in the browser, without re-laying-out the
original document. A single HTML file — open it and it works.

**Live version**: https://cormort.github.io/pdf-row-shifter/

The interface ships in Traditional Chinese and English; press **EN / 中文** in the toolbar to switch.
The choice is remembered in `localStorage`.

## Features

- **Start screen**: a full-page drop zone — drag a PDF in, or click to pick a file. A failed load
  returns here and states why (not a PDF, corrupt file, no data rows found), so the error message is
  where you already are. Nothing is uploaded; everything runs in the local browser.

- **Original layout preserved**: text and rules are extracted with pdf.js and absolutely positioned
  at their original coordinates — top/bottom rules, column rules and headers never move.
- **Repagination**: `↓ Push last row down` / `↑ Pull first row up`, or drag any row to a new position.
- **Groups**: click a start row, Shift-click an end row, group them, and they move together and are
  never split by a page break (for project names that wrap across lines).
- **Automatic leading**: rows on every page but the last are spread evenly down to the bottom of the
  table body, so removing or inserting rows never leaves an odd gap at the foot; when overfull they
  compress proportionally and never cross the bottom rule.
- **Spreads**: tick it and odd pages (left half) plus even pages (right half) are edited as one
  layout, then split back into two A4 sheets at print time, with page numbers renumbered per side.
- **Footnotes**: detected and lifted out automatically, so they never take part in pagination as data
  rows. The block on the source file's last page follows the end of the table and is drawn on the
  last page; notes on other pages stay where they are on their own page. "Note offset" sets its
  distance from the bottom rule (the source value is the default; negative when the note sits on the
  rule), and the whole block moves together at its original leading.
- **Re-wrap notes**: joins the footnote block and re-breaks the lines — each item number (`1.` `2.`)
  becomes its own entry, continuation lines align after the number, and text reaching the right edge
  of a half-page continues on the next half-page. Use it after editing the text.
- **Sink totals to bottom rule**: when the last page is not full, the trailing run of total rows sinks
  as a block onto the bottom rule and the gap is left in the middle; every other row keeps its
  position and leading (unlike "even row height", which stretches the whole page).
- **In-place editing**: double-click any cell to edit, Enter to keep, Esc to discard.
- **Free edit**: no rows, no pagination — the whole document laid out flat, with text boxes and lines
  you can drag, resize and restyle. Ticking it **takes over the layout currently on screen** (page
  breaks, row heights and notes are already accounted for) rather than re-reading the source, so the
  workflow "get the pagination right → go into free edit to touch up → print" works. "Save" writes
  the result to `.json`; drop it back in to keep editing — the `.json` carries both text and lines,
  so the original PDF is not needed.
- **Align**: ⌥ (Option) click to select cells, then left / centre / right / distribute horizontally /
  centre between column rules.
- **Undo / Redo**: ⌘Z, ⇧⌘Z (Ctrl+Z, Ctrl+Shift+Z on Windows). The key labels in the interface switch
  by platform automatically.
- **Faithful reproduction**: the source file's bold, font family (Chinese in a gothic face, numbers in
  Times) and rule widths are kept; text is positioned from a measured baseline and corrected against
  the source widths, so it never runs over a column rule.
- **Output**: the browser's "Print / Save as PDF", with the paper size taken from the source PDF and
  no margins.

## Platforms

Chrome / Edge on macOS and Windows. Windows usually already has the Microsoft JhengHei and Times New
Roman these official forms were set in, so reproduction is closer; if the machine lacks the fonts, the
program measures the actual glyph widths and corrects for them — the layout (column rules,
pagination, baselines) still lines up, only the letterforms differ.

## Rule detection: the conditions under which lines come out right

Rules are reconstructed by following the CTM through pdf.js's operator list by hand. This was verified
against 13 real official forms (rasterising each page at 4× , scanning out dark full-width bands as
ground truth, then comparing every extracted line's position / length / thickness). All of the
following must hold:

| Condition | Explanation | Measured |
|---|---|---|
| The line is a horizontal / vertical `lineTo` or a flat rectangle | Diagonals and curves are discarded | 0 diagonals across 13 files |
| The line width is read correctly | With no `setLineWidth`, use the PDF spec default of **1.0**; an explicit `w 0` is a hairline and only that counts as 0.5 | see below |
| Line width is saved and restored with `q`/`Q` | Line width is part of the graphics state; saving only the CTM leaks the inner width outward | fixed |
| Keep only lengths > 2pt | Filters out marker dots | 0 lines wrongly dropped |
| A rectangle counts as a line only if its short side is ≤ 2pt | Both sides > 2 means a filled block, discarded | 34 filled blocks dropped (44×17, 143×16), all fills |
| Merge only when thicknesses touch / overlap and the lengths intersect | Two touching 1pt lines merge into one 2pt line | assumes the width is correct |
| A spanning line must cover 90% of the table width | Used to fix the top/bottom rules and the header cut | held for all 13 files; the fallback was never used |

**Rules are per page, not one set for the whole document**: originally only the first page's set was
read and the same coordinates drawn on every page. Open a spread in single-page mode and the two
halves' column rules are simply different (`OF-08-基金`: left half 254/368/473/577, right half
135/240/345/450), so all of the right half's text landed in the wrong cells. Rules are now grouped by
the "x positions of the long verticals crossing the table body"; pages in the same group share one
set and each page takes its own:

- An ordinary continuous table has only one fingerprint → everything shares the first page's set →
  behaviour completely unchanged
- The fingerprint takes only long verticals, deduplicated and sorted: `固資成本效益` has short
  in-cell separators on every row and a different count per page, so using every vertical as the
  fingerprint would produce one set per page and the source's 783–788 jitter in the bottom rule would
  hop across all 28 pages
- With an odd page count in spread mode (`長債`, 3 pages), the last spread only has source
  rules on its left half; a half with no rules falls back to the first spread, otherwise that sheet
  would come out blank

"Centre between column rules" now uses that page's rules too. 13 files × single-page/spread = 26
page-by-page comparisons (a full coordinate fingerprint per line): in spread mode 12/13 files
identical; in single-page mode the even pages of 6 spreads were corrected and 4 files were identical.

**A trap hit along the way**: some files (e.g. `03-參考-OF-01-主要營運`) contain no
`setLineWidth` at all. Treating the default width as 0.5 means the thickness ranges never touch during
merging, so a 2pt top/bottom rule splits into two 1pt lines, `spanning()` emits duplicate y values
(89 and 90, 800 and 801), and the table body's lower bound ends up 1pt off. With the default at 1.0,
line positions and thicknesses for all 13 files match the rasterised ground truth.

## Row splitting: Chinese and numeric baselines in one row are not level

In a PDF, the Chinese (JhengHei) and the numbers (Times) in one row are often several points apart;
`03-參考-OF-03-用人費用` measures **3.26pt** with the Chinese lower. The original fixed
3pt split threshold cut one row into two on such files: the median row height collapsed from 22pt to
3.3pt and the whole table was crushed against the top of the page with rows overprinting each other.

The threshold became **`max(3pt, 0.5 × font size)`**: half a font size is far less than the leading
(which is at least one font size), so it still separates real line breaks while re-joining the Chinese
and numbers of one row. The original baseline offset within a row is preserved and scales
proportionally as rows compress. Measured across 13 files:

- `用人費用`: 58 rows / 3.3pt leading → **29 rows / 22pt leading**
- `OF-08-基金`: 42 rows → **25 rows / 25pt leading**
- Scattered mis-splits in `長債`, `綜計-OF-01` and `員工人數` were fixed too; all other
  files were unchanged.

What was verified (13 files × single-page/spread): row counts and leading, **text-overlap detection**
(text blocks on different rows must not overlap vertically where they intersect horizontally), and
**font reproduction** (the bold and serif glyph counts must exactly match the source's embedded
fonts). Bold / serif matched 10/10 exactly; overlap was zero in 18/20 — the two non-zero cases force
"spread" on a continuation-style PDF, which does not apply in the first place.

## Footnotes: the bottom rule cannot separate them

Footnotes often **straddle the bottom rule** — the first line or two above it, the continuation below.
Judging by the rule alone leaves the lines above it in the table body as data rows while the ones
below move to the last page, tearing a large gap in between (`03-參考-OF-05-固資來源`
shows it most clearly).

The rule became content-anchored: on a given page, a line starting with 註／附註／說明 ("note",
"footnote", "explanation") — restricted to the lower part of the page, `y > page height × 0.6` — starts
a footnote block that runs to the foot of the page. Across all 13 files such a line is always that
page's last block with no data rows after it, so no data is swallowed.

**Why not a global y band**: the notes' y positions look fixed, but the note bands of
`OF-06-固資成本效益` (notes start at 712.8) and `OF-07-長債` (690) contain hundreds
of genuine data rows, and a global cut would delete them too. The anchor has to be judged per page.

**The bottom rule must be measured per page**: when the last page is not full, source files often pull
the bottom rule up to make room for the notes below it (`03-參考表-01-OF-08-基金-1150812`: 736.5 on
the last page, 800.5 on the first). Judging by the first page's rule alone puts the whole note block
"above" the bottom rule, recoverable only through the 註 anchor — and in single-page mode the half
without the word 註 stays in the data rows entirely. Each page now measures its own bottom rule (only
accepting one higher than the first page's; pages with no full-width line keep the first page's value,
so it is never worse than before). The layout still uses the first page's `bottomY` throughout and
draws the same coordinates on every page. 26 comparisons (13 files × single-page/spread): 24
identical; in `OF-06-固資成本效益` (single-page 839→834 rows) and both versions of
`OF-08-基金` (single-page 97→94 rows), 8 note continuation lines moved from data rows back into the
notes, and no data row was swallowed.

**Notes stay on their own page**: opening a spread in single-page mode leaves the two halves' notes as
the left and right halves of the same sentences, with different content, so collecting them all into
one block on the last page piles them on top of each other (`用人費用`,
`固資來源`, `固資成本效益` and `OF-08-基金` all do this). Notes now follow their own
page; only the block on the source's last page is the table's footnote and follows the end of the
table, and "note offset" moves only that block. The layout's lower bound on a page with notes is
pulled up above them too (previously only on the last page), so rows cannot ride over them. Across 26
comparisons the row counts were entirely unchanged with no text overlap anywhere, and 6 corrections
(all in single-page mode): the front-half notes of `用人費用`, `固資來源`,
`固資成本效益` ×2 and `OF-08-基金` ×2 are no longer moved to the last page. One behaviour
change: `綜計-OF-01`'s note is on page 1 of the source (9 pages total) and now stays on page 1
instead of moving to the last page.

**The bottom rule is pulled up per page, as the source does**: the rule is raised to make room for the
notes below it, so drawing the first page's rule on every page boxes the notes inside the table
(`固資成本效益`: notes 82pt above the bottom rule, `OF-08-基金`: 62pt). Each page now draws its
own, with the ends of the verticals shortened to match. Three conditions must all hold, otherwise
nothing changes:

| Condition | What it blocks |
|---|---|
| The rule moves up by more than half a row height | `長債`'s last-page rule is only 1pt above the first page's (a line merged from two 1pt strokes, whose centre drifts), and its notes were already inside the frame |
| The whole note block falls below the new rule | With notes above it, raising the rule only runs the rule through the middle of them |
| The page's rows still fit at the minimum row height | The user has pushed rows in — `OF-08-基金`'s last page at 43 rows sends the rule back to 801, and undo pulls it back to 737 |

Raising the rule is **all or nothing** — half-raised looks worse than not raised. The decision uses a
trial re-layout after raising, not "how much is left after laying out at the original leading": the
notes push rows up anyway, so judging at the original leading falsely reports that they do not fit
(pages 27 and 28 of `固資成本效益` in single-page mode did exactly this, one raised and one
not, which read as two different tables).

26 page-by-page comparisons (line positions / row text bottoms / note tops): 22 entirely unchanged, 4
expected changes, all in single-page mode — page 3 of both `OF-08-基金` versions (799.5 → 735.8) and
pages 27–28 of both `固資成本效益` files (786 → 702), with the notes fully below the rule and
the rows fully above it. Zero differences in spread mode.

The last page's layout lower bound comes from a single `botLimit`: the bottom rule by default, backed
off by one original row height if the notes ride above the rule. Even row height, last-page original
leading and sink-totals-to-bottom-rule all share that one bound and cannot fight each other; with the
notes below the rule, nothing backs off.

26 verifications: no 註 line left among the data, both halves of every spread carrying the same rows,
and the last row within bounds under all three layout modes; files without notes are entirely
unchanged in row count and layout.

## Re-wrapping notes: the line breaks are baked into the source

A note is a run of absolutely positioned fragments whose line breaks came from the source file, so
after you double-click and edit the text, the following text does not reflow — it overlaps the next
fragment or leaves a hole. `Re-wrap notes` joins the whole block and refills the lines:

- **Split on item numbers**: `1.` `2.` are separate fragments in the source, used both to split the
  items and to pick up the two indents ("number column" and "body column")
- **Flow across pages**: a spread's note is one line running across both sheets by design, so text
  reaching the right edge of a half-page continues on the next half-page
- **Numbers are not split**: a run like `235,229` is one token; only Chinese breaks per character
- **Width measurement**: measured with a hidden `.seg` whose font and fallback match the screen, and
  removed from the DOM immediately after — an element parked off-layout still counts toward the layout
  width, and Chrome's print would shrink the whole document to "fit width"

Two traps found in testing: **not every note spans both pages** (`長債`'s note occupies only
the left half, and spreading it to two page widths crushes 8 lines into 4), so the source is inspected
for how many half-pages the note actually reaches; and **some notes are wider than the table**
(`固資成本效益` reaches 604 while the rules stop at 577), so the right edge is the greater of
the rule position and the original note width, otherwise the text is squeezed and gains a line for
nothing.

8 files with notes × single-page/spread = 16 runs: text identical character for character, line counts
unchanged, no overflow past the right edge, and "0 glyphs clipped by rules" after re-wrapping. Opening
a spread in single-page mode is blocked — each note there is only the left or right half of a
sentence, and joining them is gibberish.

**The cost**: re-wrapped text uses local font widths rather than the source's `data-w`, so line ends
sit slightly differently from the source (`註：1.` measured about 1.3pt out), and results differ
slightly between operating systems. Notes you do not re-wrap are entirely unaffected.

## Free edit: the two modes have different data structures

Normal mode is `rows` / `units` / `breaks` (rows split, pages split); free edit is `fpages[]` (text
boxes and lines flattened per page). Neither can reuse the other, so switching modes used to re-read
the source file — and the pagination and row heights you had set were thrown away.

It now **takes over the layout already drawn on screen** when entering free edit: it reads the DOM,
where every `.seg`'s `left` / `top` is already in points — what you see is what you get, with no need
to redo `render()`'s arithmetic (row height, translation, centring). Table-body text is nested in a
`.row` with a `top` relative to the row, so the row's own position is added; `top` is the top of the
glyph box, so `baseOff` is added back to make it a baseline when writing to `fpages`. In spread mode a
half-page is one sheet, so flattening gives exactly what prints.

Measured (same file, with pagination and note offset changed): after entering free edit **every text
segment matches in position and content, segment by segment**; 2 of 36 lines differ by 1px in end
extension — a line's thickness axis snaps to whole pixels, and a half-page's coordinates restart from
`x+595` (595pt = 793.33px, not an integer), so rounding lands one step apart. Normal mode is entirely
unchanged across 26 page-by-page comparisons.

**Leaving free edit still re-reads the source** (with the existing confirmation) — free edit is meant
to be the last step before printing. A document restored from `.json` has no original PDF, so it is
blocked with a message.

## Limitations

- Needs a network connection (pdf.js loads from a CDN).
- After free editing you cannot switch back to normal mode and keep pushing rows (it re-reads the
  source). Use "Save" to keep the work as `.json`.
- Text-based PDFs only; scans have no text layer.
- Editing works on the PDF's own text fragments; a title with letter-spacing is one fragment per
  character in the source and has to be edited character by character.
- Rule detection assumes the table has full-width top and bottom rules; unusual layouts may need
  adjustment.
- When one file holds several tables with different columns (e.g. `綜計-OF-01` contains 4), rules
  are drawn per page, but **rows cannot be pushed across tables** — text x positions do not follow the
  new table, so a pushed row lands in the wrong columns. Split out a single table first.
- Outside spread mode, a footnote continuation landing on the half without the word 註 (e.g. the right
  half of `OF-05-固資來源`) stays among the data rows. Spread mode does not have this
  problem — the halves merge by y, so the continuation and "註：" are on the same row.

## Considered and not done

The following three were evaluated and deliberately left alone; they are recorded here so the
reasoning does not have to be derived again.

**Page height cannot be locked, because height is not a per-page variable.** Every page but the last
ends on the same `fillY` — pages with more rows get smaller row heights, pages with fewer get larger,
but the bottoms align. And `fillY` is computed globally: `bodyTop + (rows on the fullest page - 1) ×
original leading`. Push any page fuller than before and `fillY` moves down, taking **every**
non-final page's row height with it, locked pages included. 🔒 locks page breaks only, not heights.
Making it stable means moving `fillY` out of `relayout()` and computing it once at load (2–3 lines,
remembering to shift it when `padT`/`padB` change), at the cost that a page later packed fuller than
any page in the source compresses to the minimum row height and crosses the rule on its own, instead
of the whole document giving way together as it does now. Recording a separate `fillY` per page would
break the "all pages end level" property of the layout.

**Dragging reorders; it does not move between pages.** `breaks` stores unit indices, and dragging only
changes the order of the `units` array, so a cross-page drag always squeezes one row back. "Push it
across without the next page sending one back" = reorder, then move that break by ±1 (the existing
`move(pi,±1)` logic, about 3 lines; better hung off a modifier key than made the default feel).
For now the row tooltip explains the behaviour and points at the push/pull buttons between pages.

**The last page's bottom rule is not adjustable by hand.** The rule is a `frame` line read from the
source; the last page auto-raises to the position measured in the source (see above), but "margin
bottom" only shrinks the layout's lower bound and "note offset" only shifts the notes — neither
touches the line itself. If the need is "the last page is not full and there is too much white space
below", the right answer is a snap-to checkbox (move the rule to the last row + bottom margin, with
`bodyBot` following, mutually exclusive with "sink totals to bottom rule") rather than a point spinner
— users cannot work that number out, and it would fight the four mechanisms sharing one lower bound
(`bodyBot` / `botLimit` / notes / sink totals).

MIT
