# _fixtures

測試素材與檢查腳本。PDF 本身不入庫（`.gitignore` 的 `*.pdf` 擋著）。

| 檔 | 做什麼 |
|---|---|
| `SPEC.md` | 給產生英文樣本的 agent 的規格書 |
| `en/` | 英文財報樣本 `A.pdf`…`G.pdf` 與答案檔 `manifest.json` |
| `real/` | 真實美國財報（來源與重新下載指令見 `real/SOURCES.md`） |
| `generate_en.py` | 產生 `en/` 那批樣本 |
| `selfcheck.py` | 對 `en/` 逐份跑 7 項檢查，全過才 `OVERALL: PASS` |
| `clipscan.py` | 單獨使用：掃一批 PDF，找畫在頁面外被裁切的字 |
| `baseline-check.js` | 在瀏覽器裡量每份 PDF 最後一列的基線有沒有越過地線 |
| `sink-before.jpg` / `sink-after.jpg` | 「合計沉到地線下面」那個 bug 的修正前後對照截圖 |

## 怎麼跑

```bash
_fixtures/.venv/bin/python _fixtures/selfcheck.py
```

需要：

- **Python 套件 `pdfminer.six`**（`reportlab` 則是 `generate_en.py` 要用的）。
  裝在 `_fixtures/.venv/`，所以用上面那行、不是系統的 `python3`。
  重建：`python3 -m venv _fixtures/.venv && _fixtures/.venv/bin/pip install pdfminer.six reportlab`
- **poppler 的 `pdftotext`**（`brew install poppler`）——`clipscan.py` 靠它拿每個字的
  bounding box，`selfcheck.py` 的第 7 項也是走這條。沒裝的話第 7 項印 `[SKIP]`，
  其餘 6 項照跑。

`clipscan.py` 也可以單獨對任何一批 PDF 用：

```bash
find ~/somewhere -name '*.pdf' -print0 | xargs -0 python3 _fixtures/clipscan.py
```

只印命中的檔（`-v` 連 0 的也印），命中時離開碼 1。它不需要 venv，只要 `pdftotext`。

## baseline-check.js：量列有沒有越過地線

排版改動（列高、合計貼地線、平均列高、表尾註收線）最容易壞在「最後一列掉到地線下面壓住註」。
這支腳本把一個資料夾裡的 PDF 逐份載進 `index.html`、開「平均列高：全部頁面」，再量
**最後一列的真基線 − 地線**。負值＝在地線上方（正常），正值＝越線。

```bash
python3 -m http.server 8731
```

瀏覽器開 `http://localhost:8731/index.html`，把 `_fixtures/baseline-check.js` 整個貼進 console，然後：

```js
await check('/samples/')        // 或 '/_fixtures/en/'、'/_fixtures/real/'
```

結果用 `console.table` 印出每份的「列數 + 最大越線 pt」。只要有正值就是有頁越線，再用那份檔
逐頁看 `scanBaselines()` 的陣列找是哪一頁。沒有相依，也不用 venv，只要 Python 的 `http.server`
（`file://` 不行：腳本要 `fetch` PDF）。

**一定要量基線，不要量 `getBoundingClientRect().bottom`**：`.seg` 的字框下緣在基線下方約 0.2 個
字級（Times 這類 ascent < 1em 的字型），`.row` 盒子更是往下留 0.2 個列高，兩者都會印出 1～3pt 的
假性越線，也會蓋掉真的。理由見根目錄 README 的「表尾註：地線切不開它」。

大檔要給它時間：`frusg_2024.pdf`（4733 列／245 頁）預設的 5 秒載入可能不夠，
用 `await check('/_fixtures/real/', { waitLoad: 12000 })`。

### 對照截圖

`sink-before.jpg`／`sink-after.jpg` 是「合計貼地線 + 文字置中」那個 bug 的修正前後，
同一份 `03-參考表-01-OF-02-繳庫-1150812.pdf`（7 列、列高被拉到 94.7pt）、同樣開「平均列高：全部頁面」：
修正前合計整列落在地線那條紅虛線**下方**（表尾註的位置），修正後回到線上方、貼著地線。
PDF 本身不入庫，檔在主計總處 OneDrive 的「三校／3-綜計參考表」。
數字量法見 `baseline-check.js`；這兩張只是給人眼確認版面長相用的。
