with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# 1. 중복 경고 모달 HTML 추가 (edit-prod-modal 앞)
# ══════════════════════════════════════════════════════════
old_edit_modal_anchor = """<!-- ════════ EDIT PROD MODAL ════════ -->"""

new_dup_modal = """<!-- ════════ DUP WARN MODAL ════════ -->
<div id="dup-warn-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);z-index:9999;align-items:center;justify-content:center;padding:16px;box-sizing:border-box">
  <div style="background:#fff;border-radius:16px;padding:20px;width:94%;max-width:400px;max-height:82vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.3)">
    <h3 style="margin:0 0 4px;font-size:1rem;color:#c62828">⚠️ 중복 등록 차단</h3>
    <div style="font-size:.78rem;color:#78909c;margin-bottom:14px">이미 등록된 패킹번호입니다.<br>아래에서 원본 기록을 수정할 수 있습니다.</div>
    <div id="dup-warn-body"></div>
    <button onclick="closeDupWarn()" style="width:100%;padding:11px;background:#90a4ae;color:#fff;border:none;border-radius:10px;font-size:.95rem;cursor:pointer;font-family:inherit;margin-top:10px">닫기</button>
  </div>
</div>

<!-- ════════ EDIT PROD MODAL ════════ -->"""

cnt = html.count(old_edit_modal_anchor)
print(f'edit_modal_anchor: {cnt}')
html = html.replace(old_edit_modal_anchor, new_dup_modal, 1)

# ══════════════════════════════════════════════════════════
# 2. 중복 체크 코드 → dupRecordMap 수집 + 모달 호출로 교체
# ══════════════════════════════════════════════════════════
old_dup = """      const registeredPacks = [];
      const fourMonthsAgo = new Date();
      fourMonthsAgo.setMonth(fourMonthsAgo.getMonth() - 4);
      const cutoff = fourMonthsAgo.toISOString().slice(0, 10);
      dupSnap.forEach(doc => {
        const d = doc.data();
        if ((d.date || '9999') >= cutoff) {
          (d.packs || []).forEach(p => registeredPacks.push(p.pack_no));
        }
      });
      const dupPacks = sel.filter(n => registeredPacks.includes(n));
      if (dupPacks.length > 0) {
        alert('\\u26a0\\ufe0f 중복 등록 차단\\n\\n이미 등록된 패킹번호가 있습니다:\\n' +
              dupPacks.join(', ') + '번\\n\\n' +
              '(주간/야간 구분 없이 4개월 내 동일 패킹 재등록 불가)\\n\\n' +
              '업체: ' + (pendingProd.company || '') + '\\n' +
              '현장: ' + (pendingProd.site    || '') + '\\n' +
              '의뢰번호: ' + (pendingProd.req_code || ''));
        return;
      }"""

new_dup = """      const registeredPacks = [];
      const dupRecordMap = {};
      const fourMonthsAgo = new Date();
      fourMonthsAgo.setMonth(fourMonthsAgo.getMonth() - 4);
      const cutoff = fourMonthsAgo.toISOString().slice(0, 10);
      dupSnap.forEach(doc => {
        const d = doc.data();
        if ((d.date || '9999') >= cutoff) {
          (d.packs || []).forEach(p => {
            registeredPacks.push(p.pack_no);
            if (!dupRecordMap[p.pack_no]) {
              dupRecordMap[p.pack_no] = {
                docId: doc.id, date: d.date||'', shift: d.shift||'', machine: d.machine||''
              };
            }
          });
        }
      });
      const dupPacks = sel.filter(n => registeredPacks.includes(n));
      if (dupPacks.length > 0) {
        showDupWarning(dupPacks, dupRecordMap);
        return;
      }"""

cnt = html.count(old_dup)
print(f'dup_check: {cnt}')
html = html.replace(old_dup, new_dup)

# ══════════════════════════════════════════════════════════
# 3. showDupWarning / closeDupWarn 함수 추가 (setAllPackCb 앞)
# ══════════════════════════════════════════════════════════
old_set_all = """function setAllPackCb(checked) {
  document.querySelectorAll('input[name="edit-pack-cb"]').forEach(cb => cb.checked = checked);
}"""

