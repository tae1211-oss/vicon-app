with open('beacon_yard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── showProdMonth: 삭제 버튼 열 추가 ─────────────────────────────────────────
old_month = """function showProdMonth(year, month) {
  const records = (window._prodRecords||[])
    .filter(r => r.date?.startsWith(year + '-' + month))
    .sort((a,b) => {
      if (a.date !== b.date) return a.date.localeCompare(b.date);
      if (a.shift !== b.shift) return a.shift === '주간' ? -1 : 1;
      return (a.machine||'').localeCompare(b.machine||'');
    });

  const navEl  = document.getElementById('prod-stat-nav');
  const bodyEl = document.getElementById('prod-stat-body');

  navEl.innerHTML = `<button class="stat-back-btn" onclick="showProdYear('${year}')">← ${year}년</button>`;

  if (!records.length) {
    bodyEl.innerHTML = '<div class="alert alert-info">해당 월 기록 없습니다.</div>'; return;
  }

  const hasDetail = records.some(r => r.total_sheets);

  let html = `<div style="overflow-x:auto"><table class="prod-stat-table"><thead><tr>
    <th>날짜</th><th>주/야</th><th>호기</th><th>현장</th><th>패킹</th>
    ${hasDetail ? '<th>장수</th><th>㎡</th>' : ''}
  </tr></thead><tbody>`;

  // 날짜별 그룹
  const byDay = {};
  records.forEach(r => { (byDay[r.date] = byDay[r.date]||[]).push(r); });

  let mPacks = 0, mSheets = 0, mArea = 0;
  Object.entries(byDay).sort().forEach(([date, recs]) => {
    const dPacks  = recs.reduce((s,r) => s+(r.pack_count||0), 0);
    const dSheets = recs.reduce((s,r) => s+(r.total_sheets||0), 0);
    const dArea   = recs.reduce((s,r) => s+(r.total_area||0), 0);
    mPacks += dPacks; mSheets += dSheets; mArea += dArea;

    const d = new Date(date + 'T12:00:00');
    const dayLbl = (d.getMonth()+1) + '/' + d.getDate() + '(' + '일월화수목금토'[d.getDay()] + ')';

    recs.forEach((r, idx) => {
      const siteShort = (r.site||'').length > 8 ? (r.site||'').slice(0,7)+'…' : (r.site||'-');
      html += `<tr>
        <td>${idx===0 ? dayLbl : ''}</td>
        <td>${r.shift||''}</td>
        <td>${r.machine||''}</td>
        <td style="text-align:left">${esc(siteShort)}</td>
        <td>${r.pack_count||0}</td>
        ${hasDetail ? `<td>${r.total_sheets??'-'}</td><td>${r.total_area!=null?r.total_area.toFixed(1):'-'}</td>` : ''}
      </tr>`;
    });
    html += `<tr class="day-total">
      <td colspan="4" style="text-align:right;font-size:.72rem">${dayLbl} 계</td>
      <td>${dPacks}</td>
      ${hasDetail ? `<td>${dSheets||'-'}</td><td>${dArea?dArea.toFixed(1):'-'}</td>` : ''}
    </tr>`;
  });

  html += `<tr class="month-total">
    <td colspan="4" style="text-align:right">${+month}월 합계</td>
    <td>${mPacks}</td>
    ${hasDetail ? `<td>${mSheets||'-'}</td><td>${mArea?mArea.toFixed(1):'-'}</td>` : ''}
  </tr></tbody></table></div>`;

  bodyEl.innerHTML = html;
}"""

new_month = """function showProdMonth(year, month) {
  const records = (window._prodRecords||[])
    .filter(r => r.date?.startsWith(year + '-' + month))
    .sort((a,b) => {
      if (a.date !== b.date) return a.date.localeCompare(b.date);
      if (a.shift !== b.shift) return a.shift === '주간' ? -1 : 1;
      return (a.machine||'').localeCompare(b.machine||'');
    });

  const navEl  = document.getElementById('prod-stat-nav');
  const bodyEl = document.getElementById('prod-stat-body');

  navEl.innerHTML = `<button class="stat-back-btn" onclick="showProdYear('${year}')">← ${year}년</button>`;

  if (!records.length) {
    bodyEl.innerHTML = '<div class="alert alert-info">해당 월 기록 없습니다.</div>'; return;
  }

  const hasDetail = records.some(r => r.total_sheets);

  let html = `<div style="overflow-x:auto"><table class="prod-stat-table"><thead><tr>
    <th>날짜</th><th>주/야</th><th>호기</th><th>현장</th><th>패킹</th>
    ${hasDetail ? '<th>장수</th><th>㎡</th>' : ''}
    <th style="width:34px"></th>
  </tr></thead><tbody>`;

  const byDay = {};
  records.forEach(r => { (byDay[r.date] = byDay[r.date]||[]).push(r); });

  let mPacks = 0, mSheets = 0, mArea = 0;
  Object.entries(byDay).sort().forEach(([date, recs]) => {
    const dPacks  = recs.reduce((s,r) => s+(r.pack_count||0), 0);
    const dSheets = recs.reduce((s,r) => s+(r.total_sheets||0), 0);
    const dArea   = recs.reduce((s,r) => s+(r.total_area||0), 0);
    mPacks += dPacks; mSheets += dSheets; mArea += dArea;

    const d = new Date(date + 'T12:00:00');
    const dayLbl = (d.getMonth()+1) + '/' + d.getDate() + '(' + '일월화수목금토'[d.getDay()] + ')';

    recs.forEach((r, idx) => {
      const siteShort = (r.site||'').length > 8 ? (r.site||'').slice(0,7)+'…' : (r.site||'-');
      html += `<tr>
        <td>${idx===0 ? dayLbl : ''}</td>
        <td>${r.shift||''}</td>
        <td>${r.machine||''}</td>
        <td style="text-align:left">${esc(siteShort)}</td>
        <td>${r.pack_count||0}</td>
        ${hasDetail ? `<td>${r.total_sheets??'-'}</td><td>${r.total_area!=null?r.total_area.toFixed(1):'-'}</td>` : ''}
        <td><button onclick="deleteProdRow('${r.id}','${year}','${month}')"
          style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#e53935;padding:2px 5px;line-height:1"
          title="삭제">🗑</button></td>
      </tr>`;
    });
    html += `<tr class="day-total">
      <td colspan="4" style="text-align:right;font-size:.72rem">${dayLbl} 계</td>
      <td>${dPacks}</td>
      ${hasDetail ? `<td>${dSheets||'-'}</td><td>${dArea?dArea.toFixed(1):'-'}</td>` : ''}
      <td></td>
    </tr>`;
  });

  html += `<tr class="month-total">
    <td colspan="4" style="text-align:right">${+month}월 합계</td>
    <td>${mPacks}</td>
    ${hasDetail ? `<td>${mSheets||'-'}</td><td>${mArea?mArea.toFixed(1):'-'}</td>` : ''}
    <td></td>
  </tr></tbody></table></div>`;

  bodyEl.innerHTML = html;
}"""

count = html.count(old_month)
print(f'showProdMonth: {count} occurrences')
html = html.replace(old_month, new_month)

# ── deleteProdRow 함수 추가 (openDeleteProd 앞에) ─────────────────────────────
delete_fn = """
// ── 생산기록 개별 삭제 (누구나 가능) ──────────────────────
async function deleteProdRow(docId, year, month) {
  if (!db) { toast('Firebase 미연결'); return; }
  if (!confirm('이 생산 기록을 삭제하시겠습니까?\\n\\n삭제 후에는 복구할 수 없습니다.')) return;
  try {
    await db.collection('production_deck').doc(docId).delete();
    if (window._prodRecords) {
      window._prodRecords = window._prodRecords.filter(r => r.id !== docId);
    }
    toast('삭제되었습니다.');
    showProdMonth(year, month);
  } catch(e) { toast('삭제 실패: ' + e.message); }
}

"""

# openDeleteProd 앞에 삽입
target = '// ── 생산기록 삭제 ─────────────────────────────────────────\nasync function openDeleteProd()'
html = html.replace(target, delete_fn + target, 1)

with open('beacon_yard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('deleteProdRow added:', 'deleteProdRow' in html)
