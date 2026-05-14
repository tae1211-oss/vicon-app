with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── search anchors ──────────────────────────────────────────
search_start = "  const hasDetail = records.some(r => r.total_sheets);\n"
search_end   = "  bodyEl.innerHTML = html;\n}"

# JavaScript new block — avoid nested backtick template literals
new_block = r"""  // machines sorted numerically then alpha
  const _allMacs = [...new Set(records.map(r => String(r.machine||'')))].filter(Boolean);
  const _macs = _allMacs.sort((a,b) => {
    const na = parseInt(a), nb = parseInt(b);
    if (!isNaN(na) && !isNaN(nb)) return na - nb;
    if (!isNaN(na)) return -1;
    if (!isNaN(nb)) return 1;
    return a.localeCompare(b);
  });
  const _dates = [...new Set(records.map(r => r.date))].sort();
  const _shifts = ['야간','주간'];
  const _dw = '일월화수목금토';

  // pivot: date|shift|machine -> total_area
  const pivot = {};
  const colTot = {};
  const rowTot = {};
  let grandTotal = 0;
  _shifts.forEach(sh => _macs.forEach(m => { colTot[sh+'|'+m] = 0; }));
  _dates.forEach(d => { rowTot[d] = 0; });
  records.forEach(r => {
    const key = (r.date||'') + '|' + (r.shift||'') + '|' + String(r.machine||'');
    pivot[key] = (pivot[key]||0) + (r.total_area||0);
  });
  Object.entries(pivot).forEach(([k, v]) => {
    const parts = k.split('|');
    const date = parts[0], sh = parts[1], mac = parts[2];
    if (colTot[sh+'|'+mac] !== undefined) colTot[sh+'|'+mac] += v;
    if (rowTot[date] !== undefined) rowTot[date] += v;
    grandTotal += v;
  });

  // header
  let thMacs = '';
  _shifts.forEach(sh => _macs.forEach(m => {
    thMacs += '<th style="background:' + (sh===_shifts[0]?'#e3f2fd':'#fff8e1') + ';font-size:.68rem;font-weight:600;padding:3px 4px;text-align:center">' + m + '</th>';
  }));
  let thShifts = '';
  _shifts.forEach(sh => {
    thShifts += '<th colspan="' + _macs.length + '" style="background:' + (sh===_shifts[0]?'#e3f2fd':'#fff8e1') + ';color:' + (sh===_shifts[0]?'#0d47a1':'#e65100') + ';padding:5px 2px;text-align:center">' + sh + '</th>';
  });

  let sumHtml = '<div style="overflow-x:auto;margin-bottom:16px">'
    + '<table class="prod-stat-table" style="font-size:.75rem;border-collapse:collapse;width:100%"><thead>'
    + '<tr><th rowspan="2" style="min-width:72px;background:#e8eaf6;vertical-align:middle;text-align:center">'
    + '생산일자</th>' + thShifts
    + '<th rowspan="2" style="background:#e8f5e9;color:#1b5e20;vertical-align:middle;text-align:center">'
    + '총합계</th></tr>'
    + '<tr>' + thMacs + '</tr>'
    + '</thead><tbody>';

  _dates.forEach(date => {
    const _d = new Date(date+'T12:00:00');
    const _dl = (_d.getMonth()+1)+'/'+_d.getDate()+'('+_dw[_d.getDay()]+')';
    sumHtml += '<tr><td style="font-size:.72rem;white-space:nowrap;text-align:center">' + _dl + '</td>';
    _shifts.forEach(sh => {
      _macs.forEach(m => {
        const v = pivot[date+'|'+sh+'|'+m] || 0;
        sumHtml += '<td style="color:' + (v?'#1a237e':'#ccc') + ';text-align:center">' + (v ? v.toFixed(1) : '-') + '</td>';
      });
    });
    const rt = rowTot[date]||0;
    sumHtml += '<td style="font-weight:700;color:#2e7d32;text-align:center">' + (rt ? rt.toFixed(1) : '-') + '</td></tr>';
  });
  sumHtml += '<tr class="month-total"><td style="text-align:center">합계</td>';
  _shifts.forEach(sh => _macs.forEach(m => {
    const v = colTot[sh+'|'+m]||0;
    sumHtml += '<td style="text-align:center">' + (v ? v.toFixed(1) : '-') + '</td>';
  }));
  sumHtml += '<td style="font-weight:700;text-align:center">' + (grandTotal ? grandTotal.toFixed(1) : '-') + '</td></tr>';
  sumHtml += '</tbody></table></div>';

  // detail records (collapsible)
  const hasDetail = records.some(r => r.total_sheets);
  let detailHtml = '<details style="margin-top:4px"><summary style="font-size:.78rem;font-weight:700;color:#546e7a;cursor:pointer;padding:6px 0;list-style:none;user-select:none">'
    + '📋 상세 기록 보기 ▾</summary>'
    + '<div style="overflow-x:auto;margin-top:8px"><table class="prod-stat-table"><thead><tr>'
    + '<th>날짜</th><th>주/야</th><th>호기</th><th>현장</th><th>패킹</th>'
    + (hasDetail ? '<th>장수</th><th>㎡</th>' : '')
    + '<th style="width:60px"></th>'
    + '</tr></thead><tbody>';

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
      detailHtml += '<tr>'
        + '<td>' + (idx===0 ? dayLbl : '') + '</td>'
        + '<td>' + (r.shift||'') + '</td>'
        + '<td>' + (r.machine||'') + '</td>'
        + '<td style="text-align:left">' + esc(siteShort) + '</td>'
        + '<td>' + (r.pack_count||0) + '</td>'
        + (hasDetail ? '<td>' + (r.total_sheets!=null?r.total_sheets:'-') + '</td><td>' + (r.total_area!=null?r.total_area.toFixed(1):'-') + '</td>' : '')
        + '<td style="white-space:nowrap">'
        + '<button onclick="openEditProd(\'' + r.id + '\',\'' + year + '\',\'' + month + '\')" style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#2e7d32;padding:2px 4px;line-height:1" title="수정/취소">✏️</button>'
        + '<button onclick="openDailyReport(\'' + r.date + '\',\'' + r.machine + '\',\'' + (r.shift||'') + '\')" style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1" title="작업일보">📋</button>'
        + '</td></tr>';
    });
    detailHtml += '<tr class="day-total">'
      + '<td colspan="4" style="text-align:right;font-size:.72rem">' + dayLbl + ' 계</td>'
      + '<td>' + dPacks + '</td>'
      + (hasDetail ? '<td>' + (dSheets||'-') + '</td><td>' + (dArea?dArea.toFixed(1):'-') + '</td>' : '')
      + '<td></td></tr>';
  });
  detailHtml += '<tr class="month-total">'
    + '<td colspan="4" style="text-align:right">' + (+month) + '월 합계</td>'
    + '<td>' + mPacks + '</td>'
    + (hasDetail ? '<td>' + (mSheets||'-') + '</td><td>' + (mArea?mArea.toFixed(1):'-') + '</td>' : '')
    + '<td></td></tr></tbody></table></div></details>';

  bodyEl.innerHTML = sumHtml + detailHtml;
}"""

count = 0
pos = 0
while True:
    idx_start = html.find(search_start, pos)
    if idx_start == -1:
        break
    idx_end = html.find(search_end, idx_start)
    if idx_end == -1:
        break
    idx_end += len(search_end)
    html = html[:idx_start] + new_block + html[idx_end:]
    pos = idx_start + len(new_block)
    count += 1

print(f'replaced: {count}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('pivot check:', html.count("pivot[date+'|'+sh+'|'+m)"))
print('grandTotal check:', html.count('grandTotal'))
