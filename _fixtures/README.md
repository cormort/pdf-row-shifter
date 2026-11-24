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
