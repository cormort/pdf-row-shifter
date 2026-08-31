# 真實美國財報樣本（PDF 本身不入庫，`.gitignore` 的 `*.pdf` 擋著）

用 curl 直接向官方來源取得，全數 `%PDF-` 檔頭通過。

| 檔名 | 來源 | 頁數 / 紙張 |
|---|---|---|
| `apple_fy24_q4_statements.pdf` | https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf | 4 頁 / Letter（含橫向頁） |
| `nvda_10k_fy2026.pdf` | https://investor.nvidia.com/files/doc_financials/2026/q4/10K-NVDA.pdf | 93 頁 / Letter |
| `nvda_q3fy26_earnings.pdf` | https://nvidianews.nvidia.com/_gallery/download_pdf/691e34d93d633290a88deeef/ | 10 頁 / A4 |
| `frusg_2024.pdf` | https://fiscaldata.treasury.gov/static-data/published-reports/frusg/FRUSG_2024.pdf | 245 頁 / Letter |

重新下載：

```bash
cd _fixtures/real
curl -L -A "Mozilla/5.0" -o apple_fy24_q4_statements.pdf "https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf"
curl -L -A "Mozilla/5.0" -o nvda_10k_fy2026.pdf "https://investor.nvidia.com/files/doc_financials/2026/q4/10K-NVDA.pdf"
curl -L -A "Mozilla/5.0" -o nvda_q3fy26_earnings.pdf "https://nvidianews.nvidia.com/_gallery/download_pdf/691e34d93d633290a88deeef/"
curl -L -A "Mozilla/5.0" -o frusg_2024.pdf "https://fiscaldata.treasury.gov/static-data/published-reports/frusg/FRUSG_2024.pdf"
```

## 實測結果（2026-08-31）

| 檔 | `noFrameDoc` | 全寬橫線 | rows | 判定 |
|---|---|---|---|---|
| Apple FY24Q4 | **true** | 0 / 248 條線 | 129 | 無框線路徑 |
| NVDA 10-K FY26 | **true** | 1 | 3632 | 無框線路徑，93 頁全成假列 |
| NVDA FY26Q3 新聞稿 | false | 2 | 376 | 走表格路徑 |
| FRUSG 2024 | **true** | 0 | 9219 | 無框線路徑 |

四份裡三份沒有橫貫全寬的天地線——美國財報用的是欄群與合計底下的短底線，不是中文公文表那種
框起來的表格。表尾註機制的第一個條件就是 `!noFrame`，所以那三份**完全走不到註的判斷**。
