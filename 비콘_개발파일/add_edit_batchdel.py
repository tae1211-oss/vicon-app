with open('index.html.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
#  2번: 수정 버튼(✏️) + 수정 모달
# ══════════════════════════════════════════════════════════

# 2-A. showProdMonth 행에 ✏️ 버튼 추가
old_btns = """        <td style="white-space:nowrap">
          <button onclick="openDailyReport('${r.date}','${r.machine}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1"
            title="작업일보">📋</button>
          <button onclick="deleteProdRow('${r.id}','${year}','${month}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#e53935;padding:2px 4px;line-height:1"
            title="삭제">🗑</button>
        </td>"""

new_btns = """        <td style="white-space:nowrap">
          <button onclick="openEditProd('${r.id}','${year}','${month}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#2e7d32;padding:2px 4px;line-height:1"
            title="수정">✏️</button>
          <button onclick="openDailyReport('${r.date}','${r.machine}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#1565c0;padding:2px 4px;line-height:1"
            title="작업일보">📋</button>
          <button onclick="deleteProdRow('${r.id}','${year}','${month}')"
            style="background:none;border:none;cursor:pointer;font-size:.9rem;color:#e53935;padding:2px 4px;line-height:1"
            title="삭제">🗑</button>
        </td>"""

cnt = html.count(old_btns)
print(f'btns replaced: {cnt}')
html = html.replace(old_btns, new_btns)

# 2-B. 수정 모달 HTML (dr-modal 앞에 삽입)
edit_modal = """
<!-- ════════ EDIT PROD MODAL ════════ -->
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
</div>
"""
html = html.replace('<!-- ════════ DAILY REPORT MODAL ════════ -->', edit_modal + '\n<!-- ════════ DAILY REPORT MODAL ════════ -->', 1)

# 2-C. 수정 JS 함수 (dr_js 앞에 추가)
edit_js = r"""
// ── 생산기록 수정 ─────────────────────────────────────────
function openEditProd(docId, year, month) {
  const r = (window._prodRecords||[]).find(r => r.id === docId);
  if (!r) { toast('기록을 찾을 수 없습니다.'); return; }
  document.getElementById('edit-prod-id').value      = docId;
  document.getElementById('edit-prod-year').value    = year;
  document.getElementById('edit-prod-month').value   = month;
  document.getElementById('edit-prod-date').value    = r.date    || '';
  document.getElementById('edit-prod-shift').value   = r.shift   || '주간';
  document.getElementById('edit-prod-machine').value = r.machine || '';
  document.getElementById('edit-prod-site').value    = r.site    || '';
  document.getElementById('edit-prod-reqcode').value = r.req_code|| '';
  document.getElementById('edit-prod-modal').style.display = 'flex';
}
function closeEditProd() {
  document.getElementById('edit-prod-modal').style.display = 'none';
}
async function saveEditProd() {
  if (!db) { toast('Firebase 미연결'); return; }
  const docId  = document.getElementById('edit-prod-id').value;
  const year   = document.getElementById('edit-prod-year').value;
  const month  = document.getElementById('edit-prod-month').value;
  const date   = document.getElementById('edit-prod-date').value;
  const shift  = document.getElementById('edit-prod-shift').value;
  const machine= document.getElementById('edit-prod-machine').value.trim();
  const site   = document.getElementById('edit-prod-site').value.trim();
  const reqCode= document.getElementById('edit-prod-reqcode').value.trim();
  if (!date) { toast('날짜를 입력하세요.'); return; }
  try {
    await db.collection('production_deck').doc(docId).update({
      date, shift, machine, site, req_code: reqCode
    });
    // 로컬 캐시 업데이트
    if (window._prodRecords) {
      const idx = window._prodRecords.findIndex(r => r.id === docId);
      if (idx >= 0) Object.assign(window._prodRecords[idx], {date, shift, machine, site, req_code: reqCode});
    }
    closeEditProd();
    toast('✅ 수정되었습니다.');
    showProdMonth(year, month);
  } catch(e) { toast('수정 실패: ' + e.message); }
}
"""

html = html.replace(
    '// ════════════════════════════════════════════════\n//  작업일보 기능',
    edit_js + '\n// ════════════════════════════════════════════════\n//  작업일보 기능',
    1
)

# ══════════════════════════════════════════════════════════
#  3번: 관리자 전용 일괄삭제 카드 (prod-admin-sec에 추가)
# ══════════════════════════════════════════════════════════

old_admin_sec = """    <div id="prod-admin-sec">
      <div class="card">
        <div class="card-title">⚠️ 생산 데이터 관리</div>
        <div style="font-size:.78rem;color:#78909c;margin-bottom:10px">최근 생산 기록을 삭제합니다.</div>
        <button class="btn btn-danger btn-full" onclick="openDeleteProd()">🗑️ 생산 기록 삭제</button>
      </div>
    </div>"""

new_admin_sec = """    <div id="prod-admin-sec">
      <div class="card">
        <div class="card-title">⚠️ 생산 데이터 관리</div>
        <div style="font-size:.78rem;color:#78909c;margin-bottom:10px">최근 생산 기록을 삭제합니다.</div>
        <button class="btn btn-danger btn-full" onclick="openDeleteProd()">🗑️ 생산 기록 삭제</button>
      </div>
      <div class="card" style="margin-top:12px">
        <div class="card-title">🗂️ 일괄 삭제 (조건 검색)</div>
        <div style="font-size:.78rem;color:#78909c;margin-bottom:12px">조건에 맞는 생산기록을 한번에 삭제합니다.</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
          <div>
            <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">년월 (YYYY-MM)</label>
            <input type="month" id="batch-del-month" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box"/>
          </div>
          <div>
            <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">날짜</label>
            <input type="date" id="batch-del-date" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box"/>
          </div>
          <div>
            <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">호기</label>
            <input type="text" id="batch-del-machine" placeholder="예: 1 (비우면 전체)" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box"/>
          </div>
          <div>
            <label style="font-size:.75rem;font-weight:700;color:#546e7a;display:block;margin-bottom:3px">주/야간</label>
            <select id="batch-del-shift" style="width:100%;padding:8px;border:1.5px solid #e0e0e0;border-radius:8px;font-size:.85rem;box-sizing:border-box">
              <option value="">전체</option>
              <option value="주간">주간</option>
              <option value="야간">야간</option>
            </select>
          </div>
        </div>
        <button class="btn btn-secondary btn-full" onclick="previewBatchDelete()" style="margin-bottom:8px">🔍 조건 검색</button>
        <div id="batch-del-preview" style="font-size:.82rem;color:#37474f;min-height:18px;margin-bottom:8px"></div>
        <button id="batch-del-btn" class="btn btn-danger btn-full" onclick="executeBatchDelete()" style="display:none">🗑️ 일괄 삭제 실행</button>
      </div>
    </div>"""

cnt = html.count(old_admin_sec)
print(f'admin_sec replaced: {cnt}')
html = html.replace(old_admin_sec, new_admin_sec, 1)

# 3-B. 일괄삭제 JS 함수
batch_js = r"""
// ── 생산기록 일괄 삭제 (관리자) ─────────────────────────
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
    if (ym   && !(r.date||'').startsWith(ym))        return false;
    if (date && r.date !== date)                      return false;
    if (mach && String(r.machine||'') !== mach)       return false;
    if (shift && r.shift !== shift)                   return false;
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
  btn.disabled = true;
  btn.textContent = '삭제 중...';
  try {
    // Firestore 배치 처리 (500개 제한)
    const CHUNK = 400;
    for (let i = 0; i < targets.length; i += CHUNK) {
      const batch = db.batch();
      targets.slice(i, i+CHUNK).forEach(r => {
        batch.delete(db.collection('production_deck').doc(r.id));
      });
      await batch.commit();
    }
    // 로컬 캐시 업데이트
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
    btn.disabled = false;
    btn.textContent = '🗑️ 일괄 삭제 실행';
  }
}
"""

html = html.replace(
    '// ── 생산기록 수정 ─────────────────────────────────────────',
    batch_js + '\n// ── 생산기록 수정 ─────────────────────────────────────────',
    1
)

with open('index.html.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Size:', len(html.encode('utf-8')))
print('openEditProd:', 'openEditProd' in html)
print('executeBatchDelete:', 'executeBatchDelete' in html)
print('edit-prod-modal:', 'edit-prod-modal' in html)
