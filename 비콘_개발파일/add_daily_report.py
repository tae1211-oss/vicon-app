with open('index.html.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. html2canvas CDN 추가 ──────────────────────────────────────────────────
if 'html2canvas' not in html:
    html = html.replace(
        '</head>',
        '<script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>\n</head>',
        1
    )

# ── 2. 작업일보 CSS 추가 ─────────────────────────────────────────────────────
dr_css = """
/* ── DAILY REPORT ───────────────────────────── */
#dr-modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.65);z-index:9999;display:none;align-items:flex-start;justify-content:center;overflow-y:auto;padding:16px;box-sizing:border-box}
.dr-wrap{background:#fff;border-radius:12px;padding:16px;width:fit-content;max-width:98vw}
.dr-actions{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:10px}
.dr-btn-dl{background:#1565c0;color:#fff;border:none;border-radius:8px;padding:9px 18px;font-size:.85rem;cursor:pointer;font-family:inherit}
.dr-btn-cl{background:#90a4ae;color:#fff;border:none;border-radius:8px;padding:9px 18px;font-size:.85rem;cursor:pointer;font-family:inherit}
.dr-page{width:790px;background:#fff;padding:14px 18px;box-sizing:border-box;font-family:'맑은 고딕','Malgun Gothic',Arial,sans-serif;font-size:9.5pt;color:#000}
.dr-hrow{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.dr-title{font-size:17pt;font-weight:bold}
.dr-stbl{border-collapse:collapse;font-size:9pt}
.dr-stbl th,.dr-stbl td{border:1px solid #000;padding:3px 10px;text-align:center;min-width:62px;height:26px}
.dr-stbl th{background:#e8e8e8}
.dr-dateline{font-size:10pt;margin:4px 0}
.dr-note{font-size:8pt;color:#444;margin:2px 0 5px}
.dr-winfo{font-size:9pt;margin-bottom:7px}
.dr-tbl{width:100%;border-collapse:collapse;font-size:9pt}
.dr-tbl th,.dr-tbl td{border:1px solid #000;padding:2px 4px;text-align:center;vertical-align:middle}
.dr-tbl thead th{background:#d0d0d0}
.dr-tbl .dr-site-td{text-align:left;padding-left:6px;width:215px}
.dr-chk{display:inline-block;width:13px;height:13px;border:1.5px solid #000;vertical-align:middle}
.dr-total-row td{font-weight:bold;background:#f0f0f0}
.dr-pgnum{text-align:right;font-size:8pt;color:#777;margin-top:3px}
.dr-page-gap{height:20px}
"""
html = html.replace('</style>', dr_css + '\n</style>', 1)

# ── 3. 작업일보 모달 HTML (</body> 앞) ──────────────────────────────────────
dr_modal = """
<!-- ════════ DAILY REPORT MODAL ════════ -->
<div id="dr-modal">
  <div class="dr-wrap">
    <div class="dr-actions">
      <strong style="font-size:1rem">📋 작업일보</strong>
      <div style="display:flex;gap:8px">
        <button class="dr-btn-dl" onclick="downloadDailyReport()">📥 이미지 저장</button>
        <button class="dr-btn-cl" onclick="closeDailyReport()">닫기</button>
      </div>
    </div>
    <div id="dr-body"></div>
  </div>
</div>
"""
html = html.replace('</body>', dr_modal + '\n</body>', 1)

# ── 4. showProdMonth 안에 📋 버튼 추가 ───────────────────────────────────────
old_del_btn = """        <td><button onclick="deleteProdRow('${r.id}','${year}','${month}')"
          style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#e53935;padding:2px 5px;line-height:1"
          title="삭제">🗑</button></td>"""

new_del_btn = """        <td style="white-space:nowrap">
          <button onclick="openDailyReport('${r.date}','${r.machine}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1"
            title="작업일보">📋</button>
          <button onclick="deleteProdRow('${r.id}','${year}','${month}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#e53935;padding:2px 4px;line-height:1"
            title="삭제">🗑</button>
        </td>"""

cnt = html.count(old_del_btn)
print(f'del_btn: {cnt} occurrences')
html = html.replace(old_del_btn, new_del_btn)

# ── 5. 헤더 빈칸 너비 조정 ───────────────────────────────────────────────────
html = html.replace(
    '<th style="width:34px"></th>',
    '<th style="width:60px"></th>',
    -1  # replace_all workaround: using str.replace with no count = all
)
# Python str.replace replaces all by default (no count = all occurrences)

# ── 6. JS 함수 추가 (</script>\n</body> 앞에) ────────────────────────────────
dr_js = r"""
// ════════════════════════════════════════════════
//  작업일보 기능
// ════════════════════════════════════════════════
function openDailyReport(date, machine) {
  const allRecs = (window._prodRecords||[])
    .filter(r => r.date === date && String(r.machine||'') === String(machine||''))
    .sort((a,b) => {
      if (a.shift !== b.shift) return a.shift==='주간' ? -1 : 1;
      return 0;
    });
  if (!allRecs.length) { toast('해당 일자/호기 기록 없음'); return; }

  const d = new Date(date + 'T12:00:00');
  const y  = d.getFullYear();
  const mo = d.getMonth() + 1;
  const dy = d.getDate();
  const dw = '일월화수목금토'[d.getDay()];
  const shift = allRecs[0].shift || '';

  const ROWS = 13;
  const pages = [];
  for (let i = 0; i < Math.max(1, Math.ceil(allRecs.length / ROWS)); i++) {
    pages.push(allRecs.slice(i * ROWS, (i+1) * ROWS));
  }

  let pagesHtml = '';
  pages.forEach((recs, pi) => {
    let rowsHtml = '';
    let tArea = 0, tSheets = 0;

    recs.forEach(r => {
      const packs = r.packs || [];
      const nos = packs.map(p => Number(p.pack_no)).filter(n => !isNaN(n)).sort((a,b)=>a-b);
      let packStr = '';
      if (nos.length) {
        packStr = nos[0] === nos[nos.length-1] ? String(nos[0]) : nos[0]+'-'+nos[nos.length-1];
      } else if (r.pack_count) {
        packStr = '('+r.pack_count+'건)';
      }

      const site  = r.site     || '';
      const req   = r.req_code || '';
      const area  = r.total_area   != null ? (+r.total_area).toFixed(2)  : '';
      const qty   = r.total_sheets != null ? r.total_sheets : (r.pack_count || '');
      tArea   += r.total_area   || 0;
      tSheets += r.total_sheets || r.pack_count || 0;

      // 현장명+패킹번호 길이 판단 (22자 초과면 두 줄)
      const combined = site + (packStr ? ' '+packStr : '');
      const siteCellInner = combined.length > 22
        ? esc(site) + '<br><span style="font-size:8pt;color:#333">' + esc(packStr) + '</span>'
        : esc(combined);

      rowsHtml += `<tr style="height:22px">
        <td class="dr-site-td">${siteCellInner}</td>
        <td>${esc(req)}</td>
        <td>${area}</td>
        <td>${qty}</td>
        <td><span class="dr-chk"></span></td>
        <td><span class="dr-chk"></span></td>
        <td style="letter-spacing:2px">&thinsp;:&thinsp;</td>
        <td>합 / 불</td>
      </tr>`;
    });

    // 빈 행 채우기
    for (let i = recs.length; i < ROWS; i++) {
      rowsHtml += `<tr style="height:22px">
        <td class="dr-site-td"></td><td></td><td></td><td></td>
        <td><span class="dr-chk"></span></td>
        <td><span class="dr-chk"></span></td>
        <td style="letter-spacing:2px">&thinsp;:&thinsp;</td>
        <td>합 / 불</td>
      </tr>`;
    }

    const shiftHtml = shift === '주간'
      ? '<span style="color:#c0392b;font-weight:bold">주</span>&nbsp;야'
      : '주&nbsp;<span style="color:#c0392b;font-weight:bold">야</span>';

    pagesHtml += `
    ${pi > 0 ? '<div class="dr-page-gap"></div>' : ''}
    <div class="dr-page">
      <div class="dr-hrow">
        <div class="dr-title">(${esc(String(machine))})호기 데크반 작업일보</div>
        <table class="dr-stbl">
          <tr><th>작&nbsp;성</th><th>조 / 반장</th><th>확&nbsp;인</th></tr>
          <tr><td style="height:30px"></td><td></td><td></td></tr>
        </table>
      </div>
      <div class="dr-dateline">
        ${y}년 ${mo}월 ${dy}일 &nbsp;${dw}요일 &nbsp;&nbsp;
        (${shiftHtml}) &nbsp;&nbsp; OP :&nbsp;&nbsp;&nbsp;&nbsp; TI
      </div>
      <div class="dr-note">※ 라벨에 날자 기록 / 자주검사 및 박리검사 명확하게 할 것</div>
      <div class="dr-winfo">
        ■ 작업시간 : 시작&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;~&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;종료
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        ■ 작업자 이름 (&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;명) :
      </div>
      <table class="dr-tbl">
        <thead>
          <tr>
            <th rowspan="2" style="width:215px">현 장 명</th>
            <th rowspan="2" style="width:95px">의뢰번호</th>
            <th rowspan="2" style="width:58px">면 적</th>
            <th rowspan="2" style="width:48px">수 량</th>
            <th colspan="2">포장방식</th>
            <th colspan="2">자 주 검 사</th>
          </tr>
          <tr>
            <th style="width:42px">롤 재</th>
            <th style="width:42px">슬리퍼</th>
            <th style="width:72px">시 간</th>
            <th style="width:62px">합 / 불</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
          <tr class="dr-total-row">
            <td colspan="2" style="text-align:right;padding-right:8px">합&nbsp;&nbsp;&nbsp;계</td>
            <td>${(+tArea).toFixed(2)}</td>
            <td>${tSheets||''}</td>
            <td colspan="4"></td>
          </tr>
        </tbody>
      </table>
      ${pages.length > 1 ? `<div class="dr-pgnum">${pi+1} / ${pages.length}</div>` : ''}
    </div>`;
  });

  document.getElementById('dr-body').innerHTML = pagesHtml;
  document.getElementById('dr-modal').style.display = 'flex';
  window._drDate    = date;
  window._drMachine = machine;
}

function closeDailyReport() {
  document.getElementById('dr-modal').style.display = 'none';
}

async function downloadDailyReport() {
  const body = document.getElementById('dr-body');
  try {
    toast('이미지 생성 중...');
    const canvas = await html2canvas(body, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false
    });
    const a = document.createElement('a');
    a.download = `작업일보_${window._drMachine}호기_${window._drDate}.png`;
    a.href = canvas.toDataURL('image/png');
    a.click();
  } catch(e) {
    toast('이미지 저장 실패: ' + e.message);
  }
}
"""

html = html.replace('</script>\n</body>', dr_js + '\n</script>\n</body>', 1)

with open('index.html.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('html2canvas:', 'html2canvas' in html)
print('openDailyReport:', 'openDailyReport' in html)
print('dr-modal:', 'dr-modal' in html)