new_set_all = """// ── 중복 경고 모달 ──────────────────────────────────────
function showDupWarning(dupPacks, dupRecordMap) {
  const byRecord = {};
  dupPacks.forEach(pn => {
    const info = dupRecordMap[pn] || {};
    const key  = info.docId || 'unknown';
    if (!byRecord[key]) byRecord[key] = { ...info, packs: [] };
    byRecord[key].packs.push(pn);
  });

  let html = '';
  Object.values(byRecord).forEach(rec => {
    const yr = (rec.date||'').slice(0,4);
    const mo = (rec.date||'').slice(5,7);
    html += `<div style="background:#fff3e0;border-radius:8px;padding:10px 12px;margin-bottom:10px;border-left:4px solid #f57c00">
      <div style="font-size:.85rem;color:#bf360c;font-weight:700">📦 ${rec.packs.join(', ')}번 패킹</div>
      <div style="font-size:.82rem;color:#555;margin-top:5px;line-height:1.7">
        📅 등록일: <strong>${rec.date}</strong><br>
        🕐 구분: <strong>${rec.shift}</strong> &nbsp; 🏭 호기: <strong>${rec.machine}호기</strong>
      </div>
      <button onclick="closeDupWarn();openEditProd('${rec.docId}','${yr}','${mo}')"
        style="margin-top:9px;padding:7px 16px;background:#1565c0;color:#fff;border:none;border-radius:7px;font-size:.82rem;cursor:pointer;font-family:inherit">
        ✏️ 이 기록 수정하러 가기
      </button>
    </div>`;
  });

  document.getElementById('dup-warn-body').innerHTML = html;
  document.getElementById('dup-warn-modal').style.display = 'flex';
}

function closeDupWarn() {
  document.getElementById('dup-warn-modal').style.display = 'none';
}

function setAllPackCb(checked) {
  document.querySelectorAll('input[name="edit-pack-cb"]').forEach(cb => cb.checked = checked);
}"""

cnt = html.count(old_set_all)
print(f'setAllPackCb: {cnt}')
html = html.replace(old_set_all, new_set_all, 1)

# ══════════════════════════════════════════════════════════
# 4. showProdMonth → 집계표 추가
# ══════════════════════════════════════════════════════════
old_stat_table = """  const hasDetail = records.some(r => r.total_sheets);

  let html = `<div style="overflow-x:auto"><table class="prod-stat-table"><thead><tr>
    <th>날짜</th><th>주/야</th><th>호기</th><th>현장</th><th>패킹</th>
    ${hasDetail ? '<th>장수</th><th>㎡</th>' : ''}
    <th style="width:60px"></th>
  </tr></thead><tbody>`;"""

new_stat_table = """  const hasDetail = records.some(r => r.total_sheets);

  // ── 호기별 집계표 ──────────────────────────────────────
  const _macs  = [...new Set(records.map(r => String(r.machine||'')))].sort((a,b)=>+a-(+b)||a.localeCompare(b));
  const _dates = [...new Set(records.map(r => r.date))].sort();
  const _cTot  = {};
  _macs.forEach(m => { _cTot[m+'주간']=0; _cTot[m+'야간']=0; });
  let _gTot = 0;
  const _dw = '일월화수목금토';

  let sumHtml = `<details open style="margin-bottom:12px">
    <summary style="font-size:.78rem;font-weight:700;color:#0d47a1;cursor:pointer;margin-bottom:6px;list-style:none">
      📊 호기별 집계표 ▾
    </summary>
    <div style="overflow-x:auto">
    <table class="prod-stat-table"><thead>
    <tr><th rowspan="2" style="min-width:72px">날짜</th>${_macs.map(m=>`<th colspan="2">${m}호기</th>`).join('')}<th rowspan="2">일계</th></tr>
    <tr>${_macs.map(()=>'<th style="font-size:.68rem;color:#1565c0;padding:3px">주간</th><th style="font-size:.68rem;color:#546e7a;padding:3px">야간</th>').join('')}</tr>
    </thead><tbody>`;
  _dates.forEach(date => {
    const _d  = new Date(date+'T12:00:00');
    const _dl = (_d.getMonth()+1)+'/'+_d.getDate()+'('+_dw[_d.getDay()]+')';
    const _dr = records.filter(r=>r.date===date);
    let _rt = 0;
    sumHtml += `<tr><td>${_dl}</td>`;
    _macs.forEach(m => {
      ['주간','야간'].forEach(sh => {
        const cnt = _dr.filter(r=>String(r.machine||'')===m&&r.shift===sh).reduce((s,r)=>s+(r.pack_count||0),0);
        _cTot[m+sh] += cnt; _rt += cnt; _gTot += cnt;
        sumHtml += `<td style="color:${cnt?'#1a237e':'#ccc'}">${cnt||'-'}</td>`;
      });
    });
    sumHtml += `<td><strong>${_rt||'-'}</strong></td></tr>`;
  });
  sumHtml += `<tr class="month-total"><td>합계</td>`;
  _macs.forEach(m=>['주간','야간'].forEach(sh=>sumHtml+=`<td>${_cTot[m+sh]||'-'}</td>`));
  sumHtml += `<td><strong>${_gTot}</strong></td></tr>`;
  sumHtml += `</tbody></table></div></details>`;

  let html = sumHtml + `<div style="overflow-x:auto"><table class="prod-stat-table"><thead><tr>
    <th>날짜</th><th>주/야</th><th>호기</th><th>현장</th><th>패킹</th>
    ${hasDetail ? '<th>장수</th><th>㎡</th>' : ''}
    <th style="width:60px"></th>
  </tr></thead><tbody>`;"""

cnt = html.count(old_stat_table)
print(f'stat_table: {cnt}')
html = html.replace(old_stat_table, new_stat_table)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('dup-warn-modal:', 'dup-warn-modal' in html)
print('showDupWarning:', 'showDupWarning' in html)
print('dupRecordMap:', 'dupRecordMap' in html)
print('호기별 집계표:', '호기별 집계표' in html)
