# 英文財報／研究報告 PDF 測試樣本規格

給產生樣本的 agent 用。你的產出是**測試素材**，不是程式改動。

## 背景（你需要知道的全部）

有一個工具會讀進 PDF 表格，把「資料列」重新分頁，並且要把「表尾註」抽離出來不參與分頁。
目前它判斷表尾註的方式是看某一列開頭的字（中文的「註」、英文的 `Note:` / `Source:`）。
我們要驗證它對**英文財報與投資報告的各種註解慣例**是否判斷正確——包含該抓到的有沒有抓到，
以及**不該抓的有沒有被誤抓**。

你不需要看那個工具的程式碼，也**不要**去看 `index.html`。請純粹依「一個財務分析師讀這張表時，
哪幾行是註解、哪幾行是資料列」來寫答案。

## 產出位置

全部寫進：`/Users/hsiehminchieh/Dev/Work/pdf-row-shifter/_fixtures/en/`

- 6 個 PDF：`A.pdf` … `F.pdf`
- 1 個答案檔：`manifest.json`

**不要動這個資料夾以外的任何檔案**，特別是 `index.html`、`README.md`、`README.en.md`、`.gitignore`。
**不要執行 `git add` / `git commit` / `git push`。**

## PDF 的硬性要求（不符合就整份作廢）

1. **文字型**，不是掃描圖。文字必須能被 pdf.js 的 `getTextContent()` 抽出來。
2. **紙張 US Letter**，612 × 792 pt。
3. **每一頁都要有橫貫全寬的天線與地線**：兩條水平向量線（stroke，不是圖片、不是底線字元），
   長度至少佔頁寬 90%。天線在頁首標題下方，地線在頁面下緣附近。
4. **多頁**：每份 2–3 頁，資料列要多到會自然跨頁。
5. **等寬列距**：資料列之間行距一致（18–22pt 之間自選一個固定值）。
6. 欄位至少 2 欄：左邊是文字標籤，右邊是金額數字（靠右對齊）。
7. 字型用 Helvetica / Times-Roman 這類標準 14 種字型即可，不要嵌入 CJK。

工具鏈自選（`reportlab` 建議，可自行 `python3 -m venv` 裝在
`/Users/hsiehminchieh/Dev/Work/pdf-row-shifter/_fixtures/.venv`；也可以手寫 PDF 語法）。
**venv 不要裝進專案根目錄。**

## 六份樣本的內容

每一份都要**同時包含該抓的註和不該抓的資料列**，這是重點。

### A.pdf — 10-K 主要財務報表
- 表頭：`CONSOLIDATED STATEMENTS OF OPERATIONS`
- 地線**正下方**一行：`See accompanying notes to consolidated financial statements.`（每一頁都要有）
- 資料列裡**必須包含**這幾列（誤判陷阱）：
  - `Notes payable to related parties`
  - `Note receivable, net of current portion`
  - 至少 3 列的金額是括號負數，例如 `(1,234)`
  - 一列 `(Loss) income before income taxes`（**以左括號開頭的資料列**）

### B.pdf — 賣方研究報告的表
- 地線下方依序：
  - `(1) Includes restructuring charges of $12.4 million.`
  - `(2) Adjusted to exclude one-time items.`
  - `Source: Company filings, XYZ Research estimates.`
- 資料列裡必須包含：一列 `(1,105)` 這種括號負數在金額欄、
  一列標籤是 `(2) Segment detail` 但**它是真的資料列**（右邊有金額）——
  這是最難的一題，答案檔要誠實標記它是資料列。

### C.pdf — 法說會簡報風格，註騎在地線上
- 註的**第一行在地線上方**、其餘在地線下方（這是重點）：
  - 地線上方：`Note: 1. Figures are unaudited and stated in thousands.`
  - 地線下方：`2. Comparatives have been restated to conform with current presentation.`
  - 地線下方：`* Excludes discontinued operations.`
- 資料列正常，無陷阱。

### D.pdf — 完全沒有註（負向對照）
- 地線下方**除了頁碼之外什麼都沒有**。
- 資料列裡放 `Notes payable`、`Source of funds`、`Note 12 - Commitments` 這三列
  （**全部都是資料列**，一列都不該被當成註）。

### E.pdf — 星號與符號註
- 地線下方：
  - `* Restated.`
  - `** Preliminary, subject to audit.`
  - `† Represents non-GAAP measure.`
- 資料列裡包含一列標籤含星號但是資料列：`Revenue*` （右邊有金額）。

### F.pdf — 混合式（最接近真實 10-K 附註頁）
- 地線下方依序：
  - `(1) Amounts in thousands, except per share data.`
  - `See accompanying notes to consolidated financial statements.`
- 資料列包含 `Notes and loans payable`、以及兩列括號負數。

## manifest.json 格式

**這是答案檔，我會拿它逐字比對。字串必須與 PDF 裡實際畫出來的完全一致（含標點、大小寫、空白）。**

```json
{
  "A.pdf": {
    "paper": [612, 792],
    "pages": 3,
    "row_leading_pt": 20,
    "note_lines": [
      "See accompanying notes to consolidated financial statements."
    ],
    "note_lines_per_page": [1, 1, 1],
    "data_row_count": 42,
    "trap_rows": [
      "Notes payable to related parties",
      "Note receivable, net of current portion",
      "(Loss) income before income taxes"
    ]
  }
}
```

欄位定義：

| 欄位 | 意思 |
|---|---|
| `note_lines` | 整份文件裡**所有**應被判為註的行，逐字、依出現順序。跨頁重複出現的句子要重複列出 |
| `note_lines_per_page` | 每頁的註行數，長度等於 `pages` |
| `data_row_count` | 整份文件的資料列總數（**不含**表頭、頁碼、註） |
| `trap_rows` | 長得像註、但其實是資料列的那幾列，逐字 |

六份都要有。`D.pdf` 的 `note_lines` 是 `[]`、`note_lines_per_page` 是 `[0,0,...]`。

## 你要自己先驗過再交（缺這步就退回）

在 `_fixtures/` 下寫一個 `selfcheck.py`，對每個 PDF 檢查並印出結果：

1. 用 `pdfminer.six` 或 `pypdf` 抽出每頁文字，確認 `manifest.json` 裡的每一條
   `note_lines` 與 `trap_rows` **都真的出現在抽出的文字裡**（逐字）。
2. 確認頁數與 `pages` 相符、頁面尺寸是 612×792。
3. 印出每份 PDF 每頁抽到的文字行數，讓我對照 `data_row_count` 是否合理。

把 `selfcheck.py` 的完整輸出貼在你的回覆裡。

## 交付檢查清單

- [ ] `_fixtures/en/A.pdf` … `F.pdf` 六份，皆為文字型、Letter、每頁有全寬天地線
- [ ] `_fixtures/en/manifest.json` 六份齊全、字串與 PDF 內容逐字一致
- [ ] `_fixtures/selfcheck.py` 及其輸出
- [ ] 沒有動到 `_fixtures/` 以外的檔案
- [ ] 沒有下過任何 git 指令
