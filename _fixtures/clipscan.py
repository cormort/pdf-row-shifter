#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
找出「畫在頁面外、被裁切掉」的字。

原檔有時把一整句畫在對開表的左半頁、靠頁面邊界把右邊裁掉（跨折線的表尾註
就是這樣）。pdf.js 抽字不吃裁切，那幾截看不見的字會留下來，勾「對開表」
併版時正好疊在右半頁自己的字上。index.html 在抽字後把它們丟掉
（`r.filter(s => s.x + s.w <= pageW + 1)`）。

這支是用來找素材與回歸的：掃一批 PDF，列出每個 xMax 超出頁寬的字。
命中的檔案就是會觸發那條路徑的檔；掃出 0 表示這份檔驗不到那個修正。

需要 poppler 的 pdftotext（`brew install poppler`）。

  python3 _fixtures/clipscan.py a.pdf b.pdf ...
  find ~/somewhere -name '*.pdf' -print0 | xargs -0 python3 _fixtures/clipscan.py

只印命中的檔；-v 連 0 的也印。離開碼 1 代表有命中。

實測命中（2026-11-24）：
  03-參考-OF-06-固資成本效益.pdf      p27  3 字（械及設／大樓新／總醫院）
  農業特別收入基金115年度預算案.pdf    p70  2 字（財目的之長期投／里山林業鐵路及）
兩份都是對開表的表尾註橫跨折線。多節文件（決算書、計畫報告書）也會命中，
那是目次的 `………` 點線溢出，不是這個工具的適用範圍。
"""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/1999/xhtml}"
TOL = 1.0  # pt：pdftotext 的 xMax 有零點幾 pt 的抖動


def scan(path):
    """回傳 (頁數, [(頁碼, xMin, xMax, 頁寬, 文字), ...])，無法解析則丟 ValueError。"""
    out = subprocess.run(
        ["pdftotext", "-bbox", "-q", path, "-"],
        capture_output=True, timeout=300,
    ).stdout.decode("utf-8", "replace")
    try:
        root = ET.fromstring(out)
    except ET.ParseError as e:
        raise ValueError(str(e))
    hits, pages = [], 0
    for pg in root.iter(NS + "page"):
        pages += 1
        w = float(pg.get("width"))
        for word in pg.iter(NS + "word"):
            x1 = float(word.get("xMax"))
            if x1 > w + TOL:
                hits.append((pages, float(word.get("xMin")), x1, w, word.text or ""))
    return pages, hits


def main(argv):
    verbose = "-v" in argv
    paths = [a for a in argv if a != "-v"]
    if not paths:
        sys.exit("用法：python3 _fixtures/clipscan.py [-v] a.pdf b.pdf …")
    found = False
    for p in paths:
        name = os.path.basename(p)
        try:
            pages, hits = scan(p)
        except Exception as e:  # 壞檔、加密、pdftotext 逾時
            print(f"ERR  {name}: {str(e)[:60]}")
            continue
        if hits:
            found = True
            print(f"*** {name}  pages={pages} clipped={len(hits)}")
            for pg, x0, x1, w, t in hits[:10]:
                print(f"      p{pg}  x {x0:.1f}→{x1:.1f} > {w:.1f}  {t[:16]}")
            if len(hits) > 10:
                print(f"      …另外 {len(hits) - 10} 個")
        elif verbose:
            print(f"    {name}  pages={pages} clipped=0")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
