// 驗收：每份 PDF 開「平均列高：全部頁面」後，量最後一列的「真基線 − 地線」。
// 負值＝在地線上方（正常），正值＝越線。量基線不量字框，理由見 README「表尾註」那節。
//
// 跑法：
//   python3 -m http.server 8731      # 在專案根目錄
//   瀏覽器開 http://localhost:8731/index.html，把這整個檔貼進 console，然後：
//   await check('/samples/')         # 或 '/_fixtures/en/'、'/_fixtures/real/'
//
// 回傳 {檔名: [列數, 最大越線 pt]}；全部是負值就是過。

const scanBaselines = () => [...document.querySelectorAll('.page')].map(p => {
  const g = [...p.querySelectorAll('.gd')].pop();
  if (!g) return null;
  const gy = g.getBoundingClientRect().bottom;
  let best = null, bv = -1e9;                       // 先用字框找出最下面那段，再量它的基線
  for (const e of p.querySelectorAll('.row .seg, .row span, .row div')) {
    const r = e.getBoundingClientRect();
    if (r.height && r.bottom > bv) { bv = r.bottom; best = e; }
  }
  if (!best) return null;                           // 沒有資料列的頁（例：en/G.pdf 第 1 頁）
  const probe = document.createElement('i');        // 零高、貼基線 → 它的 bottom 就是基線
  probe.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
  best.appendChild(probe);
  const base = probe.getBoundingClientRect().bottom;
  probe.remove();
  return +(base - gy).toFixed(1);
});

async function check(dir, { waitLoad = 5000, waitRender = 2000 } = {}) {
  const list = await (await fetch(dir)).text();
  const names = [...list.matchAll(/href="([^"]+\.pdf)"/g)].map(m => decodeURIComponent(m[1]));
  const out = {};
  for (const n of names) {
    const blob = await (await fetch(dir + encodeURIComponent(n))).blob();
    const inp = document.querySelector('input[type=file]');
    const dt = new DataTransfer();
    dt.items.add(new File([blob], n, { type: 'application/pdf' }));
    inp.files = dt.files;
    inp.dispatchEvent(new Event('change', { bubbles: true }));
    await new Promise(r => setTimeout(r, waitLoad));          // 大檔（frusg 4733 列）要久一點
    if (!avgAll.textContent.startsWith('取消')) avgAll.click();
    await new Promise(r => setTimeout(r, waitRender));
    const v = scanBaselines().filter(x => x !== null);
    out[n] = [msg.textContent.split(' / ')[0], Math.max(...v)];
  }
  console.table(out);
  return out;
}
