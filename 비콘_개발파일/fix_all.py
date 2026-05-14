with open('index.html.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# 1. 작업일보 버튼에 shift 추가
# ══════════════════════════════════════════════════════════
old_dr_btn = """          <button onclick="openDailyReport('${r.date}','${r.machine}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1"
            title="작업일보">📋</button>"""

new_dr_btn = """          <button onclick="openDailyReport('${r.date}','${r.machine}','${r.shift||''}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1"
            title="작업일보">📋</button>"""

cnt = html.count(old_dr_btn)
print(f'dr_btn: {cnt}')
html = html.replace(old_dr_btn, new_dr_btn)

# ══════════════════════════════════════════════════════════
# 2. 수정 모달 HTML 교체 (체크박스 방식)
# ══════════════════════════════════════════════════════════
old_edit_modal = """<!-- ════════ EDIT PROD MODAL ════════ -->
<div id="edit-prod-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);z-index:9998;align-items:center;justify-content:center">
  <div style="background:#fff;border-radius:16px;padding:24px;width:94%;max-width:380px;box-shadow:0 8px 32px rgba(0,0,0,.25)">
    <h3 style="margin:0 0 16px;font-size:1.05rem">✏️ 생산기록 수정</h3>
    <input type="hidden" id="edit-prod-id"/>
    <input type="hidden" id="edit-prod-year"/>
    <input type="hidden" id="edit-prod-month"/>
    <div style="margin-bottom:11px">
      <label style="font-size:.78rem;font-weight:700;color:#546e7a;display:block;margin-bottom:4px">날짜</label>
      <input type="date" id="edit-prod-date" style="width:100%;padding:10px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.95rem;box-sizing:border-box"/>
    </div>
    <div style="margin-bottom:11px">
      <label style="font-size:.78rem;font-weight:700;color:#546e7a;display:block;margin-bottom:4px">주/야간</label>
      <select id="edit-prod-shift" style="width:100%;padding:10px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.95rem;box-sizing:border-box">
        <option value="주간">주간</option>
        <option value="야간">야간</option>
      </select>
    </div>
    <div style="margin-bottom:11px">
      <label style="font-size:.78rem;font-weight:700;color:#546e7a;display:block;margin-bottom:4px">호기</label>
      <input type="text" id="edit-prod-machine" placeholder="예: 1" style="width:100%;padding:10px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.95rem;box-sizing:border-box"/>
    </div>
    <div style="margin-bottom:11px">
      <label style="font-size:.78rem;font-weight:700;color:#546e7a;display:block;margin-bottom:4px">현장명</label>
      <input type="text" id="edit-prod-site" style="width:100%;padding:10px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.95rem;box-sizing:border-box"/>
    </div>
    <div style="margin-bottom:16px">
      <label style="font-size:.78rem;font-weight:700;color:#546e7a;display:block;margin-bottom:4px">의뢰번호</label>
      <input type="text" id="edit-prod-reqcode" style="width:100%;padding:10px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.95rem;box-sizing:border-box"/>
    </div>
    <div style="display:flex;gap:8px">
      <button onclick="saveEditProd()" style="flex:1;padding:12px;background:#1565c0;color:#fff;border:none;border-radius:10px;font-size:.95rem;font-weight:700;cursor:pointer;font-family:inherit">저장</button>
      <button onclick="closeEditProd()" style="flex:1;padding:12px;background:#90a4ae;color:#fff;border:none;border-radius:10px;font-size:.95rem;cursor:pointer;font-family:inherit">취소</button>
    </div>
  </div>
</div>"""

new_edit_modal = """<!-- ════════ EDIT PROD MODAL ════════ -->
<div id="edit-prod-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);z-index:9998;align-items:center;justify-content:center;padding:16px;box-sizing:border-box">
  <div style="background:#fff;border-radius:16px;padding:20px;width:94%;max-width:400px;max-height:82vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.25)">
    <h3 style="margin:0 0 12px;font-size:1rem">✏️ 생산 취소 / 수정</h3>
    <input type="hidden" id="edit-prod-id"/>
    <input type="hidden" id="edit-prod-year"/>
    <input type="hidden" id="edit-prod-month"/>
    <div id="edit-prod-header" style="background:#f5f7fa;border-radius:10px;padding:10px 12px;margin-bottom:12px;font-size:.85rem;line-height:1.7"></div>
    <div style="font-size:.78rem;font-weight:700;color:#546e7a;margin-bottom:6px">취소할 패킹번호 체크 해제</div>
    <div id="edit-prod-packs" style="border:1px solid #e0e0e0;border-radius:8px;padding:4px 8px;max-height:300px;overflow-y:auto"></div>
    <div style="display:flex;gap:8px;margin-top:14px">
      <button onclick="saveEditProd()" style="flex:1;padding:12px;background:#1565c0;color:#fff;border:none;border-radius:10px;font-size:.95rem;font-weight:700;cursor:pointer;font-family:inherit">저장</button>
      <button onclick="closeEditProd()" style="flex:1;padding:12px;background:#90a4ae;color:#fff;border:none;border-radius:10px;font-size:.95rem;cursor:pointer;font-family:inherit">취소</button>
    </div>
  </div>
</div>"""

cnt = html.count(old_edit_modal)
print(f'edit_modal: {cnt}')
html = html.replace(old_edit_modal, new_edit_modal, 1)

# ══════════════════════════════════════════════════════════
# 3. 중복 체크에 4개월 필터 추가
# ══════════════════════════════════════════════════════════
old_dup = """    const registeredPacks = [];
      dupSnap.forEach(doc => { (doc.data().packs||[]).forEach(p => registeredPacks.push(p.pack_no)); });
      const dupPacks = sel.filter(n => registeredPacks.includes(n));
      if (dupPacks.length > 0) {
        alert('⚠️ 중복 등록 차단\\n\\n이미 등록된 패킹번호가 있습니다:\\n' +
              dupPacks.join(', ') + '번\\n\\n' +
              '업체: ' + (pendingProd.company || '') + '\\n' +
              '현장: ' + (pendingProd.site    || '') + '\\n' +
              '의뢰번호: ' + (pendingProd.req_code || ''));"""

new_dup = """    const registeredPacks = [];
      const fourMonthsAgo = new Date();
      fourMonthsAgo.setMonth(fourMonthsAgo.getMonth() - 4);
      const cutoff = fourMonthsAgo.toISOString().slice(0, 10);
      dupSnap.forEach(doc => {
        const d = doc.data();
        if ((d.date || '9999') >= cutoff) {
          (d.packs||[]).forEach(p => registeredPacks.push(p.pack_no));
        }
      });
      const dupPacks = sel.filter(n => registeredPacks.includes(n));
      if (dupPacks.length > 0) {
        alert('⚠️ 중복 등록 차단\\n\\n이미 등록된 패킹번호가 있습니다:\\n' +
              dupPacks.join(', ') + '번\\n\\n' +
              '(주간/야간 구분 없이 4개월 내 동일 패킹 재등록 불가)\\n\\n' +
              '업체: ' + (pendingProd.company || '') + '\\n' +
              '현장: ' + (pendingProd.site    || '') + '\\n' +
              '의뢰번호: ' + (pendingProd.req_code || ''));"""

cnt = html.count(old_dup)
print(f'dup_check: {cnt}')
html = html.replace(old_dup, new_dup)

# ══════════════════════════════════════════════════════════
# JS 함수들 교체 (openDailyReport, openEditProd, saveEditProd)
# ══════════════════════════════════════════════════════════

# 기존 JS 함수 블록 교체
old_js_block = """// ── 생산기록 일괄 삭제 (관리자) ─────────────────────────"""

# 새 JS 함수들 전체 (배치삭제 + 수정 + 작업일보)
new_js_funcs = r"""// ── 생산기록 일괄 삭제 (관리자) ─────────────────────────
function previewBatchDelete() {
  const ym   = document.getElementById('batch-del-month').value;
  const date = document.getElementById('batch-del-date').value;
  const mach = document.getElementById('batch-del-machine').value.trim();
  const shift= document.getElementById('batch-del-shift').value;
  const prev = document.getElementById('batch-del-preview');
  const btn  = document.getElementById('batch-del-btn');
  if (!ym && !date && !mach && !shift) {
    prev.textContent = '⚠️ 조건을 하나 이상 입력하세요.';
    btn.style.display = 'none'; return;
  }
  const matched = (window._prodRecords||[]).filter(r => {
    if (ym   && !(r.date||'').startsWith(ym))       return false;
    if (date && r.date !== date)                     return false;
    if (mach && String(r.machine||'') !== mach)      return false;
    if (shift && r.shift !== shift)                  return false;
    return true;
  });
  window._batchDeleteTargets = matched;
  if (!matched.length) {
    prev.innerHTML = '<span style="color:#e53935">조건에 맞는 기록이 없습니다.</span>';
    btn.style.display = 'none';
  } else {
    prev.innerHTML = `<span style="color:#1565c0;font-weight:700">${matched.length}건</span> 이 검색되었습니다.`;
    btn.style.display = 'block';
  }
}

async function executeBatchDelete() {
  if (!db) { toast('Firebase 미연결'); return; }
  const targets = window._batchDeleteTargets || [];
  if (!targets.length) { toast('삭제할 기록 없음'); return; }
  if (!confirm(`⚠️ 일괄 삭제 확인\n\n${targets.length}건을 삭제합니다.\n삭제 후에는 복구할 수 없습니다.\n\n계속하시겠습니까?`)) return;
  const btn = document.getElementById('batch-del-btn');
  btn.disabled = true; btn.textContent = '삭제 중...';
  try {
    const CHUNK = 400;
    for (let i = 0; i < targets.length; i += CHUNK) {
      const batch = db.batch();
      targets.slice(i, i+CHUNK).forEach(r => batch.delete(db.collection('production_deck').doc(r.id)));
      await batch.commit();
    }
    const ids = new Set(targets.map(r => r.id));
    window._prodRecords = (window._prodRecords||[]).filter(r => !ids.has(r.id));
    window._batchDeleteTargets = [];
    document.getElementById('batch-del-preview').innerHTML = '<span style="color:#2e7d32">✅ 삭제 완료</span>';
    btn.style.display = 'none';
    toast(`✅ ${targets.length}건 삭제 완료`);
    loadProdStat();
  } catch(e) {
    toast('삭제 실패: ' + e.message);
  } finally {
    btn.disabled = false; btn.textContent = '🗑️ 일괄 삭제 실행';
  }
}

// ── 생산기록 수정 (체크박스 방식) ───────────────────────
function openEditProd(docId, year, month) {
  const r = (window._prodRecords||[]).find(r => r.id === docId);
  if (!r) { toast('기록을 찾을 수 없습니다.'); return; }
  document.getElementById('edit-prod-id').value    = docId;
  document.getElementById('edit-prod-year').value  = year;
  document.getElementById('edit-prod-month').value = month;

  // 헤더 정보
  document.getElementById('edit-prod-header').innerHTML =
    `<div><span style="color:#78909c;font-size:.75rem">업체명</span><br><strong>${esc(r.company||'-')}</strong></div>
     <div style="margin-top:6px"><span style="color:#78909c;font-size:.75rem">현장명</span><br><strong>${esc(r.site||'-')}</strong></div>
     <div style="margin-top:6px"><span style="color:#78909c;font-size:.75rem">의뢰번호</span><br><strong>${esc(r.req_code||'-')}</strong></div>
     <div style="margin-top:8px;font-size:.75rem;color:#90a4ae">${r.date||''} &nbsp;·&nbsp; ${r.shift||''} &nbsp;·&nbsp; ${r.machine||''}호기</div>`;

  // 패킹 체크박스
  const packs = r.packs || [];
  const packsEl = document.getElementById('edit-prod-packs');
  if (!packs.length) {
    packsEl.innerHTML = '<div style="color:#90a4ae;font-size:.85rem;padding:8px">패킹 정보 없음</div>';
  } else {
    packsEl.innerHTML = packs.map(p => {
      const detail = (p.sheets!=null)
        ? ` <span style="color:#90a4ae;font-size:.78rem">· ${p.sheets}장 · ${(+(p.area||0)).toFixed(1)}㎡</span>`
        : '';
      return `<label style="display:flex;align-items:center;gap:10px;padding:9px 4px;border-bottom:1px solid #f5f5f5;cursor:pointer">
        <input type="checkbox" name="edit-pack-cb" value="${p.pack_no}" checked
               style="width:18px;height:18px;accent-color:#1565c0;cursor:pointer;flex-shrink:0"/>
        <div><strong>${p.pack_no}번 패킹</strong>${detail}</div>
      </label>`;
    }).join('');
  }
  document.getElementById('edit-prod-modal').style.display = 'flex';
}

function closeEditProd() {
  document.getElementById('edit-prod-modal').style.display = 'none';
}

async function saveEditProd() {
  if (!db) { toast('Firebase 미연결'); return; }
  const docId = document.getElementById('edit-prod-id').value;
  const year  = document.getElementById('edit-prod-year').value;
  const month = document.getElementById('edit-prod-month').value;
  const r = (window._prodRecords||[]).find(r => r.id === docId);
  if (!r) { toast('기록을 찾을 수 없습니다.'); return; }

  const checkedNos = new Set(
    [...document.querySelectorAll('input[name="edit-pack-cb"]:checked')].map(cb => +cb.value)
  );
  const newPacks = (r.packs||[]).filter(p => checkedNos.has(+p.pack_no));

  if (newPacks.length === 0) {
    if (!confirm('모든 패킹이 취소됩니다.\n이 생산 기록 전체를 삭제하시겠습니까?')) return;
    try {
      await db.collection('production_deck').doc(docId).delete();
      window._prodRecords = (window._prodRecords||[]).filter(r => r.id !== docId);
      closeEditProd();
      toast('✅ 삭제되었습니다.');
      showProdMonth(year, month);
    } catch(e) { toast('삭제 실패: ' + e.message); }
    return;
  }

  const hasDetail   = newPacks.some(p => p.sheets != null);
  const newSheets   = hasDetail ? newPacks.reduce((s,p) => s+(+p.sheets||0), 0) : null;
  const newArea     = hasDetail ? +newPacks.reduce((s,p) => s+(+p.area||0), 0).toFixed(2) : null;
  const updates = { packs: newPacks, pack_count: newPacks.length, total_sheets: newSheets, total_area: newArea };
  try {
    await db.collection('production_deck').doc(docId).update(updates);
    const idx = (window._prodRecords||[]).findIndex(r => r.id === docId);
    if (idx >= 0) Object.assign(window._prodRecords[idx], updates);
    closeEditProd();
    toast('✅ 수정되었습니다.');
    showProdMonth(year, month);
  } catch(e) { toast('수정 실패: ' + e.message); }
}

// ── 작업일보 ─────────────────────────────────────────────
function openDailyReport(date, machine, shift) {
  const allRecs = (window._prodRecords||[]).filter(r =>
    r.date === date &&
    String(r.machine||'') === String(machine||'') &&
    (!shift || r.shift === shift)
  ).sort((a,b) => 0);

  if (!allRecs.length) { toast('해당 일자/호기/시간대 기록 없음'); return; }

  const d  = new Date(date + 'T12:00:00');
  const y  = d.getFullYear(), mo = d.getMonth()+1, dy = d.getDate();
  const dw = '일월화수목금토'[d.getDay()];
  const ROWS = 13;
  const pages = [];
  for (let i = 0; i < Math.max(1, Math.ceil(allRecs.length / ROWS)); i++)
    pages.push(allRecs.slice(i*ROWS, (i+1)*ROWS));

  let pagesHtml = '';
  pages.forEach((recs, pi) => {
    let rowsHtml = '', tArea = 0, tSheets = 0;
    recs.forEach(r => {
      const packs = r.packs || [];
      const nos = packs.map(p => Number(p.pack_no)).filter(n => !isNaN(n)).sort((a,b)=>a-b);
      const packStr = nos.length
        ? (nos[0]===nos[nos.length-1] ? String(nos[0]) : nos[0]+'-'+nos[nos.length-1])
        : (r.pack_count ? '('+r.pack_count+'건)' : '');
      const site = r.site||'', req = r.req_code||'';
      const area = r.total_area!=null ? (+r.total_area).toFixed(2) : '';
      const qty  = r.total_sheets!=null ? r.total_sheets : (r.pack_count||'');
      tArea += r.total_area||0;
      tSheets += r.total_sheets||r.pack_count||0;
      const combined = site+(packStr?' '+packStr:'');
      const inner = combined.length>22
        ? esc(site)+'<br><span style="font-size:8pt;color:#444">'+esc(packStr)+'</span>'
        : esc(combined);
      rowsHtml += `<tr style="height:22px">
        <td class="dr-site-td">${inner}</td>
        <td>${esc(req)}</td><td>${area}</td><td>${qty}</td>
        <td><span class="dr-chk"></span></td><td><span class="dr-chk"></span></td>
        <td style="letter-spacing:2px">&thinsp;:&thinsp;</td><td>합 / 불</td></tr>`;
    });
    for (let i=recs.length; i<ROWS; i++)
      rowsHtml += `<tr style="height:22px"><td class="dr-site-td"></td><td></td><td></td><td></td>
        <td><span class="dr-chk"></span></td><td><span class="dr-chk"></span></td>
        <td style="letter-spacing:2px">&thinsp;:&thinsp;</td><td>합 / 불</td></tr>`;

    const curShift = shift || (allRecs[0] && allRecs[0].shift) || '';
    const shiftHtml = curShift==='주간'
      ? '<span style="color:#c0392b;font-weight:bold">주</span>&nbsp;야'
      : '주&nbsp;<span style="color:#c0392b;font-weight:bold">야</span>';

    pagesHtml += `
    ${pi>0?'<div class="dr-page-gap"></div>':''}
    <div class="dr-page">
      <div class="dr-hrow">
        <div class="dr-title">(${esc(String(machine))})호기 데크반 작업일보</div>
        <table class="dr-stbl"><tr><th>작&nbsp;성</th><th>조 / 반장</th><th>확&nbsp;인</th></tr>
          <tr><td style="height:30px"></td><td></td><td></td></tr></table>
      </div>
      <div class="dr-dateline">${y}년 ${mo}월 ${dy}일 &nbsp;${dw}요일 &nbsp;&nbsp;(${shiftHtml}) &nbsp;&nbsp; OP :&nbsp;&nbsp;&nbsp;&nbsp; TI</div>
      <div class="dr-note">※ 라벨에 날자 기록 / 자주검사 및 박리검사 명확하게 할 것</div>
      <div class="dr-winfo">■ 작업시간 : 시작&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;~&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;종료 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ■ 작업자 이름 (&nbsp;&nbsp;&nbsp;&nbsp;명) :</div>
      <table class="dr-tbl">
        <thead><tr>
          <th rowspan="2" style="width:215px">현 장 명</th>
          <th rowspan="2" style="width:95px">의뢰번호</th>
          <th rowspan="2" style="width:58px">면 적</th>
          <th rowspan="2" style="width:48px">수 량</th>
          <th colspan="2">포장방식</th><th colspan="2">자 주 검 사</th>
        </tr><tr>
          <th style="width:42px">롤 재</th><th style="width:42px">슬리퍼</th>
          <th style="width:72px">시 간</th><th style="width:62px">합 / 불</th>
        </tr></thead>
        <tbody>${rowsHtml}
          <tr class="dr-total-row">
            <td colspan="2" style="text-align:right;padding-right:8px">합&nbsp;&nbsp;&nbsp;계</td>
            <td>${(+tArea).toFixed(2)}</td><td>${tSheets||''}</td><td colspan="4"></td>
          </tr>
        </tbody>
      </table>
      ${pages.length>1?`<div class="dr-pgnum">${pi+1} / ${pages.length}</div>`:''}
    </div>`;
  });

  document.getElementById('dr-body').innerHTML = pagesHtml;
  document.getElementById('dr-modal').style.display = 'flex';
  window._drDate = date; window._drMachine = machine;
}

function closeDailyReport() {
  document.getElementById('dr-modal').style.display = 'none';
}

async function downloadDailyReport() {
  const body = document.getElementById('dr-body');
  try {
    toast('이미지 생성 중...');
    const canvas = await html2canvas(body, {scale:2, useCORS:true, backgroundColor:'#ffffff', logging:false});
    const a = document.createElement('a');
    a.download = `작업일보_${window._drMachine}호기_${window._drDate}.png`;
    a.href = canvas.toDataURL('image/png');
    a.click();
  } catch(e) { toast('이미지 저장 실패: '+e.message); }
}
"""

# 기존 함수 블록 전체를 새것으로 교체
old_entire_js = """// ── 생산기록 일괄 삭제 (관리자) ─────────────────────────
function previewBatchDelete() {"""

cnt = html.count(old_entire_js)
print(f'js_block start: {cnt}')

# 기존 블록의 끝 찾기 (downloadDailyReport 끝)
old_end = """async function downloadDailyReport() {
  const body = document.getElementById('dr-body');
  try {
    toast('이미지 생성 중...');
    const canvas = await html2canvas(body, {scale:2, useCORS:true, backgroundColor:'#ffffff', logging:false});
    const a = document.createElement('a');
    a.download = `작업일보_${window._drMachine}호기_${window._drDate}.png`;
    a.href = canvas.toDataURL('image/png');
    a.click();
  } catch(e) { toast('이미지 저장 실패: '+e.message); }
}
"""

if old_entire_js in html and old_end in html:
    start_idx = html.find(old_entire_js)
    end_idx   = html.find(old_end) + len(old_end)
    html = html[:start_idx] + new_js_funcs + html[end_idx:]
    print('JS block replaced via index')
else:
    print('WARNING: Could not find JS block boundaries')
    print('old_entire_js found:', old_entire_js in html)
    print('old_end found:', old_end in html)

with open('index.html.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('openDailyReport(date,machine,shift):', 'function openDailyReport(date, machine, shift)' in html)
print('openEditProd checkbox:', 'edit-pack-cb' in html)
print('4month cutoff:', 'fourMonthsAgo' in html)
print('executeBatchDelete:', 'executeBatchDelete' in html)
